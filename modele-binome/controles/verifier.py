"""Vérificateur Solen — oracle indépendant de votre code.

Il compare VOS sorties (outputs/) aux valeurs de référence calculées par le générateur
depuis la vérité terrain (reference/attendu_*.json). Il ne lit jamais votre code.

    python -m controles.verifier --etape rejets       # séance 2 : rejets du CSV de faits du lot 1 (rejets.csv seul)
    python -m controles.verifier --etape initial      # après le lot 1 (entrepôt + rejets de toutes les sources)
    python -m controles.verifier --etape increment    # après le lot 2 ; enregistre l'empreinte de l'entrepôt
    python -m controles.verifier --etape rejeu        # après avoir relancé le lot 2 ; compare à l'empreinte
    python -m controles.verifier --etape export       # export CSV + manifest.json
    python -m controles.verifier --etape app          # mini-application HTML
    python -m controles.verifier --etape tout         # tout ce qui existe déjà

La mission vient de --mission, de la variable SOLEN_MISSION ou du fichier mission.txt (tronc-commun, M01 … M10).
Code de sortie : 0 = aucun échec, 1 = au moins un échec, 2 = mission ou référence introuvable.
Ne modifiez pas ce fichier : si un contrôle échoue, corrigez le code qui produit les sorties.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

ETAPES = ("rejets", "initial", "increment", "rejeu", "export", "app", "tout")
MAX_DETAILS = 12
FLOTTANTES = ("ratio", "jours", "heures")      # unités comparées avec la tolérance du contrat


class ErreurConfiguration(Exception):
    """Mission, référence ou contrat introuvable."""


class ErreurLecture(Exception):
    """Une de VOS sorties existe mais ne peut pas être lue (encodage, format) : message en français."""


# --------------------------------------------------------------------------- rapport
@dataclass
class Rapport:
    lignes: list[tuple[str, str]] = field(default_factory=list)

    def ok(self, msg: str) -> None:
        self.lignes.append(("OK", msg))

    def echec(self, msg: str) -> None:
        self.lignes.append(("ÉCHEC", msg))

    def info(self, msg: str) -> None:
        self.lignes.append(("INFO", msg))

    def a_faire(self, msg: str) -> None:
        self.lignes.append(("À FAIRE", msg))

    def titre(self, msg: str) -> None:
        self.lignes.append(("##", msg))

    @property
    def echecs(self) -> list[str]:
        return [m for s, m in self.lignes if s == "ÉCHEC"]

    @property
    def nb_ok(self) -> int:
        return sum(1 for s, _ in self.lignes if s == "OK")

    def texte(self) -> str:
        out = []
        for s, m in self.lignes:
            out.append(f"\n== {m} ==" if s == "##" else f"{s} — {m}")
        out.append(f"\nRésultat : {self.nb_ok} OK, {len(self.echecs)} ÉCHEC.")
        return "\n".join(out)


# --------------------------------------------------------------------------- formats
def tnd(m) -> str:
    m = int(m)
    signe = "-" if m < 0 else ""
    e, r = divmod(abs(m), 1000)
    return f"{signe}{e:,}".replace(",", " ") + f",{r:03d} TND"


def montrer(valeur, unite: str) -> str:
    if valeur is None:
        return "(vide)"
    if unite == "millimes":
        return f"{int(valeur)} millimes ({tnd(valeur)})"
    if unite == "ratio":
        return f"{float(valeur):.6f} ({float(valeur) * 100:.2f} %)".replace(".", ",")
    if unite == "jours":
        return f"{float(valeur):.2f} jours".replace(".", ",")
    if unite == "heures":
        return f"{float(valeur):.2f} h".replace(".", ",")
    if unite == "centiemes_heure":
        return f"{int(valeur)} centièmes ({int(valeur) / 100:.2f} h)".replace(".", ",")
    return str(valeur)


def texte(v) -> str | None:
    """Valeur d'attribut SCD2 en texte des deux côtés : 18, 18.0 et « 18 » donnent « 18 »."""
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def egal(attendu, observe, unite: str, tolerance: float) -> bool:
    if attendu is None or observe is None:
        return attendu is None and observe is None
    if unite in FLOTTANTES:
        return abs(float(attendu) - float(observe)) <= max(tolerance, 1e-9)
    try:
        return int(attendu) == int(round(float(observe))) and float(observe) == round(float(observe))
    except (TypeError, ValueError):
        return False


# --------------------------------------------------------------------------- chargement
def normaliser_mission(mission: str) -> str:
    m = mission.strip()
    return "tronc-commun" if m.lower() == "tronc-commun" else m.upper()


def lire_mission(racine: Path, mission: str | None) -> str:
    if mission and mission.strip():
        return normaliser_mission(mission)
    f = racine / "mission.txt"
    if f.exists():
        for ligne in f.read_text(encoding="utf-8").splitlines():
            ligne = ligne.split("#", 1)[0].strip()
            if ligne:
                return normaliser_mission(ligne)
    raise ErreurConfiguration("mission inconnue : indiquez --mission ou écrivez-la dans mission.txt")


def dossier_mission(racine: Path, mission: str) -> Path:
    if mission == "tronc-commun":
        return racine / "tronc-commun"
    if re.fullmatch(r"M(0[1-9]|10)", mission):
        return racine / "catalogue" / mission
    raise ErreurConfiguration(f"mission « {mission} » inconnue (tronc-commun, M01 … M10)")


def charger_json(chemin: Path) -> dict:
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ErreurConfiguration(f"fichier de référence absent : {chemin}") from None


def lire_texte(chemin: Path, quoi: str) -> str:
    """Lit une sortie en UTF-8 ; un autre encodage donne un message clair, jamais une trace Python."""
    try:
        return chemin.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise ErreurLecture(f"{quoi} ({chemin.name}) n'est pas écrit en UTF-8 (octet illisible en position {e.start}) : "
                            f"demandez à Codex de l'écrire avec encoding=\"utf-8\", puis relancez la commande "
                            f"qui le produit") from None
    except OSError as e:
        raise ErreurLecture(f"{quoi} ({chemin.name}) illisible : {e.strerror or e}") from None


def lire_csv(chemin: Path, quoi: str = "fichier CSV") -> tuple[list[str], list[dict]]:
    texte = lire_texte(chemin, quoi)
    premiere = texte.split("\n", 1)[0]
    sep = ";" if premiere.count(";") > premiere.count(",") else ","
    try:
        lecteur = csv.DictReader(io.StringIO(texte, newline=""), delimiter=sep)
        lignes = [{(k or "").strip(): v for k, v in l.items() if isinstance(k, str)} for l in lecteur]
    except csv.Error as e:
        raise ErreurLecture(f"{quoi} ({chemin.name}) n'est pas un CSV lisible : {e}") from None
    return [c.strip() for c in (lecteur.fieldnames or [])], lignes


# --------------------------------------------------------------------------- vérificateur
class Verificateur:
    def __init__(self, racine: Path, mission: str, sorties: Path, verbeux: bool = False, strict: bool = False):
        self.racine = racine
        self.mission = mission
        self.sorties = sorties
        self.verbeux = verbeux
        self.strict = strict
        self.ref = dossier_mission(racine, mission) / "reference"
        self.contrat = charger_json(self.ref / "contrat_entrepot.json")
        self.attendus = {lot: charger_json(self.ref / info["attendu"]) for lot, info in self.contrat["lots"].items()}
        f = self.contrat["fichiers"]
        self.entrepot = sorties / f["entrepot"]
        self.rejets = sorties / f["rejets"]
        self.export = sorties / f["export"]
        self.manifest = sorties / f["manifest"]
        self.app = sorties / f["app"]
        self.r = Rapport()

    # ------------------------------------------------------------- entrée
    def verifier(self, etape: str) -> Rapport:
        self.r.info(f"mission {self.mission} · référence {self.ref} · sorties {self.sorties}")
        if etape == "rejets":
            self._proteger(self.verifier_rejets)
        elif etape in ("initial", "increment", "rejeu"):
            self._proteger(self.verifier_lot, self.contrat["etapes"][etape], etape)
        elif etape == "export":
            self._proteger(self.verifier_export, obligatoire=True)
        elif etape == "app":
            self._proteger(self.verifier_app, obligatoire=True)
        else:
            self._proteger(self.verifier_lot_detecte)
            self._proteger(self.verifier_export, obligatoire=self.strict)
            self._proteger(self.verifier_app, obligatoire=self.strict)
        return self.r

    def _proteger(self, controle, *args, **kwargs) -> None:
        """Une sortie illisible donne un ÉCHEC expliqué, jamais une trace Python."""
        try:
            controle(*args, **kwargs)
        except ErreurLecture as e:
            self.r.echec(str(e))
        except sqlite3.DatabaseError as e:
            self.r.echec(f"{self.contrat['fichiers']['entrepot']} : lecture impossible ({e}) ; supprimez le fichier et "
                         f"relancez « python -m solen initial »")

    def verifier_lot_detecte(self) -> None:
        """--etape tout : contrôle l'état présent (lot 1 ou lot 2). Au lot 2, compare à l'empreinte si elle existe,
        sinon l'enregistre (enchaînement initial → increment → increment sans --etape increment entre les deux)."""
        lot = self.detecter_lot()
        if lot is None:
            if not self.entrepot.exists():
                (self.r.echec if self.strict else self.r.a_faire)(f"entrepôt absent : {self.entrepot}")
            elif (con := self.connexion(silencieux=True)) is None:
                self.connexion()                                    # ÉCHEC expliqué : pas une base SQLite
            else:
                con.close()
                self.r.echec("l'entrepôt ne correspond à aucun lot de référence (comptes de faits différents) ; "
                             "lancez --etape initial ou --etape increment pour le détail")
            return
        etape_lot = self.contrat["lots"][lot]["etape"]
        self.r.info(f"état détecté : {lot} → contrôles de l'étape {etape_lot}")
        self.verifier_lot(lot, "tout" if etape_lot == "increment" else etape_lot)

    def sources_etape_rejets(self) -> list[str]:
        """Sources contrôlées par --etape rejets : le CSV de faits (contrat → rejets.etape_rejets.sources)."""
        cfg = self.contrat["rejets"]
        return list((cfg.get("etape_rejets") or {}).get("sources")
                    or [s for s in cfg.get("sources", []) if s.lower().endswith(".csv")])

    def verifier_rejets(self) -> None:
        """Séance 2 : seul outputs/rejets.csv est contrôlé, pour le CSV de faits du lot initial, sans entrepôt."""
        lot = self.contrat["etapes"]["initial"]
        sources = self.sources_etape_rejets()
        self.r.titre(f"Étape rejets : {', '.join(sources)} ({lot}) comparé à {self.contrat['lots'][lot]['attendu']}")
        self.rejets_lot(lot, self.attendus[lot], sources=sources)
        if self.rejets.exists() and not self.r.echecs:
            autres = sorted(set(self.attendus[lot]["rejets"]["par_source"]) - set(sources))
            self.r.info((f"rejets de {', '.join(autres)} et entrepôt" if autres else "entrepôt")
                        + " : contrôlés par --etape initial")

    def _uri(self) -> str:
        return self.entrepot.resolve().as_uri() + "?mode=ro"

    def connexion(self, silencieux: bool = False) -> sqlite3.Connection | None:
        """Ouvre l'entrepôt en lecture seule ; un fichier qui n'est pas une base SQLite donne un ÉCHEC clair."""
        if not self.entrepot.exists():
            if not silencieux:
                self.r.echec(f"entrepôt absent : attendu {self.entrepot}")
            return None
        try:
            con = sqlite3.connect(self._uri(), uri=True)
            con.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()
        except sqlite3.DatabaseError as e:
            if not silencieux:
                self.r.echec(f"{self.entrepot.name} n'est pas une base SQLite lisible ({e}) : supprimez-le et relancez "
                             f"« python -m solen initial »")
            return None
        return con

    def detecter_lot(self) -> str | None:
        con = self.connexion(silencieux=True)
        if con is None:
            return None
        try:
            for lot, a in self.attendus.items():
                try:
                    if all(con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] == a["tables"][t]
                           for t in self.contrat["faits"]):
                        return lot
                except sqlite3.Error:
                    return None
        finally:
            con.close()
        return None

    # ------------------------------------------------------------- lot
    def verifier_lot(self, lot: str, etape: str) -> None:
        a = self.attendus[lot]
        nom = "rejeu" if etape == "tout" else etape
        self.r.titre(f"Étape {nom} : comparaison avec {self.contrat['lots'][lot]['attendu']}")
        con = self.connexion()
        if con is None:
            return
        try:
            if not self.tables(con):
                return
            self.comptes(con, a)
            self.colonnes_valeurs(con)
            self.cles_etrangeres(con)
            self.scd2(con, a)
            self._proteger(self.rejets_lot, lot, a)
            self.indicateurs(con, a)
            self.agregats(con, a)
            self.empreinte(con, lot, etape)
        finally:
            con.close()

    def tables(self, con) -> bool:
        presentes = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}
        bon = True
        for t, info in self.contrat["tables"].items():
            if t not in presentes:
                self.r.echec(f"table {t} absente de l'entrepôt")
                bon = False
                continue
            cols = {r[1] for r in con.execute(f"PRAGMA table_info({t})")}
            manque = [c for c in info["colonnes"] if c not in cols]
            if manque:
                self.r.echec(f"table {t} : colonnes absentes {manque}")
                bon = False
            else:
                self.r.ok(f"table {t} présente avec ses {len(info['colonnes'])} colonnes")
        return bon

    def comptes(self, con, a) -> None:
        for t, n in a["tables"].items():
            obs = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            if obs == n:
                self.r.ok(f"{t} : {obs} lignes")
            else:
                self.r.echec(f"{t} : attendu {n} lignes, observé {obs}")
        for t in self.contrat["faits"]:
            cle = self.contrat["tables"][t]["cle"]
            n, d = con.execute(f"SELECT COUNT(*), COUNT(DISTINCT {cle}) FROM {t}").fetchone()
            if n == d:
                self.r.ok(f"{t} : clé métier {cle} unique (aucun doublon)")
            else:
                self.r.echec(f"{t} : clé métier {cle} en double, attendu 0 doublon, observé {n - d}")

    def colonnes_valeurs(self, con) -> None:
        for t, info in self.contrat["tables"].items():
            mauvais = []
            for c in info["colonnes_entieres"]:
                autorise = "('integer', 'null')" if c in info["colonnes_nullables"] else "('integer')"
                n = con.execute(f"SELECT COUNT(*) FROM {t} WHERE typeof({c}) NOT IN {autorise}").fetchone()[0]
                if n:
                    mauvais.append(f"{c} ({n} valeurs non entières)")
            for c in info["colonnes"]:
                if c not in info["colonnes_nullables"]:
                    n = con.execute(f"SELECT COUNT(*) FROM {t} WHERE {c} IS NULL").fetchone()[0]
                    if n:
                        mauvais.append(f"{c} ({n} valeurs vides)")
            if mauvais:
                self.r.echec(f"{t} : attendu des entiers et aucune valeur vide, observé {', '.join(mauvais)}")
            else:
                self.r.ok(f"{t} : types entiers (millimes, clés) et valeurs obligatoires conformes")
        dd = self.contrat["dimension_date"]
        n = con.execute(f"SELECT COUNT(*) FROM {dd['table']} WHERE {dd['cle']} != "
                        f"CAST(replace({dd['date']}, '-', '') AS INTEGER)").fetchone()[0]
        if n:
            self.r.echec(f"{dd['table']} : {dd['cle']} doit valoir AAAAMMJJ de {dd['date']}, observé {n} écarts")
        else:
            self.r.ok(f"{dd['table']} : {dd['cle']} = AAAAMMJJ de {dd['date']}")

    def cles_etrangeres(self, con) -> None:
        violations = con.execute("PRAGMA foreign_key_check").fetchall()
        declarees = sum(len(con.execute(f"PRAGMA foreign_key_list({t})").fetchall()) for t in self.contrat["tables"])
        if violations:
            self.r.echec(f"PRAGMA foreign_key_check : attendu 0 violation, observé {len(violations)}")
        elif declarees:
            self.r.ok(f"PRAGMA foreign_key_check : 0 violation ({declarees} clés étrangères déclarées)")
        else:
            self.r.info("aucune FOREIGN KEY déclarée (conseillé par le cahier des charges)")
        for t, info in self.contrat["tables"].items():
            for col, ref in info["cles_etrangeres"].items():
                tr, cr = ref.split(".")
                n = con.execute(f"SELECT COUNT(*) FROM {t} f LEFT JOIN {tr} d ON d.{cr} = f.{col} "
                                f"WHERE d.{cr} IS NULL").fetchone()[0]
                if n:
                    self.r.echec(f"{t}.{col} → {ref} : attendu 0 ligne orpheline, observé {n}")
                else:
                    self.r.ok(f"{t}.{col} → {ref} : aucune ligne orpheline")

    def scd2(self, con, a) -> None:
        s = self.contrat["scd2"]
        t, cm, at, vf, vt = s["table"], s["cle_metier"], s["attribut"], s["valid_from"], s["valid_to"]
        obs = {(str(r[0]), texte(r[1]), r[2], r[3]) for r in con.execute(f"SELECT {cm}, {at}, {vf}, {vt} FROM {t}")}
        att = {(v["cle_metier"], texte(v["attribut"]), v["valid_from"], v["valid_to"]) for v in a["scd2"]["versions"]}
        if obs == att:
            self.r.ok(f"{t} : {len(att)} versions conformes (clé métier, {at}, valid_from, valid_to)")
        else:
            for v in sorted(att - obs, key=str)[:MAX_DETAILS]:
                self.r.echec(f"{t} : version attendue absente {v}")
            for v in sorted(obs - att, key=str)[:MAX_DETAILS]:
                self.r.echec(f"{t} : version observée non attendue {v}")
        courantes = con.execute(f"SELECT {cm} FROM {t} GROUP BY {cm} "
                                f"HAVING SUM(CASE WHEN {vt} IS NULL THEN 1 ELSE 0 END) != 1").fetchall()
        if courantes:
            self.r.echec(f"{t} : attendu exactement 1 version courante par {cm}, observé un écart pour "
                         f"{[r[0] for r in courantes]}")
        else:
            self.r.ok(f"{t} : exactement une version courante ({vt} vide) par {cm}")
        n = con.execute(f"SELECT COUNT(*) FROM {t} WHERE {vt} IS NOT NULL AND {vt} <= {vf}").fetchone()[0]
        chev = con.execute(f"SELECT COUNT(*) FROM {t} x JOIN {t} y ON x.{cm} = y.{cm} AND x.{s['cle']} < y.{s['cle']} "
                           f"WHERE x.{vf} < COALESCE(y.{vt}, '9999-12-31') "
                           f"AND y.{vf} < COALESCE(x.{vt}, '9999-12-31')").fetchone()[0]
        if n or chev:
            self.r.echec(f"{t} : attendu des périodes valides sans chevauchement, observé {n} période(s) "
                         f"vide(s) et {chev} chevauchement(s)")
        else:
            self.r.ok(f"{t} : périodes [valid_from ; valid_to[ sans chevauchement")
        for f in a["scd2"]["frontieres"]:
            r = con.execute(f"SELECT {at} FROM {t} WHERE {cm} = ? AND {vf} <= ? AND ({vt} IS NULL OR {vt} > ?)",
                            (f["cle_metier"], f["date"], f["date"])).fetchall()
            obs_v = [texte(x[0]) for x in r]
            if obs_v == [texte(f["attribut"])]:
                self.r.ok(f"{t} : {f['cle_metier']} le {f['date']} → {at} « {f['attribut']} »")
            else:
                self.r.echec(f"{t} : {f['cle_metier']} le {f['date']}, attendu « {f['attribut']} », observé {obs_v}")
        dd = self.contrat["dimension_date"]
        for fa in s["faits"]:
            n = con.execute(
                f"SELECT COUNT(*) FROM {fa['table']} f JOIN {dd['table']} d ON d.{dd['cle']} = f.{fa['date_key']} "
                f"JOIN {t} v ON v.{s['cle']} = f.{fa['colonne']} "
                f"WHERE NOT (v.{vf} <= d.{dd['date']} AND (v.{vt} IS NULL OR d.{dd['date']} < v.{vt}))").fetchone()[0]
            if n:
                self.r.echec(f"{fa['table']} : attendu chaque fait relié à la version valable à sa date, "
                             f"observé {n} faits mal rattachés")
            else:
                self.r.ok(f"{fa['table']} : chaque fait est relié à la version de {t} valable à sa date")

    def rejets_lot(self, lot: str, a, sources: list[str] | None = None) -> None:
        """Compare outputs/rejets.csv à la référence du lot. `sources` limite le contrôle à ces sources (séance 2 :
        le CSV de faits) ; sinon toutes les sources du lot sont comparées, motif par motif et source par source."""
        cfg = self.contrat["rejets"]
        if not self.rejets.exists():
            self.r.echec(f"fichier des rejets absent : attendu {self.rejets}")
            return
        entete, lignes = lire_csv(self.rejets, "le fichier des rejets")
        manque = [c for c in cfg["colonnes_obligatoires"] if c not in entete]
        if manque:
            self.r.echec(f"rejets.csv : colonnes obligatoires absentes {manque} (observé {entete})")
            return
        du_lot = [l for l in lignes if (l.get("lot") or "").strip() == lot]
        if lignes and not du_lot:
            vus = sorted({(l.get("lot") or "").strip() for l in lignes})
            self.r.echec(f"rejets.csv : aucune ligne avec lot = « {lot} » ; valeurs trouvées dans la colonne lot : "
                         f"{vus[:8]}")
            return
        att_src_tout = a["rejets"]["par_source"]
        if sources is None:
            etiquette, att_src = f"rejets {lot}", att_src_tout
            att = a["rejets"]["par_motif"]
        else:
            etiquette = f"rejets {lot} · {', '.join(sources)}"
            att_src = {s: m for s, m in att_src_tout.items() if s in sources}
            att = {}
            for m in att_src.values():
                for k, n in m.items():
                    att[k] = att.get(k, 0) + n
            retenues = [l for l in du_lot if (l.get("source") or "").strip() in sources]
            if du_lot and not retenues:
                vues = sorted({(l.get("source") or "").strip() for l in du_lot})
                self.r.echec(f"rejets.csv : aucune ligne du {lot} avec source = « {' / '.join(sources)} » (nom exact du "
                             f"fichier) ; valeurs trouvées dans la colonne source : {vues[:8]}")
                return
            du_lot = retenues
        par_motif: dict[str, int] = {}
        par_source: dict[str, dict[str, int]] = {}
        for l in du_lot:
            m, s = (l.get("motif") or "").strip(), (l.get("source") or "").strip()
            if m in cfg["motifs_toleres"]:
                continue
            par_motif[m] = par_motif.get(m, 0) + 1
            par_source.setdefault(s, {})
            par_source[s][m] = par_source[s].get(m, 0) + 1
        for m in sorted(set(att) | set(par_motif)):
            e, o = att.get(m, 0), par_motif.get(m, 0)
            if m not in att:
                self.r.echec(f"{etiquette} : motif inattendu « {m} » ({o} lignes)")
            elif e == o:
                self.r.ok(f"{etiquette} : {m} = {o}")
            else:
                self.r.echec(f"{etiquette} : {m}, attendu {e}, observé {o}")
        if sources is None:
            if par_source == att_src:
                self.r.ok(f"{etiquette} : répartition par source conforme ({', '.join(sorted(att_src))})")
            elif sum(par_motif.values()) == a["rejets"]["total"]:
                self.r.echec(f"{etiquette} : par source, attendu {att_src}, observé {par_source}")
        self.numeros_de_ligne(lot, a, du_lot, sources)
        tol = sum(1 for l in du_lot if (l.get("motif") or "").strip() in cfg["motifs_toleres"])
        if tol:
            self.r.info(f"{etiquette} : {tol} ligne(s) notée(s) {cfg['motifs_toleres']} (facultatif, non compté)")

    def numeros_de_ligne(self, lot: str, a, du_lot: list[dict], sources: list[str] | None) -> None:
        """Chaque rejet d'un CSV désigne une ligne réelle du fichier (l'en-tête est la ligne 1), une seule fois."""
        toleres = self.contrat["rejets"]["motifs_toleres"]
        for src, info in sorted(a.get("sources", {}).items()):
            if not src.lower().endswith(".csv") or "lignes" not in info or (sources is not None and src not in sources):
                continue
            nums = [(l.get("numero_ligne") or "").strip() for l in du_lot
                    if (l.get("source") or "").strip() == src and (l.get("motif") or "").strip() not in toleres]
            if not nums:
                continue
            fin = int(info["lignes"]) + 1
            hors = [n for n in nums if not (n.isdigit() and 2 <= int(n) <= fin)]
            doubles = sorted({n for n in nums if nums.count(n) > 1})
            if hors or doubles:
                detail = []
                if hors:
                    detail.append(f"{len(hors)} numéro(s) hors du fichier, ex. {hors[:5]}")
                if doubles:
                    detail.append(f"{len(doubles)} numéro(s) en double, ex. {doubles[:5]}")
                self.r.echec(f"rejets {lot} · {src} : numero_ligne doit être une ligne réelle du fichier (2 à {fin}, "
                             f"l'en-tête étant la ligne 1), une seule fois ; observé {' et '.join(detail)}")
            else:
                self.r.ok(f"rejets {lot} · {src} : {len(nums)} numero_ligne réels (2 à {fin}), uniques")

    def _inds(self) -> list[dict]:
        return self.contrat["indicateurs"]

    def _requete(self, axe: str | None = None) -> str:
        vue = self.contrat["vue_analyse"]
        sel = ", ".join(f"{i['sql']} AS {i['code']}" for i in self._inds())
        if axe:
            return f"WITH mouvements AS ({vue}) SELECT {axe} AS cle, {sel} FROM mouvements GROUP BY {axe} ORDER BY {axe}"
        return f"WITH mouvements AS ({vue}) SELECT {sel} FROM mouvements"

    def indicateurs(self, con, a) -> None:
        try:
            ligne = con.execute(self._requete()).fetchone()
        except sqlite3.Error as e:
            self.r.echec(f"indicateurs : la vue d'analyse du contrat ne s'exécute pas sur votre entrepôt ({e})")
            return
        for i, v in zip(self._inds(), ligne):
            e = a["indicateurs"][i["code"]]
            if egal(e, v, i["unite"], i["tolerance"]):
                self.r.ok(f"{i['libelle']} : {montrer(v, i['unite'])}")
            else:
                self.r.echec(f"{i['libelle']} : attendu {montrer(e, i['unite'])}, observé {montrer(v, i['unite'])}")

    def agregats(self, con, a) -> None:
        for nom, axe in self.contrat["axes"].items():
            try:
                rows = con.execute(self._requete(axe)).fetchall()
            except sqlite3.Error as e:
                self.r.echec(f"agrégats {nom} : requête impossible ({e})")
                continue
            obs = {str(r[0]): r[1:] for r in rows}
            att = a["agregats"][nom]
            ecarts = []
            for cle in sorted(set(att) | set(obs)):
                if cle not in obs:
                    ecarts.append(f"{nom} « {cle} » : attendu présent, observé absent")
                    continue
                if cle not in att:
                    ecarts.append(f"{nom} « {cle} » : clé non attendue")
                    continue
                for i, v in zip(self._inds(), obs[cle]):
                    e = att[cle][i["code"]]
                    if not egal(e, v, i["unite"], i["tolerance"]):
                        ecarts.append(f"{nom} « {cle} » {i['code']} : attendu {montrer(e, i['unite'])}, "
                                      f"observé {montrer(v, i['unite'])}")
            if ecarts:
                for x in ecarts[:MAX_DETAILS]:
                    self.r.echec(x)
                if len(ecarts) > MAX_DETAILS:
                    self.r.echec(f"{nom} : {len(ecarts) - MAX_DETAILS} autres écarts non affichés")
            else:
                self.r.ok(f"agrégats {nom} : {len(att)} valeurs de « {axe} » × {len(self._inds())} indicateurs conformes")

    def fichier_empreinte(self, lot: str) -> Path:
        return self.sorties / "verification" / f"empreinte_{lot}.json"

    def empreinte(self, con, lot: str, etape: str) -> None:
        """Empreinte de l'entrepôt = nombre de lignes + somme de contrôle SHA-256 de chaque table (lignes triées).
        --etape increment l'enregistre ; --etape rejeu exige qu'elle existe et que rien n'ait changé ;
        --etape tout compare si elle existe, sinon l'enregistre."""
        h = {}
        for t in self.contrat["ordre_tables"]:
            cols = self.contrat["tables"][t]["colonnes"]
            digest, n = hashlib.sha256(), 0
            for r in con.execute(f"SELECT {', '.join(cols)} FROM {t} ORDER BY {', '.join(cols)}"):
                digest.update(repr(tuple(r)).encode())
                n += 1
            h[t] = {"lignes": n, "sha256": digest.hexdigest()}
        f = self.fichier_empreinte(lot)
        rel = f"{self.sorties.name}/{f.relative_to(self.sorties).as_posix()}"
        if etape == "increment" or (etape == "tout" and not f.exists()):
            if self.r.echecs:
                if etape == "increment":
                    self.r.info("empreinte non enregistrée : corrigez d'abord les ÉCHEC ci-dessus, puis relancez "
                                "--etape increment")
                return
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps({"lot": lot, "tables": h}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if etape == "increment":
                self.r.info(f"empreinte enregistrée : {rel}")
            else:
                self.r.info(f"empreinte enregistrée maintenant ({rel}) : pour prouver le rejeu, relancez le lot 2, "
                            f"puis --etape rejeu")
        elif etape in ("rejeu", "tout"):
            if not f.exists():
                self.r.echec(f"rejeu : empreinte absente ({rel}), le rejeu ne peut pas être prouvé. Dans l'ordre : "
                             f"« python -m solen increment », « python -m controles.verifier --etape increment » "
                             f"(enregistre l'empreinte), « python -m solen increment » (rejeu), puis --etape rejeu")
                return
            try:
                avant = json.loads(lire_texte(f, "l'empreinte enregistrée")).get("tables")
                assert isinstance(avant, dict)
            except (ErreurLecture, json.JSONDecodeError, AttributeError, AssertionError):
                self.r.echec(f"rejeu : empreinte {rel} illisible ; relancez --etape increment pour la réécrire")
                return
            changees = []
            for t, x in h.items():
                y = avant.get(t) or {}
                if y.get("sha256") != x["sha256"]:
                    changees.append(f"{t} ({y.get('lignes', '?')} → {x['lignes']} lignes)")
            if changees:
                self.r.echec(f"rejeu : attendu un entrepôt identique à l'empreinte enregistrée par --etape increment, "
                             f"observé des changements dans {', '.join(changees)} (si vous avez modifié le code depuis, "
                             f"relancez --etape increment avant le rejeu)")
            else:
                self.r.ok(f"rejeu : {len(h)} tables identiques à l'empreinte de --etape increment")

    # ------------------------------------------------------------- export
    def verifier_export(self, obligatoire: bool) -> None:
        self.r.titre("Export CSV + manifest.json")
        if not self.manifest.exists():
            (self.r.echec if obligatoire else self.r.a_faire)(f"manifest absent : {self.manifest}")
            return
        try:
            man = json.loads(lire_texte(self.manifest, "le manifeste"))
        except json.JSONDecodeError as e:
            self.r.echec(f"manifest.json illisible : JSON invalide ({e})")
            return
        if not isinstance(man, dict) or not isinstance(man.get("tables", {}), dict):
            self.r.echec("manifest.json : attendu un objet JSON avec une clé « tables » {table: {lignes, sommes}}")
            return
        con = self.connexion()
        if con is None:
            return
        try:
            lot = self.detecter_lot()
            if lot:
                self.r.ok(f"l'entrepôt exporté correspond à la référence {lot}")
            else:
                self.r.echec("l'entrepôt exporté ne correspond à aucun lot de référence")
            tables_man = man.get("tables", {})
            for t in self.contrat["export"]["tables"]:
                fichier = self.export / f"{t}.csv"
                if not fichier.exists():
                    self.r.echec(f"export : fichier absent {fichier}")
                    continue
                entete, lignes = lire_csv(fichier, f"l'export {t}.csv")
                manque = [c for c in self.contrat["tables"][t]["colonnes"] if c not in entete]
                if manque:
                    self.r.echec(f"export {t}.csv : colonnes absentes {manque}")
                n_db = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                n_man = (tables_man.get(t) or {}).get("lignes")
                if len(lignes) == n_db == n_man:
                    self.r.ok(f"export {t} : {n_db} lignes (CSV = entrepôt = manifest)")
                else:
                    self.r.echec(f"export {t} : attendu {n_db} lignes (entrepôt), observé CSV {len(lignes)} et "
                                 f"manifest {n_man}")
                for c in self.contrat["export"]["sommes"].get(t, []):
                    s_db = con.execute(f"SELECT COALESCE(SUM({c}), 0) FROM {t}").fetchone()[0]
                    try:
                        s_csv = sum(int(l[c]) for l in lignes if (l.get(c) or "") != "")
                    except KeyError:
                        s_csv = f"(colonne {c} absente)"
                    except ValueError:
                        s_csv = f"(valeur non entière dans la colonne {c})"
                    s_man = ((tables_man.get(t) or {}).get("sommes") or {}).get(c)
                    ref = ((self.attendus[lot].get("sommes_export") or {}).get(t) or {}).get(c) if lot else None
                    if ref is not None and s_db != ref:
                        self.r.echec(f"export {t}.{c} : attendu {ref} (référence), observé {s_db}")
                    elif s_csv == s_db == s_man:
                        self.r.ok(f"export {t}.{c} : somme {s_db} (CSV = entrepôt = manifest"
                                  + (" = référence)" if ref is not None else ")"))
                    else:
                        self.r.echec(f"export {t}.{c} : attendu {s_db} (entrepôt), observé CSV {s_csv} et "
                                     f"manifest {s_man}")
        finally:
            con.close()

    # ------------------------------------------------------------- application
    def verifier_app(self, obligatoire: bool) -> None:
        self.r.titre("Mini-application locale")
        cfg = self.contrat["app"]
        if not self.app.exists():
            (self.r.echec if obligatoire else self.r.a_faire)(f"application absente : {self.app}")
            return
        html = self.app.read_text(encoding="utf-8", errors="replace")
        taille = self.app.stat().st_size
        if taille <= cfg["taille_max_octets"]:
            self.r.ok(f"index.html : un seul fichier de {taille // 1024} Ko")
        else:
            self.r.echec(f"index.html : attendu ≤ {cfg['taille_max_octets']} octets, observé {taille}")
        reseau = re.findall(r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//[^"']*""", html, re.I)
        reseau += re.findall(r"""(?:@import|url\()\s*["']?\s*(?:https?:)?//[^"')]*""", html, re.I)
        reseau += re.findall(r"\b(?:fetch|XMLHttpRequest|import\s*\()", html)
        if reseau:
            self.r.echec(f"index.html : attendu aucun chargement externe, observé {sorted(set(reseau))[:5]}")
        else:
            locaux = re.findall(r"""<(?:img|script|link|iframe|source|embed)\b[^>]*?\b(?:src|href)\s*=\s*["']\s*"""
                                r"""(?!data:|#|javascript:)([^"'\s][^"']*)""", html, re.I)
            if locaux:
                self.r.echec(f"index.html : attendu un seul fichier autonome, observé des fichiers chargés à côté "
                             f"{sorted(set(locaux))[:5]} (intégrez-les ou supprimez-les)")
            else:
                self.r.ok("index.html : autonome (aucun lien réseau, aucun chargement de fichier)")
        for texte in cfg["textes_obligatoires"]:
            if texte.lower() in html.lower():
                self.r.ok(f"index.html : écran « {texte} » présent")
            else:
                self.r.echec(f"index.html : écran « {texte} » attendu, absent")
        for motif, libelle in ((r"<script", "JavaScript et données intégrés"), (r"<svg|createElementNS", "graphique SVG"),
                               (r"<select|<input", "filtres")):
            if re.search(motif, html, re.I):
                self.r.ok(f"index.html : {libelle}")
            else:
                self.r.echec(f"index.html : {libelle} attendu(s), absent(s)")


# --------------------------------------------------------------------------- API + CLI
def verifier(etape: str, mission: str | None = None, racine: Path | None = None, sorties: Path | None = None,
             strict: bool = False) -> Rapport:
    racine = Path(racine or os.environ.get("SOLEN_RACINE") or Path.cwd()).resolve()
    mission = lire_mission(racine, mission or os.environ.get("SOLEN_MISSION"))
    sorties = Path(sorties or os.environ.get("SOLEN_SORTIES") or racine / "outputs").resolve()
    return Verificateur(racine, mission, sorties, strict=strict).verifier(etape)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m controles.verifier",
                                description="Compare vos sorties aux valeurs de référence de la mission.")
    p.add_argument("--mission", help="tronc-commun ou M01 … M10 (défaut : SOLEN_MISSION, sinon mission.txt)")
    p.add_argument("--etape", choices=ETAPES, default="tout", metavar="|".join(ETAPES),
                   help="étape contrôlée, dans l'ordre du parcours : " + " → ".join(ETAPES) + " (défaut : tout)")
    p.add_argument("--racine", type=Path, help="racine du dépôt binôme (défaut : dossier courant)")
    p.add_argument("--sorties", type=Path, help="dossier des sorties (défaut : <racine>/outputs)")
    p.add_argument("--strict", action="store_true", help="avec --etape tout : export et app obligatoires")
    a = p.parse_args(argv)
    try:
        rapport = verifier(a.etape, a.mission, a.racine, a.sorties, a.strict)
    except ErreurConfiguration as e:
        print(f"ÉCHEC — {e}")
        return 2
    except Exception as e:                                  # jamais de trace Python pour l'étudiant
        print(f"ÉCHEC — le vérificateur n'a pas pu lire vos sorties ({type(e).__name__} : {e}) ; "
              f"relancez la commande qui les produit, puis le vérificateur")
        return 1
    print(rapport.texte())
    return 1 if rapport.echecs else 0


if __name__ == "__main__":
    sys.exit(main())
