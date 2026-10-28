"""Mission M10 — agence numérique « Pixel Studio » (feuilles de temps, coûts, projets SCD2, factures + avoirs).

    python authoring/generateurs/mission10_pixel_studio.py

Écrit modele-binome/catalogue/M10/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md, echantillon/,
sources/lot1/, sources/lot2/, reference/}, le bloc M10 de v7-data.json et la vérité privée dans
solutions/verite_terrain/M10/.
"""
from __future__ import annotations

from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec,
                    table_dim_date, rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv,
                    ecrire_excel, ecrire_json, ecrire_sqlite, preparer_dossier, produire_reference,
                    calculer_attendu_echantillon, ecrire_verite_privee, format_montant, lire_montant_millimes,
                    exporter_v7_data, tnd_fr, md_tableau, taille_dossier, TAILLE_MAX_MISSION)
from textes_mission10 import SPEC_TEXTES

GRAINE = 261010
CODE = "M10"
PROFILS = {"développeur": 32500, "designer": 29000, "chef de projet": 41000, "consultant": 47500}
# code, nom (fictif), profil, saisie dans le classeur (casse volontairement variable)
COLLABS = [("C01", "Amine Gharbi", "développeur", "Développeur"), ("C02", "Yasmine Cherif", "designer", "designer "),
           ("C03", "Hela Mansour", "chef de projet", "Chef de projet"), ("C04", "Omar Ferchichi", "consultant", "Consultant"),
           ("C05", "Rania Bouzid", "développeur", "DÉVELOPPEUR"), ("C06", "Mehdi Saidi", "développeur", "développeur"),
           ("C07", "Nour Jebali", "chef de projet", "chef de projet"), ("C08", "Khalil Hamdi", "designer", "Designer"),
           ("C09", "Salma Riahi", "développeur", " Développeur"), ("C10", "Walid Kefi", "consultant", "consultant"),
           ("C11", "Mariem Toumi", "designer", "Designer"), ("C12", "Bilel Chaouch", "chef de projet", "Chef de Projet"),
           ("C13", "Sarra Mejri", "développeur", "Développeur"), ("C14", "Anis Belhaj", "développeur", "développeur "),
           ("C15", "Dorra Khelifi", "consultant", "Consultant")]
NOM = {c[0]: c[1] for c in COLLABS}
PROFIL = {c[0]: c[2] for c in COLLABS}
# code, nom, client, type, début, chef (code), poids, paramètre (régie : tarif de vente TND/h ; forfait : facteur
# budget / coût final), jalons forfait (date, part) ou part facturable en régie
PROJETS = [
    ("PX01", "Site vitrine", "Boulangerie Essalem", "régie", "2025-11-03", "C03", 5, 68, 1.0),
    ("PX02", "Application de réservation", "Hôtel Corniche Bleue", "forfait", "2026-01-05", "C07", 10, 1.45,
     [("2026-01-23", .3), ("2026-04-17", .4), ("2026-08-28", .3)]),
    ("PX03", "Campagne réseaux sociaux printemps", "Parfumerie Yasmina", "forfait", "2026-02-02", "C03", 4, 1.7,
     [("2026-02-27", .5), ("2026-05-29", .5)]),
    ("PX04", "Boutique en ligne", "Tapis Bel Ombra", "régie", "2025-09-15", "C12", 8, 72, 1.0),
    ("PX05", "Refonte de l'intranet", "Assurances Najma", "forfait", "2025-12-01", "C12", 9, 0.72,
     [("2026-01-30", .4), ("2026-06-26", .3), ("2026-08-31", .3)]),
    ("PX06", "Application mobile de fidélité", "Café Les Arcades", "forfait", "2026-03-02", "C07", 7, 0.85,
     [("2026-03-27", .3), ("2026-07-24", .7)]),
    ("PX07", "Portail patients", "Clinique Les Jasmins Bleus", "régie", "2026-01-12", "C03", 8, 75, 1.0),
    ("PX08", "Identité visuelle", "Cabinet Ksouri Avocats", "forfait", "2026-01-19", "C03", 3, 2.0,
     [("2026-02-20", .5), ("2026-03-31", .5)]),
    ("PX09", "Maintenance applicative", "Transports Sahel Express", "régie", "2025-06-02", "C12", 6, 64, 0.55),
    ("PX10", "Site événementiel", "Festival Lumières du Sud", "forfait", "2026-04-06", "C07", 4, 1.3,
     [("2026-05-15", .5), ("2026-07-31", .5)]),
    ("PX11", "Tableau de bord commercial", "Groupe Atlas Négoce", "régie", "2026-02-16", "C12", 5, 80, 1.0),
    ("PX12", "Campagne de recrutement", "École Horizon Numérique", "forfait", "2026-05-04", "C03", 3, 1.6,
     [("2026-05-29", .4), ("2026-08-14", .6)]),
    ("PX13", "Configurateur de cuisines", "Cuisines Médina Design", "forfait", "2026-02-09", "C07", 6, 0.9,
     [("2026-03-13", .3), ("2026-06-19", .7)]),
    ("PX14", "Accompagnement référencement", "Agence Voyages Oasis", "régie", "2025-10-06", "C03", 3, 85, 1.0),
    ("PX15", "Application de livraison", "Marché Frais Express", "forfait", "2026-01-26", "C12", 7, 1.25,
     [("2026-02-27", .25), ("2026-05-22", .35), ("2026-08-21", .4)]),
    ("PX16", "Site institutionnel", "Association Mains Solidaires", "forfait", "2026-03-16", "C07", 3, 1.1,
     [("2026-04-30", .5), ("2026-06-30", .5)]),
    ("PX17", "Audit d'accessibilité", "Mutuelle des Enseignants du Cap", "régie", "2026-04-13", "C12", 3, 90, 1.0),
    ("PX18", "Newsletter et emailing", "Librairie La Plume d'Or", "forfait", "2026-02-23", "C03", 2, 1.5,
     [("2026-03-31", .5), ("2026-06-30", .5)]),
    ("PX19", "Prototype réalité augmentée", "Galerie Azur Mosaïques", "forfait", "2026-04-20", "C07", 5, 0.65,
     [("2026-06-12", .5), ("2026-08-07", .5)]),
    ("INT01", "Temps interne (formation, avant-vente)", "Pixel Studio", "interne", "2025-01-01", "C12", 0, 0, None),
]
TYPE_SALE = {"PX04": "Régie", "PX13": " forfait", "INT01": "Interne"}     # casse variable dans le JSON
CHANGEMENT = ("PX07", "C07", date(2026, 7, 15))
TACHES = {"développeur": ["développement", "développement", "correction d'anomalies", "intégration", "recette"],
          "designer": ["maquettes", "design graphique", "atelier client"],
          "chef de projet": ["gestion de projet", "réunion client", "recette"],
          "consultant": ["conseil", "atelier client", "rédaction des spécifications"]}
TACHES_INT = ["formation", "avant-vente", "réunion interne"]
FERIES = {date(2026, 1, 1), date(2026, 3, 20), date(2026, 4, 9), date(2026, 5, 1), date(2026, 7, 25), date(2026, 8, 13)}
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, janvier → juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 ; recopie des heures du 30 juin et des documents depuis le 15 juin ; "
           "PX07 change de chef de projet le 2026-07-15")
REJEU_TEMPS = date(2026, 6, 30)            # le lot 2 recopie les heures de ce jour (C01 à C10)
CHEVAUCHEMENT_SQL = date(2026, 6, 15)      # la base du lot 2 recopie les documents depuis cette date
ENTETE = ["temps_id", "date_travail", "collaborateur", "profil", "projet", "heures", "tache"]
CHAMPS = ChampsCSV(ENTETE, "temps_id", "heures", montants=["heures"], dates=["date_travail"],
                   codes=["collaborateur", "projet"],
                   cles_inconnues={"collaborateur": ["C99", "C16", "C21"], "projet": ["PX99", "PX31", "PX00"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=4, inconnues=6, quantites=6),
         "lot2": Doses(doublons_exacts=3, conflits=1, manquants=2, inconnues=3, quantites=3)}
HEURES_INVALIDES = ["-2", "0", "-7,5", "-1.5", "0,0", "-4", "-0.5", "0"]


# --------------------------------------------------------------------------- heures : rendu local
def heures_texte(centiemes: int, style: str) -> str:
    """canon « 7.5 » / « 8 » · virgule « 7,5 » / « 8,0 » · deux « 7.50 » / « 8.00 »."""
    e, r = divmod(centiemes, 100)
    dec = f"{r:02d}".rstrip("0")
    if style == "canon":
        return f"{e}.{dec}" if dec else str(e)
    if style == "virgule":
        return f"{e},{dec or '0'}"
    return f"{e}.{r:02d}"


def retoucher_heures(bilan, compteur: list[int]) -> None:
    """Le cadre commun rend les heures comme un montant (millièmes d'heure, « 7.500 ») et injecte des quantités
    invalides pensées pour des unités (« 1.5 » serait valable ici). On réécrit la cellule heures, ligne par ligne,
    avec une fonction du texte seul : les doublons exacts restent identiques caractère pour caractère."""
    for l in bilan.lignes:
        t = l.valeurs["heures"]
        if l.motif == "deja_charge":
            continue
        if l.motif == "quantite_invalide":
            l.valeurs["heures"] = HEURES_INVALIDES[compteur[0] % len(HEURES_INVALIDES)]
            compteur[0] += 1
            continue
        v = lire_montant_millimes(t)                   # millièmes d'heure
        if l.motif == "id_conflit" and v % 10:         # 2e ligne du conflit (+1 millième) → +0,5 h
            v += 499
        style = "virgule" if "," in t else ("canon" if t.count(".") and len(t.split(".")[1]) == 3 else "deux")
        l.valeurs["heures"] = heures_texte(v // 10, style)


# --------------------------------------------------------------------------- vérité terrain
def affectations(rng) -> dict[str, list[tuple[str, int]]]:
    clients = [p for p in PROJETS if p[3] != "interne"]
    out = {}
    for c, _n, prof, _s in COLLABS:
        k = 4
        if prof == "chef de projet":                  # un chef saisit du temps sur tous ses projets
            choix = [p[0] for p in clients if p[5] == c]
            k = len(choix)
        else:
            choix = []
            while len(choix) < k:
                p = rng.choices(clients, [x[6] for x in clients])[0][0]
                if p not in choix:
                    choix.append(p)
        if c in ("C05", "C11"):
            choix = ["PX07"] + [p for p in choix if p != "PX07"][:k - 1]
        poids_int = 3 if prof == "consultant" else 1
        out[c] = [(p, next(x[6] for x in PROJETS if x[0] == p) + rng.randint(0, 4)) for p in choix] + [("INT01", poids_int)]
    return out


def generer_temps(rng, lot: Lot, aff, p_travail: float, premier: int) -> list[dict]:
    debut = {p[0]: date.fromisoformat(p[4]) for p in PROJETS}
    temps, num = [], premier
    for d in jours(lot.debut, lot.fin):
        if d.weekday() >= 5 or d in FERIES:      # ni week-end ni jour férié
            continue
        for c, _n, prof, _s in COLLABS:
            force = lot is LOT2 and c == "C05" and d in (date(2026, 7, 14), date(2026, 7, 15))
            if not force and rng.random() > p_travail:
                continue
            n = rng.choice([1, 1, 2])
            dispo = [(p, w) for p, w in aff[c] if debut[p] <= d]
            for k in range(n):
                p = "PX07" if force and k == 0 else rng.choices([x[0] for x in dispo], [x[1] for x in dispo])[0]
                h = rng.choice([600, 700, 750, 775, 800, 800]) if n == 1 else rng.choice(
                    [100, 150, 200, 250, 300, 325, 350, 400, 400, 450, 500])
                tache = rng.choice(TACHES_INT if p == "INT01" else TACHES[prof])
                temps.append({"temps_id": f"T26-{num:05d}", "date_travail": d, "collaborateur": c, "profil": prof,
                              "projet": p, "heures": h * 10, "tache": tache, "_c": h})
                num += 1
    return temps


def cout(t: dict) -> int:
    v = t["_c"] * PROFILS[t["profil"]]
    assert v % 100 == 0
    return v // 100


def fin_de_mois(a: int, m: int) -> date:
    return (date(a, m, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)


def generer_documents(rng, temps: list[dict]) -> tuple[list[dict], list[dict]]:
    """Factures (régie : chaque fin de mois ; forfait : jalons) puis avoirs, à partir des heures vraies."""
    bruts = []
    for code, _nom, _cl, typ, _d, _ch, _w, param, extra in PROJETS:
        tp = [t for t in temps if t["projet"] == code]
        if typ == "régie":
            for m in range(1, 9):
                c = sum(t["_c"] for t in tp if t["date_travail"].month == m)
                if c:
                    montant = round(c * param * 1000 / 100 * extra)
                    bruts.append({"code_projet": code, "jour": fin_de_mois(2026, m), "montant": montant,
                                  "objet": f"Régie {['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août'][m - 1]} 2026"})
        elif typ == "forfait":
            budget = round(sum(cout(t) for t in tp) * param / 100_000) * 100_000      # arrondi à 100 TND
            for k, (j, part) in enumerate(extra, 1):
                bruts.append({"code_projet": code, "jour": date.fromisoformat(j), "montant": round(budget * part / 1000) * 1000,
                              "objet": f"Forfait — jalon {k}/{len(extra)}"})
    for s in rng.sample([b for b in bruts if b["jour"] < date(2026, 6, 1)], 3) + \
            rng.sample([b for b in bruts if b["jour"] >= date(2026, 7, 1)], 1):
        bruts.append({**s, "statut": "ANNULEE", "objet": s["objet"] + " (saisie en double)"})
    bruts.append({"code_projet": "PX99", "jour": date(2026, 3, 31), "montant": 1_850_000, "objet": "Régie mars 2026"})
    bruts.sort(key=lambda b: (b["jour"], b["code_projet"], b.get("statut", "EMISE")))
    factures = [{"id": i, "facture_id": f"F26-{i:04d}", "code_projet": b["code_projet"], "date_facture": b["jour"].isoformat(),
                 "montant_ht": round(b["montant"] / 1000, 3), "statut": b.get("statut", "EMISE"), "objet": b["objet"],
                 "_jour": b["jour"], "_m": b["montant"], "_orphelin": b["code_projet"] == "PX99"}
                for i, b in enumerate(bruts, 1)]
    ok = [f for f in factures if f["statut"] == "EMISE" and not f["_orphelin"]]
    choix = [(f, rng.randint(3, 20)) for f in rng.sample([f for f in ok if f["_jour"] < date(2026, 6, 5)], 6)] + \
            [(f, rng.randint(3, 12)) for f in rng.sample([f for f in ok if date(2026, 6, 15) <= f["_jour"] <= date(2026, 8, 15)], 3)]
    av = [{"facture": f, "jour": f["_jour"] + timedelta(days=dj), "m": round(f["_m"] * rng.choice([.05, .1, .15, .2]) / 1000) * 1000,
           "motif": rng.choice(["geste commercial", "erreur de facturation", "heures contestées"])} for f, dj in choix]
    av += [{"facture": {"facture_id": "F26-0999"}, "jour": date(2026, 4, 8), "m": 300_000, "motif": "erreur de facturation"},
           {"facture": {"facture_id": "F26-0998"}, "jour": date(2026, 8, 5), "m": 450_000, "motif": "geste commercial"}]
    av.sort(key=lambda a: (a["jour"], a["facture"]["facture_id"]))
    avoirs = [{"id": i, "avoir_id": f"AV26-{i:03d}", "facture_id": a["facture"]["facture_id"], "date_avoir": a["jour"].isoformat(),
               "montant_ht": round(a["m"] / 1000, 3), "motif": a["motif"], "_jour": a["jour"], "_m": a["m"],
               "_projet": a["facture"].get("code_projet"), "_orphelin": "code_projet" not in a["facture"]}
              for i, a in enumerate(av, 1)]
    return factures, avoirs


def versions_projets(avec_changement: bool) -> list[dict]:
    vs = []
    for k, (code, nom, client, typ, debut, chef, *_r) in enumerate(PROJETS, 1):
        fin = CHANGEMENT[2].isoformat() if (avec_changement and code == CHANGEMENT[0]) else None
        vs.append({"projet_key": k, "projet_id": code, "nom": nom, "client": client, "type_projet": typ,
                   "chef_projet": NOM[chef], "date_debut": debut, "valid_from": debut, "valid_to": fin})
    if avec_changement:
        v = dict(next(x for x in vs if x["projet_id"] == CHANGEMENT[0]))
        vs.append({**v, "projet_key": len(vs) + 1, "chef_projet": NOM[CHANGEMENT[1]],
                   "valid_from": CHANGEMENT[2].isoformat(), "valid_to": None})
    return vs


def tables_verite(temps, factures, avoirs, avec_changement: bool) -> dict[str, list[dict]]:
    vs = versions_projets(avec_changement)
    ck = {c[0]: k for k, c in enumerate(COLLABS, 1)}
    pk = lambda code, jour: cle_version(vs, "projet_id", "projet_key", code, jour)
    ft = [{"temps_id": t["temps_id"], "date_key": date_key(t["date_travail"]), "collaborateur_key": ck[t["collaborateur"]],
           "projet_key": pk(t["projet"], t["date_travail"]), "tache": t["tache"], "heures_centiemes": t["_c"],
           "taux_horaire_millimes": PROFILS[t["profil"]], "cout_charge_millimes": cout(t)} for t in temps]
    ff = [{"document_id": f["facture_id"], "type_document": "facture", "facture_origine_id": None,
           "date_key": date_key(f["_jour"]), "projet_key": pk(f["code_projet"], f["_jour"]), "signe": 1,
           "montant_ht_millimes": f["_m"]} for f in factures]
    ff += [{"document_id": a["avoir_id"], "type_document": "avoir", "facture_origine_id": a["facture_id"],
            "date_key": date_key(a["_jour"]), "projet_key": pk(a["_projet"], a["_jour"]), "signe": -1,
            "montant_ht_millimes": a["_m"]} for a in avoirs]
    dc = [{"collaborateur_key": k, "collaborateur_id": c[0], "nom": c[1], "profil": c[2],
           "taux_horaire_millimes": PROFILS[c[2]]} for k, c in enumerate(COLLABS, 1)]
    return {"dim_collaborateur": dc, "dim_projet": vs, "fact_temps": ft, "fact_facture": ff}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_couts(chemin) -> None:
    taux = [["Développeur", 32.5], ["Designer", "29,000"], ["Chef de projet", "41,000"], ["Consultant", 47.5]]
    ecrire_excel(chemin, [
        Feuille("Profils", ["Profil", "Taux horaire coût (TND)"], taux,
                titres=["Pixel Studio — coût horaire chargé par profil, 2026 (TND par heure)"]),
        Feuille("Collaborateurs", ["Code", "Nom", "Profil"],
                [[" c09" if c[0] == "C09" else c[0], c[1], c[3]] for c in COLLABS])])


def ecrire_projets(chemin, avec_changement: bool, extrait_le: str) -> None:
    ps = []
    for code, nom, client, typ, debut, chef, *_r in PROJETS:
        hist = [{"chef_projet": NOM[chef], "valide_depuis": debut}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"chef_projet": NOM[CHANGEMENT[1]], "valide_depuis": CHANGEMENT[2].isoformat()})
        ps.append({"code": code, "nom": nom, "client": client, "type": TYPE_SALE.get(code, typ),
                   "date_debut": debut, "historique": hist})
    ecrire_json(chemin, {"source": "Référentiel des projets Pixel Studio", "extrait_le": extrait_le, "projets": ps})


DDL_FACTURATION = """
CREATE TABLE facture (
  id INTEGER PRIMARY KEY,
  facture_id TEXT NOT NULL UNIQUE,
  code_projet TEXT NOT NULL,
  date_facture TEXT NOT NULL,
  montant_ht REAL NOT NULL,
  statut TEXT NOT NULL CHECK (statut IN ('EMISE', 'ANNULEE')),
  objet TEXT
);
CREATE TABLE avoir (
  id INTEGER PRIMARY KEY,
  avoir_id TEXT NOT NULL UNIQUE,
  facture_id TEXT NOT NULL,
  date_avoir TEXT NOT NULL,
  montant_ht REAL NOT NULL,
  motif TEXT
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""


def ecrire_facturation(chemin, factures, avoirs, du: date, au: date) -> None:
    propre = lambda ls: [{k: v for k, v in x.items() if not k.startswith("_")} for x in ls]
    ecrire_sqlite(chemin, DDL_FACTURATION, {
        "facture": propre(factures), "avoir": propre(avoirs),
        "parametre": [{"cle": "export_genere_le", "valeur": (au + timedelta(days=1)).isoformat()},
                      {"cle": "perimetre", "valeur": f"documents du {du.isoformat()} au {au.isoformat()}"},
                      {"cle": "devise", "valeur": "TND"}, {"cle": "montants", "valeur": "hors taxes (HT)"}]})


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
ECHANTILLON = [
    (["E-01", "2026-03-02", "C01", "développeur", "PX01", "7.5", "développement"], None),
    (["E-02", "03/03/2026", "C01", "développeur", "PX01", "7,5", "intégration"], None),
    (["E-03", "4 mars 2026", "C02", "designer", "PX02", "3", "maquettes"], None),
    (["E-03", "4 mars 2026", "C02", "designer", "PX02", "3", "maquettes"], "doublon_exact"),
    (["E-04", "2026-03-04", " c03 ", "chef de projet", "PX01", "1,25", "réunion client"], None),
    (["E-05", "2026-03-05", "C04", "consultant", "INT01", "2", "avant-vente"], None),
    (["E-06", "2026-03-05", "C02", "designer", "PX02", "4", "maquettes"], "id_conflit"),
    (["E-06", "2026-03-05", "C02", "designer", "PX02", "4,5", "maquettes"], "id_conflit"),
    (["", "2026-03-06", "C01", "développeur", "PX01", "3", "recette"], "id_manquant"),
    (["E-07", "2026-03-06", "C99", "développeur", "PX01", "2", "recette"], "cle_inconnue"),
    (["E-08", "2026-03-06", "C01", "développeur", "PX01", "-2", "recette"], "quantite_invalide"),
    (["E-09", "2026-03-06", "C01", "développeur", " px02", "6.25", "développement"], None),
]
FACTURES_ECH = [(1, "F-001", "PX02", "2026-03-20", 900.0, "EMISE", "Forfait — jalon 1/3"),
                (2, "F-002", "PX02", "2026-03-20", 900.0, "ANNULEE", "Forfait — jalon 1/3 (saisie en double)"),
                (3, "F-003", "PX01", "2026-03-31", 1200.0, "EMISE", "Régie mars 2026")]
AVOIRS_ECH = [(1, "AV-001", "F-003", "2026-03-31", 150.0, "heures contestées"),
              (2, "AV-002", "F-099", "2026-03-31", 80.0, "erreur de facturation")]


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "temps.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON])
    ecrire_couts(dossier / "couts.xlsx")
    ecrire_projets(dossier / "projets.json", False, "2026-03-31")
    ecrire_facturation(dossier / "facturation.sqlite",
                       [dict(zip(("id", "facture_id", "code_projet", "date_facture", "montant_ht", "statut", "objet"), f))
                        for f in FACTURES_ECH],
                       [dict(zip(("id", "avoir_id", "facture_id", "date_avoir", "montant_ht", "motif"), a)) for a in AVOIRS_ECH],
                       date(2026, 3, 1), date(2026, 3, 31))
    acc = []
    for v, motif in ECHANTILLON:
        if motif is None:
            j = {"2026-03-02": 2, "03/03/2026": 3, "4 mars 2026": 4}.get(v[1], int(v[1][-2:]))
            c = v[2].strip().upper()
            acc.append({"temps_id": v[0], "date_travail": date(2026, 3, j), "collaborateur": c, "profil": PROFIL[c],
                        "projet": v[4].strip().upper(), "tache": v[6], "_c": round(float(v[5].replace(",", ".")) * 100),
                        "_texte": v[5]})
    fac = [{"facture_id": f[1], "code_projet": f[2], "_jour": date.fromisoformat(f[3]), "_m": round(f[4] * 1000)}
           for f in FACTURES_ECH if f[5] == "EMISE"]
    avo = [{"avoir_id": "AV-001", "facture_id": "F-003", "_jour": date(2026, 3, 31), "_m": 150_000, "_projet": "PX01"}]
    tables = tables_verite(acc, fac, avo, False)
    rejets = {"temps.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "facturation.sqlite": {"cle_inconnue": 1}}
    att = calculer_attendu_echantillon(spec, tables, date(2026, 3, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(acc),
                                        "factures_annulees_exclues": 1,
                                        "unite_heures": "centièmes d'heure (750 = 7,5 h)"})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(acc, att), encoding="utf-8")
    return att


def md_echantillon(acc, att) -> str:
    i, ag = att["indicateurs"], att["agregats"]["par_projet"]
    t1 = md_tableau(["Ligne du fichier", "temps_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[1]} · {v[2]!r} · {v[4]!r} · heures {v[5]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 4" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    t2 = md_tableau(["temps_id", "Date ISO", "Collaborateur (profil)", "Projet", "Heures lues → centièmes", "Calcul du coût", "Coût de charge"],
                    [[a["temps_id"], a["date_travail"].isoformat(), f"{a['collaborateur']} ({a['profil']})", a["projet"],
                      f"`{a['_texte']}` → {a['_c']}", f"{heures_texte(a['_c'], 'virgule')} h × {format_montant(PROFILS[a['profil']], 'virgule3')}",
                      tnd_fr(cout(a))] for a in acc])
    t3 = md_tableau(["Projet", "Heures", "Coût de charge", "Facturé net", "Marge de contribution"],
                    [[p, f"{heures_texte(x['heures_centiemes'], 'virgule')} h", tnd_fr(x["cout_charge_millimes"]),
                      tnd_fr(x["facture_net_millimes"]), tnd_fr(x["marge_contribution_millimes"])] for p, x in ag.items()])
    return f"""# Échantillon Pixel Studio — le calcul à la main

12 lignes de `temps.csv`, le classeur des coûts complet, les 20 projets, 3 factures et 2 avoirs dans `facturation.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

Taux horaires coût (feuille Profils) : développeur 32,500 TND · designer 29,000 · chef de projet 41,000 · consultant 47,500.

## 1. Décision ligne par ligne (`temps.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées**.

## 2. Heures et coût de charge

Une virgule ou un point sépare les décimales : `7,5` = `7.5` = 7 h 30 = **750 centièmes d'heure**. `1,25` = 1 h 15 = 125. Coût = heures × taux du profil (le profil vient du classeur, pas du CSV).

{t2}

**Heures = {i['heures_centiemes']} centièmes = {heures_texte(i['heures_centiemes'], 'virgule')} h. Coût de charge = {tnd_fr(i['cout_charge_millimes'])}** ({i['cout_charge_millimes']} millimes).

## 3. Factures et avoirs (`facturation.sqlite`)

- `F-001` : PX02 (forfait, jalon 1), 900,000 TND, `EMISE` → gardée.
- `F-002` : `ANNULEE` (la même facture saisie deux fois) → ignorée (ce n'est pas un rejet).
- `F-003` : PX01 (régie de mars), 1 200,000 TND, `EMISE` → gardée.
- `AV-001` : avoir de 150,000 TND sur `F-003` → gardé, compté **en moins** sur PX01 (projet de la facture d'origine).
- `AV-002` : la facture `F-099` n'existe pas → rejet `cle_inconnue` (source `facturation.sqlite`).

**Factures = {tnd_fr(i['factures_millimes'])} · Avoirs = {tnd_fr(i['avoirs_millimes'])} · Facturé net = {tnd_fr(i['facture_net_millimes'])}.**

## 4. Marge de contribution

Marge de contribution = facturé net − coût de charge = {tnd_fr(i['facture_net_millimes'])} − {tnd_fr(i['cout_charge_millimes'])} = **{tnd_fr(i['marge_contribution_millimes'])}**. Ce n'est pas un bénéfice : aucun frais général n'est déduit.

{t3}

INT01 est le projet interne : ses heures coûtent mais ne sont jamais facturées (marge négative, c'est normal).

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_temps` : {att['tables']['fact_temps']} lignes · `fact_facture` : {att['tables']['fact_facture']} lignes (2 factures + 1 avoir) · `dim_collaborateur` : {att['tables']['dim_collaborateur']} · `dim_projet` : {att['tables']['dim_projet']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- programme principal
def main() -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    aff = affectations(rng)
    temps1 = generer_temps(rng, LOT1, aff, 0.78, 1)
    temps2 = generer_temps(rng, LOT2, aff, 0.45, len(temps1) + 1)
    factures, avoirs = generer_documents(rng, temps1 + temps2)
    f1 = [f for f in factures if f["_jour"] <= LOT1.fin]
    f2 = [f for f in factures if CHEVAUCHEMENT_SQL <= f["_jour"]]
    a1 = [a for a in avoirs if a["_jour"] <= LOT1.fin]
    a2 = [a for a in avoirs if CHEVAUCHEMENT_SQL <= a["_jour"]]
    assert not any(x["_orphelin"] for x in f1 + a1 if x["_jour"] >= CHEVAUCHEMENT_SQL)

    b1 = construire_csv(temps1, CHAMPS, DOSES["lot1"], rng, lambda k: f"T26-9{k:04d}")
    compteur_invalides = [0]
    retoucher_heures(b1, compteur_invalides)
    jour = {t["temps_id"]: (t["date_travail"], t["collaborateur"]) for t in temps1}
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None and jour[l.origine][0] == REJEU_TEMPS
                and jour[l.origine][1] <= "C10"]
    assert 10 <= len(rejouees) <= 20, len(rejouees)
    b2 = construire_csv(temps2, CHAMPS, DOSES["lot2"], rng, lambda k: f"T26-8{k:04d}", rejouees)
    retoucher_heures(b2, compteur_invalides)
    for lot, b, avec, ff, aa, du, extrait in (("lot1", b1, False, f1, a1, LOT1.debut, "2026-06-30"),
                                              ("lot2", b2, True, f2, a2, CHEVAUCHEMENT_SQL, "2026-08-31")):
        d = dossier / "sources" / lot
        ecrire_csv(d / "temps.csv", ENTETE, [{c: l.valeurs[c] for c in ENTETE} for l in b.lignes])
        ecrire_couts(d / "couts.xlsx")
        ecrire_projets(d / "projets.json", avec, extrait)
        ecrire_facturation(d / "facturation.sqlite", ff, aa, du, LOT1.fin if lot == "lot1" else LOT2.fin)

    def acceptes(ls, deja=frozenset(), cle="facture_id"):
        return [x for x in ls if x.get("statut", "EMISE") == "EMISE" and not x["_orphelin"] and x[cle] not in deja]
    fa1, aa1 = acceptes(f1), acceptes(a1, cle="avoir_id")
    fa2 = acceptes(f2, {f["facture_id"] for f in fa1})
    aa2 = acceptes(a2, {a["avoir_id"] for a in aa1}, cle="avoir_id")
    lots = []
    for lot, b, ff, aa, fa, ava, t_cumul, f_cumul, a_cumul, avec in (
            (LOT1, b1, f1, a1, fa1, aa1, temps1, fa1, aa1, False),
            (LOT2, b2, f2, a2, fa2, aa2, temps1 + temps2, fa1 + fa2, aa1 + aa2, True)):
        nettoyage_csv = {("formats_heures" if k == "formats_montants" else k): v
                         for k, v in b.compteurs.items() if k != "lignes"}
        lots.append(LotResultat(
            lot=lot,
            sources={"temps.csv": {"lignes": b.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "couts.xlsx": {"feuilles": ["Profils", "Collaborateurs"], "profils": len(PROFILS),
                                    "collaborateurs": len(COLLABS), "ligne_entete_profils": 3},
                     "projets.json": {"projets": len(PROJETS), "versions": len(PROJETS) + (1 if avec else 0)},
                     "facturation.sqlite": {"facture": len(ff), "emises": sum(f["statut"] == "EMISE" for f in ff),
                                            "annulees": sum(f["statut"] == "ANNULEE" for f in ff), "avoir": len(aa)}},
            nettoyage={"temps.csv": nettoyage_csv,
                       "facturation.sqlite": {"factures_annulees_exclues": sum(f["statut"] == "ANNULEE" for f in ff),
                                              "deja_charges": len(acceptes(ff)) + len(acceptes(aa, cle="avoir_id"))
                                              - len(fa) - len(ava),
                                              "documents_acceptes_nouveaux": len(fa) + len(ava)}},
            rejets={"temps.csv": b.rejets(),
                    "facturation.sqlite": {"cle_inconnue": sum(x["_orphelin"] for x in ff + aa)}},
            tables_verite=tables_verite(t_cumul, f_cumul, a_cumul, avec),
            increment=None if lot is LOT1 else {
                "fact_temps_ajoutees": len(temps2), "fact_facture_ajoutees": len(fa2) + len(aa2),
                "versions_scd2_ajoutees": 1, "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin))}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(t_cumul) - (0 if lot is LOT1 else len(temps1))

    attendus = produire_reference(spec, lots)
    # double contrôle Python pur (sans SQL) des nombres clés
    tt, fs, av = temps1 + temps2, fa1 + fa2, aa1 + aa2
    ind = attendus["lot2"]["indicateurs"]
    net = sum(f["_m"] for f in fs) - sum(a["_m"] for a in av)
    assert ind["heures_centiemes"] == sum(t["_c"] for t in tt)
    assert (ind["facture_net_millimes"], ind["marge_contribution_millimes"]) == (net, net - sum(cout(t) for t in tt))
    assert 15 <= len(PROJETS) <= 25 and 12 <= len(COLLABS) <= 18
    assert 1800 <= b1.compteurs["lignes"] <= 2500 and 350 <= b2.compteurs["lignes"] <= 500, (b1.compteurs, b2.compteurs)

    ech = produire_echantillon(spec, dossier / "echantillon")
    ent_t = ["lot", "temps_id", "date_travail", "collaborateur", "profil", "projet", "tache", "heures_centiemes"]
    ecrire_verite_privee(spec, {
        "temps_verite.csv": (ent_t, [{"lot": "lot1" if i < len(temps1) else "lot2", **t, "date_travail": t["date_travail"].isoformat(),
                                      "heures_centiemes": t["_c"]} for i, t in enumerate(tt)]),
        "documents_verite.csv": (["lot", "document_id", "type_document", "facture_origine_id", "projet", "jour", "signe", "montant_ht_millimes"],
                                 [{"lot": "lot1" if f in fa1 else "lot2", "document_id": f["facture_id"], "type_document": "facture",
                                   "facture_origine_id": "", "projet": f["code_projet"], "jour": f["_jour"].isoformat(), "signe": 1,
                                   "montant_ht_millimes": f["_m"]} for f in fs]
                                 + [{"lot": "lot1" if a in aa1 else "lot2", "document_id": a["avoir_id"], "type_document": "avoir",
                                     "facture_origine_id": a["facture_id"], "projet": a["_projet"], "jour": a["_jour"].isoformat(),
                                     "signe": -1, "montant_ht_millimes": a["_m"]} for a in av]),
        "collaborateurs_verite.csv": (["collaborateur_id", "nom", "profil", "taux_horaire_millimes"],
                                      [{"collaborateur_id": c[0], "nom": c[1], "profil": c[2], "taux_horaire_millimes": PROFILS[c[2]]}
                                       for c in COLLABS]),
        "projets_verite.csv": (["projet_id", "nom", "client", "type_projet", "chef_projet", "valid_from", "valid_to"],
                               versions_projets(True)),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    exporter_v7_data(spec, ech, attendus)
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : temps.csv {a['sources']['temps.csv']['lignes']} lignes · fact_temps {a['tables']['fact_temps']} · "
              f"fact_facture {a['tables']['fact_facture']} · rejets {a['rejets']['par_motif']} · "
              f"heures {heures_texte(i['heures_centiemes'], 'virgule')} · coût {tnd_fr(i['cout_charge_millimes'])} · "
              f"facturé net {tnd_fr(i['facture_net_millimes'])} · marge {tnd_fr(i['marge_contribution_millimes'])}")
    neg = {p: x["marge_contribution_millimes"] for p, x in attendus["lot2"]["agregats"]["par_projet"].items()
           if x["marge_contribution_millimes"] < 0}
    print(f"  projets à marge de contribution négative (lot2) : {neg}")
    e = ech["indicateurs"]
    print(f"  échantillon : heures {e['heures_centiemes']} · coût {tnd_fr(e['cout_charge_millimes'])} · "
          f"facturé net {tnd_fr(e['facture_net_millimes'])} · marge {tnd_fr(e['marge_contribution_millimes'])}")


TABLES = [
    table_dim_date(),
    Table("dim_collaborateur", "dimension", "Collaborateurs avec leur profil et le taux horaire coût du profil "
          "(feuilles Collaborateurs + Profils).", [
        Colonne("collaborateur_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("collaborateur_id", "TEXT", "Code normalisé (strip + majuscules), ex. `C05`."),
        Colonne("nom", "TEXT", "Nom et prénom (fictifs)."),
        Colonne("profil", "TEXT", "Profil normalisé en minuscules : `développeur`, `designer`, `chef de projet`, `consultant`."),
        Colonne("taux_horaire_millimes", "INTEGER", "Taux horaire coût du profil, en millimes par heure (32,500 TND → 32500)."),
    ], cle_metier="collaborateur_id"),
    Table("dim_projet", "dimension_scd2", "Projets avec historique du chef de projet (SCD2).", [
        Colonne("projet_key", "INTEGER", "Clé technique d'une VERSION de projet.", cle=True),
        Colonne("projet_id", "TEXT", "Code projet, ex. `PX07` (plusieurs versions possibles)."),
        Colonne("nom", "TEXT", "Nom du projet."),
        Colonne("client", "TEXT", "Client (fictif) ; `Pixel Studio` pour le projet interne."),
        Colonne("type_projet", "TEXT", "`forfait`, `régie` ou `interne` (minuscules)."),
        Colonne("chef_projet", "TEXT", "Chef de projet de cette version (nom)."),
        Colonne("date_debut", "TEXT", "Date de début du projet, AAAA-MM-JJ."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="projet_id"),
    Table("fact_temps", "fait", "Une ligne de temps acceptée.", [
        Colonne("temps_id", "TEXT", "Identifiant de la ligne de temps (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour travaillé.", ref="dim_date.date_key"),
        Colonne("collaborateur_key", "INTEGER", "Collaborateur.", ref="dim_collaborateur.collaborateur_key"),
        Colonne("projet_key", "INTEGER", "Version du projet valable le jour travaillé.", ref="dim_projet.projet_key"),
        Colonne("tache", "TEXT", "Tâche (texte de la source, espaces supprimés)."),
        Colonne("heures_centiemes", "INTEGER", "Heures en CENTIÈMES d'heure entiers (7,5 h → 750), > 0."),
        Colonne("taux_horaire_millimes", "INTEGER", "Taux horaire coût du profil du collaborateur (millimes par heure)."),
        Colonne("cout_charge_millimes", "INTEGER", "heures_centiemes × taux_horaire_millimes / 100 (entier exact)."),
    ]),
    Table("fact_facture", "fait", "Une facture EMISE ou un avoir de la base de facturation.", [
        Colonne("document_id", "TEXT", "`facture_id` (F26-…) ou `avoir_id` (AV26-…), clé métier unique.", cle=True),
        Colonne("type_document", "TEXT", "`facture` ou `avoir`."),
        Colonne("facture_origine_id", "TEXT", "Pour un avoir : la facture corrigée ; vide pour une facture.", nullable=True),
        Colonne("date_key", "INTEGER", "Jour de la facture ou de l'avoir.", ref="dim_date.date_key"),
        Colonne("projet_key", "INTEGER", "Version du projet valable à la date du DOCUMENT.", ref="dim_projet.projet_key"),
        Colonne("signe", "INTEGER", "+1 pour une facture, −1 pour un avoir."),
        Colonne("montant_ht_millimes", "INTEGER", "Montant hors taxes en millimes, toujours positif."),
    ]),
]

if __name__ == "__main__":
    main()
