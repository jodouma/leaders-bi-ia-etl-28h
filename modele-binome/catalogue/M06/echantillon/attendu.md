# Échantillon Dar Azur — le calcul à la main

12 lignes de `sejours.csv`, l'inventaire complet des chambres (4 établissements, 64 chambres), les 4 canaux et 3 annulations dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`sejours.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | sejour_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | E-01 | arrivée 2026-03-02 · départ 2026-03-05 · 'DAH' · DBL · DIR · 3 nuit(s) · 520.500 | gardée |
| 3 | E-02 | arrivée 03/03/2026 · départ 05/03/2026 · 'DSB' · STE · OTA · 2 nuit(s) · 1 007,000 | gardée |
| 4 | E-03 | arrivée 6 mars 2026 · départ 10 mars 2026 · ' dtz ' · TWN · TOP · 4 nuit(s) · 614 | gardée |
| 5 | E-04 | arrivée 2026-03-07 · départ 2026-03-08 · 'DDJ' · FAM · ENT · 1 nuit(s) · 213,5 | gardée |
| 6 | E-04 | arrivée 2026-03-07 · départ 2026-03-08 · 'DDJ' · FAM · ENT · 1 nuit(s) · 213,5 | ignorée : doublon exact de la ligne 5 |
| 7 | E-05 | arrivée 2026-03-12 · départ 2026-03-15 · 'DAH' · fam · Ota · 3 nuit(s) · 790,500 | gardée |
| 8 | E-06 | arrivée 2026-03-14 · départ 2026-03-16 · 'DDJ' · DBL · DIR · 2 nuit(s) · 390.000 | rejet `id_conflit` |
| 9 | E-06 | arrivée 2026-03-14 · départ 2026-03-16 · 'DDJ' · DBL · DIR · 3 nuit(s) · 390.000 | rejet `id_conflit` |
| 10 | (vide) | arrivée 2026-03-18 · départ 2026-03-20 · 'DAH' · TWN · DIR · 2 nuit(s) · 347.000 | rejet `id_manquant` |
| 11 | E-07 | arrivée 2026-03-19 · départ 2026-03-21 · 'DMH' · DBL · OTA · 2 nuit(s) · 367.000 | rejet `cle_inconnue` |
| 12 | E-08 | arrivée 2026-03-22 · départ 2026-03-22 · 'DTZ' · DBL · DIR · 0 nuit(s) · 0.000 | rejet `quantite_invalide` |
| 13 | E-09 | arrivée 30/03/2026 · départ 02/04/2026 · 'DSB' · DBL · DIR · 3 nuit(s) · 685,5 | gardée |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 séjours gardés**.

## 2. Séjours, montants et commissions

Une virgule ou un point sépare les décimales ; un espace sépare les milliers : `1 007,000` = 1 007 TND. Le taux de commission est celui du canal **à la date d'arrivée** (ici, avant le 15 juillet : direct 0 %, entreprise 10 %, agence en ligne 18 %, tour-opérateur 25 %).

| sejour_id | Arrivée | Établissement | Canal (taux) | Nuitées | Montant | Commission |
|---|---|---|---|---|---|---|
| E-01 | 2026-03-02 | DAH | DIR (0 %) | 3 | 520,500 TND | 520,500 × 0 / 100 = 0,000 TND |
| E-02 | 2026-03-03 | DSB | OTA (18 %) | 2 | 1 007,000 TND | 1007,000 × 18 / 100 = 181,260 TND |
| E-03 | 2026-03-06 | DTZ | TOP (25 %) | 4 | 614,000 TND | 614,000 × 25 / 100 = 153,500 TND |
| E-04 | 2026-03-07 | DDJ | ENT (10 %) | 1 | 213,500 TND | 213,500 × 10 / 100 = 21,350 TND |
| E-05 | 2026-03-12 | DAH | OTA (18 %) | 3 | 790,500 TND | 790,500 × 18 / 100 = 142,290 TND |
| E-09 | 2026-03-30 | DSB | DIR (0 %) | 3 | 685,500 TND | 685,500 × 0 / 100 = 0,000 TND |

`E-09` arrive le 30 mars et repart le 2 avril : ses **3 nuitées comptent toutes en mars** (mois d'arrivée, décision de la direction).

**Nuitées des séjours = 16** · **Montant des séjours = 3 831,000 TND** · **Commissions = 498,400 TND**.

## 3. Annulations (`operations.sqlite`, table `annulation`)

- `AN-0001` : séjour `E-05` (DAH, 3 nuitées), statut `CONFIRMEE`, annulé 4 jours avant l'arrivée → remboursement **395,250 TND** gardé ; ses 3 nuitées ne sont plus vendues.
- `AN-0002` : statut `RETIREE` (le client a finalement gardé son séjour) → ignorée (ce n'est pas un rejet).
- `AN-0003` : le séjour `E-99` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).

## 4. Les quatre indicateurs

- Nuitées vendues = 16 − 3 = **13**.
- Chambres disponibles = 64 chambres × 31 nuits de mars = **1984** (DAH 22, DSB 10, DTZ 14, DDJ 18).
- Taux d'occupation = 13 / 1984 = **0,655 %** (l'échantillon est petit : c'est normal).
- Revenu net d'annulations = 3 831,000 TND − 395,250 TND = **3 435,750 TND**.
- RevPAR = 3 435,750 TND / 1984 = **1,732 TND** par chambre disponible (arrondi au millime).

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_sejour` : 6 lignes · `fact_annulation` : 1 ligne · `dim_etablissement` : 4 · `dim_canal` : 4 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
