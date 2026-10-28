"""Textes et règles de la mission M03 (Medina Distribution). Séparés du code de génération pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

# Une ligne par mouvement : les lignes de facture, puis les avoirs.
# Un avoir prend la version du client de SA LIGNE DE FACTURE (client_key recopiée de la facture),
# mais il est rangé dans le mois de SA propre date (date_key = date de l'avoir).
VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, d.date_complete AS jour, c.client_id, c.segment, c.region,
       p.produit_id, p.famille,
       f.montant_facture_millimes AS facture, 0 AS avoir,
       f.quantite * p.cout_achat_millimes AS cout_facture, 0 AS cout_avoir,
       f.quantite AS unites_facturees, 0 AS unites_retournees
FROM fact_facture f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_client c ON c.client_key = f.client_key
JOIN dim_produit p ON p.produit_key = f.produit_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), d.date_complete, c.client_id, c.segment, c.region,
       p.produit_id, p.famille,
       0, a.montant_millimes, 0, a.quantite * p.cout_achat_millimes, 0, a.quantite
FROM fact_avoir a
JOIN dim_date d ON d.date_key = a.date_key
JOIN dim_client c ON c.client_key = a.client_key
JOIN dim_produit p ON p.produit_key = a.produit_key
"""

SPEC_TEXTES = dict(
    code="M03",
    numero="03",
    titre="Distribution B2B",
    entreprise="Medina Distribution",
    secteur="grossiste en produits alimentaires et d'entretien qui livre des épiceries, des restaurants, "
            "des grandes surfaces et des hôtels",
    contexte=("Medina Distribution achète des cartons de semoule, de pâtes, d'huile, de conserves, de boissons, de "
              "produits laitiers et d'entretien, puis les revend à une dizaine de clients professionnels. Chaque "
              "client a un prix négocié, souvent plus bas que le prix tarif. Quand un produit arrive abîmé, trop "
              "près de sa date limite ou avec une erreur de prix, le service commercial émet un **avoir** (une "
              "facture négative). Les lignes de facture sortent du logiciel de facturation dans un CSV, les coûts "
              "d'achat et les prix tarif sont dans un classeur Excel, le fichier clients (segment, région) est un "
              "JSON et les avoirs sont dans la base SQLite de la gestion commerciale. Le chiffre d'affaires monte, "
              "mais personne ne sait quels clients et quels produits rapportent vraiment. Solen Digital vous "
              "confie la mission."),
    demande=("Bonjour à tous les deux,\n\nNotre chiffre d'affaires progresse, mais la marge ne suit pas. Je veux "
             "savoir **quels clients et quels produits font baisser notre rentabilité commerciale**. Par client, "
             "par segment, par produit et par mois : le montant facturé, les avoirs, les ventes nettes, le coût "
             "d'achat des unités nettes, la marge commerciale et le taux d'avoir. Dites-moi aussi quelles lignes "
             "vous avez écartées, et pourquoi.\n\nPour information : à partir du 15 juillet, la Supérette El Amel "
             "(CL04) passe du segment « épicerie » au segment « grande surface ». Ses factures du premier "
             "semestre doivent rester dans « épicerie ».\n\n"
             "Lamia Ben Salah, directrice (Solen Digital, pour le compte de Medina Distribution)"),
    grain="une ligne de facture",
    sources=[
        Source("factures.csv", "csv", "Lignes de facture exportées du logiciel de facturation (UTF-8, séparateur `;`).", [
            ColonneSource("facture_id", "texte", "Numéro de la facture.", "F26-01234"),
            ColonneSource("ligne_id", "texte", "Identifiant de la ligne : facture + numéro de ligne (clé métier).",
                          "F26-01234-3"),
            ColonneSource("date_facture", "texte", "Date de la facture, trois formats possibles.", "04/03/2026"),
            ColonneSource("client", "texte", "Code client (casse et espaces variables).", " cl05 "),
            ColonneSource("produit", "texte", "Code article du fichier des coûts.", "PR03"),
            ColonneSource("quantite", "texte", "Nombre de cartons (ou packs) facturés.", "12"),
            ColonneSource("prix_unitaire_negocie", "texte", "Prix négocié d'un carton en TND, formats variés.", "18,280"),
            ColonneSource("commercial", "texte", "Prénom du commercial (avec accents).", "Sélima"),
        ], ["formats de prix et de dates mélangés", "doublons", "identifiants vides ou en conflit",
            "codes inconnus", "quantités invalides", "lot2 : recopie des dernières factures du 30 juin"]),
        Source("couts.xlsx", "excel", "Feuille `Articles` (en-têtes à la ligne 3) + feuille `Familles`.", [
            ColonneSource("Code article", "texte", "Code produit (une cellule mal saisie).", " pr07"),
            ColonneSource("Désignation", "texte", "Nom et conditionnement.", "Huile végétale — bidon 5 L"),
            ColonneSource("Famille", "texte", "Code famille, à traduire avec la feuille Familles.", "EPI"),
            ColonneSource("Coût d'achat (TND)", "nombre ou texte", "Coût d'achat d'un carton.", "19,600"),
            ColonneSource("Prix tarif (TND)", "nombre ou texte", "Prix catalogue avant négociation.", "21.5"),
            ColonneSource("Code famille / Libellé famille", "texte", "Feuille Familles.", "LAI / Produits laitiers"),
        ], ["titre au-dessus du tableau", "nombres stockés comme texte"]),
        Source("clients.json", "json", "Fichier clients avec l'historique des segments.", [
            ColonneSource("clients[].code", "texte", "Code client.", "CL04"),
            ColonneSource("clients[].raison_sociale", "texte", "Nom du client.", "Supérette El Amel"),
            ColonneSource("clients[].region", "texte", "Région de livraison.", "Cap Bon"),
            ColonneSource("clients[].historique[].segment", "texte",
                          "Segment : épicerie, restaurant, grande surface ou hôtel (casse variable).", "Grande Surface"),
            ColonneSource("clients[].historique[].valide_depuis", "date ISO", "Début du segment (inclus).", "2023-02-01"),
        ], ["segments écrits avec des majuscules ou des espaces",
            "lot2 : une deuxième version pour CL04 (« grande surface » au 2026-07-15)"]),
        Source("avoirs.sqlite", "sqlite", "Base de la gestion commerciale : tables `avoir`, `motif_avoir`, `parametre`.", [
            ColonneSource("avoir.id", "entier", "Numéro interne de la ligne.", "41"),
            ColonneSource("avoir.numero_avoir", "texte", "Numéro de l'avoir (unique).", "AV26-00041"),
            ColonneSource("avoir.ref_ligne_facture", "texte", "`ligne_id` de la ligne de facture corrigée.", "F26-01234-3"),
            ColonneSource("avoir.code_client", "texte", "Client (information ; le client fait foi par la facture).", "CL02"),
            ColonneSource("avoir.date_avoir", "texte", "Date d'émission de l'avoir.", "2026-03-10"),
            ColonneSource("avoir.type_avoir", "texte", "`RETOUR` (cartons repris) ou `REMISE` (geste sur le prix, 0 carton).",
                          "RETOUR"),
            ColonneSource("avoir.qte_retournee", "entier", "Cartons repris (0 pour une REMISE).", "2"),
            ColonneSource("avoir.montant_ht", "réel", "Montant de l'avoir en TND.", "16.9"),
            ColonneSource("avoir.code_motif", "texte", "Motif → `motif_avoir`.", "DLC"),
            ColonneSource("avoir.statut", "texte", "`EMIS`, `ANNULE` ou `BROUILLON`.", "EMIS"),
            ColonneSource("avoir.saisi_par", "texte", "Poste de saisie.", "adv-2"),
        ], ["avoirs annulés ou en brouillon", "avoirs vers une ligne inconnue",
            "lot2 : recopie des avoirs depuis le 20 juin"]),
    ],
    indicateurs=[
        Indicateur("montant_facture_millimes", "Montant facturé", "millimes",
                   "somme de quantite × prix_unitaire_negocie des lignes de facture acceptées", "SUM(facture)"),
        Indicateur("avoirs_millimes", "Avoirs", "millimes",
                   "somme des montants des avoirs EMIS acceptés (RETOUR et REMISE)", "SUM(avoir)"),
        Indicateur("ventes_nettes_millimes", "Ventes nettes", "millimes",
                   "montant facturé − avoirs", "SUM(facture) - SUM(avoir)"),
        Indicateur("cout_achat_net_millimes", "Coût d'achat des unités nettes", "millimes",
                   "(cartons facturés − cartons repris par avoir RETOUR) × coût d'achat unitaire, produit par produit",
                   "SUM(cout_facture) - SUM(cout_avoir)"),
        Indicateur("marge_commerciale_millimes", "Marge commerciale", "millimes",
                   "ventes nettes − coût d'achat des unités nettes",
                   "SUM(facture) - SUM(avoir) - SUM(cout_facture) + SUM(cout_avoir)"),
        Indicateur("taux_avoir", "Taux d'avoir", "ratio", "avoirs / montant facturé (en montant)",
                   "ROUND(1.0 * SUM(avoir) / NULLIF(SUM(facture), 0), 6)", tolerance=0.0001),
        Indicateur("unites_nettes", "Cartons nets", "nombre", "cartons facturés − cartons repris",
                   "SUM(unites_facturees) - SUM(unites_retournees)", principal=False),
    ],
    vue_analyse=VUE,
    axes={"par_segment": "segment", "par_client": "client_id", "par_region": "region", "par_mois": "mois",
          "par_famille": "famille", "par_produit": "produit_id"},
    scd2=SCD2("dim_client", "client_key", "client_id", "segment",
              faits=[("fact_facture", "client_key", "date_key"), ("fact_avoir", "client_key", "date_facture_key")],
              frontieres=[("CL04", "2026-06-30"), ("CL04", "2026-07-14"), ("CL04", "2026-07-15"), ("CL05", "2026-07-15")],
              changement="Le client CL04 (Supérette El Amel) passe du segment « épicerie » au segment « grande "
                         "surface » le 2026-07-15 (inclus). Cette information arrive avec `lot2/clients.json`.",
              precisions=["**Pour un avoir, la date qui choisit la version est la date de sa facture d'origine** "
                          "(`fact_avoir.date_facture_key`), pas la date de l'avoir (voir § 12)."]),
    regles=[
        ("Doublon exact", "la même ligne deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`F26-90003-9` deux fois avec des quantités différentes",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`ligne_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "produit `PR99`, client `CL99`, avoir vers `F26-00777-9`", "rejet `cle_inconnue`"),
        ("Format décimal", "`18.280`, `18,280`, `18.28`, `18,28`, `1 240,000`",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces (codes)", "` cl05 `, `Pr03`, ` pr07`", "supprimer les espaces autour + majuscules"),
        ("Casse / espaces (segment)", "`Grande Surface`, `Épicerie `", "supprimer les espaces autour + minuscules"),
        ("Quantité invalide", "`-2`, `0`, `1.5`, `2,5`", "rejet `quantite_invalide`"),
        ("Encodage", "`Sélima`, `Hédi`, `Supérette`", "lire les fichiers en UTF-8"),
        ("Avoir non émis", "`statut` = `ANNULE` ou `BROUILLON`", "ignorer (ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie les dernières factures du 30 juin", "ignorer : la clé métier existe déjà"),
    ],
    motifs=dict(MOTIFS_STANDARD),
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`ligne_id` vide → `id_manquant` ;",
        "`ligne_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "client ou produit absent des référentiels → `cle_inconnue` ;",
        "quantité non entière ou ≤ 0 → `quantite_invalide` ;",
        "`ligne_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Avoirs : statut ≠ `EMIS` ignoré → `numero_avoir` déjà chargé = ignoré → `ref_ligne_facture` absente de "
        "`fact_facture` = `cle_inconnue` (numero_ligne = `avoir.id`).",
    ],
    regles_metier=[
        "Montant facturé d'une ligne = quantité × prix **négocié** de la ligne (souvent inférieur au prix tarif).",
        "Coût d'achat = `Coût d'achat (TND)` du fichier des coûts (fixe sur 2026), pour chaque carton facturé.",
        "Un avoir prend le produit **et la version du client** de sa ligne de facture d'origine : `client_key` et "
        "`date_facture_key` sont recopiés de `fact_facture`. Son `date_key` est la **date de l'avoir**.",
        "Avoir `RETOUR` : `quantite` = cartons repris (> 0) ; leur coût d'achat est retiré du coût des unités nettes.",
        "Avoir `REMISE` : `quantite` = 0 ; il baisse les ventes nettes sans changer le coût d'achat.",
        "Montant d'un avoir = `montant_ht` converti en millimes (arrondi au millime).",
        "`famille` de `dim_produit` = libellé de la feuille Familles (ex. `LAI` → `Produits laitiers`).",
        "`segment` de `dim_client` = segment du JSON, sans espaces autour et en minuscules (`Grande Surface` → "
        "`grande surface`).",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, "
        "243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": ("Le 20 juillet, Medina Distribution émet un avoir pour une ligne facturée le 30 juin à la "
                     "Supérette El Amel (CL04). Depuis le 15 juillet, CL04 est passé du segment « épicerie » au "
                     "segment « grande surface ». L'avoir compte-t-il dans le segment de la facture (épicerie) ou "
                     "dans le segment valable le jour de l'avoir (grande surface) ?"),
        "options": ("- A : segment de la facture d'origine (l'avoir corrige une vente : il suit la version du client "
                    "valable à la date de la facture).\n"
                    "- B : segment valable à la date de l'avoir (chaque mouvement suit sa propre date)."),
        "decision": ("A. Un avoir corrige une ligne de facture : il est rattaché à la version du client valable à la "
                     "date de la **facture d'origine** (`fact_avoir.date_facture_key`), pour que la rentabilité d'un "
                     "segment compte ses propres corrections. Il reste compté dans le mois de **sa** date "
                     "(`fact_avoir.date_key`). Attention : la mission 00 a fait le choix inverse (B) pour les retours."),
    },
    variantes=[
        "Nouvel indicateur : taux de remise négociée = 1 − montant facturé / (quantité × prix tarif), par client "
        "et par produit.",
        "Nouvelle règle : un avoir émis plus de 30 jours après la date de la facture est refusé → nouveau motif "
        "`avoir_hors_delai` dans `rejets.csv`.",
        "Changement historique : le coût d'achat de l'huile végétale (PR03) augmente de 8 % au 2026-08-01 ; le coût "
        "doit dépendre de la date (dimension produit historisée ou coût stocké dans le fait).",
    ],
    ecrans_app=[
        ("Vue direction", "les six indicateurs et les ventes nettes par mois et par segment (barres empilées) ; les "
                          "filtres client, segment, famille et produit montrent qui fait baisser la marge."),
        ("Détail par client", "chaque client avec ses versions : CL04 en « épicerie » jusqu'au 2026-07-14, puis "
                              "« grande surface » ; les avoirs restent dans le segment de leur facture."),
        ("Qualité des données", "lignes lues, gardées, rejetées par motif et par lot ; avoirs ignorés."),
    ],
    textes_app=["Vue direction", "Détail par client", "Qualité des données"],
    export_sommes={"fact_facture": ["quantite", "montant_facture_millimes"],
                   "fact_avoir": ["quantite", "montant_millimes"],
                   "dim_produit": ["cout_achat_millimes", "prix_tarif_millimes"]},
    visuels=[
        {"type": "empile", "indicateur": "ventes_nettes_millimes", "x": "mois", "serie": "segment",
         "ordre_series": ["épicerie", "restaurant", "grande surface", "hôtel"],
         "fichier": "ventes_nettes_par_mois_et_segment",
         "titre": "Ventes nettes par mois et par segment", "libelle_x": "Mois", "libelle_serie": "Segment"},
        {"type": "barres", "indicateurs": ["ventes_nettes_millimes", "marge_commerciale_millimes"], "axe": "client_id",
         "fichier": "ventes_nettes_et_marge_par_client", "titre": "Ventes nettes et marge commerciale par client",
         "libelle_x": "Client", "libelle_y": "Montant"},
        {"type": "barres", "indicateurs": ["marge_commerciale_millimes"], "axe": "produit_id",
         "fichier": "marge_commerciale_par_produit", "titre": "Marge commerciale par produit",
         "libelle_x": "Produit"},
        {"type": "barres", "indicateurs": ["taux_avoir"], "axe": "client_id", "fichier": "taux_avoir_par_client",
         "titre": "Taux d'avoir par client", "libelle_x": "Client"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"factures": "factures.csv", "avoirs": "avoirs.sqlite"},
)

# Parcours de démonstration détaillé et décision attendue (écrits par common.doc_cahier / doc_fiche).
PARCOURS_DEMO = [
    ("Vue direction", "Montrer les six indicateurs sur toute la période, puis lire le graphique ventes nettes par "
                      "mois et par segment. Choisir le filtre Produit = `PR03` (huile végétale), puis Client = "
                      "`CL05` : la marge commerciale devient négative. Dire en une phrase ce que cela veut dire."),
    ("Détail par client", "Ouvrir CL04 : deux versions (« épicerie » valable jusqu'au 2026-07-15 exclu, puis "
                          "« grande surface » courante). Montrer que l'avoir du 20 juillet sur la facture du 30 juin "
                          "est compté dans « épicerie » (règle A) et dans le mois de juillet."),
    ("Qualité des données", "Montrer les lignes lues, les doublons ignorés, les lignes déjà chargées au lot 2 et les "
                            "rejets par motif ; relier un rejet `cle_inconnue` à sa ligne dans `rejets.csv`."),
]

QUESTION_DECISION = (
    "Quels **clients** et quels **produits** réduisent la rentabilité commerciale de Medina Distribution ? Classez "
    "les clients et les produits par marge commerciale et par taux de marge (marge / ventes nettes), repérez ceux "
    "dont le taux d'avoir est le plus haut, et proposez à la direction **une** action chiffrée (par exemple : "
    "revoir le prix négocié d'un produit pour un client, ou traiter la cause des avoirs d'une famille).")

SPEC_TEXTES["regle_a_clarifier"]["consequence"] = (
    "Conséquence dans l'entrepôt : `fact_avoir.client_key` = `client_key` de la ligne de facture ; "
    "`fact_avoir.date_key` = date de l'avoir (mois de l'avoir) ; `fact_avoir.date_facture_key` = date de la facture "
    "(contrôle SCD2).")
SPEC_TEXTES["parcours_app"] = "Démonstration conseillée :\n\n" + "\n".join(
    f"{k}. **{t}** — {c}" for k, (t, c) in enumerate(PARCOURS_DEMO, 1))
SPEC_TEXTES["question_decision"] = QUESTION_DECISION
