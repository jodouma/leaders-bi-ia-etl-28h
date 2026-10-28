# Mission 07 — Abonnements FibreNet

**Client fictif :** FibreNet (fournisseur d'accès internet par fibre, clients particuliers et entreprises). **Grain du fait :** une facture mensuelle d'abonnement (un abonnement × un mois facturé).
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

FibreNet vend des abonnements internet par fibre à des particuliers et à des entreprises dans plusieurs villes. Chaque mois, chaque abonnement reçoit une facture. La facturation exporte les factures dans un CSV, les comptes clients vivent dans un classeur Excel, les offres et leurs prix dans un fichier JSON, et les dates de début et de fin des abonnements dans la base SQLite de l'outil opérationnel. La direction ne sait pas dire combien d'abonnés restent, combien partent, ni combien rapporte chaque mois le parc d'abonnés. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Nous gagnons des clients, mais nous en perdons aussi. Je veux voir, mois par mois, par gamme d'offre et par type de compte : le nombre d'abonnés actifs en fin de mois, le revenu mensuel récurrent (MRR), les départs du mois et le taux de départ. Et je veux savoir ce que vous avez dû écarter dans les fichiers, et pourquoi.
> 
> Pour information : le 15 juillet, l'offre Fibre 300 passe de la gamme confort à la gamme pro, et son prix passe de 89,900 à 99,900 TND par mois. Les chiffres du premier semestre doivent rester en confort, à l'ancien prix.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de FibreNet)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_compte, dim_offre, fact_facture, fact_abonnement_mois).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. L'offre FN-F300 (Fibre 300) passe de la gamme « confort » à 89,900 TND à la gamme « pro » à 99,900 TND le 2026-07-15 (inclus). Cette information arrive avec `lot2/offres.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Abonnés actifs fin de mois** (nombre) : nombre d'abonnements actifs le dernier jour du mois (`actif_fin` = 1) — valeur d'**un** mois : lisez l'agrégat `par_mois` ; sur plusieurs mois, le total de la référence additionne les fins de mois (abonnés-mois)
- **MRR (revenu mensuel récurrent)** (TND) : somme des mensualités des abonnements actifs en fin de mois, au prix de la version de l'offre valable le dernier jour du mois
- **Départs du mois** (nombre) : nombre d'abonnements dont la `date_fin` tombe dans le mois
- **Taux de départ** (ratio) : départs du mois / abonnés actifs en début de mois (sur plusieurs mois : somme des départs / somme des actifs de début de mois)

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, janvier → juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 ; recopie les factures émises depuis le 10 juin ; base des abonnements complète (résiliations de l'été) ; FN-F300 change de gamme et de prix le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** Un abonnement résilié le 31 mars (dernier jour du mois) est-il encore actif « fin mars » ? Et le MRR de juillet d'un abonné Fibre 300 se calcule-t-il à 89,900 TND (prix à la souscription ou à la facture du 1er juillet) ou à 99,900 TND (prix valable le 31 juillet) ?

- A : actif fin mars (il est servi le 31) ; MRR au prix de la souscription.
- B : départ de mars, plus actif fin mars ; MRR au prix de la version valable le dernier jour du mois.
- C : actif fin mars, départ compté en avril ; MRR au prix de la dernière facture.

**Décision de la direction pour cette mission :** B. `date_fin` = dernier jour de service ; actif fin de mois ⇔ `date_fin` vide ou **après** le dernier jour du mois. Le MRR d'un mois utilise la version de l'offre valable le dernier jour de ce mois : Fibre 300 compte 99,900 TND dans le MRR de juillet alors que sa facture de juillet (émise le 1er) vaut 89,900 TND.

## Les trois écrans de l'application

1. **Vue direction** — abonnés actifs et MRR à la fin de la période choisie, départs et taux de départ, MRR par mois et par gamme (barres empilées) et le tableau mois par mois actifs début + nouveaux − départs = actifs fin.
2. **Détail par offre** — chaque offre avec ses versions : FN-F300 en confort à 89,900 TND jusqu'au 2026-07-14, puis pro à 99,900 TND ; actifs, départs et MRR mois par mois.
3. **Qualité des données** — factures lues, gardées, déjà chargées, rejetées par motif ; abonnements annulés et rejetés, par lot.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : revenu moyen par abonné (ARPU) = MRR / abonnés actifs fin de mois, par gamme.
2. Nouvelle règle : un abonnement résilié moins de 60 jours après son début est un « départ précoce » → colonne `depart_precoce` dans `fact_abonnement_mois` et indicateur dédié.
3. Changement historique : l'offre FN-F20 baisse à 34,900 TND le 2026-08-01 (deuxième version dans `dim_offre`, MRR d'août recalculé, factures de juillet inchangées).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M07 --etape tout
python -m pytest
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
