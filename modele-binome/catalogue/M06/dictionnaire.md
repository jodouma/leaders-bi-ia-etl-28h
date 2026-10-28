# Dictionnaire des données — Mission 06 (Dar Azur)

Ce dictionnaire décrit chaque colonne des sources, puis chaque colonne de l'entrepôt.

## Sources

### `sejours.csv` (csv)

Séjours exportés du logiciel de réception (séparateur `;`). `lot1` en UTF-8, **`lot2` en Windows-1252 (cp1252)**.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `sejour_id` | texte | Identifiant du séjour. | `DA-10234` |
| `date_reservation` | texte | Jour de la réservation, trois formats possibles. | `12/02/2026` |
| `date_arrivee` | texte | Jour d'arrivée (première nuit). | `2026-03-04` |
| `date_depart` | texte | Jour de départ (pas de nuit ce jour-là). | `7 mars 2026` |
| `etablissement` | texte | Code établissement (casse et espaces variables). | ` dah ` |
| `type_chambre` | texte | Code du type de chambre. | `DBL` |
| `canal` | texte | Code du canal de vente. | `OTA` |
| `nuitees` | texte | Nombre de nuits = départ − arrivée. | `3` |
| `prix_total` | texte | Prix du séjour en TND (taxe de séjour comprise), formats variés. | `1 007,000` |
| `provenance` | texte | Pays du client (avec accents). | `Algérie` |

### `chambres.xlsx` (excel)

Feuille `Chambres` (en-têtes à la ligne 3) + feuille `Types`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `Établissement` | texte | Code établissement (une cellule mal saisie). | ` dsb` |
| `Nom` | texte | Nom de l'établissement. | `Dar Azur Tozeur` |
| `Ville` | texte | Ville. | `Tozeur` |
| `Type de chambre` | texte | Code du type (feuille Types). | `FAM` |
| `Nombre de chambres` | nombre ou texte | Chambres de ce type dans l'établissement. | `6` |
| `Prix affiché (TND / nuit)` | nombre ou texte | Prix public indicatif (non utilisé). | `180,000` |
| `Code type / Libellé type` | texte | Feuille Types. | `FAM / Familiale` |

### `canaux.json` (json)

Contrats des canaux de vente avec l'historique du taux de commission.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `canaux[].code` | texte | Code canal. | `OTA` |
| `canaux[].libelle` | texte | `direct`, `agence en ligne`, `tour-opérateur`, `entreprise`. | `agence en ligne` |
| `canaux[].historique[].taux_commission` | nombre | Commission en % du prix total. | `18` |
| `canaux[].historique[].valide_depuis` | date ISO | Début du taux (inclus). | `2025-01-01` |

### `operations.sqlite` (sqlite)

Base opérationnelle : tables `annulation`, `motif_annulation`, `paiement`, `parametre`.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| `annulation.id` | entier | Numéro interne de la ligne. | `57` |
| `annulation.numero_annulation` | texte | Numéro de l'annulation (unique). | `AN26-0057` |
| `annulation.ref_sejour` | texte | `sejour_id` du séjour annulé. | `DA-10234` |
| `annulation.code_etablissement` | texte | Établissement du séjour. | `DDJ` |
| `annulation.date_annulation` | texte | Date et heure de l'annulation. | `2026-03-01 10:15:00` |
| `annulation.montant_rembourse` | réel | Montant rendu au client en TND (0 possible). | `395.25` |
| `annulation.code_motif` | texte | Motif → `motif_annulation`. | `PER` |
| `annulation.statut` | texte | `CONFIRMEE` ou `RETIREE` (le client a renoncé). | `CONFIRMEE` |
| `paiement.*` | — | Encaissements par séjour (non chargés ; variante 3). | `DA-10234 · 520.5 · carte` |

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

### `dim_etablissement`

Établissements : un par ligne, capacité = somme des chambres (feuille Chambres).

| Colonne | Type | Description |
|---|---|---|
| `etablissement_key` | INTEGER | Clé technique (1, 2, 3…). |
| `etablissement_id` | TEXT | Code établissement normalisé (strip + majuscules), ex. `DAH`. |
| `nom` | TEXT | Nom de l'établissement. |
| `ville` | TEXT | Ville. |
| `nombre_chambres` | INTEGER | Capacité : somme des chambres de tous les types de l'établissement. |

### `dim_canal`

Canaux de vente avec historique du taux de commission (SCD2).

| Colonne | Type | Description |
|---|---|---|
| `canal_key` | INTEGER | Clé technique d'une VERSION de canal. |
| `canal_id` | TEXT | Code canal, ex. `OTA` (plusieurs versions possibles). |
| `libelle` | TEXT | `direct`, `agence en ligne`, `tour-opérateur` ou `entreprise`. |
| `taux_commission_pct` | INTEGER | Commission de cette version, en % entier du prix total (ex. 18). |
| `valid_from` | TEXT | Début de validité (inclus), AAAA-MM-JJ. |
| `valid_to` | TEXT | Fin de validité (exclue), vide = version courante. |

### `fact_sejour`

Un séjour accepté (date du fait = date d'arrivée).

| Colonne | Type | Description |
|---|---|---|
| `sejour_id` | TEXT | Identifiant du séjour (clé métier unique). |
| `date_key` | INTEGER | Jour d'ARRIVÉE du séjour. |
| `etablissement_key` | INTEGER | Établissement du séjour. |
| `canal_key` | INTEGER | Version du canal valable à la date d'arrivée. |
| `type_chambre` | TEXT | Code du type de chambre normalisé, ex. `DBL`. |
| `date_reservation` | TEXT | Jour de la réservation, AAAA-MM-JJ (peut être en 2025). |
| `date_depart` | TEXT | Jour de départ, AAAA-MM-JJ (pas de nuit ce jour-là). |
| `nuitees` | INTEGER | Nombre de nuits (entier > 0) = départ − arrivée. |
| `montant_millimes` | INTEGER | Prix total du séjour en millimes. |
| `commission_millimes` | INTEGER | montant_millimes × taux_commission_pct (version à l'arrivée) / 100. |

### `fact_annulation`

Une annulation CONFIRMEE de la base opérationnelle.

| Colonne | Type | Description |
|---|---|---|
| `annulation_id` | TEXT | Numéro de l'annulation (`numero_annulation`), clé métier unique. |
| `sejour_id` | TEXT | Séjour annulé. |
| `date_key` | INTEGER | Jour d'ARRIVÉE du séjour annulé (pas la date d'annulation). |
| `etablissement_key` | INTEGER | Établissement du séjour annulé. |
| `canal_key` | INTEGER | Même version de canal que le séjour annulé. |
| `date_annulation` | TEXT | Jour de l'annulation, AAAA-MM-JJ (heure ignorée). |
| `nuitees` | INTEGER | Nuitées du séjour annulé (elles ne sont plus vendues). |
| `remboursement_millimes` | INTEGER | Montant remboursé en millimes (0 possible). |

## Indicateurs

| Code | Libellé | Unité | Formule |
|---|---|---|---|
| `nuitees_vendues` | Nuitées vendues | nombre | nuitées des séjours acceptés − nuitées des séjours annulés (annulations CONFIRMEE acceptées) |
| `chambres_disponibles` | Chambres disponibles (chambres × nuits) | nombre | nombre de chambres de l'établissement × nombre de nuits de la période (jours de dim_date) |
| `taux_occupation` | Taux d'occupation | ratio | nuitées vendues / (chambres × nuits de la période) |
| `montant_sejours_millimes` | Montant des séjours | millimes | somme des prix totaux des séjours acceptés |
| `remboursements_millimes` | Remboursements | millimes | somme des montants remboursés des annulations CONFIRMEE acceptées |
| `revenu_net_millimes` | Revenu net d'annulations | millimes | montant des séjours − remboursements |
| `revpar_millimes` | RevPAR | millimes | revenu net / (chambres × nuits de la période), en TND par chambre disponible, arrondi au millime |
| `commissions_millimes` | Commissions des canaux | millimes | somme de montant × taux de commission (version valable à la date d'arrivée) / 100 |
| `sejours` | Séjours acceptés | nombre | nombre de lignes de fact_sejour |
