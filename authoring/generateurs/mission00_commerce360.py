"""Mission 00 — tronc commun « Solen Commerce 360 » : Maison Zitouna (réseau de boutiques).

    python authoring/generateurs/mission00_commerce360.py

Écrit modele-binome/tronc-commun/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md,
echantillon/, sources/lot1/, sources/lot2/, reference/} et met à jour v7-data.json.
"""
from __future__ import annotations

from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, SCD2, Table, Colonne, MissionSpec,
                    table_dim_date, rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv,
                    ecrire_excel, ecrire_json, ecrire_sqlite, preparer_dossier, produire_reference,
                    calculer_attendu_echantillon, exporter_v7_data, ecrire_verite_privee, format_montant,
                    tnd_fr, pct_fr, md_tableau, taille_dossier, TAILLE_MAX_MISSION)
from textes_mission00 import SPEC_TEXTES

GRAINE = 260001
CODE = "tronc-commun"
# code, nom, famille, prix, coût (millimes), poids de vente
PRODUITS = [("P01", "Huile d'olive extra vierge 1 L", "HUI", 18500, 11200, 30),
            ("P02", "Huile d'olive extra vierge 5 L", "HUI", 82000, 52500, 9),
            ("P03", "Olives noires de Djerba 500 g", "OLV", 6800, 3900, 16),
            ("P04", "Dattes Deglet Nour 1 kg", "DAT", 14500, 8750, 18),
            ("P05", "Savon à l'huile d'olive", "COS", 3900, 1650, 14),
            ("P06", "Harissa artisanale 380 g", "EPI", 4200, 2100, 12),
            ("P07", "Coffret dégustation", "CAD", 65000, 38000, 5),
            ("P08", "Coffret entreprise (20 coffrets)", "CAD", 1240000, 790000, 1)]
FAMILLES = {"HUI": "Huiles", "OLV": "Olives", "DAT": "Dattes", "COS": "Cosmétique",
            "EPI": "Épicerie fine", "CAD": "Coffrets cadeaux"}
BOUTIQUES = [("TUN", "Maison Zitouna Tunis Centre", "Tunis", "Grand Tunis", "2018-04-02", 45),
             ("NBE", "Maison Zitouna Nabeul", "Nabeul", "Cap Bon", "2021-05-10", 25),
             ("SFX", "Maison Zitouna Sfax", "Sfax", "Sud", "2022-09-19", 30)]
CHANGEMENT = ("NBE", "Nord-Est", date(2026, 7, 15))
PAIEMENTS = ["carte bancaire", "espèces", "espèces", "chèque", "paiement mobile"]
SAISON = {1: 0.9, 2: 1.15, 3: 1.35, 4: 0.95, 5: 0.9, 6: 0.85, 7: 1.0, 8: 1.05}
MOTIFS_RETOUR = [("DEF", "Produit défectueux"), ("CAD", "Cadeau non souhaité"),
                 ("ERR", "Erreur de caisse"), ("DLC", "Date limite proche")]
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, janvier → juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 ; recopie les 29-30 juin ; NBE change de zone le 2026-07-15")
CHEVAUCHEMENT_CSV = date(2026, 6, 29)      # le lot 2 recopie les ventes depuis cette date
CHEVAUCHEMENT_SQL = date(2026, 6, 20)      # la base du lot 2 recopie les retours depuis cette date
ENTETE = ["ligne_id", "ticket_id", "date_vente", "boutique", "produit", "quantite", "prix_unitaire", "mode_paiement"]
CHAMPS = ChampsCSV(ENTETE, "ligne_id", "quantite", montants=["prix_unitaire"], dates=["date_vente"],
                   codes=["boutique", "produit"], cles_inconnues={"produit": ["P99", "P09", "P13"],
                                                                  "boutique": ["BZT", "SOU"]})
DOSES = {"lot1": Doses(doublons_exacts=14, conflits=3, manquants=5, inconnues=6, quantites=7),
         "lot2": Doses(doublons_exacts=4, conflits=1, manquants=2, inconnues=3, quantites=2)}
COUT = {p[0]: p[4] for p in PRODUITS}


# --------------------------------------------------------------------------- vérité terrain
def generer_ventes(rng, lot: Lot, n_cible: int, premier_ticket: int) -> list[dict]:
    js = jours(lot.debut, lot.fin)
    poids = [SAISON[d.month] * (1.35 if d.weekday() == 5 else 1.0) for d in js]
    par_jour = {d: 0 for d in js}
    for d in rng.choices(js, poids, k=n_cible):
        par_jour[d] += 1
    if lot is LOT2:                       # garantir des ventes NBE de part et d'autre de la frontière
        for d in (date(2026, 7, 14), date(2026, 7, 15)):
            par_jour[d] = max(par_jour[d], 3)
    ventes, num = [], premier_ticket
    for d in js:
        reste = par_jour[d]
        force_nbe = lot is LOT2 and d in (date(2026, 7, 14), date(2026, 7, 15))
        while reste > 0:
            taille = min(rng.choice([1, 1, 2, 2, 3]), reste)
            b = "NBE" if force_nbe else rng.choices([x[0] for x in BOUTIQUES], [x[5] for x in BOUTIQUES])[0]
            force_nbe = False
            prods = []
            while len(prods) < taille:
                p = rng.choices(PRODUITS, [x[5] for x in PRODUITS])[0]
                if p not in prods:
                    prods.append(p)
            paiement = rng.choice(PAIEMENTS)
            for k, p in enumerate(prods, 1):
                q = 1 if p[0] == "P08" else (rng.choice([1, 1, 2]) if p[0] in ("P02", "P07")
                                             else rng.choice([1, 1, 1, 2, 2, 3, 4]))
                prix = p[3] if rng.random() > 0.07 else round(p[3] * 0.9 / 10) * 10   # promotion -10 %
                ventes.append({"ligne_id": f"TK{num}-{k}", "ticket_id": f"TK{num}", "date_vente": d,
                               "boutique": b, "produit": p[0], "quantite": q, "prix_unitaire": prix,
                               "mode_paiement": paiement})
            num += 1
            reste -= taille
    return ventes


def generer_retours(rng, ventes: list[dict]) -> list[dict]:
    fin = LOT2.fin
    bruts = []
    for v in ventes:
        p = {"P05": 0.02, "P06": 0.02, "P08": 0.15}.get(v["produit"], 0.05)
        if v["date_vente"] > LOT1.fin:
            p *= 1.8                      # été : plus de retours (clientèle de passage)
        if rng.random() < p:
            d = v["date_vente"] + timedelta(days=rng.randint(1, 20))
            if d <= fin:
                bruts.append((v, d, "VALIDE"))
    # le cas de la règle à clarifier : vente NBE du 30 juin (ou juste avant), retour le 20 juillet
    cas = max((v for v in ventes if v["boutique"] == "NBE" and v["date_vente"] <= LOT1.fin), key=lambda v: v["date_vente"])
    bruts = [x for x in bruts if x[0] is not cas] + [(cas, date(2026, 7, 20), "VALIDE")]
    annules = (rng.sample([x for x in ventes if x["date_vente"] < date(2026, 6, 10)], 4)
               + rng.sample([x for x in ventes if date(2026, 7, 1) <= x["date_vente"] < date(2026, 8, 20)], 2))
    for v in annules:
        bruts.append((v, v["date_vente"] + timedelta(days=rng.randint(1, 10)), "ANNULE"))
    for ref, d in (("TK1999-1", date(2026, 3, 17)), ("TK2817-2", date(2026, 5, 9)), ("TK3019-1", date(2026, 8, 12))):
        faux = {"ligne_id": ref, "boutique": rng.choice(["TUN", "SFX"]), "produit": "P01",
                "quantite": 1, "prix_unitaire": 18500}
        bruts.append((faux, d, "VALIDE"))
    bruts = [(v, d, s, f"{rng.randint(9, 19):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}")
             for v, d, s in bruts]
    bruts.sort(key=lambda x: (x[1], x[3], x[0]["ligne_id"]))
    retours = []
    for i, (v, d, s, h) in enumerate(bruts, 1):
        q = rng.randint(1, v["quantite"])
        retours.append({"id": i, "numero_retour": f"R26-{i:05d}", "ref_ligne_ticket": v["ligne_id"],
                        "code_boutique": v["boutique"], "date_retour": f"{d.isoformat()} {h}", "qte": q,
                        "montant_rembourse": round(q * v["prix_unitaire"] / 1000, 3),
                        "code_motif": rng.choice(MOTIFS_RETOUR)[0], "statut": s,
                        "saisi_par": f"caisse-{v['boutique'].lower()}-{rng.randint(1, 3)}",
                        "_jour": d, "_produit": v["produit"], "_orphelin": v["ligne_id"].startswith(("TK1999", "TK2817", "TK3019"))})
    return retours


def versions_boutiques(avec_changement: bool) -> list[dict]:
    vs = []
    for k, (code, nom, _ville, zone, depuis, _w) in enumerate(BOUTIQUES, 1):
        fin = CHANGEMENT[2].isoformat() if (avec_changement and code == CHANGEMENT[0]) else None
        vs.append({"boutique_key": k, "boutique_id": code, "nom": nom, "zone": zone, "valid_from": depuis, "valid_to": fin})
    if avec_changement:
        b = next(x for x in BOUTIQUES if x[0] == CHANGEMENT[0])
        vs.append({"boutique_key": 4, "boutique_id": b[0], "nom": b[1], "zone": CHANGEMENT[1],
                   "valid_from": CHANGEMENT[2].isoformat(), "valid_to": None})
    return vs


def tables_verite(ventes, retours, avec_changement: bool) -> dict[str, list[dict]]:
    vs = versions_boutiques(avec_changement)
    pk = {p[0]: k for k, p in enumerate(PRODUITS, 1)}
    fv = [{"ligne_id": v["ligne_id"], "date_key": date_key(v["date_vente"]), "produit_key": pk[v["produit"]],
           "boutique_key": cle_version(vs, "boutique_id", "boutique_key", v["boutique"], v["date_vente"]),
           "quantite": v["quantite"], "prix_unitaire_millimes": v["prix_unitaire"],
           "montant_brut_millimes": v["quantite"] * v["prix_unitaire"]} for v in ventes]
    fr = [{"retour_id": r["numero_retour"], "date_key": date_key(r["_jour"]), "produit_key": pk[r["_produit"]],
           "boutique_key": cle_version(vs, "boutique_id", "boutique_key", r["code_boutique"], r["_jour"]),
           "quantite": r["qte"], "montant_millimes": round(r["montant_rembourse"] * 1000)} for r in retours]
    dp = [{"produit_key": k, "produit_id": p[0], "nom": p[1], "famille": FAMILLES[p[2]],
           "prix_millimes": p[3], "cout_achat_millimes": p[4]} for k, p in enumerate(PRODUITS, 1)]
    return {"dim_produit": dp, "dim_boutique": vs, "fact_vente": fv, "fact_retour": fr}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_catalogue(chemin) -> None:
    lignes = []
    for i, (code, nom, fam, prix, cout, _w) in enumerate(PRODUITS):
        prix_cell = prix / 1000 if i % 3 != 1 else format_montant(prix, "milliers" if prix >= 1_000_000 else "virgule3")
        cout_cell = cout / 1000 if i != 1 else format_montant(cout, "virgule3")
        lignes.append([" p06" if code == "P06" else code, nom, fam, prix_cell, cout_cell])
    ecrire_excel(chemin, [
        Feuille("Catalogue", ["Réf produit", "Désignation", "Famille", "Prix de vente (TND)", "Coût d'achat (TND)"],
                lignes, titres=["Maison Zitouna — catalogue et tarifs 2026 (montants en TND)"]),
        Feuille("Familles", ["Code famille", "Libellé famille"], [[k, v] for k, v in FAMILLES.items()])])


def ecrire_boutiques(chemin, avec_changement: bool, extrait_le: str) -> None:
    bs = []
    for code, nom, ville, zone, depuis, _w in BOUTIQUES:
        hist = [{"zone": zone, "valide_depuis": depuis}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"zone": CHANGEMENT[1], "valide_depuis": CHANGEMENT[2].isoformat()})
        bs.append({"code": code, "nom": nom, "ville": ville, "historique": hist})
    ecrire_json(chemin, {"source": "Référentiel des boutiques Maison Zitouna", "extrait_le": extrait_le,
                         "boutiques": bs})


DDL_OPERATIONS = """
CREATE TABLE motif_retour (code_motif TEXT PRIMARY KEY, libelle TEXT NOT NULL);
CREATE TABLE retour (
  id INTEGER PRIMARY KEY,
  numero_retour TEXT NOT NULL UNIQUE,
  ref_ligne_ticket TEXT NOT NULL,
  code_boutique TEXT NOT NULL,
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
    (["E-001-1", "E-001", "2026-03-02", "TUN", "P01", "2", "18.500", "carte bancaire"], None),
    (["E-001-2", "E-001", "02/03/2026", "TUN", "P05", "3", "3,900", "carte bancaire"], None),
    (["E-002-1", "E-002", "3 mars 2026", " nbe ", "P04", "1", "14.5", "espèces"], None),
    (["E-003-1", "E-003", "2026-03-05", "SFX", "P01", "1", "18,5", "chèque"], None),
    (["E-003-1", "E-003", "2026-03-05", "SFX", "P01", "1", "18,5", "chèque"], "doublon_exact"),
    (["E-004-1", "E-004", "2026-03-06", "Sfx", "P04", "2", "14,500", "espèces"], None),
    (["E-005-1", "E-005", "2026-03-06", "TUN", "P01", "1", "16.650", "carte bancaire"], None),
    (["E-006-1", "E-006", "2026-03-07", "TUN", "P05", "2", "3.900", "espèces"], "id_conflit"),
    (["E-006-1", "E-006", "2026-03-07", "TUN", "P05", "4", "3.900", "espèces"], "id_conflit"),
    (["", "E-007", "2026-03-08", "NBE", "P01", "1", "18.500", "espèces"], "id_manquant"),
    (["E-008-1", "E-008", "2026-03-09", "TUN", "P99", "1", "9.000", "carte bancaire"], "cle_inconnue"),
    (["E-009-1", "E-009", "2026-03-09", "NBE", "P05", "-1", "3.900", "espèces"], "quantite_invalide"),
]
RETOURS_ECH = [(1, "R-0001", "E-004-1", "SFX", "2026-03-10 10:15:00", 1, 14.5, "DEF", "VALIDE"),
               (2, "R-0002", "E-001-1", "TUN", "2026-03-11 16:40:00", 1, 18.5, "CAD", "ANNULE"),
               (3, "R-0003", "E-099-9", "TUN", "2026-03-12 11:05:00", 1, 18.5, "ERR", "VALIDE")]


def produire_echantillon(spec, dossier) -> dict:
    lignes = [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON]
    ecrire_csv(dossier / "ventes.csv", ENTETE, lignes)
    ecrire_catalogue(dossier / "catalogue.xlsx")
    ecrire_boutiques(dossier / "boutiques.json", False, "2026-03-31")
    cles = ("id", "numero_retour", "ref_ligne_ticket", "code_boutique", "date_retour", "qte",
            "montant_rembourse", "code_motif", "statut")
    ecrire_operations(dossier / "operations.sqlite", [dict(zip(cles, r), saisi_par="caisse-ech-1")
                                                      for r in RETOURS_ECH], date(2026, 3, 1), date(2026, 3, 31))
    pk = {p[0]: k for k, p in enumerate(PRODUITS, 1)}
    vs = versions_boutiques(False)
    acc = []
    for v, motif in ECHANTILLON:
        if motif is None:
            d = {"2026-03-02": 2, "02/03/2026": 2, "3 mars 2026": 3}.get(v[2], int(v[2][-2:]))
            acc.append({"ligne_id": v[0], "date": date(2026, 3, d), "boutique": v[3].strip().upper(),
                        "produit": v[4], "q": int(v[5]), "p": round(float(v[6].replace(",", ".")) * 1000)})
    fv = [{"ligne_id": a["ligne_id"], "date_key": date_key(a["date"]), "produit_key": pk[a["produit"]],
           "boutique_key": cle_version(vs, "boutique_id", "boutique_key", a["boutique"], a["date"]),
           "quantite": a["q"], "prix_unitaire_millimes": a["p"], "montant_brut_millimes": a["q"] * a["p"]} for a in acc]
    vente_ret = next(a for a in acc if a["ligne_id"] == "E-004-1")
    fr = [{"retour_id": "R-0001", "date_key": 20260310, "produit_key": pk[vente_ret["produit"]],
           "boutique_key": 3, "quantite": 1, "montant_millimes": 14500}]
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
    t1 = md_tableau(["Ligne du fichier", "ligne_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[2]} · {v[3]!r} · {v[4]} · qté {v[5]} · prix {v[6]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 5" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    t2 = md_tableau(["ligne_id", "Date ISO", "Boutique", "Produit", "Calcul", "Montant brut"],
                    [[a["ligne_id"], a["date"].isoformat(), a["boutique"], a["produit"],
                      f"{a['q']} × {format_montant(a['p'], 'virgule3')}", tnd_fr(a["q"] * a["p"])] for a in acc])
    cout_v = " + ".join(f"{a['q']} × {format_montant(COUT[a['produit']], 'virgule3')}" for a in acc)
    cv = sum(a["q"] * COUT[a["produit"]] for a in acc)
    return f"""# Échantillon Maison Zitouna — le calcul à la main

12 lignes de `ventes.csv`, le catalogue complet, 3 boutiques, 3 retours dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`ventes.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées**.

## 2. Ventes brutes

Une virgule ou un point sépare les décimales : `18,5` = `18.500` = 18 500 millimes. `16.650` est un prix promotionnel : on garde le prix du ticket.

{t2}

**Ventes brutes = {tnd_fr(i['ventes_brutes_millimes'])}** ({i['ventes_brutes_millimes']} millimes).

## 3. Retours (`operations.sqlite`, table `retour`)

- `R-0001` : 1 × Dattes (ligne `E-004-1`, SFX), statut `VALIDE` → **14,500 TND gardés**.
- `R-0002` : statut `ANNULE` → ignoré (ce n'est pas un rejet).
- `R-0003` : la ligne `E-099-9` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).

**Retours = {tnd_fr(i['retours_millimes'])}.**

## 4. Ventes nettes, coût d'achat, marge, taux de retour

- Ventes nettes = brutes − retours = {tnd_fr(i['ventes_brutes_millimes'])} − {tnd_fr(i['retours_millimes'])} = **{tnd_fr(i['ventes_nettes_millimes'])}**.
- Coût d'achat des unités vendues = {cout_v} = {tnd_fr(cv)}.
- Unités retournées : 1 × 8,750 (coût des dattes) = 8,750 TND. Coût d'achat des unités nettes = {tnd_fr(cv)} − 8,750 TND = **{tnd_fr(i['cout_achat_net_millimes'])}**.
- Marge sur coût d'achat = ventes nettes − coût des unités nettes = **{tnd_fr(i['marge_cout_achat_millimes'])}**.
- Taux de retour = retours / brutes = {i['retours_millimes']} / {i['ventes_brutes_millimes']} = **{pct_fr(i['taux_retour'])}**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_vente` : {att['tables']['fact_vente']} lignes · `fact_retour` : {att['tables']['fact_retour']} ligne · `dim_produit` : {att['tables']['dim_produit']} · `dim_boutique` : {att['tables']['dim_boutique']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- programme principal
def main() -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    ventes1 = generer_ventes(rng, LOT1, 1960, 10001)
    ventes2 = generer_ventes(rng, LOT2, 385, int(ventes1[-1]["ticket_id"][2:]) + 1)
    retours = generer_retours(rng, ventes1 + ventes2)
    r1 = [r for r in retours if r["_jour"] <= LOT1.fin]
    r2 = [r for r in retours if CHEVAUCHEMENT_SQL <= r["_jour"] <= LOT2.fin]
    assert not any(r["_orphelin"] for r in r1 if r["_jour"] >= CHEVAUCHEMENT_SQL)

    b1 = construire_csv(ventes1, CHAMPS, DOSES["lot1"], rng, lambda k: f"TK{10000 + 37 * k}-9")
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None
                and next(v for v in ventes1 if v["ligne_id"] == l.origine)["date_vente"] >= CHEVAUCHEMENT_CSV]
    b2 = construire_csv(ventes2, CHAMPS, DOSES["lot2"], rng, lambda k: f"TK{20000 + 41 * k}-9", rejouees)
    for lot, b, avec, rr, extrait in (("lot1", b1, False, r1, "2026-06-30"), ("lot2", b2, True, r2, "2026-08-31")):
        d = dossier / "sources" / lot
        ecrire_csv(d / "ventes.csv", ENTETE, [l.valeurs for l in b.lignes])
        ecrire_catalogue(d / "catalogue.xlsx")
        ecrire_boutiques(d / "boutiques.json", avec, extrait)
        lot_obj = LOT1 if lot == "lot1" else LOT2
        ecrire_operations(d / "operations.sqlite", rr, CHEVAUCHEMENT_SQL if lot == "lot2" else LOT1.debut, lot_obj.fin)

    def valides(rr, deja=frozenset()):
        return [r for r in rr if r["statut"] == "VALIDE" and not r["_orphelin"] and r["numero_retour"] not in deja]
    acc1 = valides(r1)
    acc2 = valides(r2, {r["numero_retour"] for r in acc1})
    lots = []
    for lot, b, rr, acc, ventes_cumul, retours_cumul, avec in (
            (LOT1, b1, r1, acc1, ventes1, acc1, False), (LOT2, b2, r2, acc2, ventes1 + ventes2, acc1 + acc2, True)):
        nb_versions = 4 if avec else 3
        lots.append(LotResultat(
            lot=lot,
            sources={"ventes.csv": {"lignes": b.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "catalogue.xlsx": {"feuilles": ["Catalogue", "Familles"], "produits": len(PRODUITS),
                                        "familles": len(FAMILLES), "ligne_entete_catalogue": 3},
                     "boutiques.json": {"boutiques": len(BOUTIQUES), "versions": nb_versions},
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
    # double contrôle Python pur (sans SQL) des trois nombres clés
    t = lots[-1].tables_verite
    brut = sum(f["montant_brut_millimes"] for f in t["fact_vente"])
    ret = sum(f["montant_millimes"] for f in t["fact_retour"])
    cout = sum(v["quantite"] * COUT[v["produit"]] for v in ventes1 + ventes2) - \
        sum(r["qte"] * COUT[r["_produit"]] for r in acc1 + acc2)
    ind = attendus["lot2"]["indicateurs"]
    assert (ind["ventes_nettes_millimes"], ind["marge_cout_achat_millimes"]) == (brut - ret, brut - ret - cout)

    ech = produire_echantillon(spec, dossier / "echantillon")
    exporter_v7_data(spec, ech, attendus)
    ent_v = ["lot", "ligne_id", "ticket_id", "date_vente", "boutique", "produit", "quantite", "prix_unitaire_millimes"]
    ecrire_verite_privee(spec, {
        "ventes_verite.csv": (ent_v, [{"lot": "lot1" if v in ventes1 else "lot2", **v, "date_vente": v["date_vente"].isoformat(),
                                       "prix_unitaire_millimes": v["prix_unitaire"]} for v in ventes1 + ventes2]),
        "retours_verite.csv": (["lot", "numero_retour", "ref_ligne_ticket", "produit", "code_boutique", "jour", "qte", "montant_millimes"],
                               [{"lot": "lot1" if r in acc1 else "lot2", **r, "produit": r["_produit"], "jour": r["_jour"].isoformat(),
                                 "montant_millimes": round(r["montant_rembourse"] * 1000)} for r in acc1 + acc2]),
        "produits_verite.csv": (["produit_id", "nom", "famille", "prix_millimes", "cout_achat_millimes"],
                                [dict(zip(["produit_id", "nom", "famille", "prix_millimes", "cout_achat_millimes"],
                                          [p[0], p[1], FAMILLES[p[2]], p[3], p[4]])) for p in PRODUITS]),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    a1, a2 = attendus["lot1"], attendus["lot2"]
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in (a1, a2):
        i = a["indicateurs"]
        print(f"  {a['lot']} : ventes.csv {a['sources']['ventes.csv']['lignes']} lignes · fact_vente {a['tables']['fact_vente']} · "
              f"fact_retour {a['tables']['fact_retour']} · rejets {a['rejets']['par_motif']} · "
              f"nettes {tnd_fr(i['ventes_nettes_millimes'])} · marge {tnd_fr(i['marge_cout_achat_millimes'])} · "
              f"taux retour {pct_fr(i['taux_retour'])}")
    e = ech["indicateurs"]
    print(f"  échantillon : brutes {tnd_fr(e['ventes_brutes_millimes'])} · nettes {tnd_fr(e['ventes_nettes_millimes'])} · "
          f"marge {tnd_fr(e['marge_cout_achat_millimes'])}")


TABLES = [
    table_dim_date(),
    Table("dim_produit", "dimension", "Catalogue : un produit par ligne (feuilles Catalogue + Familles).", [
        Colonne("produit_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("produit_id", "TEXT", "Code produit normalisé (strip + majuscules), ex. `P01`."),
        Colonne("nom", "TEXT", "Désignation."),
        Colonne("famille", "TEXT", "Libellé de la famille (feuille Familles), ex. `Huiles`."),
        Colonne("prix_millimes", "INTEGER", "Prix de vente du catalogue en millimes."),
        Colonne("cout_achat_millimes", "INTEGER", "Coût d'achat unitaire en millimes."),
    ], cle_metier="produit_id"),
    Table("dim_boutique", "dimension_scd2", "Boutiques avec historique de la zone commerciale (SCD2).", [
        Colonne("boutique_key", "INTEGER", "Clé technique d'une VERSION de boutique.", cle=True),
        Colonne("boutique_id", "TEXT", "Code boutique, ex. `NBE` (plusieurs versions possibles)."),
        Colonne("nom", "TEXT", "Nom de la boutique."),
        Colonne("zone", "TEXT", "Zone commerciale de cette version."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="boutique_id"),
    Table("fact_vente", "fait", "Une ligne de ticket acceptée.", [
        Colonne("ligne_id", "TEXT", "Identifiant de la ligne de ticket (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour de la vente.", ref="dim_date.date_key"),
        Colonne("produit_key", "INTEGER", "Produit vendu.", ref="dim_produit.produit_key"),
        Colonne("boutique_key", "INTEGER", "Version de la boutique valable à la date de la vente.",
                ref="dim_boutique.boutique_key"),
        Colonne("quantite", "INTEGER", "Unités vendues (entier > 0)."),
        Colonne("prix_unitaire_millimes", "INTEGER", "Prix du ticket en millimes (promotion possible)."),
        Colonne("montant_brut_millimes", "INTEGER", "quantite × prix_unitaire_millimes."),
    ]),
    Table("fact_retour", "fait", "Un retour VALIDE de la base opérationnelle.", [
        Colonne("retour_id", "TEXT", "Numéro du retour (`numero_retour`), clé métier unique.", cle=True),
        Colonne("date_key", "INTEGER", "Jour du retour (heure ignorée).", ref="dim_date.date_key"),
        Colonne("produit_key", "INTEGER", "Produit de la ligne de vente d'origine.", ref="dim_produit.produit_key"),
        Colonne("boutique_key", "INTEGER", "Version de la boutique valable à la date du RETOUR.",
                ref="dim_boutique.boutique_key"),
        Colonne("quantite", "INTEGER", "Unités retournées."),
        Colonne("montant_millimes", "INTEGER", "Montant remboursé en millimes."),
    ]),
]

if __name__ == "__main__":
    main()
