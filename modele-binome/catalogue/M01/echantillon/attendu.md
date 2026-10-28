# Échantillon Carthage Market — le calcul à la main

12 lignes de `ventes.csv`, le catalogue complet, 7 magasins, 3 retours dans `operations.sqlite`. Tout se calcule avec une calculatrice. Faites-le **avant** de demander quoi que ce soit à Codex : ces nombres servent ensuite à vérifier son code.

## 1. Décision ligne par ligne (`ventes.csv`)

La ligne 1 du fichier est l'en-tête.

| Ligne du fichier | ligne_id | Lu dans le fichier | Décision |
|---|---|---|---|
| 2 | E-01-1 | 2026-03-02 · 'LAC' · C101 · qté 4 · prix 1.350 · remise 0 | gardée |
| 3 | E-01-2 | 02/03/2026 · 'LAC' · C111 · qté 1 · prix 21,500 · remise 2,150 | gardée |
| 4 | E-02-1 | 3 mars 2026 · ' ari ' · C105 · qté 2 · prix 4.2 · remise 0 | gardée |
| 5 | E-03-1 | 2026-03-04 · 'HAM' · C107 · qté 6 · prix 1,490 · remise 0 | gardée |
| 6 | E-03-1 | 2026-03-04 · 'HAM' · C107 · qté 6 · prix 1,490 · remise 0 | ignorée : doublon exact de la ligne 5 |
| 7 | E-04-1 | 2026-03-05 · 'Sou' · C110 · qté 2 · prix 9.800 · remise 1.960 | gardée |
| 8 | E-05-1 | 2026-03-06 · 'GAB' · C104 · qté 1 · prix 7,8 · remise 0 | gardée |
| 9 | E-06-1 | 2026-03-07 · 'SFX' · C108 · qté 2 · prix 2.400 · remise 0 | rejet `id_conflit` |
| 10 | E-06-1 | 2026-03-07 · 'SFX' · C108 · qté 3 · prix 2.400 · remise 0 | rejet `id_conflit` |
| 11 | (vide) | 2026-03-08 · 'BIZ' · C102 · qté 2 · prix 1.150 · remise 0 | rejet `id_manquant` |
| 12 | E-08-1 | 2026-03-09 · 'TOZ' · C106 · qté 1 · prix 3.600 · remise 0 | rejet `cle_inconnue` |
| 13 | E-09-1 | 2026-03-09 · 'LAC' · C112 · qté 1,5 · prix 3.800 · remise 0 | rejet `quantite_invalide` |

Bilan : 12 lignes lues → 1 doublon exact ignoré, 5 lignes rejetées (2 `id_conflit`, 1 `id_manquant`, 1 `cle_inconnue`, 1 `quantite_invalide`) → **6 lignes gardées**.

## 2. Ventes brutes (remise déduite)

Une virgule ou un point sépare les décimales : `21,5` = `21.500` = 21 500 millimes. La remise vaut pour toute la ligne. Décision de la direction (règle à clarifier) : **la remise est déduite avant la marge**, donc montant brut = quantité × prix − remise.

| ligne_id | Date ISO | Magasin | Type | Produit | Calcul | Montant brut |
|---|---|---|---|---|---|---|
| E-01-1 | 2026-03-02 | LAC | propre | C101 | 4 × 1,350 − 0,000 | 5,400 TND |
| E-01-2 | 2026-03-02 | LAC | propre | C111 | 1 × 21,500 − 2,150 | 19,350 TND |
| E-02-1 | 2026-03-03 | ARI | franchisé | C105 | 2 × 4,200 − 0,000 | 8,400 TND |
| E-03-1 | 2026-03-04 | HAM | franchisé | C107 | 6 × 1,490 − 0,000 | 8,940 TND |
| E-04-1 | 2026-03-05 | SOU | propre | C110 | 2 × 9,800 − 1,960 | 17,640 TND |
| E-05-1 | 2026-03-06 | GAB | franchisé | C104 | 1 × 7,800 − 0,000 | 7,800 TND |

**Ventes brutes = 67,530 TND** (67530 millimes). Remises déjà déduites : 4,110 TND.

## 3. Retours (`operations.sqlite`, table `retour`)

- `R-0001` : 1 shampoing de la ligne `E-04-1` (SOU). Le client avait payé 2 × 9,800 − 1,960 = 17,640 TND pour 2 unités → remboursé **8,820 TND** (le prix payé, remise comprise). Statut `VALIDE` : gardé.
- `R-0002` : statut `ANNULE` → ignoré (ce n'est pas un rejet).
- `R-0003` : la ligne `E-99-9` n'existe pas → rejet `cle_inconnue` (source `operations.sqlite`).

**Retours = 8,820 TND.**

## 4. Les quatre indicateurs

- **Ventes nettes** = brutes − retours = 67,530 TND − 8,820 TND = **58,710 TND**.
- Coût d'achat des unités vendues = 4 × 0,980 + 1 × 14,800 + 2 × 2,900 + 6 × 1,160 + 2 × 5,600 + 1 × 5,300 = 47,980 TND. Unité retournée : 1 × 5,600 (coût du shampoing). Coût d'achat des unités nettes = 47,980 TND − 5,600 TND = **42,380 TND**.
- **Marge sur coût d'achat** = ventes nettes − coût d'achat des unités nettes = **16,330 TND**.
- **Part des franchisés** : magasins franchisés de l'échantillon = ARI, GAB, HAM ; leurs ventes nettes = 8,400 + 8,940 + 7,800 = 25,140 TND (aucun retour chez eux) ; part = 25140 / 58710 = **42,82 %**.
- **Taux de retour** = retours / brutes = 8820 / 67530 = **13,06 %**.

## 5. Ce que doit contenir l'entrepôt de l'échantillon

`fact_vente` : 6 lignes · `fact_retour` : 1 ligne · `dim_produit` : 12 · `dim_magasin` : 7 · `dim_date` : 31 jours (mars 2026). Rejets : 6 lignes. Les mêmes nombres sont dans `attendu.json`.
