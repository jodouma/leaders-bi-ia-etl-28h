# Dictionnaire des données — Mission 00 (Maison Zitouna)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `ventes.csv` (csv)

Lignes de tickets exportées des caisses (UTF-8, séparateur `;`).

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `ligne_id` | texte | Identifiant de la ligne : ticket + numéro de ligne. | `TK10234-2` |
| `ticket_id` | texte | Identifiant du ticket. | `TK10234` |
| `date_vente` | texte | Date du ticket, trois formats possibles. | `04/03/2026` |
| `boutique` | texte | Code boutique (casse et espaces variables). | ` nbe ` |
| `produit` | texte | Code produit du catalogue. | `P01` |
| `quantite` | texte | Unités vendues. | `2` |
| `prix_unitaire` | texte | Prix payé en TND, formats variés. | `18,500` |
| `mode_paiement` | texte | Moyen de paiement (avec accents). | `espèces` |

### `catalogue.xlsx` (excel)

Feuille `Catalogue` (en-têtes à la ligne 3) + feuille `Familles`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Réf produit` | texte | Code produit (une cellule mal saisie). | ` p06` |
| `Désignation` | texte | Nom du produit. | `Dattes Deglet Nour 1 kg` |
| `Famille` | texte | Code famille, à traduire avec la feuille Familles. | `DAT` |
| `Prix de vente (TND)` | nombre ou texte | Prix catalogue. | `1 240,000` |
| `Coût d'achat (TND)` | nombre ou texte | Coût d'achat unitaire. | `52,500` |
| `Code famille / Libellé famille` | texte | Feuille Familles. | `DAT / Dattes` |

### `boutiques.json` (json)

Référentiel des boutiques avec l'historique des zones.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `boutiques[].code` | texte | Code boutique. | `NBE` |
| `boutiques[].nom` | texte | Nom. | `Maison Zitouna Nabeul` |
| `boutiques[].ville` | texte | Ville. | `Nabeul` |
| `boutiques[].historique[].zone` | texte | Zone commerciale. | `Cap Bon` |
| `boutiques[].historique[].valide_depuis` | date ISO | Début de la zone (inclus). | `2021-05-10` |

### `operations.sqlite` (sqlite)

Base opérationnelle des retours : tables `retour`, `motif_retour`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `retour.id` | entier | Numéro interne de la ligne. | `57` |
| `retour.numero_retour` | texte | Numéro du retour (unique). | `R26-00057` |
| `retour.ref_ligne_ticket` | texte | `ligne_id` de la vente d'origine. | `TK10234-2` |
| `retour.code_boutique` | texte | Boutique du retour. | `SFX` |
| `retour.date_retour` | texte | Date et heure du retour. | `2026-03-10 10:15:00` |
| `retour.qte` | entier | Unités retournées. | `1` |
| `retour.montant_rembourse` | réel | Montant remboursé en TND. | `14.5` |
| `retour.code_motif` | texte | Motif client → `motif_retour`. | `DEF` |
| `retour.statut` | texte | `VALIDE` ou `ANNULE`. | `VALIDE` |
| `retour.saisi_par` | texte | Poste de caisse. | `caisse-sfx-2` |

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
| `produit_id` | TEXT | Code produit normalisé (strip + majuscules), ex. `P01`. |
| `nom` | TEXT | Désignation. |
| `famille` | TEXT | Libellé de la famille (feuille Familles), ex. `Huiles`. |
| `prix_millimes` | INTEGER | Prix de vente du catalogue en millimes. |
| `cout_achat_millimes` | INTEGER | Coût d'achat unitaire en millimes. |

### `dim_boutique`

Boutiques avec historique de la zone commerciale (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `boutique_key` | INTEGER | Clé technique d'une VERSION de boutique. |
| `boutique_id` | TEXT | Code boutique, ex. `NBE` (plusieurs versions possibles). |
| `nom` | TEXT | Nom de la boutique. |
| `zone` | TEXT | Zone commerciale de cette version. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_vente`

Une ligne de ticket acceptée.

| Colonne | Type | Description |
|---|---|---|
| `ligne_id` | TEXT | Identifiant de la ligne de ticket (clé métier unique). |
| `date_key` | INTEGER | Jour de la vente. |
| `produit_key` | INTEGER | Produit vendu. |
| `boutique_key` | INTEGER | Version de la boutique valable à la date de la vente. |
| `quantite` | INTEGER | Unités vendues (entier > 0). |
| `prix_unitaire_millimes` | INTEGER | Prix du ticket en millimes (promotion possible). |
| `montant_brut_millimes` | INTEGER | quantite × prix_unitaire_millimes. |

### `fact_retour`

Un retour VALIDE de la base opérationnelle.

| Colonne | Type | Description |
|---|---|---|
| `retour_id` | TEXT | Numéro du retour (`numero_retour`), clé métier unique. |
| `date_key` | INTEGER | Jour du retour (heure ignorée). |
| `produit_key` | INTEGER | Produit de la ligne de vente d'origine. |
| `boutique_key` | INTEGER | Version de la boutique valable à la date du RETOUR. |
| `quantite` | INTEGER | Unités retournées. |
| `montant_millimes` | INTEGER | Montant remboursé en millimes. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `ventes_brutes_millimes` | Ventes brutes | millimes | somme de quantite × prix_unitaire des lignes de ticket acceptées |
| `retours_millimes` | Retours | millimes | somme des montants remboursés des retours VALIDE acceptés |
| `ventes_nettes_millimes` | Ventes nettes | millimes | ventes brutes − retours |
| `cout_achat_net_millimes` | Coût d'achat des unités nettes | millimes | (unités vendues − unités retournées) × coût d'achat unitaire, produit par produit |
| `marge_cout_achat_millimes` | Marge sur coût d'achat | millimes | ventes nettes − coût d'achat des unités nettes |
| `taux_retour` | Taux de retour | ratio | retours / ventes brutes (en montant) |
| `unites_nettes` | Unités nettes | nombre | unités vendues − unités retournées |
