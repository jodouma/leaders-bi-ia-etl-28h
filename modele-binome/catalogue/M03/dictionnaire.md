# Dictionnaire des données — Mission 03 (Medina Distribution)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `factures.csv` (csv)

Lignes de facture exportées du logiciel de facturation (UTF-8, séparateur `;`).

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `facture_id` | texte | Numéro de la facture. | `F26-01234` |
| `ligne_id` | texte | Identifiant de la ligne : facture + numéro de ligne (clé métier). | `F26-01234-3` |
| `date_facture` | texte | Date de la facture, trois formats possibles. | `04/03/2026` |
| `client` | texte | Code client (casse et espaces variables). | ` cl05 ` |
| `produit` | texte | Code article du fichier des coûts. | `PR03` |
| `quantite` | texte | Nombre de cartons (ou packs) facturés. | `12` |
| `prix_unitaire_negocie` | texte | Prix négocié d'un carton en TND, formats variés. | `18,280` |
| `commercial` | texte | Prénom du commercial (avec accents). | `Sélima` |

### `couts.xlsx` (excel)

Feuille `Articles` (en-têtes à la ligne 3) + feuille `Familles`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Code article` | texte | Code produit (une cellule mal saisie). | ` pr07` |
| `Désignation` | texte | Nom et conditionnement. | `Huile végétale — bidon 5 L` |
| `Famille` | texte | Code famille, à traduire avec la feuille Familles. | `EPI` |
| `Coût d'achat (TND)` | nombre ou texte | Coût d'achat d'un carton. | `19,600` |
| `Prix tarif (TND)` | nombre ou texte | Prix catalogue avant négociation. | `21.5` |
| `Code famille / Libellé famille` | texte | Feuille Familles. | `LAI / Produits laitiers` |

### `clients.json` (json)

Fichier clients avec l'historique des segments.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `clients[].code` | texte | Code client. | `CL04` |
| `clients[].raison_sociale` | texte | Nom du client. | `Supérette El Amel` |
| `clients[].region` | texte | Région de livraison. | `Cap Bon` |
| `clients[].historique[].segment` | texte | Segment : épicerie, restaurant, grande surface ou hôtel (casse variable). | `Grande Surface` |
| `clients[].historique[].valide_depuis` | date ISO | Début du segment (inclus). | `2023-02-01` |

### `avoirs.sqlite` (sqlite)

Base de la gestion commerciale : tables `avoir`, `motif_avoir`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `avoir.id` | entier | Numéro interne de la ligne. | `41` |
| `avoir.numero_avoir` | texte | Numéro de l'avoir (unique). | `AV26-00041` |
| `avoir.ref_ligne_facture` | texte | `ligne_id` de la ligne de facture corrigée. | `F26-01234-3` |
| `avoir.code_client` | texte | Client (information ; le client fait foi par la facture). | `CL02` |
| `avoir.date_avoir` | texte | Date d'émission de l'avoir. | `2026-03-10` |
| `avoir.type_avoir` | texte | `RETOUR` (cartons repris) ou `REMISE` (geste sur le prix, 0 carton). | `RETOUR` |
| `avoir.qte_retournee` | entier | Cartons repris (0 pour une REMISE). | `2` |
| `avoir.montant_ht` | réel | Montant de l'avoir en TND. | `16.9` |
| `avoir.code_motif` | texte | Motif → `motif_avoir`. | `DLC` |
| `avoir.statut` | texte | `EMIS`, `ANNULE` ou `BROUILLON`. | `EMIS` |
| `avoir.saisi_par` | texte | Poste de saisie. | `adv-2` |

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

Articles : un produit par ligne (feuilles Articles + Familles).

| Colonne | Type | Description |
|---|---|---|
| `produit_key` | INTEGER | Clé technique (1, 2, 3…). |
| `produit_id` | TEXT | Code article normalisé (strip + majuscules), ex. `PR03`. |
| `nom` | TEXT | Désignation et conditionnement. |
| `famille` | TEXT | Libellé de la famille (feuille Familles), ex. `Produits laitiers`. |
| `cout_achat_millimes` | INTEGER | Coût d'achat d'un carton en millimes. |
| `prix_tarif_millimes` | INTEGER | Prix tarif d'un carton (avant négociation) en millimes. |

### `dim_client`

Clients avec historique du segment (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `client_key` | INTEGER | Clé technique d'une VERSION de client. |
| `client_id` | TEXT | Code client, ex. `CL04` (plusieurs versions possibles). |
| `nom` | TEXT | Raison sociale. |
| `segment` | TEXT | Segment de cette version : `épicerie`, `restaurant`, `grande surface` ou `hôtel`. |
| `region` | TEXT | Région de livraison. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_facture`

Une ligne de facture acceptée.

| Colonne | Type | Description |
|---|---|---|
| `ligne_id` | TEXT | Identifiant de la ligne de facture (clé métier unique). |
| `facture_id` | TEXT | Numéro de la facture. |
| `date_key` | INTEGER | Jour de la facture. |
| `produit_key` | INTEGER | Produit facturé. |
| `client_key` | INTEGER | Version du client valable à la date de la facture. |
| `quantite` | INTEGER | Cartons facturés (entier > 0). |
| `prix_negocie_millimes` | INTEGER | Prix négocié d'un carton en millimes. |
| `montant_facture_millimes` | INTEGER | quantite × prix_negocie_millimes. |

### `fact_avoir`

Un avoir EMIS de la gestion commerciale, rattaché à une ligne de facture.

| Colonne | Type | Description |
|---|---|---|
| `avoir_id` | TEXT | Numéro de l'avoir (`numero_avoir`), clé métier unique. |
| `ligne_id` | TEXT | Ligne de facture corrigée. |
| `date_key` | INTEGER | Jour de l'avoir (mois de comptage). |
| `date_facture_key` | INTEGER | Jour de la facture d'origine (choisit la version du client). |
| `produit_key` | INTEGER | Produit de la ligne de facture. |
| `client_key` | INTEGER | Version du client de la ligne de facture (règle A). |
| `type_avoir` | TEXT | `RETOUR` (cartons repris) ou `REMISE` (geste sur le prix). |
| `quantite` | INTEGER | Cartons repris (0 pour une REMISE). |
| `montant_millimes` | INTEGER | Montant de l'avoir en millimes. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `montant_facture_millimes` | Montant facturé | millimes | somme de quantite × prix_unitaire_negocie des lignes de facture acceptées |
| `avoirs_millimes` | Avoirs | millimes | somme des montants des avoirs EMIS acceptés (RETOUR et REMISE) |
| `ventes_nettes_millimes` | Ventes nettes | millimes | montant facturé − avoirs |
| `cout_achat_net_millimes` | Coût d'achat des unités nettes | millimes | (cartons facturés − cartons repris par avoir RETOUR) × coût d'achat unitaire, produit par produit |
| `marge_commerciale_millimes` | Marge commerciale | millimes | ventes nettes − coût d'achat des unités nettes |
| `taux_avoir` | Taux d'avoir | ratio | avoirs / montant facturé (en montant) |
| `unites_nettes` | Cartons nets | nombre | cartons facturés − cartons repris |
