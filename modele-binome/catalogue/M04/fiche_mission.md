# Mission 04 — Livraison

**Client fictif :** Colis Rapide (transporteur de colis : 7 agences, 4 zones de livraison, 3 services (Standard, Express, Économique)). **Grain du fait :** un colis livré.
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

Colis Rapide livre des colis partout en Tunisie depuis sept agences. Chaque agence est rattachée à une zone (Grand Tunis, Nord, Centre-Sahel, Sud). Le suivi des colis sort dans un CSV, la grille des tarifs vit dans un classeur Excel, la liste des agences dans un fichier JSON et la facturation (factures et pénalités de retard) dans une base SQLite. Les clients se plaignent des retards, et personne ne sait dire où l'on perd de l'argent. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Nos clients disent que nous livrons en retard, et nos pénalités augmentent. Je veux savoir où se concentrent les retards et les coûts : par agence, par zone, par service, par tranche de poids et par mois. Donnez-moi la ponctualité, le retard moyen, le revenu facturé net des pénalités, le coût transporteur et la marge de livraison. Dites-moi aussi quels colis vous avez dû écarter, et pourquoi.
> 
> Pour information : à partir du 15 juillet, l'agence de Nabeul quitte la zone Nord et rejoint la zone Centre-Sahel. Les chiffres du premier semestre doivent rester dans la zone Nord.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de Colis Rapide)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_agence, dim_service, dim_tarif, fact_colis).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. L'agence NAB (Nabeul) passe de la zone « Nord » à la zone « Centre-Sahel » le 2026-07-15 (inclus). Cette information arrive avec `lot2/agences.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Colis livrés** (nombre) : nombre de colis acceptés dans `fact_colis`
- **Ponctualité** (ratio) : colis à l'heure / colis livrés
- **Retard moyen** (jours, nombre décimal) : somme des jours de retard / nombre de colis EN RETARD (les colis à l'heure ne comptent pas) ; jours de retard = date_livraison − date_promise, en jours calendaires
- **Revenu facturé net de pénalités** (TND) : montant facturé − pénalités de retard
- **Coût transporteur** (TND) : somme du coût transporteur de la grille (zone de destination × tranche de poids) des colis acceptés
- **Marge de livraison** (TND) : revenu facturé net de pénalités − coût transporteur (marge partielle : ni salaires, ni loyers, ni carburant des agences ; ce n'est pas un bénéfice)

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, colis livrés de janvier à juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 ; recopie des colis livrés fin juin ; NAB change de zone le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** Deux cas posent problème. (1) Un colis livré **le jour même** de la date promise est-il à l'heure ? (2) Un colis de l'agence de Nabeul expédié le 13 juillet (zone Nord) et livré le 16 juillet (zone Centre-Sahel) : dans quelle zone le compter ?

- (1) A : à l'heure (date_livraison ≤ date_promise). B : en retard (il fallait livrer avant).
- (2) A : version de l'agence valable à la date d'**expédition** (Nord). B : version valable à la date de **livraison** (Centre-Sahel).

**Décision de la direction pour cette mission :** deux décisions distinctes.

- Question (1) → **option A** : un colis livré le jour promis est **à l'heure** ; son retard vaut 0 jour.
- Question (2) → **option B** : le colis est rattaché à la version de l'agence valable à sa **date de livraison**, qui est la date du fait (dim_date) ; il compte donc dans Centre-Sahel et dans le mois de juillet.

## Les trois écrans de l'application

1. **Vue direction** — ponctualité, revenu facturé net, pénalités, coût transporteur et marge de livraison ; revenu net par mois et par zone d'agence (barres empilées) ; filtres période, agence, zone, service.
2. **Détail par agence** — chaque agence avec ses versions : NAB en zone Nord jusqu'au 2026-07-14, puis Centre-Sahel ; indicateurs par version et par mois.
3. **Qualité des données** — lignes rejetées par motif, par source et par lot.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : taux de pénalité = pénalités / montant facturé, par agence et par service.
2. Nouvelle règle : le retard se compte en jours ouvrés (samedi et dimanche exclus) ; recalculer `retard_jours`, `a_l_heure` et la ponctualité.
3. Changement historique : l'agence BIZ (Bizerte) rejoint la zone « Grand Tunis » le 2026-08-16 (deuxième version pour BIZ dans `dim_agence`).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M04 --etape tout
pytest controles
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
