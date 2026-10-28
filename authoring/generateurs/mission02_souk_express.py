"""Mission M02 — E-commerce « Souk Express » (lignes de commande, remises, canaux SCD2, remboursements).

    python authoring/generateurs/mission02_souk_express.py            # depuis github/

Écrit modele-binome/catalogue/M02/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md,
echantillon/, sources/lot1/, sources/lot2/, reference/}, le bloc M02 de v7-data.json et la vérité privée du formateur.
"""
from __future__ import annotations

import sys
import zlib
from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec,
                    table_dim_date, rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv,
                    ecrire_excel, ecrire_json, ecrire_sqlite, preparer_dossier, produire_reference,
                    calculer_attendu_echantillon, exporter_v7_data, ecrire_verite_privee, format_montant,
                    tnd_fr, md_tableau, taille_dossier, TAILLE_MAX_MISSION)
from textes_mission02 import SPEC_TEXTES

GRAINE = 260202
CODE = "M02"
# code, nom, catégorie, prix, coût (millimes), poids de vente
PRODUITS = [("P01", "T-shirt en coton bio", "Mode", 45000, 19000, 14),
            ("P02", "Jean coupe droite", "Mode", 89900, 41000, 9),
            ("P03", "Coque de téléphone", "High-tech", 15900, 4200, 16),
            ("P04", "Écouteurs sans fil", "High-tech", 129000, 78000, 8),
            ("P05", "Montre connectée", "High-tech", 249000, 162000, 4),
            ("P06", "Crème hydratante à l'aloe", "Beauté", 32500, 12800, 12),
            ("P07", "Parfum Jasmin 50 ml", "Beauté", 98000, 41000, 6),
            ("P08", "Coffret soin barbe", "Beauté", 64000, 27000, 5),
            ("P09", "Lampe de chevet en céramique", "Maison", 75000, 36000, 6),
            ("P10", "Couverture en laine tissée", "Maison", 139000, 70000, 4),
            ("P11", "Set de 6 verres gravés", "Maison", 42000, 18500, 7),
            ("P12", "Café moulu 500 g", "Épicerie fine", 18500, 9800, 15),
            ("P13", "Miel de thym 1 kg", "Épicerie fine", 54000, 31000, 7),
            ("P14", "Sac à dos urbain", "Mode", 119000, 58000, 5),
            ("P15", "Robot pâtissier", "Maison", 899000, 610000, 1)]
# code, nom, famille, depuis, poids, (probabilité de remise, % min, % max), probabilité de remboursement
CANAUX = [("WEB", "Site souk-express.tn", "site", "2023-02-01", 30, (0.15, 5, 15), 0.030),
          ("APP", "Application mobile Souk Express", "application", "2024-09-15", 22, (0.30, 10, 20), 0.035),
          ("BZL", "Marketplace Bazar Lina", "marketplace", "2024-01-10", 18, (0.55, 10, 30), 0.100),
          ("SHM", "Marketplace Sahel Market", "marketplace", "2025-03-03", 8, (0.45, 10, 25), 0.085),
          ("VSO", "Vitrine sociale Souk Express", "réseaux sociaux", "2023-06-01", 12, (0.25, 10, 20), 0.100),
          ("GCO", "Groupe communauté Souk Express", "réseaux sociaux", "2023-06-01", 10, (0.30, 10, 15), 0.090)]
CHANGEMENT = ("VSO", "marketplace", date(2026, 7, 15))
VILLES = ["Tunis", "Tunis", "Ariana", "Sfax", "Sousse", "Nabeul", "Bizerte", "Gabès", "Médenine", "Kairouan",
          "Monastir", "Béja", "Kébili", "Mahdia"]
SAISON = {1: 0.95, 2: 0.9, 3: 1.3, 4: 1.1, 5: 0.9, 6: 0.95, 7: 1.25, 8: 1.05}   # mars : fêtes ; juillet : soldes
MOTIFS = [("TAI", "Taille ou modèle inadapté"), ("DEF", "Article défectueux"),
          ("RET", "Livraison en retard"), ("NRC", "Colis non reçu")]
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, janvier → juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 (fichier en cp1252) ; recopie les commandes des 29 et 30 juin ; VSO change de famille le 2026-07-15")
CHEVAUCHEMENT_CSV = date(2026, 6, 29)      # le lot 2 recopie les commandes depuis ce jour
CHEVAUCHEMENT_SQL = date(2026, 6, 20)      # la base du lot 2 recopie les remboursements depuis cette date
DEBUT_EN_COURS = date(2026, 8, 26)         # demandes des derniers jours : pas encore payées
ENTETE = ["ligne_id", "commande_id", "date_commande", "canal", "produit", "quantite", "prix_unitaire", "remise",
          "ville_livraison"]
CHAMPS = ChampsCSV(ENTETE, "ligne_id", "quantite", montants=["prix_unitaire", "remise"], dates=["date_commande"],
                   codes=["canal", "produit"], cles_inconnues={"produit": ["X15", "P99", "P16"],
                                                              "canal": ["TIK", "AMZ"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=5, inconnues=6, quantites=6),
         "lot2": Doses(doublons_exacts=4, conflits=1, manquants=2, inconnues=3, quantites=2)}
ORPHELINS = (("C109999-1", date(2026, 3, 17)), ("C108888-2", date(2026, 5, 9)), ("C209999-1", date(2026, 8, 12)))


# --------------------------------------------------------------------------- vérité terrain
def generer_commandes(rng, lot: Lot, n_cible: int, premier: int) -> list[dict]:
    js = jours(lot.debut, lot.fin)
    poids = [SAISON[d.month] * (1.25 if d.weekday() == 6 else 1.0) for d in js]
    par_jour = {d: 0 for d in js}
    for d in rng.choices(js, poids, k=n_cible):
        par_jour[d] += 1
    frontiere = (date(2026, 7, 14), date(2026, 7, 15))
    if lot is LOT2:                       # garantir des commandes VSO de part et d'autre de la frontière
        for d in frontiere:
            par_jour[d] = max(par_jour[d], 3)
    lignes, num = [], premier
    for d in js:
        reste = par_jour[d]
        force = lot is LOT2 and d in frontiere
        while reste > 0:
            taille = min(rng.choice([1, 1, 1, 2, 2, 3]), reste)
            c = next(x for x in CANAUX if x[0] == "VSO") if force else rng.choices(CANAUX, [x[4] for x in CANAUX])[0]
            force = False
            prods = []
            while len(prods) < taille:
                p = rng.choices(PRODUITS, [x[5] for x in PRODUITS])[0]
                if p not in prods:
                    prods.append(p)
            ville = rng.choice(VILLES)
            for k, p in enumerate(prods, 1):
                q = 1 if p[3] >= 200000 else rng.choice([1, 1, 1, 2, 2, 3])
                prix = p[3] if rng.random() > 0.06 else round(p[3] * 0.85 / 100) * 100   # promotion -15 %
                brut = q * prix
                prob, pmin, pmax = c[5]
                remise = round(brut * rng.randint(pmin, pmax) / 100 / 100) * 100 if rng.random() < prob else 0
                lignes.append({"ligne_id": f"C{num}-{k}", "commande_id": f"C{num}", "date_commande": d,
                               "canal": c[0], "produit": p[0], "quantite": q, "prix_unitaire": prix,
                               "remise": remise, "ville_livraison": ville})
            num += 1
            reste -= taille
    return lignes


def generer_remboursements(rng, lignes: list[dict]) -> list[dict]:
    proba = {c[0]: c[6] for c in CANAUX}
    bruts = []
    for v in lignes:
        if rng.random() < proba[v["canal"]] * (1.3 if v["date_commande"] > LOT1.fin else 1.0):
            d = v["date_commande"] + timedelta(days=rng.randint(2, 25))
            if d <= LOT2.fin:
                bruts.append((v, d, "EN_COURS" if d >= DEBUT_EN_COURS else "REMBOURSE"))
    # le cas de la règle à clarifier : commande VSO du 30 juin (ou juste avant), remboursée le 20 juillet
    cas = max((v for v in lignes if v["canal"] == "VSO" and v["date_commande"] <= LOT1.fin),
              key=lambda v: (v["date_commande"], v["ligne_id"]))
    bruts = [x for x in bruts if x[0] is not cas] + [(cas, date(2026, 7, 20), "REMBOURSE")]
    deja = {id(x[0]) for x in bruts}
    libres1 = [x for x in lignes if x["date_commande"] < date(2026, 6, 1) and id(x) not in deja]
    libres2 = [x for x in lignes if date(2026, 7, 1) <= x["date_commande"] < date(2026, 8, 10) and id(x) not in deja]
    tires = rng.sample(libres1, 8)
    for v in tires[:5] + rng.sample(libres2, 2):
        bruts.append((v, v["date_commande"] + timedelta(days=rng.randint(2, 10)), "REFUSE"))
    for v in tires[5:]:                   # demandes restées EN_COURS (jamais payées)
        bruts.append((v, v["date_commande"] + timedelta(days=rng.randint(2, 6)), "EN_COURS"))
    for ref, d in ORPHELINS:
        faux = {"ligne_id": ref, "canal": rng.choice(["WEB", "BZL"]), "produit": "P03", "quantite": 1,
                "prix_unitaire": 15900, "remise": 0}
        bruts.append((faux, d, "REMBOURSE"))
    bruts = [(v, d, s, f"{rng.randint(8, 20):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}")
             for v, d, s in bruts]
    bruts.sort(key=lambda x: (x[1], x[3], x[0]["ligne_id"]))
    out = []
    for i, (v, d, s, h) in enumerate(bruts, 1):
        q = rng.randint(1, v["quantite"])
        m = round(q * (v["quantite"] * v["prix_unitaire"] - v["remise"]) / v["quantite"])
        out.append({"id": i, "numero_remboursement": f"RB26-{i:05d}", "ref_ligne_commande": v["ligne_id"],
                    "date_remboursement": f"{d.isoformat()} {h}", "qte": q, "montant": round(m / 1000, 3),
                    "code_motif": rng.choice(MOTIFS)[0], "statut": s, "traite_par": f"agent-{rng.randint(1, 9):02d}",
                    "_jour": d, "_produit": v["produit"], "_canal": v["canal"],
                    "_orphelin": any(v["ligne_id"] == o for o, _ in ORPHELINS)})
    return out


def versions_canaux(avec_changement: bool) -> list[dict]:
    vs = []
    for k, (code, nom, fam, depuis, *_r) in enumerate(CANAUX, 1):
        fin = CHANGEMENT[2].isoformat() if (avec_changement and code == CHANGEMENT[0]) else None
        vs.append({"canal_key": k, "canal_id": code, "nom": nom, "famille": fam, "valid_from": depuis, "valid_to": fin})
    if avec_changement:
        c = next(x for x in CANAUX if x[0] == CHANGEMENT[0])
        vs.append({"canal_key": len(CANAUX) + 1, "canal_id": c[0], "nom": c[1], "famille": CHANGEMENT[1],
                   "valid_from": CHANGEMENT[2].isoformat(), "valid_to": None})
    return vs


PK = {p[0]: k for k, p in enumerate(PRODUITS, 1)}


def faits_commande(lignes, vs) -> list[dict]:
    return [{"ligne_id": v["ligne_id"], "commande_id": v["commande_id"], "date_key": date_key(v["date_commande"]),
             "produit_key": PK[v["produit"]],
             "canal_key": cle_version(vs, "canal_id", "canal_key", v["canal"], v["date_commande"]),
             "quantite": v["quantite"], "prix_unitaire_millimes": v["prix_unitaire"],
             "montant_brut_millimes": v["quantite"] * v["prix_unitaire"], "remise_millimes": v["remise"]} for v in lignes]


def faits_remboursement(rembs, vs) -> list[dict]:
    # règle à clarifier, décision B : version du canal valable à la date du REMBOURSEMENT
    return [{"remboursement_id": r["numero_remboursement"], "ligne_id": r["ref_ligne_commande"],
             "date_key": date_key(r["_jour"]), "produit_key": PK[r["_produit"]],
             "canal_key": cle_version(vs, "canal_id", "canal_key", r["_canal"], r["_jour"]),
             "quantite": r["qte"], "montant_millimes": round(r["montant"] * 1000)} for r in rembs]


def dim_produit() -> list[dict]:
    return [{"produit_key": k, "produit_id": p[0], "nom": p[1], "categorie": p[2], "prix_millimes": p[3],
             "cout_millimes": p[4]} for k, p in enumerate(PRODUITS, 1)]


def tables_verite(lignes, rembs, avec_changement: bool) -> dict[str, list[dict]]:
    vs = versions_canaux(avec_changement)
    return {"dim_produit": dim_produit(), "dim_canal": vs, "fact_commande": faits_commande(lignes, vs),
            "fact_remboursement": faits_remboursement(rembs, vs)}


# --------------------------------------------------------------------------- rendu des sources
def remise_vide(valeurs: dict) -> dict:
    """Une remise nulle est parfois exportée vide : règle déterministe par ligne_id (doublons exacts préservés)."""
    r = valeurs.get("remise", "")
    if r and set(r) <= set("0.,") and zlib.crc32(valeurs["ligne_id"].encode()) % 3 != 0:
        valeurs["remise"] = ""
    return valeurs


def ecrire_produits(chemin) -> None:
    lignes = []
    for i, (code, nom, cat, prix, cout, _w) in enumerate(PRODUITS):
        prix_cell = prix / 1000 if i % 3 != 1 else format_montant(prix, "virgule3")
        cout_cell = cout / 1000 if i != 14 else format_montant(cout, "court")
        lignes.append([" p12" if code == "P12" else code, nom, f" {cat}" if code in ("P06", "P11") else cat,
                       prix_cell, cout_cell])
    ecrire_excel(chemin, [Feuille("Produits", ["Code article", "Libellé", "Catégorie", "Prix public (TND)",
                                               "Coût de revient (TND)"], lignes,
                                  titres=["Souk Express — catalogue produits 2026 (montants en TND)"])])


def ecrire_canaux(chemin, avec_changement: bool, extrait_le: str) -> None:
    cs = []
    for code, nom, fam, depuis, *_r in CANAUX:
        hist = [{"famille": fam, "depuis": depuis}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"famille": CHANGEMENT[1], "depuis": CHANGEMENT[2].isoformat()})
        cs.append({"code": code, "nom": nom, "historique": hist})
    ecrire_json(chemin, {"source": "Référentiel des canaux de vente Souk Express", "extrait_le": extrait_le,
                         "familles_possibles": ["site", "application", "marketplace", "réseaux sociaux"],
                         "canaux": cs})


DDL_OPERATIONS = """
CREATE TABLE motif_remboursement (code_motif TEXT PRIMARY KEY, libelle TEXT NOT NULL);
CREATE TABLE remboursement (
  id INTEGER PRIMARY KEY,
  numero_remboursement TEXT NOT NULL UNIQUE,
  ref_ligne_commande TEXT NOT NULL,
  date_remboursement TEXT NOT NULL,
  qte INTEGER NOT NULL,
  montant REAL NOT NULL,
  code_motif TEXT REFERENCES motif_remboursement(code_motif),
  statut TEXT NOT NULL CHECK (statut IN ('REMBOURSE', 'EN_COURS', 'REFUSE')),
  traite_par TEXT
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""


def ecrire_operations(chemin, rembs: list[dict], du: date, au: date) -> None:
    lignes = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rembs]
    ecrire_sqlite(chemin, DDL_OPERATIONS, {
        "motif_remboursement": [{"code_motif": c, "libelle": l} for c, l in MOTIFS],
        "remboursement": lignes,
        "parametre": [{"cle": "export_genere_le", "valeur": (au + timedelta(days=1)).isoformat()},
                      {"cle": "perimetre", "valeur": f"remboursements du {du.isoformat()} au {au.isoformat()}"},
                      {"cle": "devise", "valeur": "TND"}]})


def comptes_operations(rembs: list[dict]) -> dict:
    return {"remboursement": len(rembs), **{s.lower(): sum(r["statut"] == s for r in rembs)
                                            for s in ("REMBOURSE", "EN_COURS", "REFUSE")},
            "motif_remboursement": len(MOTIFS)}


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
ECHANTILLON = [  # (valeurs texte, décision)
    (["E-01-1", "E-01", "2026-03-02", "WEB", "P01", "2", "45.000", "", "Tunis"], None),
    (["E-01-2", "E-01", "02/03/2026", "WEB", "P12", "1", "18,5", "", "Tunis"], None),
    (["E-02-1", "E-02", "3 mars 2026", " bzl ", "P02", "1", "89,900", "9,000", "Sfax"], None),
    (["E-03-1", "E-03", "2026-03-05", "VSO", "P03", "3", "15.900", "0", "Gabès"], None),
    (["E-03-1", "E-03", "2026-03-05", "VSO", "P03", "3", "15.900", "0", "Gabès"], "doublon_exact"),
    (["E-04-1", "E-04", "2026-03-06", "App", "P06", "2", "32,500", "6.5", "Sousse"], None),
    (["E-05-1", "E-05", "2026-03-07", "SHM", "P01", "1", "40.500", "4,050", "Bizerte"], None),
    (["E-06-1", "E-06", "2026-03-07", "WEB", "P12", "1", "18.500", "", "Ariana"], "id_conflit"),
    (["E-06-1", "E-06", "2026-03-07", "WEB", "P12", "2", "18.500", "", "Ariana"], "id_conflit"),
    (["", "E-07", "2026-03-08", "GCO", "P01", "1", "45.000", "", "Kébili"], "id_manquant"),
    (["E-08-1", "E-08", "2026-03-09", "WEB", "X99", "1", "9.000", "", "Tunis"], "cle_inconnue"),
    (["E-09-1", "E-09", "2026-03-09", "APP", "P06", "0", "32.500", "", "Sfax"], "quantite_invalide"),
]
REMB_ECH = [(1, "RB-0001", "E-03-1", "2026-03-12 10:15:00", 1, 15.9, "DEF", "REMBOURSE"),
            (2, "RB-0002", "E-04-1", "2026-03-13 16:40:00", 1, 29.25, "TAI", "REFUSE"),
            (3, "RB-0003", "E-99-9", "2026-03-14 11:05:00", 1, 45.0, "NRC", "REMBOURSE"),
            (4, "RB-0004", "E-02-1", "2026-03-30 09:20:00", 1, 80.9, "TAI", "EN_COURS")]


def lire_ech(texte: str) -> int:
    return round(float(texte.replace(",", ".")) * 1000) if texte.strip() else 0


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "commandes.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON])
    ecrire_produits(dossier / "produits.xlsx")
    ecrire_canaux(dossier / "canaux.json", False, "2026-03-31")
    cles = ("id", "numero_remboursement", "ref_ligne_commande", "date_remboursement", "qte", "montant", "code_motif",
            "statut")
    ecrire_operations(dossier / "operations.sqlite", [dict(zip(cles, r), traite_par="agent-01") for r in REMB_ECH],
                      date(2026, 3, 1), date(2026, 3, 31))
    jour = {"02/03/2026": 2, "3 mars 2026": 3}
    acc = [{"ligne_id": v[0], "commande_id": v[1], "date_commande": date(2026, 3, jour.get(v[2]) or int(v[2][-2:])),
            "canal": v[3].strip().upper(), "produit": v[4], "quantite": int(v[5]), "prix_unitaire": lire_ech(v[6]),
            "remise": lire_ech(v[7])} for v, m in ECHANTILLON if m is None]
    rb = [{"numero_remboursement": "RB-0001", "ref_ligne_commande": "E-03-1", "_jour": date(2026, 3, 12),
           "_produit": "P03", "_canal": "VSO", "qte": 1, "montant": 15.9}]
    tables = tables_verite(acc, rb, False)
    rejets = {"commandes.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "operations.sqlite": {"cle_inconnue": 1}}
    att = calculer_attendu_echantillon(spec, tables, date(2026, 3, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(acc),
                                        "remboursements_ignores": 2})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(acc, att), encoding="utf-8")
    return att


def md_echantillon(acc, att) -> str:
    i = att["indicateurs"]
    t1 = md_tableau(["Ligne du fichier", "ligne_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[2]} · {v[3]!r} · {v[4]} · qté {v[5]} · prix {v[6]} · remise {v[7]!r}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 5" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    t2 = md_tableau(["ligne_id", "Commande", "Date ISO", "Canal", "Calcul du brut", "Brut", "Remise"],
                    [[a["ligne_id"], a["commande_id"], a["date_commande"].isoformat(), a["canal"],
                      f"{a['quantite']} × {format_montant(a['prix_unitaire'], 'virgule3')}",
                      tnd_fr(a["quantite"] * a["prix_unitaire"]), tnd_fr(a["remise"])] for a in acc])
    brut = " + ".join(format_montant(a["quantite"] * a["prix_unitaire"], "virgule3") for a in acc)
    rem = " + ".join(format_montant(a["remise"], "virgule3") for a in acc if a["remise"])
    return f"""# Échantillon Souk Express — le calcul à la main

12 lignes de `commandes.csv`, le catalogue complet, 6 canaux, 4 remboursements dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`commandes.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées, dans 5 commandes** (`E-01` a deux lignes).

## 2. CA brut et remises

Une virgule ou un point sépare les décimales : `18,5` = `18.500` = 18 500 millimes. `40.500` est un prix promotionnel : on garde le prix payé. La remise est un montant en TND pour **toute la ligne** ; vide ou `0` = pas de remise.

{t2}

- **CA brut** = {brut} = **{tnd_fr(i['ca_brut_millimes'])}** ({i['ca_brut_millimes']} millimes).
- **Remises** = {rem} = **{tnd_fr(i['remises_millimes'])}**.

## 3. Remboursements (`operations.sqlite`, table `remboursement`)

- `RB-0001` : 1 coque (ligne `E-03-1`, canal VSO), statut `REMBOURSE` → **15,900 TND gardés**.
- `RB-0002` : statut `REFUSE` → ignoré (ce n'est pas un rejet).
- `RB-0003` : la ligne `E-99-9` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).
- `RB-0004` : statut `EN_COURS` (pas encore payé) → ignoré.

**Remboursements = {tnd_fr(i['remboursements_millimes'])}.**

## 4. CA net et panier moyen net

- CA net = CA brut − remises − remboursements = {tnd_fr(i['ca_brut_millimes'])} − {tnd_fr(i['remises_millimes'])} − {tnd_fr(i['remboursements_millimes'])} = **{tnd_fr(i['ca_net_millimes'])}**.
- Commandes distinctes : E-01, E-02, E-03, E-04, E-05 = **{i['nb_commandes']}**.
- Panier moyen net = {tnd_fr(i['ca_net_millimes'])} / {i['nb_commandes']} = **{tnd_fr(i['panier_moyen_net_millimes'])}**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_commande` : {att['tables']['fact_commande']} lignes · `fact_remboursement` : {att['tables']['fact_remboursement']} ligne · `dim_produit` : {att['tables']['dim_produit']} · `dim_canal` : {att['tables']['dim_canal']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- compléments du cahier des charges
# --------------------------------------------------------------------------- programme principal
def main(argv: list[str]) -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    c1 = generer_commandes(rng, LOT1, 2050, 100001)
    c2 = generer_commandes(rng, LOT2, 460, int(c1[-1]["commande_id"][1:]) + 1)
    rembs = generer_remboursements(rng, c1 + c2)
    r1 = [r for r in rembs if r["_jour"] <= LOT1.fin]
    r2 = [r for r in rembs if CHEVAUCHEMENT_SQL <= r["_jour"] <= LOT2.fin]
    assert not any(r["_orphelin"] for r in r1 if r["_jour"] >= CHEVAUCHEMENT_SQL)

    b1 = construire_csv(c1, CHAMPS, DOSES["lot1"], rng, lambda k: f"C{150000 + 37 * k}-9")
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None
                and next(v for v in c1 if v["ligne_id"] == l.origine)["date_commande"] >= CHEVAUCHEMENT_CSV]
    assert 10 <= len(rejouees) <= 20, len(rejouees)
    b2 = construire_csv(c2, CHAMPS, DOSES["lot2"], rng, lambda k: f"C{250000 + 41 * k}-9", rejouees)
    encodage = {"lot1": "utf-8", "lot2": "cp1252"}
    for lot, b, avec, rr, extrait in (("lot1", b1, False, r1, "2026-06-30"), ("lot2", b2, True, r2, "2026-08-31")):
        d = dossier / "sources" / lot
        ecrire_csv(d / "commandes.csv", ENTETE, [remise_vide(l.valeurs) for l in b.lignes], encodage=encodage[lot])
        ecrire_produits(d / "produits.xlsx")
        ecrire_canaux(d / "canaux.json", avec, extrait)
        ecrire_operations(d / "operations.sqlite", rr, CHEVAUCHEMENT_SQL if lot == "lot2" else LOT1.debut,
                          (LOT1 if lot == "lot1" else LOT2).fin)

    def valides(rr, deja=frozenset()):
        return [r for r in rr if r["statut"] == "REMBOURSE" and not r["_orphelin"] and r["numero_remboursement"] not in deja]
    acc1 = valides(r1)
    acc2 = valides(r2, {r["numero_remboursement"] for r in acc1})
    lots = []
    for lot, b, rr, acc, cumul_c, cumul_r, avec in (
            (LOT1, b1, r1, acc1, c1, acc1, False), (LOT2, b2, r2, acc2, c1 + c2, acc1 + acc2, True)):
        lots.append(LotResultat(
            lot=lot,
            sources={"commandes.csv": {"lignes": b.compteurs["lignes"], "encodage": encodage[lot.nom], "separateur": ";"},
                     "produits.xlsx": {"feuilles": ["Produits"], "produits": len(PRODUITS),
                                       "categories": len({p[2] for p in PRODUITS}), "ligne_entete_produits": 3},
                     "canaux.json": {"canaux": len(CANAUX), "versions": len(CANAUX) + (1 if avec else 0)},
                     "operations.sqlite": comptes_operations(rr)},
            nettoyage={"commandes.csv": {**{k: v for k, v in b.compteurs.items() if k != "lignes"},
                                         "remises_vides": sum(1 for l in b.lignes if l.valeurs["remise"] == "")},
                       "operations.sqlite": {"ignores_en_cours": sum(r["statut"] == "EN_COURS" for r in rr),
                                             "ignores_refuses": sum(r["statut"] == "REFUSE" for r in rr),
                                             "deja_charges": len(valides(rr)) - len(acc),
                                             "remboursements_acceptes_nouveaux": len(acc)}},
            rejets={"commandes.csv": b.rejets(), "operations.sqlite": {"cle_inconnue": sum(r["_orphelin"] for r in rr)}},
            tables_verite=tables_verite(cumul_c, cumul_r, avec),
            increment=None if lot is LOT1 else {
                "fact_commande_ajoutees": len(c2), "fact_remboursement_ajoutees": len(acc2),
                "versions_scd2_ajoutees": 1, "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin))}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(cumul_c) - (0 if lot is LOT1 else len(c1))

    attendus = produire_reference(spec, lots)
    # double contrôle Python pur (sans SQL) des nombres clés
    t = lots[-1].tables_verite
    brut = sum(f["montant_brut_millimes"] for f in t["fact_commande"])
    rem = sum(f["remise_millimes"] for f in t["fact_commande"])
    rb = sum(f["montant_millimes"] for f in t["fact_remboursement"])
    nb = len({f["commande_id"] for f in t["fact_commande"]})
    ind = attendus["lot2"]["indicateurs"]
    assert (ind["ca_net_millimes"], ind["nb_commandes"]) == (brut - rem - rb, nb)
    assert abs(ind["panier_moyen_net_millimes"] - (brut - rem - rb) / nb) <= 0.5
    canal_c1 = {v["ligne_id"]: v["canal"] for v in c1}
    cas = next(f for f in t["fact_remboursement"] if f["date_key"] == 20260720 and canal_c1.get(f["ligne_id"]) == "VSO")
    assert next(v for v in t["dim_canal"] if v["canal_key"] == cas["canal_key"])["famille"] == "marketplace"

    ech = produire_echantillon(spec, dossier / "echantillon")
    exporter_v7_data(spec, ech, attendus)
    ent_c = ["lot", "ligne_id", "commande_id", "date_commande", "canal", "produit", "quantite", "prix_unitaire_millimes",
             "remise_millimes"]
    ids1 = {v["ligne_id"] for v in c1}
    ids_r1 = {r["numero_remboursement"] for r in acc1}
    ecrire_verite_privee(spec, {
        "commandes_verite.csv": (ent_c, [{"lot": "lot1" if v["ligne_id"] in ids1 else "lot2", **v, "date_commande": v["date_commande"].isoformat(),
                                          "prix_unitaire_millimes": v["prix_unitaire"], "remise_millimes": v["remise"]}
                                         for v in c1 + c2]),
        "remboursements_verite.csv": (["lot", "numero_remboursement", "ref_ligne_commande", "produit", "canal", "jour",
                                       "qte", "montant_millimes"],
                                      [{"lot": "lot1" if r["numero_remboursement"] in ids_r1 else "lot2", **r, "produit": r["_produit"],
                                        "canal": r["_canal"], "jour": r["_jour"].isoformat(),
                                        "montant_millimes": round(r["montant"] * 1000)} for r in acc1 + acc2]),
        "canaux_verite.csv": (["canal_id", "nom", "famille", "valid_from", "valid_to"], versions_canaux(True)),
        "produits_verite.csv": (["produit_id", "nom", "categorie", "prix_millimes", "cout_millimes"], dim_produit()),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko) ; lignes rejouées dans lot2 : {len(rejouees)}")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : commandes.csv {a['sources']['commandes.csv']['lignes']} lignes · fact_commande "
              f"{a['tables']['fact_commande']} · fact_remboursement {a['tables']['fact_remboursement']} · "
              f"rejets {a['rejets']['par_motif']} · brut {tnd_fr(i['ca_brut_millimes'])} · remises "
              f"{tnd_fr(i['remises_millimes'])} · remb. {tnd_fr(i['remboursements_millimes'])} · net "
              f"{tnd_fr(i['ca_net_millimes'])} · {i['nb_commandes']} commandes · panier {tnd_fr(i['panier_moyen_net_millimes'])}")
    e = ech["indicateurs"]
    print(f"  échantillon : brut {tnd_fr(e['ca_brut_millimes'])} · remises {tnd_fr(e['remises_millimes'])} · "
          f"net {tnd_fr(e['ca_net_millimes'])} · panier {tnd_fr(e['panier_moyen_net_millimes'])}")


TABLES = [
    table_dim_date(),
    Table("dim_produit", "dimension", "Catalogue : un produit par ligne (feuille Produits).", [
        Colonne("produit_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("produit_id", "TEXT", "Code produit normalisé (strip + majuscules), ex. `P12`."),
        Colonne("nom", "TEXT", "Libellé du produit."),
        Colonne("categorie", "TEXT", "Catégorie (espaces supprimés), ex. `Beauté`."),
        Colonne("prix_millimes", "INTEGER", "Prix public du catalogue en millimes."),
        Colonne("cout_millimes", "INTEGER", "Coût de revient unitaire en millimes."),
    ], cle_metier="produit_id"),
    Table("dim_canal", "dimension_scd2", "Canaux de vente avec historique de la famille de canal (SCD2).", [
        Colonne("canal_key", "INTEGER", "Clé technique d'une VERSION de canal.", cle=True),
        Colonne("canal_id", "TEXT", "Code canal, ex. `VSO` (plusieurs versions possibles)."),
        Colonne("nom", "TEXT", "Nom du canal."),
        Colonne("famille", "TEXT", "Famille de cette version : `site`, `application`, `marketplace` ou `réseaux sociaux`."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="canal_id"),
    Table("fact_commande", "fait", "Une ligne de commande acceptée.", [
        Colonne("ligne_id", "TEXT", "Identifiant de la ligne de commande (clé métier unique).", cle=True),
        Colonne("commande_id", "TEXT", "Identifiant de la commande (sert à compter les commandes distinctes)."),
        Colonne("date_key", "INTEGER", "Jour de la commande.", ref="dim_date.date_key"),
        Colonne("produit_key", "INTEGER", "Produit commandé.", ref="dim_produit.produit_key"),
        Colonne("canal_key", "INTEGER", "Version du canal valable à la date de la commande.", ref="dim_canal.canal_key"),
        Colonne("quantite", "INTEGER", "Unités commandées (entier > 0)."),
        Colonne("prix_unitaire_millimes", "INTEGER", "Prix unitaire payé en millimes (promotion possible)."),
        Colonne("montant_brut_millimes", "INTEGER", "quantite × prix_unitaire_millimes."),
        Colonne("remise_millimes", "INTEGER", "Remise de la ligne entière en millimes (0 si vide)."),
    ]),
    Table("fact_remboursement", "fait", "Un remboursement au statut REMBOURSE de la base opérationnelle.", [
        Colonne("remboursement_id", "TEXT", "Numéro du remboursement (`numero_remboursement`), clé métier unique.", cle=True),
        Colonne("ligne_id", "TEXT", "Ligne de commande remboursée.", ref="fact_commande.ligne_id"),
        Colonne("date_key", "INTEGER", "Jour du remboursement (heure ignorée).", ref="dim_date.date_key"),
        Colonne("produit_key", "INTEGER", "Produit de la ligne de commande d'origine.", ref="dim_produit.produit_key"),
        Colonne("canal_key", "INTEGER", "Version du canal DE LA COMMANDE valable à la date du REMBOURSEMENT.",
                ref="dim_canal.canal_key"),
        Colonne("quantite", "INTEGER", "Unités remboursées."),
        Colonne("montant_millimes", "INTEGER", "Montant remboursé en millimes."),
    ]),
]

if __name__ == "__main__":
    main(sys.argv[1:])
