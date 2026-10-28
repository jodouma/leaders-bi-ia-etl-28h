"""Mission M01 — Réseau de magasins : Carthage Market (franchise).

    python authoring/generateurs/mission01_carthage_market.py              # depuis github/
    python authoring/generateurs/mission01_carthage_market.py --v7-data    # + met à jour v7-data.json

Écrit modele-binome/catalogue/M01/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md,
echantillon/, sources/lot1/, sources/lot2/, reference/} et la vérité privée du formateur.
v7-data.json (fichier partagé entre missions) n'est mis à jour qu'avec --v7-data.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec,
                    table_dim_date, rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv,
                    ecrire_excel, ecrire_json, ecrire_sqlite, preparer_dossier, produire_reference,
                    calculer_attendu_echantillon, exporter_v7_data, ecrire_verite_privee, format_montant,
                    lire_montant_millimes, tnd_fr, pct_fr, md_tableau, taille_dossier, MOIS_FR,
                    entrepot_verite, indicateur_dict, PALETTE, SERIES, _plt, _sauver, _nombre_fr, _echelle)
from textes_mission01 import SPEC_TEXTES

GRAINE = 260101
CODE = "M01"
TAILLE_MAX = 1_500_000                       # consigne de l'édition pour un dossier de mission catalogue
# code, nom, famille, prix, coût (millimes), poids de vente
PRODUITS = [("C101", "Semoule fine 1 kg", "EPI", 1350, 980, 30),
            ("C102", "Pâtes spaghetti 500 g", "EPI", 1150, 760, 28),
            ("C103", "Huile de tournesol 1 L", "EPI", 5900, 4600, 18),
            ("C104", "Café moulu 250 g", "EPI", 7800, 5300, 14),
            ("C105", "Eau minérale 6 × 1,5 L", "BOI", 4200, 2900, 25),
            ("C106", "Jus d'orange 1 L", "BOI", 3600, 2350, 16),
            ("C107", "Lait demi-écrémé 1 L", "LAI", 1490, 1160, 34),
            ("C108", "Yaourt nature × 4", "LAI", 2400, 1500, 20),
            ("C109", "Fromage à tartiner 200 g", "LAI", 4950, 3200, 10),
            ("C110", "Shampoing 400 ml", "HYG", 9800, 5600, 8),
            ("C111", "Lessive liquide 3 L", "ENT", 21500, 14800, 7),
            ("C112", "Liquide vaisselle 1 L", "ENT", 3800, 2200, 12)]
FAMILLES = {"EPI": "Épicerie", "BOI": "Boissons", "LAI": "Produits laitiers", "HYG": "Hygiène", "ENT": "Entretien"}
# code, nom, ville, type, région, ouverture, poids
MAGASINS = [("LAC", "Carthage Market Les Berges du Lac", "Tunis", "propre", "Grand Tunis", "2017-09-04", 26),
            ("ARI", "Carthage Market Ariana", "Ariana", "franchisé", "Grand Tunis", "2020-02-17", 16),
            ("BIZ", "Carthage Market Bizerte", "Bizerte", "franchisé", "Nord", "2021-06-07", 11),
            ("HAM", "Carthage Market Hammamet", "Hammamet", "franchisé", "Cap Bon", "2022-04-11", 14),
            ("SOU", "Carthage Market Sousse", "Sousse", "propre", "Sahel", "2018-11-05", 20),
            ("SFX", "Carthage Market Sfax", "Sfax", "propre", "Sud", "2019-05-13", 18),
            ("GAB", "Carthage Market Gabès", "Gabès", "franchisé", "Sud", "2023-03-20", 9)]
TYPE_JSON = {"HAM": " Franchisé", "GAB": "FRANCHISÉ", "SOU": "Propre "}   # écritures « sales » du référentiel
CHANGEMENT = ("HAM", "Sahel", date(2026, 7, 15))
PAIEMENTS = ["carte bancaire", "espèces", "espèces", "espèces", "chèque", "paiement mobile"]
SAISON = {1: 0.95, 2: 1.0, 3: 1.25, 4: 0.95, 5: 0.9, 6: 0.95, 7: 1.1, 8: 1.15}
RAMADAN = (date(2026, 2, 18), date(2026, 3, 19))
MOTIFS_RETOUR = [("DLC", "Date limite proche"), ("DEF", "Produit abîmé"), ("ERR", "Erreur de caisse"),
                 ("CHG", "Changement d'avis")]
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, janvier → juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 ; recopie les 29-30 juin ; HAM change de région le 2026-07-15")
CHEVAUCHEMENT_CSV = date(2026, 6, 29)      # le lot 2 recopie les ventes depuis cette date
CHEVAUCHEMENT_SQL = date(2026, 6, 20)      # la base du lot 2 recopie les retours depuis cette date
ENTETE = ["ligne_id", "ticket_id", "date_vente", "magasin", "produit", "quantite", "prix_unitaire",
          "code_promo", "remise", "mode_paiement"]
CHAMPS = ChampsCSV(ENTETE, "ligne_id", "quantite", montants=["prix_unitaire", "remise"], dates=["date_vente"],
                   codes=["magasin", "produit"], cles_inconnues={"produit": ["C199", "C120", "C000"],
                                                                 "magasin": ["TOZ", "KEF"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=4, inconnues=6, quantites=6),
         "lot2": Doses(doublons_exacts=4, conflits=1, manquants=2, inconnues=2, quantites=3)}
ORPHELINS = [("T499001-1", date(2026, 3, 17)), ("T499517-2", date(2026, 5, 9)), ("T499873-1", date(2026, 8, 12))]
COUT = {p[0]: p[4] for p in PRODUITS}
TYPE = {m[0]: m[3] for m in MAGASINS}


# --------------------------------------------------------------------------- vérité terrain
def promotion(rng, d: date) -> tuple[str, float]:
    if RAMADAN[0] <= d <= RAMADAN[1] and rng.random() < 0.35:
        return "RAMADAN26", 0.10
    if d.month in (7, 8) and rng.random() < 0.20:
        return "ETE26", 0.15
    if rng.random() < 0.08:
        return "FIDELITE", 0.05
    return "", 0.0


def generer_ventes(rng, lot: Lot, n_cible: int, premier_ticket: int) -> list[dict]:
    js = jours(lot.debut, lot.fin)
    poids = [SAISON[d.month] * (1.3 if d.weekday() == 5 else 1.0) * (1.2 if RAMADAN[0] <= d <= RAMADAN[1] else 1.0)
             for d in js]
    par_jour = {d: 0 for d in js}
    for d in rng.choices(js, poids, k=n_cible):
        par_jour[d] += 1
    force = {date(2026, 7, 14), date(2026, 7, 15)} if lot is LOT2 else set()   # HAM des deux côtés de la frontière
    for d in force:
        par_jour[d] = max(par_jour[d], 4)
    ventes, num = [], premier_ticket
    for d in js:
        reste, force_ham = par_jour[d], d in force
        while reste > 0:
            taille = min(rng.choice([1, 1, 2, 2, 3, 4]), reste)
            m = "HAM" if force_ham else rng.choices([x[0] for x in MAGASINS], [x[6] for x in MAGASINS])[0]
            force_ham = False
            prods = []
            while len(prods) < taille:
                p = rng.choices(PRODUITS, [x[5] for x in PRODUITS])[0]
                if p not in prods:
                    prods.append(p)
            paiement = rng.choice(PAIEMENTS)
            for k, p in enumerate(prods, 1):
                q = rng.choice([1, 1, 2]) if p[0] in ("C110", "C111") else rng.choice([1, 1, 1, 2, 2, 3, 4, 6])
                code, taux = promotion(rng, d)
                remise = round(q * p[3] * taux / 10) * 10
                ventes.append({"ligne_id": f"T{num}-{k}", "ticket_id": f"T{num}", "date_vente": d, "magasin": m,
                               "produit": p[0], "quantite": q, "prix_unitaire": p[3], "code_promo": code,
                               "remise": remise, "mode_paiement": paiement, "montant": q * p[3] - remise})
            num += 1
            reste -= taille
    return ventes


def generer_retours(rng, ventes: list[dict]) -> list[dict]:
    bruts = []
    for v in ventes:
        p = {"C109": 0.06, "C108": 0.045, "C107": 0.04, "C111": 0.05}.get(v["produit"], 0.025)
        if v["date_vente"] > LOT1.fin:
            p *= 1.5                      # été : produits frais plus souvent rapportés
        if rng.random() < p:
            d = v["date_vente"] + timedelta(days=rng.randint(1, 15))
            if d <= LOT2.fin:
                bruts.append((v, d, "VALIDE"))
    annules = (rng.sample([x for x in ventes if x["date_vente"] < date(2026, 6, 10)], 4)
               + rng.sample([x for x in ventes if date(2026, 7, 1) <= x["date_vente"] < date(2026, 8, 20)], 2))
    for v in annules:
        bruts.append((v, v["date_vente"] + timedelta(days=rng.randint(1, 10)), "ANNULE"))
    for ref, d in ORPHELINS:
        faux = {"ligne_id": ref, "magasin": rng.choice(["LAC", "SFX"]), "produit": "C103", "quantite": 1,
                "montant": 5900}
        bruts.append((faux, d, "VALIDE"))
    bruts = [(v, d, s, f"{rng.randint(8, 20):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}")
             for v, d, s in bruts]
    bruts.sort(key=lambda x: (x[1], x[3], x[0]["ligne_id"]))
    retours = []
    for i, (v, d, s, h) in enumerate(bruts, 1):
        q = rng.randint(1, v["quantite"])
        montant = round(q * v["montant"] / v["quantite"])          # prorata du prix PAYÉ (remise comprise)
        retours.append({"id": i, "numero_retour": f"RCM-{i:05d}", "ref_ligne_ticket": v["ligne_id"],
                        "code_magasin": v["magasin"], "date_retour": f"{d.isoformat()} {h}", "qte": q,
                        "montant_rembourse": round(montant / 1000, 3), "code_motif": rng.choice(MOTIFS_RETOUR)[0],
                        "statut": s, "saisi_par": f"caisse-{v['magasin'].lower()}-{rng.randint(1, 3)}",
                        "_jour": d, "_produit": v["produit"], "_montant": montant,
                        "_orphelin": v["ligne_id"] in dict(ORPHELINS)})
    return retours


def versions_magasins(avec_changement: bool) -> list[dict]:
    vs = []
    for k, (code, nom, _ville, typ, region, depuis, _w) in enumerate(MAGASINS, 1):
        fin = CHANGEMENT[2].isoformat() if (avec_changement and code == CHANGEMENT[0]) else None
        vs.append({"magasin_key": k, "magasin_id": code, "nom": nom, "type": typ, "region": region,
                   "valid_from": depuis, "valid_to": fin})
    if avec_changement:
        m = next(x for x in MAGASINS if x[0] == CHANGEMENT[0])
        vs.append({"magasin_key": len(MAGASINS) + 1, "magasin_id": m[0], "nom": m[1], "type": m[3],
                   "region": CHANGEMENT[1], "valid_from": CHANGEMENT[2].isoformat(), "valid_to": None})
    return vs


def tables_verite(ventes, retours, avec_changement: bool) -> dict[str, list[dict]]:
    vs = versions_magasins(avec_changement)
    pk = {p[0]: k for k, p in enumerate(PRODUITS, 1)}
    fv = [{"ligne_id": v["ligne_id"], "date_key": date_key(v["date_vente"]), "produit_key": pk[v["produit"]],
           "magasin_key": cle_version(vs, "magasin_id", "magasin_key", v["magasin"], v["date_vente"]),
           "quantite": v["quantite"], "prix_unitaire_millimes": v["prix_unitaire"], "remise_millimes": v["remise"],
           "montant_brut_millimes": v["quantite"] * v["prix_unitaire"] - v["remise"]} for v in ventes]
    fr = [{"retour_id": r["numero_retour"], "date_key": date_key(r["_jour"]), "produit_key": pk[r["_produit"]],
           "magasin_key": cle_version(vs, "magasin_id", "magasin_key", r["code_magasin"], r["_jour"]),
           "quantite": r["qte"], "montant_millimes": round(r["montant_rembourse"] * 1000)} for r in retours]
    dp = [{"produit_key": k, "produit_id": p[0], "nom": p[1], "famille": FAMILLES[p[2]],
           "prix_millimes": p[3], "cout_achat_millimes": p[4]} for k, p in enumerate(PRODUITS, 1)]
    return {"dim_produit": dp, "dim_magasin": vs, "fact_vente": fv, "fact_retour": fr}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_catalogue(chemin) -> None:
    lignes = []
    for i, (code, nom, fam, prix, cout, _w) in enumerate(PRODUITS):
        prix_cell = prix / 1000 if i % 4 != 2 else format_montant(prix, "virgule3")
        cout_cell = cout / 1000 if i not in (3, 10) else format_montant(cout, "virgule3")
        lignes.append([" c108" if code == "C108" else code, nom, fam, prix_cell, cout_cell])
    ecrire_excel(chemin, [
        Feuille("Catalogue", ["Code article", "Libellé article", "Famille", "Prix de vente (TND)", "Coût d'achat (TND)"],
                lignes, titres=["Carthage Market — catalogue et tarifs 2026 (montants en TND)"]),
        Feuille("Familles", ["Code famille", "Libellé famille"], [[k, v] for k, v in FAMILLES.items()])])


def ecrire_magasins(chemin, avec_changement: bool, extrait_le: str) -> None:
    ms = []
    for code, nom, ville, typ, region, depuis, _w in MAGASINS:
        hist = [{"region": region, "valide_depuis": depuis}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"region": CHANGEMENT[1], "valide_depuis": CHANGEMENT[2].isoformat()})
        ms.append({"code": code, "nom": nom, "ville": ville, "type": TYPE_JSON.get(code, typ), "historique": hist})
    ecrire_json(chemin, {"source": "Référentiel des magasins Carthage Market", "extrait_le": extrait_le,
                         "magasins": ms})


DDL_OPERATIONS = """
CREATE TABLE motif_retour (code_motif TEXT PRIMARY KEY, libelle TEXT NOT NULL);
CREATE TABLE retour (
  id INTEGER PRIMARY KEY,
  numero_retour TEXT NOT NULL UNIQUE,
  ref_ligne_ticket TEXT NOT NULL,
  code_magasin TEXT NOT NULL,
  date_retour TEXT NOT NULL,
  qte INTEGER NOT NULL,
  montant_rembourse REAL NOT NULL,
  code_motif TEXT REFERENCES motif_retour(code_motif),
  statut TEXT NOT NULL CHECK (statut IN ('VALIDE', 'ANNULE')),
  saisi_par TEXT
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""


def ecrire_operations(chemin, retours: list[dict], du: date, au: date) -> None:
    lignes = [{k: v for k, v in r.items() if not k.startswith("_")} for r in retours]
    ecrire_sqlite(chemin, DDL_OPERATIONS, {
        "motif_retour": [{"code_motif": c, "libelle": l} for c, l in MOTIFS_RETOUR],
        "retour": lignes,
        "parametre": [{"cle": "export_genere_le", "valeur": (au + timedelta(days=1)).isoformat()},
                      {"cle": "perimetre", "valeur": f"retours du {du.isoformat()} au {au.isoformat()}"},
                      {"cle": "devise", "valeur": "TND"}]})


def comptes_operations(retours: list[dict]) -> dict:
    return {"retour": len(retours), "valides": sum(r["statut"] == "VALIDE" for r in retours),
            "annules": sum(r["statut"] == "ANNULE" for r in retours), "motif_retour": len(MOTIFS_RETOUR)}


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
ECHANTILLON = [  # (valeurs texte, décision)
    (["E-01-1", "E-01", "2026-03-02", "LAC", "C101", "4", "1.350", "", "0", "carte bancaire"], None),
    (["E-01-2", "E-01", "02/03/2026", "LAC", "C111", "1", "21,500", "RAMADAN26", "2,150", "carte bancaire"], None),
    (["E-02-1", "E-02", "3 mars 2026", " ari ", "C105", "2", "4.2", "", "0", "espèces"], None),
    (["E-03-1", "E-03", "2026-03-04", "HAM", "C107", "6", "1,490", "", "0", "espèces"], None),
    (["E-03-1", "E-03", "2026-03-04", "HAM", "C107", "6", "1,490", "", "0", "espèces"], "doublon_exact"),
    (["E-04-1", "E-04", "2026-03-05", "Sou", "C110", "2", "9.800", "RAMADAN26", "1.960", "chèque"], None),
    (["E-05-1", "E-05", "2026-03-06", "GAB", "C104", "1", "7,8", "", "0", "espèces"], None),
    (["E-06-1", "E-06", "2026-03-07", "SFX", "C108", "2", "2.400", "", "0", "espèces"], "id_conflit"),
    (["E-06-1", "E-06", "2026-03-07", "SFX", "C108", "3", "2.400", "", "0", "espèces"], "id_conflit"),
    (["", "E-07", "2026-03-08", "BIZ", "C102", "2", "1.150", "", "0", "espèces"], "id_manquant"),
    (["E-08-1", "E-08", "2026-03-09", "TOZ", "C106", "1", "3.600", "", "0", "carte bancaire"], "cle_inconnue"),
    (["E-09-1", "E-09", "2026-03-09", "LAC", "C112", "1,5", "3.800", "", "0", "espèces"], "quantite_invalide"),
]
RETOURS_ECH = [(1, "R-0001", "E-04-1", "SOU", "2026-03-10 10:15:00", 1, 8.82, "DEF", "VALIDE"),
               (2, "R-0002", "E-01-1", "LAC", "2026-03-11 16:40:00", 2, 2.7, "CHG", "ANNULE"),
               (3, "R-0003", "E-99-9", "LAC", "2026-03-12 11:05:00", 1, 5.9, "ERR", "VALIDE")]


def jour_texte(t: str) -> date:
    t = t.strip()
    if "/" in t:
        j, m, a = t.split("/")
        return date(int(a), int(m), int(j))
    if t[:4].isdigit():
        return date.fromisoformat(t)
    j, mois, a = t.split()
    return date(int(a), MOIS_FR.index(mois) + 1, int(j))


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "ventes.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON])
    ecrire_catalogue(dossier / "catalogue.xlsx")
    ecrire_magasins(dossier / "magasins.json", False, "2026-03-31")
    cles = ("id", "numero_retour", "ref_ligne_ticket", "code_magasin", "date_retour", "qte",
            "montant_rembourse", "code_motif", "statut")
    ecrire_operations(dossier / "operations.sqlite", [dict(zip(cles, r), saisi_par="caisse-ech-1")
                                                      for r in RETOURS_ECH], date(2026, 3, 1), date(2026, 3, 31))
    pk = {p[0]: k for k, p in enumerate(PRODUITS, 1)}
    vs = versions_magasins(False)
    acc = []
    for v, motif in ECHANTILLON:
        if motif is None:
            q, p, r = int(v[5]), lire_montant_millimes(v[6]), lire_montant_millimes(v[8])
            acc.append({"ligne_id": v[0], "date": jour_texte(v[2]), "magasin": v[3].strip().upper(),
                        "produit": v[4], "q": q, "p": p, "r": r, "promo": v[7]})
    fv = [{"ligne_id": a["ligne_id"], "date_key": date_key(a["date"]), "produit_key": pk[a["produit"]],
           "magasin_key": cle_version(vs, "magasin_id", "magasin_key", a["magasin"], a["date"]),
           "quantite": a["q"], "prix_unitaire_millimes": a["p"], "remise_millimes": a["r"],
           "montant_brut_millimes": a["q"] * a["p"] - a["r"]} for a in acc]
    vr = next(a for a in acc if a["ligne_id"] == "E-04-1")
    assert round((vr["q"] * vr["p"] - vr["r"]) / vr["q"]) == 8820
    fr = [{"retour_id": "R-0001", "date_key": 20260310, "produit_key": pk[vr["produit"]],
           "magasin_key": cle_version(vs, "magasin_id", "magasin_key", "SOU", date(2026, 3, 10)),
           "quantite": 1, "montant_millimes": 8820}]
    tables = tables_verite([], [], False)
    tables.update({"fact_vente": fv, "fact_retour": fr})
    rejets = {"ventes.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "operations.sqlite": {"cle_inconnue": 1}}
    att = calculer_attendu_echantillon(spec, tables, date(2026, 3, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(fv),
                                        "retours_annules_exclus": 1})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(acc, att), encoding="utf-8")
    return att


def md_echantillon(acc, att) -> str:
    i = att["indicateurs"]
    f3 = lambda m: format_montant(m, "virgule3")
    t1 = md_tableau(["Ligne du fichier", "ligne_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[2]} · {v[3]!r} · {v[4]} · qté {v[5]} · prix {v[6]} · remise {v[8]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 5" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    t2 = md_tableau(["ligne_id", "Date ISO", "Magasin", "Type", "Produit", "Calcul", "Montant brut"],
                    [[a["ligne_id"], a["date"].isoformat(), a["magasin"], TYPE[a["magasin"]], a["produit"],
                      f"{a['q']} × {f3(a['p'])} − {f3(a['r'])}", tnd_fr(a["q"] * a["p"] - a["r"])] for a in acc])
    cout_v = " + ".join(f"{a['q']} × {f3(COUT[a['produit']])}" for a in acc)
    cv = sum(a["q"] * COUT[a["produit"]] for a in acc)
    fr = [a for a in acc if TYPE[a["magasin"]] == "franchisé"]
    nf = sum(a["q"] * a["p"] - a["r"] for a in fr)
    return f"""# Échantillon Carthage Market — le calcul à la main

12 lignes de `ventes.csv`, le catalogue complet, 7 magasins, 3 retours dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`ventes.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **{len(acc)} lignes gardées**.

## 2. Ventes brutes (remise déduite)

Une virgule ou un point sépare les décimales : `21,5` = `21.500` = 21 500 millimes. La remise vaut pour toute la ligne. Décision de la direction (règle à clarifier) : **la remise est déduite avant la marge**, donc montant brut = quantité × prix − remise.

{t2}

**Ventes brutes = {tnd_fr(i['ventes_brutes_millimes'])}** ({i['ventes_brutes_millimes']} millimes). Remises déjà déduites : {tnd_fr(i['remises_millimes'])}.

## 3. Retours (`operations.sqlite`, table `retour`)

- `R-0001` : 1 shampoing de la ligne `E-04-1` (SOU). Le client avait payé 2 × 9,800 − 1,960 = 17,640 TND pour 2 unités → remboursé **8,820 TND** (le prix payé, remise comprise). Statut `VALIDE` : gardé.
- `R-0002` : statut `ANNULE` → ignoré (ce n'est pas un rejet).
- `R-0003` : la ligne `E-99-9` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).

**Retours = {tnd_fr(i['retours_millimes'])}.**

## 4. Les quatre indicateurs

- **Ventes nettes** = brutes − retours = {tnd_fr(i['ventes_brutes_millimes'])} − {tnd_fr(i['retours_millimes'])} = **{tnd_fr(i['ventes_nettes_millimes'])}**.
- Coût d'achat des unités vendues = {cout_v} = {tnd_fr(cv)}. Unité retournée : 1 × 5,600 (coût du shampoing). Coût d'achat des unités nettes = {tnd_fr(cv)} − 5,600 TND = **{tnd_fr(i['cout_achat_net_millimes'])}**.
- **Marge sur coût d'achat** = ventes nettes − coût d'achat des unités nettes = **{tnd_fr(i['marge_cout_achat_millimes'])}**.
- **Part des franchisés** : magasins franchisés de l'échantillon = {', '.join(sorted({a['magasin'] for a in fr}))} ; leurs ventes nettes = {' + '.join(f3(a['q'] * a['p'] - a['r']) for a in fr)} = {tnd_fr(nf)} (aucun retour chez eux) ; part = {nf} / {i['ventes_nettes_millimes']} = **{pct_fr(i['part_franchises'])}**.
- **Taux de retour** = retours / brutes = {i['retours_millimes']} / {i['ventes_brutes_millimes']} = **{pct_fr(i['taux_retour'])}**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_vente` : {att['tables']['fact_vente']} lignes · `fact_retour` : {att['tables']['fact_retour']} ligne · `dim_produit` : {att['tables']['dim_produit']} · `dim_magasin` : {att['tables']['dim_magasin']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- visuel local
def visuel_empile_bas(spec, con, v: dict, base) -> None:
    """Barres empilées comme common.visuel_empile, mais légende SOUS le graphique (5 régions : la légende
    du cadre commun recouvrait la barre de mars). Type de visuel « empile_bas », ignoré par produire_reference."""
    from matplotlib.ticker import FuncFormatter
    plt = _plt()
    ind = indicateur_dict(next(i for i in spec.indicateurs if i.code == v["indicateur"]))
    rows = con.execute(f"WITH mouvements AS ({spec.vue_analyse}) SELECT {v['x']}, {v['serie']}, {ind['sql']} "
                       f"FROM mouvements GROUP BY 1, 2 ORDER BY 1, 2").fetchall()
    xs = sorted({r[0] for r in rows})
    series = list(dict.fromkeys(v.get("ordre_series") or sorted({r[1] for r in rows})))
    div, unite = _echelle(ind)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    bas = [0.0] * len(xs)
    for k, s in enumerate(series):
        val = [next((r[2] for r in rows if r[0] == x and r[1] == s), 0) / div for x in xs]
        ax.bar(xs, val, bottom=bas, label=s, color=SERIES[k % len(SERIES)], width=0.65)
        bas = [a + b for a, b in zip(bas, val)]
    ax.set_title(v["titre"], color=PALETTE["deep"], fontweight="bold", loc="left")
    ax.set_ylabel(f"{ind['libelle']} ({unite})")
    ax.set_xlabel(v.get("libelle_x", v["x"]))
    ax.yaxis.set_major_formatter(FuncFormatter(_nombre_fr))
    ax.legend(title=v.get("libelle_serie", v["serie"]), frameon=False, ncol=len(series), loc="upper center",
              bbox_to_anchor=(0.5, -0.16))
    ax.grid(axis="y", color=PALETTE["pale"])
    ax.set_axisbelow(True)
    _sauver(fig, base)
    plt.close(fig)


# --------------------------------------------------------------------------- compléments du cahier
def completer_cahier(spec, dossier) -> None:
    """Le cadre commun n'écrit dans le cahier ni les variantes ni le parcours de l'app : on les ajoute ici."""
    f = dossier / "cahier_des_charges.md"
    q = spec.regle_a_clarifier
    variantes = "\n".join(f"{k}. {v}" for k, v in enumerate(spec.variantes, 1))
    ecrans = "\n".join(f"{k}. **{t}** — {c}" for k, (t, c) in enumerate(spec.ecrans_app, 1))
    f.write_text(f.read_text(encoding="utf-8") + f"""
Options étudiées :

{q['options']}

## 13. Trois variantes (évolutions possibles en soutenance)

{variantes}

## 14. Parcours de démonstration de l'application (3 écrans)

{ecrans}

Pendant la démonstration : choisir une période et un magasin dans les filtres, lire un indicateur et son unité, puis montrer sur l'écran 2 que les ventes de HAM avant le 2026-07-15 restent en « Cap Bon ».
""", encoding="utf-8")


# --------------------------------------------------------------------------- programme principal
def main(argv: list[str]) -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    ventes1 = generer_ventes(rng, LOT1, 2150, 500001)
    ventes2 = generer_ventes(rng, LOT2, 420, int(ventes1[-1]["ticket_id"][1:]) + 1)
    retours = generer_retours(rng, ventes1 + ventes2)
    r1 = [r for r in retours if r["_jour"] <= LOT1.fin]
    r2 = [r for r in retours if CHEVAUCHEMENT_SQL <= r["_jour"] <= LOT2.fin]
    assert not any(r["_orphelin"] for r in r1 if r["_jour"] >= CHEVAUCHEMENT_SQL)

    b1 = construire_csv(ventes1, CHAMPS, DOSES["lot1"], rng, lambda k: f"T{400000 + 37 * k}-9")
    jour_de = {v["ligne_id"]: v["date_vente"] for v in ventes1}
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None and jour_de[l.origine] >= CHEVAUCHEMENT_CSV]
    assert 10 <= len(rejouees) <= 20, len(rejouees)
    b2 = construire_csv(ventes2, CHAMPS, DOSES["lot2"], rng, lambda k: f"T{450000 + 41 * k}-9", rejouees)
    for lot, b, avec, rr, extrait in (("lot1", b1, False, r1, "2026-06-30"), ("lot2", b2, True, r2, "2026-08-31")):
        d = dossier / "sources" / lot
        ecrire_csv(d / "ventes.csv", ENTETE, [l.valeurs for l in b.lignes])
        ecrire_catalogue(d / "catalogue.xlsx")
        ecrire_magasins(d / "magasins.json", avec, extrait)
        lot_obj = LOT1 if lot == "lot1" else LOT2
        ecrire_operations(d / "operations.sqlite", rr, CHEVAUCHEMENT_SQL if lot == "lot2" else LOT1.debut, lot_obj.fin)

    def valides(rr, deja=frozenset()):
        return [r for r in rr if r["statut"] == "VALIDE" and not r["_orphelin"] and r["numero_retour"] not in deja]
    acc1 = valides(r1)
    acc2 = valides(r2, {r["numero_retour"] for r in acc1})
    lots = []
    for lot, b, rr, acc, ventes_cumul, retours_cumul, avec in (
            (LOT1, b1, r1, acc1, ventes1, acc1, False), (LOT2, b2, r2, acc2, ventes1 + ventes2, acc1 + acc2, True)):
        lots.append(LotResultat(
            lot=lot,
            sources={"ventes.csv": {"lignes": b.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "catalogue.xlsx": {"feuilles": ["Catalogue", "Familles"], "produits": len(PRODUITS),
                                        "familles": len(FAMILLES), "ligne_entete_catalogue": 3},
                     "magasins.json": {"magasins": len(MAGASINS), "versions": len(MAGASINS) + int(avec),
                                       "franchises": sum(t == "franchisé" for t in TYPE.values())},
                     "operations.sqlite": comptes_operations(rr)},
            nettoyage={"ventes.csv": {k: v for k, v in b.compteurs.items() if k != "lignes"},
                       "operations.sqlite": {"retours_annules_exclus": sum(r["statut"] == "ANNULE" for r in rr),
                                             "deja_charges": len(valides(rr)) - len(acc),
                                             "retours_acceptes_nouveaux": len(acc)}},
            rejets={"ventes.csv": b.rejets(), "operations.sqlite": {"cle_inconnue": sum(r["_orphelin"] for r in rr)}},
            tables_verite=tables_verite(ventes_cumul, retours_cumul, avec),
            increment=None if lot is LOT1 else {
                "fact_vente_ajoutees": len(ventes2), "fact_retour_ajoutees": len(acc2),
                "versions_scd2_ajoutees": 1, "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin))}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(ventes_cumul) - (0 if lot is LOT1 else len(ventes1))

    attendus = produire_reference(spec, lots)
    con = entrepot_verite(spec, lots[-1].tables_verite, LOT2.fin)
    for v in spec.visuels:
        if v["type"] == "empile_bas":
            visuel_empile_bas(spec, con, v, dossier / "reference" / "visuels" / v["fichier"])
    completer_cahier(spec, dossier)
    # double contrôle Python pur (sans SQL) des quatre indicateurs
    vt, rt = ventes1 + ventes2, acc1 + acc2
    brut = sum(v["montant"] for v in vt)
    ret = sum(r["_montant"] for r in rt)
    cout = sum(v["quantite"] * COUT[v["produit"]] for v in vt) - sum(r["qte"] * COUT[r["_produit"]] for r in rt)
    net_f = sum(v["montant"] for v in vt if TYPE[v["magasin"]] == "franchisé") - \
        sum(r["_montant"] for r in rt if TYPE[r["code_magasin"]] == "franchisé")
    ind = attendus["lot2"]["indicateurs"]
    assert (ind["ventes_nettes_millimes"], ind["marge_cout_achat_millimes"]) == (brut - ret, brut - ret - cout)
    assert abs(ind["part_franchises"] - net_f / (brut - ret)) < 1e-6
    assert abs(ind["taux_retour"] - ret / brut) < 1e-6

    ech = produire_echantillon(spec, dossier / "echantillon")
    if "--v7-data" in argv:
        exporter_v7_data(spec, ech, attendus)
    ent_v = ["lot", "ligne_id", "ticket_id", "date_vente", "magasin", "produit", "quantite", "prix_unitaire_millimes",
             "code_promo", "remise_millimes", "montant_millimes"]
    ecrire_verite_privee(spec, {
        "ventes_verite.csv": (ent_v, [{"lot": "lot1" if v["date_vente"] <= LOT1.fin else "lot2", **v,
                                       "date_vente": v["date_vente"].isoformat(), "prix_unitaire_millimes": v["prix_unitaire"],
                                       "remise_millimes": v["remise"], "montant_millimes": v["montant"]} for v in vt]),
        "retours_verite.csv": (["lot", "numero_retour", "ref_ligne_ticket", "produit", "code_magasin", "jour", "qte",
                                "montant_millimes"],
                               [{"lot": "lot1" if r["_jour"] <= LOT1.fin else "lot2", **r, "produit": r["_produit"],
                                 "jour": r["_jour"].isoformat(), "montant_millimes": r["_montant"]} for r in rt]),
        "produits_verite.csv": (["produit_id", "nom", "famille", "prix_millimes", "cout_achat_millimes"],
                                [dict(zip(["produit_id", "nom", "famille", "prix_millimes", "cout_achat_millimes"],
                                          [p[0], p[1], FAMILLES[p[2]], p[3], p[4]])) for p in PRODUITS]),
        "magasins_verite.csv": (["magasin_id", "nom", "type", "region_initiale"],
                                [{"magasin_id": m[0], "nom": m[1], "type": m[3], "region_initiale": m[4]} for m in MAGASINS]),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : ventes.csv {a['sources']['ventes.csv']['lignes']} lignes · fact_vente {a['tables']['fact_vente']} · "
              f"fact_retour {a['tables']['fact_retour']} · rejets {a['rejets']['par_motif']} · "
              f"nettes {tnd_fr(i['ventes_nettes_millimes'])} · marge {tnd_fr(i['marge_cout_achat_millimes'])} · "
              f"part franchisés {pct_fr(i['part_franchises'])} · taux retour {pct_fr(i['taux_retour'])}")
    print(f"  lot2 : {len(rejouees)} lignes des 29-30 juin recopiées (rejeu)")
    e = ech["indicateurs"]
    print(f"  échantillon : brutes {tnd_fr(e['ventes_brutes_millimes'])} · nettes {tnd_fr(e['ventes_nettes_millimes'])} · "
          f"marge {tnd_fr(e['marge_cout_achat_millimes'])} · part franchisés {pct_fr(e['part_franchises'])}")


TABLES = [
    table_dim_date(),
    Table("dim_produit", "dimension", "Catalogue : un produit par ligne (feuilles Catalogue + Familles).", [
        Colonne("produit_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("produit_id", "TEXT", "Code article normalisé (strip + majuscules), ex. `C107`."),
        Colonne("nom", "TEXT", "Libellé de l'article."),
        Colonne("famille", "TEXT", "Libellé de la famille (feuille Familles), ex. `Produits laitiers`."),
        Colonne("prix_millimes", "INTEGER", "Prix de vente du catalogue en millimes."),
        Colonne("cout_achat_millimes", "INTEGER", "Coût d'achat unitaire en millimes."),
    ], cle_metier="produit_id"),
    Table("dim_magasin", "dimension_scd2", "Magasins avec leur type et l'historique de la région (SCD2).", [
        Colonne("magasin_key", "INTEGER", "Clé technique d'une VERSION de magasin.", cle=True),
        Colonne("magasin_id", "TEXT", "Code magasin, ex. `HAM` (plusieurs versions possibles)."),
        Colonne("nom", "TEXT", "Nom du magasin."),
        Colonne("type", "TEXT", "`propre` ou `franchisé` (minuscules)."),
        Colonne("region", "TEXT", "Région commerciale de cette version."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="magasin_id"),
    Table("fact_vente", "fait", "Une ligne de ticket acceptée.", [
        Colonne("ligne_id", "TEXT", "Identifiant de la ligne de ticket (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour de la vente.", ref="dim_date.date_key"),
        Colonne("produit_key", "INTEGER", "Produit vendu.", ref="dim_produit.produit_key"),
        Colonne("magasin_key", "INTEGER", "Version du magasin valable à la date de la vente.",
                ref="dim_magasin.magasin_key"),
        Colonne("quantite", "INTEGER", "Unités vendues (entier > 0)."),
        Colonne("prix_unitaire_millimes", "INTEGER", "Prix unitaire du ticket en millimes (avant remise)."),
        Colonne("remise_millimes", "INTEGER", "Remise de la ligne en millimes (0 sans promotion)."),
        Colonne("montant_brut_millimes", "INTEGER", "quantite × prix_unitaire_millimes − remise_millimes (montant payé)."),
    ]),
    Table("fact_retour", "fait", "Un retour VALIDE de la base opérationnelle.", [
        Colonne("retour_id", "TEXT", "Numéro du retour (`numero_retour`), clé métier unique.", cle=True),
        Colonne("date_key", "INTEGER", "Jour du retour (heure ignorée).", ref="dim_date.date_key"),
        Colonne("produit_key", "INTEGER", "Produit de la ligne de vente d'origine.", ref="dim_produit.produit_key"),
        Colonne("magasin_key", "INTEGER", "Version du magasin valable à la date du RETOUR.",
                ref="dim_magasin.magasin_key"),
        Colonne("quantite", "INTEGER", "Unités retournées."),
        Colonne("montant_millimes", "INTEGER", "Montant remboursé en millimes (prix payé, remise comprise)."),
    ]),
]

if __name__ == "__main__":
    main(sys.argv[1:])
