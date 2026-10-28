# Dictionnaire des données — Mission 02 (Souk Express)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `commandes.csv` (csv)

Lignes de commande exportées du site (séparateur `;`). Lot 1 en UTF-8, **lot 2 en Windows-1252 (`cp1252`)**.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `ligne_id` | texte | Identifiant de la ligne : commande + numéro de ligne. | `C100234-2` |
| `commande_id` | texte | Identifiant de la commande (plusieurs lignes possibles). | `C100234` |
| `date_commande` | texte | Date de la commande, trois formats possibles. | `04/03/2026` |
| `canal` | texte | Code du canal de vente (casse et espaces variables). | ` app ` |
| `produit` | texte | Code produit du catalogue. | `P06` |
| `quantite` | texte | Unités commandées. | `2` |
| `prix_unitaire` | texte | Prix unitaire payé en TND, formats variés. | `32,500` |
| `remise` | texte | Remise en **TND** sur la ligne entière (code promo) ; vide = aucune remise. | `6,500` |
| `ville_livraison` | texte | Ville de livraison (avec accents ; non chargée dans l'étoile). | `Gabès` |

### `produits.xlsx` (excel)

Feuille `Produits` (titre au-dessus, en-têtes à la ligne 3).

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Code article` | texte | Code produit (une cellule mal saisie). | ` p12` |
| `Libellé` | texte | Nom du produit. | `Miel de thym 1 kg` |
| `Catégorie` | texte | Catégorie (espaces parasites possibles). | `Épicerie fine` |
| `Prix public (TND)` | nombre ou texte | Prix catalogue. | `899,000` |
| `Coût de revient (TND)` | nombre ou texte | Coût unitaire (informatif dans cette mission). | `610` |

### `canaux.json` (json)

Référentiel des canaux de vente avec l'historique de leur famille.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `canaux[].code` | texte | Code canal. | `VSO` |
| `canaux[].nom` | texte | Nom du canal. | `Vitrine sociale Souk Express` |
| `canaux[].historique[].famille` | texte | Famille : `site`, `application`, `marketplace` ou `réseaux sociaux`. | `réseaux sociaux` |
| `canaux[].historique[].depuis` | date ISO | Début de la famille (inclus). | `2023-06-01` |

### `operations.sqlite` (sqlite)

Base opérationnelle du service client : tables `remboursement`, `motif_remboursement`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `remboursement.id` | entier | Numéro interne de la ligne. | `41` |
| `remboursement.numero_remboursement` | texte | Numéro du remboursement (unique). | `RB26-00041` |
| `remboursement.ref_ligne_commande` | texte | `ligne_id` de la ligne de commande remboursée. | `C100234-2` |
| `remboursement.date_remboursement` | texte | Date et heure du remboursement. | `2026-03-10 10:15:00` |
| `remboursement.qte` | entier | Unités remboursées. | `1` |
| `remboursement.montant` | réel | Montant remboursé en TND (déjà net de la remise). | `26.0` |
| `remboursement.code_motif` | texte | Motif → `motif_remboursement`. | `TAI` |
| `remboursement.statut` | texte | `REMBOURSE`, `EN_COURS` ou `REFUSE`. | `REMBOURSE` |
| `remboursement.traite_par` | texte | Agent du service client. | `agent-04` |

## Entrepôt

### `dim_date`

Calendrier : une ligne par jour de la période chargée.

| Colonne | Type | Description |
|---|---|---|
| `date_key` | INTEGER | Clé du jour au format AAAAMMJJ (ex. 20260304). |
| `date_complete` | TEXT | Date ISO AAAA-MM-JJ. |
| `annee` | INTEGER | Année. |
| `mois` | INTEGER | Mois de 1 à 12. |
| `jour` | INTEGER | Jour du mois. |

### `dim_produit`

Catalogue : un produit par ligne (feuille Produits).

| Colonne | Type | Description |
|---|---|---|
| `produit_key` | INTEGER | Clé technique (1, 2, 3…). |
| `produit_id` | TEXT | Code produit normalisé (strip + majuscules), ex. `P12`. |
| `nom` | TEXT | Libellé du produit. |
| `categorie` | TEXT | Catégorie (espaces supprimés), ex. `Beauté`. |
| `prix_millimes` | INTEGER | Prix public du catalogue en millimes. |
| `cout_millimes` | INTEGER | Coût de revient unitaire en millimes. |

### `dim_canal`

Canaux de vente avec historique de la famille de canal (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `canal_key` | INTEGER | Clé technique d'une VERSION de canal. |
| `canal_id` | TEXT | Code canal, ex. `VSO` (plusieurs versions possibles). |
| `nom` | TEXT | Nom du canal. |
| `famille` | TEXT | Famille de cette version : `site`, `application`, `marketplace` ou `réseaux sociaux`. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_commande`

Une ligne de commande acceptée.

| Colonne | Type | Description |
|---|---|---|
| `ligne_id` | TEXT | Identifiant de la ligne de commande (clé métier unique). |
| `commande_id` | TEXT | Identifiant de la commande (sert à compter les commandes distinctes). |
| `date_key` | INTEGER | Jour de la commande. |
| `produit_key` | INTEGER | Produit commandé. |
| `canal_key` | INTEGER | Version du canal valable à la date de la commande. |
| `quantite` | INTEGER | Unités commandées (entier > 0). |
| `prix_unitaire_millimes` | INTEGER | Prix unitaire payé en millimes (promotion possible). |
| `montant_brut_millimes` | INTEGER | quantite × prix_unitaire_millimes. |
| `remise_millimes` | INTEGER | Remise de la ligne entière en millimes (0 si vide). |

### `fact_remboursement`

Un remboursement au statut REMBOURSE de la base opérationnelle.

| Colonne | Type | Description |
|---|---|---|
| `remboursement_id` | TEXT | Numéro du remboursement (`numero_remboursement`), clé métier unique. |
| `ligne_id` | TEXT | Ligne de commande remboursée. |
| `date_key` | INTEGER | Jour du remboursement (heure ignorée). |
| `produit_key` | INTEGER | Produit de la ligne de commande d'origine. |
| `canal_key` | INTEGER | Version du canal DE LA COMMANDE valable à la date du REMBOURSEMENT. |
| `quantite` | INTEGER | Unités remboursées. |
| `montant_millimes` | INTEGER | Montant remboursé en millimes. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `ca_brut_millimes` | CA brut | millimes | somme de quantite × prix_unitaire des lignes de commande acceptées |
| `remises_millimes` | Remises | millimes | somme des remises (TND) des lignes de commande acceptées |
| `remboursements_millimes` | Remboursements | millimes | somme des montants des remboursements au statut REMBOURSE acceptés |
| `ca_net_millimes` | CA net | millimes | CA brut − remises − remboursements |
| `nb_commandes` | Nombre de commandes | nombre | nombre de `commande_id` distincts parmi les lignes de commande acceptées |
| `panier_moyen_net_millimes` | Panier moyen net | millimes | CA net / nombre de commandes distinctes, arrondi au millime |
| `unites_nettes` | Unités nettes | nombre | unités commandées − unités remboursées |
