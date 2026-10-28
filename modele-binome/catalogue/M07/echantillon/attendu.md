# Échantillon FibreNet — le calcul à la main (mars 2026)

12 lignes de `facturation.csv`, 5 comptes, les 5 offres, 8 abonnements dans `abonnements.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`facturation.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | facture_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | F-E001 | AB-E01 · 'C0001' · FN-F20 · 2026-03-01 · nb_mois 1 · 39.900 | gardée |
| 3 | F-E002 | AB-E02 · 'c0002' · fn-f100 · 01/03/2026 · nb_mois 1 · 69,900 | gardée |
| 4 | F-E003 | AB-E03 · 'C0003' · FN-F300 · 10 mars 2026 · nb_mois 1 · 89.9 | gardée |
| 5 | F-E004 | AB-E04 · 'C0004' · FN-PRO1G · 2026-03-01 · nb_mois 1 · 149,000 | gardée |
| 6 | F-E004 | AB-E04 · 'C0004' · FN-PRO1G · 2026-03-01 · nb_mois 1 · 149,000 | ignorée : doublon exact de la ligne 5 |
| 7 | F-E005 | AB-E05 · ' C0005 ' · FN-F50 · 2026-03-01 · nb_mois 1 · 49,9 | gardée |
| 8 | F-E006 | AB-E06 · 'C0003' · FN-F300 · 2026-03-01 · nb_mois 1 · 89,900 | gardée |
| 9 | F-E007 | AB-E01 · 'C0001' · FN-F20 · 2026-03-01 · nb_mois 1 · 39.900 | rejet `id_conflit` |
| 10 | F-E007 | AB-E01 · 'C0001' · FN-F20 · 2026-03-01 · nb_mois 2 · 79.800 | rejet `id_conflit` |
| 11 | (vide) | AB-E05 · 'C0005' · FN-F50 · 2026-03-01 · nb_mois 1 · 49.900 | rejet `id_manquant` |
| 12 | F-E008 | AB-E08 · 'C0999' · FN-F20 · 2026-03-05 · nb_mois 1 · 39.900 | rejet `cle_inconnue` |
| 13 | F-E009 | AB-E06 · 'C0003' · FN-F300 · 2026-03-01 · nb_mois 0 · 89.900 | rejet `quantite_invalide` |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 factures gardées**.

## 2. Montant facturé en mars

`89.9` = `89,900` = 89 900 millimes ; `49,9` = 49 900 millimes. Somme des 6 factures : 39,900 + 69,900 + 89,900 + 149,000 + 49,900 + 89,900 = **488,500 TND**.

## 3. Les abonnements du mois : la ligne dérivée de `fact_abonnement_mois`

Règle : actif début de mois = actif le 28 février ; nouveau = début en mars ; départ = fin en mars ; actif fin de mois = début ≤ 31 mars **et** (fin vide **ou** fin **après** le 31 mars). `AB-E02` finit le 31 mars : c'est un départ de mars et il n'est **pas** actif fin mars (règle à clarifier, décision B).

| Abonnement | Offre | date_debut | date_fin | actif_debut · nouveau · départ · actif_fin | MRR de mars |
|---|---|---|---|---|---|
| AB-E01 | FN-F20 | 2025-06-10 | (vide) | 1 · 0 · 0 · 1 | 39,900 TND |
| AB-E02 | FN-F100 | 2025-09-01 | 2026-03-31 | 1 · 0 · 1 · 0 | 0 |
| AB-E03 | FN-F300 | 2026-03-10 | (vide) | 0 · 1 · 0 · 1 | 89,900 TND |
| AB-E04 | FN-PRO1G | 2024-11-04 | 2026-03-15 | 1 · 0 · 1 · 0 | 0 |
| AB-E05 | FN-F50 | 2025-12-01 | (vide) | 1 · 0 · 0 · 1 | 49,900 TND |
| AB-E06 | FN-F300 | 2025-02-03 | (vide) | 1 · 0 · 0 · 1 | 89,900 TND |
| AB-E07 | FN-F50 | 2026-03-20 | (vide) | ignoré : `ANNULE` | 0 |
| AB-E08 | FN-F20 | 2026-03-05 | (vide) | rejet `cle_inconnue` (compte C0999 inconnu) | 0 |

## 4. Les indicateurs de mars

- Actifs début de mois = **5** ; nouveaux = **1** ; départs = **2**.
- Abonnés actifs fin de mois = 5 + 1 − 2 = **4**.
- MRR = 39,900 + 89,900 + 49,900 + 89,900 = **269,600 TND** (les deux départs ne comptent pas).
- Taux de départ = départs / actifs début = 2 / 5 = **40,00 %**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_facture` : 6 lignes · `fact_abonnement_mois` : 6 lignes · `dim_compte` : 5 · `dim_offre` : 5 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
