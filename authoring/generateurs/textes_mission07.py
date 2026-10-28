"""Textes et règles de la mission M07 (FibreNet, abonnements internet). Séparés du code pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

# Une ligne par « mouvement » : soit un abonnement-mois (état dérivé), soit une facture.
VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, o.offre_id, o.gamme, c.type_compte, c.ville,
       a.actif_debut, a.actif_fin, a.nouveau, a.depart,
       a.actif_fin * a.mensualite_millimes AS mrr, 0 AS facture
FROM fact_abonnement_mois a
JOIN dim_date d ON d.date_key = a.date_key
JOIN dim_offre o ON o.offre_key = a.offre_key
JOIN dim_compte c ON c.compte_key = a.compte_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), o.offre_id, o.gamme, c.type_compte, c.ville,
       0, 0, 0, 0, 0, f.montant_millimes
FROM fact_facture f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_offre o ON o.offre_key = f.offre_key
JOIN dim_compte c ON c.compte_key = f.compte_key
"""

LECTURE_MOIS = ("valeur d'**un** mois : lisez l'agrégat `par_mois` ; sur plusieurs mois, le total de la référence "
                "additionne les fins de mois (abonnés-mois)")

DERIVATION = [
    ("`actif_debut`", "1 si l'abonnement était actif le dernier jour du mois **précédent** : "
                      "`date_debut` < 1er jour du mois ET (`date_fin` vide OU `date_fin` ≥ 1er jour du mois)"),
    ("`nouveau`", "1 si `date_debut` tombe dans le mois"),
    ("`depart`", "1 si `date_fin` tombe dans le mois (même le dernier jour du mois)"),
    ("`actif_fin`", "1 si l'abonnement est actif le dernier jour du mois : `date_debut` ≤ dernier jour ET "
                    "(`date_fin` vide OU `date_fin` > dernier jour)"),
    ("`mensualite_millimes`", "prix mensuel de la version de l'offre valable le **dernier jour du mois**"),
    ("contrôle", "pour chaque mois : actifs fin = actifs début + nouveaux − départs"),
]

SPEC_TEXTES = dict(
    code="M07",
    numero="07",
    titre="Abonnements FibreNet",
    entreprise="FibreNet",
    secteur="fournisseur d'accès internet par fibre, clients particuliers et entreprises",
    contexte=("FibreNet vend des abonnements internet par fibre à des particuliers et à des entreprises dans "
              "plusieurs villes. Chaque mois, chaque abonnement reçoit une facture. La facturation exporte les "
              "factures dans un CSV, les comptes clients vivent dans un classeur Excel, les offres et leurs prix "
              "dans un fichier JSON, et les dates de début et de fin des abonnements dans la base SQLite de "
              "l'outil opérationnel. La direction ne sait pas dire combien d'abonnés restent, combien partent, ni "
              "combien rapporte chaque mois le parc d'abonnés. Solen Digital vous confie la mission."),
    demande=("Bonjour à tous les deux,\n\nNous gagnons des clients, mais nous en perdons aussi. Je veux voir, mois "
             "par mois, par gamme d'offre et par type de compte : le nombre d'abonnés actifs en fin de mois, le "
             "revenu mensuel récurrent (MRR), les départs du mois et le taux de départ. Et je veux savoir ce que "
             "vous avez dû écarter dans les fichiers, et pourquoi.\n\nPour information : le 15 juillet, l'offre "
             "Fibre 300 passe de la gamme confort à la gamme pro, et son prix passe de 89,900 à 99,900 TND par "
             "mois. Les chiffres du premier semestre doivent rester en confort, à l'ancien prix.\n\n"
             "Lamia Ben Salah, directrice (Solen Digital, pour le compte de FibreNet)"),
    grain="une facture mensuelle d'abonnement (un abonnement × un mois facturé)",
    sources=[
        Source("facturation.csv", "csv", "Factures mensuelles exportées de la facturation (UTF-8, séparateur `;`).", [
            ColonneSource("facture_id", "texte", "Numéro de facture (unique).", "F26-000412"),
            ColonneSource("abonnement_id", "texte", "Abonnement facturé (→ base des abonnements).", "AB00137"),
            ColonneSource("compte", "texte", "Numéro de compte client (casse et espaces variables).", " c0042"),
            ColonneSource("offre", "texte", "Code de l'offre (casse variable).", "FN-F100"),
            ColonneSource("mois_facture", "texte", "Mois facturé, AAAA-MM.", "2026-03"),
            ColonneSource("date_facture", "texte", "Date d'émission, trois formats possibles.", "01/03/2026"),
            ColonneSource("nb_mois", "texte", "Nombre de mensualités facturées (toujours 1 si la ligne est juste).", "1"),
            ColonneSource("montant", "texte", "Montant facturé en TND, formats variés.", "69,900"),
        ], ["formats de montants et de dates mélangés", "doublons", "identifiants vides ou en conflit",
            "comptes, offres ou abonnements inconnus", "nb_mois invalide", "lot2 : recopie des factures depuis le 10 juin"]),
        Source("comptes.xlsx", "excel", "Feuille `Comptes` (titre au-dessus, en-têtes à la ligne 3).", [
            ColonneSource("N° compte", "texte", "Numéro de compte (une cellule mal saisie).", " c0017"),
            ColonneSource("Nom / raison sociale", "texte", "Nom inventé du client (accents).", "Atelier Yasmine Déco"),
            ColonneSource("Type de compte", "texte", "`particulier` ou `entreprise`, casse variable.", " Entreprise "),
            ColonneSource("Ville", "texte", "Ville du compte.", "Sousse"),
            ColonneSource("Client depuis", "date", "Date d'ouverture du compte.", "2024-05-12"),
        ], ["titre au-dessus du tableau", "type de compte en casse variable", "lot2 : nouveaux comptes"]),
        Source("offres.json", "json", "Catalogue des offres avec l'historique de gamme et de prix.", [
            ColonneSource("offres[].code", "texte", "Code de l'offre.", "FN-F300"),
            ColonneSource("offres[].nom", "texte", "Nom commercial.", "Fibre 300"),
            ColonneSource("offres[].historique[].gamme", "texte", "Gamme (casse variable).", "Confort"),
            ColonneSource("offres[].historique[].prix_mensuel", "texte ou nombre", "Prix mensuel en TND.", "89,900"),
            ColonneSource("offres[].historique[].valide_depuis", "date ISO", "Début de la version (inclus).", "2024-03-01"),
        ], ["prix tantôt nombre, tantôt texte à virgule", "lot2 : une deuxième version pour FN-F300 au 2026-07-15"]),
        Source("abonnements.sqlite", "sqlite", "Base opérationnelle : tables `abonnement`, `motif_resiliation`, `parametre`.", [
            ColonneSource("abonnement.id", "entier", "Numéro interne de la ligne.", "137"),
            ColonneSource("abonnement.abonnement_id", "texte", "Identifiant de l'abonnement (unique).", "AB00137"),
            ColonneSource("abonnement.num_compte", "texte", "Compte titulaire.", "C0042"),
            ColonneSource("abonnement.code_offre", "texte", "Offre souscrite (casse variable).", " fn-f20"),
            ColonneSource("abonnement.date_debut", "texte ISO", "Premier jour de service.", "2025-11-03"),
            ColonneSource("abonnement.date_fin", "texte ISO ou NULL", "Dernier jour de service ; NULL = toujours actif.", "2026-03-31"),
            ColonneSource("abonnement.statut", "texte", "`ACTIF`, `RESILIE` ou `ANNULE` (jamais installé).", "RESILIE"),
            ColonneSource("abonnement.code_motif", "texte ou NULL", "Motif de résiliation → `motif_resiliation`.", "DEM"),
        ], ["abonnements annulés avant installation", "abonnements vers un compte inconnu",
            "abonnements résiliés en 2025 (aucun mois en 2026)", "lot2 : la base complète, résiliations de l'été comprises"]),
    ],
    indicateurs=[
        Indicateur("actifs_fin_mois", "Abonnés actifs fin de mois", "nombre",
                   "nombre d'abonnements actifs le dernier jour du mois (`actif_fin` = 1) — " + LECTURE_MOIS,
                   "SUM(actif_fin)"),
        Indicateur("mrr_millimes", "MRR (revenu mensuel récurrent)", "millimes",
                   "somme des mensualités des abonnements actifs en fin de mois, au prix de la version de l'offre "
                   "valable le dernier jour du mois", "SUM(mrr)"),
        Indicateur("departs", "Départs du mois", "nombre",
                   "nombre d'abonnements dont la `date_fin` tombe dans le mois", "SUM(depart)"),
        Indicateur("taux_depart", "Taux de départ", "ratio",
                   "départs du mois / abonnés actifs en début de mois (sur plusieurs mois : somme des départs / "
                   "somme des actifs de début de mois)", "ROUND(1.0 * SUM(depart) / NULLIF(SUM(actif_debut), 0), 6)",
                   tolerance=0.0001),
        Indicateur("actifs_debut_mois", "Abonnés actifs début de mois", "nombre",
                   "abonnements actifs le dernier jour du mois précédent (`actif_debut` = 1)", "SUM(actif_debut)",
                   principal=False),
        Indicateur("nouveaux", "Nouveaux abonnements", "nombre", "abonnements dont la `date_debut` tombe dans le mois",
                   "SUM(nouveau)", principal=False),
        Indicateur("facture_millimes", "Montant facturé", "millimes",
                   "somme des montants des factures acceptées, rangées dans le mois de leur date de facture",
                   "SUM(facture)", principal=False),
    ],
    vue_analyse=VUE,
    axes={"par_mois": "mois", "par_gamme": "gamme", "par_offre": "offre_id", "par_type_compte": "type_compte",
          "par_ville": "ville", "par_mois_gamme": "mois || ' · ' || gamme"},
    scd2=SCD2("dim_offre", "offre_key", "offre_id", "gamme",
              faits=[("fact_facture", "offre_key", "date_key"), ("fact_abonnement_mois", "offre_key", "date_key")],
              frontieres=[("FN-F300", "2026-06-30"), ("FN-F300", "2026-07-14"), ("FN-F300", "2026-07-15"),
                          ("FN-F100", "2026-07-15")],
              changement="L'offre FN-F300 (Fibre 300) passe de la gamme « confort » à 89,900 TND à la gamme « pro » à "
                         "99,900 TND le 2026-07-15 (inclus). Cette information arrive avec `lot2/offres.json`."),
    regles=[
        ("Doublon exact", "la même facture deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`F26-900002` deux fois avec des `nb_mois` différents",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`facture_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "offre `FN-TV`, compte `C0999`, abonnement `AB09999` ; abonnement SQLite vers un compte inconnu",
         "rejet `cle_inconnue`"),
        ("Format décimal", "`69.900`, `69,900`, `69.9`, `69,9`, `149,000`",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers"),
        ("Format date", "`2026-03-01`, `01/03/2026`, `1 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` c0042`, `fn-f100`, ` Entreprise `",
         "codes : espaces autour supprimés + majuscules ; type de compte et gamme : + minuscules"),
        ("nb_mois invalide", "`-2`, `0`, `1.5`, `2,5`", "rejet `quantite_invalide`"),
        ("Encodage", "`Déco`, `Hôtel`, `Médina` dans les noms", "lire les fichiers en UTF-8"),
        ("Abonnement annulé", "`statut = 'ANNULE'`", "ignorer (jamais installé : ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie les factures émises depuis le 10 juin", "ignorer : la clé métier existe déjà"),
    ],
    motifs={**MOTIFS_STANDARD,
            "cle_inconnue": "compte, offre ou abonnement absent du référentiel",
            "quantite_invalide": "nb_mois nul, négatif ou non entier"},
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`facture_id` vide → `id_manquant` ;",
        "`facture_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "compte absent de `comptes.xlsx`, offre absente de `offres.json` ou abonnement absent des abonnements acceptés "
        "→ `cle_inconnue` ;",
        "`nb_mois` non entier ou ≤ 0 → `quantite_invalide` ;",
        "`facture_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Abonnements (lus **avant** les factures) : `ANNULE` ignoré → `num_compte` absent de `dim_compte` = "
        "`cle_inconnue` (numero_ligne = `abonnement.id`) → ligne-mois déjà chargée = ignorée.",
    ],
    regles_metier=[
        "Une facture est émise pour **chaque mois entamé** : le 1er du mois, ou le jour de début pour le premier mois. "
        "Montant = `nb_mois` × prix de la version de l'offre valable à la date de facture.",
        "`fact_facture` : version de l'offre valable à la **date de la facture** (la facture de juillet de Fibre 300, "
        "émise le 1er juillet, reste en confort à 89,900 TND).",
        "`fact_abonnement_mois` est **dérivée** de la base des abonnements (dates de début et de fin), pas du CSV : "
        "une ligne par abonnement et par mois où il est actif au moins un jour, rattachée au **dernier jour du mois** "
        "(`date_key`) et à la version de l'offre valable ce jour-là. Voir § 13.",
        "`date_fin` = dernier jour de service (inclus). Un abonnement résilié le dernier jour du mois est un départ "
        "de ce mois et n'est **pas** actif en fin de mois (voir la règle à clarifier).",
        "`type_compte` ∈ {`particulier`, `entreprise`} et `gamme` ∈ {`essentiel`, `confort`, `pro`} : en minuscules.",
        "Abonnés et MRR sont des stocks de fin de mois : on les lit **mois par mois** (agrégat `par_mois`). La somme "
        "sur plusieurs mois (total de la référence) compte des abonnés-mois, pas des abonnés.",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, "
        "243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": ("Un abonnement résilié le 31 mars (dernier jour du mois) est-il encore actif « fin mars » ? Et le "
                     "MRR de juillet d'un abonné Fibre 300 se calcule-t-il à 89,900 TND (prix à la souscription ou à "
                     "la facture du 1er juillet) ou à 99,900 TND (prix valable le 31 juillet) ?"),
        "options": ("- A : actif fin mars (il est servi le 31) ; MRR au prix de la souscription.\n"
                    "- B : départ de mars, plus actif fin mars ; MRR au prix de la version valable le dernier jour "
                    "du mois.\n- C : actif fin mars, départ compté en avril ; MRR au prix de la dernière facture."),
        "decision": ("B. `date_fin` = dernier jour de service ; actif fin de mois ⇔ `date_fin` vide ou **après** le "
                     "dernier jour du mois. Le MRR d'un mois utilise la version de l'offre valable le dernier jour de "
                     "ce mois : Fibre 300 compte 99,900 TND dans le MRR de juillet alors que sa facture de juillet "
                     "(émise le 1er) vaut 89,900 TND."),
    },
    variantes=[
        "Nouvel indicateur : revenu moyen par abonné (ARPU) = MRR / abonnés actifs fin de mois, par gamme.",
        "Nouvelle règle : un abonnement résilié moins de 60 jours après son début est un « départ précoce » → "
        "colonne `depart_precoce` dans `fact_abonnement_mois` et indicateur dédié.",
        "Changement historique : l'offre FN-F20 baisse à 34,900 TND le 2026-08-01 (deuxième version dans `dim_offre`, "
        "MRR d'août recalculé, factures de juillet inchangées).",
    ],
    ecrans_app=[
        ("Vue direction", "abonnés actifs et MRR à la fin de la période choisie, départs et taux de départ, MRR par "
                          "mois et par gamme (barres empilées) et le tableau mois par mois actifs début + nouveaux − "
                          "départs = actifs fin."),
        ("Détail par offre", "chaque offre avec ses versions : FN-F300 en confort à 89,900 TND jusqu'au 2026-07-14, "
                             "puis pro à 99,900 TND ; actifs, départs et MRR mois par mois."),
        ("Qualité des données", "factures lues, gardées, déjà chargées, rejetées par motif ; abonnements annulés et "
                                "rejetés, par lot."),
    ],
    textes_app=["Vue direction", "Détail par offre", "Qualité des données"],
    export_sommes={"fact_facture": ["nb_mois", "montant_millimes"],
                   "fact_abonnement_mois": ["actif_debut", "actif_fin", "nouveau", "depart", "mensualite_millimes"],
                   "dim_offre": ["prix_mensuel_millimes"]},
    visuels=[
        {"type": "empile", "indicateur": "mrr_millimes", "x": "mois", "serie": "gamme",
         "ordre_series": ["essentiel", "confort", "pro"], "fichier": "mrr_par_mois_et_gamme",
         "titre": "MRR par mois et par gamme (prix valable en fin de mois)", "libelle_x": "Mois", "libelle_serie": "Gamme"},
        {"type": "barres", "indicateurs": ["actifs_fin_mois"], "axe": "mois", "fichier": "actifs_fin_de_mois",
         "titre": "Abonnés actifs en fin de mois", "libelle_x": "Mois"},
        {"type": "barres", "indicateurs": ["nouveaux", "departs"], "axe": "mois", "fichier": "nouveaux_et_departs_par_mois",
         "titre": "Nouveaux abonnements et départs par mois", "libelle_x": "Mois", "libelle_y": "Abonnements"},
        {"type": "barres", "indicateurs": ["taux_depart"], "axe": "mois", "fichier": "taux_depart_par_mois",
         "titre": "Taux de départ par mois", "libelle_x": "Mois"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"factures": "facturation.csv", "abonnements": "abonnements.sqlite"},
    parcours_app="Démonstration conseillée : (1) Vue direction sur toute la période (abonnés et MRR lus au dernier mois "
                 "choisi), puis filtre « type de compte = entreprise » ; (2) Détail par offre sur FN-F300 : juin en "
                 "confort, août en pro, MRR d'août au nouveau prix ; (3) Qualité des données : rejets du lot 1 et du "
                 "lot 2, factures déjà chargées au rejeu (une ligne « lot2 (rejeu) » à 0 ajout).",
)
