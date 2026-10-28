# Dictionnaire des données — Mission 05 (Académie Nour)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `presences.csv` (csv)

Feuilles d'émargement exportées (UTF-8, séparateur `;`) : chaque inscrit figure à chaque séance tenue, avec `present` = 1 ou 0.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `presence_id` | texte | Identifiant de la ligne d'émargement. | `PRS-00412` |
| `session` | texte | Code de la session (casse et espaces variables). | ` ses-2604 ` |
| `participant` | texte | Code du participant. | `PA-0137` |
| `date_seance` | texte | Date de la séance, trois formats possibles. | `04/03/2026` |
| `present` | texte | 1 = présent, 0 = absent. | `1` |

### `catalogue.xlsx` (excel)

Feuille `Formations` (en-têtes à la ligne 3) : tarif, capacité et nombre de séances.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Code formation` | texte | Code de la formation (une cellule mal saisie). | ` f03` |
| `Intitulé` | texte | Nom de la formation. | `Comptabilité pratique` |
| `Domaine` | texte | Domaine. | `Gestion` |
| `Prix par participant (TND)` | nombre ou texte | Prix d'une inscription. | `450,000` |
| `Capacité (places)` | nombre ou texte | Places par session. | `14` |
| `Nombre de séances` | nombre ou texte | Séances par session. | `8` |

### `sessions.json` (json)

Planning des sessions avec l'historique du centre de rattachement.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `sessions[].code` | texte | Code de la session. | `SES-2619` |
| `sessions[].formation` | texte | Code de la formation. | `F04` |
| `sessions[].formateur` | texte | Formateur (nom inventé). | `Mme Olfa Chebbi` |
| `sessions[].date_debut` | texte | Date de la première séance (deux formats). | `2026-05-26` |
| `sessions[].rythme` | texte | Jours et horaires (information). | `mardi, 18 h – 21 h` |
| `sessions[].historique[].centre` | texte | Centre de rattachement. | `Sousse` |
| `sessions[].historique[].valide_depuis` | date ISO | Début de validité (inclus) : ouverture des inscriptions, puis date du changement. | `2026-04-21` |

### `operations.sqlite` (sqlite)

Base de gestion : tables `participant`, `inscription`, `paiement`, `remboursement`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `inscription.numero_inscription` | texte | Numéro de l'inscription (unique). | `INS-26-0042` |
| `inscription.code_session / participant_id` | texte | Session et participant. | `SES-2604 / PA-0137` |
| `inscription.statut` | texte | `CONFIRMEE` ou `ANNULEE`. | `CONFIRMEE` |
| `paiement.id / numero_paiement` | entier / texte | Ligne interne / numéro unique. | `57 / PAI-26-00057` |
| `paiement.numero_inscription` | texte | Inscription payée. | `INS-26-0042` |
| `paiement.date_paiement` | texte | Date et heure. | `2026-02-11 10:15:00` |
| `paiement.montant` | réel ou texte | Montant payé en TND. | `225.0` |
| `paiement.statut` | texte | `VALIDE` ou `ANNULE` (saisie annulée). | `VALIDE` |
| `remboursement.*` | — | Même structure : `numero_remboursement`, `numero_inscription`, `date_remboursement`, `montant`, `motif`, `statut`. | `RMB-26-0003` |

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

### `dim_formation`

Catalogue : une formation par ligne (feuille Formations).

| Colonne | Type | Description |
|---|---|---|
| `formation_key` | INTEGER | Clé technique (1, 2, 3…). |
| `formation_id` | TEXT | Code formation normalisé (strip + majuscules), ex. `F03`. |
| `intitule` | TEXT | Intitulé de la formation. |
| `domaine` | TEXT | Domaine, ex. `Données`. |
| `prix_millimes` | INTEGER | Prix par participant en millimes. |
| `capacite` | INTEGER | Places par session. |
| `nb_seances` | INTEGER | Nombre de séances d'une session. |

### `dim_session`

Sessions avec historique du centre de rattachement (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `session_key` | INTEGER | Clé technique d'une VERSION de session. |
| `session_id` | TEXT | Code session, ex. `SES-2619` (plusieurs versions possibles). |
| `formation_id` | TEXT | Code de la formation donnée dans la session. |
| `formateur` | TEXT | Formateur. |
| `date_debut` | TEXT | Date de la première séance, AAAA-MM-JJ. |
| `centre` | TEXT | Centre de rattachement de cette version : `Tunis`, `Sousse` ou `Sfax`. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_presence`

Une ligne d'émargement acceptée : un inscrit × une séance.

| Colonne | Type | Description |
|---|---|---|
| `presence_id` | TEXT | Identifiant de la ligne d'émargement (clé métier unique). |
| `date_key` | INTEGER | Jour de la séance. |
| `session_key` | INTEGER | Version de la session valable à la date de la séance. |
| `formation_key` | INTEGER | Formation de la session. |
| `participant_id` | TEXT | Code participant normalisé, ex. `PA-0137`. |
| `present` | INTEGER | 1 = présent, 0 = absent. |

### `fact_paiement`

Un paiement ou un remboursement VALIDE de la base de gestion.

| Colonne | Type | Description |
|---|---|---|
| `mouvement_id` | TEXT | `numero_paiement` ou `numero_remboursement` (clé métier unique). |
| `date_key` | INTEGER | Jour du mouvement (heure ignorée). |
| `session_key` | INTEGER | Version de la session de l'inscription valable à la date du MOUVEMENT. |
| `formation_key` | INTEGER | Formation de la session. |
| `inscription_id` | TEXT | `numero_inscription` concerné. |
| `type_mouvement` | TEXT | `paiement` ou `remboursement`. |
| `signe` | INTEGER | 1 pour un paiement, -1 pour un remboursement. |
| `montant_millimes` | INTEGER | Montant en millimes, toujours positif. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `inscrits` | Inscrits | nombre | nombre d'inscriptions distinctes de la session (participants de la feuille d'émargement), compté une fois par session, à la date de début de la session |
| `taux_assiduite` | Taux d'assiduité | ratio | présences / (inscrits × séances), soit la somme de `present` divisée par le nombre de lignes de présence (chaque inscrit figure à chaque séance tenue) |
| `taux_remplissage` | Taux de remplissage | ratio | inscrits / capacité (capacité du catalogue, une fois par session) |
| `paiements_millimes` | Paiements | millimes | somme des paiements VALIDE acceptés |
| `remboursements_millimes` | Remboursements | millimes | somme des remboursements VALIDE acceptés |
| `encaissements_nets_millimes` | Encaissements nets | millimes | paiements − remboursements |
| `encaissement_attendu_millimes` | Encaissement attendu | millimes | inscrits × prix par participant du catalogue |
| `taux_encaissement` | Taux d'encaissement | ratio | encaissements nets / encaissement attendu |
| `presences` | Présences | nombre | somme de `present` (séances suivies) |
