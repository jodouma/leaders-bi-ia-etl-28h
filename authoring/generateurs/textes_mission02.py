"""Textes et règles de la mission M02 (Souk Express, e-commerce). Séparés du code de génération pour la relecture."""
from datetime import date

from common import MOTIFS_STANDARD, SCD2, ColonneSource, Indicateur, Source

# Une ligne par mouvement : lignes de commande (brut, remise, nb_commandes = 1 sur la première ligne
# de chaque commande) puis remboursements (montant remboursé). commande_id est vide pour un remboursement.
VUE = """
SELECT printf('%04d-%02d', d.annee, d.mois) AS mois, d.date_complete AS jour, c.canal_id, c.famille,
       p.produit_id, p.categorie, f.commande_id,
       CASE WHEN ROW_NUMBER() OVER (PARTITION BY f.commande_id ORDER BY f.ligne_id) = 1 THEN 1 ELSE 0 END AS nb_commandes,
       f.montant_brut_millimes AS brut, f.remise_millimes AS remise, 0 AS rembourse,
       f.quantite AS unites_vendues, 0 AS unites_remboursees
FROM fact_commande f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_canal c ON c.canal_key = f.canal_key
JOIN dim_produit p ON p.produit_key = f.produit_key
UNION ALL
SELECT printf('%04d-%02d', d.annee, d.mois), d.date_complete, c.canal_id, c.famille, p.produit_id, p.categorie,
       NULL, 0, 0, 0, r.montant_millimes, 0, r.quantite
FROM fact_remboursement r
JOIN dim_date d ON d.date_key = r.date_key
JOIN dim_canal c ON c.canal_key = r.canal_key
JOIN dim_produit p ON p.produit_key = r.produit_key
"""

SPEC_TEXTES = dict(
    code="M02",
    numero="02",
    titre="E-commerce · Souk Express",
    entreprise="Souk Express",
    secteur="boutique en ligne tunisienne : mode, high-tech, beauté, maison, épicerie fine",
    contexte=("Souk Express vend en ligne par six canaux : son site, son application mobile, deux places de "
              "marché partenaires (Bazar Lina, Sahel Market) et deux canaux sur les réseaux sociaux (la vitrine "
              "sociale et le groupe communauté). Le système de commande exporte les lignes de commande dans un "
              "CSV, les produits vivent dans un classeur Excel, la liste des canaux dans un fichier JSON et les "
              "remboursements clients dans une petite base SQLite. Chaque canal se dit « rentable », mais "
              "personne ne compte les remises et les remboursements. Solen Digital vous confie la mission."),
    demande=("Bonjour à tous les deux,\n\nNos places de marché font beaucoup de chiffre d'affaires, mais avec "
             "beaucoup de codes promo et de remboursements. Je veux savoir quels canaux nous font vraiment "
             "vendre une fois les remises et les remboursements enlevés. Par canal, par famille de canal et par "
             "mois : CA brut, remises, remboursements, CA net et panier moyen net. Dites-moi aussi ce que vous "
             "avez dû écarter, et pourquoi.\n\nPour information : à partir du 15 juillet, notre vitrine sociale "
             "(canal VSO) accueille des vendeurs partenaires. Elle passe de la famille « réseaux sociaux » à la "
             "famille « marketplace ». Les chiffres du premier semestre doivent rester dans « réseaux sociaux ».\n\n"
             "Lamia Ben Salah, directrice (Solen Digital, pour le compte de Souk Express)"),
    grain="une ligne de commande en ligne",
    sources=[
        Source("commandes.csv", "csv", "Lignes de commande exportées du site (séparateur `;`). Lot 1 en UTF-8, "
               "**lot 2 en Windows-1252 (`cp1252`)**.", [
            ColonneSource("ligne_id", "texte", "Identifiant de la ligne : commande + numéro de ligne.", "C100234-2"),
            ColonneSource("commande_id", "texte", "Identifiant de la commande (plusieurs lignes possibles).", "C100234"),
            ColonneSource("date_commande", "texte", "Date de la commande, trois formats possibles.", "04/03/2026"),
            ColonneSource("canal", "texte", "Code du canal de vente (casse et espaces variables).", " app "),
            ColonneSource("produit", "texte", "Code produit du catalogue.", "P06"),
            ColonneSource("quantite", "texte", "Unités commandées.", "2"),
            ColonneSource("prix_unitaire", "texte", "Prix unitaire payé en TND, formats variés.", "32,500"),
            ColonneSource("remise", "texte", "Remise en **TND** sur la ligne entière (code promo) ; vide = aucune remise.", "6,500"),
            ColonneSource("ville_livraison", "texte", "Ville de livraison (avec accents ; non chargée dans l'étoile).", "Gabès"),
        ], ["formats de montants et de dates mélangés", "remise vide, `0` ou montant", "doublons",
            "identifiants vides ou en conflit", "codes inconnus", "quantités invalides",
            "lot2 : fichier en cp1252 (lu en UTF-8, il plante sur les accents : `août`, `Gabès`)", "lot2 : recopie des commandes des 29 et 30 juin"]),
        Source("produits.xlsx", "excel", "Feuille `Produits` (titre au-dessus, en-têtes à la ligne 3).", [
            ColonneSource("Code article", "texte", "Code produit (une cellule mal saisie).", " p12"),
            ColonneSource("Libellé", "texte", "Nom du produit.", "Miel de thym 1 kg"),
            ColonneSource("Catégorie", "texte", "Catégorie (espaces parasites possibles).", "Épicerie fine"),
            ColonneSource("Prix public (TND)", "nombre ou texte", "Prix catalogue.", "899,000"),
            ColonneSource("Coût de revient (TND)", "nombre ou texte", "Coût unitaire (informatif dans cette mission).", "610"),
        ], ["titre au-dessus du tableau", "nombres stockés comme texte"]),
        Source("canaux.json", "json", "Référentiel des canaux de vente avec l'historique de leur famille.", [
            ColonneSource("canaux[].code", "texte", "Code canal.", "VSO"),
            ColonneSource("canaux[].nom", "texte", "Nom du canal.", "Vitrine sociale Souk Express"),
            ColonneSource("canaux[].historique[].famille", "texte",
                          "Famille : `site`, `application`, `marketplace` ou `réseaux sociaux`.", "réseaux sociaux"),
            ColonneSource("canaux[].historique[].depuis", "date ISO", "Début de la famille (inclus).", "2023-06-01"),
        ], ["lot2 : une deuxième version pour VSO (marketplace au 2026-07-15)"]),
        Source("operations.sqlite", "sqlite", "Base opérationnelle du service client : tables `remboursement`, "
               "`motif_remboursement`, `parametre`.", [
            ColonneSource("remboursement.id", "entier", "Numéro interne de la ligne.", "41"),
            ColonneSource("remboursement.numero_remboursement", "texte", "Numéro du remboursement (unique).", "RB26-00041"),
            ColonneSource("remboursement.ref_ligne_commande", "texte", "`ligne_id` de la ligne de commande remboursée.", "C100234-2"),
            ColonneSource("remboursement.date_remboursement", "texte", "Date et heure du remboursement.", "2026-03-10 10:15:00"),
            ColonneSource("remboursement.qte", "entier", "Unités remboursées.", "1"),
            ColonneSource("remboursement.montant", "réel", "Montant remboursé en TND (déjà net de la remise).", "26.0"),
            ColonneSource("remboursement.code_motif", "texte", "Motif → `motif_remboursement`.", "TAI"),
            ColonneSource("remboursement.statut", "texte", "`REMBOURSE`, `EN_COURS` ou `REFUSE`.", "REMBOURSE"),
            ColonneSource("remboursement.traite_par", "texte", "Agent du service client.", "agent-04"),
        ], ["statuts EN_COURS et REFUSE (à ignorer)", "remboursements vers une ligne inconnue",
            "pas de canal dans la table : il vient de la commande", "lot2 : recopie des remboursements depuis le 20 juin"]),
    ],
    indicateurs=[
        Indicateur("ca_brut_millimes", "CA brut", "millimes",
                   "somme de quantite × prix_unitaire des lignes de commande acceptées", "SUM(brut)"),
        Indicateur("remises_millimes", "Remises", "millimes",
                   "somme des remises (TND) des lignes de commande acceptées", "SUM(remise)"),
        Indicateur("remboursements_millimes", "Remboursements", "millimes",
                   "somme des montants des remboursements au statut REMBOURSE acceptés", "SUM(rembourse)"),
        Indicateur("ca_net_millimes", "CA net", "millimes",
                   "CA brut − remises − remboursements", "SUM(brut) - SUM(remise) - SUM(rembourse)"),
        Indicateur("nb_commandes", "Nombre de commandes", "nombre",
                   "nombre de `commande_id` distincts parmi les lignes de commande acceptées",
                   "COUNT(DISTINCT commande_id)", principal=False),
        Indicateur("panier_moyen_net_millimes", "Panier moyen net", "millimes",
                   "CA net / nombre de commandes distinctes, arrondi au millime",
                   "ROUND(1.0 * (SUM(brut) - SUM(remise) - SUM(rembourse)) / NULLIF(COUNT(DISTINCT commande_id), 0))"),
        Indicateur("unites_nettes", "Unités nettes", "nombre", "unités commandées − unités remboursées",
                   "SUM(unites_vendues) - SUM(unites_remboursees)", principal=False),
    ],
    vue_analyse=VUE,
    axes={"par_famille": "famille", "par_canal": "canal_id", "par_mois": "mois", "par_categorie": "categorie"},
    scd2=SCD2("dim_canal", "canal_key", "canal_id", "famille",
              faits=[("fact_commande", "canal_key", "date_key"), ("fact_remboursement", "canal_key", "date_key")],
              frontieres=[("VSO", "2026-06-30"), ("VSO", "2026-07-14"), ("VSO", "2026-07-15"), ("WEB", "2026-07-15")],
              changement="Le canal VSO (vitrine sociale) passe de la famille « réseaux sociaux » à la famille "
                         "« marketplace » le 2026-07-15 (inclus). Cette information arrive avec `lot2/canaux.json`."),
    regles=[
        ("Doublon exact", "la même ligne deux fois", "garder une seule occurrence (pas un rejet)"),
        ("Doublon d'identifiant", "`C150037-9` deux fois avec des quantités différentes",
         "rejeter **les deux** lignes, motif `id_conflit`"),
        ("Identifiant manquant", "`ligne_id` vide ou blanc", "rejet `id_manquant`"),
        ("Clé inconnue", "produit `X15` (sources) ou `X99` (échantillon), canal `TIK`, remboursement vers `C109999-1`", "rejet `cle_inconnue`"),
        ("Format décimal", "`32.500`, `32,500`, `32.5`, `32,5`, `1 240,000`",
         "point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers"),
        ("Remise vide", "`remise` vide, `0`, `0.000`", "remise = 0 millime (ce n'est pas un rejet)"),
        ("Format date", "`2026-03-04`, `04/03/2026`, `4 mars 2026`",
         "convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord"),
        ("Casse / espaces", "` app `, `Web`, ` p12`", "supprimer les espaces autour + majuscules"),
        ("Quantité invalide", "`-2`, `0`, `1.5`, `2,5`", "rejet `quantite_invalide`"),
        ("Encodage", "lot2 : `Gabès` écrit en Windows-1252",
         "lire `lot1/commandes.csv` en UTF-8 et `lot2/commandes.csv` en `cp1252` (sinon erreur `UnicodeDecodeError`)"),
        ("Remboursement non payé", "`statut` = `EN_COURS` ou `REFUSE`", "ignorer (ce n'est pas un rejet)"),
        ("Ligne déjà chargée", "lot2 recopie les commandes des 29 et 30 juin", "ignorer : la clé métier existe déjà"),
    ],
    motifs=dict(MOTIFS_STANDARD),
    ordre_controles=[
        "ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;",
        "`ligne_id` vide → `id_manquant` ;",
        "`ligne_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;",
        "canal ou produit absent des référentiels → `cle_inconnue` ;",
        "quantité non entière ou ≤ 0 → `quantite_invalide` ;",
        "`ligne_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.",
        "Remboursements : statut autre que `REMBOURSE` ignoré → `ref_ligne_commande` absente de `fact_commande` = "
        "`cle_inconnue` (numero_ligne = `remboursement.id`) → `numero_remboursement` déjà chargé = ignoré.",
    ],
    regles_metier=[
        "Montant brut d'une ligne = quantité × prix unitaire **payé** (une promotion peut donner un prix inférieur au catalogue).",
        "`remise` = montant en **TND** de la remise accordée sur **la ligne entière** (pas par unité, pas un pourcentage). "
        "Vide = 0. Elle est stockée telle quelle en millimes dans `fact_commande.remise_millimes`.",
        "Un remboursement prend le produit et le **canal** de sa ligne de commande d'origine (la table `remboursement` n'a pas de canal), "
        "et la **date du remboursement** (heure ignorée).",
        "Montant d'un remboursement = `montant` converti en millimes (arrondi au millime). Il est déjà net de la remise : on ne retire rien d'autre.",
        "Nombre de commandes = nombre de `commande_id` distincts parmi les lignes de commande acceptées. "
        "Par catégorie, une commande qui contient deux catégories compte dans chacune.",
        "Panier moyen net = CA net / nombre de commandes, arrondi au millime (pour un groupe sans commande : vide).",
        "`categorie` de `dim_produit` = colonne Catégorie du classeur, espaces supprimés (ex. `Beauté`).",
        "`dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, 243 après le lot 2).",
    ],
    regle_a_clarifier={
        "question": "Une cliente a commandé le 30 juin sur la vitrine sociale (VSO, alors « réseaux sociaux ») et a été "
                    "remboursée le 20 juillet (VSO est alors « marketplace »). Dans quelle famille compte ce remboursement ?",
        "options": "- A : famille valable à la date de la **commande** (« réseaux sociaux ») : il faut relier le remboursement à la version de la commande.\n"
                   "- B : famille valable à la date du **remboursement** (« marketplace ») : chaque mouvement suit sa propre date.",
        "decision": "B. Chaque mouvement (ligne de commande ou remboursement) est rattaché à la version du canal valable "
                    "à SA date et compté dans SON mois. Le remboursement du 20 juillet compte donc en « marketplace », en juillet. "
                    "C'est la même règle que pour les commandes, et c'est ce que vérifie `controles/verifier.py`.",
    },
    variantes=[
        "Nouvel indicateur : taux de remise = remises / CA brut, par canal et par famille.",
        "Nouvelle règle : un remboursement plus de 30 jours après la commande est refusé → nouveau motif `remboursement_hors_delai`.",
        "Changement historique : l'application (APP) passe en famille « site » le 2026-08-01 (fusion des deux équipes) : "
        "troisième version dans `dim_canal`.",
    ],
    ecrans_app=[
        ("Vue direction", "les cinq indicateurs (CA brut, remises, remboursements, CA net, panier moyen net) et le CA net "
                          "par mois et par famille de canal (barres empilées) ; filtres période, canal, famille."),
        ("Détail par canal", "chaque canal avec ses versions : VSO en « réseaux sociaux » jusqu'au 2026-07-14, puis "
                             "« marketplace » ; indicateurs par famille et par mois."),
        ("Qualité des données", "lignes lues, gardées, rejetées par motif et par lot ; remboursements ignorés."),
    ],
    textes_app=["Vue direction", "Détail par canal", "Qualité des données"],
    export_sommes={"fact_commande": ["quantite", "montant_brut_millimes", "remise_millimes"],
                   "fact_remboursement": ["quantite", "montant_millimes"],
                   "dim_produit": ["prix_millimes", "cout_millimes"]},
    visuels=[
        {"type": "empile", "indicateur": "ca_net_millimes", "x": "mois", "serie": "famille",
         "ordre_series": ["site", "application", "marketplace", "réseaux sociaux"], "fichier": "ca_net_par_mois_et_famille",
         "titre": "CA net par mois et par famille de canal", "libelle_x": "Mois", "libelle_serie": "Famille"},
        {"type": "barres", "indicateurs": ["ca_brut_millimes", "ca_net_millimes"], "axe": "canal_id",
         "fichier": "ca_brut_et_net_par_canal", "titre": "CA brut et CA net par canal",
         "libelle_x": "Canal", "libelle_y": "Montant"},
        {"type": "barres", "indicateurs": ["panier_moyen_net_millimes"], "axe": "canal_id",
         "fichier": "panier_moyen_net_par_canal", "titre": "Panier moyen net par canal", "libelle_x": "Canal"},
        {"type": "rejets", "fichier": "rejets_par_motif", "titre": "Lignes rejetées par motif et par lot"},
    ],
    debut_calendrier=date(2026, 1, 1),
    sources_rejets={"commandes": "commandes.csv", "remboursements": "operations.sqlite"},
    parcours_app="Démonstration conseillée : (1) Vue direction, toute la période, puis filtre famille « marketplace » : "
                 "le CA brut est élevé, le CA net beaucoup moins ; (2) Détail par canal, VSO : deux versions, et le "
                 "remboursement du 20 juillet compté en « marketplace » ; (3) Qualité des données : rejets par motif et "
                 "par lot, remboursements `EN_COURS`/`REFUSE` ignorés.",
)
