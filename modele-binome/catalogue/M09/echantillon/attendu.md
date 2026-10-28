# Échantillon Scène Libre — le calcul à la main

12 lignes de `billets.csv`, un programme de 2 événements (capacités 10 et 8 places), les 4 canaux, 4 demandes dans `remboursements.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`billets.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | billet_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | S-001 | E01 · canal 'WEB' · 2026-03-02 · CAT1 · places 1 · prix 40.000 | gardée |
| 3 | S-002 | E01 · canal ' web ' · 02/03/2026 · CAT2 · places 1 · prix 25,000 | gardée |
| 4 | S-003 | E01 · canal 'GUI' · 3 mars 2026 · cat2 · places 1 · prix 20 | gardée |
| 5 | S-004 | E02 · canal 'REV' · 2026-03-05 · VIP · places 1 · prix 80,000 | gardée |
| 6 | S-004 | E02 · canal 'REV' · 2026-03-05 · VIP · places 1 · prix 80,000 | ignorée : doublon exact de la ligne 5 |
| 7 | S-005 | E02 · canal 'PAR' · 2026-03-06 · CAT1 · places 1 · prix 50,0 | gardée |
| 8 | S-006 | E02 · canal 'WEB' · 2026-03-06 · CAT1 · places 1 · prix 50.000 | rejet `id_conflit` |
| 9 | S-006 | E02 · canal 'WEB' · 2026-03-06 · CAT1 · places 2 · prix 50.000 | rejet `id_conflit` |
| 10 | (vide) | E01 · canal 'WEB' · 2026-03-07 · CAT1 · places 1 · prix 40.000 | rejet `id_manquant` |
| 11 | S-007 | E09 · canal 'WEB' · 2026-03-07 · CAT1 · places 1 · prix 40.000 | rejet `cle_inconnue` |
| 12 | S-008 | E01 · canal 'GUI' · 2026-03-08 · CAT2 · places 0 · prix 25.000 | rejet `quantite_invalide` |
| 13 | S-009 | E02 · canal 'Rev' · 2026-03-09 · CAT2 · places 1 · prix 35 | gardée |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 billets gardés**.

## 2. Recettes des billets et frais de distribution

Une virgule ou un point sépare les décimales : `50,0` = `50.000` = 50 000 millimes. `20` est un tarif réduit (CAT2 à 25 TND − 20 %) : on garde le prix payé. Frais = prix (TND) × frais du canal (pour mille), en millimes : WEB 45 ‰, GUI 0 ‰, REV 90 ‰, PAR 60 ‰ (`canaux.json`, mars 2026).

| billet_id | Date ISO | Événement | Canal | Prix | Frais (‰) | Calcul des frais | Frais |
|---|---|---|---|---|---|---|---|
| S-001 | 2026-03-02 | E01 | WEB | 40,000 TND | 45 | 40 × 45 | 1,800 TND |
| S-002 | 2026-03-02 | E01 | WEB | 25,000 TND | 45 | 25 × 45 | 1,125 TND |
| S-003 | 2026-03-03 | E01 | GUI | 20,000 TND | 0 | 20 × 0 | 0,000 TND |
| S-004 | 2026-03-05 | E02 | REV | 80,000 TND | 90 | 80 × 90 | 7,200 TND |
| S-005 | 2026-03-06 | E02 | PAR | 50,000 TND | 60 | 50 × 60 | 3,000 TND |
| S-009 | 2026-03-09 | E02 | REV | 35,000 TND | 90 | 35 × 90 | 3,150 TND |

**Recettes des billets = 250,000 TND** · **frais de distribution = 16,275 TND**.

## 3. Remboursements (`remboursements.sqlite`, table `remboursement`)

- `RB-0001` : billet `S-005` (E02 reporté), statut `REMBOURSE` → **50,000 TND remboursés, 1 billet remboursé**.
- `RB-0002` : statut `CONSERVE` (le client garde son billet pour la nouvelle date) → ignoré : un report n'est pas un remboursement.
- `RB-0003` : le billet `S-099` n'existe pas → rejet `cle_inconnue` (source `remboursements.sqlite`).
- `RB-0004` : statut `REFUSE` → ignoré (ce n'est pas un rejet).

Les frais du billet `S-005` restent dus au canal PAR : ils ne sont pas remboursés.

## 4. Billets nets, taux de remplissage, recettes nettes

- Billets nets = vendus − remboursés = 6 − 1 = **5**.
- Taux de remplissage = billets nets / capacité = 5 / 18 = **27,78 %** ; par événement : E01 = 3 / 10 = **30,00 %**, E02 = 2 / 8 = **25,00 %**.
- Recettes nettes = recettes − remboursements − frais = 250,000 TND − 50,000 TND − 16,275 TND = **183,725 TND**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_billet` : 6 lignes · `fact_remboursement` : 1 ligne · `dim_evenement` : 2 · `dim_canal` : 4 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
