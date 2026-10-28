# Dictionnaire des données — Mission 10 (Pixel Studio)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `temps.csv` (csv)

Feuilles de temps exportées de l'outil de saisie (UTF-8, séparateur `;`).

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `temps_id` | texte | Identifiant de la ligne de temps. | `T26-00412` |
| `date_travail` | texte | Jour travaillé, trois formats possibles. | `04/03/2026` |
| `collaborateur` | texte | Code du collaborateur (casse et espaces variables). | ` c05 ` |
| `profil` | texte | Profil affiché dans l'outil de saisie (information seulement). | `développeur` |
| `projet` | texte | Code du projet. | `PX07` |
| `heures` | texte | Heures travaillées, point ou virgule décimale. | `7,5` |
| `tache` | texte | Tâche réalisée (avec accents). | `réunion client` |

### `couts.xlsx` (excel)

Feuille `Profils` (en-têtes à la ligne 3) + feuille `Collaborateurs`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Profil` | texte | Profil (feuille Profils). | `Chef de projet` |
| `Taux horaire coût (TND)` | nombre ou texte | Coût d'une heure du profil. | `41,000` |
| `Code` | texte | Code collaborateur (feuille Collaborateurs). | `C03` |
| `Nom` | texte | Nom et prénom (fictifs). | `Hela Mansour` |
| `Profil (Collaborateurs)` | texte | Profil du collaborateur, casse variable. | `DÉVELOPPEUR` |

### `projets.json` (json)

Référentiel des projets avec l'historique des chefs de projet.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `projets[].code` | texte | Code projet. | `PX07` |
| `projets[].nom` | texte | Nom du projet. | `Portail patients` |
| `projets[].client` | texte | Client (fictif). | `Clinique Les Jasmins Bleus` |
| `projets[].type` | texte | `forfait`, `régie` ou `interne` (casse variable). | `Régie` |
| `projets[].date_debut` | date ISO | Début du projet. | `2026-01-12` |
| `projets[].historique[].chef_projet` | texte | Chef de projet. | `Hela Mansour` |
| `projets[].historique[].valide_depuis` | date ISO | Début de ce chef (inclus). | `2026-01-12` |

### `facturation.sqlite` (sqlite)

Base de facturation : tables `facture`, `avoir`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `facture.id` | entier | Numéro interne de la ligne. | `12` |
| `facture.facture_id` | texte | Numéro de facture (unique). | `F26-0012` |
| `facture.code_projet` | texte | Projet facturé. | `PX04` |
| `facture.date_facture` | texte | Date de la facture. | `2026-02-28` |
| `facture.montant_ht` | réel | Montant hors taxes en TND. | `5236.5` |
| `facture.statut` | texte | `EMISE` ou `ANNULEE`. | `EMISE` |
| `facture.objet` | texte | Objet de la facture. | `Régie février 2026` |
| `avoir.id` | entier | Numéro interne de la ligne. | `3` |
| `avoir.avoir_id` | texte | Numéro d'avoir (unique). | `AV26-003` |
| `avoir.facture_id` | texte | Facture corrigée par l'avoir. | `F26-0012` |
| `avoir.date_avoir` | texte | Date de l'avoir. | `2026-03-09` |
| `avoir.montant_ht` | réel | Montant HT de l'avoir en TND (positif). | `500.0` |
| `avoir.motif` | texte | Raison de l'avoir. | `geste commercial` |

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

### `dim_collaborateur`

Collaborateurs avec leur profil et le taux horaire coût du profil (feuilles Collaborateurs + Profils).

| Colonne | Type | Description |
|---|---|---|
| `collaborateur_key` | INTEGER | Clé technique (1, 2, 3…). |
| `collaborateur_id` | TEXT | Code normalisé (strip + majuscules), ex. `C05`. |
| `nom` | TEXT | Nom et prénom (fictifs). |
| `profil` | TEXT | Profil normalisé en minuscules : `développeur`, `designer`, `chef de projet`, `consultant`. |
| `taux_horaire_millimes` | INTEGER | Taux horaire coût du profil, en millimes par heure (32,500 TND → 32500). |

### `dim_projet`

Projets avec historique du chef de projet (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `projet_key` | INTEGER | Clé technique d'une VERSION de projet. |
| `projet_id` | TEXT | Code projet, ex. `PX07` (plusieurs versions possibles). |
| `nom` | TEXT | Nom du projet. |
| `client` | TEXT | Client (fictif) ; `Pixel Studio` pour le projet interne. |
| `type_projet` | TEXT | `forfait`, `régie` ou `interne` (minuscules). |
| `chef_projet` | TEXT | Chef de projet de cette version (nom). |
| `date_debut` | TEXT | Date de début du projet, AAAA-MM-JJ. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_temps`

Une ligne de temps acceptée.

| Colonne | Type | Description |
|---|---|---|
| `temps_id` | TEXT | Identifiant de la ligne de temps (clé métier unique). |
| `date_key` | INTEGER | Jour travaillé. |
| `collaborateur_key` | INTEGER | Collaborateur. |
| `projet_key` | INTEGER | Version du projet valable le jour travaillé. |
| `tache` | TEXT | Tâche (texte de la source, espaces supprimés). |
| `heures_centiemes` | INTEGER | Heures en CENTIÈMES d'heure entiers (7,5 h → 750), > 0. |
| `taux_horaire_millimes` | INTEGER | Taux horaire coût du profil du collaborateur (millimes par heure). |
| `cout_charge_millimes` | INTEGER | heures_centiemes × taux_horaire_millimes / 100 (entier exact). |

### `fact_facture`

Une facture EMISE ou un avoir de la base de facturation.

| Colonne | Type | Description |
|---|---|---|
| `document_id` | TEXT | `facture_id` (F26-…) ou `avoir_id` (AV26-…), clé métier unique. |
| `type_document` | TEXT | `facture` ou `avoir`. |
| `facture_origine_id` | TEXT | Pour un avoir : la facture corrigée ; vide pour une facture. |
| `date_key` | INTEGER | Jour de la facture ou de l'avoir. |
| `projet_key` | INTEGER | Version du projet valable à la date du DOCUMENT. |
| `signe` | INTEGER | +1 pour une facture, −1 pour un avoir. |
| `montant_ht_millimes` | INTEGER | Montant hors taxes en millimes, toujours positif. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `heures_centiemes` | Heures | centièmes d'heure, 750 = 7,5 h | somme des heures des lignes de temps acceptées, en centièmes d'heure (750 = 7,5 h) |
| `cout_charge_millimes` | Coût de charge | millimes | somme de heures × taux horaire coût du profil du collaborateur |
| `factures_millimes` | Factures | millimes | somme des montants HT des factures EMISE acceptées |
| `avoirs_millimes` | Avoirs | millimes | somme des montants HT des avoirs acceptés |
| `facture_net_millimes` | Facturé net | millimes | factures − avoirs (montants HT) |
| `marge_contribution_millimes` | Marge de contribution | millimes | facturé net − coût de charge (ce n'est PAS un bénéfice : aucun frais général) |
