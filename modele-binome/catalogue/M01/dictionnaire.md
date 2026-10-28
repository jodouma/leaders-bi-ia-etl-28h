# Dictionnaire des données — Mission 01 (Carthage Market)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `ventes.csv` (csv)

Lignes de tickets exportées des caisses (UTF-8, séparateur `;`), avec promotion et remise.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `ligne_id` | texte | Identifiant de la ligne : ticket + numéro de ligne. | `T500234-2` |
| `ticket_id` | texte | Identifiant du ticket. | `T500234` |
| `date_vente` | texte | Date du ticket, trois formats possibles. | `04/03/2026` |
| `magasin` | texte | Code magasin (casse et espaces variables). | ` ham ` |
| `produit` | texte | Code article du catalogue. | `C107` |
| `quantite` | texte | Unités vendues. | `6` |
| `prix_unitaire` | texte | Prix unitaire du catalogue en TND, formats variés. | `1,490` |
| `code_promo` | texte | Code de la promotion appliquée, vide sans promotion. | `RAMADAN26` |
| `remise` | texte | Remise de TOUTE la ligne en TND (0 sans promotion). | `2,150` |
| `mode_paiement` | texte | Moyen de paiement (avec accents). | `espèces` |

### `catalogue.xlsx` (excel)

Feuille `Catalogue` (en-têtes à la ligne 3) + feuille `Familles`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Code article` | texte | Code produit (une cellule mal saisie). | ` c108` |
| `Libellé article` | texte | Nom du produit. | `Lait demi-écrémé 1 L` |
| `Famille` | texte | Code famille, à traduire avec la feuille Familles. | `LAI` |
| `Prix de vente (TND)` | nombre ou texte | Prix catalogue unitaire. | `21,500` |
| `Coût d'achat (TND)` | nombre ou texte | Coût d'achat unitaire. | `14,800` |
| `Code famille / Libellé famille` | texte | Feuille Familles. | `LAI / Produits laitiers` |

### `magasins.json` (json)

Référentiel des magasins : type (propre ou franchisé) et historique des régions.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `magasins[].code` | texte | Code magasin. | `HAM` |
| `magasins[].nom` | texte | Nom. | `Carthage Market Hammamet` |
| `magasins[].ville` | texte | Ville. | `Hammamet` |
| `magasins[].type` | texte | `propre` ou `franchisé` (casse et espaces variables). | ` Franchisé` |
| `magasins[].historique[].region` | texte | Région commerciale. | `Cap Bon` |
| `magasins[].historique[].valide_depuis` | date ISO | Début de la région (inclus). | `2022-04-11` |

### `operations.sqlite` (sqlite)

Base opérationnelle des retours : tables `retour`, `motif_retour`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `retour.id` | entier | Numéro interne de la ligne. | `57` |
| `retour.numero_retour` | texte | Numéro du retour (unique). | `RCM-00057` |
| `retour.ref_ligne_ticket` | texte | `ligne_id` de la vente d'origine. | `T500234-2` |
| `retour.code_magasin` | texte | Magasin du retour. | `SOU` |
| `retour.date_retour` | texte | Date et heure du retour. | `2026-03-10 10:15:00` |
| `retour.qte` | entier | Unités retournées. | `1` |
| `retour.montant_rembourse` | réel | Montant remboursé en TND (prix payé, remise comprise). | `8.82` |
| `retour.code_motif` | texte | Motif client → `motif_retour`. | `DLC` |
| `retour.statut` | texte | `VALIDE` ou `ANNULE`. | `VALIDE` |
| `retour.saisi_par` | texte | Poste de caisse. | `caisse-sou-2` |

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

Catalogue : un produit par ligne (feuilles Catalogue + Familles).

| Colonne | Type | Description |
|---|---|---|
| `produit_key` | INTEGER | Clé technique (1, 2, 3…). |
| `produit_id` | TEXT | Code article normalisé (strip + majuscules), ex. `C107`. |
| `nom` | TEXT | Libellé de l'article. |
| `famille` | TEXT | Libellé de la famille (feuille Familles), ex. `Produits laitiers`. |
| `prix_millimes` | INTEGER | Prix de vente du catalogue en millimes. |
| `cout_achat_millimes` | INTEGER | Coût d'achat unitaire en millimes. |

### `dim_magasin`

Magasins avec leur type et l'historique de la région (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `magasin_key` | INTEGER | Clé technique d'une VERSION de magasin. |
| `magasin_id` | TEXT | Code magasin, ex. `HAM` (plusieurs versions possibles). |
| `nom` | TEXT | Nom du magasin. |
| `type` | TEXT | `propre` ou `franchisé` (minuscules). |
| `region` | TEXT | Région commerciale de cette version. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_vente`

Une ligne de ticket acceptée.

| Colonne | Type | Description |
|---|---|---|
| `ligne_id` | TEXT | Identifiant de la ligne de ticket (clé métier unique). |
| `date_key` | INTEGER | Jour de la vente. |
| `produit_key` | INTEGER | Produit vendu. |
| `magasin_key` | INTEGER | Version du magasin valable à la date de la vente. |
| `quantite` | INTEGER | Unités vendues (entier > 0). |
| `prix_unitaire_millimes` | INTEGER | Prix unitaire du ticket en millimes (avant remise). |
| `remise_millimes` | INTEGER | Remise de la ligne en millimes (0 sans promotion). |
| `montant_brut_millimes` | INTEGER | quantite × prix_unitaire_millimes − remise_millimes (montant payé). |

### `fact_retour`

Un retour VALIDE de la base opérationnelle.

| Colonne | Type | Description |
|---|---|---|
| `retour_id` | TEXT | Numéro du retour (`numero_retour`), clé métier unique. |
| `date_key` | INTEGER | Jour du retour (heure ignorée). |
| `produit_key` | INTEGER | Produit de la ligne de vente d'origine. |
| `magasin_key` | INTEGER | Version du magasin valable à la date du RETOUR. |
| `quantite` | INTEGER | Unités retournées. |
| `montant_millimes` | INTEGER | Montant remboursé en millimes (prix payé, remise comprise). |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `ventes_brutes_millimes` | Ventes brutes | millimes | somme de (quantité × prix unitaire − remise) des lignes de ticket acceptées |
| `remises_millimes` | Remises | millimes | somme des remises des lignes de ticket acceptées (déjà déduites des ventes brutes) |
| `retours_millimes` | Retours | millimes | somme des montants remboursés des retours VALIDE acceptés |
| `ventes_nettes_millimes` | Ventes nettes | millimes | ventes brutes − retours |
| `cout_achat_net_millimes` | Coût d'achat des unités nettes | millimes | (unités vendues − unités retournées) × coût d'achat unitaire, produit par produit |
| `marge_cout_achat_millimes` | Marge sur coût d'achat | millimes | ventes nettes − coût d'achat des unités nettes |
| `part_franchises` | Part des franchisés | ratio | ventes nettes des magasins franchisés / ventes nettes totales |
| `taux_retour` | Taux de retour | ratio | retours / ventes brutes (en montant) |
| `unites_nettes` | Unités nettes | nombre | unités vendues − unités retournées |
