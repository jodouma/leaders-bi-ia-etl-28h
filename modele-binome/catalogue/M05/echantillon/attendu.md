# Échantillon Académie Nour — le calcul à la main

12 lignes de `presences.csv` (les deux premières séances de la session SES-2690, Marketing digital à Tunis), le catalogue complet, 1 session dans `sessions.json`, 4 inscriptions, 6 paiements et 1 remboursement dans `operations.sqlite`. Faites le calcul **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`presences.csv`)

La ligne 1 du fichier est l'en-tête. `pa-0901`, ` ses-2690 ` et `Ses-2690` deviennent `PA-0901` et `SES-2690` (espaces enlevés, majuscules). `SES-2699` n'existe pas dans `sessions.json`.

| Ligne du fichier | presence_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | PRS-E01 | 'SES-2690' · 'PA-0901' · 2026-03-02 · present 1 | gardée |
| 3 | PRS-E02 | 'SES-2690' · 'PA-0902' · 02/03/2026 · present 1 | gardée |
| 4 | PRS-E03 | ' ses-2690 ' · 'PA-0903' · 2 mars 2026 · present 0 | gardée |
| 5 | PRS-E04 | 'SES-2690' · 'pa-0901' · 2026-03-04 · present 1 | gardée |
| 6 | PRS-E04 | 'SES-2690' · 'pa-0901' · 2026-03-04 · present 1 | ignorée : doublon exact de la ligne 5 |
| 7 | PRS-E05 | 'SES-2690' · 'PA-0902' · 04/03/2026 · present 0 | gardée |
| 8 | PRS-E06 | 'Ses-2690' · 'PA-0903' · 2026-03-04 · present 0 | gardée |
| 9 | PRS-E07 | 'SES-2690' · 'PA-0901' · 2026-03-04 · present 1 | rejet `id_conflit` |
| 10 | PRS-E07 | 'SES-2690' · 'PA-0901' · 2026-03-04 · present 0 | rejet `id_conflit` |
| 11 | (vide) | 'SES-2690' · 'PA-0902' · 2026-03-04 · present 1 | rejet `id_manquant` |
| 12 | PRS-E08 | 'SES-2699' · 'PA-0901' · 2026-03-04 · present 1 | rejet `cle_inconnue` |
| 13 | PRS-E09 | 'SES-2690' · 'PA-0902' · 2026-03-04 · present 2 | rejet `quantite_invalide` |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées** : 3 participants × 2 séances (2 et 4 mars).

## 2. Inscrits, assiduité, remplissage

| Participant | 2 mars | 4 mars | Présences |
|---|---|---|---|
| PA-0901 | 1 | 1 | 2 |
| PA-0902 | 1 | 0 | 1 |
| PA-0903 | 0 | 0 | 0 (a payé, n'est jamais venu) |

- Inscrits = participants distincts de la feuille = **3** (PA-0903 compte : décision (1) A de la direction). PA-0904 a annulé : il n'est pas sur la feuille.
- Taux d'assiduité = présences / (inscrits × séances tenues) = 3 / (3 × 2) = **50,00 %**.
- Taux de remplissage = inscrits / capacité = 3 / 20 (capacité de F06 dans le catalogue) = **15,00 %**.
- Si l'on avait exclu PA-0903 (option B) : 2 inscrits, assiduité 3 / 4 = 75,00 %, remplissage 10,00 %. Ce n'est pas la règle retenue.

## 3. Paiements et remboursements (`operations.sqlite`)

- `PAI-E1` 320,000 + `PAI-E2` 160,000 (acompte) + `PAI-E3` `320,000` (montant stocké en texte avec virgule) + `PAI-E4` 320,000 (inscription annulée, payée puis remboursée) = **1 120,000 TND**.
- `PAI-E5` : statut `ANNULE` → ignoré (ce n'est pas un rejet).
- `PAI-E6` : l'inscription `INS-E9` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).
- `RMB-E1` : remboursement de l'inscription annulée = **320,000 TND**.

**Encaissements nets = 1 120,000 TND − 320,000 TND = 800,000 TND.**

Encaissement attendu = inscrits × prix = 3 × 320,000 = 960,000 TND → taux d'encaissement = 83,33 % (PA-0902 n'a payé que l'acompte).

## 4. Ce que doit contenir l'entrepôt de l'échantillon

`fact_presence` : 6 lignes · `fact_paiement` : 5 lignes (4 paiements avec `signe` = 1, 1 remboursement avec `signe` = -1) · `dim_formation` : 7 · `dim_session` : 1 · `dim_date` : 59 jours (février et mars 2026, car les paiements commencent en février). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
