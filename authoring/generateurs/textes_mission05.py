"""Textes et règles de la mission M05 (Académie Nour). Séparés du code de génération pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source, tnd_fr

# Une ligne par « mouvement » : présence (date de la séance), session (date de début), paiement / remboursement
# (date du mouvement). Toutes les colonnes chiffrées sont additives : les ratios sont des rapports de sommes.
VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, s.session_id, s.centre, fo.formation_id,
       p.present AS present, 1 AS lignes_presence, 0 AS inscrits, 0 AS capacite, 0 AS attendu_encaisse,
       0 AS paye, 0 AS rembourse
FROM fact_presence p
JOIN dim_date d ON d.date_key = p.date_key
JOIN dim_session s ON s.session_key = p.session_key
JOIN dim_formation fo ON fo.formation_key = p.formation_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), s.session_id, s.centre, fo.formation_id, 0, 0,
       COALESCE(i.inscrits, 0), fo.capacite, COALESCE(i.inscrits, 0) * fo.prix_millimes, 0, 0
FROM dim_session s
JOIN dim_formation fo ON fo.formation_id = s.formation_id
JOIN dim_date d ON d.date_complete = s.date_debut
LEFT JOIN (SELECT s2.session_id AS session_id, COUNT(DISTINCT p2.participant_id) AS inscrits
           FROM fact_presence p2 JOIN dim_session s2 ON s2.session_key = p2.session_key
           GROUP BY s2.session_id) i ON i.session_id = s.session_id
WHERE s.valid_from <= s.date_debut AND (s.valid_to IS NULL OR s.date_debut < s.valid_to)
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), s.session_id, s.centre, fo.formation_id, 0, 0, 0, 0, 0,
       CASE WHEN m.signe = 1 THEN m.montant_millimes ELSE 0 END,
       CASE WHEN m.signe = -1 THEN m.montant_millimes ELSE 0 END
FROM fact_paiement m
JOIN dim_date d ON d.date_key = m.date_key
JOIN dim_session s ON s.session_key = m.session_key
JOIN dim_formation fo ON fo.formation_key = m.formation_key
"""

MOTIFS = dict(MOTIFS_STANDARD)
MOTIFS["cle_inconnue"] = ("code absent du référentiel : session absente de `sessions.json`, participant sans "
                          "inscription confirmée à cette session, ou paiement / remboursement vers une inscription inconnue")
MOTIFS["quantite_invalide"] = "valeur de `present` autre que `0` ou `1` (ex. `2`, `-1`, `oui`, `1,5`)"

SPEC_TEXTES = dict(
    code="M05",
    numero="05",
    titre="Centre de formation",
    entreprise="Académie Nour",
    secteur="centre de formations professionnelles courtes (bureautique, données, gestion, langues) à Tunis, Sousse et Sfax",
    contexte=("L'Académie Nour propose des formations courtes pour les salariés et les jeunes diplômés : Excel, "
              "Power BI, comptabilité, anglais professionnel, gestion de projet, marketing digital, Python. Chaque "
              "formation est donnée en **sessions** (un groupe, un formateur, un centre, un nombre fixe de séances). "
              "Les formateurs remplissent une feuille d'émargement (CSV), le catalogue vit dans un classeur Excel, le "
              "planning des sessions dans un fichier JSON, et les inscriptions, paiements et remboursements dans une "
              "petite base SQLite. La direction ne sait pas quelles sessions remplissent leurs objectifs."),
    demande=("Bonjour à tous les deux,\n\nNous ouvrons beaucoup de sessions, mais je ne sais pas lesquelles marchent. "
             "Je veux, par session, par centre, par formation et par mois : le nombre d'inscrits, le taux "
             "d'assiduité, le taux de remplissage et les encaissements nets (paiements moins remboursements). "
             "Nos objectifs : remplissage d'au moins 70 %, assiduité d'au moins 80 %, et au moins 95 % de "
             "l'encaissement attendu (inscrits × prix). Dites-moi aussi quelles lignes vous avez écartées, et "
             "pourquoi.\n\nPour information : à partir du 15 juillet, la session d'anglais SES-2619 (classe du mardi "
             "soir, à distance) est rattachée au centre de Sfax au lieu de Sousse. Ce qui s'est passé avant reste à "
             "Sousse.\n\nLamia Ben Salah, directrice (Solen Digital, pour le compte de l'Académie Nour)"),
    grain="une présence : un participant inscrit × une séance d'une session (présent 0 ou 1)",
    sources=[
        Source("presences.csv", "csv", "Feuilles d'émargement exportées (UTF-8, séparateur `;`) : chaque inscrit "
               "figure à chaque séance tenue, avec `present` = 1 ou 0.", [
                   ColonneSource("presence_id", "texte", "Identifiant de la ligne d'émargement.", "PRS-00412"),
                   ColonneSource("session", "texte", "Code de la session (casse et espaces variables).", " ses-2604 "),
                   ColonneSource("participant", "texte", "Code du participant.", "PA-0137"),
                   ColonneSource("date_seance", "texte", "Date de la séance, trois formats possibles.", "04/03/2026"),
                   ColonneSource("present", "texte", "1 = présent, 0 = absent.", "1"),
               ], ["formats de dates mélangés", "doublons", "identifiants vides ou en conflit",
                   "session inconnue ou participant non inscrit", "valeurs de `present` invalides",
                   "lot2 : recopie la séance du 30 juin de SES-2619"]),
        Source("catalogue.xlsx", "excel", "Feuille `Formations` (en-têtes à la ligne 3) : tarif, capacité et nombre de séances.", [
            ColonneSource("Code formation", "texte", "Code de la formation (une cellule mal saisie).", " f03"),
            ColonneSource("Intitulé", "texte", "Nom de la formation.", "Comptabilité pratique"),
            ColonneSource("Domaine", "texte", "Domaine.", "Gestion"),
            ColonneSource("Prix par participant (TND)", "nombre ou texte", "Prix d'une inscription.", "450,000"),
            ColonneSource("Capacité (places)", "nombre ou texte", "Places par session.", "14"),
            ColonneSource("Nombre de séances", "nombre ou texte", "Séances par session.", "8"),
        ], ["titre au-dessus du tableau", "nombres stockés comme texte"]),
        Source("sessions.json", "json", "Planning des sessions avec l'historique du centre de rattachement.", [
            ColonneSource("sessions[].code", "texte", "Code de la session.", "SES-2619"),
            ColonneSource("sessions[].formation", "texte", "Code de la formation.", "F04"),
            ColonneSource("sessions[].formateur", "texte", "Formateur (nom inventé).", "Mme Olfa Chebbi"),
            ColonneSource("sessions[].date_debut", "texte", "Date de la première séance (deux formats).", "2026-05-26"),
            ColonneSource("sessions[].rythme", "texte", "Jours et horaires (information).", "mardi, 18 h – 21 h"),
            ColonneSource("sessions[].historique[].centre", "texte", "Centre de rattachement.", "Sousse"),
            ColonneSource("sessions[].historique[].valide_depuis", "date ISO",
                          "Début de validité (inclus) : ouverture des inscriptions, puis date du changement.", "2026-04-21"),
        ], ["lot2 : une deuxième version pour SES-2619 (Sfax au 2026-07-15)", "une date au format JJ/MM/AAAA",
            "un code en minuscules"]),
        Source("operations.sqlite", "sqlite", "Base de gestion : tables `participant`, `inscription`, `paiement`, "
               "`remboursement`, `parametre`.", [
                   ColonneSource("inscription.numero_inscription", "texte", "Numéro de l'inscription (unique).", "INS-26-0042"),
                   ColonneSource("inscription.code_session / participant_id", "texte", "Session et participant.", "SES-2604 / PA-0137"),
                   ColonneSource("inscription.statut", "texte", "`CONFIRMEE` ou `ANNULEE`.", "CONFIRMEE"),
                   ColonneSource("paiement.id / numero_paiement", "entier / texte", "Ligne interne / numéro unique.", "57 / PAI-26-00057"),
                   ColonneSource("paiement.numero_inscription", "texte", "Inscription payée.", "INS-26-0042"),
                   ColonneSource("paiement.date_paiement", "texte", "Date et heure.", "2026-02-11 10:15:00"),
                   ColonneSource("paiement.montant", "réel ou texte", "Montant payé en TND.", "225.0"),
                   ColonneSource("paiement.statut", "texte", "`VALIDE` ou `ANNULE` (saisie annulée).", "VALIDE"),
                   ColonneSource("remboursement.*", "—", "Même structure : `numero_remboursement`, "
                                 "`numero_inscription`, `date_remboursement`, `montant`, `motif`, `statut`.", "RMB-26-0003"),
               ], ["paiements annulés", "paiement vers une inscription inconnue", "montants stockés en texte avec virgule",
                   "lot2 : recopie des mouvements depuis le 1er juin"]),
    ],
    indicateurs=[
        Indicateur("inscrits", "Inscrits", "nombre",
                   "nombre d'inscriptions distinctes de la session (participants de la feuille d'émargement), "
                   "compté une fois par session, à la date de début de la session", "SUM(inscrits)"),
        Indicateur("taux_assiduite", "Taux d'assiduité", "ratio",
                   "présences / (inscrits × séances), soit la somme de `present` divisée par le nombre de lignes de "
                   "présence (chaque inscrit figure à chaque séance tenue)",
                   "ROUND(1.0 * SUM(present) / NULLIF(SUM(lignes_presence), 0), 6)", tolerance=0.0001),
        Indicateur("taux_remplissage", "Taux de remplissage", "ratio",
                   "inscrits / capacité (capacité du catalogue, une fois par session)",
                   "ROUND(1.0 * SUM(inscrits) / NULLIF(SUM(capacite), 0), 6)", tolerance=0.0001),
        Indicateur("paiements_millimes", "Paiements", "millimes",
                   "somme des paiements VALIDE acceptés", "SUM(paye)", principal=False),
        Indicateur("remboursements_millimes", "Remboursements", "millimes",
                   "somme des remboursements VALIDE acceptés", "SUM(rembourse)", principal=False),
        Indicateur("encaissements_nets_millimes", "Encaissements nets", "millimes",
                   "paiements − remboursements", "SUM(paye) - SUM(rembourse)"),
        Indicateur("encaissement_attendu_millimes", "Encaissement attendu", "millimes",
                   "inscrits × prix par participant du catalogue", "SUM(attendu_encaisse)", principal=False),
        Indicateur("taux_encaissement", "Taux d'encaissement", "ratio",
                   "encaissements nets / encaissement attendu",
                   "ROUND(1.0 * (SUM(paye) - SUM(rembourse)) / NULLIF(SUM(attendu_encaisse), 0), 6)",
                   tolerance=0.0001, principal=False),
        Indicateur("presences", "Présences", "nombre", "somme de `present` (séances suivies)", "SUM(present)",
                   principal=False),
    ],
    vue_analyse=VUE,
    axes={"par_session": "session_id", "par_centre": "centre", "par_formation": "formation_id", "par_mois": "mois"},
    scd2=SCD2("dim_session", "session_key", "session_id", "centre",
              faits=[("fact_presence", "session_key", "date_key"), ("fact_paiement", "session_key", "date_key")],
              frontieres=[("SES-2619", "2026-06-30"), ("SES-2619", "2026-07-14"), ("SES-2619", "2026-07-15"),
                          ("SES-2613", "2026-07-15")],
              changement="La session SES-2619 (anglais professionnel, mardi soir, à distance) passe du centre "
                         "« Sousse » au centre « Sfax » le 2026-07-15 (inclus). Cette information arrive avec "
                         "`lot2/sessions.json`."),
    regles=[
        ("Doublon exact", "la même ligne d'émargement deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`PRS-80037` deux fois avec `present` différent",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`presence_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "session `SES-2699`, participant `PA-9001` non inscrit, paiement vers `INS-26-9001`",
         "rejet `cle_inconnue`"),
        ("Présence invalide", "`present` = `2`, `-1`, `oui`, `1,5`", "rejet `quantite_invalide`"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` ses-2604 `, `Ses-2604`, ` pa-0137`, ` f03`", "supprimer les espaces autour + majuscules"),
        ("Format décimal", "`450,000` (Excel), `225,000` (texte dans SQLite), `225.0`",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers"),
        ("Encodage", "`Comptabilité`, `espèces`", "lire les fichiers en UTF-8"),
        ("Paiement ou remboursement annulé", "`statut = 'ANNULE'`", "ignorer (ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie la séance du 30 juin et les mouvements depuis le 1er juin",
         "ignorer : la clé métier existe déjà"),
    ],
    motifs=MOTIFS,
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`presence_id` vide → `id_manquant` ;",
        "`presence_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "session absente de `sessions.json`, ou participant sans inscription `CONFIRMEE` à cette session dans "
        "`operations.sqlite` → `cle_inconnue` ;",
        "`present` différent de `0` ou `1` → `quantite_invalide` ;",
        "`presence_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Paiements puis remboursements : `ANNULE` ignoré → `numero_inscription` absent de la table `inscription` = "
        "`cle_inconnue` (source `operations.sqlite`, numero_ligne = `id` de la ligne) → numéro déjà chargé = ignoré.",
    ],
    regles_metier=[
        "Une ligne de présence prend la version de la session valable à la **date de la séance**.",
        "Un paiement ou un remboursement prend la session de son inscription et la version valable à la **date du "
        "mouvement** (heure ignorée). `fact_paiement.signe` = `1` pour un paiement, `-1` pour un remboursement ; "
        "`montant_millimes` est toujours positif.",
        "Les paiements et remboursements d'une inscription `ANNULEE` sont chargés (l'argent est entré puis sorti) ; "
        "une inscription annulée n'est pas sur la feuille d'émargement, donc elle ne compte pas dans les inscrits.",
        "Inscrits d'une session = participants distincts de la feuille d'émargement de cette session. Ils sont "
        "comptés une fois, avec la capacité et l'encaissement attendu, dans le **mois et le centre de la date de "
        "début** de la session (vue d'analyse).",
        "Une session terminée a exactement inscrits × nombre de séances (catalogue) lignes de présence : c'est le "
        "dénominateur du taux d'assiduité.",
        "`dim_formation.prix_millimes` = prix par participant du catalogue ; `capacite` et `nb_seances` en entiers.",
        "`dim_session.valid_from` de la première version = `valide_depuis` (ouverture des inscriptions) ; "
        "`date_debut` = date ISO de la première séance.",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, "
        "243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": ("(1) Un participant a payé mais n'est jamais venu (présent = 0 à toutes les séances) : compte-t-il "
                     "dans les inscrits ? (2) Un participant de SES-2619 est remboursé le 20 juillet, après le "
                     "changement de centre : le remboursement compte-t-il à Sousse (centre de son inscription) ou à "
                     "Sfax (centre le jour du remboursement) ?"),
        "options": ("- (1) A : oui, il occupe une place et il a payé ; ses absences font baisser l'assiduité.\n"
                    "- (1) B : non, on ne compte que les participants venus au moins une fois (le remplissage baisse, "
                    "l'assiduité monte).\n"
                    "- (2) A : version de la session à la date de l'inscription (Sousse).\n"
                    "- (2) B : version valable à la date du remboursement (Sfax), comme chaque mouvement."),
        "decision": ("(1) A : il compte dans les inscrits et dans le dénominateur de l'assiduité ; son paiement compte "
                     "dans les encaissements. (2) B : chaque présence, paiement ou remboursement est rattaché à la "
                     "version de la session valable à SA date et compté dans SON mois ; le remboursement du 20 juillet "
                     "compte donc à Sfax."),
    },
    variantes=[
        "Nouvel indicateur : taux d'abandon = inscrits absents aux deux dernières séances de leur session / inscrits.",
        "Nouvelle règle : une présence datée d'un jour qui n'est pas une séance de la session (hors rythme du "
        "planning) est rejetée avec un nouveau motif `seance_inconnue`.",
        "Changement historique : la session SES-2622 est rattachée à Tunis à partir du 2026-07-20 (deuxième session "
        "historisée dans `dim_session`).",
    ],
    ecrans_app=[
        ("Vue direction", "inscrits, assiduité, remplissage, encaissements nets et taux d'encaissement, puis les "
                          "encaissements nets par mois et par centre (barres empilées)."),
        ("Détail par session", "chaque session avec ses versions : SES-2619 à Sousse jusqu'au 2026-07-14, puis à Sfax."),
        ("Qualité des données", "lignes lues, gardées, rejetées par motif et par lot."),
    ],
    textes_app=["Vue direction", "Détail par session", "Qualité des données"],
    export_sommes={"fact_presence": ["present"], "fact_paiement": ["montant_millimes", "signe"],
                   "dim_formation": ["prix_millimes", "capacite", "nb_seances"]},
    visuels=[
        {"type": "empile", "indicateur": "encaissements_nets_millimes", "x": "mois", "serie": "centre",
         "ordre_series": ["Tunis", "Sousse", "Sfax"], "fichier": "encaissements_nets_par_mois_et_centre",
         "titre": "Encaissements nets par mois et par centre", "libelle_x": "Mois", "libelle_serie": "Centre"},
        {"type": "barres", "indicateurs": ["taux_assiduite", "taux_remplissage"], "axe": "centre",
         "fichier": "assiduite_et_remplissage_par_centre", "titre": "Taux d'assiduité et de remplissage par centre",
         "libelle_x": "Centre", "libelle_y": "Taux"},
        {"type": "barres", "indicateurs": ["encaissements_nets_millimes", "encaissement_attendu_millimes"],
         "axe": "formation_id", "fichier": "encaissements_nets_et_attendus_par_formation",
         "titre": "Encaissements nets et encaissement attendu par formation", "libelle_x": "Formation",
         "libelle_y": "Montant"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"presences": "presences.csv", "paiements": "operations.sqlite"},
    regle_mois="(présences, sessions, paiements et remboursements réunis ; une session est rangée à sa date de début). "
               "Un mouvement est rangé dans le mois **de sa propre date**.",
    sections_cahier=[("Objectifs de la direction (décision)",
                      "Une session **atteint ses objectifs** si : taux de remplissage ≥ 70 %, taux d'assiduité ≥ 80 % et "
                      "encaissements nets ≥ 95 % de l'encaissement attendu (inscrits × prix). Les valeurs par session "
                      "sont dans l'agrégat `par_session` de `reference/attendu_lot2.json`. La recommandation à la "
                      "direction nomme les sessions qui n'atteignent pas un objectif, dit lequel, et propose une action."),
                     ("Ce que le lot 2 ajoute au passé (paiements de juin, sessions d'été)", lambda a: (
                      "Le `operations.sqlite` du lot 1 est un export **par session** : il ne contient que les inscriptions "
                      "et les mouvements des 20 sessions de janvier à juin. Les 5 sessions d'été (début en juillet-août) "
                      "ouvrent leurs inscriptions en juin et leurs participants **paient en juin**, mais ces paiements ne "
                      "sont exportés qu'avec le lot 2, qui contient toutes les inscriptions et tout mouvement du "
                      "2026-06-01 au 2026-08-31. C'est un fait **arrivé en retard** : il est rangé dans le mois de SA "
                      "date (juin), pas dans le mois du chargement. Le mois de juin change donc après l'incrément : "
                      f"encaissements nets de juin {tnd_fr(a['lot1']['agregats']['par_mois']['2026-06']['encaissements_nets_millimes'])} "
                      f"après le lot 1, {tnd_fr(a['lot2']['agregats']['par_mois']['2026-06']['encaissements_nets_millimes'])} après le lot 2. "
                      "Ce n'est pas une erreur : vérifiez-le dans `par_mois` des deux fichiers `attendu_*.json`.\n\n"
                      f"`dim_session` gagne {a['lot2']['increment']['versions_scd2_ajoutees']} versions au lot 2 : "
                      f"{a['lot2']['increment']['sessions_ajoutees']} sessions d'été nouvelles (une première version "
                      "chacune) + **une seule** nouvelle version historique, SES-2619 qui passe de Sousse à Sfax le "
                      "2026-07-15 (le seul changement SCD2 de la mission)."))],
    parcours_app="Pendant la démonstration : choisir une période et un centre dans les filtres, lire un indicateur et "
                 "son unité, puis montrer sur l'écran 2 que les présences et paiements de SES-2619 avant le 2026-07-15 "
                 "restent à « Sousse » et que le remboursement du 2026-07-20 est à « Sfax ».",
)
SPEC_TEXTES["regle_a_clarifier"]["consequence"] = (
    "Conséquence dans l'entrepôt : le participant jamais venu garde ses lignes `present = 0` dans `fact_presence` ; "
    "le remboursement du 2026-07-20 de SES-2619 pointe vers la version « Sfax » de `dim_session`.")
