"""Mission M07 — « Abonnements FibreNet » : fournisseur d'accès internet (particuliers et entreprises).

    python authoring/generateurs/mission07_fibrenet.py

Écrit modele-binome/catalogue/M07/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md, echantillon/,
sources/lot1/, sources/lot2/, reference/}, le bloc M07 de v7-data.json et la vérité privée (formateur).
"""
from __future__ import annotations

from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec, table_dim_date,
                    rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv, ecrire_excel, ecrire_json,
                    ecrire_sqlite, preparer_dossier, produire_reference, calculer_attendu_echantillon,
                    ecrire_verite_privee, exporter_v7_data, format_montant, tnd_fr, pct_fr, md_tableau, taille_dossier,
                    TAILLE_MAX_MISSION)
from textes_mission07 import SPEC_TEXTES, DERIVATION

GRAINE = 260007
CODE = "M07"
# code, nom, gamme, prix (millimes), lancée le, poids particulier, poids entreprise
OFFRES = [("FN-F20", "Fibre 20", "essentiel", 39900, "2023-01-02", 30, 0),
          ("FN-F50", "Fibre 50", "essentiel", 49900, "2023-01-02", 32, 6),
          ("FN-F100", "Fibre 100", "confort", 69900, "2023-06-01", 25, 22),
          ("FN-F300", "Fibre 300", "confort", 89900, "2024-03-01", 13, 34),
          ("FN-PRO1G", "Fibre Pro 1 Gbit/s", "pro", 149000, "2024-09-02", 0, 38)]
CHANGEMENT = ("FN-F300", "pro", 99900, date(2026, 7, 15))
VILLES = [("Tunis", 30), ("Ariana", 14), ("Sousse", 16), ("Sfax", 15), ("Nabeul", 9), ("Bizerte", 8), ("Monastir", 8)]
PRENOMS = ["Amine", "Sarra", "Yassine", "Nour", "Mehdi", "Ines", "Rayan", "Salma", "Hamza", "Lina", "Omar", "Maha",
           "Karim", "Emna", "Wassim", "Rim", "Firas", "Asma", "Bilel", "Hela", "Anis", "Dorra", "Seif", "Olfa"]
NOMS = ["Ben Amor", "Gharbi", "Jlassi", "Mansouri", "Haddad", "Ferchichi", "Bouzid", "Khelifi", "Sassi", "Chaabane",
        "Ayari", "Mejri", "Dridi", "Hamdi", "Zouari", "Belhaj", "Nasri", "Toumi", "Rekik", "Baccouche"]
PREFIXES = ["Atelier", "Cabinet", "Hôtel", "Boulangerie", "Clinique", "Agence", "Studio", "Pharmacie", "Garage",
            "Librairie", "Café", "École"]
ENSEIGNES = ["Yasmine Déco", "Les Jasmins", "Médina Conseil", "El Kram", "Carthage Sud", "Zéphyr", "Olivier Bleu",
             "Sidi Salem", "Corniche", "Les Orangers", "Bab Saâdoun", "Phénix", "Étoile du Sahel", "Riadh"]
MOTIFS = [("DEM", "Déménagement"), ("PRX", "Prix trop élevé"), ("CON", "Départ chez un concurrent"),
          ("QUA", "Qualité de service"), ("FER", "Fermeture de l'entreprise")]
CANAUX = ["agence", "site web", "téléphone", "revendeur"]
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, janvier → juin 2026")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 ; recopie les factures émises depuis le 10 juin ; base des abonnements "
           "complète (résiliations de l'été) ; FN-F300 change de gamme et de prix le 2026-07-15")
CHEVAUCHEMENT_CSV = date(2026, 6, 10)
ENTETE = ["facture_id", "abonnement_id", "compte", "offre", "mois_facture", "date_facture", "nb_mois", "montant"]
CHAMPS = ChampsCSV(ENTETE, "facture_id", "nb_mois", montants=["montant"], dates=["date_facture"],
                   codes=["compte", "offre"], cles_inconnues={"offre": ["FN-TV", "FN-F999"], "compte": ["C0999", "C1999"],
                                                              "abonnement_id": ["AB09999", "AB08888"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=5, inconnues=6, quantites=5),
         "lot2": Doses(doublons_exacts=4, conflits=1, manquants=2, inconnues=3, quantites=2)}
ORPHELINS = [("C0997", date(2026, 2, 9)), ("C0998", date(2026, 4, 2)), ("C0999", date(2026, 5, 18)),
             ("C0996", date(2026, 7, 20))]


def mois_entre(debut: date, fin: date) -> list[tuple[date, date]]:
    """(premier jour, dernier jour) de chaque mois de debut à fin."""
    out, p = [], debut.replace(day=1)
    while p <= fin:
        s = (p.replace(day=28) + timedelta(days=4)).replace(day=1)
        out.append((p, s - timedelta(days=1)))
        p = s
    return out


# --------------------------------------------------------------------------- vérité terrain
def generer_comptes(rng) -> list[dict]:
    brut = ([("particulier", date(2023, 1, 2) + timedelta(days=rng.randint(0, 1078))) for _ in range(115)]
            + [("entreprise", date(2023, 1, 2) + timedelta(days=rng.randint(0, 1078))) for _ in range(65)]
            + [(t, date(2026, 1, 2) + timedelta(days=rng.randint(0, 174))) for t in ["particulier"] * 18 + ["entreprise"] * 7]
            + [(t, date(2026, 7, 1) + timedelta(days=rng.randint(0, 55))) for t in ["particulier"] * 9 + ["entreprise"] * 3])
    brut.sort(key=lambda x: (x[1], x[0]))
    raisons = rng.sample([f"{p} {e}" for p in PREFIXES for e in ENSEIGNES], 80)
    comptes = []
    for k, (t, d) in enumerate(brut, 1):
        nom = raisons.pop() if t == "entreprise" else f"{rng.choice(PRENOMS)} {rng.choice(NOMS)}"
        comptes.append({"compte_id": f"C{k:04d}", "nom": nom, "type_compte": t, "depuis": d,
                        "ville": rng.choices([v for v, _ in VILLES], [w for _, w in VILLES])[0]})
    return comptes


def choisir_offre(rng, type_compte: str, jour: date) -> str:
    ok = [o for o in OFFRES if date.fromisoformat(o[4]) <= jour and o[5 if type_compte == "particulier" else 6] > 0]
    return rng.choices([o[0] for o in ok], [o[5 if type_compte == "particulier" else 6] for o in ok])[0]


def generer_abonnements(rng, comptes: list[dict]) -> list[dict]:
    abos = []
    for c in comptes:
        nb = (2 if rng.random() < 0.12 else 1) if c["type_compte"] == "particulier" else rng.choice([1, 2, 2, 3, 4, 5])
        for k in range(nb):
            debut = c["depuis"] + timedelta(days=rng.randint(0, 6) if k == 0 else rng.randint(20, 420))
            if debut <= LOT2.fin:
                abos.append({"compte": c["compte_id"], "type": c["type_compte"], "debut": debut, "fin": None,
                             "offre": choisir_offre(rng, c["type_compte"], debut), "statut": "VALIDE"})
    for a in abos:                                   # départs : risque mensuel à partir de juillet 2025
        p = 0.024 if a["type"] == "particulier" else 0.013
        for premier, dernier in mois_entre(max(a["debut"] + timedelta(days=30), date(2025, 7, 1)), LOT2.fin):
            if rng.random() < p:
                a["fin"] = premier + timedelta(days=rng.randint(0, (dernier - premier).days))
                break
    # cas de la règle à clarifier : résiliations le dernier jour du mois (dont le 30 juin, fin du lot 1)
    actifs = [a for a in abos if a["fin"] is None and a["debut"] < date(2026, 1, 1)]
    for a, fin in zip(rng.sample(actifs, 4), (date(2026, 3, 31), date(2026, 3, 31), date(2026, 6, 30), date(2026, 7, 31))):
        a["fin"] = fin
    entreprises = [c for c in comptes if c["type_compte"] == "entreprise" and c["depuis"] < date(2026, 1, 1)]
    for c, d in zip(rng.sample(entreprises, 2), (date(2026, 7, 14), date(2026, 7, 15))):   # FN-F300 de part et d'autre
        abos.append({"compte": c["compte_id"], "type": "entreprise", "debut": d, "fin": None, "offre": "FN-F300",
                     "statut": "VALIDE"})
    for c, d in zip(rng.sample(comptes[:150], 4), (date(2026, 2, 16), date(2026, 3, 23), date(2026, 5, 4), date(2026, 8, 10))):
        abos.append({"compte": c["compte_id"], "type": c["type_compte"], "debut": d, "fin": None,
                     "offre": choisir_offre(rng, c["type_compte"], d), "statut": "ANNULE"})
    for compte, d in ORPHELINS:
        abos.append({"compte": compte, "type": "particulier", "debut": d, "fin": None, "offre": "FN-F50", "statut": "ORPHELIN"})
    abos.sort(key=lambda a: (a["debut"], a["compte"], a["offre"]))
    for i, a in enumerate(abos, 1):
        a.update(id=i, abonnement_id=f"AB{i:05d}", canal=rng.choice(CANAUX),
                 motif=rng.choice(MOTIFS[:4] if a["type"] == "particulier" else MOTIFS[1:])[0],
                 _offre_txt=a["offre"] if rng.random() > 0.05 else rng.choice([f" {a['offre'].lower()}", a["offre"] + " "]),
                 _compte_txt=a["compte"] if rng.random() > 0.03 else f" {a['compte'].lower()}")
    return abos


def versions_offres(avec_changement: bool) -> list[dict]:
    vs = []
    for k, (code, nom, gamme, prix, depuis, _p, _e) in enumerate(OFFRES, 1):
        fin = CHANGEMENT[3].isoformat() if (avec_changement and code == CHANGEMENT[0]) else None
        vs.append({"offre_key": k, "offre_id": code, "nom": nom, "gamme": gamme, "prix_mensuel_millimes": prix,
                   "valid_from": depuis, "valid_to": fin})
    if avec_changement:
        nom = next(o[1] for o in OFFRES if o[0] == CHANGEMENT[0])
        vs.append({"offre_key": len(OFFRES) + 1, "offre_id": CHANGEMENT[0], "nom": nom, "gamme": CHANGEMENT[1],
                   "prix_mensuel_millimes": CHANGEMENT[2], "valid_from": CHANGEMENT[3].isoformat(), "valid_to": None})
    return vs


def prix_version(vs: list[dict], offre: str, jour: date) -> tuple[int, int]:
    k = cle_version(vs, "offre_id", "offre_key", offre, jour)
    return k, next(v["prix_mensuel_millimes"] for v in vs if v["offre_key"] == k)


def actif_un_jour(a: dict, p: date, d: date) -> bool:
    return a["debut"] <= d and (a["fin"] is None or a["fin"] >= p)


def factures_du_lot(abos: list[dict], lot: Lot, vs: list[dict], premier_num: int) -> list[dict]:
    """Une facture par abonnement et par mois entamé, datée du 1er du mois (ou du jour de début)."""
    out = []
    for a in abos:
        for p, d in mois_entre(lot.debut, lot.fin):
            if actif_un_jour(a, p, d):
                jour = max(a["debut"], p)
                _k, prix = prix_version(vs, a["offre"], jour)
                out.append({"abonnement_id": a["abonnement_id"], "compte": a["compte"], "offre": a["offre"],
                            "mois_facture": f"{p:%Y-%m}", "date_facture": jour, "nb_mois": 1, "montant": prix})
    out.sort(key=lambda f: (f["date_facture"], f["abonnement_id"]))
    for i, f in enumerate(out, premier_num):
        f["facture_id"] = f"F26-{i:06d}"
    return out


def lignes_abonnement_mois(abos, mois, vs, ck) -> list[dict]:
    out = []
    for a in abos:
        for p, d in mois:
            if not actif_un_jour(a, p, d):
                continue
            k, prix = prix_version(vs, a["offre"], d)
            fin = a["fin"]
            out.append({"abonnement_mois_id": f"{a['abonnement_id']}-{p:%Y-%m}", "abonnement_id": a["abonnement_id"],
                        "date_key": date_key(d), "compte_key": ck[a["compte"]], "offre_key": k,
                        "actif_debut": int(a["debut"] < p and (fin is None or fin >= p)),
                        "nouveau": int(p <= a["debut"] <= d), "depart": int(fin is not None and p <= fin <= d),
                        "actif_fin": int(a["debut"] <= d and (fin is None or fin > d)), "mensualite_millimes": prix})
    return out


def tables_verite(comptes, abos, factures, mois, avec_changement: bool) -> dict[str, list[dict]]:
    vs = versions_offres(avec_changement)
    ck = {c["compte_id"]: k for k, c in enumerate(comptes, 1)}
    dc = [{"compte_key": k, "compte_id": c["compte_id"], "nom": c["nom"], "type_compte": c["type_compte"],
           "ville": c["ville"]} for k, c in enumerate(comptes, 1)]
    ff = [{"facture_id": f["facture_id"], "date_key": date_key(f["date_facture"]), "compte_key": ck[f["compte"]],
           "offre_key": prix_version(vs, f["offre"], f["date_facture"])[0], "abonnement_id": f["abonnement_id"],
           "mois_facture": f["mois_facture"], "nb_mois": f["nb_mois"], "montant_millimes": f["montant"]} for f in factures]
    return {"dim_compte": dc, "dim_offre": vs, "fact_facture": ff,
            "fact_abonnement_mois": lignes_abonnement_mois(abos, mois, vs, ck)}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_comptes(chemin, comptes: list[dict], extrait_le: str) -> None:
    lignes = []
    for c in comptes:
        n = int(c["compte_id"][1:])
        code = f" {c['compte_id'].lower()}" if n % 41 == 17 else c["compte_id"]
        t = c["type_compte"]
        t = f" {t.capitalize()} " if n % 7 == 3 else (t.upper() if n % 11 == 5 else t)
        lignes.append([code, c["nom"], t, c["ville"], c["depuis"].isoformat()])
    ecrire_excel(chemin, [Feuille("Comptes", ["N° compte", "Nom / raison sociale", "Type de compte", "Ville", "Client depuis"],
                                  lignes, titres=[f"FibreNet — comptes clients (extraction du {extrait_le})"])])


def ecrire_offres(chemin, avec_changement: bool, extrait_le: str) -> None:
    offres = []
    for i, (code, nom, gamme, prix, depuis, _p, _e) in enumerate(OFFRES):
        hist = [{"gamme": gamme.capitalize() if i % 2 else gamme, "valide_depuis": depuis,
                 "prix_mensuel": format_montant(prix, "virgule3") if i % 2 == 0 else prix / 1000}]
        if avec_changement and code == CHANGEMENT[0]:
            hist.append({"gamme": CHANGEMENT[1].capitalize(), "valide_depuis": CHANGEMENT[3].isoformat(),
                         "prix_mensuel": format_montant(CHANGEMENT[2], "virgule3")})
        offres.append({"code": code, "nom": nom, "historique": hist})
    ecrire_json(chemin, {"source": "Catalogue des offres FibreNet", "extrait_le": extrait_le, "devise": "TND",
                         "offres": offres})


DDL_ABONNEMENTS = """
CREATE TABLE motif_resiliation (code_motif TEXT PRIMARY KEY, libelle TEXT NOT NULL);
CREATE TABLE abonnement (
  id INTEGER PRIMARY KEY,
  abonnement_id TEXT NOT NULL UNIQUE,
  num_compte TEXT NOT NULL,
  code_offre TEXT NOT NULL,
  date_debut TEXT NOT NULL,
  date_fin TEXT,
  statut TEXT NOT NULL CHECK (statut IN ('ACTIF', 'RESILIE', 'ANNULE')),
  code_motif TEXT REFERENCES motif_resiliation(code_motif),
  canal TEXT
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""


def instantane(abos: list[dict], au: date) -> list[dict]:
    """Ce que la base opérationnelle montre le jour de l'export (`au`)."""
    out = []
    for a in abos:
        if a["debut"] > au:
            continue
        fin = a["fin"] if a["fin"] is not None and a["fin"] <= au else None
        statut = "ANNULE" if a["statut"] == "ANNULE" else ("RESILIE" if fin else "ACTIF")
        out.append({"id": a["id"], "abonnement_id": a["abonnement_id"], "num_compte": a["_compte_txt"],
                    "code_offre": a["_offre_txt"], "date_debut": a["debut"].isoformat(),
                    "date_fin": fin.isoformat() if fin else None, "statut": statut,
                    "code_motif": a["motif"] if statut == "RESILIE" else None, "canal": a["canal"]})
    return out


def ecrire_abonnements(chemin, lignes: list[dict], au: date) -> None:
    ecrire_sqlite(chemin, DDL_ABONNEMENTS, {
        "motif_resiliation": [{"code_motif": c, "libelle": l} for c, l in MOTIFS], "abonnement": lignes,
        "parametre": [{"cle": "export_genere_le", "valeur": (au + timedelta(days=1)).isoformat()},
                      {"cle": "perimetre", "valeur": f"tous les abonnements connus au {au.isoformat()}"},
                      {"cle": "convention_date_fin", "valeur": "date_fin = dernier jour de service (inclus)"}]})


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
COMPTES_ECH = [("C0001", "Amine Gharbi", "particulier", "Tunis"), ("C0002", "Sarra Jlassi", "particulier", "Sousse"),
               ("C0003", "Atelier Yasmine Déco", "entreprise", "Sfax"), ("C0004", "Hôtel Les Jasmins", "entreprise", "Nabeul"),
               ("C0005", "Mehdi Bouzid", "particulier", "Ariana")]
ABOS_ECH = [  # id, abonnement_id, compte, offre, début, fin, statut, motif
    (1, "AB-E01", "C0001", "FN-F20", "2025-06-10", None, "ACTIF", None),
    (2, "AB-E02", "C0002", "FN-F100", "2025-09-01", "2026-03-31", "RESILIE", "DEM"),
    (3, "AB-E03", "C0003", "FN-F300", "2026-03-10", None, "ACTIF", None),
    (4, "AB-E04", "C0004", "FN-PRO1G", "2024-11-04", "2026-03-15", "RESILIE", "FER"),
    (5, "AB-E05", "C0005", "FN-F50", "2025-12-01", None, "ACTIF", None),
    (6, "AB-E06", "C0003", "FN-F300", "2025-02-03", None, "ACTIF", None),
    (7, "AB-E07", "C0002", "FN-F50", "2026-03-20", None, "ANNULE", None),
    (8, "AB-E08", "C0999", "FN-F20", "2026-03-05", None, "ACTIF", None)]
ECHANTILLON = [  # valeurs texte, décision
    (["F-E001", "AB-E01", "C0001", "FN-F20", "2026-03", "2026-03-01", "1", "39.900"], None),
    (["F-E002", "AB-E02", "c0002", "fn-f100", "2026-03", "01/03/2026", "1", "69,900"], None),
    (["F-E003", "AB-E03", "C0003", "FN-F300", "2026-03", "10 mars 2026", "1", "89.9"], None),
    (["F-E004", "AB-E04", "C0004", "FN-PRO1G", "2026-03", "2026-03-01", "1", "149,000"], None),
    (["F-E004", "AB-E04", "C0004", "FN-PRO1G", "2026-03", "2026-03-01", "1", "149,000"], "doublon_exact"),
    (["F-E005", "AB-E05", " C0005 ", "FN-F50", "2026-03", "2026-03-01", "1", "49,9"], None),
    (["F-E006", "AB-E06", "C0003", "FN-F300", "2026-03", "2026-03-01", "1", "89,900"], None),
    (["F-E007", "AB-E01", "C0001", "FN-F20", "2026-03", "2026-03-01", "1", "39.900"], "id_conflit"),
    (["F-E007", "AB-E01", "C0001", "FN-F20", "2026-03", "2026-03-01", "2", "79.800"], "id_conflit"),
    (["", "AB-E05", "C0005", "FN-F50", "2026-03", "2026-03-01", "1", "49.900"], "id_manquant"),
    (["F-E008", "AB-E08", "C0999", "FN-F20", "2026-03", "2026-03-05", "1", "39.900"], "cle_inconnue"),
    (["F-E009", "AB-E06", "C0003", "FN-F300", "2026-03", "2026-03-01", "0", "89.900"], "quantite_invalide"),
]


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "facturation.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON])
    comptes = [{"compte_id": c, "nom": n, "type_compte": t, "ville": v, "depuis": date(2024, 1, 15)} for c, n, t, v in COMPTES_ECH]
    ecrire_comptes(dossier / "comptes.xlsx", comptes, "2026-03-31")
    ecrire_offres(dossier / "offres.json", False, "2026-03-31")
    cles = ("id", "abonnement_id", "num_compte", "code_offre", "date_debut", "date_fin", "statut", "code_motif")
    ecrire_abonnements(dossier / "abonnements.sqlite", [dict(zip(cles, a), canal="agence") for a in ABOS_ECH], date(2026, 3, 31))
    abos = [{"abonnement_id": a[1], "compte": a[2], "offre": a[3], "debut": date.fromisoformat(a[4]),
             "fin": date.fromisoformat(a[5]) if a[5] else None} for a in ABOS_ECH if a[6] != "ANNULE" and a[2] != "C0999"]
    mars = Lot("echantillon", "initial", date(2026, 3, 1), date(2026, 3, 31), "")
    facts = {f["abonnement_id"]: f for f in factures_du_lot(abos, mars, versions_offres(False), 1)}
    for v, motif in ECHANTILLON:                       # les factures gardées gardent leur numéro d'échantillon
        if motif is None:
            facts[v[1]]["facture_id"] = v[0]
    tables = tables_verite(comptes, abos, list(facts.values()), mois_entre(mars.debut, mars.fin), False)
    rejets = {"facturation.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "abonnements.sqlite": {"cle_inconnue": 1}}
    att = calculer_attendu_echantillon(spec, tables, mars.debut, mars.fin, rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(facts),
                                        "abonnements_annules_exclus": 1})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(tables, att), encoding="utf-8")
    return att


def md_echantillon(tables, att) -> str:
    i = att["indicateurs"]
    t1 = md_tableau(["Ligne du fichier", "facture_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[1]} · {v[2]!r} · {v[3]} · {v[5]} · nb_mois {v[6]} · {v[7]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 5" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    prix = {o[0]: o[3] for o in OFFRES}
    lignes = []
    for a in ABOS_ECH:
        r = next((x for x in tables["fact_abonnement_mois"] if x["abonnement_id"] == a[1]), None)
        etat = ("ignoré : `ANNULE`" if a[6] == "ANNULE" else "rejet `cle_inconnue` (compte C0999 inconnu)") if r is None else \
            f"{r['actif_debut']} · {r['nouveau']} · {r['depart']} · {r['actif_fin']}"
        mrr = tnd_fr(prix[a[3]]) if r and r["actif_fin"] else "0"
        lignes.append([a[1], a[3], a[4], a[5] or "(vide)", etat, mrr])
    t2 = md_tableau(["Abonnement", "Offre", "date_debut", "date_fin", "actif_debut · nouveau · départ · actif_fin",
                     "MRR de mars"], lignes)
    return f"""# Échantillon FibreNet — le calcul à la main (mars 2026)

12 lignes de `facturation.csv`, 5 comptes, les 5 offres, 8 abonnements dans `abonnements.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`facturation.csv`)

La ligne 1 du fichier est l'en-tête.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 factures gardées**.

## 2. Montant facturé en mars

`89.9` = `89,900` = 89 900 millimes ; `49,9` = 49 900 millimes. Somme des 6 factures : 39,900 + 69,900 + 89,900 + 149,000 + 49,900 + 89,900 = **{tnd_fr(i['facture_millimes'])}**.

## 3. Les abonnements du mois : la ligne dérivée de `fact_abonnement_mois`

Règle : actif début de mois = actif le 28 février ; nouveau = début en mars ; départ = fin en mars ; actif fin de mois = début ≤ 31 mars **et** (fin vide **ou** fin **après** le 31 mars). `AB-E02` finit le 31 mars : c'est un départ de mars et il n'est **pas** actif fin mars (règle à clarifier, décision B).

{t2}

## 4. Les indicateurs de mars

- Actifs début de mois = **{i['actifs_debut_mois']}** ; nouveaux = **{i['nouveaux']}** ; départs = **{i['departs']}**.
- Abonnés actifs fin de mois = {i['actifs_debut_mois']} + {i['nouveaux']} − {i['departs']} = **{i['actifs_fin_mois']}**.
- MRR = 39,900 + 89,900 + 49,900 + 89,900 = **{tnd_fr(i['mrr_millimes'])}** (les deux départs ne comptent pas).
- Taux de départ = départs / actifs début = {i['departs']} / {i['actifs_debut_mois']} = **{pct_fr(i['taux_depart'])}**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_facture` : {att['tables']['fact_facture']} lignes · `fact_abonnement_mois` : {att['tables']['fact_abonnement_mois']} lignes · `dim_compte` : {att['tables']['dim_compte']} · `dim_offre` : {att['tables']['dim_offre']} · `dim_date` : {att['tables']['dim_date']} jours (mars 2026). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- compléments de documents
def table_mois(spec, a: dict) -> str:
    return md_tableau(["Mois", "Actifs début", "Nouveaux", "Départs", "Actifs fin", "Taux de départ", "MRR", "Facturé"],
                      [[m, x["actifs_debut_mois"], x["nouveaux"], x["departs"], x["actifs_fin_mois"],
                        pct_fr(x["taux_depart"]) if x["taux_depart"] is not None else "—", tnd_fr(x["mrr_millimes"]),
                        tnd_fr(x["facture_millimes"])] for m, x in a["agregats"]["par_mois"].items()])


def section_derivation() -> str:
    deriv = md_tableau(["Colonne", "Règle de calcul (mois M)"], [list(r) for r in DERIVATION])
    return f"""Ce fait ne vient pas du CSV : il est **calculé** depuis les dates de `abonnements.sqlite` (abonnements acceptés). Une ligne = un abonnement × un mois où il est actif **au moins un jour** (`date_debut` ≤ dernier jour du mois ET (`date_fin` vide OU `date_fin` ≥ 1er jour du mois)), de janvier 2026 au dernier mois du lot chargé. `abonnement_mois_id` = `<abonnement_id>-<AAAA-MM>` (ex. `AB00137-2026-03`) ; `date_key` = dernier jour du mois (ex. `20260331`) ; `offre_key` = version de l'offre valable ce dernier jour.

{deriv}

Un abonnement résilié avant 2026 n'a aucune ligne. Relancer un lot recalcule les mêmes lignes : celles dont la clé existe sont ignorées, le passé ne change pas."""


def lecture_mois_par_mois(attendus: dict) -> str:
    return ("\n## Lecture mois par mois (après le dernier lot)\n\nLes abonnés et le MRR sont des stocks de fin de "
            "mois. Les totaux « Indicateurs » ci-dessus additionnent les mois (abonnés-mois, MRR cumulé) : pour "
            "un mois, lisez ce tableau (agrégat `par_mois`).\n\n" + table_mois(None, attendus["lot2"]) + "\n")


# --------------------------------------------------------------------------- programme principal
def main() -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES,
                       sections_cahier=[("Dérivation de `fact_abonnement_mois` (le cœur de la mission)",
                                         section_derivation())],
                       complement_reference=lecture_mois_par_mois)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    comptes = generer_comptes(rng)
    abos = generer_abonnements(rng, comptes)
    valides = [a for a in abos if a["statut"] == "VALIDE"]
    vs1, vs2 = versions_offres(False), versions_offres(True)
    f1 = factures_du_lot([a for a in valides if a["debut"] <= LOT1.fin], LOT1, vs1, 1)
    f2 = factures_du_lot(valides, LOT2, vs2, len(f1) + 1)
    b1 = construire_csv(f1, CHAMPS, DOSES["lot1"], rng, lambda k: f"F26-9{k:05d}")
    date_f = {f["facture_id"]: f["date_facture"] for f in f1}
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None and date_f[l.origine] >= CHEVAUCHEMENT_CSV]
    b2 = construire_csv(f2, CHAMPS, DOSES["lot2"], rng, lambda k: f"F26-8{k:05d}", rejouees)
    lots = []
    for lot, b, avec, facts in ((LOT1, b1, False, f1), (LOT2, b2, True, f1 + f2)):
        d = dossier / "sources" / lot.nom
        cpt = [c for c in comptes if c["depuis"] <= lot.fin]
        inst = instantane(abos, lot.fin)
        ecrire_csv(d / "facturation.csv", ENTETE, [l.valeurs for l in b.lignes])
        ecrire_comptes(d / "comptes.xlsx", cpt, lot.fin.isoformat())
        ecrire_offres(d / "offres.json", avec, lot.fin.isoformat())
        ecrire_abonnements(d / "abonnements.sqlite", inst, lot.fin)
        val = [a for a in valides if a["debut"] <= lot.fin]
        t = tables_verite(cpt, [dict(a, fin=a["fin"] if a["fin"] and a["fin"] <= lot.fin else None) for a in val],
                          facts, mois_entre(LOT1.debut, lot.fin), avec)
        n_orph = sum(a["statut"] == "ORPHELIN" for a in abos if a["debut"] <= lot.fin)
        nb_mois_lot = sum(1 for r in t["fact_abonnement_mois"] if r["date_key"] >= date_key(lot.debut))
        lots.append(LotResultat(
            lot=lot,
            sources={"facturation.csv": {"lignes": b.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "comptes.xlsx": {"feuilles": ["Comptes"], "comptes": len(cpt), "ligne_entete": 3},
                     "offres.json": {"offres": len(OFFRES), "versions": len(OFFRES) + int(avec)},
                     "abonnements.sqlite": {"abonnement": len(inst), **{s.lower(): sum(r["statut"] == s for r in inst)
                                                                        for s in ("ACTIF", "RESILIE", "ANNULE")},
                                            "motif_resiliation": len(MOTIFS)}},
            nettoyage={"facturation.csv": {k: v for k, v in b.compteurs.items() if k != "lignes"},
                       "abonnements.sqlite": {"annules_ignores": sum(r["statut"] == "ANNULE" for r in inst),
                                              "abonnements_acceptes": len(val),
                                              "resilies_avant_2026_sans_ligne": sum(1 for a in val if a["fin"] and a["fin"] < LOT1.debut),
                                              "lignes_mois_nouvelles": nb_mois_lot}},
            rejets={"facturation.csv": b.rejets(), "abonnements.sqlite": {"cle_inconnue": n_orph}},
            tables_verite=t,
            increment=None if lot is LOT1 else {
                "fact_facture_ajoutees": len(f2), "fact_abonnement_mois_ajoutees": nb_mois_lot,
                "versions_scd2_ajoutees": 1, "dim_compte_ajoutees": len(cpt) - len(lots[0].tables_verite["dim_compte"]),
                "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin))}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(facts) - (0 if lot is LOT1 else len(f1))
        assert len(t["fact_facture"]) == len(t["fact_abonnement_mois"])   # une facture par abonnement-mois

    attendus = produire_reference(spec, lots)
    # double contrôle Python pur (sans SQL) : fin août, depuis les seules dates des abonnements
    fin = LOT2.fin
    actifs = [a for a in valides if a["debut"] <= fin and (a["fin"] is None or a["fin"] > fin)]
    mrr = sum(prix_version(vs2, a["offre"], fin)[1] for a in actifs)
    aout = attendus["lot2"]["agregats"]["par_mois"]["2026-08"]
    assert (aout["actifs_fin_mois"], aout["mrr_millimes"]) == (len(actifs), mrr)
    assert aout["departs"] == sum(1 for a in valides if a["fin"] and date(2026, 8, 1) <= a["fin"] <= fin)
    for m, x in attendus["lot2"]["agregats"]["par_mois"].items():
        assert x["actifs_fin_mois"] == x["actifs_debut_mois"] + x["nouveaux"] - x["departs"], m
    ech = produire_echantillon(spec, dossier / "echantillon")

    ids1 = {f["facture_id"] for f in f1}
    ent_a = ["abonnement_id", "compte", "offre", "date_debut", "date_fin", "statut"]
    ecrire_verite_privee(spec, {
        "abonnements_verite.csv": (ent_a, [{"abonnement_id": a["abonnement_id"], "compte": a["compte"], "offre": a["offre"],
                                            "date_debut": a["debut"].isoformat(),
                                            "date_fin": a["fin"].isoformat() if a["fin"] else "", "statut": a["statut"]}
                                           for a in abos]),
        "factures_verite.csv": (["lot"] + ENTETE[:-1] + ["montant_millimes"],
                                [{"lot": "lot1" if f["facture_id"] in ids1 else "lot2", **f, "date_facture": f["date_facture"].isoformat(),
                                  "montant_millimes": f["montant"]} for f in f1 + f2]),
        "offres_verite.csv": (["offre_id", "nom", "gamme", "prix_mensuel_millimes", "valid_from", "valid_to"], vs2),
        "comptes_verite.csv": (["compte_id", "nom", "type_compte", "ville", "depuis"],
                               [dict(c, depuis=c["depuis"].isoformat()) for c in comptes]),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    exporter_v7_data(spec, ech, attendus)
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        dern = list(a["agregats"]["par_mois"].items())[-1]
        print(f"  {a['lot']} : facturation.csv {a['sources']['facturation.csv']['lignes']} lignes · tables {a['tables']} · "
              f"rejets {a['rejets']['par_motif']} · fin {dern[0]} : actifs {dern[1]['actifs_fin_mois']} · "
              f"MRR {tnd_fr(dern[1]['mrr_millimes'])} · départs période {a['indicateurs']['departs']} · "
              f"taux période {pct_fr(a['indicateurs']['taux_depart'])}")
    e = ech["indicateurs"]
    print(f"  échantillon : actifs fin {e['actifs_fin_mois']} · MRR {tnd_fr(e['mrr_millimes'])} · départs {e['departs']} · "
          f"taux {pct_fr(e['taux_depart'])} · facturé {tnd_fr(e['facture_millimes'])}")


TABLES = [
    table_dim_date(),
    Table("dim_compte", "dimension", "Comptes clients (feuille Comptes de `comptes.xlsx`).", [
        Colonne("compte_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("compte_id", "TEXT", "Numéro de compte normalisé (strip + majuscules), ex. `C0042`."),
        Colonne("nom", "TEXT", "Nom ou raison sociale (inventé)."),
        Colonne("type_compte", "TEXT", "`particulier` ou `entreprise` (strip + minuscules)."),
        Colonne("ville", "TEXT", "Ville du compte."),
    ], cle_metier="compte_id"),
    Table("dim_offre", "dimension_scd2", "Offres avec l'historique de la gamme et du prix mensuel (SCD2).", [
        Colonne("offre_key", "INTEGER", "Clé technique d'une VERSION d'offre.", cle=True),
        Colonne("offre_id", "TEXT", "Code de l'offre, ex. `FN-F300` (plusieurs versions possibles)."),
        Colonne("nom", "TEXT", "Nom commercial."),
        Colonne("gamme", "TEXT", "`essentiel`, `confort` ou `pro` pour cette version (minuscules)."),
        Colonne("prix_mensuel_millimes", "INTEGER", "Prix mensuel de cette version en millimes."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="offre_id"),
    Table("fact_facture", "fait", "Une facture mensuelle acceptée de `facturation.csv`.", [
        Colonne("facture_id", "TEXT", "Numéro de facture (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour de la facture.", ref="dim_date.date_key"),
        Colonne("compte_key", "INTEGER", "Compte facturé.", ref="dim_compte.compte_key"),
        Colonne("offre_key", "INTEGER", "Version de l'offre valable à la date de la facture.", ref="dim_offre.offre_key"),
        Colonne("abonnement_id", "TEXT", "Abonnement facturé (clé métier de la base opérationnelle)."),
        Colonne("mois_facture", "TEXT", "Mois facturé, AAAA-MM."),
        Colonne("nb_mois", "INTEGER", "Mensualités facturées (entier > 0)."),
        Colonne("montant_millimes", "INTEGER", "Montant facturé en millimes."),
    ]),
    Table("fact_abonnement_mois", "fait", "Un abonnement × un mois où il est actif au moins un jour (fait DÉRIVÉ des "
          "dates de début et de fin, voir § 13).", [
        Colonne("abonnement_mois_id", "TEXT", "`<abonnement_id>-<AAAA-MM>` (clé métier unique).", cle=True),
        Colonne("abonnement_id", "TEXT", "Abonnement (clé métier de la base opérationnelle)."),
        Colonne("date_key", "INTEGER", "DERNIER jour du mois (ex. 20260331).", ref="dim_date.date_key"),
        Colonne("compte_key", "INTEGER", "Compte titulaire.", ref="dim_compte.compte_key"),
        Colonne("offre_key", "INTEGER", "Version de l'offre valable le dernier jour du mois.", ref="dim_offre.offre_key"),
        Colonne("actif_debut", "INTEGER", "1 si actif le dernier jour du mois précédent, sinon 0."),
        Colonne("nouveau", "INTEGER", "1 si `date_debut` tombe dans le mois, sinon 0."),
        Colonne("depart", "INTEGER", "1 si `date_fin` tombe dans le mois, sinon 0."),
        Colonne("actif_fin", "INTEGER", "1 si actif le dernier jour du mois (`date_fin` vide ou après), sinon 0."),
        Colonne("mensualite_millimes", "INTEGER", "Prix mensuel de la version `offre_key`, en millimes."),
    ]),
]

if __name__ == "__main__":
    main()
