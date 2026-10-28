"""Mission M09 — Événementiel « Scène Libre » (concerts, théâtre, festivals).

    python authoring/generateurs/mission09_scene_libre.py            # écrit la mission

Écrit modele-binome/catalogue/M09/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md, echantillon/,
sources/lot1/, sources/lot2/, reference/} et, si SOLEN_VERITE_PRIVEE est définie,
la vérité brute dans <SOLEN_VERITE_PRIVEE>/M09/ (dossier privé, hors dépôt).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec, table_dim_date,
                    rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv, ecrire_excel, ecrire_json,
                    ecrire_sqlite, preparer_dossier, produire_reference, calculer_attendu_echantillon,
                    exporter_v7_data, ecrire_verite_privee, format_date, format_montant, tnd_fr, pct_fr,
                    md_tableau, taille_dossier, TAILLE_MAX_MISSION)
from textes_mission09 import SPEC_TEXTES

GRAINE = 260009
CODE = "M09"
LIEUX = {"JAS": ("Théâtre des Jasmins", "Tunis", 220), "KAS": ("Espace Kasbah Live", "Tunis", 450),
         "COR": ("Amphithéâtre de la Corniche", "Sousse", 600), "ZEP": ("Salle Zéphyr", "Sfax", 180),
         "ORA": ("Jardin des Orangers", "Nabeul", 1000)}
TARIFS = {"Concert": {"VIP": 80, "CAT1": 50, "CAT2": 35}, "Théâtre": {"CAT1": 40, "CAT2": 25},
          "Festival": {"VIP": 120, "CAT1": 70, "CAT2": 45}}
POIDS_CAT = {"VIP": 12, "CAT1": 45, "CAT2": 43}
# code, nom, type, lieu, date (actuelle), part de la salle vendue sur toute la fenêtre, fenêtre (jours), lot d'annonce
EVENEMENTS = [
    ("EV01", "Nuit du malouf revisité", "Concert", "JAS", date(2026, 2, 14), 0.95, 45, 1),
    ("EV02", "Les Fourberies du quartier", "Théâtre", "ZEP", date(2026, 2, 28), 0.70, 45, 1),
    ("EV03", "Rythmes du Sahel", "Concert", "KAS", date(2026, 3, 20), 0.50, 60, 1),
    ("EV04", "Le Silence des oliviers", "Théâtre", "JAS", date(2026, 4, 4), 0.88, 50, 1),
    ("EV05", "Jazz sur la Corniche", "Concert", "COR", date(2026, 4, 25), 0.55, 60, 1),
    ("EV06", "Festival Printemps Libre", "Festival", "ORA", date(2026, 5, 16), 0.33, 90, 1),
    ("EV07", "Contes de la Médina", "Théâtre", "ZEP", date(2026, 5, 30), 0.92, 45, 1),
    ("EV08", "Électro Dunes", "Concert", "KAS", date(2026, 7, 11), 0.55, 100, 1),
    ("EV09", "Hommage aux divas", "Concert", "COR", date(2026, 6, 27), 0.58, 75, 1),
    ("EV10", "Rire en été", "Théâtre", "JAS", date(2026, 7, 4), 0.90, 50, 1),
    ("EV11", "Festival Mer et Musique", "Festival", "ORA", date(2026, 7, 25), 0.17, 100, 1),
    ("EV12", "Quatuor des sables", "Concert", "ZEP", date(2026, 8, 8), 0.60, 70, 1),
    ("EV13", "La Ronde des masques", "Théâtre", "JAS", date(2026, 8, 22), 0.30, 60, 1),
    ("EV14", "Nuits de la Corniche", "Festival", "COR", date(2026, 9, 5), 0.16, 90, 1),
    ("EV15", "Slam et oud", "Concert", "KAS", date(2026, 8, 29), 0.14, 45, 2),
    ("EV16", "Festival des Jeunes Talents", "Festival", "ORA", date(2026, 9, 12), 0.05, 60, 2),
    ("EV17", "Le Barbier en scène", "Théâtre", "ZEP", date(2026, 9, 19), 0.35, 60, 2),
]
TARIFS_SPECIAUX = {"EV09": {"VIP": 100, "CAT1": 60, "CAT2": 40}, "EV16": {"VIP": 60, "CAT1": 35, "CAT2": 20}}
ANNULATIONS = {"EV05": date(2026, 4, 10), "EV12": date(2026, 7, 18)}
REPORT = ("EV08", date(2026, 5, 20), date(2026, 6, 13))       # événement, annonce du report, date initiale
# code, libellé, frais (pour mille), valide depuis, texte du JSON, poids de vente
CANAUX = [("WEB", "billetterie en ligne", 45, "2025-09-01", "4,5 %", 50), ("GUI", "guichet", 0, "2025-09-01", 0, 18),
          ("REV", "revendeur", 90, "2025-09-01", "9 %", 20), ("PAR", "partenaire", 60, "2025-11-15", 6, 12)]
CHANGEMENT = ("REV", 110, date(2026, 7, 15), "11 %")
MOTIFS = [("ANNULATION", "Événement annulé"), ("REPORT", "Événement reporté"), ("CONVENANCE", "Convenance personnelle")]
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial : billets vendus de janvier à juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 ; recopie les 16 derniers billets de juin ; 3 nouveaux événements ; "
           "REV passe à 11 % le 2026-07-15")
N_REJOUEES = 16                            # le lot 2 recopie les 16 derniers billets du lot 1
CHEVAUCHEMENT_SQL = date(2026, 6, 1)
ENTETE = ["billet_id", "evenement", "canal", "date_vente", "categorie", "nb_places", "prix"]
CHAMPS = ChampsCSV(ENTETE, "billet_id", "nb_places", montants=["prix"], dates=["date_vente"],
                   codes=["evenement", "canal", "categorie"],
                   cles_inconnues={"evenement": ["EV99", "EV18", "EV00"], "canal": ["TEL", "APP"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=5, inconnues=6, quantites=6),
         "lot2": Doses(doublons_exacts=4, conflits=1, manquants=2, inconnues=3, quantites=2)}
ORPHELINS = [("B990001", date(2026, 3, 3)), ("B990002", date(2026, 5, 12)), ("B990003", date(2026, 8, 6))]
EV = {e[0]: e for e in EVENEMENTS}


def tarifs(code: str) -> dict[str, int]:
    return TARIFS_SPECIAUX.get(code, TARIFS[EV[code][2]])


def capacite(code: str) -> int:
    return LIEUX[EV[code][3]][2]


# --------------------------------------------------------------------------- vérité terrain
def generer_billets(rng) -> list[dict]:
    ventes = []
    for code, _nom, typ, _lieu, d_ev, part, fenetre, lot_annonce in EVENEMENTS:
        ouverture = max(d_ev - timedelta(days=fenetre), date(2026, 1, 2) if lot_annonce == 1 else LOT2.debut)
        js = jours(ouverture, d_ev - timedelta(days=1))
        poids = [1 + 3 * ((i + 1) / len(js)) ** 2 for i in range(len(js))]      # on achète plutôt au dernier moment
        fin = min(ANNULATIONS.get(code, d_ev) - timedelta(days=1), LOT2.fin)
        cats = list(tarifs(code))
        for d in sorted(rng.choices(js, poids, k=round(capacite(code) * part))):
            canal = rng.choices([c[0] for c in CANAUX], [c[5] * (2 if c[0] == "PAR" and typ == "Festival" else 1)
                                                         for c in CANAUX])[0]
            cat = rng.choices(cats, [POIDS_CAT[c] for c in cats])[0]
            prix = tarifs(code)[cat] * (800 if cat == "CAT2" and rng.random() < 0.15 else 1000)  # tarif réduit −20 %
            if d <= fin:
                ventes.append({"evenement": code, "canal": canal, "date_vente": d, "categorie": cat, "nb_places": 1,
                               "prix": prix, "_tri": rng.random()})
    for jour in (date(2026, 7, 14), date(2026, 7, 15)):     # des ventes REV de part et d'autre de la frontière
        next(v for v in ventes if v["date_vente"] == jour and v["evenement"] != "EV12")["canal"] = "REV"
    ventes.sort(key=lambda v: (v["date_vente"], v["_tri"]))
    for k, v in enumerate(ventes):
        v["billet_id"] = f"B{100001 + k}"
        del v["_tri"]
    return ventes


def generer_remboursements(rng, billets: list[dict]) -> list[dict]:
    bruts = []
    for b in billets:
        ev = b["evenement"]
        if ev in ANNULATIONS:
            bruts.append((b, ANNULATIONS[ev] + timedelta(days=rng.randint(0, 20)), "ANNULATION", "REMBOURSE"))
        elif ev == REPORT[0] and b["date_vente"] < REPORT[1]:
            if rng.random() < 0.35:
                bruts.append((b, REPORT[1] + timedelta(days=rng.randint(0, 45)), "REPORT",
                              "REMBOURSE" if rng.random() < 0.55 else "CONSERVE"))
        elif rng.random() < 0.012:
            d = b["date_vente"] + timedelta(days=rng.randint(1, 15))
            if d < EV[ev][4] and d <= LOT2.fin:
                bruts.append((b, d, "CONVENANCE", "REFUSE"))
    for bid, d in ORPHELINS:
        bruts.append(({"billet_id": bid, "evenement": "EV99", "canal": "WEB", "prix": 45000}, d, "ANNULATION", "REMBOURSE"))
    bruts = [(b, d, m, s, f"{rng.randint(9, 18):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}")
             for b, d, m, s in bruts]
    bruts.sort(key=lambda x: (x[1], x[4], x[0]["billet_id"]))
    out = []
    for i, (b, d, m, s, h) in enumerate(bruts, 1):
        out.append({"id": i, "numero": f"RB26-{i:05d}", "billet_id": b["billet_id"], "date_operation": f"{d} {h}",
                    "montant_rembourse": round(b["prix"] / 1000, 3) if s == "REMBOURSE" else 0.0,
                    "code_motif": m, "statut": s, "traite_par": f"agent-{rng.randint(1, 4)}",
                    "_jour": d, "_billet": b, "_orphelin": b["billet_id"].startswith("B99")})
    return out


def versions_canaux(avec_changement: bool) -> list[dict]:
    vs = [{"canal_key": k, "canal_id": c, "libelle": lib, "frais_pour_mille": pm, "valid_from": depuis,
           "valid_to": CHANGEMENT[2].isoformat() if avec_changement and c == CHANGEMENT[0] else None}
          for k, (c, lib, pm, depuis, _t, _w) in enumerate(CANAUX, 1)]
    if avec_changement:
        lib = next(c[1] for c in CANAUX if c[0] == CHANGEMENT[0])
        vs.append({"canal_key": len(CANAUX) + 1, "canal_id": CHANGEMENT[0], "libelle": lib,
                   "frais_pour_mille": CHANGEMENT[1], "valid_from": CHANGEMENT[2].isoformat(), "valid_to": None})
    return vs


def frais(prix: int, pm: int) -> int:
    return (prix * pm + 500) // 1000          # arrondi au millime le plus proche (tombe juste : prix en TND entiers)


def dim_evenements(lot: int, programme=EVENEMENTS, cap=capacite) -> list[dict]:
    return [{"evenement_key": k, "evenement_id": e[0], "nom": e[1], "type_evenement": e[2], "lieu": LIEUX[e[3]][0],
             "ville": LIEUX[e[3]][1], "date_evenement": e[4].isoformat(), "capacite": cap(e[0])}
            for k, e in enumerate(programme, 1) if e[7] <= lot]


def tables_verite(billets, rembs, lot: int) -> dict[str, list[dict]]:
    vs = versions_canaux(lot == 2)
    de = dim_evenements(lot)
    ek = {e["evenement_id"]: e["evenement_key"] for e in de}
    pm = {v["canal_key"]: v["frais_pour_mille"] for v in vs}
    fb = []
    for b in billets:
        ck = cle_version(vs, "canal_id", "canal_key", b["canal"], b["date_vente"])
        fb.append({"billet_id": b["billet_id"], "date_key": date_key(b["date_vente"]), "evenement_key": ek[b["evenement"]],
                   "canal_key": ck, "categorie": b["categorie"], "prix_millimes": b["prix"],
                   "frais_millimes": frais(b["prix"], pm[ck])})
    fr = [{"remboursement_id": r["numero"], "billet_id": r["billet_id"], "date_key": date_key(r["_jour"]),
           "evenement_key": ek[r["_billet"]["evenement"]],
           "canal_key": cle_version(vs, "canal_id", "canal_key", r["_billet"]["canal"], r["_jour"]),
           "motif": r["code_motif"], "montant_millimes": round(r["montant_rembourse"] * 1000)} for r in rembs]
    return {"dim_evenement": de, "dim_canal": vs, "fact_billet": fb, "fact_remboursement": fr}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_programme(chemin, lot: int, programme=EVENEMENTS, cap=capacite, statuts=None, titre=None) -> None:
    lignes, tar = [], []
    for i, e in enumerate(x for x in programme if x[7] <= lot):
        code, nom, typ, lieu, d = e[:5]
        cell_d = (datetime(d.year, d.month, d.day) if i % 4 != 1 else format_date(d, "fr"))
        if code == "EV04":
            cell_d = format_date(d, "long")
        c = cap(code)
        statut = (statuts or {}).get(code) or ("annulé" if code in ANNULATIONS and ANNULATIONS[code] <= (
            LOT1.fin if lot == 1 else LOT2.fin) else ("reporté" if code == REPORT[0] else "programmé"))
        lignes.append([" ev07" if code == "EV07" else code, nom, typ, LIEUX[lieu][0], LIEUX[lieu][1], cell_d,
                       f"{c:,}".replace(",", " ") if c >= 1000 else c, statut])
        for k, (cat, t) in enumerate((tarifs(code) if code in EV else TARIFS[typ]).items()):
            tar.append([code, cat, format_montant(t * 1000, "virgule3") if (i + k) % 5 == 2 else t])
    ecrire_excel(chemin, [
        Feuille("Programme", ["Code", "Événement", "Type", "Lieu", "Ville", "Date", "Capacité", "Statut"], lignes,
                titres=[titre or "Scène Libre — programme de la saison 2026 (capacité en places)"]),
        Feuille("Tarifs", ["Code événement", "Catégorie", "Tarif (TND)"], tar)])


def ecrire_canaux(chemin, avec_changement: bool, extrait_le: str) -> None:
    cs = []
    for code, lib, _pm, depuis, texte, _w in CANAUX:
        hist = [{"frais_distribution": texte, "valide_depuis": depuis}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"frais_distribution": CHANGEMENT[3], "valide_depuis": CHANGEMENT[2].isoformat()})
        cs.append({"code": code, "libelle": lib, "historique": hist})
    ecrire_json(chemin, {"source": "Référentiel des canaux de vente Scène Libre", "extrait_le": extrait_le,
                         "unite_frais": "pourcentage du prix payé", "canaux": cs})


DDL_REMBOURSEMENTS = """
CREATE TABLE motif (code_motif TEXT PRIMARY KEY, libelle TEXT NOT NULL);
CREATE TABLE remboursement (
  id INTEGER PRIMARY KEY,
  numero TEXT NOT NULL UNIQUE,
  billet_id TEXT NOT NULL,
  date_operation TEXT NOT NULL,
  montant_rembourse REAL NOT NULL,
  code_motif TEXT REFERENCES motif(code_motif),
  statut TEXT NOT NULL CHECK (statut IN ('REMBOURSE', 'CONSERVE', 'REFUSE')),
  traite_par TEXT
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""


def ecrire_remboursements(chemin, rembs: list[dict], du: date, au: date) -> None:
    ecrire_sqlite(chemin, DDL_REMBOURSEMENTS, {
        "motif": [{"code_motif": c, "libelle": l} for c, l in MOTIFS],
        "remboursement": [{k: v for k, v in r.items() if not k.startswith("_")} for r in rembs],
        "parametre": [{"cle": "export_genere_le", "valeur": (au + timedelta(days=1)).isoformat()},
                      {"cle": "perimetre", "valeur": f"décisions du {du.isoformat()} au {au.isoformat()}"},
                      {"cle": "devise", "valeur": "TND"}]})


def comptes_remboursements(rr: list[dict]) -> dict:
    return {"remboursement": len(rr), **{s.lower(): sum(r["statut"] == s for r in rr)
                                         for s in ("REMBOURSE", "CONSERVE", "REFUSE")}, "motif": len(MOTIFS)}


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
PROGRAMME_ECH = [("EV01", "Avant-première : Le Silence des oliviers", "Théâtre", "JAS", date(2026, 3, 14), 0, 0, 1),
                 ("EV02", "Concert d'essai : Rythmes du Sahel", "Concert", "KAS", date(2026, 3, 28), 0, 0, 1)]
CAP_ECH = {"EV01": 10, "EV02": 8}
ECHANTILLON = [  # (valeurs texte, décision)
    (["S-001", "EV01", "WEB", "2026-03-02", "CAT1", "1", "40.000"], None),
    (["S-002", "EV01", " web ", "02/03/2026", "CAT2", "1", "25,000"], None),
    (["S-003", "EV01", "GUI", "3 mars 2026", "cat2", "1", "20"], None),
    (["S-004", "EV02", "REV", "2026-03-05", "VIP", "1", "80,000"], None),
    (["S-004", "EV02", "REV", "2026-03-05", "VIP", "1", "80,000"], "doublon_exact"),
    (["S-005", "EV02", "PAR", "2026-03-06", "CAT1", "1", "50,0"], None),
    (["S-006", "EV02", "WEB", "2026-03-06", "CAT1", "1", "50.000"], "id_conflit"),
    (["S-006", "EV02", "WEB", "2026-03-06", "CAT1", "2", "50.000"], "id_conflit"),
    (["", "EV01", "WEB", "2026-03-07", "CAT1", "1", "40.000"], "id_manquant"),
    (["S-007", "EV99", "WEB", "2026-03-07", "CAT1", "1", "40.000"], "cle_inconnue"),
    (["S-008", "EV01", "GUI", "2026-03-08", "CAT2", "0", "25.000"], "quantite_invalide"),
    (["S-009", "EV02", "Rev", "2026-03-09", "CAT2", "1", "35"], None),
]
REMB_ECH = [(1, "RB-0001", "S-005", "2026-03-10 10:15:00", 50.0, "REPORT", "REMBOURSE"),
            (2, "RB-0002", "S-001", "2026-03-11 16:40:00", 0.0, "REPORT", "CONSERVE"),
            (3, "RB-0003", "S-099", "2026-03-12 11:05:00", 40.0, "ANNULATION", "REMBOURSE"),
            (4, "RB-0004", "S-002", "2026-03-12 15:30:00", 0.0, "CONVENANCE", "REFUSE")]


def lire_date_ech(t: str) -> date:
    return {"02/03/2026": date(2026, 3, 2), "3 mars 2026": date(2026, 3, 3)}.get(t) or date.fromisoformat(t)


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "billets.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON])
    ecrire_programme(dossier / "evenements.xlsx", 1, PROGRAMME_ECH, CAP_ECH.get, {"EV01": "programmé", "EV02": "reporté"},
                     "Scène Libre — échantillon de programme (mars 2026)")
    ecrire_canaux(dossier / "canaux.json", False, "2026-03-31")
    cles = ("id", "numero", "billet_id", "date_operation", "montant_rembourse", "code_motif", "statut")
    ecrire_remboursements(dossier / "remboursements.sqlite", [dict(zip(cles, r), traite_par="agent-1") for r in REMB_ECH],
                          date(2026, 3, 1), date(2026, 3, 31))
    vs = versions_canaux(False)
    pm = {v["canal_key"]: v["frais_pour_mille"] for v in vs}
    de = dim_evenements(1, PROGRAMME_ECH, CAP_ECH.get)
    ek = {e["evenement_id"]: e["evenement_key"] for e in de}
    acc = [{"billet_id": v[0], "ev": v[1], "canal": v[2].strip().upper(), "date": lire_date_ech(v[3]),
            "cat": v[4].upper(), "prix": round(float(v[6].replace(",", ".")) * 1000)} for v, m in ECHANTILLON if m is None]
    fb = []
    for a in acc:
        ck = cle_version(vs, "canal_id", "canal_key", a["canal"], a["date"])
        a["pm"], a["frais"] = pm[ck], frais(a["prix"], pm[ck])
        fb.append({"billet_id": a["billet_id"], "date_key": date_key(a["date"]), "evenement_key": ek[a["ev"]],
                   "canal_key": ck, "categorie": a["cat"], "prix_millimes": a["prix"], "frais_millimes": a["frais"]})
    fr = [{"remboursement_id": "RB-0001", "billet_id": "S-005", "date_key": 20260310, "evenement_key": ek["EV02"],
           "canal_key": cle_version(vs, "canal_id", "canal_key", "PAR", date(2026, 3, 10)), "motif": "REPORT",
           "montant_millimes": 50000}]
    tables = {"dim_evenement": de, "dim_canal": vs, "fact_billet": fb, "fact_remboursement": fr}
    rejets = {"billets.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "remboursements.sqlite": {"cle_inconnue": 1}}
    att = calculer_attendu_echantillon(spec, tables, date(2026, 3, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(fb),
                                        "demandes_non_remboursees_ignorees": 2})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(acc, att), encoding="utf-8", newline="\n")
    return att


def md_echantillon(acc, att) -> str:
    i, ev = att["indicateurs"], att["agregats"]["par_evenement"]
    t1 = md_tableau(["Ligne du fichier", "billet_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[1]} · canal {v[2]!r} · {v[3]} · {v[4]} · places {v[5]} · prix {v[6]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 5" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    t2 = md_tableau(["billet_id", "Date ISO", "Événement", "Canal", "Prix", "Frais (‰)", "Calcul des frais", "Frais"],
                    [[a["billet_id"], a["date"].isoformat(), a["ev"], a["canal"], tnd_fr(a["prix"]), a["pm"],
                      f"{a['prix'] // 1000} × {a['pm']}", tnd_fr(a["frais"])] for a in acc])
    return f"""# Échantillon Scène Libre — le calcul à la main

12 lignes de `billets.csv`, un programme de 2 événements (capacités 10 et 8 places), les 4 canaux, 4 demandes dans `remboursements.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`billets.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 billets gardés**.

## 2. Recettes des billets et frais de distribution

Une virgule ou un point sépare les décimales : `50,0` = `50.000` = 50 000 millimes. `20` est un tarif réduit (CAT2 à 25 TND − 20 %) : on garde le prix payé. Frais = prix (TND) × frais du canal (pour mille), en millimes : WEB 45 ‰, GUI 0 ‰, REV 90 ‰, PAR 60 ‰ (`canaux.json`, mars 2026).

{t2}

**Recettes des billets = {tnd_fr(i['recettes_billets_millimes'])}** · **frais de distribution = {tnd_fr(i['frais_distribution_millimes'])}**.

## 3. Remboursements (`remboursements.sqlite`, table `remboursement`)

- `RB-0001` : billet `S-005` (EV02 reporté), statut `REMBOURSE` → **50,000 TND remboursés, 1 billet remboursé**.
- `RB-0002` : statut `CONSERVE` (le client garde son billet pour la nouvelle date) → ignoré : un report n'est pas un remboursement.
- `RB-0003` : le billet `S-099` n'existe pas → rejet `cle_inconnue` (source `remboursements.sqlite`).
- `RB-0004` : statut `REFUSE` → ignoré (ce n'est pas un rejet).

Les frais du billet `S-005` restent dus au canal PAR : ils ne sont pas remboursés.

## 4. Billets nets, taux de remplissage, recettes nettes

- Billets nets = vendus − remboursés = {i['billets_vendus']} − {i['billets_rembourses']} = **{i['billets_nets']}**.
- Taux de remplissage = billets nets / capacité = {i['billets_nets']} / 18 = **{pct_fr(i['taux_remplissage'])}** ; par événement : EV01 = {ev['EV01']['billets_nets']} / 10 = **{pct_fr(ev['EV01']['taux_remplissage'])}**, EV02 = {ev['EV02']['billets_nets']} / 8 = **{pct_fr(ev['EV02']['taux_remplissage'])}**.
- Recettes nettes = recettes − remboursements − frais = {tnd_fr(i['recettes_billets_millimes'])} − {tnd_fr(i['remboursements_millimes'])} − {tnd_fr(i['frais_distribution_millimes'])} = **{tnd_fr(i['recettes_nettes_millimes'])}**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_billet` : {att['tables']['fact_billet']} lignes · `fact_remboursement` : {att['tables']['fact_remboursement']} ligne · `dim_evenement` : {att['tables']['dim_evenement']} · `dim_canal` : {att['tables']['dim_canal']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- programme principal
def parcours_demo(attendus: dict) -> str:
    """Démonstration conseillée après le lot 2, chiffrée depuis la référence (MissionSpec.parcours_app)."""
    a = attendus["lot2"]
    ev, can, i = a["agregats"]["par_evenement"], a["agregats"]["par_canal"], a["indicateurs"]
    meilleurs = sorted((k for k in ev if ev[k]["taux_remplissage"] is not None), key=lambda k: -ev[k]["taux_remplissage"])[:3]
    return f"""Démonstration conseillée (après le lot 2) :

1. **Vue direction** — sans filtre : billets nets {i['billets_nets']}, taux de remplissage {pct_fr(i['taux_remplissage'])}, recettes nettes {tnd_fr(i['recettes_nettes_millimes'])}. Filtrer l'événement `EV05` (annulé) : {ev['EV05']['billets_nets']} billet net, recettes nettes {tnd_fr(ev['EV05']['recettes_nettes_millimes'])} (les frais restent dus). Les trois meilleurs remplissages : {", ".join(f"`{k}` {pct_fr(ev[k]['taux_remplissage'])}" for k in meilleurs)}.
2. **Détail par canal** — `REV` montre deux versions : 90 ‰ du 2025-09-01 au 2026-07-15 (exclu), puis 110 ‰ (courante) ; frais REV au total {tnd_fr(can['REV']['frais_distribution_millimes'])}. Expliquer le cas de la règle à clarifier : un billet `EV12` vendu par REV avant le 15 juillet et remboursé après garde 90 ‰.
3. **Qualité des données** — rejets lot1 = {attendus['lot1']['rejets']['total']}, lot2 = {a['rejets']['total']} (par motif et par source) ; billets déjà chargés au rejeu ; demandes `CONSERVE` / `REFUSE` ignorées (ce ne sont pas des rejets)."""


def a_savoir(_attendus: dict) -> str:
    return """
## À savoir pour M09

- La vue d'analyse ajoute **une ligne « capacité » par événement** (canal `(capacité)`) : c'est elle qui donne le dénominateur du taux de remplissage. Par canal, ce taux est vide (`null`) : la capacité d'une salle ne dépend d'aucun canal.
- L'axe `par_mois` = mois de la **date de l'événement** (date du spectacle après report), pas de la vente.
- Dans `scd2.versions` comme dans `scd2.frontieres`, `attribut` (frais en pour mille) est un entier (`90`), comme la colonne `frais_pour_mille` (INTEGER) de l'entrepôt. Le vérificateur compare l'attribut en texte des deux côtés.
- Événements annulés : `EV05` (le 2026-04-10, lot 1) et `EV12` (le 2026-07-18, lot 2) ; tous leurs billets sont remboursés. `EV08` est reporté au 2026-07-11 : seules les demandes `REMBOURSE` comptent.
"""


def main() -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES, parcours_app=parcours_demo,
                       complement_reference=a_savoir)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    billets = generer_billets(rng)
    b1 = [b for b in billets if b["date_vente"] <= LOT1.fin]
    b2 = [b for b in billets if b["date_vente"] > LOT1.fin]
    rembs = generer_remboursements(rng, billets)
    r1 = [r for r in rembs if r["_jour"] <= LOT1.fin]
    r2 = [r for r in rembs if CHEVAUCHEMENT_SQL <= r["_jour"] <= LOT2.fin]
    assert not any(r["_orphelin"] for r in r1 if r["_jour"] >= CHEVAUCHEMENT_SQL)

    c1 = construire_csv(b1, CHAMPS, DOSES["lot1"], rng, lambda k: f"B{800000 + 37 * k}")
    rejouees = [l.valeurs for l in c1.lignes if l.motif is None][-N_REJOUEES:]
    c2 = construire_csv(b2, CHAMPS, DOSES["lot2"], rng, lambda k: f"B{850000 + 41 * k}", rejouees)
    for lot, c, rr, n, du in (("lot1", c1, r1, 1, LOT1.debut), ("lot2", c2, r2, 2, CHEVAUCHEMENT_SQL)):
        d = dossier / "sources" / lot
        ecrire_csv(d / "billets.csv", ENTETE, [l.valeurs for l in c.lignes])
        ecrire_programme(d / "evenements.xlsx", n)
        ecrire_canaux(d / "canaux.json", n == 2, (LOT1.fin if n == 1 else LOT2.fin).isoformat())
        ecrire_remboursements(d / "remboursements.sqlite", rr, du, LOT1.fin if n == 1 else LOT2.fin)

    def valides(rr, deja=frozenset()):
        return [r for r in rr if r["statut"] == "REMBOURSE" and not r["_orphelin"] and r["numero"] not in deja]
    acc1 = valides(r1)
    acc2 = valides(r2, {r["numero"] for r in acc1})
    assert len({r["billet_id"] for r in acc1 + acc2}) == len(acc1 + acc2), "un billet remboursé deux fois"
    lots = []
    for lot, c, rr, acc, b_cumul, r_cumul, n in ((LOT1, c1, r1, acc1, b1, acc1, 1),
                                                  (LOT2, c2, r2, acc2, billets, acc1 + acc2, 2)):
        nb_ev = len(dim_evenements(n))
        lots.append(LotResultat(
            lot=lot,
            sources={"billets.csv": {"lignes": c.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "evenements.xlsx": {"feuilles": ["Programme", "Tarifs"], "evenements": nb_ev,
                                         "tarifs": sum(len(tarifs(e[0])) for e in EVENEMENTS if e[7] <= n),
                                         "ligne_entete_programme": 3},
                     "canaux.json": {"canaux": len(CANAUX), "versions": len(CANAUX) + (n == 2)},
                     "remboursements.sqlite": comptes_remboursements(rr)},
            nettoyage={"billets.csv": {k: v for k, v in c.compteurs.items() if k != "lignes"},
                       "remboursements.sqlite": {
                           "demandes_non_remboursees_ignorees": sum(r["statut"] != "REMBOURSE" for r in rr),
                           "deja_charges": len(valides(rr)) - len(acc), "remboursements_acceptes_nouveaux": len(acc)}},
            rejets={"billets.csv": c.rejets(), "remboursements.sqlite": {"cle_inconnue": sum(r["_orphelin"] for r in rr)}},
            tables_verite=tables_verite(b_cumul, r_cumul, n),
            increment=None if n == 1 else {
                "fact_billet_ajoutees": len(b2), "fact_remboursement_ajoutees": len(acc2), "versions_scd2_ajoutees": 1,
                "dim_evenement_ajoutees": nb_ev - len(dim_evenements(1)), "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin))}))
        assert c.compteurs["lignes_acceptees_nouvelles"] == (len(b1) if n == 1 else len(b2))

    attendus = produire_reference(spec, lots)
    # double contrôle Python pur (sans SQL) : billets nets, recettes nettes, le cas de la règle à clarifier
    t = lots[-1].tables_verite
    pm_vente = {b["billet_id"]: (CHANGEMENT[1] if b["canal"] == CHANGEMENT[0] and b["date_vente"] >= CHANGEMENT[2]
                                 else next(c[2] for c in CANAUX if c[0] == b["canal"])) for b in billets}
    fr_tot = sum(b["prix"] * pm_vente[b["billet_id"]] // 1000 for b in billets)
    ind = attendus["lot2"]["indicateurs"]
    assert ind["billets_nets"] == len(billets) - len(acc1 + acc2)
    assert ind["recettes_nettes_millimes"] == sum(b["prix"] for b in billets) - sum(
        round(r["montant_rembourse"] * 1000) for r in acc1 + acc2) - fr_tot
    cas = [r for r in acc2 if r["_billet"]["canal"] == "REV" and r["_billet"]["date_vente"] < CHANGEMENT[2] <= r["_jour"]]
    assert cas and all(f["frais_millimes"] == f["prix_millimes"] * 90 // 1000 for f in t["fact_billet"]
                       if f["billet_id"] in {r["billet_id"] for r in cas})
    assert 10 <= len(rejouees) <= 20, len(rejouees)

    ech = produire_echantillon(spec, dossier / "echantillon")
    exporter_v7_data(spec, ech, attendus)
    ent_b = ["lot", "billet_id", "evenement", "canal", "date_vente", "categorie", "prix_millimes"]
    ecrire_verite_privee(spec, {
        "billets_verite.csv": (ent_b, [{"lot": "lot1" if b["date_vente"] <= LOT1.fin else "lot2", **b,
                                        "date_vente": b["date_vente"].isoformat(), "prix_millimes": b["prix"]}
                                       for b in billets]),
        "remboursements_verite.csv": (["lot", "numero", "billet_id", "jour", "motif", "montant_millimes"],
                                      [{"lot": "lot1" if r in acc1 else "lot2", **r, "jour": r["_jour"].isoformat(),
                                        "motif": r["code_motif"], "montant_millimes": round(r["montant_rembourse"] * 1000)}
                                       for r in acc1 + acc2]),
        "evenements_verite.csv": (["lot_annonce", "evenement_id", "nom", "type_evenement", "date_evenement", "capacite"],
                                  [{"lot_annonce": f"lot{e[7]}", "evenement_id": e[0], "nom": e[1], "type_evenement": e[2],
                                    "date_evenement": e[4].isoformat(), "capacite": capacite(e[0])} for e in EVENEMENTS]),
        "canaux_verite.csv": (["canal_id", "frais_pour_mille", "valid_from", "valid_to"], versions_canaux(True)),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, c in (("lot1", c1), ("lot2", c2)) for r in c.detail_rejets()]),
    })
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : billets.csv {a['sources']['billets.csv']['lignes']} lignes · fact_billet "
              f"{a['tables']['fact_billet']} · fact_remboursement {a['tables']['fact_remboursement']} · rejets "
              f"{a['rejets']['par_motif']} · billets nets {i['billets_nets']} · remplissage {pct_fr(i['taux_remplissage'])} · "
              f"recettes nettes {tnd_fr(i['recettes_nettes_millimes'])}")
    e = ech["indicateurs"]
    print(f"  échantillon : billets nets {e['billets_nets']} · remplissage {pct_fr(e['taux_remplissage'])} · "
          f"recettes nettes {tnd_fr(e['recettes_nettes_millimes'])} · rejouées {len(rejouees)} · cas règle {len(cas)}")


TABLES = [
    table_dim_date(),
    Table("dim_evenement", "dimension", "Programme : un événement par ligne (feuille Programme).", [
        Colonne("evenement_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("evenement_id", "TEXT", "Code événement normalisé (strip + majuscules), ex. `EV07`."),
        Colonne("nom", "TEXT", "Nom du spectacle."),
        Colonne("type_evenement", "TEXT", "`Concert`, `Théâtre` ou `Festival`."),
        Colonne("lieu", "TEXT", "Nom de la salle."),
        Colonne("ville", "TEXT", "Ville de la salle."),
        Colonne("date_evenement", "TEXT", "Date actuelle du spectacle (après un éventuel report), AAAA-MM-JJ."),
        Colonne("capacite", "INTEGER", "Nombre de places mises en vente (entier)."),
    ], cle_metier="evenement_id"),
    Table("dim_canal", "dimension_scd2", "Canaux de vente avec l'historique des frais de distribution (SCD2).", [
        Colonne("canal_key", "INTEGER", "Clé technique d'une VERSION de canal.", cle=True),
        Colonne("canal_id", "TEXT", "Code canal, ex. `REV` (plusieurs versions possibles)."),
        Colonne("libelle", "TEXT", "Nom du canal, ex. `revendeur`."),
        Colonne("frais_pour_mille", "INTEGER", "Frais de distribution de cette version en pour mille (9 % → 90)."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="canal_id"),
    Table("fact_billet", "fait", "Un billet vendu accepté.", [
        Colonne("billet_id", "TEXT", "Identifiant du billet (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour de la vente.", ref="dim_date.date_key"),
        Colonne("evenement_key", "INTEGER", "Événement du billet.", ref="dim_evenement.evenement_key"),
        Colonne("canal_key", "INTEGER", "Version du canal valable à la date de vente.", ref="dim_canal.canal_key"),
        Colonne("categorie", "TEXT", "Catégorie de place normalisée : `VIP`, `CAT1`, `CAT2`."),
        Colonne("prix_millimes", "INTEGER", "Prix payé en millimes (tarif réduit possible)."),
        Colonne("frais_millimes", "INTEGER", "prix_millimes × frais_pour_mille de la version / 1 000 (arrondi au millime)."),
    ]),
    Table("fact_remboursement", "fait", "Un remboursement `REMBOURSE` de la base du service client.", [
        Colonne("remboursement_id", "TEXT", "Numéro de la demande (`numero`), clé métier unique.", cle=True),
        Colonne("billet_id", "TEXT", "Billet remboursé.", ref="fact_billet.billet_id"),
        Colonne("date_key", "INTEGER", "Jour de l'opération (heure ignorée).", ref="dim_date.date_key"),
        Colonne("evenement_key", "INTEGER", "Événement du billet.", ref="dim_evenement.evenement_key"),
        Colonne("canal_key", "INTEGER", "Version du canal du billet valable à la date du REMBOURSEMENT.",
                ref="dim_canal.canal_key"),
        Colonne("motif", "TEXT", "`ANNULATION` ou `REPORT`."),
        Colonne("montant_millimes", "INTEGER", "Montant rendu en millimes."),
    ]),
]

if __name__ == "__main__":
    main()
