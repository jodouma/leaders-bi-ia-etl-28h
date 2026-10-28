# Cahier des charges — Mission 01 : Réseau de magasins

Client fictif : **Carthage Market**. Ce document fixe les règles. En cas de doute, il gagne sur toute autre explication. Les noms de tables et de colonnes ci-dessous sont **obligatoires** : les contrôles automatiques et le guide Power BI les utilisent.

## 1. Grain

**Une ligne de fait = une ligne de ticket de caisse.** Chaque fait a une clé métier unique (identifiant texte de la source).

## 2. Sources (identiques dans `lot1/` et `lot2/`)

Les sources sont **lues, jamais modifiées**.

| Fichier | Type | Contenu | Pièges connus |
|---|---|---|---|
| `ventes.csv` | csv | Lignes de tickets exportées des caisses (UTF-8, séparateur `;`), avec promotion et remise. | formats de prix, de remises et de dates mélangés ; doublons ; identifiants vides ou en conflit ; codes inconnus ; quantités invalides ; lot2 : recopie des ventes des 29 et 30 juin |
| `catalogue.xlsx` | excel | Feuille `Catalogue` (en-têtes à la ligne 3) + feuille `Familles`. | titre au-dessus du tableau ; nombres stockés comme texte |
| `magasins.json` | json | Référentiel des magasins : type (propre ou franchisé) et historique des régions. | type écrit avec une majuscule ou un espace ; lot2 : une deuxième version pour HAM (Sahel au 2026-07-15) |
| `operations.sqlite` | sqlite | Base opérationnelle des retours : tables `retour`, `motif_retour`, `parametre`. | retours annulés ; retours vers une ligne inconnue ; lot2 : recopie des retours depuis le 20 juin |

## 3. Règles de nettoyage

| Anomalie | Exemple | Règle |
|---|---|---|
| Doublon exact | la même ligne deux fois | garder une seule occurrence (pas un rejet) |
| Doublon d'identifiant | `T400037-9` deux fois avec des quantités différentes | rejeter **les deux** lignes, motif `id_conflit` |
| Identifiant manquant | `ligne_id` vide ou blanc | rejet `id_manquant` |
| Clé inconnue | produit `C199`, magasin `TOZ`, retour vers `T499001-1` | rejet `cle_inconnue` |
| Format décimal | `21.500`, `21,500`, `21.5`, `21,5`, `1 240,000` | point ou virgule = décimales ; espace = milliers ; convertir en millimes entiers (prix ET remise) |
| Format date | `2026-03-04`, `04/03/2026`, `4 mars 2026` | convertir en ISO `AAAA-MM-JJ` ; `JJ/MM/AAAA` = le jour d'abord |
| Casse / espaces | ` ham `, `Sou`, ` c108`, ` Franchisé` | supprimer les espaces autour ; codes en majuscules ; type de magasin en minuscules |
| Quantité invalide | `-2`, `0`, `1.5`, `2,5` | rejet `quantite_invalide` |
| Encodage | `espèces`, `chèque`, `franchisé` | lire les fichiers en UTF-8 |
| Retour annulé | `statut = 'ANNULE'` | ignorer (ce n'est pas un rejet) |
| Ligne déjà chargée | lot2 recopie les ventes des 29 et 30 juin | ignorer : la clé métier existe déjà |

## 4. Motifs de rejet

| Motif (`motif`) | Signification |
|---|---|
| `id_conflit` | même identifiant sur deux lignes différentes : les deux lignes sont rejetées |
| `id_manquant` | identifiant vide |
| `cle_inconnue` | code absent du référentiel (produit, boutique, ligne de vente…) |
| `quantite_invalide` | quantité nulle, négative ou non entière |

Ordre des contrôles sur chaque ligne (le premier problème trouvé donne le motif) :

1. ligne identique, caractère pour caractère, à une ligne précédente du même fichier → ignorée (doublon exact) ;
2. `ligne_id` vide → `id_manquant` ;
3. `ligne_id` présent sur plusieurs lignes différentes du même fichier → `id_conflit` pour toutes ces lignes ;
4. magasin ou produit absent des référentiels → `cle_inconnue` ;
5. quantité non entière ou ≤ 0 → `quantite_invalide` ;
6. `ligne_id` déjà présent dans l'entrepôt → ignorée (rejeu), pas un rejet.
7. Retours : `ANNULE` ignoré → `ref_ligne_ticket` absente de `fact_vente` = `cle_inconnue` (numero_ligne = `retour.id`) → `numero_retour` déjà chargé = ignoré.

`outputs/rejets.csv` : une ligne par ligne source rejetée, en UTF-8, avec au moins les colonnes `lot` (`lot1` ou `lot2`), `source` (nom du fichier, ex. `ventes.csv`), `numero_ligne` (numéro de ligne dans le fichier, l'en-tête étant la ligne 1 ; pour la base SQLite, l'identifiant de la ligne), `motif`. Le fichier garde les rejets de tous les lots ; relancer un lot **remplace** ses rejets (pas de doublon). Les doublons exacts ne sont pas des rejets : on garde une occurrence (on peut les noter avec le motif `doublon_exact`, facultatif).

## 5. Règles métier

- Montant brut d'une ligne = quantité × prix unitaire − remise de la ligne : c'est le montant **payé** par le client.
- `remise` vaut pour toute la ligne (pas par unité) ; `0` quand `code_promo` est vide.
- Coût d'achat = `Coût d'achat (TND)` du catalogue (fixe sur 2026) ; une remise ne change pas le coût d'achat.
- Un retour prend le produit de sa ligne de vente d'origine, le magasin `code_magasin` et la **date du retour** (heure ignorée).
- Montant d'un retour = `montant_rembourse` converti en millimes (la caisse rembourse le prix payé, remise comprise).
- `type` de `dim_magasin` = type du JSON, sans espaces, en minuscules : `propre` ou `franchisé`. Le type ne change pas en 2026 ; seule la région est historisée.
- Part des franchisés : un mouvement compte comme « franchisé » si la version du magasin valable à SA date est de type `franchisé`.
- `famille` de `dim_produit` = libellé de la feuille Familles (ex. `LAI` → `Produits laitiers`).
- `dim_date` : un jour par ligne, du 2026-01-01 au dernier jour du dernier lot chargé (181 jours après le lot 1, 243 après le lot 2).

## 6. Entrepôt `outputs/entrepot.sqlite` (modèle en étoile)

Charger les dimensions **avant** les faits. Clés techniques `*_key` entières ; clés métier `*_id` en texte. Montants en **millimes entiers** (type INTEGER). Les clés étrangères sont déclarées (`FOREIGN KEY`).

### `dim_date` — dimension

Calendrier : une ligne par jour de la période chargée.

| Colonne | Type | Règle |
|---|---|---|
| `date_key` | INTEGER (clé) | Clé du jour au format AAAAMMJJ (ex. 20260304). |
| `date_complete` | TEXT | Date ISO AAAA-MM-JJ. |
| `annee` | INTEGER | Année. |
| `mois` | INTEGER | Mois de 1 à 12. |
| `jour` | INTEGER | Jour du mois. |

### `dim_produit` — dimension

Catalogue : un produit par ligne (feuilles Catalogue + Familles).

| Colonne | Type | Règle |
|---|---|---|
| `produit_key` | INTEGER (clé) | Clé technique (1, 2, 3…). |
| `produit_id` | TEXT | Code article normalisé (strip + majuscules), ex. `C107`. |
| `nom` | TEXT | Libellé de l'article. |
| `famille` | TEXT | Libellé de la famille (feuille Familles), ex. `Produits laitiers`. |
| `prix_millimes` | INTEGER | Prix de vente du catalogue en millimes. |
| `cout_achat_millimes` | INTEGER | Coût d'achat unitaire en millimes. |

### `dim_magasin` — dimension scd2

Magasins avec leur type et l'historique de la région (SCD2).

| Colonne | Type | Règle |
|---|---|---|
| `magasin_key` | INTEGER (clé) | Clé technique d'une VERSION de magasin. |
| `magasin_id` | TEXT | Code magasin, ex. `HAM` (plusieurs versions possibles). |
| `nom` | TEXT | Nom du magasin. |
| `type` | TEXT | `propre` ou `franchisé` (minuscules). |
| `region` | TEXT | Région commerciale de cette version. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_vente` — fait

Une ligne de ticket acceptée.

| Colonne | Type | Règle |
|---|---|---|
| `ligne_id` | TEXT (clé) | Identifiant de la ligne de ticket (clé métier unique). |
| `date_key` | INTEGER → `dim_date.date_key` | Jour de la vente. |
| `produit_key` | INTEGER → `dim_produit.produit_key` | Produit vendu. |
| `magasin_key` | INTEGER → `dim_magasin.magasin_key` | Version du magasin valable à la date de la vente. |
| `quantite` | INTEGER | Unités vendues (entier > 0). |
| `prix_unitaire_millimes` | INTEGER | Prix unitaire du ticket en millimes (avant remise). |
| `remise_millimes` | INTEGER | Remise de la ligne en millimes (0 sans promotion). |
| `montant_brut_millimes` | INTEGER | quantite × prix_unitaire_millimes − remise_millimes (montant payé). |

### `fact_retour` — fait

Un retour VALIDE de la base opérationnelle.

| Colonne | Type | Règle |
|---|---|---|
| `retour_id` | TEXT (clé) | Numéro du retour (`numero_retour`), clé métier unique. |
| `date_key` | INTEGER → `dim_date.date_key` | Jour du retour (heure ignorée). |
| `produit_key` | INTEGER → `dim_produit.produit_key` | Produit de la ligne de vente d'origine. |
| `magasin_key` | INTEGER → `dim_magasin.magasin_key` | Version du magasin valable à la date du RETOUR. |
| `quantite` | INTEGER | Unités retournées. |
| `montant_millimes` | INTEGER | Montant remboursé en millimes (prix payé, remise comprise). |


## 7. Historique (SCD2) sur `dim_magasin`

Le magasin HAM (Hammamet, franchisé) passe de la région « Cap Bon » à la région « Sahel » le 2026-07-15 (inclus). Cette information arrive avec `lot2/magasins.json`.

- Une ligne par version : `valid_from` **inclus**, `valid_to` **exclu**, `valid_to` vide (NULL) = version courante.
- La première version commence à la date `valide_depuis` donnée par la source.
- Une nouvelle version **ferme** la précédente : `valid_to` de l'ancienne = `valid_from` de la nouvelle.
- Un fait est rattaché à la version valable **à la date du fait** : un fait ancien garde l'ancienne version.

## 8. Chargement incrémental et rejeu

- `initial` : entrepôt neuf + `lot1`.
- `increment` : ajoute `lot2` sans effacer `lot1` (nouvelles lignes, nouvelle version SCD2, calendrier prolongé).
- `rejeu` : relancer `lot2` ne change **rien** (aucune ligne ajoutée, mêmes rejets). Un fait dont la clé métier est déjà dans l'entrepôt est ignoré.
- `lot2` contient volontairement des lignes de `lot1` (chevauchement d'export) : elles ne créent pas de doublon.

## 9. Indicateurs (définitions exactes)

| Indicateur | Unité | Formule exacte |
|---|---|---|
| Ventes brutes | TND (stocké en millimes) | somme de (quantité × prix unitaire − remise) des lignes de ticket acceptées |
| Remises | TND (stocké en millimes) | somme des remises des lignes de ticket acceptées (déjà déduites des ventes brutes) |
| Retours | TND (stocké en millimes) | somme des montants remboursés des retours VALIDE acceptés |
| Ventes nettes | TND (stocké en millimes) | ventes brutes − retours |
| Coût d'achat des unités nettes | TND (stocké en millimes) | (unités vendues − unités retournées) × coût d'achat unitaire, produit par produit |
| Marge sur coût d'achat | TND (stocké en millimes) | ventes nettes − coût d'achat des unités nettes |
| Part des franchisés | ratio | ventes nettes des magasins franchisés / ventes nettes totales |
| Taux de retour | ratio | retours / ventes brutes (en montant) |
| Unités nettes | nombre | unités vendues − unités retournées |

Le calcul de référence est fait sur la vue « mouvements » de `reference/contrat_entrepot.json` (ventes et ajustements réunis). Un mouvement est rangé dans le mois **de sa propre date**.

## 10. Sorties

- `outputs/rejets.csv` (voir § 4).
- `outputs/export/<table>.csv` pour chaque table de l'entrepôt (UTF-8, séparateur virgule, en-tête = noms de colonnes) + `outputs/export/manifest.json` : `{"tables": {"<table>": {"fichier": "<table>.csv", "lignes": N, "sommes": {"<colonne>": S}}}}`. Sommes obligatoires : `fact_vente` : quantite, remise_millimes, montant_brut_millimes; `fact_retour` : quantite, montant_millimes; `dim_produit` : prix_millimes, cout_achat_millimes.
- `outputs/app/index.html` : **un seul fichier** autonome (CSS, JavaScript et données à l'intérieur, aucun lien Internet), avec les écrans « Vue direction », « Détail par magasin », « Qualité des données » et des filtres.

## 11. Contrôles

```bash
python -m controles.verifier --mission M01 --etape initial     # après le lot 1
python -m controles.verifier --mission M01 --etape increment   # après le lot 2
python -m controles.verifier --mission M01 --etape rejeu       # après avoir relancé le lot 2
python -m controles.verifier --mission M01 --etape export
python -m controles.verifier --mission M01 --etape tout
```

## 12. Règle à clarifier

Une ligne vendue en promotion (code `RAMADAN26`, remise de 10 %) : la marge se calcule-t-elle sur le prix payé (après remise) ou sur le prix du catalogue, la remise étant suivie à part comme une dépense de promotion ? — **Décision :** A. Les ventes brutes sont le montant réellement payé (remise déduite), donc la marge sur coût d'achat tient compte de la remise. L'indicateur « Remises » reste calculé à part pour montrer combien les promotions ont coûté. Un retour rembourse le prix payé, remise comprise.

Options étudiées :

- A : remise déduite **avant** la marge. Ventes brutes = quantité × prix − remise ; la remise baisse les ventes et la marge.
- B : remise déduite **après** la marge. Ventes brutes au prix catalogue ; la marge ignore la remise ; un indicateur « remises » est suivi à part.

## 13. Trois variantes (évolutions possibles en soutenance)

1. Nouvel indicateur : marge par famille et taux de marge = marge sur coût d'achat / ventes nettes, par famille de produits.
2. Changement historique : le magasin SOU (Sousse, propre) devient franchisé le 2026-08-01 → le type devient lui aussi historisé (nouvelle version de `dim_magasin`) et la part des franchisés change à partir d'août.
3. Nouvelle région : un huitième magasin, KAI (Kairouan, franchisé), ouvre le 2026-09-01 dans une nouvelle région « Centre » (lot 3 : nouveau magasin, nouvelle région, aucune ligne avant son ouverture).

## 14. Parcours de démonstration de l'application (3 écrans)

1. **Vue direction** — les quatre indicateurs (ventes nettes, marge sur coût d'achat, part des franchisés, taux de retour) et les ventes nettes par mois et par région ; filtres période, magasin, région, type.
2. **Détail par magasin** — chaque magasin avec ses versions : HAM en Cap Bon jusqu'au 2026-07-14, puis en Sahel ; ventes nettes et marge par version et par mois.
3. **Qualité des données** — lignes lues, gardées, déjà chargées, rejetées par motif et par lot.

Pendant la démonstration : choisir une période et un magasin dans les filtres, lire un indicateur et son unité, puis montrer sur l'écran 2 que les ventes de HAM avant le 2026-07-15 restent en « Cap Bon ».
