"""Vérificateur Solen — oracle indépendant de votre code.

Il compare VOS sorties (outputs/) aux valeurs de référence calculées par le générateur
depuis la vérité terrain (reference/attendu_*.json). Il ne lit jamais votre code.

    python -m controles.verifier --etape rejets       # après le nettoyage du lot 1 (rejets.csv seul)
    python -m controles.verifier --etape initial      # après le lot 1
    python -m controles.verifier --etape increment    # après le lot 2
    python -m controles.verifier --etape rejeu        # après avoir relancé le lot 2
    python -m controles.verifier --etape export       # export CSV + manifest.json
    python -m controles.verifier --etape app          # mini-application HTML
    python -m controles.verifier --etape tout         # tout ce qui existe déjà

La mission vient de --mission ou du fichier mission.txt (tronc-commun, M01 … M10).
Code de sortie : 0 = aucun échec, 1 = au moins un échec, 2 = mission ou référence introuvable.
Ne modifiez pas ce fichier : si un contrôle échoue, corrigez le code qui produit les sorties.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
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
def lire_mission(racine: Path, mission: str | None) -> str:
    if mission:
        return mission.strip()
    f = racine / "mission.txt"
    if f.exists():
        for ligne in f.read_text(encoding="utf-8").splitlines():
            ligne = ligne.split("#", 1)[0].strip()
            if ligne:
                return ligne
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


def lire_csv(chemin: Path) -> tuple[list[str], list[dict]]:
    texte = chemin.read_text(encoding="utf-8-sig")
    premiere = texte.split("\n", 1)[0]
    sep = ";" if premiere.count(";") > premiere.count(",") else ","
    lecteur = csv.DictReader(texte.splitlines(), delimiter=sep)
    lignes = list(lecteur)
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
            self.verifier_rejets()
        elif etape in ("initial", "increment", "rejeu"):
            self.verifier_lot(self.contrat["etapes"][etape], etape)
        elif etape == "export":
            self.verifier_export(obligatoire=True)
        elif etape == "app":
            self.verifier_app(obligatoire=True)
        else:
            lot = self.detecter_lot()
            if lot is None:
                if not self.entrepot.exists():
                    (self.r.echec if self.strict else self.r.a_faire)(f"entrepôt absent : {self.entrepot}")
                else:
                    self.r.echec("l'entrepôt ne correspond à aucun lot de référence (comptes de faits différents) ; "
                                 "lancez --etape initial ou --etape increment pour le détail")
            else:
                etape_lot = self.contrat["lots"][lot]["etape"]
                self.r.info(f"état détecté : {lot} → contrôles de l'étape {etape_lot}")
                self.verifier_lot(lot, "rejeu" if etape_lot == "increment" else etape_lot)
            self.verifier_export(obligatoire=self.strict)
            self.verifier_app(obligatoire=self.strict)
        return self.r

    def verifier_rejets(self) -> None:
        """Séance 2 : seul outputs/rejets.csv est contrôlé (lot initial), sans entrepôt."""
        lot = self.contrat["etapes"]["initial"]
        self.r.titre(f"Étape rejets : rejets.csv ({lot}) comparé à {self.contrat['lots'][lot]['attendu']}")
        self.rejets_lot(lot, self.attendus[lot])
        if self.rejets.exists() and not self.r.echecs:
            self.r.info("l'entrepôt n'est pas contrôlé à cette étape : lancez ensuite --etape initial")

    def connexion(self) -> sqlite3.Connection | None:
        if not self.entrepot.exists():
            self.r.echec(f"entrepôt absent : attendu {self.entrepot}")
            return None
        con = sqlite3.connect(f"file:{self.entrepot}?mode=ro", uri=True)
        return con

    def detecter_lot(self) -> str | None:
        if not self.entrepot.exists():
            return None
        con = sqlite3.connect(f"file:{self.entrepot}?mode=ro", uri=True)
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
        self.r.titre(f"Étape {etape} : comparaison avec {self.contrat['lots'][lot]['attendu']}")
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
            self.rejets_lot(lot, a)
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

    def rejets_lot(self, lot: str, a) -> None:
        cfg = self.contrat["rejets"]
        if not self.rejets.exists():
            self.r.echec(f"fichier des rejets absent : attendu {self.rejets}")
            return
        entete, lignes = lire_csv(self.rejets)
        manque = [c for c in cfg["colonnes_obligatoires"] if c not in entete]
        if manque:
            self.r.echec(f"rejets.csv : colonnes obligatoires absentes {manque} (observé {entete})")
            return
        du_lot = [l for l in lignes if (l.get("lot") or "").strip() == lot]
        par_motif: dict[str, int] = {}
        par_source: dict[str, dict[str, int]] = {}
        for l in du_lot:
            m, s = (l.get("motif") or "").strip(), (l.get("source") or "").strip()
            if m in cfg["motifs_toleres"]:
                continue
            par_motif[m] = par_motif.get(m, 0) + 1
            par_source.setdefault(s, {})
            par_source[s][m] = par_source[s].get(m, 0) + 1
        att = a["rejets"]["par_motif"]
        for m in sorted(set(att) | set(par_motif)):
            e, o = att.get(m, 0), par_motif.get(m, 0)
            if m not in att:
                self.r.echec(f"rejets {lot} : motif inattendu « {m} » ({o} lignes)")
            elif e == o:
                self.r.ok(f"rejets {lot} : {m} = {o}")
            else:
                self.r.echec(f"rejets {lot} : {m}, attendu {e}, observé {o}")
        att_src = a["rejets"]["par_source"]
        if par_source == att_src:
            self.r.ok(f"rejets {lot} : répartition par source conforme ({', '.join(sorted(att_src))})")
        elif sum(par_motif.values()) == a["rejets"]["total"]:
            self.r.echec(f"rejets {lot} : par source, attendu {att_src}, observé {par_source}")
        tol = sum(1 for l in du_lot if (l.get("motif") or "").strip() in cfg["motifs_toleres"])
        if tol:
            self.r.info(f"rejets {lot} : {tol} ligne(s) notée(s) {cfg['motifs_toleres']} (facultatif, non compté)")

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

    def empreinte(self, con, lot: str, etape: str) -> None:
        h = {}
        for t in self.contrat["ordre_tables"]:
            cols = self.contrat["tables"][t]["colonnes"]
            digest = hashlib.sha256()
            for r in con.execute(f"SELECT {', '.join(cols)} FROM {t} ORDER BY {', '.join(cols)}"):
                digest.update(repr(tuple(r)).encode())
            h[t] = digest.hexdigest()
        f = self.sorties / "verification" / f"empreinte_{lot}.json"
        if etape == "increment":
            if not self.r.echecs:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(json.dumps(h, indent=2) + "\n", encoding="utf-8")
                self.r.info(f"empreinte de l'entrepôt enregistrée ({f}) : --etape rejeu la comparera")
        elif etape == "rejeu":
            if not f.exists():
                self.r.info("pas d'empreinte enregistrée : lancez --etape increment avant de relancer le lot")
                return
            avant = json.loads(f.read_text(encoding="utf-8"))
            changees = [t for t in h if avant.get(t) != h[t]]
            if changees:
                self.r.echec(f"rejeu : attendu un entrepôt identique, observé des changements dans {changees}")
            else:
                self.r.ok("rejeu : entrepôt identique, ligne par ligne, à celui contrôlé après l'incrément")

    # ------------------------------------------------------------- export
    def verifier_export(self, obligatoire: bool) -> None:
        self.r.titre("Export CSV + manifest.json")
        if not self.manifest.exists():
            (self.r.echec if obligatoire else self.r.a_faire)(f"manifest absent : {self.manifest}")
            return
        try:
            man = json.loads(self.manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self.r.echec(f"manifest.json illisible : {e}")
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
                entete, lignes = lire_csv(fichier)
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
                    except (KeyError, ValueError):
                        s_csv = None
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
    mission = lire_mission(racine, mission)
    sorties = Path(sorties or os.environ.get("SOLEN_SORTIES") or racine / "outputs").resolve()
    return Verificateur(racine, mission, sorties, strict=strict).verifier(etape)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m controles.verifier",
                                description="Compare vos sorties aux valeurs de référence de la mission.")
    p.add_argument("--mission", help="tronc-commun ou M01 … M10 (défaut : mission.txt)")
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
    print(rapport.texte())
    return 1 if rapport.echecs else 0


if __name__ == "__main__":
    sys.exit(main())
