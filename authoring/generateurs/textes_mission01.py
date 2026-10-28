"""Textes et règles de la mission M01 (Carthage Market, réseau de magasins en franchise).

Séparés du code de génération pour la relecture.
"""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, d.date_complete AS jour, m.magasin_id, m.region,
       m.type AS type_magasin, p.produit_id, p.famille,
       f.montant_brut_millimes AS brut, 0 AS retour, f.remise_millimes AS remise,
       CASE WHEN m.type = 'franchisé' THEN f.montant_brut_millimes ELSE 0 END AS brut_franchise,
       0 AS retour_franchise,
       f.quantite * p.cout_achat_millimes AS cout_vendu, 0 AS cout_retour,
       f.quantite AS unites_vendues, 0 AS unites_retournees
FROM fact_vente f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_magasin m ON m.magasin_key = f.magasin_key
JOIN dim_produit p ON p.produit_key = f.produit_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), d.date_complete, m.magasin_id, m.region, m.type,
       p.produit_id, p.famille,
       0, r.montant_millimes, 0,
       0, CASE WHEN m.type = 'franchisé' THEN r.montant_millimes ELSE 0 END,
       0, r.quantite * p.cout_achat_millimes, 0, r.quantite
FROM fact_retour r
JOIN dim_date d ON d.date_key = r.date_key
JOIN dim_magasin m ON m.magasin_key = r.magasin_key
JOIN dim_produit p ON p.produit_key = r.produit_key
"""

SPEC_TEXTES = dict(
    code="M01",
    numero="01",
    titre="Réseau de magasins",
    entreprise="Carthage Market",
    secteur="réseau de sept supérettes de quartier, trois magasins propres et quatre magasins franchisés",
    contexte=("Carthage Market est une enseigne fictive de supérettes : épicerie, boissons, produits laitiers, "
              "hygiène et entretien. Le réseau compte sept magasins. Trois sont des magasins **propres** (gérés par "
              "l'enseigne) et quatre sont **franchisés** (gérés par un commerçant partenaire qui utilise la marque). "
              "Les caisses exportent les lignes de ticket dans un CSV, avec les codes promotion et les remises. Le "
              "catalogue (prix, coût d'achat, famille) vit dans un classeur Excel, la liste des magasins dans un "
              "fichier JSON et les retours clients dans une petite base SQLite. La direction veut savoir quels "
              "magasins et quels produits font vraiment les ventes et la marge. Solen Digital vous confie la mission."),
    demande=("Bonjour à tous les deux,\n\nNous ouvrons de plus en plus de magasins en franchise. Avant d'aller plus "
             "loin, je veux savoir quels magasins et quels produits apportent les ventes et la marge. Par magasin, "
             "par région, par famille et par mois : les ventes nettes, la marge sur coût d'achat, la part des "
             "franchisés dans les ventes nettes et le taux de retour. Dites-moi aussi quelles lignes vous avez dû "
             "écarter, et pourquoi.\n\nPour information : le 15 juillet, le magasin de Hammamet quitte la région "
             "Cap Bon et rejoint la région Sahel. Les chiffres du premier semestre doivent rester dans Cap Bon.\n\n"
             "Lamia Ben Salah, directrice (Solen Digital, pour le compte de Carthage Market)"),
    grain="une ligne de ticket de caisse",
    sources=[
        Source("ventes.csv", "csv", "Lignes de tickets exportées des caisses (UTF-8, séparateur `;`), avec promotion et remise.", [
            ColonneSource("ligne_id", "texte", "Identifiant de la ligne : ticket + numéro de ligne.", "T500234-2"),
            ColonneSource("ticket_id", "texte", "Identifiant du ticket.", "T500234"),
            ColonneSource("date_vente", "texte", "Date du ticket, trois formats possibles.", "04/03/2026"),
            ColonneSource("magasin", "texte", "Code magasin (casse et espaces variables).", " ham "),
            ColonneSource("produit", "texte", "Code article du catalogue.", "C107"),
            ColonneSource("quantite", "texte", "Unités vendues.", "6"),
            ColonneSource("prix_unitaire", "texte", "Prix unitaire du catalogue en TND, formats variés.", "1,490"),
            ColonneSource("code_promo", "texte", "Code de la promotion appliquée, vide sans promotion.", "RAMADAN26"),
            ColonneSource("remise", "texte", "Remise de TOUTE la ligne en TND (0 sans promotion).", "2,150"),
            ColonneSource("mode_paiement", "texte", "Moyen de paiement (avec accents).", "espèces"),
        ], ["formats de prix, de remises et de dates mélangés", "doublons", "identifiants vides ou en conflit",
            "codes inconnus", "quantités invalides", "lot2 : recopie des ventes des 29 et 30 juin"]),
        Source("catalogue.xlsx", "excel", "Feuille `Catalogue` (en-têtes à la ligne 3) + feuille `Familles`.", [
            ColonneSource("Code article", "texte", "Code produit (une cellule mal saisie).", " c108"),
            ColonneSource("Libellé article", "texte", "Nom du produit.", "Lait demi-écrémé 1 L"),
            ColonneSource("Famille", "texte", "Code famille, à traduire avec la feuille Familles.", "LAI"),
            ColonneSource("Prix de vente (TND)", "nombre ou texte", "Prix catalogue unitaire.", "21,500"),
            ColonneSource("Coût d'achat (TND)", "nombre ou texte", "Coût d'achat unitaire.", "14,800"),
            ColonneSource("Code famille / Libellé famille", "texte", "Feuille Familles.", "LAI / Produits laitiers"),
        ], ["titre au-dessus du tableau", "nombres stockés comme texte"]),
        Source("magasins.json", "json", "Référentiel des magasins : type (propre ou franchisé) et historique des régions.", [
            ColonneSource("magasins[].code", "texte", "Code magasin.", "HAM"),
            ColonneSource("magasins[].nom", "texte", "Nom.", "Carthage Market Hammamet"),
            ColonneSource("magasins[].ville", "texte", "Ville.", "Hammamet"),
            ColonneSource("magasins[].type", "texte", "`propre` ou `franchisé` (casse et espaces variables).", " Franchisé"),
            ColonneSource("magasins[].historique[].region", "texte", "Région commerciale.", "Cap Bon"),
            ColonneSource("magasins[].historique[].valide_depuis", "date ISO", "Début de la région (inclus).", "2022-04-11"),
        ], ["type écrit avec une majuscule ou un espace", "lot2 : une deuxième version pour HAM (Sahel au 2026-07-15)"]),
        Source("operations.sqlite", "sqlite", "Base opérationnelle des retours : tables `retour`, `motif_retour`, `parametre`.", [
            ColonneSource("retour.id", "entier", "Numéro interne de la ligne.", "57"),
            ColonneSource("retour.numero_retour", "texte", "Numéro du retour (unique).", "RCM-00057"),
            ColonneSource("retour.ref_ligne_ticket", "texte", "`ligne_id` de la vente d'origine.", "T500234-2"),
            ColonneSource("retour.code_magasin", "texte", "Magasin du retour.", "SOU"),
            ColonneSource("retour.date_retour", "texte", "Date et heure du retour.", "2026-03-10 10:15:00"),
            ColonneSource("retour.qte", "entier", "Unités retournées.", "1"),
            ColonneSource("retour.montant_rembourse", "réel", "Montant remboursé en TND (prix payé, remise comprise).", "8.82"),
            ColonneSource("retour.code_motif", "texte", "Motif client → `motif_retour`.", "DLC"),
            ColonneSource("retour.statut", "texte", "`VALIDE` ou `ANNULE`.", "VALIDE"),
            ColonneSource("retour.saisi_par", "texte", "Poste de caisse.", "caisse-sou-2"),
        ], ["retours annulés", "retours vers une ligne inconnue", "lot2 : recopie des retours depuis le 20 juin"]),
    ],
    indicateurs=[
        Indicateur("ventes_brutes_millimes", "Ventes brutes", "millimes",
                   "somme de (quantité × prix unitaire − remise) des lignes de ticket acceptées",
                   "SUM(brut)", principal=False),
        Indicateur("remises_millimes", "Remises", "millimes",
                   "somme des remises des lignes de ticket acceptées (déjà déduites des ventes brutes)",
                   "SUM(remise)", principal=False),
        Indicateur("retours_millimes", "Retours", "millimes",
                   "somme des montants remboursés des retours VALIDE acceptés", "SUM(retour)", principal=False),
        Indicateur("ventes_nettes_millimes", "Ventes nettes", "millimes",
                   "ventes brutes − retours", "SUM(brut) - SUM(retour)"),
        Indicateur("cout_achat_net_millimes", "Coût d'achat des unités nettes", "millimes",
                   "(unités vendues − unités retournées) × coût d'achat unitaire, produit par produit",
                   "SUM(cout_vendu) - SUM(cout_retour)", principal=False),
        Indicateur("marge_cout_achat_millimes", "Marge sur coût d'achat", "millimes",
                   "ventes nettes − coût d'achat des unités nettes",
                   "SUM(brut) - SUM(retour) - SUM(cout_vendu) + SUM(cout_retour)"),
        Indicateur("part_franchises", "Part des franchisés", "ratio",
                   "ventes nettes des magasins franchisés / ventes nettes totales",
                   "ROUND(1.0 * (SUM(brut_franchise) - SUM(retour_franchise)) / NULLIF(SUM(brut) - SUM(retour), 0), 6)",
                   tolerance=0.0001),
        Indicateur("taux_retour", "Taux de retour", "ratio", "retours / ventes brutes (en montant)",
                   "ROUND(1.0 * SUM(retour) / NULLIF(SUM(brut), 0), 6)", tolerance=0.0001),
        Indicateur("unites_nettes", "Unités nettes", "nombre", "unités vendues − unités retournées",
                   "SUM(unites_vendues) - SUM(unites_retournees)", principal=False),
    ],
    vue_analyse=VUE,
    axes={"par_region": "region", "par_magasin": "magasin_id", "par_type": "type_magasin", "par_mois": "mois",
          "par_famille": "famille", "par_produit": "produit_id"},
    scd2=SCD2("dim_magasin", "magasin_key", "magasin_id", "region",
              faits=[("fact_vente", "magasin_key", "date_key"), ("fact_retour", "magasin_key", "date_key")],
              frontieres=[("HAM", "2026-06-30"), ("HAM", "2026-07-14"), ("HAM", "2026-07-15"), ("LAC", "2026-07-15")],
              changement="Le magasin HAM (Hammamet, franchisé) passe de la région « Cap Bon » à la région « Sahel » le "
                         "2026-07-15 (inclus). Cette information arrive avec `lot2/magasins.json`."),
    regles=[
        ("Doublon exact", "la même ligne deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`T400037-9` deux fois avec des quantités différentes",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`ligne_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "produit `C199`, magasin `TOZ`, retour vers `T499001-1`", "rejet `cle_inconnue`"),
        ("Format décimal", "`21.500`, `21,500`, `21.5`, `21,5`, `1 240,000`",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers (prix ET remise)"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` ham `, `Sou`, ` c108`, ` Franchisé`",
         "supprimer les espaces autour ; codes en majuscules ; type de magasin en minuscules"),
        ("Quantité invalide", "`-2`, `0`, `1.5`, `2,5`", "rejet `quantite_invalide`"),
        ("Encodage", "`espèces`, `chèque`, `franchisé`", "lire les fichiers en UTF-8"),
        ("Retour annulé", "`statut = 'ANNULE'`", "ignorer (ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie les ventes des 29 et 30 juin", "ignorer : la clé métier existe déjà"),
    ],
    motifs=dict(MOTIFS_STANDARD),
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`ligne_id` vide → `id_manquant` ;",
        "`ligne_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "magasin ou produit absent des référentiels → `cle_inconnue` ;",
        "quantité non entière ou ≤ 0 → `quantite_invalide` ;",
        "`ligne_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Retours : `ANNULE` ignoré → `ref_ligne_ticket` absente de `fact_vente` = `cle_inconnue` (numero_ligne = `retour.id`) "
        "→ `numero_retour` déjà chargé = ignoré.",
    ],
    regles_metier=[
        "Montant brut d'une ligne = quantité × prix unitaire − remise de la ligne : c'est le montant **payé** par le client.",
        "`remise` vaut pour toute la ligne (pas par unité) ; `0` quand `code_promo` est vide.",
        "Coût d'achat = `Coût d'achat (TND)` du catalogue (fixe sur 2026) ; une remise ne change pas le coût d'achat.",
        "Un retour prend le produit de sa ligne de vente d'origine, le magasin `code_magasin` et la **date du retour** (heure ignorée).",
        "Montant d'un retour = `montant_rembourse` converti en millimes (la caisse rembourse le prix payé, remise comprise).",
        "`type` de `dim_magasin` = type du JSON, sans espaces, en minuscules : `propre` ou `franchisé`. Le type ne change pas en 2026 ; seule la région est historisée.",
        "Part des franchisés : un mouvement compte comme « franchisé » si la version du magasin valable à SA date est de type `franchisé`.",
        "`famille` de `dim_produit` = libellé de la feuille Familles (ex. `LAI` → `Produits laitiers`).",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, 243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": "Une ligne vendue en promotion (code `RAMADAN26`, remise de 10 %) : la marge se calcule-t-elle sur le prix payé (après remise) ou sur le prix du catalogue, la remise étant suivie à part comme une dépense de promotion ?",
        "options": "- A : remise déduite **avant** la marge. Ventes brutes = quantité × prix − remise ; la remise baisse les ventes et la marge.\n- B : remise déduite **après** la marge. Ventes brutes au prix catalogue ; la marge ignore la remise ; un indicateur « remises » est suivi à part.",
        "decision": "A. Les ventes brutes sont le montant réellement payé (remise déduite), donc la marge sur coût d'achat tient compte de la remise. L'indicateur « Remises » reste calculé à part pour montrer combien les promotions ont coûté. Un retour rembourse le prix payé, remise comprise.",
    },
    variantes=[
        "Nouvel indicateur : marge par famille et taux de marge = marge sur coût d'achat / ventes nettes, par famille de produits.",
        "Changement historique : le magasin SOU (Sousse, propre) devient franchisé le 2026-08-01 → le type devient lui aussi historisé (nouvelle version de `dim_magasin`) et la part des franchisés change à partir d'août.",
        "Nouvelle région : un huitième magasin, KAI (Kairouan, franchisé), ouvre le 2026-09-01 dans une nouvelle région « Centre » (lot 3 : nouveau magasin, nouvelle région, aucune ligne avant son ouverture).",
    ],
    ecrans_app=[
        ("Vue direction", "les quatre indicateurs (ventes nettes, marge sur coût d'achat, part des franchisés, taux de retour) "
                          "et les ventes nettes par mois et par région ; filtres période, magasin, région, type."),
        ("Détail par magasin", "chaque magasin avec ses versions : HAM en Cap Bon jusqu'au 2026-07-14, puis en Sahel ; "
                               "ventes nettes et marge par version et par mois."),
        ("Qualité des données", "lignes lues, gardées, déjà chargées, rejetées par motif et par lot."),
    ],
    textes_app=["Vue direction", "Détail par magasin", "Qualité des données"],
    export_sommes={"fact_vente": ["quantite", "remise_millimes", "montant_brut_millimes"],
                   "fact_retour": ["quantite", "montant_millimes"],
                   "dim_produit": ["prix_millimes", "cout_achat_millimes"]},
    visuels=[
        {"type": "empile", "indicateur": "ventes_nettes_millimes", "x": "mois", "serie": "region",
         "ordre_series": ["Grand Tunis", "Nord", "Cap Bon", "Sahel", "Sud"], "fichier": "ventes_nettes_par_mois_et_region",
         "titre": "Ventes nettes par mois et par région", "libelle_x": "Mois", "libelle_serie": "Région"},
        {"type": "barres", "indicateurs": ["ventes_nettes_millimes", "marge_cout_achat_millimes"], "axe": "magasin_id",
         "fichier": "ventes_nettes_et_marge_par_magasin", "titre": "Ventes nettes et marge sur coût d'achat par magasin",
         "libelle_x": "Magasin", "libelle_y": "Montant"},
        {"type": "barres", "indicateurs": ["ventes_nettes_millimes", "marge_cout_achat_millimes"], "axe": "famille",
         "fichier": "ventes_nettes_et_marge_par_famille", "titre": "Ventes nettes et marge sur coût d'achat par famille",
         "libelle_x": "Famille", "libelle_y": "Montant"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"ventes": "ventes.csv", "retours": "operations.sqlite"},
    parcours_app="Pendant la démonstration : choisir une période et un magasin dans les filtres, lire un indicateur et "
                 "son unité, puis montrer sur l'écran 2 que les ventes de HAM avant le 2026-07-15 restent en « Cap Bon ».",
)
