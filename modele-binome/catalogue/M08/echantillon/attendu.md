# Échantillon TechniServ — le calcul à la main

12 lignes de `interventions.csv`, le catalogue complet des pièces et des taux, 4 équipements, 3 contrats et 7 consommations de pièces dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code. Les forfaits des contrats de l'échantillon sont réduits (1 200,000, 850,500 et 600,000 TND) pour garder des calculs simples. EQ-017 (contrat CT-03) n'a pas d'intervention en mars : il sert à la question de la règle à clarifier.

## 1. Décision ligne par ligne (`interventions.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | intervention_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | I-001 | 'EQ-001' · demande 2026-03-02 08:00 · intervention 2026-03-02 14:00 · 2 h · correctif | gardée |
| 3 | I-002 | 'EQ-004' · demande 02/03/2026 09:00 · intervention 03/03/2026 11:00 · 3 h · correctif | gardée |
| 4 | I-003 | ' eq-011 ' · demande 2026-02-20 08:00 · intervention 4 mars 2026 08:00 · 2 h · Préventif | gardée |
| 5 | I-004 | 'EQ-001' · demande 2026-03-05 10:00 · intervention 2026-03-05 13:00 · 1 h · correctif | gardée |
| 6 | I-004 | 'EQ-001' · demande 2026-03-05 10:00 · intervention 2026-03-05 13:00 · 1 h · correctif | ignorée : doublon exact de la ligne 5 |
| 7 | I-005 | 'EQ-004' · demande 2026-02-27 08:00 · intervention 2026-03-06 09:00 · 2 h · préventif | gardée |
| 8 | I-006 | 'EQ-001' · demande 2026-03-09 08:00 · intervention 2026-03-09 10:00 · 2 h · correctif | rejet `id_conflit` |
| 9 | I-006 | 'EQ-001' · demande 2026-03-09 08:00 · intervention 2026-03-09 10:00 · 3 h · correctif | rejet `id_conflit` |
| 10 | (vide) | 'EQ-004' · demande 2026-03-10 08:00 · intervention 2026-03-10 15:00 · 2 h · correctif | rejet `id_manquant` |
| 11 | I-007 | 'EQ-099' · demande 2026-03-10 09:00 · intervention 2026-03-11 09:00 · 1 h · correctif | rejet `cle_inconnue` |
| 12 | I-008 | 'EQ-011' · demande 2026-03-11 10:00 · intervention 2026-03-11 16:00 · 1,5 h · correctif | rejet `quantite_invalide` |
| 13 | I-009 | 'EQ-011' · demande 2026-03-09 16:00 · intervention 10/03/2026 10:00 · 4 h · correctif | gardée |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide` car `1,5` heure n'est pas un entier) → **6 interventions gardées**.

## 2. Pièces consommées (`operations.sqlite`, table `consommation`)

| consommation.id | intervention_id | Pièce | Calcul | Décision |
|---|---|---|---|---|
| 1 | I-001 | PC-101 | 2 × 35,000 | gardée : 70,000 TND |
| 2 | I-002 | PC-203 | 1 × 145,000 | gardée : 145,000 TND |
| 3 | I-003 | PC-301 | 6 × 18,250 | gardée : 109,500 TND |
| 4 | I-003 | PC-302 | 1 × 42,000 | gardée : 42,000 TND |
| 5 | I-009 | PC-305 | 1 × 310,000 | gardée : 310,000 TND |
| 6 | I-077 | PC-101 | 1 × 35,000 | rejet `cle_inconnue` (intervention I-077 inconnue) |
| 7 | I-004 | PC-999 | — | rejet `cle_inconnue` (pièce PC-999 absente du catalogue) |

Coût des pièces = **676,500 TND**.

## 3. Délai, main-d'œuvre, coût par intervention

Taux horaires (feuille `Taux horaires`) : Climatisation 45,000 TND/h · Ascenseur 62,500 TND/h · Groupe électrogène 55,000 TND/h.

| intervention_id | Équipement | Type | Demande → intervention | Délai | Main-d'œuvre | Pièces | Coût |
|---|---|---|---|---|---|---|---|
| I-001 | EQ-001 (Climatisation) | correctif | 2026-03-02 08:00 → 2026-03-02 14:00 | 6 h | 2 × 45,000 = 90,000 TND | 70,000 TND | 160,000 TND |
| I-002 | EQ-004 (Ascenseur) | correctif | 2026-03-02 09:00 → 2026-03-03 11:00 | 26 h | 3 × 62,500 = 187,500 TND | 145,000 TND | 332,500 TND |
| I-003 | EQ-011 (Groupe électrogène) | préventif | 2026-02-20 08:00 → 2026-03-04 08:00 | 288 h (exclu) | 2 × 55,000 = 110,000 TND | 151,500 TND | 261,500 TND |
| I-004 | EQ-001 (Climatisation) | correctif | 2026-03-05 10:00 → 2026-03-05 13:00 | 3 h | 1 × 45,000 = 45,000 TND | 0,000 TND | 45,000 TND |
| I-005 | EQ-004 (Ascenseur) | préventif | 2026-02-27 08:00 → 2026-03-06 09:00 | 169 h (exclu) | 2 × 62,500 = 125,000 TND | 0,000 TND | 125,000 TND |
| I-009 | EQ-011 (Groupe électrogène) | correctif | 2026-03-09 16:00 → 2026-03-10 10:00 | 18 h | 4 × 55,000 = 220,000 TND | 310,000 TND | 530,000 TND |

## 4. Les indicateurs

- Interventions = **6** (dont 4 correctives).
- Délai moyen (correctifs seulement) = (6 + 26 + 3 + 18) / 4 = 53 / 4 = **13,25 h**. Les deux préventifs (planifiés des jours à l'avance) sont exclus.
- Coût d'intervention = main-d'œuvre 777,500 TND + pièces 676,500 TND = **1 454,000 TND**.
- Revenu de contrat (mars 2026) = CT-01 1 200,000 + CT-02 850,500 + CT-03 600,000 = **2 650,500 TND** (3 lignes dans `fact_revenu_contrat`).
- Marge de service = revenu − coût = **1 196,500 TND** (marge partielle).

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_intervention` : 6 lignes · `fact_revenu_contrat` : 3 · `dim_equipement` : 4 · `dim_contrat` : 3 · `dim_date` : 31 jours (mars 2026). Rejets : 7 lignes (5 interventions + 2 consommations). Les mêmes nombres sont dans `attendu.json`.
