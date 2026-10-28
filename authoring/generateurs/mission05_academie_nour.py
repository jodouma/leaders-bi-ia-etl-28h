"""Mission M05 — Centre de formation : Académie Nour (sessions de formation courte, Tunis / Sousse / Sfax).

    python authoring/generateurs/mission05_academie_nour.py            # depuis github/

Écrit modele-binome/catalogue/M05/{fiche_mission.md, cahier_des_charges.md, dictionnaire.md,
echantillon/, sources/lot1/, sources/lot2/, reference/}, le bloc M05 de v7-data.json et la vérité privée du formateur.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from datetime import date, timedelta

from common import (ChampsCSV, Doses, Feuille, Lot, LotResultat, Table, Colonne, MissionSpec, table_dim_date,
                    rng_mission, jours, date_key, cle_version, construire_csv, ecrire_csv, ecrire_excel, ecrire_json,
                    ecrire_sqlite, preparer_dossier, produire_reference, calculer_attendu_echantillon,
                    exporter_v7_data, ecrire_verite_privee, format_montant, entrepot_verite, tnd_fr, pct_fr,
                    md_tableau, taille_dossier, TAILLE_MAX_MISSION)
from textes_mission05 import SPEC_TEXTES

GRAINE = 260005
CODE = "M05"
# code, intitulé, domaine, prix (millimes), capacité, nombre de séances
FORMATIONS = [("F01", "Excel avancé", "Bureautique", 280000, 16, 6),
              ("F02", "Power BI pour débutants", "Données", 450000, 14, 8),
              ("F03", "Comptabilité pratique", "Gestion", 380000, 18, 10),
              ("F04", "Anglais professionnel", "Langues", 360000, 15, 12),
              ("F05", "Gestion de projet agile", "Management", 520000, 12, 6),
              ("F06", "Marketing digital", "Commercial", 320000, 20, 5),
              ("F07", "Python pour l'analyse de données", "Données", 590000, 12, 10)]
FORM = {f[0]: f for f in FORMATIONS}
FORMATEURS = {"F01": "M. Hatem Ferchichi", "F02": "Mme Rim Zouari", "F03": "M. Anis Kammoun", "F04": "Mme Olfa Chebbi",
              "F05": "M. Slim Boughanmi", "F06": "Mme Nadia Ayari", "F07": "M. Fares Mejri"}
RYTHMES = {(0, 2): "lundi et mercredi, 18 h – 21 h", (1, 3): "mardi et jeudi, 18 h – 21 h",
           (5,): "samedi, 9 h – 13 h", (1,): "mardi, 18 h – 21 h (à distance)"}
# session, formation, centre, 1re séance, jours, remplissage, assiduité, part d'impayés, absents total, abandons, annulées
SESSIONS = [
    ("SES-2601", "F01", "Tunis", date(2026, 1, 19), (0, 2), .94, .90, .05, 0, 0, 1),
    ("SES-2602", "F03", "Sousse", date(2026, 1, 20), (1, 3), .83, .88, .05, 1, 0, 0),
    ("SES-2603", "F06", "Sfax", date(2026, 1, 24), (5,), .45, .84, .05, 0, 0, 1),
    ("SES-2604", "F02", "Tunis", date(2026, 2, 3), (1, 3), .93, .91, .05, 0, 1, 0),
    ("SES-2605", "F07", "Tunis", date(2026, 2, 9), (0, 2), .92, .87, .05, 0, 0, 1),
    ("SES-2606", "F01", "Sousse", date(2026, 2, 16), (0, 2), .75, .86, .05, 0, 0, 0),
    ("SES-2607", "F04", "Tunis", date(2026, 2, 21), (5,), .87, .83, .05, 1, 1, 0),
    ("SES-2608", "F05", "Sfax", date(2026, 3, 2), (0, 2), .75, .89, .05, 0, 0, 0),
    ("SES-2609", "F02", "Sousse", date(2026, 3, 3), (1, 3), .86, .68, .05, 1, 1, 0),
    ("SES-2610", "F06", "Tunis", date(2026, 3, 7), (5,), .90, .86, .05, 0, 0, 1),
    ("SES-2611", "F03", "Tunis", date(2026, 3, 16), (0, 2), .89, .90, .05, 1, 0, 0),
    ("SES-2612", "F01", "Sfax", date(2026, 3, 24), (1, 3), .56, .87, .05, 0, 0, 0),
    ("SES-2613", "F07", "Sousse", date(2026, 4, 6), (0, 2), .83, .85, .05, 0, 1, 0),
    ("SES-2614", "F05", "Tunis", date(2026, 4, 7), (1, 3), 1.0, .92, .05, 0, 0, 1),
    ("SES-2615", "F02", "Sfax", date(2026, 4, 13), (0, 2), .79, .86, .45, 0, 0, 0),
    ("SES-2616", "F06", "Sousse", date(2026, 4, 18), (5,), .80, .82, .05, 1, 0, 0),
    ("SES-2617", "F01", "Tunis", date(2026, 5, 4), (0, 2), .88, .89, .05, 0, 0, 1),
    ("SES-2618", "F03", "Sfax", date(2026, 5, 5), (1, 3), .67, .84, .05, 0, 1, 0),
    ("SES-2619", "F04", "Sousse", date(2026, 5, 26), (1,), .87, .88, .05, 0, 0, 0),
    ("SES-2620", "F07", "Tunis", date(2026, 5, 25), (0, 2), 1.0, .90, .05, 0, 0, 0),
    ("SES-2621", "F06", "Tunis", date(2026, 7, 4), (5,), .80, .83, .05, 0, 0, 1),
    ("SES-2622", "F01", "Sousse", date(2026, 7, 6), (0, 2), .81, .88, .05, 1, 0, 0),
    ("SES-2623", "F02", "Sfax", date(2026, 7, 7), (1, 3), .71, .78, .05, 0, 1, 0),
    ("SES-2624", "F05", "Tunis", date(2026, 7, 20), (0, 2), .92, .90, .25, 0, 0, 0),
    ("SES-2625", "F01", "Sfax", date(2026, 8, 3), (0, 2), .50, .86, .05, 0, 0, 1),
]
CHANGEMENT = ("SES-2619", "Sfax", date(2026, 7, 15))
LOT1 = Lot("lot1", "initial", date(2026, 1, 1), date(2026, 6, 30), "chargement initial, janvier → juin 2026 (20 sessions)")
LOT2 = Lot("lot2", "increment", date(2026, 7, 1), date(2026, 8, 31),
           "incrément juillet → août 2026 (5 nouvelles sessions + la fin de SES-2619) ; recopie la séance du 30 juin "
           "et les mouvements depuis le 1er juin ; SES-2619 passe à Sfax le 2026-07-15")
CHEVAUCHEMENT_CSV = date(2026, 6, 30)     # le lot 2 recopie les présences de ce jour
CHEVAUCHEMENT_SQL = date(2026, 6, 1)      # la base du lot 2 recopie les mouvements depuis ce jour
ENTETE = ["presence_id", "session", "participant", "date_seance", "present"]
CHAMPS = ChampsCSV(ENTETE, "presence_id", "present", dates=["date_seance"], codes=["session", "participant"],
                   cles_inconnues={"session": ["SES-2699", "SES-2588", "SES-2630"], "participant": ["PA-9001", "PA-9002"]})
DOSES = {"lot1": Doses(doublons_exacts=12, conflits=3, manquants=5, inconnues=6, quantites=6, part_codes=0.12),
         "lot2": Doses(doublons_exacts=4, conflits=1, manquants=2, inconnues=3, quantites=2, part_codes=0.12)}
PRESENTS_INVALIDES = ["2", "-1", "oui", "1,5", "x", "3", "0.5", "10"]   # « 0 » est valide ici : liste propre
MODES = ["espèces", "carte bancaire", "carte bancaire", "virement", "chèque", "paiement mobile"]
PRENOMS = ["Amel", "Yassine", "Sonia", "Mehdi", "Rania", "Karim", "Ines", "Oussama", "Meriem", "Bilel", "Salma", "Aymen",
           "Hela", "Nizar", "Asma", "Wassim", "Nour", "Skander", "Dorra", "Firas", "Emna", "Ghassen", "Lina", "Hamza",
           "Syrine", "Malek", "Yosra", "Rami", "Chaima", "Tarek"]
NOMS = ["Ben Amor", "Trabelsi", "Jaziri", "Mansouri", "Gharbi", "Haddad", "Bouaziz", "Saidi", "Karoui", "Mejri",
        "Hamdi", "Chaabane", "Ayadi", "Ferjani", "Belhadj", "Sassi", "Zribi", "Dridi", "Khelifi", "Nasri", "Rekik",
        "Jlassi", "Masmoudi", "Toumi", "Abidi", "Ouni", "Baccar", "Hlel"]
VILLES = ["Tunis", "Ariana", "Ben Arous", "La Marsa", "Sousse", "Monastir", "Sfax", "Nabeul", "Mahdia"]


def sl(sid: str) -> str:
    """Lot de la session (la date de première séance décide)."""
    return "lot1" if next(s for s in SESSIONS if s[0] == sid)[3] <= LOT1.fin else "lot2"


def seances(debut: date, jours_sem: tuple, n: int) -> list[date]:
    assert debut.weekday() in jours_sem, debut
    out, d = [], debut
    while len(out) < n:
        if d.weekday() in jours_sem:
            out.append(d)
        d += timedelta(days=1)
    return out


def ouverture(debut: date) -> date:
    return max(date(2026, 1, 2), debut - timedelta(days=35))


def heure(rng) -> str:
    return f"{rng.randint(8, 18):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}"


# --------------------------------------------------------------------------- vérité terrain
def generer(rng):
    """Inscriptions, feuille d'émargement complète et mouvements d'argent (paiements + remboursements)."""
    pool = [f"PA-{i:04d}" for i in range(1, 401)]
    participants = {p: (rng.choice(PRENOMS), rng.choice(NOMS), rng.choice(VILLES)) for p in pool}
    presences, inscriptions, mouvements = [], [], []
    for sid, fid, centre, debut, js, fill, assid, impayes, n_abs, n_ab, n_ann in SESSIONS:
        _, _, _, prix, cap, n_seances = FORM[fid]
        dates = seances(debut, js, n_seances)
        assert dates[-1] <= (LOT1.fin if sid != CHANGEMENT[0] and debut <= LOT1.fin else LOT2.fin), (sid, dates[-1])
        n = round(cap * fill)
        choisis = rng.sample(pool, n + n_ann)
        inscrits, annules = choisis[:n], choisis[n:]
        ouv = ouverture(debut)
        speciaux = {}
        for k, p in enumerate(inscrits):
            role = "absent" if k < n_abs else ("abandon" if k < n_abs + n_ab else "normal")
            if sid == CHANGEMENT[0] and k == 0:
                role = "abandon_frontiere"
            speciaux[p] = role
        for p in inscrits + annules:
            jour = ouv + timedelta(days=rng.randint(0, (debut - ouv).days - 1))
            inscriptions.append({"sess": sid, "participant": p, "date": jour,
                                 "statut": "CONFIRMEE" if p in inscrits else "ANNULEE", "centre": centre})
        for p in inscrits:
            role = speciaux[p]
            q = min(1.0, max(0.4, assid + rng.uniform(-0.09, 0.09)))
            arret = {"abandon": rng.randint(n_seances // 3, n_seances - 2), "abandon_frontiere": 8}.get(role, n_seances)
            for j, d in enumerate(dates):
                pr = 0 if role == "absent" or j >= arret else int(rng.random() < q)
                presences.append({"session": sid, "participant": p, "date_seance": d, "present": pr})
            insc = next(i for i in inscriptions if i["sess"] == sid and i["participant"] == p)
            schema = "plein" if role == "absent" else rng.choices(["plein", "deux"], [0.6, 0.4])[0]
            if sid == CHANGEMENT[0] and p == inscrits[1]:
                schema = "deux"
            if schema == "plein":
                mouvements.append(dict(type="paiement", insc=insc, jour=insc["date"], montant=prix))
            else:
                mouvements.append(dict(type="paiement", insc=insc, jour=insc["date"], montant=prix // 2))
                if rng.random() >= impayes or (sid == CHANGEMENT[0] and p == inscrits[1]):
                    j_solde = debut + timedelta(days=rng.randint(0, 21))
                    if sid == CHANGEMENT[0] and p == inscrits[1]:
                        j_solde = date(2026, 7, 16)            # solde payé APRÈS le changement de centre
                    mouvements.append(dict(type="paiement", insc=insc, jour=j_solde, montant=prix - prix // 2))
            if role == "abandon":
                mouvements.append(dict(type="remboursement", insc=insc, jour=dates[arret] + timedelta(days=rng.randint(2, 6)),
                                       montant=prix * 3 // 10, motif="abandon en cours de session"))
            elif role == "abandon_frontiere":                   # le cas de la règle à clarifier (2)
                mouvements.append(dict(type="remboursement", insc=insc, jour=date(2026, 7, 20),
                                       montant=prix * 4 // 10, motif="abandon en cours de session"))
        for p in annules:
            insc = next(i for i in inscriptions if i["sess"] == sid and i["participant"] == p)
            mouvements.append(dict(type="paiement", insc=insc, jour=insc["date"], montant=prix))
            j = min(insc["date"] + timedelta(days=rng.randint(3, 10)), debut - timedelta(days=1))
            mouvements.append(dict(type="remboursement", insc=insc, jour=j, montant=prix, motif="annulation de l'inscription"))
    # numéros métier, dans l'ordre chronologique (stables d'un lot à l'autre)
    inscriptions.sort(key=lambda i: (i["date"], i["sess"], i["participant"]))
    for k, i in enumerate(inscriptions, 1):
        i["id"], i["numero"] = k, f"INS-26-{k:04d}"
    presences.sort(key=lambda x: (x["date_seance"], x["session"], x["participant"]))
    for k, x in enumerate(presences, 1):
        x["presence_id"] = f"PRS-{k:05d}"
    for m in mouvements:
        m.update(heure=heure(rng), statut="VALIDE", orphelin=False, sess=m["insc"]["sess"], num_insc=None,
                 texte=rng.random() < 0.07, mode=rng.choice(MODES))
    # pièges de la base : saisies annulées et mouvements vers une inscription inconnue
    p1 = [m for m in mouvements if m["type"] == "paiement" and sl(m["sess"]) == "lot1" and m["jour"] < date(2026, 6, 1)]
    p2 = [m for m in mouvements if m["type"] == "paiement" and sl(m["sess"]) == "lot2"]
    r2 = [m for m in mouvements if m["type"] == "remboursement" and sl(m["sess"]) == "lot2"]
    for m in rng.sample(p1, 2) + rng.sample(p2, 1) + rng.sample(r2, 1):
        mouvements.append({**m, "statut": "ANNULE", "heure": heure(rng)})
    for t, num, j in (("paiement", "INS-26-9001", date(2026, 3, 11)), ("paiement", "INS-26-9002", date(2026, 5, 19)),
                      ("paiement", "INS-26-9003", date(2026, 7, 22)), ("remboursement", "INS-26-9004", date(2026, 4, 28))):
        mouvements.append(dict(type=t, insc=None, jour=j, montant=280000, heure=heure(rng), statut="VALIDE",
                               orphelin=True, sess=None, num_insc=num, texte=False, mode="espèces",
                               motif="abandon en cours de session"))
    for t, prefixe, largeur in (("paiement", "PAI-26-", 5), ("remboursement", "RMB-26-", 4)):
        ms = sorted((m for m in mouvements if m["type"] == t),
                    key=lambda m: (m["jour"], m["heure"], m["num_insc"] or m["insc"]["numero"]))
        for k, m in enumerate(ms, 1):
            m["id"], m["numero"] = k, f"{prefixe}{k:0{largeur}d}"
    for m in mouvements:
        m["num_insc"] = m["num_insc"] or m["insc"]["numero"]
    return participants, inscriptions, presences, mouvements


def dans_lot(m: dict, lot: str) -> bool:
    """Périmètre des exports de la base : lot1 = sessions du lot 1 jusqu'au 30 juin ;
    lot2 = sessions de l'été + tout mouvement depuis le 1er juin (recouvrement)."""
    if lot == "lot1":
        return m["jour"] <= LOT1.fin and (m["sess"] is None or sl(m["sess"]) == "lot1")
    return (m["sess"] is not None and sl(m["sess"]) == "lot2") or CHEVAUCHEMENT_SQL <= m["jour"] <= LOT2.fin


def versions_sessions(lot: str, avec_changement: bool) -> list[dict]:
    vs, k = [], 0
    for sid, fid, centre, debut, *_ in sorted(SESSIONS):
        if lot == "lot1" and sl(sid) != "lot1":
            continue
        k += 1
        fin = CHANGEMENT[2].isoformat() if (avec_changement and sid == CHANGEMENT[0]) else None
        vs.append({"session_key": k, "session_id": sid, "formation_id": fid, "formateur": FORMATEURS[fid],
                   "date_debut": debut.isoformat(), "centre": centre, "valid_from": ouverture(debut).isoformat(),
                   "valid_to": fin})
    if avec_changement:
        v = next(x for x in vs if x["session_id"] == CHANGEMENT[0])
        vs.append({**v, "session_key": k + 1, "centre": CHANGEMENT[1], "valid_from": CHANGEMENT[2].isoformat(),
                   "valid_to": None})
    return vs


def dim_formation() -> list[dict]:
    return [{"formation_key": k, "formation_id": f[0], "intitule": f[1], "domaine": f[2], "prix_millimes": f[3],
             "capacite": f[4], "nb_seances": f[5]} for k, f in enumerate(FORMATIONS, 1)]


def tables_verite(presences, mouvements, vs) -> dict[str, list[dict]]:
    fk = {f[0]: k for k, f in enumerate(FORMATIONS, 1)}
    form = {s[0]: s[1] for s in SESSIONS}
    fp = [{"presence_id": x["presence_id"], "date_key": date_key(x["date_seance"]),
           "session_key": cle_version(vs, "session_id", "session_key", x["session"], x["date_seance"]),
           "formation_key": fk[form[x["session"]]], "participant_id": x["participant"], "present": x["present"]}
          for x in presences]
    fm = [{"mouvement_id": m["numero"], "date_key": date_key(m["jour"]),
           "session_key": cle_version(vs, "session_id", "session_key", m["sess"], m["jour"]),
           "formation_key": fk[form[m["sess"]]], "inscription_id": m["num_insc"], "type_mouvement": m["type"],
           "signe": 1 if m["type"] == "paiement" else -1, "montant_millimes": m["montant"]} for m in mouvements]
    return {"dim_formation": dim_formation(), "dim_session": vs, "fact_presence": fp, "fact_paiement": fm}


# --------------------------------------------------------------------------- rendu des sources
def ecrire_catalogue(chemin) -> None:
    lignes = []
    for i, (code, nom, dom, prix, cap, n) in enumerate(FORMATIONS):
        prix_cell = prix / 1000 if i % 3 != 1 else format_montant(prix, "virgule3")
        lignes.append([" f03" if code == "F03" else code, nom, dom, prix_cell,
                       str(cap) if code == "F05" else cap, str(n) if code == "F02" else n])
    ecrire_excel(chemin, [Feuille("Formations", ["Code formation", "Intitulé", "Domaine", "Prix par participant (TND)",
                                                 "Capacité (places)", "Nombre de séances"], lignes,
                                  titres=["Académie Nour — catalogue des formations 2026 (prix en TND par participant)"])])


def ecrire_sessions(chemin, lot: str, avec_changement: bool, extrait_le: str, liste=None) -> None:
    ss = []
    for sid, fid, centre, debut, js, *_ in (liste or SESSIONS):
        if liste is None and lot == "lot1" and sl(sid) != "lot1":
            continue
        hist = [{"centre": centre, "valide_depuis": ouverture(debut).isoformat() if liste is None else "2026-02-01"}]
        if avec_changement and sid == CHANGEMENT[0]:
            hist.append({"centre": CHANGEMENT[1], "valide_depuis": CHANGEMENT[2].isoformat()})
        ss.append({"code": " ses-2611" if sid == "SES-2611" else sid, "formation": fid, "formateur": FORMATEURS[fid],
                   "date_debut": debut.strftime("%d/%m/%Y") if sid == "SES-2605" else debut.isoformat(),
                   "rythme": RYTHMES[js], "historique": hist})
    ecrire_json(chemin, {"source": "Planning des sessions — Académie Nour", "extrait_le": extrait_le,
                         "centres": ["Tunis", "Sousse", "Sfax"], "sessions": ss})


DDL_OPERATIONS = """
CREATE TABLE participant (participant_id TEXT PRIMARY KEY, prenom TEXT NOT NULL, nom TEXT NOT NULL, ville TEXT);
CREATE TABLE inscription (
  id INTEGER PRIMARY KEY,
  numero_inscription TEXT NOT NULL UNIQUE,
  code_session TEXT NOT NULL,
  participant_id TEXT NOT NULL REFERENCES participant(participant_id),
  date_inscription TEXT NOT NULL,
  statut TEXT NOT NULL CHECK (statut IN ('CONFIRMEE', 'ANNULEE'))
);
CREATE TABLE paiement (
  id INTEGER PRIMARY KEY,
  numero_paiement TEXT NOT NULL UNIQUE,
  numero_inscription TEXT NOT NULL,
  date_paiement TEXT NOT NULL,
  montant REAL NOT NULL,
  mode TEXT,
  statut TEXT NOT NULL CHECK (statut IN ('VALIDE', 'ANNULE')),
  saisi_par TEXT
);
CREATE TABLE remboursement (
  id INTEGER PRIMARY KEY,
  numero_remboursement TEXT NOT NULL UNIQUE,
  numero_inscription TEXT NOT NULL,
  date_remboursement TEXT NOT NULL,
  montant REAL NOT NULL,
  motif TEXT,
  statut TEXT NOT NULL CHECK (statut IN ('VALIDE', 'ANNULE')),
  saisi_par TEXT
);
CREATE TABLE parametre (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
"""


def _montant(m) -> float | str:
    return format_montant(m["montant"], "virgule3") if m["texte"] else m["montant"] / 1000


def ecrire_operations(chemin, participants, inscriptions, mouvements, perimetre: str, genere_le: str) -> None:
    pids = sorted({i["participant"] for i in inscriptions})
    saisi = lambda m: f"accueil-{(m['insc']['centre'] if m['insc'] else 'Tunis').lower()}-{1 + m['id'] % 2}"
    pai = sorted((m for m in mouvements if m["type"] == "paiement"), key=lambda m: m["id"])
    rmb = sorted((m for m in mouvements if m["type"] == "remboursement"), key=lambda m: m["id"])
    ecrire_sqlite(chemin, DDL_OPERATIONS, {
        "participant": [{"participant_id": p, "prenom": participants[p][0], "nom": participants[p][1],
                         "ville": participants[p][2]} for p in pids],
        "inscription": [{"id": i["id"], "numero_inscription": i["numero"], "code_session": i["sess"],
                         "participant_id": i["participant"], "date_inscription": i["date"].isoformat(),
                         "statut": i["statut"]} for i in sorted(inscriptions, key=lambda i: i["id"])],
        "paiement": [{"id": m["id"], "numero_paiement": m["numero"], "numero_inscription": m["num_insc"],
                      "date_paiement": f"{m['jour'].isoformat()} {m['heure']}", "montant": _montant(m),
                      "mode": m["mode"], "statut": m["statut"], "saisi_par": saisi(m)} for m in pai],
        "remboursement": [{"id": m["id"], "numero_remboursement": m["numero"], "numero_inscription": m["num_insc"],
                           "date_remboursement": f"{m['jour'].isoformat()} {m['heure']}", "montant": _montant(m),
                           "motif": m["motif"], "statut": m["statut"], "saisi_par": saisi(m)} for m in rmb],
        "parametre": [{"cle": "export_genere_le", "valeur": genere_le}, {"cle": "perimetre", "valeur": perimetre},
                      {"cle": "devise", "valeur": "TND"}]})


def comptes_operations(participants_n, inscriptions, mouvements) -> dict:
    t = lambda typ, st=None: sum(m["type"] == typ and (st is None or m["statut"] == st) for m in mouvements)
    return {"participant": participants_n, "inscription": len(inscriptions),
            "inscriptions_annulees": sum(i["statut"] == "ANNULEE" for i in inscriptions),
            "paiement": t("paiement"), "paiements_annules": t("paiement", "ANNULE"),
            "remboursement": t("remboursement"), "remboursements_annules": t("remboursement", "ANNULE")}


# --------------------------------------------------------------------------- échantillon (≤ 12 lignes)
ECH_SESSION = ("SES-2690", "F06", "Tunis", date(2026, 3, 2), (0, 2))
ECHANTILLON = [  # (valeurs texte, décision)
    (["PRS-E01", "SES-2690", "PA-0901", "2026-03-02", "1"], None),
    (["PRS-E02", "SES-2690", "PA-0902", "02/03/2026", "1"], None),
    (["PRS-E03", " ses-2690 ", "PA-0903", "2 mars 2026", "0"], None),
    (["PRS-E04", "SES-2690", "pa-0901", "2026-03-04", "1"], None),
    (["PRS-E04", "SES-2690", "pa-0901", "2026-03-04", "1"], "doublon_exact"),
    (["PRS-E05", "SES-2690", "PA-0902", "04/03/2026", "0"], None),
    (["PRS-E06", "Ses-2690", "PA-0903", "2026-03-04", "0"], None),
    (["PRS-E07", "SES-2690", "PA-0901", "2026-03-04", "1"], "id_conflit"),
    (["PRS-E07", "SES-2690", "PA-0901", "2026-03-04", "0"], "id_conflit"),
    (["", "SES-2690", "PA-0902", "2026-03-04", "1"], "id_manquant"),
    (["PRS-E08", "SES-2699", "PA-0901", "2026-03-04", "1"], "cle_inconnue"),
    (["PRS-E09", "SES-2690", "PA-0902", "2026-03-04", "2"], "quantite_invalide"),
]
ECH_INSC = [(1, "INS-E1", "PA-0901", "2026-02-20", "CONFIRMEE"), (2, "INS-E2", "PA-0902", "2026-02-22", "CONFIRMEE"),
            (3, "INS-E3", "PA-0903", "2026-02-25", "CONFIRMEE"), (4, "INS-E4", "PA-0904", "2026-02-26", "ANNULEE")]
# id, numéro, inscription, date, montant (millimes), en texte ?, statut
ECH_PAI = [(1, "PAI-E1", "INS-E1", "2026-02-20 10:05:00", 320000, False, "VALIDE"),
           (2, "PAI-E2", "INS-E2", "2026-02-22 11:40:00", 160000, False, "VALIDE"),
           (3, "PAI-E3", "INS-E3", "2026-02-25 09:15:00", 320000, True, "VALIDE"),
           (4, "PAI-E4", "INS-E4", "2026-02-26 16:20:00", 320000, False, "VALIDE"),
           (5, "PAI-E5", "INS-E2", "2026-02-22 11:42:00", 160000, False, "ANNULE"),
           (6, "PAI-E6", "INS-E9", "2026-03-03 15:00:00", 320000, False, "VALIDE")]
ECH_RMB = [(1, "RMB-E1", "INS-E4", "2026-03-01 10:30:00", 320000, False, "VALIDE")]


def produire_echantillon(spec, dossier) -> dict:
    ecrire_csv(dossier / "presences.csv", ENTETE, [dict(zip(ENTETE, v)) for v, _ in ECHANTILLON])
    ecrire_catalogue(dossier / "catalogue.xlsx")
    ecrire_sessions(dossier / "sessions.json", "lot1", False, "2026-03-31", liste=[ECH_SESSION])
    insc = [{"id": a, "numero": b, "participant": c, "date": date.fromisoformat(d), "statut": e, "sess": ECH_SESSION[0],
             "centre": "Tunis"} for a, b, c, d, e in ECH_INSC]
    parts = {"PA-0901": ("Amel", "Ben Amor", "Tunis"), "PA-0902": ("Mehdi", "Karoui", "Ariana"),
             "PA-0903": ("Salma", "Dridi", "La Marsa"), "PA-0904": ("Firas", "Ouni", "Tunis")}
    mv = [dict(type=t, id=a, numero=b, num_insc=c, jour=date.fromisoformat(d[:10]), heure=d[11:], montant=e, texte=f,
               statut=g, insc=None, mode="carte bancaire", motif="annulation de l'inscription")
          for t, rows in (("paiement", ECH_PAI), ("remboursement", ECH_RMB)) for a, b, c, d, e, f, g in rows]
    ecrire_operations(dossier / "operations.sqlite", parts, insc, mv, "mouvements de la session SES-2690", "2026-03-31")
    vs = [{"session_key": 1, "session_id": "SES-2690", "formation_id": "F06", "formateur": FORMATEURS["F06"],
           "date_debut": "2026-03-02", "centre": "Tunis", "valid_from": "2026-02-01", "valid_to": None}]
    gardees = [v for v, m in ECHANTILLON if m is None]
    jour = {"2026-03-02": 2, "02/03/2026": 2, "2 mars 2026": 2}
    fp = [{"presence_id": v[0], "date_key": 20260300 + jour.get(v[3], 4), "session_key": 1, "formation_key": 6,
           "participant_id": v[2].strip().upper(), "present": int(v[4])} for v in gardees]
    fm = [{"mouvement_id": m["numero"], "date_key": date_key(m["jour"]), "session_key": 1, "formation_key": 6,
           "inscription_id": m["num_insc"], "type_mouvement": m["type"], "signe": 1 if m["type"] == "paiement" else -1,
           "montant_millimes": m["montant"]} for m in mv if m["statut"] == "VALIDE" and m["num_insc"] != "INS-E9"]
    tables = {"dim_formation": dim_formation(), "dim_session": vs, "fact_presence": fp, "fact_paiement": fm}
    rejets = {"presences.csv": {"cle_inconnue": 1, "id_conflit": 2, "id_manquant": 1, "quantite_invalide": 1},
              "operations.sqlite": {"cle_inconnue": 1}}
    spec_ech = replace(spec, scd2=replace(spec.scd2, frontieres=[]))     # les sessions des frontières n'y sont pas
    att = calculer_attendu_echantillon(spec_ech, tables, date(2026, 2, 1), date(2026, 3, 31), rejets,
                                       {"lignes_csv": 12, "doublons_exacts": 1, "lignes_gardees": len(fp),
                                        "paiements_annules_exclus": 1, "mouvements_gardes": len(fm)})
    ecrire_json(dossier / "attendu.json", att)
    (dossier / "attendu.md").write_text(md_echantillon(att), encoding="utf-8")
    return att


def md_echantillon(att) -> str:
    i = att["indicateurs"]
    t1 = md_tableau(["Ligne du fichier", "presence_id", "Lu dans le fichier", "Décision"],
                    [[n + 2, v[0] or "(vide)", f"{v[1]!r} · {v[2]!r} · {v[3]} · present {v[4]}",
                      "gardée" if m is None else ("ignorée : doublon exact de la ligne 5" if m == "doublon_exact"
                                                  else f"rejet `{m}`")] for n, (v, m) in enumerate(ECHANTILLON)])
    return f"""# Échantillon Académie Nour — le calcul à la main

12 lignes de `presences.csv` (les deux premières séances de la session SES-2690, Marketing digital à Tunis), le catalogue complet, 1 session dans `sessions.json`, 4 inscriptions, 6 paiements et 1 remboursement dans `operations.sqlite`. Faites le calcul **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`presences.csv`)

La ligne 1 du fichier est l'en-tête. `pa-0901`, ` ses-2690 ` et `Ses-2690` deviennent `PA-0901` et `SES-2690` (espaces enlevés, majuscules). `SES-2699` n'existe pas dans `sessions.json`.

{t1}

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées** : 3 participants × 2 séances (2 et 4 mars).

## 2. Inscrits, assiduité, remplissage

| Participant | 2 mars | 4 mars | Présences |
|---|---|---|---|
| PA-0901 | 1 | 1 | 2 |
| PA-0902 | 1 | 0 | 1 |
| PA-0903 | 0 | 0 | 0 (a payé, n'est jamais venu) |

- Inscrits = participants distincts de la feuille = **{i['inscrits']}** (PA-0903 compte : décision (1) A de la direction). PA-0904 a annulé : il n'est pas sur la feuille.
- Taux d'assiduité = présences / (inscrits × séances tenues) = 3 / (3 × 2) = **{pct_fr(i['taux_assiduite'])}**.
- Taux de remplissage = inscrits / capacité = 3 / 20 (capacité de F06 dans le catalogue) = **{pct_fr(i['taux_remplissage'])}**.
- Si l'on avait exclu PA-0903 (option B) : 2 inscrits, assiduité 3 / 4 = 75,00 %, remplissage 10,00 %. Ce n'est pas la règle retenue.

## 3. Paiements et remboursements (`operations.sqlite`)

- `PAI-E1` 320,000 + `PAI-E2` 160,000 (acompte) + `PAI-E3` `320,000` (montant stocké en texte avec virgule) + `PAI-E4` 320,000 (inscription annulée, payée puis remboursée) = **{tnd_fr(i['paiements_millimes'])}**.
- `PAI-E5` : statut `ANNULE` → ignoré (ce n'est pas un rejet).
- `PAI-E6` : l'inscription `INS-E9` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).
- `RMB-E1` : remboursement de l'inscription annulée = **{tnd_fr(i['remboursements_millimes'])}**.

**Encaissements nets = {tnd_fr(i['paiements_millimes'])} − {tnd_fr(i['remboursements_millimes'])} = {tnd_fr(i['encaissements_nets_millimes'])}.**

Encaissement attendu = inscrits × prix = 3 × 320,000 = {tnd_fr(i['encaissement_attendu_millimes'])} → taux d'encaissement = {pct_fr(i['taux_encaissement'])} (PA-0902 n'a payé que l'acompte).

## 4. Ce que doit contenir l'entrepôt de l'échantillon

`fact_presence` : {att['tables']['fact_presence']} lignes · `fact_paiement` : {att['tables']['fact_paiement']} lignes (4 paiements avec `signe` = 1, 1 remboursement avec `signe` = -1) · `dim_formation` : {att['tables']['dim_formation']} · `dim_session` : {att['tables']['dim_session']} · `dim_date` : {att['tables']['dim_date']} jours (février et mars 2026, car les paiements commencent en février). Rejets : {att['rejets']['total']} lignes. Les mêmes nombres sont dans `attendu.json`.
"""


# --------------------------------------------------------------------------- programme principal
def main(argv: list[str]) -> None:
    spec = MissionSpec(**SPEC_TEXTES, lots=[LOT1, LOT2], graine=GRAINE, tables=TABLES)
    dossier = preparer_dossier(spec)
    rng = rng_mission(GRAINE)
    participants, inscriptions, presences, mouvements = generer(rng)
    pres1 = [x for x in presences if x["date_seance"] <= LOT1.fin]
    pres2 = [x for x in presences if x["date_seance"] > LOT1.fin]
    m1 = [m for m in mouvements if dans_lot(m, "lot1")]
    m2 = [m for m in mouvements if dans_lot(m, "lot2")]
    assert not any(m["orphelin"] for m in m1 if m["jour"] >= CHEVAUCHEMENT_SQL)

    b1 = construire_csv(pres1, CHAMPS, DOSES["lot1"], rng, lambda k: f"PRS-8{k:04d}")
    jour_de = {x["presence_id"]: x["date_seance"] for x in pres1}
    rejouees = [l.valeurs for l in b1.lignes if l.motif is None and jour_de[l.origine] >= CHEVAUCHEMENT_CSV]
    assert 10 <= len(rejouees) <= 20, len(rejouees)
    b2 = construire_csv(pres2, CHAMPS, DOSES["lot2"], rng, lambda k: f"PRS-9{k:04d}", rejouees)
    for b in (b1, b2):                   # « 0 » est une valeur valide de present : valeurs invalides propres
        invalides = [l for l in b.lignes if l.motif == "quantite_invalide"]
        for k, l in enumerate(invalides):
            l.valeurs["present"] = PRESENTS_INVALIDES[k % len(PRESENTS_INVALIDES)]
    insc1 = [i for i in inscriptions if sl(i["sess"]) == "lot1"]
    for lot, b, mm, ii, extrait, perim in (
            ("lot1", b1, m1, insc1, "2026-06-30", "sessions de janvier à juin, mouvements jusqu'au 2026-06-30"),
            ("lot2", b2, m2, inscriptions, "2026-08-31", "toutes les inscriptions ; mouvements des sessions d'été et "
                                                          "tout mouvement du 2026-06-01 au 2026-08-31")):
        d = dossier / "sources" / lot
        ecrire_csv(d / "presences.csv", ENTETE, [l.valeurs for l in b.lignes])
        ecrire_catalogue(d / "catalogue.xlsx")
        ecrire_sessions(d / "sessions.json", lot, lot == "lot2", extrait)
        ecrire_operations(d / "operations.sqlite", participants, ii, mm, perim,
                          (date.fromisoformat(extrait) + timedelta(days=1)).isoformat())

    valides = lambda mm, deja=frozenset(): [m for m in mm if m["statut"] == "VALIDE" and not m["orphelin"]
                                             and m["numero"] not in deja]
    acc1 = valides(m1)
    acc2 = valides(m2, {m["numero"] for m in acc1})
    assert acc1 and acc2 and len(valides(m2)) > len(acc2), "il faut des mouvements déjà chargés au lot 2"
    lots = []
    for lot, b, mm, ii, acc, pres_cumul, mouv_cumul, vs in (
            (LOT1, b1, m1, insc1, acc1, pres1, acc1, versions_sessions("lot1", False)),
            (LOT2, b2, m2, inscriptions, acc2, presences, acc1 + acc2, versions_sessions("lot2", True))):
        n_sess = len({v["session_id"] for v in vs})
        lots.append(LotResultat(
            lot=lot,
            sources={"presences.csv": {"lignes": b.compteurs["lignes"], "encodage": "utf-8", "separateur": ";"},
                     "catalogue.xlsx": {"feuilles": ["Formations"], "formations": len(FORMATIONS),
                                        "ligne_entete_catalogue": 3},
                     "sessions.json": {"sessions": n_sess, "versions": len(vs)},
                     "operations.sqlite": comptes_operations(len({i["participant"] for i in ii}), ii, mm)},
            nettoyage={"presences.csv": {k: v for k, v in b.compteurs.items() if k not in ("lignes", "formats_montants")},
                       "catalogue.xlsx": {"cellules_texte_converties": 5, "codes_normalises": 1},
                       "sessions.json": {"dates_jj_mm_aaaa": 1, "codes_normalises": 1},
                       "operations.sqlite": {
                           "paiements_annules_exclus": sum(m["type"] == "paiement" and m["statut"] == "ANNULE" for m in mm),
                           "remboursements_annules_exclus": sum(m["type"] == "remboursement" and m["statut"] == "ANNULE"
                                                                for m in mm),
                           "montants_texte_virgule": sum(m["texte"] for m in mm),
                           "deja_charges": len(valides(mm)) - len(acc),
                           "mouvements_acceptes_nouveaux": len(acc)}},
            rejets={"presences.csv": b.rejets(), "operations.sqlite": {"cle_inconnue": sum(m["orphelin"] for m in mm)}},
            tables_verite=tables_verite(pres_cumul, mouv_cumul, vs),
            increment=None if lot is LOT1 else {
                "fact_presence_ajoutees": len(pres2), "fact_paiement_ajoutees": len(acc2),
                "sessions_ajoutees": 5, "versions_scd2_ajoutees": 6, "dim_date_ajoutees": len(jours(LOT2.debut, LOT2.fin))}))
        assert b.compteurs["lignes_acceptees_nouvelles"] == len(pres_cumul) - (0 if lot is LOT1 else len(pres1))

    attendus = produire_reference(spec, lots)
    con = entrepot_verite(spec, lots[-1].tables_verite, LOT2.fin)
    # double contrôle Python pur (sans SQL) des quatre indicateurs, après le lot 2
    insc_s = {s[0]: len({x["participant"] for x in presences if x["session"] == s[0]}) for s in SESSIONS}
    for s in SESSIONS:                   # une session terminée = inscrits × séances lignes
        assert sum(x["session"] == s[0] for x in presences) == insc_s[s[0]] * FORM[s[1]][5]
    ind = attendus["lot2"]["indicateurs"]
    nets = sum(m["montant"] * (1 if m["type"] == "paiement" else -1) for m in acc1 + acc2)
    assert ind["inscrits"] == sum(insc_s.values())
    assert abs(ind["taux_assiduite"] - sum(x["present"] for x in presences) / len(presences)) < 1e-6
    assert abs(ind["taux_remplissage"] - sum(insc_s.values()) / sum(FORM[s[1]][4] for s in SESSIONS)) < 1e-6
    assert ind["encaissements_nets_millimes"] == nets
    # cas de la règle à clarifier (2)
    assert con.execute("SELECT s.centre FROM fact_paiement m JOIN dim_session s ON s.session_key = m.session_key "
                       "WHERE s.session_id = ? AND m.date_key = 20260720", (CHANGEMENT[0],)).fetchall() == [("Sfax",)]

    ech = produire_echantillon(spec, dossier / "echantillon")
    exporter_v7_data(spec, ech, attendus)
    lot_de = lambda m: "lot1" if m in acc1 else "lot2"
    ecrire_verite_privee(spec, {
        "presences_verite.csv": (["lot", "presence_id", "session", "participant", "date_seance", "present"],
                                 [{**x, "lot": "lot1" if x["date_seance"] <= LOT1.fin else "lot2",
                                   "date_seance": x["date_seance"].isoformat()} for x in presences]),
        "mouvements_verite.csv": (["lot", "numero", "type", "num_insc", "sess", "jour", "montant_millimes"],
                                  [{**m, "lot": lot_de(m), "jour": m["jour"].isoformat(),
                                    "montant_millimes": m["montant"]} for m in acc1 + acc2]),
        "sessions_verite.csv": (["session_id", "formation_id", "centre_initial", "date_debut", "capacite", "prix_millimes",
                                 "nb_seances"],
                                [{"session_id": s[0], "formation_id": s[1], "centre_initial": s[2],
                                  "date_debut": s[3].isoformat(), "capacite": FORM[s[1]][4],
                                  "prix_millimes": FORM[s[1]][3], "nb_seances": FORM[s[1]][5]} for s in SESSIONS]),
        "rejets_verite.csv": (["lot", "numero_ligne", "motif", "identifiant"],
                              [{"lot": lot, **r} for lot, b in (("lot1", b1), ("lot2", b2)) for r in b.detail_rejets()]),
    })
    taille = taille_dossier(dossier)
    assert taille < TAILLE_MAX_MISSION, taille
    print(f"Mission {CODE} écrite dans {dossier} ({taille / 1024:.0f} Ko)")
    for a in attendus.values():
        i = a["indicateurs"]
        print(f"  {a['lot']} : presences.csv {a['sources']['presences.csv']['lignes']} lignes · "
              f"fact_presence {a['tables']['fact_presence']} · fact_paiement {a['tables']['fact_paiement']} · "
              f"rejets {a['rejets']['par_motif']} · inscrits {i['inscrits']} · assiduité {pct_fr(i['taux_assiduite'])} · "
              f"remplissage {pct_fr(i['taux_remplissage'])} · nets {tnd_fr(i['encaissements_nets_millimes'])}")
    e = ech["indicateurs"]
    print(f"  échantillon : inscrits {e['inscrits']} · assiduité {pct_fr(e['taux_assiduite'])} · "
          f"nets {tnd_fr(e['encaissements_nets_millimes'])}")


TABLES = [
    table_dim_date(),
    Table("dim_formation", "dimension", "Catalogue : une formation par ligne (feuille Formations).", [
        Colonne("formation_key", "INTEGER", "Clé technique (1, 2, 3…).", cle=True),
        Colonne("formation_id", "TEXT", "Code formation normalisé (strip + majuscules), ex. `F03`."),
        Colonne("intitule", "TEXT", "Intitulé de la formation."),
        Colonne("domaine", "TEXT", "Domaine, ex. `Données`."),
        Colonne("prix_millimes", "INTEGER", "Prix par participant en millimes."),
        Colonne("capacite", "INTEGER", "Places par session."),
        Colonne("nb_seances", "INTEGER", "Nombre de séances d'une session."),
    ], cle_metier="formation_id"),
    Table("dim_session", "dimension_scd2", "Sessions avec historique du centre de rattachement (SCD2).", [
        Colonne("session_key", "INTEGER", "Clé technique d'une VERSION de session.", cle=True),
        Colonne("session_id", "TEXT", "Code session, ex. `SES-2619` (plusieurs versions possibles)."),
        Colonne("formation_id", "TEXT", "Code de la formation donnée dans la session."),
        Colonne("formateur", "TEXT", "Formateur."),
        Colonne("date_debut", "TEXT", "Date de la première séance, AAAA-MM-JJ."),
        Colonne("centre", "TEXT", "Centre de rattachement de cette version : `Tunis`, `Sousse` ou `Sfax`."),
        Colonne("valid_from", "TEXT", "Début de validité (inclus), AAAA-MM-JJ."),
        Colonne("valid_to", "TEXT", "Fin de validité (exclue), vide = version courante.", nullable=True),
    ], cle_metier="session_id"),
    Table("fact_presence", "fait", "Une ligne d'émargement acceptée : un inscrit × une séance.", [
        Colonne("presence_id", "TEXT", "Identifiant de la ligne d'émargement (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour de la séance.", ref="dim_date.date_key"),
        Colonne("session_key", "INTEGER", "Version de la session valable à la date de la séance.",
                ref="dim_session.session_key"),
        Colonne("formation_key", "INTEGER", "Formation de la session.", ref="dim_formation.formation_key"),
        Colonne("participant_id", "TEXT", "Code participant normalisé, ex. `PA-0137`."),
        Colonne("present", "INTEGER", "1 = présent, 0 = absent."),
    ]),
    Table("fact_paiement", "fait", "Un paiement ou un remboursement VALIDE de la base de gestion.", [
        Colonne("mouvement_id", "TEXT", "`numero_paiement` ou `numero_remboursement` (clé métier unique).", cle=True),
        Colonne("date_key", "INTEGER", "Jour du mouvement (heure ignorée).", ref="dim_date.date_key"),
        Colonne("session_key", "INTEGER", "Version de la session de l'inscription valable à la date du MOUVEMENT.",
                ref="dim_session.session_key"),
        Colonne("formation_key", "INTEGER", "Formation de la session.", ref="dim_formation.formation_key"),
        Colonne("inscription_id", "TEXT", "`numero_inscription` concerné."),
        Colonne("type_mouvement", "TEXT", "`paiement` ou `remboursement`."),
        Colonne("signe", "INTEGER", "1 pour un paiement, -1 pour un remboursement."),
        Colonne("montant_millimes", "INTEGER", "Montant en millimes, toujours positif."),
    ]),
]

if __name__ == "__main__":
    main(sys.argv[1:])
