"""Mission M06 — Hôtellerie : Dar Azur (quatre maisons d'hôtes).

    python authoring/generateurs/mission06_dar_azur.py

Écrit modele-binome/catalogue/M06/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md,
echantillon/, sources/lot1/, sources/lot2/, reference/}, le bloc M06 de v7-data.json et la vérité privée du formateur.
"""
from __future__ import annotations

from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec,
                    table_dim_date, rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv,
                    ecrire_excel, ecrire_json, ecrire_sqlite, preparer_dossier, produire_reference,
                    calculer_attendu_echantillon, ecrire_verite_privee, exporter_v7_data, format_montant,
                    tnd_fr, pct_fr, md_tableau, taille_dossier, _plt, _sauver, PALETTE, SERIES, TAILLE_MAX_MISSION)
from textes_mission06 import SPEC_TEXTES

GRAINE = 260006
CODE = "M06"
# code, nom, ville, chambres par type, coefficient de prix, saisonnalité janv.→août, nuits moyennes l'été
ETABS = [("DAH", "Dar Azur Hammamet", "Hammamet", {"DBL": 10, "TWN": 6, "FAM": 4, "STE": 2}, 1.00,
          [0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 2.2], 6.5),
         ("DSB", "Dar Azur Sidi Bou Saïd", "Sidi Bou Saïd", {"DBL": 6, "TWN": 2, "STE": 2}, 1.25,
          [0.8, 0.8, 1.0, 1.1, 1.2, 1.2, 1.3, 1.3], 3.5),
         ("DTZ", "Dar Azur Tozeur", "Tozeur", {"DBL": 6, "TWN": 4, "FAM": 2, "STE": 2}, 0.90,
          [1.6, 1.7, 1.6, 1.3, 0.8, 0.5, 0.35, 0.3], 2.0),
         ("DDJ", "Dar Azur Djerba", "Djerba", {"DBL": 8, "TWN": 4, "FAM": 4, "STE": 2}, 1.05,
          [0.6, 0.6, 0.8, 1.0, 1.2, 1.5, 1.9, 2.1], 6.5)]
CAPACITE = {e[0]: sum(e[3].values()) for e in ETABS}
TYPES = {"DBL": ("Double", 180), "TWN": ("Twin (deux lits)", 170), "FAM": ("Familiale", 260), "STE": ("Suite", 390)}
SAISON_PRIX = {1: 0.8, 2: 0.8, 3: 0.95, 4: 0.95, 5: 1.05, 6: 1.05, 7: 1.35, 8: 1.35}
TAXE = 3500                                   # taxe de séjour par nuit, millimes
CANAUX = [("DIR", "direct", 0), ("ENT", "entreprise", 10), ("OTA", "agence en ligne", 18),
          ("TOP", "tour-opérateur", 25)]
POIDS_CANAL = {"DSB": [0.35, 0.20, 0.40, 0.05], "DTZ": [0.25, 0.05, 0.35, 0.35]}
DELAI = {"DIR": (0, 45), "ENT": (2, 20), "OTA": (0, 30), "TOP": (20, 120)}
P_ANNUL = {"DIR": 0.04, "ENT": 0.03, "OTA": 0.10, "TOP": 0.05}
CHANGEMENT = ("OTA", 15, date(2026, 7, 15))
PROVENANCES = [("Tunisie", 35), ("Algérie", 15), ("Libye", 8), ("France", 14), ("Allemagne", 9), ("Italie", 7),
               ("Royaume-Uni", 5), ("Côte d'Ivoire", 4), ("Émirats arabes unis", 3)]
MOTIFS_ANNUL = [("PER", "Raison personnelle"), ("VOL", "Vol annulé ou décalé"), ("MAL", "Maladie"),
                ("DOU", "Réservation en double"), ("MET", "Météo")]
MOYENS = ["carte bancaire", "virement", "espèces", "carte bancaire", "chèque"]
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30),
           "chargement initial : séjours arrivés de janvier à juin 2026 (CSV en UTF-8)")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément : arrivées de juillet-août ; recopie les séjours arrivés le 30 juin ; commission OTA "
           "18 % → 15 % le 2026-07-15 ; **CSV encodé en cp1252**")
CHEVAUCHEMENT_CSV = date(2026, 6, 30)        # le lot 2 recopie les séjours arrivés depuis ce jour
CHEVAUCHEMENT_SQL = date(2026, 6, 20)        # la base du lot 2 recopie les annulations depuis ce jour
ENTETE = ["sejour_id", "date_reservation", "date_arrivee", "date_depart", "etablissement", "type_chambre",
          "canal", "nuitees", "prix_total", "provenance"]
CHAMPS = ChampsCSV(ENTETE, "sejour_id", "nuitees", montants=["prix_total"],
                   dates=["date_reservation", "date_arrivee", "date_depart"],
                   codes=["etablissement", "type_chambre", "canal"],
                   cles_inconnues={"etablissement": ["DMH", "DSF"], "canal": ["AGC", "WEB"],
                                   "type_chambre": ["VIL", "PEN"]})
DOSES = {"lot1": Doses(doublons_exacts=15, conflits=4, manquants=6, inconnues=7, quantites=6),
         "lot2": Doses(doublons_exacts=4, conflits=2, manquants=2, inconnues=3, quantites=3)}
ENCODAGE = {"lot1": "utf-8", "lot2": "cp1252"}


# --------------------------------------------------------------------------- vérité terrain
def prix_nuit(etab: tuple, typ: str, jour: date, canal: str) -> int:
    p = round(TYPES[typ][1] * etab[4] * SAISON_PRIX[jour.month] / 5) * 5
    if canal == "ENT":                                     # tarif entreprise −10 %
        p = round(p * 0.9 / 5) * 5
    return p * 1000 + TAXE


def sejour(rng, etab, arrivee: date, nuits: int, canal: str | None = None, typ: str | None = None,
           reservation: date | None = None) -> dict:
    canal = canal or rng.choices([c[0] for c in CANAUX], POIDS_CANAL.get(etab[0], [0.30, 0.10, 0.40, 0.20]))[0]
    typ = typ or rng.choices(list(etab[3]), list(etab[3].values()))[0]
    lo, hi = DELAI[canal]
    return {"date_reservation": reservation or arrivee - timedelta(days=rng.randint(lo, hi)),
            "date_arrivee": arrivee, "date_depart": arrivee + timedelta(days=nuits), "etablissement": etab[0],
            "type_chambre": typ, "canal": canal, "nuitees": nuits,
            "prix_total": nuits * prix_nuit(etab, typ, arrivee, canal),
            "provenance": rng.choices([p[0] for p in PROVENANCES], [p[1] for p in PROVENANCES])[0]}


def generer_sejours(rng, lot: Lot, premier: int, forces: list[tuple]) -> list[dict]:
    evs = []
    for m in sorted({d.month for d in jours(lot.debut, lot.fin)}):
        js = [d for d in jours(lot.debut, lot.fin) if d.month == m]
        for etab in ETABS:
            moy = 2.5 if m <= 6 else etab[6]
            cible = CAPACITE[etab[0]] * len(js) * min(0.9, 0.40 * etab[5][m - 1])
            for _ in range(round(cible / moy)):
                evs.append(sejour(rng, etab, rng.choice(js), rng.randint(1, round(2 * moy - 1))))
    for code, arrivee, nuits, canal, reservation in forces:      # cas frontières (documentés dans le reçu)
        evs.append(sejour(rng, next(e for e in ETABS if e[0] == code), arrivee, nuits, canal, "DBL", reservation))
    evs.sort(key=lambda e: (e["date_arrivee"], e["etablissement"], e["date_reservation"], e["prix_total"]))
    for k, e in enumerate(evs):
        e["sejour_id"] = f"DA-{premier + k}"
    return evs


def generer_annulations(rng, sejours1, sejours2) -> list[dict]:
    bruts = []
    for lot_fin, evs in ((LOT1, sejours1), (LOT2, sejours2)):
        for s in evs:
            if s["date_reservation"] == date(2026, 7, 10) or rng.random() >= P_ANNUL[s["canal"]]:
                continue
            d = s["date_arrivee"] - timedelta(days=rng.randint(0, min(40, (s["date_arrivee"] - s["date_reservation"]).days)))
            if lot_fin is LOT2:
                d = max(d, LOT2.debut)
            avant = (s["date_arrivee"] - d).days
            remb = s["prix_total"] * (2 if avant >= 7 else (1 if avant >= 2 else 0)) // 2
            bruts.append({"s": s, "jour": d, "remb": remb, "statut": "CONFIRMEE"})
    retirees = rng.sample([b for b in bruts if b["jour"] < date(2026, 6, 10)], 3) + \
        rng.sample([b for b in bruts if b["jour"] >= LOT2.debut], 2)
    for b in retirees:
        b["statut"] = "RETIREE"
    for ref, d in (("DA-09990", date(2026, 2, 11)), ("DA-09991", date(2026, 5, 3)), ("DA-09992", date(2026, 7, 22))):
        bruts.append({"s": {"sejour_id": ref, "etablissement": rng.choice(["DAH", "DDJ"]), "prix_total": 412500},
                      "jour": d, "remb": 412500, "statut": "CONFIRMEE"})
    bruts = [dict(b, h=f"{rng.randint(8, 21):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}") for b in bruts]
    bruts.sort(key=lambda b: (b["jour"], b["h"], b["s"]["sejour_id"]))
    out = []
    for i, b in enumerate(bruts, 1):
        s = b["s"]
        out.append({"id": i, "numero_annulation": f"AN26-{i:04d}", "ref_sejour": s["sejour_id"],
                    "code_etablissement": s["etablissement"], "date_annulation": f"{b['jour'].isoformat()} {b['h']}",
                    "montant_rembourse": b["remb"] / 1000, "code_motif": rng.choice(MOTIFS_ANNUL)[0],
                    "statut": b["statut"], "saisi_par": f"reception-{s['etablissement'].lower()}-{rng.randint(1, 2)}",
                    "_jour": b["jour"], "_orphelin": s["sejour_id"].startswith("DA-0999"), "_sejour": s,
                    "_remb": b["remb"]})
    return out


def versions_canaux(avec_changement: bool) -> list[dict]:
    vs = [{"canal_key": k, "canal_id": c, "libelle": l, "taux_commission_pct": t, "valid_from": "2025-01-01",
           "valid_to": CHANGEMENT[2].isoformat() if (avec_changement and c == CHANGEMENT[0]) else None}
          for k, (c, l, t) in enumerate(CANAUX, 1)]
    if avec_changement:
        vs.append({"canal_key": 5, "canal_id": "OTA", "libelle": "agence en ligne", "taux_commission_pct": CHANGEMENT[1],
                   "valid_from": CHANGEMENT[2].isoformat(), "valid_to": None})
    return vs


def tables_verite(sejours, annulations, avec_changement: bool) -> dict[str, list[dict]]:
    vs = versions_canaux(avec_changement)
    ek = {e[0]: k for k, e in enumerate(ETABS, 1)}
    taux = {v["canal_key"]: v["taux_commission_pct"] for v in vs}
    fs, par_id = [], {}
    for s in sejours:
        ck = cle_version(vs, "canal_id", "canal_key", s["canal"], s["date_arrivee"])
        assert s["prix_total"] * taux[ck] % 100 == 0
        par_id[s["sejour_id"]] = ck
        fs.append({"sejour_id": s["sejour_id"], "date_key": date_key(s["date_arrivee"]),
                   "etablissement_key": ek[s["etablissement"]], "canal_key": ck, "type_chambre": s["type_chambre"],
                   "date_reservation": s["date_reservation"].isoformat(), "date_depart": s["date_depart"].isoformat(),
                   "nuitees": s["nuitees"], "montant_millimes": s["prix_total"],
                   "commission_millimes": s["prix_total"] * taux[ck] // 100})
    fa = [{"annulation_id": a["numero_annulation"], "sejour_id": a["ref_sejour"],
           "date_key": date_key(a["_sejour"]["date_arrivee"]), "etablissement_key": ek[a["_sejour"]["etablissement"]],
           "canal_key": par_id[a["ref_sejour"]], "date_annulation": a["_jour"].isoformat(),
           "nuitees": a["_sejour"]["nuitees"], "remboursement_millimes": a["_remb"]} for a in annulations]
    de = [{"etablissement_key": ek[e[0]], "etablissement_id": e[0], "nom": e[1], "ville": e[2],
           "nombre_chambres": CAPACITE[e[0]]} for e in ETABS]
    return {"dim_etablissement": de, "dim_canal": vs, "fact_sejour": fs, "fact_annulation": fa}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_chambres(chemin) -> None:
    lignes, i = [], 0
    for code, nom, ville, types, coef, _s, _n in ETABS:
        for t, n in types.items():
            prix = round(TYPES[t][1] * coef / 5) * 5 * 1000
            lignes.append([" dsb" if (code, t) == ("DSB", "TWN") else code, nom, ville, t,
                           f"{n}" if i % 4 == 2 else n, format_montant(prix, "virgule3") if i % 3 == 1 else prix / 1000])
            i += 1
    ecrire_excel(chemin, [
        Feuille("Chambres", ["Établissement", "Nom", "Ville", "Type de chambre", "Nombre de chambres",
                             "Prix affiché (TND / nuit)"], lignes,
                titres=["Dar Azur — inventaire des chambres 2026 (une ligne par établissement et type)"]),
        Feuille("Types", ["Code type", "Libellé type"], [[k, v[0]] for k, v in TYPES.items()])])


def ecrire_canaux(chemin, avec_changement: bool, extrait_le: str) -> None:
    cs = []
    for code, lib, t in CANAUX:
        hist = [{"taux_commission": 10.0 if code == "ENT" else t, "valide_depuis": "2025-01-01"}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"taux_commission": CHANGEMENT[1], "valide_depuis": CHANGEMENT[2].isoformat()})
        cs.append({"code": code, "libelle": lib, "historique": hist})
    ecrire_json(chemin, {"source": "Contrats de distribution Dar Azur (commission en % du prix total)",
                         "extrait_le": extrait_le, "canaux": cs})


DDL_OPERATIONS = """
CREATE TABLE motif_annulation (code_motif TEXT PRIMARY KEY, libelle TEXT NOT NULL);
CREATE TABLE annulation (
  id INTEGER PRIMARY KEY,
  numero_annulation TEXT NOT NULL UNIQUE,
  ref_sejour TEXT NOT NULL,
  code_etablissement TEXT NOT NULL,
  date_annulation TEXT NOT NULL,
  montant_rembourse REAL NOT NULL,
  code_motif TEXT REFERENCES motif_annulation(code_motif),
  statut TEXT NOT NULL CHECK (statut IN ('CONFIRMEE', 'RETIREE')),
  saisi_par TEXT
);
CREATE TABLE paiement (id INTEGER PRIMARY KEY, ref_sejour TEXT NOT NULL, date_paiement TEXT NOT NULL,
  montant REAL NOT NULL, moyen TEXT NOT NULL);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""


def ecrire_operations(chemin, annulations: list[dict], paiements: list[dict], perimetre: str, au: date) -> None:
    ecrire_sqlite(chemin, DDL_OPERATIONS, {
        "motif_annulation": [{"code_motif": c, "libelle": l} for c, l in MOTIFS_ANNUL],
        "annulation": [{k: v for k, v in a.items() if not k.startswith("_")} for a in annulations],
        "paiement": paiements,
        "parametre": [{"cle": "export_genere_le", "valeur": (au + timedelta(days=1)).isoformat()},
                      {"cle": "perimetre", "valeur": perimetre}, {"cle": "devise", "valeur": "TND"}]})


def paiements_de(sejours) -> list[dict]:
    """Un encaissement par séjour (informatif : non chargé dans l'entrepôt, sert à la variante 3)."""
    return [{"id": k, "ref_sejour": s["sejour_id"], "date_paiement": s["date_reservation"].isoformat(),
             "montant": s["prix_total"] / 1000, "moyen": MOYENS[k % len(MOYENS)]} for k, s in enumerate(sejours, 1)]


def comptes_operations(aa: list[dict], n_paiements: int) -> dict:
    return {"annulation": len(aa), "confirmees": sum(a["statut"] == "CONFIRMEE" for a in aa),
            "retirees": sum(a["statut"] == "RETIREE" for a in aa), "paiement": n_paiements,
            "motif_annulation": len(MOTIFS_ANNUL)}


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
ECHANTILLON = [  # (valeurs texte, décision)
    (["E-01", "2026-02-10", "2026-03-02", "2026-03-05", "DAH", "DBL", "DIR", "3", "520.500", "Tunisie"], None),
    (["E-02", "15/02/2026", "03/03/2026", "05/03/2026", "DSB", "STE", "OTA", "2", "1 007,000", "France"], None),
    (["E-03", "20 février 2026", "6 mars 2026", "10 mars 2026", " dtz ", "TWN", "TOP", "4", "614", "Allemagne"], None),
    (["E-04", "2026-03-01", "2026-03-07", "2026-03-08", "DDJ", "FAM", "ENT", "1", "213,5", "Algérie"], None),
    (["E-04", "2026-03-01", "2026-03-07", "2026-03-08", "DDJ", "FAM", "ENT", "1", "213,5", "Algérie"], "doublon_exact"),
    (["E-05", "2026-03-05", "2026-03-12", "2026-03-15", "DAH", "fam", "Ota", "3", "790,500", "Libye"], None),
    (["E-06", "2026-03-10", "2026-03-14", "2026-03-16", "DDJ", "DBL", "DIR", "2", "390.000", "Italie"], "id_conflit"),
    (["E-06", "2026-03-10", "2026-03-14", "2026-03-16", "DDJ", "DBL", "DIR", "3", "390.000", "Italie"], "id_conflit"),
    (["", "2026-03-11", "2026-03-18", "2026-03-20", "DAH", "TWN", "DIR", "2", "347.000", "Tunisie"], "id_manquant"),
    (["E-07", "2026-03-12", "2026-03-19", "2026-03-21", "DMH", "DBL", "OTA", "2", "367.000", "France"], "cle_inconnue"),
    (["E-08", "2026-03-15", "2026-03-22", "2026-03-22", "DTZ", "DBL", "DIR", "0", "0.000", "Tunisie"], "quantite_invalide"),
    (["E-09", "2026-03-15", "30/03/2026", "02/04/2026", "DSB", "DBL", "DIR", "3", "685,5", "Italie"], None),
]
ANNUL_ECH = [(1, "AN-0001", "E-05", "DAH", "2026-03-08 10:15:00", 395.25, "PER", "CONFIRMEE"),
             (2, "AN-0002", "E-01", "DAH", "2026-02-25 16:40:00", 520.5, "MAL", "RETIREE"),
             (3, "AN-0003", "E-99", "DSB", "2026-03-09 11:05:00", 300.0, "VOL", "CONFIRMEE")]


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "sejours.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON])
    ecrire_chambres(dossier / "chambres.xlsx")
    ecrire_canaux(dossier / "canaux.json", False, "2026-03-31")
    cles = ("id", "numero_annulation", "ref_sejour", "code_etablissement", "date_annulation", "montant_rembourse",
            "code_motif", "statut")
    pay = [{"id": k, "ref_sejour": v[0], "date_paiement": "2026-03-01", "montant": float(v[8].replace(" ", "").replace(",", ".")),
            "moyen": "carte bancaire"} for k, (v, m) in enumerate(ECHANTILLON, 1) if m is None]
    ecrire_operations(dossier / "operations.sqlite", [dict(zip(cles, a), saisi_par="reception-ech-1") for a in ANNUL_ECH],
                      pay, "annulations et paiements de mars 2026", date(2026, 3, 31))
    ek = {e[0]: k for k, e in enumerate(ETABS, 1)}
    vs = versions_canaux(False)
    taux = {v["canal_key"]: v["taux_commission_pct"] for v in vs}
    acc = []
    for v, motif in ECHANTILLON:
        if motif is None:
            arr = {"2026-03-02": 2, "03/03/2026": 3, "6 mars 2026": 6, "2026-03-07": 7, "2026-03-12": 12, "30/03/2026": 30}[v[2]]
            acc.append({"id": v[0], "arrivee": date(2026, 3, arr), "etab": v[4].strip().upper(), "type": v[5].strip().upper(),
                        "canal": v[6].strip().upper(), "n": int(v[7]),
                        "m": round(float(v[8].replace(" ", "").replace(",", ".")) * 1000)})
    fs = []
    for a in acc:
        ck = cle_version(vs, "canal_id", "canal_key", a["canal"], a["arrivee"])
        a["taux"] = taux[ck]
        fs.append({"sejour_id": a["id"], "date_key": date_key(a["arrivee"]), "etablissement_key": ek[a["etab"]],
                   "canal_key": ck, "type_chambre": a["type"], "date_reservation": "2026-03-01",
                   "date_depart": (a["arrivee"] + timedelta(days=a["n"])).isoformat(), "nuitees": a["n"],
                   "montant_millimes": a["m"], "commission_millimes": a["m"] * taux[ck] // 100})
    e05 = next(f for f in fs if f["sejour_id"] == "E-05")
    fa = [{"annulation_id": "AN-0001", "sejour_id": "E-05", "date_key": e05["date_key"],
           "etablissement_key": e05["etablissement_key"], "canal_key": e05["canal_key"], "date_annulation": "2026-03-08",
           "nuitees": 3, "remboursement_millimes": 395250}]
    tables = tables_verite([], [], False)
    tables.update({"fact_sejour": fs, "fact_annulation": fa})
    rejets = {"sejours.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "operations.sqlite": {"cle_inconnue": 1}}
    att = calculer_attendu_echantillon(spec, tables, date(2026, 3, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(fs),
                                        "annulations_retirees_ignorees": 1})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(acc, att), encoding="utf-8")
    return att


def md_echantillon(acc, att) -> str:
    i = att["indicateurs"]
    t1 = md_tableau(["Ligne du fichier", "sejour_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"arrivée {v[2]} · départ {v[3]} · {v[4]!r} · {v[5]} · {v[6]} · "
                                               f"{v[7]} nuit(s) · {v[8]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 5" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    t2 = md_tableau(["sejour_id", "Arrivée", "Établissement", "Canal (taux)", "Nuitées", "Montant", "Commission"],
                    [[a["id"], a["arrivee"].isoformat(), a["etab"], f"{a['canal']} ({a['taux']} %)", a["n"],
                      tnd_fr(a["m"]), f"{format_montant(a['m'], 'virgule3')} × {a['taux']} / 100 = "
                                      f"{tnd_fr(a['m'] * a['taux'] // 100)}"] for a in acc])
    cap = i["chambres_disponibles"]
    return f"""# Échantillon Dar Azur — le calcul à la main

12 lignes de `sejours.csv`, l'inventaire complet des chambres (4 établissements, 64 chambres), les 4 canaux et 3 annulations dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`sejours.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **{len(acc)} séjours gardés**.

## 2. Séjours, montants et commissions

Une virgule ou un point sépare les décimales ; un espace sépare les milliers : `1 007,000` = 1 007 TND. Le taux de commission est celui du canal **à la date d'arrivée** (ici, avant le 15 juillet : direct 0 %, entreprise 10 %, agence en ligne 18 %, tour-opérateur 25 %).

{t2}

`E-09` arrive le 30 mars et repart le 2 avril : ses **3 nuitées comptent toutes en mars** (mois d'arrivée, décision de la direction).

**Nuitées des séjours = {sum(a['n'] for a in acc)}** · **Montant des séjours = {tnd_fr(i['montant_sejours_millimes'])}** · **Commissions = {tnd_fr(i['commissions_millimes'])}**.

## 3. Annulations (`operations.sqlite`, table `annulation`)

- `AN-0001` : séjour `E-05` (DAH, 3 nuitées), statut `CONFIRMEE`, annulé 4 jours avant l'arrivée → remboursement **395,250 TND** gardé ; ses 3 nuitées ne sont plus vendues.
- `AN-0002` : statut `RETIREE` (le client a finalement gardé son séjour) → ignorée (ce n'est pas un rejet).
- `AN-0003` : le séjour `E-99` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).

## 4. Les quatre indicateurs

- Nuitées vendues = {sum(a['n'] for a in acc)} − 3 = **{i['nuitees_vendues']}**.
- Chambres disponibles = 64 chambres × 31 nuits de mars = **{cap}** (DAH 22, DSB 10, DTZ 14, DDJ 18).
- Taux d'occupation = {i['nuitees_vendues']} / {cap} = **{pct_fr(i['taux_occupation'], 3)}** (l'échantillon est petit : c'est normal).
- Revenu net d'annulations = {tnd_fr(i['montant_sejours_millimes'])} − 395,250 TND = **{tnd_fr(i['revenu_net_millimes'])}**.
- RevPAR = {tnd_fr(i['revenu_net_millimes'])} / {cap} = **{tnd_fr(i['revpar_millimes'])}** par chambre disponible (arrondi au millime).

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_sejour` : {att['tables']['fact_sejour']} lignes · `fact_annulation` : {att['tables']['fact_annulation']} ligne · `dim_etablissement` : {att['tables']['dim_etablissement']} · `dim_canal` : {att['tables']['dim_canal']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- graphique propre à la mission
def visuel_occupation_semestres(spec, con, attendus: dict, base) -> None:
    """Taux d'occupation janvier-juin vs juillet-août par établissement (réponse directe à la décision).
    Visuel de type « fonction » : common.produire_reference l'appelle et le liste dans reference/README.md."""
    plt = _plt()
    ag = attendus["lot2"]["agregats"]["par_etablissement_mois"]
    codes = [e[0] for e in ETABS]
    periodes = [("janvier → juin", ("01", "02", "03", "04", "05", "06")), ("juillet → août", ("07", "08"))]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for k, (lib, ms) in enumerate(periodes):
        vals = []
        for c in codes:
            sel = [v for cle, v in ag.items() if cle.startswith(c + " ") and cle[-2:] in ms]
            vals.append(100 * sum(v["nuitees_vendues"] for v in sel) / sum(v["chambres_disponibles"] for v in sel))
        xs = [i + (k - 0.5) * 0.38 for i in range(len(codes))]
        b = ax.bar(xs, vals, width=0.38, label=lib, color=SERIES[k])
        ax.bar_label(b, labels=[f"{x:.1f}".replace(".", ",") for x in vals], fontsize=8, padding=2)
    ax.set_xticks(range(len(codes)), codes)
    ax.set_title("Taux d'occupation par établissement : premier semestre et été", color=PALETTE["deep"],
                 fontweight="bold", loc="left")
    ax.set_ylabel("Taux d'occupation (%)")
    ax.set_xlabel("Établissement")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=PALETTE["pale"])
    ax.set_axisbelow(True)
    _sauver(fig, base)
    plt.close(fig)


# --------------------------------------------------------------------------- programme principal
def main() -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    spec.visuels = spec.visuels[:-1] + [
        {"type": "fonction", "fichier": "occupation_semestre_ete_par_etablissement", "dessiner": visuel_occupation_semestres},
        spec.visuels[-1]]
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    s1 = generer_sejours(rng, LOT1, 10001, [("DSB", date(2026, 6, 30), 3, "OTA", date(2026, 6, 1))])
    s2 = generer_sejours(rng, LOT2, 10001 + len(s1), [("DAH", date(2026, 7, 14), 3, "OTA", date(2026, 7, 1)),
                                                      ("DDJ", date(2026, 7, 15), 2, "OTA", date(2026, 7, 2)),
                                                      ("DSB", date(2026, 7, 20), 2, "OTA", date(2026, 7, 10))])
    ann = generer_annulations(rng, s1, s2)
    a1 = [a for a in ann if a["_jour"] <= LOT1.fin]
    a2 = [a for a in ann if a["_jour"] >= CHEVAUCHEMENT_SQL]
    ids1 = {s["sejour_id"] for s in s1}
    assert all(a["_orphelin"] or a["ref_sejour"] in ids1 for a in a1)

    b1 = construire_csv(s1, CHAMPS, DOSES["lot1"], rng, lambda k: f"DA-9{k:04d}")
    par_id = {s["sejour_id"]: s for s in s1}
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None and par_id[l.origine]["date_arrivee"] >= CHEVAUCHEMENT_CSV]
    assert 10 <= len(rejouees) <= 20, len(rejouees)
    b2 = construire_csv(s2, CHAMPS, DOSES["lot2"], rng, lambda k: f"DA-8{k:04d}", rejouees)
    tous_p = paiements_de(s1 + s2)
    ids_rej = {v["sejour_id"] for v in rejouees}
    p1 = [p for p in tous_p if p["ref_sejour"] in ids1]
    p2 = [p for p in tous_p if p["ref_sejour"] not in ids1 or p["ref_sejour"] in ids_rej]
    for lot, b, avec, aa, pp, extrait, perim in (
            ("lot1", b1, False, a1, p1, "2026-06-30", "annulations jusqu'au 2026-06-30 ; paiements des séjours de janvier à juin"),
            ("lot2", b2, True, a2, p2, "2026-08-31", "annulations du 2026-06-20 au 2026-08-31 ; paiements des séjours du lot 2")):
        d = dossier / "sources" / lot
        ecrire_csv(d / "sejours.csv", ENTETE, [l.valeurs for l in b.lignes], encodage=ENCODAGE[lot])
        ecrire_chambres(d / "chambres.xlsx")
        ecrire_canaux(d / "canaux.json", avec, extrait)
        ecrire_operations(d / "operations.sqlite", aa, pp, perim, LOT1.fin if lot == "lot1" else LOT2.fin)

    def acceptees(aa, deja=frozenset()):
        return [a for a in aa if a["statut"] == "CONFIRMEE" and not a["_orphelin"] and a["numero_annulation"] not in deja]
    acc1 = acceptees(a1)
    acc2 = acceptees(a2, {a["numero_annulation"] for a in acc1})
    lots = []
    for lot, b, aa, acc, pp, s_cumul, a_cumul, avec in (
            (LOT1, b1, a1, acc1, p1, s1, acc1, False), (LOT2, b2, a2, acc2, p2, s1 + s2, acc1 + acc2, True)):
        lots.append(LotResultat(
            lot=lot,
            sources={"sejours.csv": {"lignes": b.compteurs["lignes"], "encodage": ENCODAGE[lot.nom], "separateur": ";"},
                     "chambres.xlsx": {"feuilles": ["Chambres", "Types"], "lignes_chambres": sum(len(e[3]) for e in ETABS),
                                       "etablissements": len(ETABS), "chambres": sum(CAPACITE.values()),
                                       "ligne_entete_chambres": 3},
                     "canaux.json": {"canaux": len(CANAUX), "versions": 5 if avec else 4},
                     "operations.sqlite": comptes_operations(aa, len(pp))},
            nettoyage={"sejours.csv": {k: v for k, v in b.compteurs.items() if k != "lignes"},
                       "operations.sqlite": {"annulations_retirees_ignorees": sum(a["statut"] == "RETIREE" for a in aa),
                                             "deja_chargees": len(acceptees(aa)) - len(acc),
                                             "annulations_acceptees_nouvelles": len(acc),
                                             "paiements_non_charges": len(pp)}},
            rejets={"sejours.csv": b.rejets(), "operations.sqlite": {"cle_inconnue": sum(a["_orphelin"] for a in aa)}},
            tables_verite=tables_verite(s_cumul, a_cumul, avec),
            increment=None if lot is LOT1 else {
                "fact_sejour_ajoutees": len(s2), "fact_annulation_ajoutees": len(acc2), "versions_scd2_ajoutees": 1,
                "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin)), "sejours_deja_charges": len(rejouees)}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(s_cumul) - (0 if lot is LOT1 else len(s1))

    attendus = produire_reference(spec, lots)
    # double contrôle Python pur (sans SQL) des nombres clés après le lot 2
    t = lots[-1].tables_verite
    nuits = sum(f["nuitees"] for f in t["fact_sejour"]) - sum(f["nuitees"] for f in t["fact_annulation"])
    net = sum(f["montant_millimes"] for f in t["fact_sejour"]) - sum(f["remboursement_millimes"] for f in t["fact_annulation"])
    cap = sum(CAPACITE.values()) * len(jours(LOT1.debut, LOT2.fin))
    ind = attendus["lot2"]["indicateurs"]
    assert (ind["nuitees_vendues"], ind["revenu_net_millimes"], ind["chambres_disponibles"]) == (nuits, net, cap)
    assert ind["revpar_millimes"] == round(net / cap) and abs(ind["taux_occupation"] - nuits / cap) < 1e-6

    ech = produire_echantillon(spec, dossier / "echantillon")

    ent_s = ["lot", "sejour_id", "date_reservation", "date_arrivee", "date_depart", "etablissement", "type_chambre",
             "canal", "nuitees", "prix_total_millimes"]
    ecrire_verite_privee(spec, {
        "sejours_verite.csv": (ent_s, [{"lot": "lot1" if s["sejour_id"] in ids1 else "lot2", **s,
                                        **{k: s[k].isoformat() for k in ("date_reservation", "date_arrivee", "date_depart")},
                                        "prix_total_millimes": s["prix_total"]} for s in s1 + s2]),
        "annulations_verite.csv": (["lot", "numero_annulation", "ref_sejour", "remboursement_millimes"],
                                   [{"lot": "lot1" if a in acc1 else "lot2", **a, "remboursement_millimes": a["_remb"]}
                                    for a in acc1 + acc2]),
        "etablissements_verite.csv": (["etablissement_id", "nombre_chambres"],
                                      [{"etablissement_id": c, "nombre_chambres": n} for c, n in CAPACITE.items()]),
        "canaux_verite.csv": (["canal_id", "taux_commission_pct", "valid_from", "valid_to"], versions_canaux(True)),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    exporter_v7_data(spec, ech, attendus)
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : sejours.csv {a['sources']['sejours.csv']['lignes']} lignes · fact_sejour "
              f"{a['tables']['fact_sejour']} · fact_annulation {a['tables']['fact_annulation']} · rejets "
              f"{a['rejets']['par_motif']} · nuitées {i['nuitees_vendues']} · occupation {pct_fr(i['taux_occupation'])} · "
              f"revenu net {tnd_fr(i['revenu_net_millimes'])} · RevPAR {tnd_fr(i['revpar_millimes'])}")
    print(f"  lot2 : {len(rejouees)} séjours déjà chargés recopiés · {len(s2)} nouveaux séjours")
    e = ech["indicateurs"]
    print(f"  échantillon : nuitées {e['nuitees_vendues']} · revenu net {tnd_fr(e['revenu_net_millimes'])} · "
          f"RevPAR {tnd_fr(e['revpar_millimes'])}")


TABLES = [
    table_dim_date(),
    Table("dim_etablissement", "dimension", "Établissements : un par ligne, capacité = somme des chambres (feuille Chambres).", [
        Colonne("etablissement_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("etablissement_id", "TEXT", "Code établissement normalisé (strip + majuscules), ex. `DAH`."),
        Colonne("nom", "TEXT", "Nom de l'établissement."),
        Colonne("ville", "TEXT", "Ville."),
        Colonne("nombre_chambres", "INTEGER", "Capacité : somme des chambres de tous les types de l'établissement."),
    ], cle_metier="etablissement_id"),
    Table("dim_canal", "dimension_scd2", "Canaux de vente avec historique du taux de commission (SCD2).", [
        Colonne("canal_key", "INTEGER", "Clé technique d'une VERSION de canal.", cle=True),
        Colonne("canal_id", "TEXT", "Code canal, ex. `OTA` (plusieurs versions possibles)."),
        Colonne("libelle", "TEXT", "`direct`, `agence en ligne`, `tour-opérateur` ou `entreprise`."),
        Colonne("taux_commission_pct", "INTEGER", "Commission de cette version, en % entier du prix total (ex. 18)."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="canal_id"),
    Table("fact_sejour", "fait", "Un séjour accepté (date du fait = date d'arrivée).", [
        Colonne("sejour_id", "TEXT", "Identifiant du séjour (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour d'ARRIVÉE du séjour.", ref="dim_date.date_key"),
        Colonne("etablissement_key", "INTEGER", "Établissement du séjour.", ref="dim_etablissement.etablissement_key"),
        Colonne("canal_key", "INTEGER", "Version du canal valable à la date d'arrivée.", ref="dim_canal.canal_key"),
        Colonne("type_chambre", "TEXT", "Code du type de chambre normalisé, ex. `DBL`."),
        Colonne("date_reservation", "TEXT", "Jour de la réservation, AAAA-MM-JJ (peut être en 2025)."),
        Colonne("date_depart", "TEXT", "Jour de départ, AAAA-MM-JJ (pas de nuit ce jour-là)."),
        Colonne("nuitees", "INTEGER", "Nombre de nuits (entier > 0) = départ − arrivée."),
        Colonne("montant_millimes", "INTEGER", "Prix total du séjour en millimes."),
        Colonne("commission_millimes", "INTEGER", "montant_millimes × taux_commission_pct (version à l'arrivée) / 100."),
    ]),
    Table("fact_annulation", "fait", "Une annulation CONFIRMEE de la base opérationnelle.", [
        Colonne("annulation_id", "TEXT", "Numéro de l'annulation (`numero_annulation`), clé métier unique.", cle=True),
        Colonne("sejour_id", "TEXT", "Séjour annulé.", ref="fact_sejour.sejour_id"),
        Colonne("date_key", "INTEGER", "Jour d'ARRIVÉE du séjour annulé (pas la date d'annulation).", ref="dim_date.date_key"),
        Colonne("etablissement_key", "INTEGER", "Établissement du séjour annulé.", ref="dim_etablissement.etablissement_key"),
        Colonne("canal_key", "INTEGER", "Même version de canal que le séjour annulé.", ref="dim_canal.canal_key"),
        Colonne("date_annulation", "TEXT", "Jour de l'annulation, AAAA-MM-JJ (heure ignorée)."),
        Colonne("nuitees", "INTEGER", "Nuitées du séjour annulé (elles ne sont plus vendues)."),
        Colonne("remboursement_millimes", "INTEGER", "Montant remboursé en millimes (0 possible)."),
    ]),
]

if __name__ == "__main__":
    main()
