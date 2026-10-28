# Dictionnaire des données — Mission 04 (Colis Rapide)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `colis.csv` (csv)

Suivi des colis livrés exporté du logiciel des agences (UTF-8, séparateur `;`).

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `colis_id` | texte | Numéro du colis (clé métier). | `CR100234` |
| `date_expedition` | texte | Jour où l'agence a pris le colis, trois formats possibles. | `02/03/2026` |
| `date_promise` | texte | Jour de livraison promis au client. | `5 mars 2026` |
| `date_livraison` | texte | Jour où le colis a été livré (date du fait). | `2026-03-06` |
| `agence` | texte | Code de l'agence qui a expédié le colis (casse et espaces variables). | ` nab ` |
| `zone_destination` | texte | Code de la zone de destination (sert au tarif). | `SU` |
| `poids_kg` | texte | Poids en kg, formats décimaux variés. | `2,35` |
| `service` | texte | Code du service : STD, EXP ou ECO. | `EXP` |
| `ville_destination` | texte | Ville du destinataire (avec accents). | `Médenine` |

### `tarifs.xlsx` (excel)

Feuilles `Grille` (en-têtes à la ligne 3), `Tranches`, `Zones`, `Services`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Grille : Zone / Tranche` | texte | Code zone et code tranche (une cellule mal saisie). | ` su / T3` |
| `Grille : Prix facturé (TND)` | nombre ou texte | Prix catalogue d'un colis Standard. | `19,500` |
| `Grille : Coût transporteur (TND)` | nombre ou texte | Ce que coûte le transport du colis. | `15.3` |
| `Tranches : Poids min (kg, exclu) / Poids max (kg, inclus)` | nombre | Bornes de la tranche. | `5 / 10` |
| `Zones : Code zone / Libellé zone` | texte | Traduction des codes. | `SU / Sud` |
| `Services : Code / Libellé / Délai promis (jours) / Coefficient prix (%)` | texte et nombre | Les trois services. | `EXP / Express / 1 / 150` |

### `agences.json` (json)

Référentiel des agences avec l'historique de leur zone de rattachement.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `agences[].code` | texte | Code agence. | `NAB` |
| `agences[].nom` | texte | Nom. | `Colis Rapide Nabeul` |
| `agences[].ville` | texte | Ville de l'agence. | `Nabeul` |
| `agences[].historique[].zone` | texte | Zone de rattachement. | `Nord` |
| `agences[].historique[].valide_depuis` | date | Début de la zone (inclus), ISO ou JJ/MM/AAAA. | `2020-09-01` |

### `facturation.sqlite` (sqlite)

Base opérationnelle de facturation : tables `facture`, `penalite`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `facture.id` | entier | Numéro interne de la ligne. | `57` |
| `facture.numero_facture` | texte | Numéro de facture (unique). | `FA26-000057` |
| `facture.colis_id` | texte | Colis facturé. | `CR100234` |
| `facture.date_facture` | texte | Date et heure de la facture. | `2026-03-07 10:15:00` |
| `facture.montant_facture` | réel | Montant facturé au client en TND. | `17.25` |
| `facture.statut` | texte | `EMISE`, `PAYEE` ou `ANNULEE`. | `PAYEE` |
| `penalite.id / numero_penalite` | entier / texte | Ligne et numéro de la pénalité. | `PE26-00012` |
| `penalite.colis_id` | texte | Colis livré en retard. | `CR100234` |
| `penalite.jours_retard` | entier | Jours de retard constatés par la facturation. | `2` |
| `penalite.montant_penalite` | réel | Pénalité remboursée au client en TND (10 % par jour de retard, 5 jours au plus, rien pour ECO). | `2.8` |
| `penalite.statut` | texte | `APPLIQUEE` ou `ANNULEE`. | `APPLIQUEE` |

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

### `dim_agence`

Agences avec l'historique de leur zone de rattachement (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `agence_key` | INTEGER | Clé technique d'une VERSION d'agence. |
| `agence_id` | TEXT | Code agence normalisé, ex. `NAB` (plusieurs versions possibles). |
| `nom` | TEXT | Nom de l'agence. |
| `ville` | TEXT | Ville de l'agence. |
| `zone` | TEXT | Zone de rattachement de cette version, ex. `Nord`. |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `dim_service`

Les trois services (feuille Services).

| Colonne | Type | Description |
|---|---|---|
| `service_key` | INTEGER | Clé technique (1, 2, 3). |
| `service_id` | TEXT | Code service normalisé : `STD`, `EXP`, `ECO`. |
| `libelle` | TEXT | Libellé, ex. `Express`. |
| `delai_promis_jours` | INTEGER | Délai promis au client en jours. |
| `coefficient_prix_pct` | INTEGER | Coefficient appliqué au prix de la grille, en % (Express = 150). |

### `dim_tarif`

Grille tarifaire : une ligne par zone de destination × tranche de poids (16 lignes).

| Colonne | Type | Description |
|---|---|---|
| `tarif_key` | INTEGER | Clé technique. |
| `tarif_id` | TEXT | Code zone + `-` + code tranche, ex. `SU-T3`. |
| `zone_destination` | TEXT | Libellé de la zone de destination (feuille Zones), ex. `Sud`. |
| `tranche` | TEXT | Code tranche de poids : `T1` … `T4`. |
| `tranche_libelle` | TEXT | Libellé de la tranche (feuille Tranches). |
| `poids_min_grammes` | INTEGER | Borne basse de la tranche en grammes (exclue). |
| `poids_max_grammes` | INTEGER | Borne haute de la tranche en grammes (incluse). |
| `prix_millimes` | INTEGER | Prix de la grille (service Standard) en millimes. |
| `cout_transporteur_millimes` | INTEGER | Coût transporteur en millimes. |

### `fact_colis`

Un colis livré accepté, complété par sa facture et ses pénalités.

| Colonne | Type | Description |
|---|---|---|
| `colis_id` | TEXT | Numéro du colis (clé métier unique). |
| `date_key` | INTEGER | Jour de LIVRAISON (date du fait). |
| `agence_key` | INTEGER | Version de l'agence valable à la date de livraison. |
| `service_key` | INTEGER | Service du colis. |
| `tarif_key` | INTEGER | Ligne de grille : zone de destination × tranche du poids. |
| `date_expedition` | TEXT | Date d'expédition ISO AAAA-MM-JJ. |
| `date_promise` | TEXT | Date de livraison promise ISO AAAA-MM-JJ. |
| `poids_grammes` | INTEGER | Poids en grammes entiers (0 < poids ≤ 30 000). |
| `retard_jours` | INTEGER | max(0, date_livraison − date_promise) en jours calendaires. |
| `a_l_heure` | INTEGER | 1 si date_livraison ≤ date_promise, sinon 0. |
| `montant_facture_millimes` | INTEGER | Montant de la facture EMISE ou PAYEE du colis, en millimes. |
| `penalite_millimes` | INTEGER | Somme des pénalités APPLIQUEE du colis, en millimes (0 si aucune). |
| `cout_transporteur_millimes` | INTEGER | Coût de la grille pour ce tarif, en millimes. |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `colis_livres` | Colis livrés | nombre | nombre de colis acceptés dans `fact_colis` |
| `colis_a_l_heure` | Colis à l'heure | nombre | colis avec date_livraison ≤ date_promise (livré le jour promis = à l'heure) |
| `ponctualite` | Ponctualité | ratio | colis à l'heure / colis livrés |
| `retard_moyen_jours` | Retard moyen | jours, nombre décimal | somme des jours de retard / nombre de colis EN RETARD (les colis à l'heure ne comptent pas) ; jours de retard = date_livraison − date_promise, en jours calendaires |
| `montant_facture_millimes` | Montant facturé | millimes | somme des montants des factures EMISE ou PAYEE des colis acceptés |
| `penalites_millimes` | Pénalités de retard | millimes | somme des pénalités APPLIQUEE des colis acceptés |
| `revenu_net_millimes` | Revenu facturé net de pénalités | millimes | montant facturé − pénalités de retard |
| `cout_transporteur_millimes` | Coût transporteur | millimes | somme du coût transporteur de la grille (zone de destination × tranche de poids) des colis acceptés |
| `marge_livraison_millimes` | Marge de livraison | millimes | revenu facturé net de pénalités − coût transporteur (marge partielle : ni salaires, ni loyers, ni carburant des agences ; ce n'est pas un bénéfice) |
