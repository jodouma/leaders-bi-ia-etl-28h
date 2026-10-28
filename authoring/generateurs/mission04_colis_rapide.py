"""Mission M04 — Livraison : Colis Rapide (transporteur de colis).

    python authoring/generateurs/mission04_colis_rapide.py            # écrit la mission

Écrit modele-binome/catalogue/M04/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md,
echantillon/, sources/lot1/, sources/lot2/, reference/}, le bloc M04 de v7-data.json et, si SOLEN_VERITE_PRIVEE
est définie, la vérité brute dans <SOLEN_VERITE_PRIVEE>/M04/ (dossier privé, hors dépôt).
"""
from __future__ import annotations

import sys
from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec,
                    table_dim_date, rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv,
                    ecrire_excel, ecrire_json, ecrire_sqlite, preparer_dossier, produire_reference,
                    calculer_attendu_echantillon, exporter_v7_data, ecrire_verite_privee, format_montant,
                    tnd_fr, pct_fr, jours_fr, md_tableau, taille_dossier, TAILLE_MAX_MISSION)
from textes_mission04 import SPEC_TEXTES

GRAINE = 260004
CODE = "M04"
# code, libellé
ZONES = [("GT", "Grand Tunis"), ("NO", "Nord"), ("SA", "Centre-Sahel"), ("SU", "Sud")]
LIB_ZONE = dict(ZONES)
CODE_ZONE = {v: k for k, v in ZONES}
# code, libellé, poids min exclu (g), poids max inclus (g), part des colis
TRANCHES = [("T1", "jusqu'à 1 kg", 0, 1000, 34), ("T2", "plus de 1 kg à 5 kg", 1000, 5000, 40),
            ("T3", "plus de 5 kg à 10 kg", 5000, 10000, 17), ("T4", "plus de 10 kg à 30 kg", 10000, 30000, 9)]
# grille : zone → [(prix, coût) par tranche] en millimes
GRILLE = {"GT": [(7000, 4200), (9500, 5900), (13000, 8400), (19000, 12800)],
          "NO": [(8500, 5300), (11500, 7400), (16000, 10600), (24000, 16500)],
          "SA": [(8500, 5600), (11500, 7700), (16000, 11000), (24000, 17200)],
          "SU": [(10000, 7100), (14000, 10200), (19500, 15300), (29000, 24600)]}
# code, libellé, délai promis (jours), coefficient prix (%), part, pénalité (% par jour de retard)
SERVICES = [("STD", "Standard", 3, 100, 60, 10), ("EXP", "Express", 1, 150, 22, 10), ("ECO", "Économique", 5, 85, 18, 0)]
SRV = {s[0]: s for s in SERVICES}
# code, nom, ville, zone (libellé), valide depuis, volume, probabilité de retard
AGENCES = [("TUN", "Colis Rapide Tunis Lac", "Tunis", "Grand Tunis", "2019-03-01", 30, 0.08),
           ("ARI", "Colis Rapide Ariana", "Ariana", "Grand Tunis", "2020-01-06", 18, 0.10),
           ("BIZ", "Colis Rapide Bizerte", "Bizerte", "Nord", "2021-04-12", 9, 0.13),
           ("NAB", "Colis Rapide Nabeul", "Nabeul", "Nord", "2020-09-01", 11, 0.12),
           ("SOU", "Colis Rapide Sousse", "Sousse", "Centre-Sahel", "2019-11-18", 14, 0.11),
           ("SFX", "Colis Rapide Sfax", "Sfax", "Sud", "2020-05-04", 12, 0.22),
           ("GAB", "Colis Rapide Gabès", "Gabès", "Sud", "2023-02-01", 6, 0.27)]
CHANGEMENT = ("NAB", "Centre-Sahel", date(2026, 7, 15))
VILLES = {"GT": ["Tunis", "Ariana", "Ben Arous", "La Marsa"], "NO": ["Bizerte", "Béja", "Jendouba", "Nabeul"],
          "SA": ["Sousse", "Monastir", "Mahdia", "Kairouan"], "SU": ["Sfax", "Gabès", "Médenine", "Tozeur"]}
POIDS_INVALIDES = ["-1,200", "0", "45.000", "-2.5", "0,000", "38,2", "-0.750", "0"]
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, colis livrés de janvier à juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 ; recopie des colis livrés fin juin ; NAB change de zone le 2026-07-15")
ENTETE = ["colis_id", "date_expedition", "date_promise", "date_livraison", "agence", "zone_destination",
          "poids_kg", "service", "ville_destination"]
CHAMPS = ChampsCSV(ENTETE, "colis_id", "poids_kg", montants=["poids_kg"],
                   dates=["date_expedition", "date_promise", "date_livraison"],
                   codes=["agence", "service", "zone_destination"],
                   cles_inconnues={"agence": ["KAI", "MON"], "service": ["PRM", "VIP"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=5, inconnues=6, quantites=7),
         "lot2": Doses(doublons_exacts=4, conflits=1, manquants=2, inconnues=3, quantites=2)}


def tranche_de(poids_g: int) -> int:
    """Indice de tranche : borne basse exclue, borne haute incluse."""
    return next(i for i, t in enumerate(TRANCHES) if t[2] < poids_g <= t[3])


# --------------------------------------------------------------------------- vérité terrain
def zone_agence(code: str, jour: date) -> str:
    a = next(x for x in AGENCES if x[0] == code)
    return CHANGEMENT[1] if code == CHANGEMENT[0] and jour >= CHANGEMENT[2] else a[3]


def nouveau_colis(rng, jour: date, agence: str, service: str | None = None, retard: int | None = None) -> dict:
    s = SRV[service or rng.choices([x[0] for x in SERVICES], [x[4] for x in SERVICES])[0]]
    p_retard = next(x for x in AGENCES if x[0] == agence)[6] * (1.6 if s[0] == "EXP" else 1.0) \
        * (1.3 if jour > LOT1.fin else 1.0) * (1.5 if agence == "NAB" and jour >= CHANGEMENT[2] else 1.0)
    if retard is None:
        r = rng.random()
        if r < p_retard:
            retard = rng.choice([1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 7])
        elif r < p_retard + (0.25 if s[0] == "ECO" else 0.10):
            retard = -min(rng.choice([1, 1, 2]), s[2])
        else:
            retard = 0
    promise = jour - timedelta(days=retard)
    zone_a = CODE_ZONE[zone_agence(agence, jour)]
    zone_d = zone_a if rng.random() < 0.5 else rng.choice([z for z, _ in ZONES])
    u = rng.random()
    if u < 0.03:
        poids = 1000
    elif u < 0.06:
        poids = 5000
    elif u < 0.07:
        poids = 10000
    else:
        t = rng.choices(TRANCHES, [x[4] for x in TRANCHES])[0]
        poids = rng.randrange(t[2] + 10, t[3] + 1, 10)
    return {"date_expedition": promise - timedelta(days=s[2]), "date_promise": promise, "date_livraison": jour,
            "agence": agence, "zone_destination": zone_d, "poids_kg": poids, "service": s[0],
            "ville_destination": rng.choice(VILLES[zone_d])}


def generer_colis(rng, lot: Lot, n_cible: int, premier: int) -> list[dict]:
    js = jours(lot.debut, lot.fin)
    poids_j = [(0.15 if d.weekday() == 6 else (0.7 if d.weekday() == 5 else 1.0)) * (1.12 if d.month in (3, 7) else 1.0)
               for d in js]
    evs = []
    codes, vol = [a[0] for a in AGENCES], [a[5] for a in AGENCES]
    for d in rng.choices(js, poids_j, k=n_cible):
        evs.append(nouveau_colis(rng, d, rng.choices(codes, vol)[0]))
    if lot is LOT2:   # NAB de part et d'autre de la frontière + le cas de la règle à clarifier
        for d in (date(2026, 7, 14), date(2026, 7, 14), date(2026, 7, 14), date(2026, 7, 15), date(2026, 7, 15),
                  date(2026, 7, 15)):
            evs.append(nouveau_colis(rng, d, "NAB"))
        evs.append(nouveau_colis(rng, date(2026, 7, 16), "NAB", "STD", 0))   # expédié 13/07, livré 16/07 = promis
    evs.sort(key=lambda e: (e["date_livraison"], e["date_expedition"], e["agence"], e["poids_kg"]))
    for k, e in enumerate(evs):
        e["colis_id"] = f"CR{premier + k}"
    return evs


def facturer(rng, colis: list[dict], orphelins: list[tuple[str, date]], orphelins_pen: list[tuple[str, date]]):
    """Factures et pénalités de la base opérationnelle (ids globaux, triés par date de facture)."""
    fact, pen = [], []
    for c in colis:
        z, t, s = c["zone_destination"], tranche_de(c["poids_kg"]), SRV[c["service"]]
        prix = GRILLE[z][t][0]
        remise = 10 if rng.random() < 0.12 else 0
        montant = (prix * s[3] * (100 - remise) + 50000) // 100000 * 10
        jf = c["date_livraison"] + timedelta(days=rng.choice([0, 0, 1, 1, 2]))
        h = f"{rng.randint(8, 18):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}"
        if rng.random() < 0.025:   # facture fausse annulée, puis refaite
            faux = GRILLE[z][min(t + 1, 3)][0] * s[3] // 100 + 1000
            fact.append({"colis_id": c["colis_id"], "jour": jf, "h": "07:30:00",
                         "montant": faux, "statut": "ANNULEE", "_colis": c})
        fact.append({"colis_id": c["colis_id"], "jour": jf, "h": h, "montant": montant,
                     "statut": rng.choice(["PAYEE", "PAYEE", "PAYEE", "EMISE"]), "_colis": c})
        retard = max(0, (c["date_livraison"] - c["date_promise"]).days)
        c["_facture"] = montant
        c["_penalite"] = 0
        if retard > 0 and s[5] > 0:
            p = (montant * s[5] * min(retard, 5) + 50) // 100
            statut = "ANNULEE" if rng.random() < 0.10 else "APPLIQUEE"
            pen.append({"colis_id": c["colis_id"], "jour": jf, "jr": retard, "montant": p, "statut": statut, "_colis": c})
            if statut == "APPLIQUEE":
                c["_penalite"] = p
    for cid, j in orphelins:
        fact.append({"colis_id": cid, "jour": j, "h": "11:11:00", "montant": 9500, "statut": "EMISE", "_colis": None})
    for cid, j in orphelins_pen:
        pen.append({"colis_id": cid, "jour": j, "jr": 2, "montant": 950, "statut": "APPLIQUEE", "_colis": None})
    fact.sort(key=lambda f: (f["jour"], f["h"], f["colis_id"], f["statut"] != "ANNULEE"))
    pen.sort(key=lambda p: (p["jour"], p["colis_id"]))
    for i, f in enumerate(fact, 1):
        f.update(id=i, numero_facture=f"FA26-{i:06d}")
    for i, p in enumerate(pen, 1):
        p.update(id=i, numero_penalite=f"PE26-{i:05d}")
    return fact, pen


def versions_agences(avec_changement: bool) -> list[dict]:
    vs = []
    for k, (code, nom, ville, zone, depuis, _v, _p) in enumerate(AGENCES, 1):
        fin = CHANGEMENT[2].isoformat() if (avec_changement and code == CHANGEMENT[0]) else None
        vs.append({"agence_key": k, "agence_id": code, "nom": nom, "ville": ville, "zone": zone,
                   "valid_from": depuis, "valid_to": fin})
    if avec_changement:
        a = next(x for x in AGENCES if x[0] == CHANGEMENT[0])
        vs.append({"agence_key": len(AGENCES) + 1, "agence_id": a[0], "nom": a[1], "ville": a[2], "zone": CHANGEMENT[1],
                   "valid_from": CHANGEMENT[2].isoformat(), "valid_to": None})
    return vs


def dims_fixes() -> dict[str, list[dict]]:
    ds = [{"service_key": k, "service_id": s[0], "libelle": s[1], "delai_promis_jours": s[2],
           "coefficient_prix_pct": s[3]} for k, s in enumerate(SERVICES, 1)]
    dt = []
    for zi, (z, lib) in enumerate(ZONES):
        for ti, t in enumerate(TRANCHES):
            dt.append({"tarif_key": zi * len(TRANCHES) + ti + 1, "tarif_id": f"{z}-{t[0]}", "zone_destination": lib,
                       "tranche": t[0], "tranche_libelle": t[1], "poids_min_grammes": t[2], "poids_max_grammes": t[3],
                       "prix_millimes": GRILLE[z][ti][0], "cout_transporteur_millimes": GRILLE[z][ti][1]})
    return {"dim_service": ds, "dim_tarif": dt}


def ligne_fait(c: dict, vs: list[dict]) -> dict:
    zi = [z for z, _ in ZONES].index(c["zone_destination"])
    ti = tranche_de(c["poids_kg"])
    retard = (c["date_livraison"] - c["date_promise"]).days
    return {"colis_id": c["colis_id"], "date_key": date_key(c["date_livraison"]),
            "agence_key": cle_version(vs, "agence_id", "agence_key", c["agence"], c["date_livraison"]),
            "service_key": [s[0] for s in SERVICES].index(c["service"]) + 1, "tarif_key": zi * len(TRANCHES) + ti + 1,
            "date_expedition": c["date_expedition"].isoformat(), "date_promise": c["date_promise"].isoformat(),
            "poids_grammes": c["poids_kg"], "retard_jours": max(0, retard), "a_l_heure": int(retard <= 0),
            "montant_facture_millimes": c["_facture"], "penalite_millimes": c["_penalite"],
            "cout_transporteur_millimes": GRILLE[c["zone_destination"]][ti][1]}


def tables_verite(colis: list[dict], avec_changement: bool) -> dict[str, list[dict]]:
    vs = versions_agences(avec_changement)
    return {"dim_agence": vs, **dims_fixes(), "fact_colis": [ligne_fait(c, vs) for c in colis]}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_tarifs(chemin) -> None:
    grille = []
    for zi, (z, _lib) in enumerate(ZONES):
        for ti, t in enumerate(TRANCHES):
            prix, cout = GRILLE[z][ti]
            k = zi * 4 + ti
            prix_cell = prix / 1000 if k % 3 != 1 else format_montant(prix, "virgule3")
            cout_cell = cout / 1000 if k % 5 != 2 else format_montant(cout, "virgule_court")
            grille.append([" su" if (z, t[0]) == ("SU", "T3") else z, t[0], prix_cell, cout_cell])
    ecrire_excel(chemin, [
        Feuille("Grille", ["Zone", "Tranche", "Prix facturé (TND)", "Coût transporteur (TND)"], grille,
                titres=["Colis Rapide — grille tarifaire 2026, service Standard (montants en TND)"]),
        Feuille("Tranches", ["Tranche", "Libellé", "Poids min (kg, exclu)", "Poids max (kg, inclus)"],
                [[t[0], t[1], t[2] // 1000, t[3] // 1000] for t in TRANCHES]),
        Feuille("Zones", ["Code zone", "Libellé zone"], [list(z) for z in ZONES]),
        Feuille("Services", ["Code service", "Libellé", "Délai promis (jours)", "Coefficient prix (%)"],
                [[s[0], s[1], s[2], s[3]] for s in SERVICES])])


def ecrire_agences(chemin, avec_changement: bool, extrait_le: str) -> None:
    ags = []
    for code, nom, ville, zone, depuis, _v, _p in AGENCES:
        d = depuis if code != "GAB" else date.fromisoformat(depuis).strftime("%d/%m/%Y")
        hist = [{"zone": zone, "valide_depuis": d}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"zone": CHANGEMENT[1], "valide_depuis": CHANGEMENT[2].isoformat()})
        ags.append({"code": code, "nom": nom, "ville": ville, "historique": hist})
    ecrire_json(chemin, {"source": "Référentiel des agences Colis Rapide", "extrait_le": extrait_le, "agences": ags})


DDL_FACTURATION = """
CREATE TABLE facture (
  id INTEGER PRIMARY KEY,
  numero_facture TEXT NOT NULL UNIQUE,
  colis_id TEXT NOT NULL,
  date_facture TEXT NOT NULL,
  montant_facture REAL NOT NULL,
  statut TEXT NOT NULL CHECK (statut IN ('EMISE', 'PAYEE', 'ANNULEE'))
);
CREATE TABLE penalite (
  id INTEGER PRIMARY KEY,
  numero_penalite TEXT NOT NULL UNIQUE,
  colis_id TEXT NOT NULL,
  jours_retard INTEGER NOT NULL,
  montant_penalite REAL NOT NULL,
  statut TEXT NOT NULL CHECK (statut IN ('APPLIQUEE', 'ANNULEE'))
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""


def ecrire_facturation(chemin, fact: list[dict], pen: list[dict], perimetre: str, genere_le: str) -> None:
    ecrire_sqlite(chemin, DDL_FACTURATION, {
        "facture": [{"id": f["id"], "numero_facture": f["numero_facture"], "colis_id": f["colis_id"],
                     "date_facture": f"{f['jour'].isoformat()} {f['h']}", "montant_facture": f["montant"] / 1000,
                     "statut": f["statut"]} for f in fact],
        "penalite": [{"id": p["id"], "numero_penalite": p["numero_penalite"], "colis_id": p["colis_id"],
                      "jours_retard": p["jr"], "montant_penalite": p["montant"] / 1000, "statut": p["statut"]}
                     for p in pen],
        "parametre": [{"cle": "export_genere_le", "valeur": genere_le}, {"cle": "perimetre", "valeur": perimetre},
                      {"cle": "devise", "valeur": "TND"},
                      {"cle": "regle_penalite", "valeur": "10 % du montant facturé par jour de retard, au plus 5 jours ; "
                                                          "aucune pénalité pour le service ECO"}]})


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
ECH = [  # (valeurs texte, décision)
    (["CR-E01", "2026-03-02", "2026-03-05", "2026-03-05", "TUN", "GT", "0.800", "STD", "Ariana"], None),
    (["CR-E02", "02/03/2026", "03/03/2026", "03/03/2026", "ARI", "NO", "2,5", "EXP", "Bizerte"], None),
    (["CR-E03", "3 mars 2026", "6 mars 2026", "8 mars 2026", " sfx ", "SU", "5.000", "STD", "Médenine"], None),
    (["CR-E04", "2026-03-04", "2026-03-09", "2026-03-08", "NAB", "sa", "12,75", "ECO", "Monastir"], None),
    (["CR-E05", "2026-03-05", "2026-03-06", "2026-03-09", "SOU", "GT", "1", "EXP", "Tunis"], None),
    (["CR-E05", "2026-03-05", "2026-03-06", "2026-03-09", "SOU", "GT", "1", "EXP", "Tunis"], "doublon_exact"),
    (["CR-E06", "2026-03-06", "2026-03-09", "2026-03-09", "TUN", "NO", "3.2", "STD", "Béja"], "id_conflit"),
    (["CR-E06", "2026-03-06", "2026-03-09", "2026-03-10", "TUN", "NO", "3.2", "STD", "Béja"], "id_conflit"),
    (["", "2026-03-07", "2026-03-10", "2026-03-10", "BIZ", "NO", "1.1", "STD", "Jendouba"], "id_manquant"),
    (["CR-E07", "2026-03-07", "2026-03-10", "2026-03-11", "KAI", "SA", "2.0", "STD", "Kairouan"], "cle_inconnue"),
    (["CR-E08", "2026-03-08", "2026-03-11", "2026-03-11", "GAB", "SU", "-1,200", "STD", "Gabès"], "quantite_invalide"),
    (["CR-E09", "2026-03-09", "2026-03-12", "2026-03-13", "GAB", "SU", "7.4", "STD", "Tozeur"], None),
]
FACT_ECH = [(1, "FA-E01", "CR-E01", "2026-03-05 16:20:00", 7.0, "PAYEE"),
            (2, "FA-E02", "CR-E02", "2026-03-03 18:05:00", 17.25, "EMISE"),
            (3, "FA-E03", "CR-E03", "2026-03-08 09:40:00", 19.5, "ANNULEE"),
            (4, "FA-E04", "CR-E03", "2026-03-09 10:10:00", 14.0, "EMISE"),
            (5, "FA-E05", "CR-E04", "2026-03-08 14:30:00", 20.4, "PAYEE"),
            (6, "FA-E06", "CR-E05", "2026-03-09 11:00:00", 10.5, "EMISE"),
            (7, "FA-E07", "CR-E09", "2026-03-13 17:45:00", 19.5, "EMISE"),
            (8, "FA-E08", "CR-E99", "2026-03-14 09:00:00", 7.0, "EMISE")]
PEN_ECH = [(1, "PE-E01", "CR-E03", 2, 2.8, "APPLIQUEE"), (2, "PE-E02", "CR-E04", 0, 2.04, "ANNULEE"),
           (3, "PE-E03", "CR-E05", 3, 3.15, "APPLIQUEE"), (4, "PE-E04", "CR-E09", 1, 1.95, "APPLIQUEE")]


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "colis.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECH])
    ecrire_tarifs(dossier / "tarifs.xlsx")
    ecrire_agences(dossier / "agences.json", False, "2026-03-31")
    fact = [dict(zip(("id", "numero_facture", "colis_id", "date_facture", "montant_facture", "statut"), f)) for f in FACT_ECH]
    pen = [dict(zip(("id", "numero_penalite", "colis_id", "jours_retard", "montant_penalite", "statut"), p)) for p in PEN_ECH]
    ecrire_sqlite(dossier / "facturation.sqlite", DDL_FACTURATION, {
        "facture": fact, "penalite": pen,
        "parametre": [{"cle": "perimetre", "valeur": "échantillon, colis livrés en mars 2026"}, {"cle": "devise", "valeur": "TND"}]})
    colis = []
    for v, motif in ECH:
        if motif is not None:
            continue
        def d(t):
            if "/" in t:
                return date(int(t[6:]), int(t[3:5]), int(t[:2]))
            if "mars" in t:
                return date(2026, 3, int(t.split()[0]))
            return date.fromisoformat(t)
        colis.append({"colis_id": v[0], "date_expedition": d(v[1]), "date_promise": d(v[2]), "date_livraison": d(v[3]),
                      "agence": v[4].strip().upper(), "zone_destination": v[5].strip().upper(),
                      "poids_kg": round(float(v[6].replace(",", ".")) * 1000), "service": v[7]})
    for c in colis:
        c["_facture"] = round(next(f["montant_facture"] for f in fact if f["colis_id"] == c["colis_id"]
                                   and f["statut"] != "ANNULEE") * 1000)
        c["_penalite"] = sum(round(p["montant_penalite"] * 1000) for p in pen
                             if p["colis_id"] == c["colis_id"] and p["statut"] == "APPLIQUEE")
    tables = tables_verite(colis, False)
    rejets = {"colis.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "facturation.sqlite": {"cle_inconnue": 1}}
    att = calculer_attendu_echantillon(spec, tables, date(2026, 3, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(colis),
                                        "factures_annulees_exclues": 1, "penalites_annulees_exclues": 1})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(colis, tables["fact_colis"], att), encoding="utf-8", newline="\n")
    return att


def md_echantillon(colis, faits, att) -> str:
    i = att["indicateurs"]
    t1 = md_tableau(["Ligne du fichier", "colis_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[3]} · {v[4]!r} · {v[5]} · {v[6]} kg · {v[7]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 6" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECH)])
    lignes = []
    for c, f in zip(colis, faits):
        t = TRANCHES[tranche_de(c["poids_kg"])][0]
        r = (c["date_livraison"] - c["date_promise"]).days
        lignes.append([c["colis_id"], c["date_promise"].isoformat(), c["date_livraison"].isoformat(),
                       f"{r:+d} → {f['retard_jours']}", "oui" if f["a_l_heure"] else "non",
                       f"{c['poids_kg']} g → {t}", f"{c['zone_destination']}-{t}", tnd_fr(f["cout_transporteur_millimes"]),
                       tnd_fr(f["montant_facture_millimes"]), tnd_fr(f["penalite_millimes"])])
    t2 = md_tableau(["colis_id", "Promis", "Livré", "Écart → retard_jours", "À l'heure", "Poids → tranche", "Tarif",
                     "Coût transporteur", "Facturé", "Pénalité"], lignes)
    return f"""# Échantillon Colis Rapide — le calcul à la main

12 lignes de `colis.csv`, la grille tarifaire complète, 7 agences, 8 factures et 4 pénalités dans `facturation.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`colis.csv`)

La ligne 1 du fichier est l'en-tête. Colonnes montrées : date de livraison · agence · zone de destination · poids · service.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue` pour l'agence `KAI`, 1 `quantite_invalide` pour le poids `-1,200`) → **{len(colis)} colis gardés**.

## 2. Retard, tranche, coût et facture de chaque colis

- Écart = date livrée − date promise. `retard_jours` = l'écart s'il est positif, sinon 0. **Livré le jour promis = à l'heure** (`CR-E01`, `CR-E02`) ; livré en avance aussi (`CR-E04`).
- Tranche : borne basse exclue, borne haute incluse. `1` kg → T1 (`CR-E05`) ; `5.000` kg → T2 (`CR-E03`).
- Le coût transporteur vient de la grille (feuille `Grille`, zone de destination × tranche). Le montant facturé vient de la **facture non annulée** de la base ; la pénalité, des pénalités `APPLIQUEE`.

{t2}

Base `facturation.sqlite` : la facture `FA-E03` de `CR-E03` est `ANNULEE` (elle a été refaite : `FA-E04`, 14,000 TND) ; la pénalité `PE-E02` est `ANNULEE` → ignorées, ce ne sont pas des rejets. La facture `FA-E08` vise le colis `CR-E99`, qui n'existe pas → rejet `cle_inconnue` (source `facturation.sqlite`, numero_ligne 8).

## 3. Les indicateurs

- Colis livrés = **{i['colis_livres']}** ; à l'heure = {i['colis_a_l_heure']} (CR-E01, CR-E02, CR-E04) ; en retard = {i['colis_livres'] - i['colis_a_l_heure']}.
- Ponctualité = {i['colis_a_l_heure']} / {i['colis_livres']} = **{pct_fr(i['ponctualite'])}**.
- Retard moyen = jours de retard des colis en retard / nombre de colis en retard = (2 + 3 + 1) / 3 = **{jours_fr(i['retard_moyen_jours'])}**. Les colis à l'heure ne comptent pas.
- Montant facturé = {tnd_fr(i['montant_facture_millimes'])} ; pénalités (10 % du montant facturé par jour de retard, service ECO exempté) = 20 % × 14,000 + 30 % × 10,500 + 10 % × 19,500 = 2,800 + 3,150 + 1,950 = {tnd_fr(i['penalites_millimes'])}.
- Revenu facturé net de pénalités = **{tnd_fr(i['revenu_net_millimes'])}**.
- Coût transporteur = **{tnd_fr(i['cout_transporteur_millimes'])}**.
- Marge de livraison = revenu net − coût transporteur = **{tnd_fr(i['marge_livraison_millimes'])}** (marge partielle, pas un bénéfice).

## 4. Ce que doit contenir l'entrepôt de l'échantillon

`fact_colis` : {att['tables']['fact_colis']} lignes · `dim_agence` : {att['tables']['dim_agence']} · `dim_service` : {att['tables']['dim_service']} · `dim_tarif` : {att['tables']['dim_tarif']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- compléments de la référence
def facturation_ignoree(attendus: dict) -> str:
    """Lignes de facturation.sqlite ignorées (pas des rejets), par lot : annulées et déjà chargées au lot 2."""
    cles = [("factures_annulees_exclues", "Factures `ANNULEE` ignorées"),
            ("penalites_annulees_exclues", "Pénalités `ANNULEE` ignorées"),
            ("factures_deja_chargees", "Factures de colis déjà chargés (recopiées au lot 2)"),
            ("penalites_deja_chargees", "Pénalités `APPLIQUEE` de colis déjà chargés (recopiées au lot 2)")]
    return ("\n## Facturation : lignes ignorées (ce ne sont pas des rejets)\n\n"
            + md_tableau(["Lignes de `facturation.sqlite`"] + list(attendus),
                         [[lib] + [a["nettoyage"]["facturation.sqlite"].get(k, 0) for a in attendus.values()]
                          for k, lib in cles]) + "\n")


# --------------------------------------------------------------------------- programme principal
def main(argv: list[str]) -> None:
    spec = MissionSpec(complement_reference=facturation_ignoree, **SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    colis1 = generer_colis(rng, LOT1, 2080, 100001)
    colis2 = generer_colis(rng, LOT2, 410, int(colis1[-1]["colis_id"][2:]) + 1)
    fact, pen = facturer(rng, colis1 + colis2,
                         [("CR777001", date(2026, 2, 11)), ("CR777002", date(2026, 4, 3)), ("CR777003", date(2026, 6, 8)),
                          ("CR777101", date(2026, 8, 5))],
                         [("CR777004", date(2026, 3, 19)), ("CR777005", date(2026, 5, 27)), ("CR777102", date(2026, 7, 22))])

    b1 = construire_csv(colis1, CHAMPS, DOSES["lot1"], rng, lambda k: f"CR9{k:05d}")
    par_id = {c["colis_id"]: c for c in colis1}
    gardees = [l for l in b1.lignes if l.motif is None]
    rejouees = [l.valeurs for l in gardees if par_id[l.origine]["date_livraison"] >= date(2026, 6, 30)]
    if len(rejouees) < 10:
        rejouees = [l.valeurs for l in gardees if par_id[l.origine]["date_livraison"] >= date(2026, 6, 29)]
    rejouees = rejouees[-18:]
    ids_rejoues = {v["colis_id"] for v in rejouees}
    assert 10 <= len(rejouees) <= 20, len(rejouees)
    b2 = construire_csv(colis2, CHAMPS, DOSES["lot2"], rng, lambda k: f"CR8{k:05d}", rejouees)
    for b in (b1, b2):   # le poids joue le rôle de la quantité : valeurs invalides propres à la mission
        for k, l in enumerate(x for x in b.lignes if x.motif == "quantite_invalide"):
            l.valeurs["poids_kg"] = POIDS_INVALIDES[k % len(POIDS_INVALIDES)]

    ids1, ids2 = {c["colis_id"] for c in colis1}, {c["colis_id"] for c in colis2}
    def du_lot(rows, ids, orph_lot):
        return [x for x in rows if x["colis_id"] in ids or (x["_colis"] is None and orph_lot(x["jour"]))]
    f1 = du_lot(fact, ids1, lambda j: j <= LOT1.fin)
    p1 = du_lot(pen, ids1, lambda j: j <= LOT1.fin)
    f2 = du_lot(fact, ids2 | ids_rejoues, lambda j: j > LOT1.fin)
    p2 = du_lot(pen, ids2 | ids_rejoues, lambda j: j > LOT1.fin)
    for lot, b, avec, ff, pp, extrait, perim in (
            ("lot1", b1, False, f1, p1, "2026-06-30", "factures des colis livrés du 2026-01-01 au 2026-06-30"),
            ("lot2", b2, True, f2, p2, "2026-08-31", "factures des colis livrés du 2026-06-30 au 2026-08-31")):
        d = dossier / "sources" / lot
        ecrire_csv(d / "colis.csv", ENTETE, [l.valeurs for l in b.lignes])
        ecrire_tarifs(d / "tarifs.xlsx")
        ecrire_agences(d / "agences.json", avec, extrait)
        ecrire_facturation(d / "facturation.sqlite", ff, pp, perim,
                           (date.fromisoformat(extrait) + timedelta(days=1)).isoformat())

    lots = []
    for lot, b, ff, pp, cumul, nouveaux, avec in ((LOT1, b1, f1, p1, colis1, ids1, False),
                                                   (LOT2, b2, f2, p2, colis1 + colis2, ids2, True)):
        orph_f = sum(f["_colis"] is None for f in ff)
        orph_p = sum(p["_colis"] is None for p in pp)
        lots.append(LotResultat(
            lot=lot,
            sources={"colis.csv": {"lignes": b.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "tarifs.xlsx": {"feuilles": ["Grille", "Tranches", "Zones", "Services"], "tarifs": 16,
                                     "tranches": len(TRANCHES), "zones": len(ZONES), "services": len(SERVICES),
                                     "ligne_entete_grille": 3},
                     "agences.json": {"agences": len(AGENCES), "versions": len(AGENCES) + int(avec)},
                     "facturation.sqlite": {"facture": len(ff), "penalite": len(pp),
                                            "factures_annulees": sum(f["statut"] == "ANNULEE" for f in ff),
                                            "penalites_annulees": sum(p["statut"] == "ANNULEE" for p in pp)}},
            nettoyage={"colis.csv": {k: v for k, v in b.compteurs.items() if k != "lignes"},
                       "facturation.sqlite": {
                           "factures_annulees_exclues": sum(f["statut"] == "ANNULEE" for f in ff),
                           "penalites_annulees_exclues": sum(p["statut"] == "ANNULEE" for p in pp),
                           "factures_deja_chargees": sum(f["statut"] != "ANNULEE" and f["colis_id"] in ids_rejoues
                                                         for f in ff) if avec else 0,
                           "penalites_deja_chargees": sum(p["statut"] == "APPLIQUEE" and p["colis_id"] in ids_rejoues
                                                          for p in pp) if avec else 0,
                           "factures_acceptees_nouvelles": sum(f["statut"] != "ANNULEE" and f["colis_id"] in nouveaux
                                                               for f in ff),
                           "penalites_appliquees_nouvelles": sum(p["statut"] == "APPLIQUEE" and p["colis_id"] in nouveaux
                                                                 for p in pp)}},
            rejets={"colis.csv": b.rejets(), "facturation.sqlite": {"cle_inconnue": orph_f + orph_p}},
            tables_verite=tables_verite(cumul, avec),
            increment=None if lot is LOT1 else {
                "fact_colis_ajoutees": len(colis2), "versions_scd2_ajoutees": 1,
                "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin)), "colis_rejoues_ignores": len(rejouees)}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(nouveaux)
        assert all(sum(f["colis_id"] == c and f["statut"] != "ANNULEE" for f in ff) == 1 for c in nouveaux)

    attendus = produire_reference(spec, lots)
    # double contrôle Python pur (sans SQL) des nombres clés
    tous = colis1 + colis2
    ind = attendus["lot2"]["indicateurs"]
    alh = sum(c["date_livraison"] <= c["date_promise"] for c in tous)
    jr = sum(max(0, (c["date_livraison"] - c["date_promise"]).days) for c in tous)
    net = sum(c["_facture"] - c["_penalite"] for c in tous)
    cout = sum(GRILLE[c["zone_destination"]][tranche_de(c["poids_kg"])][1] for c in tous)
    assert ind["colis_a_l_heure"] == alh and ind["revenu_net_millimes"] == net
    assert ind["marge_livraison_millimes"] == net - cout
    assert abs(ind["retard_moyen_jours"] - round(jr / (len(tous) - alh), 6)) < 1e-9

    ech = produire_echantillon(spec, dossier / "echantillon")
    exporter_v7_data(spec, ech, attendus)
    ent_c = ["lot", "colis_id", "date_expedition", "date_promise", "date_livraison", "agence", "zone_destination",
             "poids_grammes", "service", "montant_facture_millimes", "penalite_millimes"]
    ecrire_verite_privee(spec, {
        "colis_verite.csv": (ent_c, [{"lot": "lot1" if c["colis_id"] in ids1 else "lot2", **c,
                                      "date_expedition": c["date_expedition"].isoformat(),
                                      "date_promise": c["date_promise"].isoformat(),
                                      "date_livraison": c["date_livraison"].isoformat(), "poids_grammes": c["poids_kg"],
                                      "montant_facture_millimes": c["_facture"], "penalite_millimes": c["_penalite"]}
                                     for c in tous]),
        "grille_verite.csv": (["zone_destination", "tranche", "poids_min_grammes", "poids_max_grammes", "prix_millimes",
                               "cout_transporteur_millimes"],
                              [{"zone_destination": z, "tranche": t[0], "poids_min_grammes": t[2], "poids_max_grammes": t[3],
                                "prix_millimes": GRILLE[z][i][0], "cout_transporteur_millimes": GRILLE[z][i][1]}
                               for z, _ in ZONES for i, t in enumerate(TRANCHES)]),
        "agences_verite.csv": (["agence_id", "zone", "valid_from", "valid_to"], versions_agences(True)),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : colis.csv {a['sources']['colis.csv']['lignes']} lignes · fact_colis {a['tables']['fact_colis']} · "
              f"rejets {a['rejets']['par_source']} · ponctualité {pct_fr(i['ponctualite'])} · "
              f"retard moyen {jours_fr(i['retard_moyen_jours'])} · revenu net {tnd_fr(i['revenu_net_millimes'])} · "
              f"coût {tnd_fr(i['cout_transporteur_millimes'])} · marge {tnd_fr(i['marge_livraison_millimes'])}")
    e = ech["indicateurs"]
    print(f"  échantillon : ponctualité {pct_fr(e['ponctualite'])} · retard moyen {jours_fr(e['retard_moyen_jours'])} · "
          f"revenu net {tnd_fr(e['revenu_net_millimes'])} · marge {tnd_fr(e['marge_livraison_millimes'])}")


TABLES = [
    table_dim_date(),
    Table("dim_agence", "dimension_scd2", "Agences avec l'historique de leur zone de rattachement (SCD2).", [
        Colonne("agence_key", "INTEGER", "Clé technique d'une VERSION d'agence.", cle=True),
        Colonne("agence_id", "TEXT", "Code agence normalisé, ex. `NAB` (plusieurs versions possibles)."),
        Colonne("nom", "TEXT", "Nom de l'agence."),
        Colonne("ville", "TEXT", "Ville de l'agence."),
        Colonne("zone", "TEXT", "Zone de rattachement de cette version, ex. `Nord`."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="agence_id"),
    Table("dim_service", "dimension", "Les trois services (feuille Services).", [
        Colonne("service_key", "INTEGER", "Clé technique (1, 2, 3).", cle=True),
        Colonne("service_id", "TEXT", "Code service normalisé : `STD`, `EXP`, `ECO`."),
        Colonne("libelle", "TEXT", "Libellé, ex. `Express`."),
        Colonne("delai_promis_jours", "INTEGER", "Délai promis au client en jours."),
        Colonne("coefficient_prix_pct", "INTEGER", "Coefficient appliqué au prix de la grille, en % (Express = 150)."),
    ], cle_metier="service_id"),
    Table("dim_tarif", "dimension", "Grille tarifaire : une ligne par zone de destination × tranche de poids (16 lignes).", [
        Colonne("tarif_key", "INTEGER", "Clé technique.", cle=True),
        Colonne("tarif_id", "TEXT", "Code zone + `-` + code tranche, ex. `SU-T3`."),
        Colonne("zone_destination", "TEXT", "Libellé de la zone de destination (feuille Zones), ex. `Sud`."),
        Colonne("tranche", "TEXT", "Code tranche de poids : `T1` … `T4`."),
        Colonne("tranche_libelle", "TEXT", "Libellé de la tranche (feuille Tranches)."),
        Colonne("poids_min_grammes", "INTEGER", "Borne basse de la tranche en grammes (exclue)."),
        Colonne("poids_max_grammes", "INTEGER", "Borne haute de la tranche en grammes (incluse)."),
        Colonne("prix_millimes", "INTEGER", "Prix de la grille (service Standard) en millimes."),
        Colonne("cout_transporteur_millimes", "INTEGER", "Coût transporteur en millimes."),
    ], cle_metier="tarif_id"),
    Table("fact_colis", "fait", "Un colis livré accepté, complété par sa facture et ses pénalités.", [
        Colonne("colis_id", "TEXT", "Numéro du colis (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour de LIVRAISON (date du fait).", ref="dim_date.date_key"),
        Colonne("agence_key", "INTEGER", "Version de l'agence valable à la date de livraison.", ref="dim_agence.agence_key"),
        Colonne("service_key", "INTEGER", "Service du colis.", ref="dim_service.service_key"),
        Colonne("tarif_key", "INTEGER", "Ligne de grille : zone de destination × tranche du poids.", ref="dim_tarif.tarif_key"),
        Colonne("date_expedition", "TEXT", "Date d'expédition ISO AAAA-MM-JJ."),
        Colonne("date_promise", "TEXT", "Date de livraison promise ISO AAAA-MM-JJ."),
        Colonne("poids_grammes", "INTEGER", "Poids en grammes entiers (0 < poids ≤ 30 000)."),
        Colonne("retard_jours", "INTEGER", "max(0, date_livraison − date_promise) en jours calendaires."),
        Colonne("a_l_heure", "INTEGER", "1 si date_livraison ≤ date_promise, sinon 0."),
        Colonne("montant_facture_millimes", "INTEGER", "Montant de la facture EMISE ou PAYEE du colis, en millimes."),
        Colonne("penalite_millimes", "INTEGER", "Somme des pénalités APPLIQUEE du colis, en millimes (0 si aucune)."),
        Colonne("cout_transporteur_millimes", "INTEGER", "Coût de la grille pour ce tarif, en millimes."),
    ]),
]

if __name__ == "__main__":
    main(sys.argv[1:])
