# Dictionnaire des données — Mission 09 (Scène Libre)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `billets.csv` (csv)

Billets exportés de la billetterie (UTF-8, séparateur `;`), une ligne = un billet.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `billet_id` | texte | Identifiant du billet. | `B100234` |
| `evenement` | texte | Code de l'événement (casse et espaces variables). | ` ev04 ` |
| `canal` | texte | Code du canal de vente. | `REV` |
| `date_vente` | texte | Date de la vente, trois formats possibles. | `04/03/2026` |
| `categorie` | texte | Catégorie de place : `VIP`, `CAT1` ou `CAT2`. | `cat2` |
| `nb_places` | texte | Nombre de places de la ligne : toujours 1. | `1` |
| `prix` | texte | Prix payé en TND (tarif réduit possible), formats variés. | `35,000` |

### `evenements.xlsx` (excel)

Feuille `Programme` (en-têtes à la ligne 3) + feuille `Tarifs`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Code` | texte | Code événement (une cellule mal saisie). | ` ev07` |
| `Événement` | texte | Nom du spectacle. | `Contes de la Médina` |
| `Type` | texte | `Concert`, `Théâtre` ou `Festival`. | `Théâtre` |
| `Lieu / Ville` | texte | Salle et ville. | `Salle Zéphyr / Sfax` |
| `Date` | date ou texte | Date (actuelle) du spectacle. | `4 avril 2026` |
| `Capacité` | nombre ou texte | Nombre de places de la salle pour ce spectacle. | `1 000` |
| `Statut` | texte | `programmé`, `reporté` ou `annulé` (information). | `reporté` |
| `Tarifs : Code événement / Catégorie / Tarif (TND)` | texte / nombre | Feuille Tarifs : prix plein par catégorie. | `EV03 / VIP / 80` |

### `canaux.json` (json)

Référentiel des canaux de vente avec l'historique des frais de distribution.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `canaux[].code` | texte | Code canal. | `REV` |
| `canaux[].libelle` | texte | Nom du canal. | `revendeur` |
| `canaux[].historique[].frais_distribution` | nombre ou texte | Frais en % du prix du billet. | `4,5 %` |
| `canaux[].historique[].valide_depuis` | date ISO | Début du taux (inclus). | `2025-09-01` |

### `remboursements.sqlite` (sqlite)

Base opérationnelle du service client : tables `remboursement`, `motif`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `remboursement.id` | entier | Numéro interne de la ligne. | `57` |
| `remboursement.numero` | texte | Numéro de la demande (unique). | `RB26-00057` |
| `remboursement.billet_id` | texte | `billet_id` du billet concerné. | `B100234` |
| `remboursement.date_operation` | texte | Date et heure de la décision. | `2026-04-12 10:15:00` |
| `remboursement.montant_rembourse` | réel | Montant rendu en TND (0 si rien n'est rendu). | `35.0` |
| `remboursement.code_motif` | texte | `ANNULATION`, `REPORT` ou `CONVENANCE` (convenance personnelle : toujours `REFUSE`, donc ignorée) → `motif`. | `REPORT` |
| `remboursement.statut` | texte | `REMBOURSE` (argent rendu), `CONSERVE` (billet gardé pour la nouvelle date) ou `REFUSE`. | `CONSERVE` |
| `remboursement.traite_par` | texte | Agent du service client. | `agent-2` |

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

### `dim_evenement`

Programme : un événement par ligne (feuille Programme).

| Colonne | Type | Description |
|---|---|---|
| `evenement_key` | INTEGER | Clé technique (1, 2, 3…). |
| `evenement_id` | TEXT | Code événement normalisé (strip + majuscules), ex. `EV07`. |
| `nom` | TEXT | Nom du spectacle. |
| `type_evenement` | TEXT | `Concert`, `Théâtre` ou `Festival`. |
| `lieu` | TEXT | Nom de la salle. |
| `ville` | TEXT | Ville de la salle. |
| `date_evenement` | TEXT | Date actuelle du spectacle (après un éventuel report), AAAA-MM-JJ. |
| `capacite` | INTEGER | Nombre de places mises en vente (entier). |

### `dim_canal`

Canaux de vente avec l'historique des frais de distribution (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `canal_key` | INTEGER | Clé technique d'une VERSION de canal. |
| `canal_id` | TEXT | Code canal, ex. `REV` (plusieurs versions possibles). |
| `libelle` | TEXT | Nom du canal, ex. `revendeur`. |
| `frais_pour_mille` | INTEGER | Frais de distribution de cette version en pour mille (9 % → 90). |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_billet`

Un billet vendu accepté.

| Colonne | Type | Description |
|---|---|---|
| `billet_id` | TEXT | Identifiant du billet (clé métier unique). |
| `date_key` | INTEGER | Jour de la vente. |
| `evenement_key` | INTEGER | Événement du billet. |
| `canal_key` | INTEGER | Version du canal valable à la date de vente. |
| `categorie` | TEXT | Catégorie de place normalisée : `VIP`, `CAT1`, `CAT2`. |
| `prix_millimes` | INTEGER | Prix payé en millimes (tarif réduit possible). |
| `frais_millimes` | INTEGER | prix_millimes × frais_pour_mille de la version / 1 000 (arrondi au millime). |

### `fact_remboursement`

Un remboursement `REMBOURSE` de la base du service client.

| Colonne | Type | Description |
|---|---|---|
| `remboursement_id` | TEXT | Numéro de la demande (`numero`), clé métier unique. |
| `billet_id` | TEXT | Billet remboursé. |
| `date_key` | INTEGER | Jour de l'opération (heure ignorée). |
| `evenement_key` | INTEGER | Événement du billet. |
| `canal_key` | INTEGER | Version du canal du billet valable à la date du REMBOURSEMENT. |
| `motif` | TEXT | `ANNULATION` ou `REPORT`. |
| `montant_millimes` | INTEGER | Montant rendu en millimes. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `billets_vendus` | Billets vendus | nombre | nombre de billets acceptés |
| `billets_rembourses` | Billets remboursés | nombre | nombre de remboursements acceptés (statut REMBOURSE, un par billet) |
| `billets_nets` | Billets nets | nombre | billets vendus − billets remboursés |
| `taux_remplissage` | Taux de remplissage | ratio | billets nets / capacité des événements (somme des capacités des événements concernés) |
| `recettes_billets_millimes` | Recettes des billets | millimes | somme des prix payés des billets acceptés |
| `remboursements_millimes` | Remboursements | millimes | somme des montants rendus des remboursements acceptés |
| `frais_distribution_millimes` | Frais de distribution | millimes | somme des frais des billets acceptés (taux du canal valable à la date de vente) |
| `recettes_nettes_millimes` | Recettes nettes | millimes | recettes des billets − remboursements − frais de distribution |
