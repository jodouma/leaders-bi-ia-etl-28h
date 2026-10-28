"""Mission M03 — Distribution B2B : Medina Distribution (grossiste, factures et avoirs).

    python authoring/generateurs/mission03_medina_distribution.py            # depuis github/

Écrit modele-binome/catalogue/M03/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md,
echantillon/, sources/lot1/, sources/lot2/, reference/}, le bloc M03 de v7-data.json et la vérité privée du formateur.
"""
from __future__ import annotations

from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec,
                    table_dim_date, rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv,
                    ecrire_excel, ecrire_json, ecrire_sqlite, preparer_dossier, produire_reference,
                    calculer_attendu_echantillon, exporter_v7_data, ecrire_verite_privee, format_montant,
                    tnd_fr, pct_fr, md_tableau, taille_dossier, TAILLE_MAX_MISSION, entrepot_verite,
                    indicateur_dict, _ind_valeur)
from textes_mission03 import SPEC_TEXTES

GRAINE = 260003
CODE = "M03"
# code, désignation, famille, prix tarif, coût d'achat (millimes), poids de vente, quantité (min, max)
PRODUITS = [("PR01", "Semoule fine — carton 10 × 1 kg", "EPI", 14500, 11900, 14, (1, 12)),
            ("PR02", "Pâtes spaghetti — carton 20 × 500 g", "EPI", 18000, 13200, 14, (1, 12)),
            ("PR03", "Huile végétale — bidon 5 L", "EPI", 21500, 19600, 12, (1, 10)),
            ("PR04", "Sucre blanc — ballot 10 × 1 kg", "EPI", 15000, 13800, 10, (1, 10)),
            ("PR05", "Concentré de tomate — carton 12 × 800 g", "CON", 33600, 24100, 10, (1, 8)),
            ("PR06", "Thon à l'huile — carton 24 × 160 g", "CON", 62400, 45000, 7, (1, 6)),
            ("PR07", "Eau minérale — pack 6 × 1,5 L", "BOI", 3900, 2700, 16, (5, 40)),
            ("PR08", "Jus d'orange — carton 12 × 1 L", "BOI", 27600, 19300, 8, (1, 8)),
            ("PR09", "Lait demi-écrémé — pack 6 × 1 L", "LAI", 8100, 6900, 14, (4, 30)),
            ("PR10", "Yaourt nature — plateau 24 pots", "LAI", 9600, 6700, 10, (2, 16)),
            ("PR11", "Fromage fondu — carton 12 boîtes", "LAI", 30000, 21500, 6, (1, 6)),
            ("PR12", "Savon liquide mains — carton 12 × 500 mL", "HYG", 26400, 16800, 5, (1, 5)),
            ("PR13", "Liquide vaisselle — carton 12 × 1 L", "ENT", 22800, 14900, 6, (1, 6)),
            ("PR14", "Eau de Javel — carton 12 × 1 L", "ENT", 13200, 8600, 6, (1, 6))]
FAMILLES = {"EPI": "Épicerie sèche", "CON": "Conserves", "BOI": "Boissons", "LAI": "Produits laitiers",
            "HYG": "Hygiène", "ENT": "Entretien"}
# code, raison sociale, région, segment, client depuis, poids, remise négociée, facteur de volume
CLIENTS = [("CL01", "Épicerie Ben Ammar", "Tunis", "épicerie", "2022-03-01", 10, 0.03, 0.7),
           ("CL02", "Restaurant Le Golfe", "Sahel", "restaurant", "2023-06-15", 9, 0.12, 0.9),
           ("CL03", "Hôtel Les Dunes", "Sahel", "hôtel", "2021-11-02", 8, 0.08, 1.3),
           ("CL04", "Supérette El Amel", "Cap Bon", "épicerie", "2023-02-01", 10, 0.05, 0.9),
           ("CL05", "Hypermarché Zahra", "Tunis", "grande surface", "2020-09-14", 12, 0.15, 2.2),
           ("CL06", "Restaurant Dar Jasmin", "Tunis", "restaurant", "2024-01-08", 8, 0.06, 0.8),
           ("CL07", "Épicerie Fine Kerkennah", "Sfax", "épicerie", "2022-05-20", 7, 0.02, 0.6),
           ("CL08", "Hôtel Rivage Bleu", "Cap Bon", "hôtel", "2021-04-12", 7, 0.10, 1.2),
           ("CL09", "Marché Plus Sfax", "Sfax", "grande surface", "2022-10-03", 10, 0.13, 1.8),
           ("CL10", "Café-Restaurant Nour", "Sahel", "restaurant", "2024-03-18", 7, 0.04, 0.7)]
SEGMENT_JSON = {"CL05": "Grande Surface", "CL07": "Épicerie "}      # casse / espaces à normaliser
CHANGEMENT = ("CL04", "grande surface", date(2026, 7, 15))
PREFERENCES = {"restaurant": {"EPI": 1.5, "CON": 1.5, "LAI": 1.3, "BOI": 0.8, "HYG": 0.5, "ENT": 0.7},
               "hôtel": {"LAI": 1.5, "BOI": 1.5, "HYG": 1.6, "CON": 0.7},
               "grande surface": {"BOI": 1.3}, "épicerie": {}}
LIGNES_PAR_FACTURE = {"grande surface": (4, 8), "hôtel": (3, 6), "restaurant": (2, 5), "épicerie": (2, 6)}
PRIX_APPEL = {("CL05", "PR03"), ("CL05", "PR04"), ("CL09", "PR03")}  # prix d'appel négociés : marge négative
COMMERCIAUX = ["Hédi", "Sélima", "Néjib", "Amira"]
SAISON = {1: 0.95, 2: 1.0, 3: 1.15, 4: 1.0, 5: 1.05, 6: 1.1, 7: 1.2, 8: 1.15}
MOTIFS_AVOIR = [("DLC", "Date limite trop proche"), ("CASSE", "Produit abîmé à la livraison"),
                ("LITIGE", "Litige qualité"), ("ERRPRIX", "Erreur de prix sur la facture"),
                ("GESTE", "Geste commercial")]
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, janvier → juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 ; recopie les dernières factures du 30 juin ; CL04 change de segment le 2026-07-15")
CHEVAUCHEMENT_CSV = date(2026, 6, 30)      # le lot 2 recopie les lignes de facture de ce jour
CHEVAUCHEMENT_SQL = date(2026, 6, 20)      # la base du lot 2 recopie les avoirs depuis cette date
ENTETE = ["facture_id", "ligne_id", "date_facture", "client", "produit", "quantite", "prix_unitaire_negocie",
          "commercial"]
CHAMPS = ChampsCSV(ENTETE, "ligne_id", "quantite", montants=["prix_unitaire_negocie"], dates=["date_facture"],
                   codes=["client", "produit"], cles_inconnues={"produit": ["PR99", "PR15", "PR00"],
                                                                "client": ["CL99", "CL11"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=4, inconnues=6, quantites=6),
         "lot2": Doses(doublons_exacts=4, conflits=1, manquants=2, inconnues=3, quantites=2)}
ORPHELINS = [("F26-07771-2", date(2026, 3, 17)), ("F26-08815-1", date(2026, 5, 12)), ("F26-09902-4", date(2026, 8, 11))]
COUT = {p[0]: p[4] for p in PRODUITS}
CLI = {c[0]: c for c in CLIENTS}
PROD = {p[0]: p for p in PRODUITS}


# --------------------------------------------------------------------------- vérité terrain
def generer_factures(rng, lot: Lot, n_cible: int, premier_num: int) -> list[dict]:
    js = [d for d in jours(lot.debut, lot.fin) if d.weekday() != 6]          # pas de livraison le dimanche
    poids = [SAISON[d.month] * (0.6 if d.weekday() == 5 else 1.0) for d in js]
    forcees = ([(date(2026, 6, 30), "CL04")] if lot is LOT1 else
               [(date(2026, 7, 10), "CL04"), (date(2026, 7, 14), "CL04"), (date(2026, 7, 15), "CL04")])
    entetes, n = [], 0
    while n < n_cible:
        if forcees:
            d, c = forcees.pop(0)
        else:
            d = rng.choices(js, poids)[0]
            c = rng.choices([x[0] for x in CLIENTS], [x[5] for x in CLIENTS])[0]
        lo, hi = LIGNES_PAR_FACTURE[CLI[c][3]]
        k = rng.randint(lo, hi)
        entetes.append((d, len(entetes), c, k))
        n += k
    lignes = []
    for num, (d, _ordre, c, k) in enumerate(sorted(entetes), premier_num):
        _, _, _, seg, _, _, remise, volume = CLI[c]
        pref = PREFERENCES[seg]
        prods: list[tuple] = []
        while len(prods) < k:
            p = rng.choices(PRODUITS, [x[5] * pref.get(x[2], 1.0) for x in PRODUITS])[0]
            if p not in prods:
                prods.append(p)
        commercial = rng.choice(COMMERCIAUX)
        for j, p in enumerate(prods, 1):
            q = max(1, round(rng.randint(*p[6]) * volume))
            r = remise + (0.05 if rng.random() < 0.08 else 0.0) + (0.10 if (c, p[0]) in PRIX_APPEL else 0.0)
            prix = round(p[3] * (1 - r) / 10) * 10
            lignes.append({"facture_id": f"F26-{num:05d}", "ligne_id": f"F26-{num:05d}-{j}", "date_facture": d,
                           "client": c, "produit": p[0], "quantite": q, "prix_unitaire_negocie": prix,
                           "commercial": commercial})
    return lignes


def _avoir(rng, l: dict, jour: date, type_avoir: str, statut: str) -> dict:
    if type_avoir == "RETOUR":
        q = rng.randint(1, max(1, l["quantite"] // 2))
        montant = q * l["prix_unitaire_negocie"]
        motif = "DLC" if PROD[l["produit"]][2] == "LAI" and rng.random() < 0.7 else rng.choice(["CASSE", "LITIGE"])
    else:
        q = 0
        montant = max(10, round(l["quantite"] * l["prix_unitaire_negocie"] * rng.choice([0.05, 0.08, 0.12]) / 10) * 10)
        motif = rng.choice(["ERRPRIX", "GESTE"])
    return {"ref_ligne_facture": l["ligne_id"], "code_client": l["client"], "date_avoir": jour.isoformat(),
            "type_avoir": type_avoir, "qte_retournee": q, "montant_ht": round(montant / 1000, 3),
            "code_motif": motif, "statut": statut, "_jour": jour, "_ligne": l, "_orphelin": False}


def generer_avoirs(rng, lignes: list[dict]) -> list[dict]:
    bruts = []
    for l in lignes:
        p = 0.035 * (2.5 if PROD[l["produit"]][2] == "LAI" else 1.0) * {"CL02": 3.0, "CL10": 1.5}.get(l["client"], 1.0)
        if l["date_facture"] > LOT1.fin and PROD[l["produit"]][2] == "LAI":
            p *= 1.5                      # été : plus de produits frais abîmés
        if rng.random() < p:
            d = l["date_facture"] + timedelta(days=rng.randint(1, 25))
            if d <= LOT2.fin:
                bruts.append(_avoir(rng, l, d, "REMISE" if rng.random() < 0.3 else "RETOUR", "EMIS"))
    # la règle à clarifier : deux lignes CL04 facturées avant le 15 juillet, avoirs émis après
    cas1 = max((l for l in lignes if l["client"] == "CL04" and l["date_facture"] <= LOT1.fin),
               key=lambda l: (l["date_facture"], l["ligne_id"]))
    cas2 = max((l for l in lignes if l["client"] == "CL04" and l["date_facture"] < CHANGEMENT[2]),
               key=lambda l: (l["date_facture"], l["ligne_id"]))
    bruts = [a for a in bruts if a["_ligne"] not in (cas1, cas2)]
    bruts += [_avoir(rng, cas1, date(2026, 7, 20), "RETOUR", "EMIS"), _avoir(rng, cas2, date(2026, 7, 22), "REMISE", "EMIS")]
    non_emis = ([(l, "ANNULE") for l in rng.sample([x for x in lignes if x["date_facture"] < date(2026, 6, 10)], 4)]
                + [(l, "BROUILLON") for l in rng.sample([x for x in lignes if x["date_facture"] < date(2026, 6, 10)], 2)]
                + [(l, "ANNULE") for l in rng.sample([x for x in lignes if date(2026, 7, 1) <= x["date_facture"] < date(2026, 8, 20)], 2)]
                + [(l, "BROUILLON") for l in rng.sample([x for x in lignes if date(2026, 7, 1) <= x["date_facture"] < date(2026, 8, 20)], 1)])
    for l, s in non_emis:
        bruts.append(_avoir(rng, l, l["date_facture"] + timedelta(days=rng.randint(1, 9)), "RETOUR", s))
    for ref, d in ORPHELINS:
        faux = {"ligne_id": ref, "client": rng.choice(["CL01", "CL06"]), "produit": "PR01", "quantite": 2,
                "prix_unitaire_negocie": 14000}
        a = _avoir(rng, faux, d, "RETOUR", "EMIS")
        a["_orphelin"] = True
        bruts.append(a)
    bruts.sort(key=lambda a: (a["_jour"], a["ref_ligne_facture"], a["statut"]))
    for i, a in enumerate(bruts, 1):
        a.update({"id": i, "numero_avoir": f"AV26-{i:05d}", "saisi_par": f"adv-{rng.randint(1, 3)}"})
    return bruts


def versions_clients(avec_changement: bool) -> list[dict]:
    vs = []
    for k, (code, nom, region, seg, depuis, *_r) in enumerate(CLIENTS, 1):
        fin = CHANGEMENT[2].isoformat() if (avec_changement and code == CHANGEMENT[0]) else None
        vs.append({"client_key": k, "client_id": code, "nom": nom, "segment": seg, "region": region,
                   "valid_from": depuis, "valid_to": fin})
    if avec_changement:
        c = CLI[CHANGEMENT[0]]
        vs.append({"client_key": len(CLIENTS) + 1, "client_id": c[0], "nom": c[1], "segment": CHANGEMENT[1],
                   "region": c[2], "valid_from": CHANGEMENT[2].isoformat(), "valid_to": None})
    return vs


def tables_verite(lignes, avoirs, avec_changement: bool) -> dict[str, list[dict]]:
    vs = versions_clients(avec_changement)
    pk = {p[0]: k for k, p in enumerate(PRODUITS, 1)}

    def ck(code, jour):
        return cle_version(vs, "client_id", "client_key", code, jour)
    ff = [{"ligne_id": l["ligne_id"], "facture_id": l["facture_id"], "date_key": date_key(l["date_facture"]),
           "produit_key": pk[l["produit"]], "client_key": ck(l["client"], l["date_facture"]),
           "quantite": l["quantite"], "prix_negocie_millimes": l["prix_unitaire_negocie"],
           "montant_facture_millimes": l["quantite"] * l["prix_unitaire_negocie"]} for l in lignes]
    fa = [{"avoir_id": a["numero_avoir"], "ligne_id": a["ref_ligne_facture"], "date_key": date_key(a["_jour"]),
           "date_facture_key": date_key(a["_ligne"]["date_facture"]), "produit_key": pk[a["_ligne"]["produit"]],
           "client_key": ck(a["_ligne"]["client"], a["_ligne"]["date_facture"]),       # règle A : version de la facture
           "type_avoir": a["type_avoir"], "quantite": a["qte_retournee"],
           "montant_millimes": round(a["montant_ht"] * 1000)} for a in avoirs]
    dp = [{"produit_key": k, "produit_id": p[0], "nom": p[1], "famille": FAMILLES[p[2]],
           "cout_achat_millimes": p[4], "prix_tarif_millimes": p[3]} for k, p in enumerate(PRODUITS, 1)]
    return {"dim_produit": dp, "dim_client": vs, "fact_facture": ff, "fact_avoir": fa}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_couts(chemin) -> None:
    lignes = []
    for i, (code, nom, fam, tarif, cout, *_r) in enumerate(PRODUITS):
        cout_cell = cout / 1000 if i % 4 != 2 else format_montant(cout, "virgule3")
        tarif_cell = tarif / 1000 if i % 3 != 1 else format_montant(tarif, "virgule_court")
        lignes.append([" pr07" if code == "PR07" else code, nom, fam, cout_cell, tarif_cell])
    ecrire_excel(chemin, [
        Feuille("Articles", ["Code article", "Désignation", "Famille", "Coût d'achat (TND)", "Prix tarif (TND)"],
                lignes, titres=["Medina Distribution — coûts d'achat et prix tarif 2026 (TND par carton)"]),
        Feuille("Familles", ["Code famille", "Libellé famille"], [[k, v] for k, v in FAMILLES.items()])])


def ecrire_clients(chemin, avec_changement: bool, extrait_le: str) -> None:
    cs = []
    for code, nom, region, seg, depuis, *_r in CLIENTS:
        hist = [{"segment": SEGMENT_JSON.get(code, seg), "valide_depuis": depuis}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"segment": CHANGEMENT[1], "valide_depuis": CHANGEMENT[2].isoformat()})
        cs.append({"code": code, "raison_sociale": nom, "region": region, "historique": hist})
    ecrire_json(chemin, {"source": "Fichier clients Medina Distribution", "extrait_le": extrait_le, "clients": cs})


DDL_AVOIRS = """
CREATE TABLE motif_avoir (code_motif TEXT PRIMARY KEY, libelle TEXT NOT NULL);
CREATE TABLE avoir (
  id INTEGER PRIMARY KEY,
  numero_avoir TEXT NOT NULL UNIQUE,
  ref_ligne_facture TEXT NOT NULL,
  code_client TEXT NOT NULL,
  date_avoir TEXT NOT NULL,
  type_avoir TEXT NOT NULL CHECK (type_avoir IN ('RETOUR', 'REMISE')),
  qte_retournee INTEGER NOT NULL,
  montant_ht REAL NOT NULL,
  code_motif TEXT REFERENCES motif_avoir(code_motif),
  statut TEXT NOT NULL CHECK (statut IN ('EMIS', 'ANNULE', 'BROUILLON')),
  saisi_par TEXT
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""
COLS_AVOIR = ["id", "numero_avoir", "ref_ligne_facture", "code_client", "date_avoir", "type_avoir", "qte_retournee",
              "montant_ht", "code_motif", "statut", "saisi_par"]


def ecrire_avoirs(chemin, avoirs: list[dict], du: date, au: date) -> None:
    ecrire_sqlite(chemin, DDL_AVOIRS, {
        "motif_avoir": [{"code_motif": c, "libelle": l} for c, l in MOTIFS_AVOIR],
        "avoir": [{k: a[k] for k in COLS_AVOIR} for a in avoirs],
        "parametre": [{"cle": "export_genere_le", "valeur": (au + timedelta(days=1)).isoformat()},
                      {"cle": "perimetre", "valeur": f"avoirs du {du.isoformat()} au {au.isoformat()}"},
                      {"cle": "devise", "valeur": "TND"}]})


def comptes_avoirs(avoirs: list[dict]) -> dict:
    return {"avoir": len(avoirs), "emis": sum(a["statut"] == "EMIS" for a in avoirs),
            "annules": sum(a["statut"] == "ANNULE" for a in avoirs),
            "brouillons": sum(a["statut"] == "BROUILLON" for a in avoirs), "motif_avoir": len(MOTIFS_AVOIR)}


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
ECHANTILLON = [  # (valeurs texte, décision)
    (["FE-001", "FE-001-1", "2026-03-02", "CL01", "PR01", "4", "14.070", "Hédi"], None),
    (["FE-001", "FE-001-2", "02/03/2026", "CL01", "PR09", "10", "7,860", "Hédi"], None),
    (["FE-002", "FE-002-1", "3 mars 2026", " cl05 ", "PR03", "20", "17.2", "Sélima"], None),
    (["FE-002", "FE-002-2", "2026-03-03", "CL05", "PR07", "40", "3,315", "Sélima"], None),
    (["FE-002", "FE-002-2", "2026-03-03", "CL05", "PR07", "40", "3,315", "Sélima"], "doublon_exact"),
    (["FE-003", "FE-003-1", "2026-03-04", "Cl02", "PR10", "6", "8.450", "Néjib"], None),
    (["FE-004", "FE-004-1", "2026-03-05", "CL08", "PR06", "3", "56,160", "Néjib"], None),
    (["FE-005", "FE-005-1", "2026-03-06", "CL06", "PR13", "5", "21.430", "Hédi"], "id_conflit"),
    (["FE-005", "FE-005-1", "2026-03-06", "CL06", "PR13", "6", "21.430", "Hédi"], "id_conflit"),
    (["FE-006", "", "2026-03-07", "CL01", "PR02", "2", "17.460", "Hédi"], "id_manquant"),
    (["FE-007", "FE-007-1", "2026-03-09", "CL99", "PR01", "1", "14.500", "Sélima"], "cle_inconnue"),
    (["FE-008", "FE-008-1", "2026-03-09", "CL07", "PR12", "0", "25.870", "Amira"], "quantite_invalide"),
]
AVOIRS_ECH = [(1, "AV-0001", "FE-003-1", "CL02", "2026-03-10", "RETOUR", 2, 16.9, "DLC", "EMIS"),
              (2, "AV-0002", "FE-002-1", "CL05", "2026-03-11", "REMISE", 0, 17.2, "ERRPRIX", "EMIS"),
              (3, "AV-0003", "FE-001-2", "CL01", "2026-03-12", "RETOUR", 1, 7.86, "CASSE", "ANNULE"),
              (4, "AV-0004", "FE-099-1", "CL01", "2026-03-13", "RETOUR", 1, 14.5, "CASSE", "EMIS")]


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "factures.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON])
    ecrire_couts(dossier / "couts.xlsx")
    ecrire_clients(dossier / "clients.json", False, "2026-03-31")
    ecrire_avoirs(dossier / "avoirs.sqlite", [dict(zip(COLS_AVOIR[:-1], r), saisi_par="adv-ech")
                                              for r in AVOIRS_ECH], date(2026, 3, 1), date(2026, 3, 31))
    acc = []
    for v, motif in ECHANTILLON:
        if motif is None:
            j = {"2026-03-02": 2, "02/03/2026": 2, "3 mars 2026": 3}.get(v[2], int(v[2][-2:]))
            acc.append({"facture_id": v[0], "ligne_id": v[1], "date_facture": date(2026, 3, j),
                        "client": v[3].strip().upper(), "produit": v[4], "quantite": int(v[5]),
                        "prix_unitaire_negocie": round(float(v[6].replace(",", ".")) * 1000)})
    par_id = {a["ligne_id"]: a for a in acc}
    av = [{"numero_avoir": r[1], "ref_ligne_facture": r[2], "_jour": date.fromisoformat(r[4]), "type_avoir": r[5],
           "qte_retournee": r[6], "montant_ht": r[7], "_ligne": par_id[r[2]]} for r in AVOIRS_ECH if r[9] == "EMIS"
          and r[2] in par_id]
    tables = tables_verite(acc, av, False)
    rejets = {"factures.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "avoirs.sqlite": {"cle_inconnue": 1}}
    att = calculer_attendu_echantillon(spec, tables, date(2026, 3, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(acc),
                                        "avoirs_non_emis_exclus": 1})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(acc, av, att), encoding="utf-8")
    return att


def md_echantillon(acc, av, att) -> str:
    i = att["indicateurs"]
    m3 = lambda m: format_montant(m, "virgule3")
    t1 = md_tableau(["Ligne du fichier", "ligne_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[1] or "(vide)", f"{v[2]} · {v[3]!r} · {v[4]} · qté {v[5]} · prix {v[6]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 5" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    t2 = md_tableau(["ligne_id", "Date ISO", "Client", "Produit", "Calcul", "Montant facturé", "Coût d'achat"],
                    [[a["ligne_id"], a["date_facture"].isoformat(), a["client"], a["produit"],
                      f"{a['quantite']} × {m3(a['prix_unitaire_negocie'])}", tnd_fr(a["quantite"] * a["prix_unitaire_negocie"]),
                      f"{a['quantite']} × {m3(COUT[a['produit']])} = {tnd_fr(a['quantite'] * COUT[a['produit']])}"]
                     for a in acc])
    cout_f = sum(a["quantite"] * COUT[a["produit"]] for a in acc)
    cout_r = sum(x["qte_retournee"] * COUT[x["_ligne"]["produit"]] for x in av)
    return f"""# Échantillon Medina Distribution — le calcul à la main

12 lignes de `factures.csv`, le fichier des coûts complet, 10 clients, 4 avoirs dans `avoirs.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`factures.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées**.

## 2. Montant facturé et coût d'achat

Une virgule ou un point sépare les décimales : `7,860` = `7.860` = 7 860 millimes ; `17.2` = 17 200 millimes. Le prix est le prix **négocié** de la ligne, pas le prix tarif.

{t2}

**Montant facturé = {tnd_fr(i['montant_facture_millimes'])}** ({i['montant_facture_millimes']} millimes). Coût d'achat des cartons facturés = {tnd_fr(cout_f)}.

Remarque : la ligne `FE-002-1` (huile végétale vendue 17,200 TND à l'Hypermarché Zahra) est vendue **sous** son coût d'achat (19,600 TND) : c'est un prix d'appel négocié.

## 3. Avoirs (`avoirs.sqlite`, table `avoir`)

- `AV-0001` : `RETOUR` de 2 plateaux de yaourt (ligne `FE-003-1`, CL02), statut `EMIS` → **16,900 TND gardés** ; 2 cartons repris.
- `AV-0002` : `REMISE` sur la ligne `FE-002-1` (erreur de prix), 0 carton, statut `EMIS` → **17,200 TND gardés**.
- `AV-0003` : statut `ANNULE` → ignoré (ce n'est pas un rejet).
- `AV-0004` : la ligne `FE-099-1` n'existe pas → rejet `cle_inconnue` (source `avoirs.sqlite`).

**Avoirs = {tnd_fr(i['avoirs_millimes'])}.**

## 4. Ventes nettes, coût d'achat, marge commerciale, taux d'avoir

- Ventes nettes = montant facturé − avoirs = {tnd_fr(i['montant_facture_millimes'])} − {tnd_fr(i['avoirs_millimes'])} = **{tnd_fr(i['ventes_nettes_millimes'])}**.
- Cartons repris : 2 × {m3(COUT['PR10'])} (coût du yaourt) = {tnd_fr(cout_r)}. La `REMISE` ne reprend aucun carton.
- Coût d'achat des unités nettes = {tnd_fr(cout_f)} − {tnd_fr(cout_r)} = **{tnd_fr(i['cout_achat_net_millimes'])}**.
- Marge commerciale = ventes nettes − coût d'achat des unités nettes = **{tnd_fr(i['marge_commerciale_millimes'])}**.
- Taux d'avoir = avoirs / montant facturé = {i['avoirs_millimes']} / {i['montant_facture_millimes']} = **{pct_fr(i['taux_avoir'])}**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_facture` : {att['tables']['fact_facture']} lignes · `fact_avoir` : {att['tables']['fact_avoir']} lignes · `dim_produit` : {att['tables']['dim_produit']} · `dim_client` : {att['tables']['dim_client']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- cas de démonstration (référence)
def cas_demo(spec, lr, produit: str = "PR03", client: str = "CL05"):
    """Indicateurs du croisement produit × client demandé par la démonstration (depuis la vérité, après le lot 2)."""
    inds = [indicateur_dict(i) for i in spec.indicateurs]
    con = entrepot_verite(spec, lr.tables_verite, lr.lot.fin)
    ligne = con.execute(f"WITH mouvements AS ({spec.vue_analyse}) SELECT "
                        + ", ".join(f"{i['sql']} AS {i['code']}" for i in inds)
                        + " FROM mouvements WHERE produit_id = ? AND client_id = ?", (produit, client)).fetchone()
    con.close()
    table = md_tableau(["Indicateur", f"{produit} × {client} (après lot2)", "code"],
                       [[i["libelle"], _ind_valeur(i, v), f"`{i['code']}`"] for i, v in zip(inds, ligne)])
    return lambda _attendus: (f"\n## Cas de démonstration : produit `{produit}` × client `{client}`\n\n"
                              f"Valeurs à retrouver dans l'application avec les filtres Produit = `{produit}` et Client = "
                              f"`{client}` (toute la période) : la marge commerciale est négative.\n\n{table}\n")


# --------------------------------------------------------------------------- programme principal
def main() -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    lignes1 = generer_factures(rng, LOT1, 2050, 1)
    lignes2 = generer_factures(rng, LOT2, 400, int(lignes1[-1]["facture_id"][4:]) + 1)
    avoirs = generer_avoirs(rng, lignes1 + lignes2)
    a1 = [a for a in avoirs if a["_jour"] <= LOT1.fin]
    a2 = [a for a in avoirs if CHEVAUCHEMENT_SQL <= a["_jour"] <= LOT2.fin]
    assert not any(a["_orphelin"] for a in a1 if a["_jour"] >= CHEVAUCHEMENT_SQL)

    b1 = construire_csv(lignes1, CHAMPS, DOSES["lot1"], rng, lambda k: f"F26-9{k:04d}-9")
    # le lot 2 recopie les dernières factures du 30 juin (export qui se chevauche) : 10 à 20 lignes
    factures_fin = sorted({l["facture_id"] for l in lignes1 if l["date_facture"] >= CHEVAUCHEMENT_CSV}, reverse=True)
    recopiees: set[str] = set()
    for f in factures_fin:
        if sum(l["facture_id"] in recopiees for l in lignes1) >= 10:
            break
        recopiees.add(f)
    facture_de = {l["ligne_id"]: l["facture_id"] for l in lignes1}
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None and facture_de[l.origine] in recopiees]
    assert 10 <= len(rejouees) <= 20, len(rejouees)
    b2 = construire_csv(lignes2, CHAMPS, DOSES["lot2"], rng, lambda k: f"F26-8{k:04d}-9", rejouees)
    for lot, b, avec, aa, extrait in (("lot1", b1, False, a1, "2026-06-30"), ("lot2", b2, True, a2, "2026-08-31")):
        d = dossier / "sources" / lot
        ecrire_csv(d / "factures.csv", ENTETE, [l.valeurs for l in b.lignes])
        ecrire_couts(d / "couts.xlsx")
        ecrire_clients(d / "clients.json", avec, extrait)
        lot_obj = LOT1 if lot == "lot1" else LOT2
        ecrire_avoirs(d / "avoirs.sqlite", aa, CHEVAUCHEMENT_SQL if lot == "lot2" else LOT1.debut, lot_obj.fin)

    def emis(aa, deja=frozenset()):
        return [a for a in aa if a["statut"] == "EMIS" and not a["_orphelin"] and a["numero_avoir"] not in deja]
    acc1 = emis(a1)
    acc2 = emis(a2, {a["numero_avoir"] for a in acc1})
    lots = []
    for lot, b, aa, acc, lignes_cumul, avoirs_cumul, avec in (
            (LOT1, b1, a1, acc1, lignes1, acc1, False), (LOT2, b2, a2, acc2, lignes1 + lignes2, acc1 + acc2, True)):
        lots.append(LotResultat(
            lot=lot,
            sources={"factures.csv": {"lignes": b.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "couts.xlsx": {"feuilles": ["Articles", "Familles"], "produits": len(PRODUITS),
                                    "familles": len(FAMILLES), "ligne_entete_articles": 3},
                     "clients.json": {"clients": len(CLIENTS), "versions": len(CLIENTS) + int(avec)},
                     "avoirs.sqlite": comptes_avoirs(aa)},
            nettoyage={"factures.csv": {k: v for k, v in b.compteurs.items() if k != "lignes"},
                       "avoirs.sqlite": {"avoirs_non_emis_exclus": sum(a["statut"] != "EMIS" for a in aa),
                                         "deja_charges": len(emis(aa)) - len(acc),
                                         "avoirs_acceptes_nouveaux": len(acc)},
                       "clients.json": {"segments_normalises": len(SEGMENT_JSON)}},
            rejets={"factures.csv": b.rejets(), "avoirs.sqlite": {"cle_inconnue": sum(a["_orphelin"] for a in aa)}},
            tables_verite=tables_verite(lignes_cumul, avoirs_cumul, avec),
            increment=None if lot is LOT1 else {
                "fact_facture_ajoutees": len(lignes2), "fact_avoir_ajoutees": len(acc2),
                "versions_scd2_ajoutees": 1, "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin))}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(lignes_cumul) - (0 if lot is LOT1 else len(lignes1))

    spec.complement_reference = cas_demo(spec, lots[-1])
    attendus = produire_reference(spec, lots)
    # double contrôle Python pur (sans SQL) des nombres clés
    t = lots[-1].tables_verite
    fac = sum(f["montant_facture_millimes"] for f in t["fact_facture"])
    av = sum(f["montant_millimes"] for f in t["fact_avoir"])
    cout = sum(l["quantite"] * COUT[l["produit"]] for l in lignes1 + lignes2) - \
        sum(a["qte_retournee"] * COUT[a["_ligne"]["produit"]] for a in acc1 + acc2)
    ind = attendus["lot2"]["indicateurs"]
    assert (ind["ventes_nettes_millimes"], ind["marge_commerciale_millimes"]) == (fac - av, fac - av - cout)
    # la règle A doit changer un résultat (sinon l'oracle ne la contrôle pas)
    croise = [a for a in acc1 + acc2 if a["_ligne"]["client"] == "CL04"
              and a["_ligne"]["date_facture"] < CHANGEMENT[2] <= a["_jour"]]
    assert len(croise) >= 2, croise

    ech = produire_echantillon(spec, dossier / "echantillon")
    exporter_v7_data(spec, ech, attendus)
    lot_de = {l["ligne_id"]: "lot1" for l in lignes1} | {l["ligne_id"]: "lot2" for l in lignes2}
    vs = versions_clients(True)
    ecrire_verite_privee(spec, {
        "factures_verite.csv": (["lot"] + ENTETE[:-1] + ["prix_negocie_millimes"],
                                [{"lot": lot_de[l["ligne_id"]], **l, "date_facture": l["date_facture"].isoformat(),
                                  "prix_negocie_millimes": l["prix_unitaire_negocie"]} for l in lignes1 + lignes2]),
        "avoirs_verite.csv": (["lot", "numero_avoir", "ref_ligne_facture", "produit", "client", "segment_facture",
                               "date_facture", "date_avoir", "type_avoir", "qte", "montant_millimes"],
                              [{"lot": "lot1" if a in acc1 else "lot2", **a, "produit": a["_ligne"]["produit"],
                                "client": a["_ligne"]["client"],
                                "segment_facture": next(v["segment"] for v in vs if v["client_key"] == cle_version(
                                    vs, "client_id", "client_key", a["_ligne"]["client"], a["_ligne"]["date_facture"])),
                                "date_facture": a["_ligne"]["date_facture"].isoformat(), "qte": a["qte_retournee"],
                                "montant_millimes": round(a["montant_ht"] * 1000)} for a in acc1 + acc2]),
        "produits_verite.csv": (["produit_id", "nom", "famille", "cout_achat_millimes", "prix_tarif_millimes"],
                                [{"produit_id": p[0], "nom": p[1], "famille": FAMILLES[p[2]],
                                  "cout_achat_millimes": p[4], "prix_tarif_millimes": p[3]} for p in PRODUITS]),
        "clients_verite.csv": (["client_id", "nom", "segment", "region", "valid_from", "valid_to"], vs),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : factures.csv {a['sources']['factures.csv']['lignes']} lignes · fact_facture "
              f"{a['tables']['fact_facture']} · fact_avoir {a['tables']['fact_avoir']} · rejets {a['rejets']['par_motif']} · "
              f"facturé {tnd_fr(i['montant_facture_millimes'])} · avoirs {tnd_fr(i['avoirs_millimes'])} · "
              f"nettes {tnd_fr(i['ventes_nettes_millimes'])} · marge {tnd_fr(i['marge_commerciale_millimes'])} · "
              f"taux d'avoir {pct_fr(i['taux_avoir'])}")
    e = ech["indicateurs"]
    print(f"  échantillon : facturé {tnd_fr(e['montant_facture_millimes'])} · nettes {tnd_fr(e['ventes_nettes_millimes'])} · "
          f"marge {tnd_fr(e['marge_commerciale_millimes'])} · taux {pct_fr(e['taux_avoir'])}")
    print(f"  lignes rejouées au lot 2 : {len(rejouees)} · avoirs CL04 à cheval sur le 2026-07-15 : {len(croise)}")
    ag = attendus["lot2"]["agregats"]
    for axe in ("par_client", "par_produit", "par_segment"):
        tri = sorted(ag[axe].items(), key=lambda kv: kv[1]["marge_commerciale_millimes"] / kv[1]["ventes_nettes_millimes"])
        print(f"  {axe} (taux de marge croissant) : " + " · ".join(
            f"{k} {pct_fr(v['marge_commerciale_millimes'] / v['ventes_nettes_millimes'], 1)} "
            f"(avoir {pct_fr(v['taux_avoir'], 1)})" for k, v in tri))


TABLES = [
    table_dim_date(),
    Table("dim_produit", "dimension", "Articles : un produit par ligne (feuilles Articles + Familles).", [
        Colonne("produit_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("produit_id", "TEXT", "Code article normalisé (strip + majuscules), ex. `PR03`."),
        Colonne("nom", "TEXT", "Désignation et conditionnement."),
        Colonne("famille", "TEXT", "Libellé de la famille (feuille Familles), ex. `Produits laitiers`."),
        Colonne("cout_achat_millimes", "INTEGER", "Coût d'achat d'un carton en millimes."),
        Colonne("prix_tarif_millimes", "INTEGER", "Prix tarif d'un carton (avant négociation) en millimes."),
    ], cle_metier="produit_id"),
    Table("dim_client", "dimension_scd2", "Clients avec historique du segment (SCD2).", [
        Colonne("client_key", "INTEGER", "Clé technique d'une VERSION de client.", cle=True),
        Colonne("client_id", "TEXT", "Code client, ex. `CL04` (plusieurs versions possibles)."),
        Colonne("nom", "TEXT", "Raison sociale."),
        Colonne("segment", "TEXT", "Segment de cette version : `épicerie`, `restaurant`, `grande surface` ou `hôtel`."),
        Colonne("region", "TEXT", "Région de livraison."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="client_id"),
    Table("fact_facture", "fait", "Une ligne de facture acceptée.", [
        Colonne("ligne_id", "TEXT", "Identifiant de la ligne de facture (clé métier unique).", cle=True),
        Colonne("facture_id", "TEXT", "Numéro de la facture."),
        Colonne("date_key", "INTEGER", "Jour de la facture.", ref="dim_date.date_key"),
        Colonne("produit_key", "INTEGER", "Produit facturé.", ref="dim_produit.produit_key"),
        Colonne("client_key", "INTEGER", "Version du client valable à la date de la facture.",
                ref="dim_client.client_key"),
        Colonne("quantite", "INTEGER", "Cartons facturés (entier > 0)."),
        Colonne("prix_negocie_millimes", "INTEGER", "Prix négocié d'un carton en millimes."),
        Colonne("montant_facture_millimes", "INTEGER", "quantite × prix_negocie_millimes."),
    ]),
    Table("fact_avoir", "fait", "Un avoir EMIS de la gestion commerciale, rattaché à une ligne de facture.", [
        Colonne("avoir_id", "TEXT", "Numéro de l'avoir (`numero_avoir`), clé métier unique.", cle=True),
        Colonne("ligne_id", "TEXT", "Ligne de facture corrigée.", ref="fact_facture.ligne_id"),
        Colonne("date_key", "INTEGER", "Jour de l'avoir (mois de comptage).", ref="dim_date.date_key"),
        Colonne("date_facture_key", "INTEGER", "Jour de la facture d'origine (choisit la version du client).",
                ref="dim_date.date_key"),
        Colonne("produit_key", "INTEGER", "Produit de la ligne de facture.", ref="dim_produit.produit_key"),
        Colonne("client_key", "INTEGER", "Version du client de la ligne de facture (règle A).",
                ref="dim_client.client_key"),
        Colonne("type_avoir", "TEXT", "`RETOUR` (cartons repris) ou `REMISE` (geste sur le prix)."),
        Colonne("quantite", "INTEGER", "Cartons repris (0 pour une REMISE)."),
        Colonne("montant_millimes", "INTEGER", "Montant de l'avoir en millimes."),
    ]),
]

if __name__ == "__main__":
    main()
