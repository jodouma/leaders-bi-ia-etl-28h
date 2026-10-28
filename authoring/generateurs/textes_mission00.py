"""Textes et règles de la mission 00 (Maison Zitouna). Séparés du code de génération pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, d.date_complete AS jour, b.boutique_id, b.zone,
       p.produit_id, p.famille,
       f.montant_brut_millimes AS brut, 0 AS retour,
       f.quantite * p.cout_achat_millimes AS cout_vendu, 0 AS cout_retour,
       f.quantite AS unites_vendues, 0 AS unites_retournees
FROM fact_vente f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_boutique b ON b.boutique_key = f.boutique_key
JOIN dim_produit p ON p.produit_key = f.produit_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), d.date_complete, b.boutique_id, b.zone, p.produit_id, p.famille,
       0, r.montant_millimes, 0, r.quantite * p.cout_achat_millimes, 0, r.quantite
FROM fact_retour r
JOIN dim_date d ON d.date_key = r.date_key
JOIN dim_boutique b ON b.boutique_key = r.boutique_key
JOIN dim_produit p ON p.produit_key = r.produit_key
"""

SPEC_TEXTES = dict(
    code="tronc-commun",
    numero="00",
    titre="Solen Commerce 360",
    entreprise="Maison Zitouna",
    secteur="réseau de trois boutiques de produits du terroir : huile d'olive, olives, dattes, coffrets",
    contexte=("Maison Zitouna vend de l'huile d'olive, des olives, des dattes et des coffrets cadeaux dans trois "
              "boutiques : Tunis Centre (zone Grand Tunis), Nabeul (zone Cap Bon) et Sfax (zone Sud). Les caisses "
              "exportent les tickets dans un CSV, le catalogue vit dans un classeur Excel, la liste des boutiques "
              "dans un fichier JSON et les retours clients dans une petite base SQLite. Personne ne sait dire "
              "combien l'entreprise gagne vraiment après les retours. Solen Digital vous confie la mission."),
    demande=("Bonjour à tous les deux,\n\nLes ventes montent, mais où passe la marge ? Je veux, par boutique, par "
             "zone et par mois : les ventes brutes, les retours, les ventes nettes, la marge sur coût d'achat et le "
             "taux de retour. Et je veux pouvoir faire confiance aux chiffres : dites-moi aussi ce que vous avez dû "
             "écarter, et pourquoi.\n\nPour information : à partir du 15 juillet, la boutique de Nabeul passe de la "
             "zone Cap Bon à la zone Nord-Est. Les chiffres du premier semestre doivent rester dans Cap Bon.\n\n"
             "Lamia Ben Salah, directrice (Solen Digital, pour le compte de Maison Zitouna)"),
    grain="une ligne de ticket de caisse",
    sources=[
        Source("ventes.csv", "csv", "Lignes de tickets exportées des caisses (UTF-8, séparateur `;`).", [
            ColonneSource("ligne_id", "texte", "Identifiant de la ligne : ticket + numéro de ligne.", "TK10234-2"),
            ColonneSource("ticket_id", "texte", "Identifiant du ticket.", "TK10234"),
            ColonneSource("date_vente", "texte", "Date du ticket, trois formats possibles.", "04/03/2026"),
            ColonneSource("boutique", "texte", "Code boutique (casse et espaces variables).", " nbe "),
            ColonneSource("produit", "texte", "Code produit du catalogue.", "P01"),
            ColonneSource("quantite", "texte", "Unités vendues.", "2"),
            ColonneSource("prix_unitaire", "texte", "Prix payé en TND, formats variés.", "18,500"),
            ColonneSource("mode_paiement", "texte", "Moyen de paiement (avec accents).", "espèces"),
        ], ["formats de prix et de dates mélangés", "doublons", "identifiants vides ou en conflit",
            "codes inconnus", "quantités invalides", "lot2 : recopie des 29 et 30 juin"]),
        Source("catalogue.xlsx", "excel", "Feuille `Catalogue` (en-têtes à la ligne 3) + feuille `Familles`.", [
            ColonneSource("Réf produit", "texte", "Code produit (une cellule mal saisie).", " p06"),
            ColonneSource("Désignation", "texte", "Nom du produit.", "Dattes Deglet Nour 1 kg"),
            ColonneSource("Famille", "texte", "Code famille, à traduire avec la feuille Familles.", "DAT"),
            ColonneSource("Prix de vente (TND)", "nombre ou texte", "Prix catalogue.", "1 240,000"),
            ColonneSource("Coût d'achat (TND)", "nombre ou texte", "Coût d'achat unitaire.", "52,500"),
            ColonneSource("Code famille / Libellé famille", "texte", "Feuille Familles.", "DAT / Dattes"),
        ], ["titre au-dessus du tableau", "nombres stockés comme texte"]),
        Source("boutiques.json", "json", "Référentiel des boutiques avec l'historique des zones.", [
            ColonneSource("boutiques[].code", "texte", "Code boutique.", "NBE"),
            ColonneSource("boutiques[].nom", "texte", "Nom.", "Maison Zitouna Nabeul"),
            ColonneSource("boutiques[].ville", "texte", "Ville.", "Nabeul"),
            ColonneSource("boutiques[].historique[].zone", "texte", "Zone commerciale.", "Cap Bon"),
            ColonneSource("boutiques[].historique[].valide_depuis", "date ISO", "Début de la zone (inclus).", "2021-05-10"),
        ], ["lot2 : une deuxième version pour NBE (Nord-Est au 2026-07-15)"]),
        Source("operations.sqlite", "sqlite", "Base opérationnelle des retours : tables `retour`, `motif_retour`, `parametre`.", [
            ColonneSource("retour.id", "entier", "Numéro interne de la ligne.", "57"),
            ColonneSource("retour.numero_retour", "texte", "Numéro du retour (unique).", "R26-00057"),
            ColonneSource("retour.ref_ligne_ticket", "texte", "`ligne_id` de la vente d'origine.", "TK10234-2"),
            ColonneSource("retour.code_boutique", "texte", "Boutique du retour.", "SFX"),
            ColonneSource("retour.date_retour", "texte", "Date et heure du retour.", "2026-03-10 10:15:00"),
            ColonneSource("retour.qte", "entier", "Unités retournées.", "1"),
            ColonneSource("retour.montant_rembourse", "réel", "Montant remboursé en TND.", "14.5"),
            ColonneSource("retour.code_motif", "texte", "Motif client → `motif_retour`.", "DEF"),
            ColonneSource("retour.statut", "texte", "`VALIDE` ou `ANNULE`.", "VALIDE"),
            ColonneSource("retour.saisi_par", "texte", "Poste de caisse.", "caisse-sfx-2"),
        ], ["retours annulés", "retours vers une ligne inconnue", "lot2 : recopie des retours depuis le 20 juin"]),
    ],
    indicateurs=[
        Indicateur("ventes_brutes_millimes", "Ventes brutes", "millimes",
                   "somme de quantite × prix_unitaire des lignes de ticket acceptées", "SUM(brut)"),
        Indicateur("retours_millimes", "Retours", "millimes",
                   "somme des montants remboursés des retours VALIDE acceptés", "SUM(retour)"),
        Indicateur("ventes_nettes_millimes", "Ventes nettes", "millimes",
                   "ventes brutes − retours", "SUM(brut) - SUM(retour)"),
        Indicateur("cout_achat_net_millimes", "Coût d'achat des unités nettes", "millimes",
                   "(unités vendues − unités retournées) × coût d'achat unitaire, produit par produit",
                   "SUM(cout_vendu) - SUM(cout_retour)", principal=False),
        Indicateur("marge_cout_achat_millimes", "Marge sur coût d'achat", "millimes",
                   "ventes nettes − coût d'achat des unités nettes",
                   "SUM(brut) - SUM(retour) - SUM(cout_vendu) + SUM(cout_retour)"),
        Indicateur("taux_retour", "Taux de retour", "ratio", "retours / ventes brutes (en montant)",
                   "ROUND(1.0 * SUM(retour) / NULLIF(SUM(brut), 0), 6)", tolerance=0.0001),
        Indicateur("unites_nettes", "Unités nettes", "nombre", "unités vendues − unités retournées",
                   "SUM(unites_vendues) - SUM(unites_retournees)", principal=False),
    ],
    vue_analyse=VUE,
    axes={"par_zone": "zone", "par_boutique": "boutique_id", "par_mois": "mois", "par_famille": "famille"},
    scd2=SCD2("dim_boutique", "boutique_key", "boutique_id", "zone",
              faits=[("fact_vente", "boutique_key", "date_key"), ("fact_retour", "boutique_key", "date_key")],
              frontieres=[("NBE", "2026-06-30"), ("NBE", "2026-07-14"), ("NBE", "2026-07-15"), ("TUN", "2026-07-15")],
              changement="La boutique NBE (Nabeul) passe de la zone « Cap Bon » à la zone « Nord-Est » le "
                         "2026-07-15 (inclus). Cette information arrive avec `lot2/boutiques.json`."),
    regles=[
        ("Doublon exact", "la même ligne deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`TK10037-9` deux fois avec des quantités différentes",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`ligne_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "produit `P99`, boutique `BZT`, retour vers `TK1999-1`", "rejet `cle_inconnue`"),
        ("Format décimal", "`18.500`, `18,500`, `18.5`, `18,5`, `1 240,000`",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` tun `, `Sfx`, ` p06`", "supprimer les espaces autour + majuscules"),
        ("Quantité invalide", "`-2`, `0`, `1.5`, `2,5`", "rejet `quantite_invalide`"),
        ("Encodage", "`espèces`, `chèque`", "lire les fichiers en UTF-8"),
        ("Retour annulé", "`statut = 'ANNULE'`", "ignorer (ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie les ventes des 29-30 juin", "ignorer : la clé métier existe déjà"),
    ],
    motifs=dict(MOTIFS_STANDARD),
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`ligne_id` vide → `id_manquant` ;",
        "`ligne_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "boutique ou produit absent des référentiels → `cle_inconnue` ;",
        "quantité non entière ou ≤ 0 → `quantite_invalide` ;",
        "`ligne_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Retours : `ANNULE` ignoré → `ref_ligne_ticket` absente de `fact_vente` = `cle_inconnue` (numero_ligne = `retour.id`) "
        "→ `numero_retour` déjà chargé = ignoré.",
    ],
    regles_metier=[
        "Montant brut d'une ligne = quantité × prix du **ticket** (une promotion peut donner un prix inférieur au catalogue).",
        "Coût d'achat = `cout_achat` du catalogue (fixe sur 2026).",
        "Un retour prend le produit de sa ligne de vente d'origine, la boutique `code_boutique` et la **date du retour** (heure ignorée).",
        "Montant d'un retour = `montant_rembourse` converti en millimes (arrondi au millime).",
        "`famille` de `dim_produit` = libellé de la feuille Familles (ex. `DAT` → `Dattes`).",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, 243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": "Un client rapporte le 20 juillet un produit acheté le 30 juin à Nabeul. Le retour compte-t-il dans la zone Cap Bon (zone de la vente) ou Nord-Est (zone le jour du retour) ?",
        "options": "- A : zone de la vente d'origine (il faut relier le retour à la version de la vente).\n- B : zone valable à la date du retour (chaque mouvement suit sa propre date).",
        "decision": "B. Chaque mouvement (vente ou retour) est rattaché à la version de la boutique valable à SA date et compté dans SON mois. C'est la même règle que pour les ventes.",
    },
    variantes=[
        "Nouvel indicateur : panier moyen net = ventes nettes / nombre de tickets distincts.",
        "Nouvelle règle : un retour plus de 30 jours après la vente est refusé → nouveau motif `retour_hors_delai`.",
        "Changement historique : SFX passe en zone « Centre-Est » le 2026-08-01 (troisième version dans `dim_boutique`).",
    ],
    ecrans_app=[
        ("Vue direction", "les cinq indicateurs et les ventes nettes par mois et par zone (barres empilées)."),
        ("Détail par boutique", "chaque boutique avec ses versions : NBE en Cap Bon jusqu'au 2026-07-14, puis Nord-Est."),
        ("Qualité des données", "lignes lues, gardées, rejetées par motif et par lot."),
    ],
    textes_app=["Vue direction", "Détail par boutique", "Qualité des données"],
    export_sommes={"fact_vente": ["quantite", "montant_brut_millimes"], "fact_retour": ["quantite", "montant_millimes"],
                   "dim_produit": ["prix_millimes", "cout_achat_millimes"]},
    visuels=[
        {"type": "empile", "indicateur": "ventes_nettes_millimes", "x": "mois", "serie": "zone",
         "ordre_series": ["Grand Tunis", "Cap Bon", "Nord-Est", "Sud"], "fichier": "ventes_nettes_par_mois_et_zone",
         "titre": "Ventes nettes par mois et par zone commerciale", "libelle_x": "Mois", "libelle_serie": "Zone"},
        {"type": "barres", "indicateurs": ["ventes_nettes_millimes", "marge_cout_achat_millimes"], "axe": "boutique_id",
         "fichier": "ventes_nettes_et_marge_par_boutique", "titre": "Ventes nettes et marge sur coût d'achat par boutique",
         "libelle_x": "Boutique", "libelle_y": "Montant"},
        {"type": "barres", "indicateurs": ["taux_retour"], "axe": "mois", "fichier": "taux_retour_par_mois",
         "titre": "Taux de retour par mois", "libelle_x": "Mois"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"ventes": "ventes.csv", "retours": "operations.sqlite"},
)
