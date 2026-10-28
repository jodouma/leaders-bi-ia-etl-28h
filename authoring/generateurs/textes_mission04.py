"""Textes et règles de la mission M04 (Colis Rapide). Séparés du code de génération pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, d.date_complete AS jour,
       a.agence_id, a.zone, t.zone_destination, t.tranche, s.service_id,
       1 AS nb, f.a_l_heure AS a_l_heure, f.retard_jours AS retard,
       f.montant_facture_millimes AS facture, f.penalite_millimes AS penalite,
       f.cout_transporteur_millimes AS cout
FROM fact_colis f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_agence a ON a.agence_key = f.agence_key
JOIN dim_service s ON s.service_key = f.service_key
JOIN dim_tarif t ON t.tarif_key = f.tarif_key
"""

MOTIFS = dict(MOTIFS_STANDARD)
MOTIFS["quantite_invalide"] = ("poids nul, négatif, illisible ou supérieur à 30 kg (le poids joue ici le rôle "
                               "de la quantité)")
MOTIFS["cle_inconnue"] = "code absent du référentiel (agence, service, zone) ou facture / pénalité vers un colis inconnu"

SPEC_TEXTES = dict(
    code="M04",
    numero="04",
    titre="Livraison",
    entreprise="Colis Rapide",
    secteur="transporteur de colis : 7 agences, 4 zones de livraison, 3 services (Standard, Express, Économique)",
    contexte=("Colis Rapide livre des colis partout en Tunisie depuis sept agences. Chaque agence est rattachée à "
              "une zone (Grand Tunis, Nord, Centre-Sahel, Sud). Le suivi des colis sort dans un CSV, la grille des "
              "tarifs vit dans un classeur Excel, la liste des agences dans un fichier JSON et la facturation "
              "(factures et pénalités de retard) dans une base SQLite. Les clients se plaignent des retards, et "
              "personne ne sait dire où l'on perd de l'argent. Solen Digital vous confie la mission."),
    demande=("Bonjour à tous les deux,\n\nNos clients disent que nous livrons en retard, et nos pénalités "
             "augmentent. Je veux savoir où se concentrent les retards et les coûts : par agence, par zone, par "
             "service, par tranche de poids et par mois. Donnez-moi la ponctualité, le retard moyen, le revenu "
             "facturé net des pénalités, le coût transporteur et la marge de livraison. Dites-moi aussi quels colis "
             "vous avez dû écarter, et pourquoi.\n\nPour information : à partir du 15 juillet, l'agence de Nabeul "
             "quitte la zone Nord et rejoint la zone Centre-Sahel. Les chiffres du premier semestre doivent rester "
             "dans la zone Nord.\n\nLamia Ben Salah, directrice (Solen Digital, pour le compte de Colis Rapide)"),
    grain="un colis livré",
    sources=[
        Source("colis.csv", "csv", "Suivi des colis livrés exporté du logiciel des agences (UTF-8, séparateur `;`).", [
            ColonneSource("colis_id", "texte", "Numéro du colis (clé métier).", "CR100234"),
            ColonneSource("date_expedition", "texte", "Jour où l'agence a pris le colis, trois formats possibles.", "02/03/2026"),
            ColonneSource("date_promise", "texte", "Jour de livraison promis au client.", "5 mars 2026"),
            ColonneSource("date_livraison", "texte", "Jour où le colis a été livré (date du fait).", "2026-03-06"),
            ColonneSource("agence", "texte", "Code de l'agence qui a expédié le colis (casse et espaces variables).", " nab "),
            ColonneSource("zone_destination", "texte", "Code de la zone de destination (sert au tarif).", "SU"),
            ColonneSource("poids_kg", "texte", "Poids en kg, formats décimaux variés.", "2,35"),
            ColonneSource("service", "texte", "Code du service : STD, EXP ou ECO.", "EXP"),
            ColonneSource("ville_destination", "texte", "Ville du destinataire (avec accents).", "Médenine"),
        ], ["formats de poids et de dates mélangés", "doublons", "identifiants vides ou en conflit",
            "agences ou services inconnus", "poids invalides", "lot2 : recopie de colis livrés fin juin"]),
        Source("tarifs.xlsx", "excel", "Feuilles `Grille` (en-têtes à la ligne 3), `Tranches`, `Zones`, `Services`.", [
            ColonneSource("Grille : Zone / Tranche", "texte", "Code zone et code tranche (une cellule mal saisie).", " su / T3"),
            ColonneSource("Grille : Prix facturé (TND)", "nombre ou texte", "Prix catalogue d'un colis Standard.", "19,500"),
            ColonneSource("Grille : Coût transporteur (TND)", "nombre ou texte", "Ce que coûte le transport du colis.", "15.3"),
            ColonneSource("Tranches : Poids min (kg, exclu) / Poids max (kg, inclus)", "nombre", "Bornes de la tranche.", "5 / 10"),
            ColonneSource("Zones : Code zone / Libellé zone", "texte", "Traduction des codes.", "SU / Sud"),
            ColonneSource("Services : Code / Libellé / Délai promis (jours) / Coefficient prix (%)", "texte et nombre",
                          "Les trois services.", "EXP / Express / 1 / 150"),
        ], ["titre au-dessus de la grille", "nombres stockés comme texte"]),
        Source("agences.json", "json", "Référentiel des agences avec l'historique de leur zone de rattachement.", [
            ColonneSource("agences[].code", "texte", "Code agence.", "NAB"),
            ColonneSource("agences[].nom", "texte", "Nom.", "Colis Rapide Nabeul"),
            ColonneSource("agences[].ville", "texte", "Ville de l'agence.", "Nabeul"),
            ColonneSource("agences[].historique[].zone", "texte", "Zone de rattachement.", "Nord"),
            ColonneSource("agences[].historique[].valide_depuis", "date", "Début de la zone (inclus), ISO ou JJ/MM/AAAA.", "2020-09-01"),
        ], ["une date au format JJ/MM/AAAA", "lot2 : une deuxième version pour NAB (Centre-Sahel au 2026-07-15)"]),
        Source("facturation.sqlite", "sqlite", "Base opérationnelle de facturation : tables `facture`, `penalite`, `parametre`.", [
            ColonneSource("facture.id", "entier", "Numéro interne de la ligne.", "57"),
            ColonneSource("facture.numero_facture", "texte", "Numéro de facture (unique).", "FA26-000057"),
            ColonneSource("facture.colis_id", "texte", "Colis facturé.", "CR100234"),
            ColonneSource("facture.date_facture", "texte", "Date et heure de la facture.", "2026-03-07 10:15:00"),
            ColonneSource("facture.montant_facture", "réel", "Montant facturé au client en TND.", "17.25"),
            ColonneSource("facture.statut", "texte", "`EMISE`, `PAYEE` ou `ANNULEE`.", "PAYEE"),
            ColonneSource("penalite.id / numero_penalite", "entier / texte", "Ligne et numéro de la pénalité.", "PE26-00012"),
            ColonneSource("penalite.colis_id", "texte", "Colis livré en retard.", "CR100234"),
            ColonneSource("penalite.jours_retard", "entier", "Jours de retard constatés par la facturation.", "2"),
            ColonneSource("penalite.montant_penalite", "réel", "Pénalité remboursée au client en TND (10 % par jour de retard, 5 jours au plus, rien pour ECO).", "2.8"),
            ColonneSource("penalite.statut", "texte", "`APPLIQUEE` ou `ANNULEE`.", "APPLIQUEE"),
        ], ["factures annulées puis refaites", "pénalités annulées", "factures et pénalités vers un colis inconnu",
            "lot2 : recopie des factures des colis de fin juin"]),
    ],
    indicateurs=[
        Indicateur("colis_livres", "Colis livrés", "nombre", "nombre de colis acceptés dans `fact_colis`", "SUM(nb)"),
        Indicateur("colis_a_l_heure", "Colis à l'heure", "nombre",
                   "colis avec date_livraison ≤ date_promise (livré le jour promis = à l'heure)", "SUM(a_l_heure)",
                   principal=False),
        Indicateur("ponctualite", "Ponctualité", "ratio", "colis à l'heure / colis livrés",
                   "ROUND(1.0 * SUM(a_l_heure) / NULLIF(SUM(nb), 0), 6)", tolerance=0.0001),
        Indicateur("retard_moyen_jours", "Retard moyen", "jours",
                   "somme des jours de retard / nombre de colis EN RETARD (les colis à l'heure ne comptent pas) ; "
                   "jours de retard = date_livraison − date_promise, en jours calendaires",
                   "ROUND(1.0 * SUM(retard) / NULLIF(SUM(nb) - SUM(a_l_heure), 0), 6)", tolerance=0.001),
        Indicateur("montant_facture_millimes", "Montant facturé", "millimes",
                   "somme des montants des factures EMISE ou PAYEE des colis acceptés", "SUM(facture)", principal=False),
        Indicateur("penalites_millimes", "Pénalités de retard", "millimes",
                   "somme des pénalités APPLIQUEE des colis acceptés", "SUM(penalite)", principal=False),
        Indicateur("revenu_net_millimes", "Revenu facturé net de pénalités", "millimes",
                   "montant facturé − pénalités de retard", "SUM(facture) - SUM(penalite)"),
        Indicateur("cout_transporteur_millimes", "Coût transporteur", "millimes",
                   "somme du coût transporteur de la grille (zone de destination × tranche de poids) des colis acceptés",
                   "SUM(cout)"),
        Indicateur("marge_livraison_millimes", "Marge de livraison", "millimes",
                   "revenu facturé net de pénalités − coût transporteur (marge partielle : ni salaires, ni loyers, "
                   "ni carburant des agences ; ce n'est pas un bénéfice)",
                   "SUM(facture) - SUM(penalite) - SUM(cout)"),
    ],
    vue_analyse=VUE,
    axes={"par_zone": "zone", "par_agence": "agence_id", "par_mois": "mois", "par_service": "service_id",
          "par_zone_destination": "zone_destination", "par_tranche": "tranche"},
    scd2=SCD2("dim_agence", "agence_key", "agence_id", "zone",
              faits=[("fact_colis", "agence_key", "date_key")],
              frontieres=[("NAB", "2026-06-30"), ("NAB", "2026-07-14"), ("NAB", "2026-07-15"), ("TUN", "2026-07-15")],
              changement="L'agence NAB (Nabeul) passe de la zone « Nord » à la zone « Centre-Sahel » le 2026-07-15 "
                         "(inclus). Cette information arrive avec `lot2/agences.json`."),
    regles=[
        ("Doublon exact", "la même ligne deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`CR900001` deux fois avec des poids différents",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`colis_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "agence `KAI`, service `PRM`, facture vers `CR777001`", "rejet `cle_inconnue`"),
        ("Format décimal du poids", "`2.350`, `2,350`, `2.35`, `2,35`, `1`",
         "point ou virgule = décimales ; convertir en **grammes entiers** (2,35 kg = 2 350 g)"),
        ("Poids invalide", "`-1,200`, `0`, `45.000` (plus de 30 kg)", "rejet `quantite_invalide`"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` nab `, `Exp`, ` su`", "supprimer les espaces autour + majuscules"),
        ("Encodage", "`Médenine`, `Béja`, `Gabès`", "lire les fichiers en UTF-8"),
        ("Facture annulée", "`statut = 'ANNULEE'`", "ignorer (ce n'est pas un rejet) ; la facture refaite compte"),
        ("Pénalité annulée", "`statut = 'ANNULEE'`", "ignorer (ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie des colis livrés fin juin et leurs factures",
         "ignorer : la clé métier existe déjà"),
    ],
    motifs=MOTIFS,
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`colis_id` vide → `id_manquant` ;",
        "`colis_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "agence, service ou zone de destination absent des référentiels → `cle_inconnue` ;",
        "poids illisible, ≤ 0 ou > 30 kg → `quantite_invalide` ;",
        "`colis_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Facturation : factures `ANNULEE` et pénalités `ANNULEE` ignorées → `colis_id` ni dans `fact_colis` ni parmi les "
        "colis acceptés du lot = `cle_inconnue` (numero_ligne = `id` de la table `facture` ou `penalite`) → facture ou "
        "pénalité d'un colis déjà chargé = ignorée (lot 2 : voir `nettoyage.facturation.sqlite` de la référence).",
    ],
    regles_metier=[
        "Date du fait = **date de livraison** (`date_key` de `fact_colis`) : un colis compte dans le mois où il est livré.",
        "`retard_jours` = date_livraison − date_promise en jours calendaires, **0 si le colis arrive avant ou le jour promis** "
        "(jamais négatif).",
        "`a_l_heure` = 1 si date_livraison ≤ date_promise, sinon 0. Un colis livré **le jour promis** est à l'heure.",
        "Tranche de poids : la borne basse est exclue, la borne haute incluse (1,000 kg → T1 ; 1,010 kg → T2 ; 5,000 kg → T2).",
        "`tarif_id` = code zone de destination + `-` + code tranche (ex. `SU-T3`) ; `zone_destination` = libellé de la "
        "feuille Zones (ex. `Sud`).",
        "`cout_transporteur_millimes` du colis = coût de la grille pour sa zone de destination et sa tranche.",
        "`montant_facture_millimes` = montant de l'unique facture `EMISE` ou `PAYEE` du colis (la base garantit qu'il y en a "
        "exactement une par colis accepté). La remise éventuelle est déjà dedans : ne pas recalculer depuis la grille.",
        "`penalite_millimes` = somme des pénalités `APPLIQUEE` du colis, 0 s'il n'y en a pas.",
        "Poids stocké en **grammes entiers** (`poids_grammes`).",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, "
        "243 après le lot 2). Les dates d'expédition et promises restent du texte ISO dans `fact_colis`.",
    ],
    regle_a_clarifier={
        "question": ("Deux cas posent problème. (1) Un colis livré **le jour même** de la date promise est-il à l'heure ? "
                     "(2) Un colis de l'agence de Nabeul expédié le 13 juillet (zone Nord) et livré le 16 juillet "
                     "(zone Centre-Sahel) : dans quelle zone le compter ?"),
        "options": ("- (1) A : à l'heure (date_livraison ≤ date_promise). B : en retard (il fallait livrer avant).\n"
                    "- (2) A : version de l'agence valable à la date d'**expédition** (Nord). "
                    "B : version valable à la date de **livraison** (Centre-Sahel)."),
        "decision": ("deux décisions distinctes.\n\n"
                     "- Question (1) → **option A** : un colis livré le jour promis est **à l'heure** ; son retard vaut "
                     "0 jour.\n"
                     "- Question (2) → **option B** : le colis est rattaché à la version de l'agence valable à sa "
                     "**date de livraison**, qui est la date du fait (dim_date) ; il compte donc dans Centre-Sahel et "
                     "dans le mois de juillet."),
    },
    variantes=[
        "Nouvel indicateur : taux de pénalité = pénalités / montant facturé, par agence et par service.",
        "Nouvelle règle : le retard se compte en jours ouvrés (samedi et dimanche exclus) ; recalculer `retard_jours`, "
        "`a_l_heure` et la ponctualité.",
        "Changement historique : l'agence BIZ (Bizerte) rejoint la zone « Grand Tunis » le 2026-08-16 "
        "(deuxième version pour BIZ dans `dim_agence`).",
    ],
    ecrans_app=[
        ("Vue direction", "ponctualité, revenu facturé net, pénalités, coût transporteur et marge de livraison ; "
                          "revenu net par mois et par zone d'agence (barres empilées) ; filtres période, agence, zone, service."),
        ("Détail par agence", "chaque agence avec ses versions : NAB en zone Nord jusqu'au 2026-07-14, puis Centre-Sahel ; "
                              "indicateurs par version et par mois."),
        ("Qualité des données", "lignes rejetées par motif, par source et par lot."),
    ],
    textes_app=["Vue direction", "Détail par agence", "Qualité des données"],
    export_sommes={"fact_colis": ["poids_grammes", "retard_jours", "a_l_heure", "montant_facture_millimes",
                                  "penalite_millimes", "cout_transporteur_millimes"],
                   "dim_tarif": ["prix_millimes", "cout_transporteur_millimes"]},
    visuels=[
        {"type": "empile", "indicateur": "revenu_net_millimes", "x": "mois", "serie": "zone",
         "ordre_series": ["Grand Tunis", "Nord", "Centre-Sahel", "Sud"], "fichier": "revenu_net_par_mois_et_zone",
         "titre": "Revenu facturé net de pénalités par mois et par zone d'agence", "libelle_x": "Mois",
         "libelle_serie": "Zone"},
        {"type": "barres", "indicateurs": ["ponctualite"], "axe": "agence_id", "fichier": "ponctualite_par_agence",
         "titre": "Ponctualité par agence", "libelle_x": "Agence"},
        {"type": "barres", "indicateurs": ["revenu_net_millimes", "cout_transporteur_millimes", "marge_livraison_millimes"],
         "axe": "tranche", "fichier": "revenu_cout_marge_par_tranche",
         "titre": "Revenu net, coût transporteur et marge de livraison par tranche de poids",
         "libelle_x": "Tranche de poids", "libelle_y": "Montant"},
        {"type": "barres", "indicateurs": ["retard_moyen_jours"], "axe": "agence_id", "fichier": "retard_moyen_par_agence",
         "titre": "Retard moyen des colis en retard, par agence", "libelle_x": "Agence"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"colis": "colis.csv", "facturation": "facturation.sqlite"},
    regle_mois="(une ligne par colis livré). Un colis est rangé dans le mois **de sa date de livraison**.",
    parcours_app="Démonstration conseillée (5 minutes) : écran 1 sans filtre (ponctualité, retard moyen en jours et "
                 "montants) → filtre zone « Sud » (où se concentrent retards et coûts) → écran 2, agence NAB (deux "
                 "versions, chiffres de juillet répartis entre Nord et Centre-Sahel) → écran 3 (rejets par motif et "
                 "par lot, puis une ligne par chargement : lot 1, lot 2 et le rejeu à 0 ajout).",
)
SPEC_TEXTES["regle_a_clarifier"]["consequence"] = (
    "Exemple : le colis de Nabeul expédié le 2026-07-13 et livré le 2026-07-16 (date promise 2026-07-16) est "
    "**à l'heure** et compte dans la zone **Centre-Sahel**, mois 2026-07.")
