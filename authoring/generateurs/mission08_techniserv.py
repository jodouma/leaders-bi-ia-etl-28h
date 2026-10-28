"""Mission M08 — Maintenance · TechniServ (interventions sous contrat : climatisation, ascenseurs, groupes électrogènes).

    python authoring/generateurs/mission08_techniserv.py            # depuis github/

Écrit modele-binome/catalogue/M08/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md, echantillon/,
sources/lot1/, sources/lot2/, reference/} et, si SOLEN_VERITE_PRIVEE est définie,
la vérité brute dans <SOLEN_VERITE_PRIVEE>/M08/ (dossier privé, hors dépôt).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec, table_dim_date,
                    rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv, ecrire_excel, ecrire_json,
                    ecrire_sqlite, preparer_dossier, produire_reference, calculer_attendu_echantillon,
                    exporter_v7_data, ecrire_verite_privee, format_montant, tnd_fr, heures_fr, md_tableau,
                    taille_dossier, MOIS_FR, TAILLE_MAX_MISSION)
from textes_mission08 import (SPEC_TEXTES, EQUIPEMENT_MOBILE, CONTRAT_AVANT, CONTRAT_APRES, DATE_CHANGEMENT,
                              SANS_OBJET)

GRAINE = 260008
CODE = "M08"
CATEGORIES = {"CLIM": ("Climatisation", 45000), "ASC": ("Ascenseur", 62500), "GE": ("Groupe électrogène", 55000)}
TECHNICIENS = {"CLIM": ["T01", "T02", "T03"], "ASC": ["T04", "T05", "T06"], "GE": ["T07", "T08", "T09"]}
# code, désignation, catégorie, prix (millimes)
PIECES = [("PC-101", "Filtre à air", "CLIM", 35000), ("PC-102", "Gaz réfrigérant R32 (kg)", "CLIM", 48500),
          ("PC-103", "Condensateur de démarrage", "CLIM", 62000), ("PC-104", "Ventilateur intérieur", "CLIM", 210000),
          ("PC-105", "Carte électronique de commande", "CLIM", 385000),
          ("PC-106", "Compresseur 18 000 BTU", "CLIM", 1450000),
          ("PC-201", "Huile de graissage des guides (L)", "ASC", 22750), ("PC-202", "Galet de porte", "ASC", 85000),
          ("PC-203", "Contacteur", "ASC", 145000), ("PC-204", "Bouton palier", "ASC", 28000),
          ("PC-205", "Câble de traction (m)", "ASC", 38750), ("PC-206", "Batterie de secours", "ASC", 165000),
          ("PC-207", "Variateur de fréquence", "ASC", 2350000),
          ("PC-301", "Huile moteur (L)", "GE", 18250), ("PC-302", "Filtre à huile", "GE", 42000),
          ("PC-303", "Filtre à gasoil", "GE", 39500), ("PC-304", "Courroie d'alternateur", "GE", 64000),
          ("PC-305", "Batterie de démarrage 12 V", "GE", 310000), ("PC-306", "Régulateur de tension", "GE", 890000),
          ("PC-307", "Liquide de refroidissement (L)", "GE", 12900)]
PRIX = {p[0]: p[3] for p in PIECES}
# pièces d'un préventif : (code, probabilité, quantité min, max) ; d'un correctif : (code, poids, qmin, qmax)
PREVENTIF = {"CLIM": [("PC-101", .9, 1, 2), ("PC-102", .3, 1, 2)], "ASC": [("PC-201", .9, 1, 3)],
             "GE": [("PC-301", .9, 4, 10), ("PC-302", .9, 1, 1), ("PC-303", .5, 1, 1), ("PC-307", .3, 2, 5)]}
CORRECTIF = {"CLIM": [("PC-102", 30, 1, 3), ("PC-103", 25, 1, 1), ("PC-104", 15, 1, 1), ("PC-105", 12, 1, 1),
                      ("PC-101", 15, 1, 2), ("PC-106", 3, 1, 1)],
             "ASC": [("PC-202", 25, 1, 2), ("PC-203", 22, 1, 1), ("PC-204", 20, 1, 2), ("PC-205", 12, 5, 20),
                     ("PC-206", 15, 1, 1), ("PC-207", 3, 1, 1)],
             "GE": [("PC-304", 30, 1, 1), ("PC-305", 20, 1, 1), ("PC-302", 20, 1, 1), ("PC-303", 15, 1, 1),
                    ("PC-306", 5, 1, 1), ("PC-307", 10, 2, 5)]}
DESIGNATIONS = {"CLIM": ["Climatiseur split 18 000 BTU", "Climatiseur gainable 48 000 BTU", "Groupe d'eau glacée",
                         "Centrale de traitement d'air"],
                "ASC": ["Ascenseur 8 personnes", "Ascenseur 630 kg", "Monte-charge 1 000 kg"],
                "GE": ["Groupe électrogène 100 kVA", "Groupe électrogène 250 kVA", "Groupe électrogène 60 kVA"]}
# contrat, client, site, début, fin, facteur de revenu (revenu ≈ coût mensuel moyen × facteur), parc [(cat, fragilité)]
CONTRATS = [
    ("CT-01", "SCI Tour Azuria", "Tour Azuria — Tunis", "2024-01-01", None, 1.35,
     [("CLIM", 1), ("CLIM", 1), ("CLIM", 1), ("ASC", 1), ("ASC", 1), ("GE", 1)]),
    ("CT-02", "Clinique Les Glycines", "Clinique Les Glycines — Ariana", "2023-06-01", "2026-12-31", 1.25,
     [("CLIM", 1), ("CLIM", 1), ("ASC", 1), ("ASC", 1), ("GE", 1), ("GE", 1)]),
    ("CT-03", "Groupe Nakhla", "Résidences Nakhla — Les Berges", "2024-09-01", None, 0.80,
     [("CLIM", 1), ("ASC", 1.4), ("ASC", 1.2), ("ASC", 1), ("GE", 2.5)]),
    ("CT-04", "Hôtel Corail Bleu", "Hôtel Corail Bleu — Hammamet", "2025-02-01", None, 1.20,
     [("CLIM", 1), ("CLIM", 3), ("CLIM", 1), ("ASC", 1), ("ASC", 1), ("GE", 1)]),
    ("CT-05", "Centre commercial Zéphyr", "Centre Zéphyr — Sousse", "2023-01-01", None, 1.10,
     [("CLIM", 1), ("CLIM", 1), ("CLIM", 1), ("ASC", 1), ("ASC", 1), ("ASC", 4), ("GE", 1)]),
    ("CT-06", "École Les Amandiers", "École Les Amandiers — Ben Arous", "2025-09-01", None, 0.95,
     [("CLIM", 1), ("CLIM", 1), ("GE", 1)]),
    ("CT-07", "Entrepôts Frigo Sud", "Frigo Sud — Sfax", "2024-04-01", None, 1.30,
     [("CLIM", 1.5), ("CLIM", 1.5), ("GE", 1), ("GE", 1)]),
    ("CT-08", "Résidence Belle Rive", "Résidence Belle Rive — La Marsa", "2026-03-01", None, 1.15,
     [("CLIM", 1), ("ASC", 1), ("ASC", 1)]),
    ("CT-09", "Groupe Nakhla", "Résidences Nakhla — Les Jardins", "2025-11-01", None, 1.50,
     [("ASC", 1), ("GE", 1), ("GE", 1)]),
    ("CT-10", "Centre de données Altaïr", "Centre Altaïr — Monastir", "2025-05-01", None, 1.10,
     [("CLIM", 1.2), ("CLIM", 1.2), ("CLIM", 1.2), ("GE", 1), ("GE", 1)]),
]
STYLES_REVENU = ["milliers", "point3", "virgule3", "court", "milliers", "virgule_court", "point3", "milliers",
                 "virgule3", "court"]
SAISON_CLIM = {1: .6, 2: .6, 3: .8, 4: 1.0, 5: 1.3, 6: 1.8, 7: 2.2, 8: 2.3}
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, janvier → juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 ; recopie les interventions du 30 juin ; EQ-017 passe du contrat CT-03 "
           "au contrat CT-09 le 2026-07-15")
CHEVAUCHEMENT = date(2026, 6, 30)              # le lot 2 recopie les interventions (et pièces) de ce jour
ENTETE = ["intervention_id", "equipement", "date_demande", "heure_demande", "date_intervention",
          "heure_intervention", "technicien", "heures", "type_intervention"]
CHAMPS = ChampsCSV(ENTETE, "intervention_id", "heures", dates=["date_demande", "date_intervention"],
                   codes=["equipement", "technicien", "type_intervention"],
                   cles_inconnues={"equipement": ["EQ-099", "EQ-120", "EQ-0I7"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=4, inconnues=5, quantites=6),
         "lot2": Doses(doublons_exacts=3, conflits=1, manquants=2, inconnues=2, quantites=2)}
ORPHELINES = {"lot1": [("INT-26-08812", "PC-302", 1), ("INT-26-08847", "PC-203", 1), ("INT-26-09903", "PC-101", 2)],
              "lot2": [("INT-26-08890", "PC-305", 1), ("INT-26-09951", "PC-202", 1)]}
PIECES_INCONNUES = {"lot1": ["PC-999", "PC-108"], "lot2": []}


# --------------------------------------------------------------------------- parc et contrats
def parc() -> list[dict]:
    eqs, n, vus = [], 0, {}
    for ct, _cl, site, debut, _f, _x, compo in CONTRATS:
        for cat, frag in compo:
            n += 1
            k = vus.get(cat, 0)
            vus[cat] = k + 1
            eqs.append({"id": f"EQ-{n:03d}", "categorie": cat, "designation": DESIGNATIONS[cat][k % len(DESIGNATIONS[cat])],
                        "site": site, "contrat": ct, "depuis": debut, "fragilite": frag})
    return eqs


EQUIPEMENTS = parc()
EQ = {e["id"]: e for e in EQUIPEMENTS}
assert EQ[EQUIPEMENT_MOBILE]["categorie"] == "GE" and EQ[EQUIPEMENT_MOBILE]["contrat"] == CONTRAT_AVANT
assert EQ["EQ-014"]["categorie"] == "ASC" and EQ["EQ-014"]["contrat"] == CONTRAT_AVANT


def versions_equipements(avec_changement: bool) -> list[dict]:
    vs = []
    for k, e in enumerate(EQUIPEMENTS, 1):
        mobile = avec_changement and e["id"] == EQUIPEMENT_MOBILE
        vs.append({"equipement_key": k, "equipement_id": e["id"], "designation": e["designation"],
                   "categorie": CATEGORIES[e["categorie"]][0], "site": e["site"], "contrat_id": e["contrat"],
                   "valid_from": e["depuis"], "valid_to": DATE_CHANGEMENT.isoformat() if mobile else None})
    if avec_changement:
        e = EQ[EQUIPEMENT_MOBILE]
        vs.append({"equipement_key": len(EQUIPEMENTS) + 1, "equipement_id": e["id"], "designation": e["designation"],
                   "categorie": CATEGORIES[e["categorie"]][0], "site": e["site"], "contrat_id": CONTRAT_APRES,
                   "valid_from": DATE_CHANGEMENT.isoformat(), "valid_to": None})
    return vs


def contrat_de(eq: str, jour: date) -> str:
    vs = versions_equipements(True)
    return next(v["contrat_id"] for v in vs if v["equipement_id"] == eq and v["valid_from"] <= jour.isoformat()
                and (v["valid_to"] is None or jour.isoformat() < v["valid_to"]))


def actif_le(ct: tuple, premier: date) -> bool:
    return ct[3] <= premier.isoformat() and (ct[4] is None or ct[4] >= premier.isoformat())


def mois_du_lot(lot: Lot) -> list[date]:
    return [d for d in jours(lot.debut, lot.fin) if d.day == 1]


# --------------------------------------------------------------------------- vérité terrain
def generer_interventions(rng, lot: Lot, n: int, premier: int) -> list[dict]:
    js = jours(lot.debut, lot.fin)
    poids_j = [{5: .5, 6: .15}.get(d.weekday(), 1.0) for d in js]
    evs = []
    for d in rng.choices(js, poids_j, k=n):
        prev = rng.random() < (0.15 if d.month == 8 else 0.38)
        elig = [e for e in EQUIPEMENTS if e["depuis"] <= d.isoformat()]
        if prev:
            e = rng.choice(elig)
        else:
            e = rng.choices(elig, [x["fragilite"] * (SAISON_CLIM[d.month] if x["categorie"] == "CLIM" else 1.0)
                                   for x in elig])[0]
        evs.append(_evenement(rng, e, d, prev))
    if lot is LOT2:                       # le cas de la règle à clarifier, de part et d'autre de la frontière
        evs.append(_evenement(rng, EQ[EQUIPEMENT_MOBILE], date(2026, 7, 14), False, 13, 5))
        evs.append(_evenement(rng, EQ[EQUIPEMENT_MOBILE], date(2026, 7, 15), False, 9, 14))
    evs.sort(key=lambda v: (v["_fin"], v["equipement"], v["_debut"]))
    for i, v in enumerate(evs):
        v["intervention_id"] = f"INT-26-{premier + i:05d}"
    return evs


def _evenement(rng, e: dict, d: date, prev: bool, heure: int | None = None, delai: int | None = None) -> dict:
    cat = e["categorie"]
    if prev:
        fin = datetime(d.year, d.month, d.day, rng.choice([8, 9, 10, 14]))
        debut = datetime.combine(d - timedelta(days=rng.randint(7, 28)), datetime.min.time()).replace(hour=8)
        heures = rng.choice([1, 1, 2, 2, 2, 3])
    else:
        fin = datetime(d.year, d.month, d.day, heure if heure is not None else rng.randint(7, 18))
        if delai is None:
            delai = max(1, int(rng.triangular(*{"ASC": (1, 36, 4), "CLIM": (2, 72, 10), "GE": (1, 48, 6)}[cat])))
        debut = fin - timedelta(hours=delai)
        heures = rng.choice([1, 2, 2, 3, 3, 3, 4, 4, 5, 6])
    return {"intervention_id": None, "equipement": e["id"], "date_demande": debut.date(),
            "heure_demande": debut.strftime("%H:%M"), "date_intervention": fin.date(),
            "heure_intervention": fin.strftime("%H:%M"), "technicien": rng.choice(TECHNICIENS[cat]), "heures": heures,
            "type_intervention": "préventif" if prev else "correctif", "_debut": debut, "_fin": fin, "_cat": cat}


def generer_consommations(rng, evs: list[dict]) -> list[dict]:
    out = []
    for v in evs:
        cat = v["_cat"]
        lignes = []
        if v["type_intervention"] == "préventif":
            lignes = [(c, rng.randint(a, b)) for c, p, a, b in PREVENTIF[cat] if rng.random() < p]
        elif rng.random() < 0.7:
            choix = []
            for _ in range(rng.choice([1, 1, 2])):
                c = rng.choices(CORRECTIF[cat], [x[1] for x in CORRECTIF[cat]])[0]
                if c not in choix:
                    choix.append(c)
            lignes = [(c[0], rng.randint(c[2], c[3])) for c in choix]
        for code, q in lignes:
            out.append({"intervention_id": v["intervention_id"], "code_piece": code, "quantite": q,
                        "saisi_le": (v["_fin"] + timedelta(hours=v["heures"])).strftime("%Y-%m-%d %H:%M")})
    return out


def numeroter(lignes: list[dict], premier: int) -> list[dict]:
    lignes = sorted(lignes, key=lambda c: (c["saisi_le"], c["intervention_id"], c["code_piece"]))
    for i, c in enumerate(lignes):
        c["id"] = premier + i
    return lignes


def calibrer_revenus(evs1: list[dict], conso: dict[str, int]) -> dict[str, int]:
    """Forfait mensuel ≈ coût mensuel moyen du contrat au lot 1 × facteur, arrondi à 50 TND."""
    cout = {c[0]: 0 for c in CONTRATS}
    for v in evs1:
        cout[contrat_de(v["equipement"], v["date_intervention"])] += cout_mo(v) + conso.get(v["intervention_id"], 0)
    out = {}
    for ct in CONTRATS:
        n_mois = sum(actif_le(ct, m) for m in mois_du_lot(LOT1))
        out[ct[0]] = max(1000000, round(cout[ct[0]] / n_mois * ct[5] / 50000) * 50000)
    return out


def cout_mo(v: dict) -> int:
    return v["heures"] * CATEGORIES[v["_cat"]][1]


def tables_verite(evs, conso: dict[str, int], revenus: dict[str, int], lots: list[Lot], avec: bool) -> dict:
    vs = versions_equipements(avec)
    ck = {c[0]: k for k, c in enumerate(CONTRATS, 1)}
    dc = [{"contrat_key": ck[c[0]], "contrat_id": c[0], "client": c[1], "revenu_mensuel_millimes": revenus[c[0]],
           "date_debut": c[3], "date_fin": c[4]} for c in CONTRATS]
    fi = []
    for v in evs:
        j = v["date_intervention"]
        k = cle_version(vs, "equipement_id", "equipement_key", v["equipement"], j)
        fi.append({"intervention_id": v["intervention_id"], "date_key": date_key(j), "equipement_key": k,
                   "contrat_key": ck[next(x["contrat_id"] for x in vs if x["equipement_key"] == k)],
                   "technicien": v["technicien"], "type_intervention": v["type_intervention"],
                   "demande_le": f"{v['date_demande'].isoformat()} {v['heure_demande']}",
                   "intervention_le": f"{j.isoformat()} {v['heure_intervention']}", "heures": v["heures"],
                   "delai_heures": int((v["_fin"] - v["_debut"]).total_seconds() // 3600),
                   "cout_main_oeuvre_millimes": cout_mo(v), "cout_pieces_millimes": conso.get(v["intervention_id"], 0)})
    fr = [{"revenu_id": f"{c[0]}-{m.isoformat()[:7]}", "date_key": date_key(m), "contrat_key": ck[c[0]],
           "revenu_millimes": revenus[c[0]]} for lot in lots for m in mois_du_lot(lot) for c in CONTRATS if actif_le(c, m)]
    return {"dim_contrat": dc, "dim_equipement": vs, "fact_intervention": fi, "fact_revenu_contrat": fr}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_pieces(chemin) -> None:
    lignes = []
    for i, (code, nom, cat, prix) in enumerate(PIECES):
        cell = prix / 1000 if i % 3 != 1 else format_montant(prix, "milliers" if prix >= 1_000_000 else "virgule3")
        lignes.append([" pc-204" if code == "PC-204" else code, nom, cat, cell])
    ecrire_excel(chemin, [
        Feuille("Pièces", ["Code pièce", "Désignation", "Catégorie", "Prix unitaire (TND)"], lignes,
                titres=["TechniServ — catalogue des pièces détachées 2026 (prix d'achat en TND)"]),
        Feuille("Taux horaires", ["Code catégorie", "Catégorie", "Taux horaire (TND)"],
                [["CLIM", "Climatisation", 45.0], ["ASC", "Ascenseur", "62,5"], ["GE", "Groupe électrogène", 55]])])


def ecrire_equipements(chemin, eqs: list[dict], avec_changement: bool, extrait_le: str) -> None:
    out = []
    for e in eqs:
        depuis = e["depuis"]
        if e["id"] == "EQ-038":                       # piège : date au format JJ/MM/AAAA
            depuis = date.fromisoformat(depuis).strftime("%d/%m/%Y")
        ct = " ct-05" if e["id"] == "EQ-027" else e["contrat"]   # piège : casse et espace
        hist = [{"contrat": ct, "valide_depuis": depuis}]
        if avec_changement and e["id"] == EQUIPEMENT_MOBILE:
            hist.append({"contrat": CONTRAT_APRES, "valide_depuis": DATE_CHANGEMENT.isoformat()})
        out.append({"id": e["id"], "designation": e["designation"], "categorie": e["categorie"], "site": e["site"],
                    "historique": hist})
    ecrire_json(chemin, {"source": "Parc d'équipements sous contrat TechniServ", "extrait_le": extrait_le,
                         "equipements": out})


DDL_OPERATIONS = """
CREATE TABLE contrat (
  contrat_id TEXT PRIMARY KEY,
  client TEXT NOT NULL,
  revenu_mensuel TEXT NOT NULL,
  date_debut TEXT NOT NULL,
  date_fin TEXT,
  gestionnaire TEXT
);
CREATE TABLE consommation (
  id INTEGER PRIMARY KEY,
  intervention_id TEXT NOT NULL,
  code_piece TEXT NOT NULL,
  quantite INTEGER NOT NULL CHECK (quantite > 0),
  saisi_le TEXT NOT NULL
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""
GESTIONNAIRES = ["S. Gharbi", "M. Trabelsi", "N. Ayari"]


def ecrire_operations(chemin, contrats: list[tuple], revenus: dict[str, int], conso: list[dict], du: date, au: date):
    ecrire_sqlite(chemin, DDL_OPERATIONS, {
        "contrat": [{"contrat_id": c[0], "client": c[1], "revenu_mensuel": format_montant(revenus[c[0]], STYLES_REVENU[i]),
                     "date_debut": c[3], "date_fin": c[4], "gestionnaire": GESTIONNAIRES[i % 3]}
                    for i, c in enumerate(contrats)],
        "consommation": [{k: c[k] for k in ("id", "intervention_id", "code_piece", "quantite", "saisi_le")} for c in conso],
        "parametre": [{"cle": "export_genere_le", "valeur": (au + timedelta(days=1)).isoformat()},
                      {"cle": "perimetre", "valeur": f"consommations saisies du {du.isoformat()} au {au.isoformat()}"},
                      {"cle": "devise", "valeur": "TND"}]})


# --------------------------------------------------------------------------- échantillon (12 lignes)
ECHANTILLON = [
    (["I-001", "EQ-001", "2026-03-02", "08:00", "2026-03-02", "14:00", "T01", "2", "correctif"], None),
    (["I-002", "EQ-004", "02/03/2026", "09:00", "03/03/2026", "11:00", "T04", "3", "correctif"], None),
    (["I-003", " eq-011 ", "2026-02-20", "08:00", "4 mars 2026", "08:00", "T07", "2", "Préventif"], None),
    (["I-004", "EQ-001", "2026-03-05", "10:00", "2026-03-05", "13:00", "T02", "1", "correctif"], None),
    (["I-004", "EQ-001", "2026-03-05", "10:00", "2026-03-05", "13:00", "T02", "1", "correctif"], "doublon_exact"),
    (["I-005", "EQ-004", "2026-02-27", "08:00", "2026-03-06", "09:00", " t05", "2", "préventif"], None),
    (["I-006", "EQ-001", "2026-03-09", "08:00", "2026-03-09", "10:00", "T01", "2", "correctif"], "id_conflit"),
    (["I-006", "EQ-001", "2026-03-09", "08:00", "2026-03-09", "10:00", "T01", "3", "correctif"], "id_conflit"),
    (["", "EQ-004", "2026-03-10", "08:00", "2026-03-10", "15:00", "T05", "2", "correctif"], "id_manquant"),
    (["I-007", "EQ-099", "2026-03-10", "09:00", "2026-03-11", "09:00", "T03", "1", "correctif"], "cle_inconnue"),
    (["I-008", "EQ-011", "2026-03-11", "10:00", "2026-03-11", "16:00", "T08", "1,5", "correctif"], "quantite_invalide"),
    (["I-009", "EQ-011", "2026-03-09", "16:00", "10/03/2026", "10:00", "T08", "4", "correctif"], None),
]
CONSO_ECH = [(1, "I-001", "PC-101", 2), (2, "I-002", "PC-203", 1), (3, "I-003", "PC-301", 6), (4, "I-003", "PC-302", 1),
             (5, "I-009", "PC-305", 1), (6, "I-077", "PC-101", 1), (7, "I-004", "PC-999", 1)]
CONSO_ECH_REJET = {6: "intervention I-077 inconnue", 7: "pièce PC-999 absente du catalogue"}
REVENUS_ECH = {"CT-01": 1200000, "CT-02": 850500, "CT-03": 600000}


def _lire_date(t: str) -> date:
    t = t.strip()
    if "/" in t:
        j, m, a = t.split("/")
        return date(int(a), int(m), int(j))
    if t[:4].isdigit():
        return date.fromisoformat(t)
    j, m, a = t.split()
    return date(int(a), MOIS_FR.index(m) + 1, int(j))


def produire_echantillon(spec, dossier) -> dict:
    lignes = [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON]
    ecrire_csv(dossier / "interventions.csv", ENTETE, lignes)
    ecrire_pieces(dossier / "pieces.xlsx")
    ecrire_equipements(dossier / "equipements.json", [EQ["EQ-001"], EQ["EQ-004"], EQ["EQ-011"], EQ[EQUIPEMENT_MOBILE]], False, "2026-03-31")
    ech_ct = [c for c in CONTRATS if c[0] in REVENUS_ECH]
    ecrire_operations(dossier / "operations.sqlite", ech_ct, REVENUS_ECH,
                      [dict(zip(("id", "intervention_id", "code_piece", "quantite"), c), saisi_le="2026-03-12 17:00")
                       for c in CONSO_ECH], date(2026, 3, 1), date(2026, 3, 31))
    pieces = {}
    for _id, iid, code, q in CONSO_ECH:
        if _id not in CONSO_ECH_REJET:
            pieces[iid] = pieces.get(iid, 0) + q * PRIX[code]
    vs = [v for v in versions_equipements(False) if v["equipement_id"] in ("EQ-001", "EQ-004", "EQ-011", EQUIPEMENT_MOBILE)]
    ck = {"CT-01": 1, "CT-02": 2, "CT-03": 3}
    acc, fi = [], []
    for v, motif in ECHANTILLON:
        if motif is not None:
            continue
        eq = v[1].strip().upper()
        d0, d1 = _lire_date(v[2]), _lire_date(v[4])
        t0, t1 = datetime.fromisoformat(f"{d0.isoformat()} {v[3]}"), datetime.fromisoformat(f"{d1.isoformat()} {v[5]}")
        cat = EQ[eq]["categorie"]
        a = {"id": v[0], "eq": eq, "cat": cat, "d": d1, "h": int(v[7]), "type": v[8].strip().lower(),
             "delai": int((t1 - t0).total_seconds() // 3600), "mo": int(v[7]) * CATEGORIES[cat][1],
             "pieces": pieces.get(v[0], 0), "t0": t0, "t1": t1}
        acc.append(a)
        k = cle_version(vs, "equipement_id", "equipement_key", eq, d1)
        fi.append({"intervention_id": a["id"], "date_key": date_key(d1), "equipement_key": k,
                   "contrat_key": ck[EQ[eq]["contrat"]], "technicien": v[6].strip().upper(), "type_intervention": a["type"],
                   "demande_le": t0.strftime("%Y-%m-%d %H:%M"), "intervention_le": t1.strftime("%Y-%m-%d %H:%M"),
                   "heures": a["h"], "delai_heures": a["delai"], "cout_main_oeuvre_millimes": a["mo"],
                   "cout_pieces_millimes": a["pieces"]})
    dc = [{"contrat_key": ck[c[0]], "contrat_id": c[0], "client": c[1], "revenu_mensuel_millimes": REVENUS_ECH[c[0]],
           "date_debut": c[3], "date_fin": c[4]} for c in ech_ct]
    fr = [{"revenu_id": f"{c}-2026-03", "date_key": 20260301, "contrat_key": ck[c], "revenu_millimes": r}
          for c, r in REVENUS_ECH.items()]
    tables = {"dim_contrat": dc, "dim_equipement": vs, "fact_intervention": fi, "fact_revenu_contrat": fr}
    rejets = {"interventions.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "operations.sqlite": {"cle_inconnue": 2}}
    att = calculer_attendu_echantillon(spec, tables, date(2026, 3, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(fi),
                                        "consommations_lues": len(CONSO_ECH),
                                        "consommations_acceptees": len(CONSO_ECH) - len(CONSO_ECH_REJET)})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(acc, att), encoding="utf-8", newline="\n")
    return att


def md_echantillon(acc, att) -> str:
    i = att["indicateurs"]
    t1 = md_tableau(["Ligne du fichier", "intervention_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[1]!r} · demande {v[2]} {v[3]} · intervention {v[4]} {v[5]} · "
                      f"{v[7]} h · {v[8]}", "gardée" if m is None else ("ignorée : doublon exact de la ligne 5"
                                                                      if m == "doublon_exact" else f"rejet `{m}`")]
                     for n, (v, m) in enumerate(ECHANTILLON)])
    t2 = md_tableau(["intervention_id", "Équipement", "Type", "Demande → intervention", "Délai", "Main-d'œuvre",
                     "Pièces", "Coût"],
                    [[a["id"], f"{a['eq']} ({CATEGORIES[a['cat']][0]})", a["type"],
                      f"{a['t0']:%Y-%m-%d %H:%M} → {a['t1']:%Y-%m-%d %H:%M}",
                      f"{a['delai']} h" + ("" if a["type"] == "correctif" else " (exclu)"),
                      f"{a['h']} × {format_montant(CATEGORIES[a['cat']][1], 'virgule3')} = {tnd_fr(a['mo'])}",
                      tnd_fr(a["pieces"]), tnd_fr(a["mo"] + a["pieces"])] for a in acc])
    cor = [a for a in acc if a["type"] == "correctif"]
    conso = md_tableau(["consommation.id", "intervention_id", "Pièce", "Calcul", "Décision"],
                       [[c[0], c[1], c[2], f"{c[3]} × {format_montant(PRIX[c[2]], 'virgule3')}" if c[2] in PRIX else "—",
                         f"rejet `cle_inconnue` ({CONSO_ECH_REJET[c[0]]})" if c[0] in CONSO_ECH_REJET
                         else f"gardée : {tnd_fr(c[3] * PRIX[c[2]])}"] for c in CONSO_ECH])
    return f"""# Échantillon TechniServ — le calcul à la main

12 lignes de `interventions.csv`, le catalogue complet des pièces et des taux, 4 équipements, 3 contrats et 7 consommations de pièces dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code. Les forfaits des contrats de l'échantillon sont réduits (1 200,000, 850,500 et 600,000 TND) pour garder des calculs simples. EQ-017 (contrat CT-03) n'a pas d'intervention en mars : il sert à la question de la règle à clarifier.

## 1. Décision ligne par ligne (`interventions.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide` car `1,5` heure n'est pas un entier) → **{len(acc)} interventions gardées**.

## 2. Pièces consommées (`operations.sqlite`, table `consommation`)

{conso}

Coût des pièces = **{tnd_fr(i['cout_pieces_millimes'])}**.

## 3. Délai, main-d'œuvre, coût par intervention

Taux horaires (feuille `Taux horaires`) : Climatisation 45,000 TND/h · Ascenseur 62,500 TND/h · Groupe électrogène 55,000 TND/h.

{t2}

## 4. Les indicateurs

- Interventions = **{i['interventions']}** (dont {i['interventions_correctives']} correctives).
- Délai moyen (correctifs seulement) = ({' + '.join(str(a['delai']) for a in cor)}) / {len(cor)} = {i['delai_total_correctif_heures']} / {i['interventions_correctives']} = **{heures_fr(i['delai_moyen_heures'])}**. Les deux préventifs (planifiés des jours à l'avance) sont exclus.
- Coût d'intervention = main-d'œuvre {tnd_fr(i['cout_main_oeuvre_millimes'])} + pièces {tnd_fr(i['cout_pieces_millimes'])} = **{tnd_fr(i['cout_intervention_millimes'])}**.
- Revenu de contrat (mars 2026) = CT-01 1 200,000 + CT-02 850,500 + CT-03 600,000 = **{tnd_fr(i['revenu_contrat_millimes'])}** (3 lignes dans `fact_revenu_contrat`).
- Marge de service = revenu − coût = **{tnd_fr(i['marge_service_millimes'])}** (marge partielle).

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_intervention` : {att['tables']['fact_intervention']} lignes · `fact_revenu_contrat` : {att['tables']['fact_revenu_contrat']} · `dim_equipement` : {att['tables']['dim_equipement']} · `dim_contrat` : {att['tables']['dim_contrat']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes (5 interventions + 2 consommations). Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- parcours de démonstration chiffré
def parcours_demo(attendus: dict) -> str:
    """Démonstration conseillée, chiffrée depuis la référence (MissionSpec.parcours_app)."""
    a2 = attendus["lot2"]
    pc = a2["agregats"]["par_contrat"]
    pire = min(pc, key=lambda c: pc[c]["marge_service_millimes"])
    eq = a2["agregats"]["par_equipement"]
    top = max((k for k in eq if k != SANS_OBJET), key=lambda k: eq[k]["cout_intervention_millimes"])
    return f"""Démonstration conseillée :

1. **Vue direction** — sans filtre (janvier → août) : {a2['indicateurs']['interventions']} interventions, délai moyen {heures_fr(a2['indicateurs']['delai_moyen_heures'])}, coût d'intervention {tnd_fr(a2['indicateurs']['cout_intervention_millimes'])}, marge de service {tnd_fr(a2['indicateurs']['marge_service_millimes'])}. Choisir le contrat `{pire}` : marge {tnd_fr(pc[pire]['marge_service_millimes'])}, le contrat le moins rentable. Montrer le graphique « coût par mois et par catégorie » (la climatisation monte en été).
2. **Détail par équipement** — ouvrir `{EQUIPEMENT_MOBILE}` : deux versions ({CONTRAT_AVANT} jusqu'au 2026-07-14, {CONTRAT_APRES} depuis le 2026-07-15) ; ses interventions de juillet sont réparties entre les deux contrats selon la date d'intervention. Citer l'équipement le plus coûteux : `{top}` ({tnd_fr(eq[top]['cout_intervention_millimes'])}).
3. **Qualité des données** — rejets par motif et par lot (lot1 : {attendus['lot1']['rejets']['total']}, lot2 : {a2['rejets']['total']}), lignes déjà chargées du lot 2 ({a2['nettoyage']['interventions.csv']['deja_charges']} interventions recopiées du 30 juin), consommations rejetées ; la table « Chargements » montre le lot 2 puis son rejeu à 0 ajout."""


# --------------------------------------------------------------------------- programme principal
def main() -> None:
    spec = MissionSpec(parcours_app=parcours_demo, **SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    ev1 = generer_interventions(rng, LOT1, 1560, 1)
    ev2 = generer_interventions(rng, LOT2, 468, len(ev1) + 1)
    c1 = numeroter(generer_consommations(rng, ev1)
                   + [{"intervention_id": i, "code_piece": p, "quantite": q, "saisi_le": "2026-05-1" + str(k) + " 17:00",
                       "_rejet": True} for k, (i, p, q) in enumerate(ORPHELINES["lot1"])]
                   + [{"intervention_id": ev1[200 + 300 * k]["intervention_id"], "code_piece": p, "quantite": 1,
                       "saisi_le": "2026-04-0" + str(k + 1) + " 16:00", "_rejet": True}
                      for k, p in enumerate(PIECES_INCONNUES["lot1"])], 1)
    c2_neuves = numeroter(generer_consommations(rng, ev2)
                          + [{"intervention_id": i, "code_piece": p, "quantite": q, "saisi_le": f"2026-08-2{k} 17:00",
                              "_rejet": True} for k, (i, p, q) in enumerate(ORPHELINES["lot2"])], len(c1) + 1)
    conso = {}
    for c in c1 + c2_neuves:
        if not c.get("_rejet"):
            conso[c["intervention_id"]] = conso.get(c["intervention_id"], 0) + c["quantite"] * PRIX[c["code_piece"]]
    revenus = calibrer_revenus(ev1, conso)

    b1 = construire_csv(ev1, CHAMPS, DOSES["lot1"], rng, lambda k: f"INT-26-{90000 + 37 * k}")
    jour1 = {v["intervention_id"]: v["date_intervention"] for v in ev1}
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None and jour1[l.origine] >= CHEVAUCHEMENT]
    assert 10 <= len(rejouees) <= 20, len(rejouees)
    ids_rejoues = {v["intervention_id"] for v in rejouees}
    c2_rejouees = [c for c in c1 if c["intervention_id"] in ids_rejoues]
    b2 = construire_csv(ev2, CHAMPS, DOSES["lot2"], rng, lambda k: f"INT-26-{95000 + 41 * k}", rejouees)
    for lot, b, avec, cc, extrait in (("lot1", b1, False, c1, "2026-06-30"),
                                      ("lot2", b2, True, c2_rejouees + c2_neuves, "2026-08-31")):
        d = dossier / "sources" / lot
        lot_obj = LOT1 if lot == "lot1" else LOT2
        ecrire_csv(d / "interventions.csv", ENTETE, [l.valeurs for l in b.lignes])
        ecrire_pieces(d / "pieces.xlsx")
        ecrire_equipements(d / "equipements.json", EQUIPEMENTS, avec, extrait)
        ecrire_operations(d / "operations.sqlite", CONTRATS, revenus, cc,
                          CHEVAUCHEMENT if lot == "lot2" else LOT1.debut, lot_obj.fin)

    lots = []
    for lot, b, cc, evs, ev_cumul, avec in ((LOT1, b1, c1, ev1, ev1, False),
                                            (LOT2, b2, c2_rejouees + c2_neuves, ev2, ev1 + ev2, True)):
        ids = {v["intervention_id"] for v in evs}
        rej_c = sum(1 for c in cc if c.get("_rejet"))
        lots.append(LotResultat(
            lot=lot,
            sources={"interventions.csv": {"lignes": b.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "pieces.xlsx": {"feuilles": ["Pièces", "Taux horaires"], "pieces": len(PIECES),
                                     "categories": len(CATEGORIES), "ligne_entete_pieces": 3},
                     "equipements.json": {"equipements": len(EQUIPEMENTS), "versions": len(EQUIPEMENTS) + int(avec)},
                     "operations.sqlite": {"contrat": len(CONTRATS), "consommation": len(cc)}},
            nettoyage={"interventions.csv": {k: v for k, v in b.compteurs.items()
                                             if k not in ("lignes", "formats_montants")},
                       "operations.sqlite": {"consommations_deja_chargees": sum(1 for c in cc if c["intervention_id"]
                                                                               in ids_rejoues and lot is LOT2),
                                             "consommations_acceptees_nouvelles": sum(
                                                 1 for c in cc if not c.get("_rejet") and c["intervention_id"] in ids)}},
            rejets={"interventions.csv": b.rejets(), "operations.sqlite": {"cle_inconnue": rej_c}},
            tables_verite=tables_verite(ev_cumul, conso, revenus, [LOT1] if lot is LOT1 else [LOT1, LOT2], avec),
            increment=None if lot is LOT1 else {
                "fact_intervention_ajoutees": len(ev2),
                "fact_revenu_contrat_ajoutees": sum(actif_le(c, m) for m in mois_du_lot(LOT2) for c in CONTRATS),
                "versions_scd2_ajoutees": 1, "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin))}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(evs)

    attendus = produire_reference(spec, lots)
    # double contrôle Python pur (sans SQL) : coût, marge, délai moyen
    evs = ev1 + ev2
    cout = sum(cout_mo(v) + conso.get(v["intervention_id"], 0) for v in evs)
    rev = sum(f["revenu_millimes"] for f in lots[-1].tables_verite["fact_revenu_contrat"])
    cor = [v for v in evs if v["type_intervention"] == "correctif"]
    delai = sum(int((v["_fin"] - v["_debut"]).total_seconds() // 3600) for v in cor) / len(cor)
    ind = attendus["lot2"]["indicateurs"]
    assert (ind["cout_intervention_millimes"], ind["marge_service_millimes"]) == (cout, rev - cout)
    assert abs(ind["delai_moyen_heures"] - delai) < 1e-6
    cas = [v for v in ev2 if v["equipement"] == EQUIPEMENT_MOBILE and v["date_intervention"] == DATE_CHANGEMENT
           and v["date_demande"] < DATE_CHANGEMENT]
    assert cas and all(contrat_de(v["equipement"], v["date_intervention"]) == CONTRAT_APRES for v in cas)

    ech = produire_echantillon(spec, dossier / "echantillon")
    exporter_v7_data(spec, ech, attendus)
    ecrire_verite_privee(spec, {
        "interventions_verite.csv": (
            ["lot", "intervention_id", "equipement", "contrat_id", "categorie", "type_intervention", "demande_le",
             "intervention_le", "heures", "taux_horaire_millimes"],
            [{"lot": "lot1" if v in ev1 else "lot2", "intervention_id": v["intervention_id"], "equipement": v["equipement"],
              "contrat_id": contrat_de(v["equipement"], v["date_intervention"]), "categorie": v["_cat"],
              "type_intervention": v["type_intervention"], "demande_le": v["_debut"].isoformat(sep=" "),
              "intervention_le": v["_fin"].isoformat(sep=" "), "heures": v["heures"],
              "taux_horaire_millimes": CATEGORIES[v["_cat"]][1]} for v in evs]),
        "consommations_verite.csv": (["intervention_id", "code_piece", "quantite"],
                                     [c for c in c1 + c2_neuves if not c.get("_rejet")]),
        "pieces_verite.csv": (["code_piece", "prix_millimes"], [{"code_piece": p[0], "prix_millimes": p[3]} for p in PIECES]),
        "revenus_verite.csv": (["lot", "revenu_id", "contrat_id", "revenu_millimes"],
                               [{"lot": "lot1" if f["revenu_id"][-2:] <= "06" else "lot2", "revenu_id": f["revenu_id"],
                                 "contrat_id": f["revenu_id"][:5], "revenu_millimes": f["revenu_millimes"]}
                                for f in lots[-1].tables_verite["fact_revenu_contrat"]]),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]
                              + [{"lot": lot, "numero_ligne": c["id"], "motif": "cle_inconnue",
                                  "identifiant": c["intervention_id"]}
                                 for lot, cc in (("lot1", c1), ("lot2", c2_neuves)) for c in cc if c.get("_rejet")]),
    })
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : interventions.csv {a['sources']['interventions.csv']['lignes']} lignes · "
              f"fact_intervention {a['tables']['fact_intervention']} · fact_revenu_contrat {a['tables']['fact_revenu_contrat']} · "
              f"rejets {a['rejets']['par_motif']} · délai moyen {heures_fr(i['delai_moyen_heures'])} · "
              f"coût {tnd_fr(i['cout_intervention_millimes'])} · revenu {tnd_fr(i['revenu_contrat_millimes'])} · "
              f"marge {tnd_fr(i['marge_service_millimes'])}")
    e = ech["indicateurs"]
    print(f"  échantillon : {e['interventions']} interventions · délai {heures_fr(e['delai_moyen_heures'])} · "
          f"coût {tnd_fr(e['cout_intervention_millimes'])} · marge {tnd_fr(e['marge_service_millimes'])}")
    print(f"  règle à clarifier : {', '.join(v['intervention_id'] for v in cas)} (demande avant, intervention le "
          f"{DATE_CHANGEMENT.isoformat()}) → {CONTRAT_APRES}")


TABLES = [
    table_dim_date(),
    Table("dim_contrat", "dimension", "Contrats de maintenance (table `contrat` de la base de l'atelier).", [
        Colonne("contrat_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("contrat_id", "TEXT", "Code contrat normalisé (strip + majuscules), ex. `CT-03`."),
        Colonne("client", "TEXT", "Nom du client."),
        Colonne("revenu_mensuel_millimes", "INTEGER", "Forfait mensuel du contrat en millimes."),
        Colonne("date_debut", "TEXT", "Début du contrat, AAAA-MM-JJ."),
        Colonne("date_fin", "TEXT", "Fin du contrat, AAAA-MM-JJ ; vide = sans fin prévue.", nullable=True),
    ], cle_metier="contrat_id"),
    Table("dim_equipement", "dimension_scd2", "Équipements avec l'historique de leur contrat (SCD2).", [
        Colonne("equipement_key", "INTEGER", "Clé technique d'une VERSION d'équipement.", cle=True),
        Colonne("equipement_id", "TEXT", "Code équipement, ex. `EQ-017` (plusieurs versions possibles)."),
        Colonne("designation", "TEXT", "Description de l'équipement."),
        Colonne("categorie", "TEXT", "Libellé de la catégorie (feuille Taux horaires), ex. `Ascenseur`."),
        Colonne("site", "TEXT", "Site du client où se trouve l'équipement."),
        Colonne("contrat_id", "TEXT", "Contrat qui couvre l'équipement pendant cette version."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="equipement_id"),
    Table("fact_intervention", "fait", "Une intervention acceptée.", [
        Colonne("intervention_id", "TEXT", "Identifiant de l'intervention (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour de l'intervention.", ref="dim_date.date_key"),
        Colonne("equipement_key", "INTEGER", "Version de l'équipement valable à la date d'intervention.",
                ref="dim_equipement.equipement_key"),
        Colonne("contrat_key", "INTEGER", "Contrat de cette version de l'équipement.", ref="dim_contrat.contrat_key"),
        Colonne("technicien", "TEXT", "Code technicien normalisé, ex. `T04`."),
        Colonne("type_intervention", "TEXT", "`préventif` ou `correctif` (minuscules)."),
        Colonne("demande_le", "TEXT", "Date et heure de la demande, `AAAA-MM-JJ HH:MM`."),
        Colonne("intervention_le", "TEXT", "Date et heure de l'intervention, `AAAA-MM-JJ HH:MM`."),
        Colonne("heures", "INTEGER", "Heures facturées (entier > 0)."),
        Colonne("delai_heures", "INTEGER", "intervention_le − demande_le, en heures."),
        Colonne("cout_main_oeuvre_millimes", "INTEGER", "heures × taux horaire de la catégorie, en millimes."),
        Colonne("cout_pieces_millimes", "INTEGER", "Somme quantité × prix des pièces consommées acceptées (0 si aucune)."),
    ]),
    Table("fact_revenu_contrat", "fait", "Le forfait d'un contrat pour un mois où il est actif.", [
        Colonne("revenu_id", "TEXT", "`<contrat_id>-<AAAA-MM>`, ex. `CT-03-2026-07` (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "1er jour du mois.", ref="dim_date.date_key"),
        Colonne("contrat_key", "INTEGER", "Contrat.", ref="dim_contrat.contrat_key"),
        Colonne("revenu_millimes", "INTEGER", "Forfait mensuel en millimes."),
    ]),
]

if __name__ == "__main__":
    main()
