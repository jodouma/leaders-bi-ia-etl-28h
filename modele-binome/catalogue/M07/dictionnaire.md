# Dictionnaire des données — Mission 07 (FibreNet)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `facturation.csv` (csv)

Factures mensuelles exportées de la facturation (UTF-8, séparateur `;`).

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `facture_id` | texte | Numéro de facture (unique). | `F26-000412` |
| `abonnement_id` | texte | Abonnement facturé (→ base des abonnements). | `AB00137` |
| `compte` | texte | Numéro de compte client (casse et espaces variables). | ` c0042` |
| `offre` | texte | Code de l'offre (casse variable). | `FN-F100` |
| `mois_facture` | texte | Mois facturé, AAAA-MM. | `2026-03` |
| `date_facture` | texte | Date d'émission, trois formats possibles. | `01/03/2026` |
| `nb_mois` | texte | Nombre de mensualités facturées (toujours 1 si la ligne est juste). | `1` |
| `montant` | texte | Montant facturé en TND, formats variés. | `69,900` |

### `comptes.xlsx` (excel)

Feuille `Comptes` (titre au-dessus, en-têtes à la ligne 3).

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `N° compte` | texte | Numéro de compte (une cellule mal saisie). | ` c0017` |
| `Nom / raison sociale` | texte | Nom inventé du client (accents). | `Atelier Yasmine Déco` |
| `Type de compte` | texte | `particulier` ou `entreprise`, casse variable. | ` Entreprise ` |
| `Ville` | texte | Ville du compte. | `Sousse` |
| `Client depuis` | date | Date d'ouverture du compte. | `2024-05-12` |

### `offres.json` (json)

Catalogue des offres avec l'historique de gamme et de prix.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `offres[].code` | texte | Code de l'offre. | `FN-F300` |
| `offres[].nom` | texte | Nom commercial. | `Fibre 300` |
| `offres[].historique[].gamme` | texte | Gamme (casse variable). | `Confort` |
| `offres[].historique[].prix_mensuel` | texte ou nombre | Prix mensuel en TND. | `89,900` |
| `offres[].historique[].valide_depuis` | date ISO | Début de la version (inclus). | `2024-03-01` |

### `abonnements.sqlite` (sqlite)

Base opérationnelle : tables `abonnement`, `motif_resiliation`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `abonnement.id` | entier | Numéro interne de la ligne. | `137` |
| `abonnement.abonnement_id` | texte | Identifiant de l'abonnement (unique). | `AB00137` |
| `abonnement.num_compte` | texte | Compte titulaire. | `C0042` |
| `abonnement.code_offre` | texte | Offre souscrite (casse variable). | ` fn-f20` |
| `abonnement.date_debut` | texte ISO | Premier jour de service. | `2025-11-03` |
| `abonnement.date_fin` | texte ISO ou NULL | Dernier jour de service ; NULL = toujours actif. | `2026-03-31` |
| `abonnement.statut` | texte | `ACTIF`, `RESILIE` ou `ANNULE` (jamais installé). | `RESILIE` |
| `abonnement.code_motif` | texte ou NULL | Motif de résiliation → `motif_resiliation`. | `DEM` |

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

### `dim_compte`

Comptes clients (feuille Comptes de `comptes.xlsx`).

| Colonne | Type | Description |
|---|---|---|
| `compte_key` | INTEGER | Clé technique (1, 2, 3…). |
| `compte_id` | TEXT | Numéro de compte normalisé (strip + majuscules), ex. `C0042`. |
| `nom` | TEXT | Nom ou raison sociale (inventé). |
| `type_compte` | TEXT | `particulier` ou `entreprise` (strip + minuscules). |
| `ville` | TEXT | Ville du compte. |

### `dim_offre`

Offres avec l'historique de la gamme et du prix mensuel (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `offre_key` | INTEGER | Clé technique d'une VERSION d'offre. |
| `offre_id` | TEXT | Code de l'offre, ex. `FN-F300` (plusieurs versions possibles). |
| `nom` | TEXT | Nom commercial. |
| `gamme` | TEXT | `essentiel`, `confort` ou `pro` pour cette version (minuscules). |
| `prix_mensuel_millimes` | INTEGER | Prix mensuel de cette version en millimes. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_facture`

Une facture mensuelle acceptée de `facturation.csv`.

| Colonne | Type | Description |
|---|---|---|
| `facture_id` | TEXT | Numéro de facture (clé métier unique). |
| `date_key` | INTEGER | Jour de la facture. |
| `compte_key` | INTEGER | Compte facturé. |
| `offre_key` | INTEGER | Version de l'offre valable à la date de la facture. |
| `abonnement_id` | TEXT | Abonnement facturé (clé métier de la base opérationnelle). |
| `mois_facture` | TEXT | Mois facturé, AAAA-MM. |
| `nb_mois` | INTEGER | Mensualités facturées (entier > 0). |
| `montant_millimes` | INTEGER | Montant facturé en millimes. |

### `fact_abonnement_mois`

Un abonnement × un mois où il est actif au moins un jour (fait DÉRIVÉ des dates de début et de fin, voir § 13).

| Colonne | Type | Description |
|---|---|---|
| `abonnement_mois_id` | TEXT | `<abonnement_id>-<AAAA-MM>` (clé métier unique). |
| `abonnement_id` | TEXT | Abonnement (clé métier de la base opérationnelle). |
| `date_key` | INTEGER | DERNIER jour du mois (ex. 20260331). |
| `compte_key` | INTEGER | Compte titulaire. |
| `offre_key` | INTEGER | Version de l'offre valable le dernier jour du mois. |
| `actif_debut` | INTEGER | 1 si actif le dernier jour du mois précédent, sinon 0. |
| `nouveau` | INTEGER | 1 si `date_debut` tombe dans le mois, sinon 0. |
| `depart` | INTEGER | 1 si `date_fin` tombe dans le mois, sinon 0. |
| `actif_fin` | INTEGER | 1 si actif le dernier jour du mois (`date_fin` vide ou après), sinon 0. |
| `mensualite_millimes` | INTEGER | Prix mensuel de la version `offre_key`, en millimes. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `actifs_fin_mois` | Abonnés actifs fin de mois | nombre | nombre d'abonnements actifs le dernier jour du mois (`actif_fin` = 1) — valeur d'**un** mois : lisez l'agrégat `par_mois` ; sur plusieurs mois, le total de la référence additionne les fins de mois (abonnés-mois) |
| `mrr_millimes` | MRR (revenu mensuel récurrent) | millimes | somme des mensualités des abonnements actifs en fin de mois, au prix de la version de l'offre valable le dernier jour du mois |
| `departs` | Départs du mois | nombre | nombre d'abonnements dont la `date_fin` tombe dans le mois |
| `taux_depart` | Taux de départ | ratio | départs du mois / abonnés actifs en début de mois (sur plusieurs mois : somme des départs / somme des actifs de début de mois) |
| `actifs_debut_mois` | Abonnés actifs début de mois | nombre | abonnements actifs le dernier jour du mois précédent (`actif_debut` = 1) |
| `nouveaux` | Nouveaux abonnements | nombre | abonnements dont la `date_debut` tombe dans le mois |
| `facture_millimes` | Montant facturé | millimes | somme des montants des factures acceptées, rangées dans le mois de leur date de facture |
