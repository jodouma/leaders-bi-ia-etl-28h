"""Textes et règles de la mission M10 (Pixel Studio, agence numérique). Séparés du code pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, d.date_complete AS jour, p.projet_id, p.client,
       p.type_projet, p.chef_projet,
       t.heures_centiemes AS heures, t.cout_charge_millimes AS cout, 0 AS facture, 0 AS avoir
FROM fact_temps t
JOIN dim_date d ON d.date_key = t.date_key
JOIN dim_projet p ON p.projet_key = t.projet_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), d.date_complete, p.projet_id, p.client, p.type_projet, p.chef_projet,
       0, 0, CASE WHEN f.signe = 1 THEN f.montant_ht_millimes ELSE 0 END,
       CASE WHEN f.signe = -1 THEN f.montant_ht_millimes ELSE 0 END
FROM fact_facture f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_projet p ON p.projet_key = f.projet_key
"""

SPEC_TEXTES = dict(
    code="M10",
    numero="10",
    titre="Agence numérique",
    entreprise="Pixel Studio",
    secteur="agence numérique de 15 personnes : sites web, applications, campagnes",
    contexte=("Pixel Studio réalise des sites web, des applications et des campagnes pour une vingtaine de "
              "clients. Chaque collaborateur saisit ses heures dans une feuille de temps (CSV). Le coût d'une "
              "heure dépend du profil (développeur, designer, chef de projet, consultant) : il est dans un "
              "classeur Excel. La liste des projets (client, type forfait ou régie, chef de projet) est dans un "
              "fichier JSON. Les factures et les avoirs sortent du logiciel de facturation, une petite base "
              "SQLite. Personne ne sait dire quels projets consomment du temps sans rapporter assez. "
              "Solen Digital vous confie la mission. Les heures sont stockées en **centièmes d'heure entiers** "
              "(7,5 h = 750) et les montants en millimes entiers."),
    demande=("Bonjour à tous les deux,\n\nNous travaillons beaucoup, mais je ne sais pas quels projets nous "
             "rapportent vraiment. Je veux, par projet, par client, par chef de projet et par mois : les heures, "
             "le coût de charge (heures × taux horaire du profil), le facturé net (factures − avoirs) et la "
             "marge de contribution. Je sais que ce n'est pas notre bénéfice : les loyers et les frais généraux "
             "ne sont pas dedans. Dites-moi aussi quelles lignes vous avez écartées, et pourquoi.\n\n"
             "Pour information : à partir du 15 juillet, le projet « Portail patients » (PX07) passe de Hela "
             "Mansour à Nour Jebali. Les heures du premier semestre restent à Hela.\n\n"
             "Lamia Ben Salah, directrice (Solen Digital, pour le compte de Pixel Studio)"),
    grain="une ligne de temps (un collaborateur, un projet, un jour, une tâche, des heures)",
    sources=[
        Source("temps.csv", "csv", "Feuilles de temps exportées de l'outil de saisie (UTF-8, séparateur `;`).", [
            ColonneSource("temps_id", "texte", "Identifiant de la ligne de temps.", "T26-00412"),
            ColonneSource("date_travail", "texte", "Jour travaillé, trois formats possibles.", "04/03/2026"),
            ColonneSource("collaborateur", "texte", "Code du collaborateur (casse et espaces variables).", " c05 "),
            ColonneSource("profil", "texte", "Profil affiché dans l'outil de saisie (information seulement).",
                          "développeur"),
            ColonneSource("projet", "texte", "Code du projet.", "PX07"),
            ColonneSource("heures", "texte", "Heures travaillées, point ou virgule décimale.", "7,5"),
            ColonneSource("tache", "texte", "Tâche réalisée (avec accents).", "réunion client"),
        ], ["heures `7,5` / `7.5` / `7.50`", "dates en trois formats", "doublons",
            "identifiants vides ou en conflit", "codes inconnus", "heures nulles ou négatives",
            "lot2 : recopie de lignes de fin juin"]),
        Source("couts.xlsx", "excel", "Feuille `Profils` (en-têtes à la ligne 3) + feuille `Collaborateurs`.", [
            ColonneSource("Profil", "texte", "Profil (feuille Profils).", "Chef de projet"),
            ColonneSource("Taux horaire coût (TND)", "nombre ou texte", "Coût d'une heure du profil.", "41,000"),
            ColonneSource("Code", "texte", "Code collaborateur (feuille Collaborateurs).", "C03"),
            ColonneSource("Nom", "texte", "Nom et prénom (fictifs).", "Hela Mansour"),
            ColonneSource("Profil (Collaborateurs)", "texte", "Profil du collaborateur, casse variable.",
                          "DÉVELOPPEUR"),
        ], ["titre au-dessus du tableau", "nombres stockés comme texte", "profils en casse variable"]),
        Source("projets.json", "json", "Référentiel des projets avec l'historique des chefs de projet.", [
            ColonneSource("projets[].code", "texte", "Code projet.", "PX07"),
            ColonneSource("projets[].nom", "texte", "Nom du projet.", "Portail patients"),
            ColonneSource("projets[].client", "texte", "Client (fictif).", "Clinique Les Jasmins Bleus"),
            ColonneSource("projets[].type", "texte", "`forfait`, `régie` ou `interne` (casse variable).", "Régie"),
            ColonneSource("projets[].date_debut", "date ISO", "Début du projet.", "2026-01-12"),
            ColonneSource("projets[].historique[].chef_projet", "texte", "Chef de projet.", "Hela Mansour"),
            ColonneSource("projets[].historique[].valide_depuis", "date ISO", "Début de ce chef (inclus).",
                          "2026-01-12"),
        ], ["lot2 : une deuxième version pour PX07 (Nour Jebali au 2026-07-15)", "un projet interne non facturable"]),
        Source("facturation.sqlite", "sqlite", "Base de facturation : tables `facture`, `avoir`, `parametre`.", [
            ColonneSource("facture.id", "entier", "Numéro interne de la ligne.", "12"),
            ColonneSource("facture.facture_id", "texte", "Numéro de facture (unique).", "F26-0012"),
            ColonneSource("facture.code_projet", "texte", "Projet facturé.", "PX04"),
            ColonneSource("facture.date_facture", "texte", "Date de la facture.", "2026-02-28"),
            ColonneSource("facture.montant_ht", "réel", "Montant hors taxes en TND.", "5236.5"),
            ColonneSource("facture.statut", "texte", "`EMISE` ou `ANNULEE`.", "EMISE"),
            ColonneSource("facture.objet", "texte", "Objet de la facture.", "Régie février 2026"),
            ColonneSource("avoir.id", "entier", "Numéro interne de la ligne.", "3"),
            ColonneSource("avoir.avoir_id", "texte", "Numéro d'avoir (unique).", "AV26-003"),
            ColonneSource("avoir.facture_id", "texte", "Facture corrigée par l'avoir.", "F26-0012"),
            ColonneSource("avoir.date_avoir", "texte", "Date de l'avoir.", "2026-03-09"),
            ColonneSource("avoir.montant_ht", "réel", "Montant HT de l'avoir en TND (positif).", "500.0"),
            ColonneSource("avoir.motif", "texte", "Raison de l'avoir.", "geste commercial"),
        ], ["factures annulées", "facture vers un projet inconnu", "avoir vers une facture inconnue",
            "lot2 : recopie des documents depuis le 15 juin"]),
    ],
    indicateurs=[
        Indicateur("heures_centiemes", "Heures", "centiemes_heure",
                   "somme des heures des lignes de temps acceptées, en centièmes d'heure (750 = 7,5 h)",
                   "SUM(heures)"),
        Indicateur("cout_charge_millimes", "Coût de charge", "millimes",
                   "somme de heures × taux horaire coût du profil du collaborateur",
                   "SUM(cout)"),
        Indicateur("factures_millimes", "Factures", "millimes",
                   "somme des montants HT des factures EMISE acceptées", "SUM(facture)", principal=False),
        Indicateur("avoirs_millimes", "Avoirs", "millimes",
                   "somme des montants HT des avoirs acceptés", "SUM(avoir)", principal=False),
        Indicateur("facture_net_millimes", "Facturé net", "millimes",
                   "factures − avoirs (montants HT)", "SUM(facture) - SUM(avoir)"),
        Indicateur("marge_contribution_millimes", "Marge de contribution", "millimes",
                   "facturé net − coût de charge (ce n'est PAS un bénéfice : aucun frais général)",
                   "SUM(facture) - SUM(avoir) - SUM(cout)"),
    ],
    vue_analyse=VUE,
    axes={"par_projet": "projet_id", "par_client": "client", "par_type": "type_projet",
          "par_chef_projet": "chef_projet", "par_mois": "mois"},
    scd2=SCD2("dim_projet", "projet_key", "projet_id", "chef_projet",
              faits=[("fact_temps", "projet_key", "date_key"), ("fact_facture", "projet_key", "date_key")],
              frontieres=[("PX07", "2026-06-30"), ("PX07", "2026-07-14"), ("PX07", "2026-07-15"),
                          ("PX02", "2026-07-15")],
              changement="Le projet PX07 (Portail patients) passe de la cheffe de projet « Hela Mansour » à "
                         "« Nour Jebali » le 2026-07-15 (inclus). Cette information arrive avec "
                         "`lot2/projets.json`."),
    regles=[
        ("Doublon exact", "la même ligne de temps deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`T26-90001` deux fois avec des heures différentes",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`temps_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "collaborateur `C99`, projet `PX99`, avoir vers `F26-0999`", "rejet `cle_inconnue`"),
        ("Format des heures", "`7.5`, `7,5`, `7.50`, `8,0`",
         "point ou virgule = décimales ; convertir en centièmes d'heure entiers (7,5 h → 750)"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` c05 `, `Px07`, `DÉVELOPPEUR`, `Régie`",
         "codes : espaces autour supprimés + majuscules ; profils et types : espaces supprimés + minuscules"),
        ("Heures invalides", "`-2`, `0`, `-7,5`, `0,0`", "rejet `quantite_invalide`"),
        ("Montants Excel", "`41,000`, `32.5`", "point ou virgule = décimales ; millimes entiers"),
        ("Encodage", "`réunion client`, `développeur`", "lire les fichiers en UTF-8"),
        ("Facture annulée", "`statut = 'ANNULEE'`", "ignorer (ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie des lignes de temps de fin juin et les documents depuis le 15 juin",
         "ignorer : la clé métier existe déjà"),
    ],
    motifs=dict(MOTIFS_STANDARD,
                cle_inconnue="code absent du référentiel (collaborateur, projet, facture d'origine d'un avoir)",
                quantite_invalide="heures nulles, négatives ou illisibles"),
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`temps_id` vide → `id_manquant` ;",
        "`temps_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "collaborateur ou projet absent des référentiels → `cle_inconnue` ;",
        "heures illisibles, nulles ou négatives → `quantite_invalide` ;",
        "`temps_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Factures : `ANNULEE` ignorée → `facture_id` déjà chargé = ignoré → `code_projet` inconnu = `cle_inconnue` "
        "(numero_ligne = `facture.id`). Avoirs (après les factures) : `avoir_id` déjà chargé = ignoré → "
        "`facture_id` absent de `fact_facture` = `cle_inconnue` (numero_ligne = `avoir.id`).",
    ],
    regles_metier=[
        "Heures : stockées en **centièmes d'heure entiers** dans `heures_centiemes` (7,5 h → 750 ; 1,25 h → 125). "
        "Au plus deux décimales dans la source.",
        "Taux horaire coût = taux du **profil** du collaborateur (`couts.xlsx`, feuille Collaborateurs puis Profils), "
        "fixe sur 2026. La colonne `profil` du CSV n'est qu'une information : le référentiel gagne.",
        "`cout_charge_millimes` = `heures_centiemes` × `taux_horaire_millimes` / 100. Le résultat est un entier exact "
        "(tous les taux sont des multiples de 0,100 TND).",
        "Une facture `EMISE` → une ligne de `fact_facture` : `type_document` = `facture`, `signe` = +1. "
        "Un avoir → `type_document` = `avoir`, `signe` = −1, projet de sa facture d'origine, **date de l'avoir**.",
        "`montant_ht_millimes` est toujours positif : c'est `signe` qui dit s'il ajoute ou retire.",
        "Chaque fait (heure, facture, avoir) est rattaché à la version du projet valable à **sa propre date**.",
        "Le projet `INT01` (type `interne` : formation, avant-vente) n'est jamais facturé : ses heures **comptent** "
        "dans le coût de charge et sa marge de contribution est négative.",
        "Marge de contribution = facturé net − coût de charge. Ce n'est **pas** un bénéfice : loyers, logiciels, "
        "heures non saisies et frais généraux n'y sont pas.",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le "
        "lot 1, 243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": ("(1) Les heures saisies sur PX07 avant le 15 juillet, et la facture de régie de juillet "
                     "datée du 31 juillet : quel chef de projet ? (2) Les heures passées sur le projet interne "
                     "INT01 (non facturable) comptent-elles dans le coût de charge ?"),
        "options": ("- (1) A : le chef courant pour tout le projet (on réécrit l'historique).\n"
                    "- (1) B : le chef valable le jour de la ligne de temps (ou de la facture).\n"
                    "- (2) A : oui, toute heure saisie coûte, facturable ou non.\n"
                    "- (2) B : non, on n'analyse que les projets clients."),
        "decision": ("(1) B : chaque heure, facture ou avoir prend la version de PX07 valable à SA date : les "
                     "heures jusqu'au 14 juillet restent à Hela Mansour, la facture du 31 juillet (qui couvre "
                     "tout juillet) va à Nour Jebali. (2) A : les heures de INT01 comptent dans le coût de charge "
                     "global ; INT01 apparaît comme un projet de type `interne` avec un facturé net nul."),
    },
    variantes=[
        "Nouvel indicateur : taux de facturabilité = heures des projets forfait ou régie / heures totales.",
        "Nouvelle règle : une ligne de plus de 12 heures est refusée → nouveau motif `heures_hors_bornes`.",
        "Changement historique : le taux horaire coût des développeurs passe de 32,500 à 34,000 TND le "
        "2026-08-01 (le coût d'une heure dépend de sa date : historiser les taux).",
    ],
    ecrans_app=[
        ("Vue direction", "factures, avoirs, facturé net, coût de charge et marge de contribution ; coût de charge "
                          "par mois et par type de projet (barres empilées)."),
        ("Détail par projet", "chaque projet avec ses versions : PX07 chez Hela Mansour jusqu'au 2026-07-14, puis "
                              "Nour Jebali ; les projets à marge négative se repèrent ici."),
        ("Qualité des données", "lignes lues, gardées, rejetées par motif et par lot."),
    ],
    textes_app=["Vue direction", "Détail par projet", "Qualité des données"],
    export_sommes={"fact_temps": ["heures_centiemes", "cout_charge_millimes"],
                   "fact_facture": ["signe", "montant_ht_millimes"],
                   "dim_collaborateur": ["taux_horaire_millimes"]},
    visuels=[
        {"type": "empile", "indicateur": "cout_charge_millimes", "x": "mois", "serie": "type_projet",
         "ordre_series": ["forfait", "régie", "interne"], "fichier": "cout_charge_par_mois_et_type",
         "titre": "Coût de charge par mois et par type de projet", "libelle_x": "Mois",
         "libelle_serie": "Type de projet"},
        {"type": "barres", "indicateurs": ["marge_contribution_millimes"], "axe": "projet_id", "horizontal": True,
         "fichier": "marge_contribution_par_projet", "titre": "Marge de contribution par projet (orange : négative)",
         "libelle_x": "Projet", "libelle_y": "Marge de contribution"},
        {"type": "barres", "indicateurs": ["facture_net_millimes", "cout_charge_millimes",
                                           "marge_contribution_millimes"], "axe": "type_projet",
         "fichier": "facture_cout_marge_par_type", "titre": "Facturé net, coût de charge et marge par type de projet",
         "libelle_x": "Type de projet", "libelle_y": "Montant"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"temps": "temps.csv", "documents": "facturation.sqlite"},
)
