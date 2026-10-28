# Mission 10 — Agence numérique

**Client fictif :** Pixel Studio (agence numérique de 15 personnes : sites web, applications, campagnes). **Grain du fait :** une ligne de temps (un collaborateur, un projet, un jour, une tâche, des heures).
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

Pixel Studio réalise des sites web, des applications et des campagnes pour une vingtaine de clients. Chaque collaborateur saisit ses heures dans une feuille de temps (CSV). Le coût d'une heure dépend du profil (développeur, designer, chef de projet, consultant) : il est dans un classeur Excel. La liste des projets (client, type forfait ou régie, chef de projet) est dans un fichier JSON. Les factures et les avoirs sortent du logiciel de facturation, une petite base SQLite. Personne ne sait dire quels projets consomment du temps sans rapporter assez. Solen Digital vous confie la mission. Les heures sont stockées en **centièmes d'heure entiers** (7,5 h = 750) et les montants en millimes entiers.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Nous travaillons beaucoup, mais je ne sais pas quels projets nous rapportent vraiment. Je veux, par projet, par client, par chef de projet et par mois : les heures, le coût de charge (heures × taux horaire du profil), le facturé net (factures − avoirs) et la marge de contribution. Je sais que ce n'est pas notre bénéfice : les loyers et les frais généraux ne sont pas dedans. Dites-moi aussi quelles lignes vous avez écartées, et pourquoi.
> 
> Pour information : à partir du 15 juillet, le projet « Portail patients » (PX07) passe de Hela Mansour à Nour Jebali. Les heures du premier semestre restent à Hela.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de Pixel Studio)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_collaborateur, dim_projet, fact_temps, fact_facture).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. Le projet PX07 (Portail patients) passe de la cheffe de projet « Hela Mansour » à « Nour Jebali » le 2026-07-15 (inclus). Cette information arrive avec `lot2/projets.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Heures** (centièmes d'heure, 750 = 7,5 h) : somme des heures des lignes de temps acceptées, en centièmes d'heure (750 = 7,5 h)
- **Coût de charge** (TND) : somme de heures × taux horaire coût du profil du collaborateur
- **Facturé net** (TND) : factures − avoirs (montants HT)
- **Marge de contribution** (TND) : facturé net − coût de charge (ce n'est PAS un bénéfice : aucun frais général)

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, janvier → juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 ; recopie des heures du 30 juin et des documents depuis le 15 juin ; PX07 change de chef de projet le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** (1) Les heures saisies sur PX07 avant le 15 juillet, et la facture de régie de juillet datée du 31 juillet : quel chef de projet ? (2) Les heures passées sur le projet interne INT01 (non facturable) comptent-elles dans le coût de charge ?

- (1) A : le chef courant pour tout le projet (on réécrit l'historique).
- (1) B : le chef valable le jour de la ligne de temps (ou de la facture).
- (2) A : oui, toute heure saisie coûte, facturable ou non.
- (2) B : non, on n'analyse que les projets clients.

**Décision de la direction pour cette mission :** (1) B : chaque heure, facture ou avoir prend la version de PX07 valable à SA date : les heures jusqu'au 14 juillet restent à Hela Mansour, la facture du 31 juillet (qui couvre tout juillet) va à Nour Jebali. (2) A : les heures de INT01 comptent dans le coût de charge global ; INT01 apparaît comme un projet de type `interne` avec un facturé net nul.

## Les trois écrans de l'application

1. **Vue direction** — factures, avoirs, facturé net, coût de charge et marge de contribution ; coût de charge par mois et par type de projet (barres empilées).
2. **Détail par projet** — chaque projet avec ses versions : PX07 chez Hela Mansour jusqu'au 2026-07-14, puis Nour Jebali ; les projets à marge négative se repèrent ici.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : taux de facturabilité = heures des projets forfait ou régie / heures totales.
2. Nouvelle règle : une ligne de plus de 12 heures est refusée → nouveau motif `heures_hors_bornes`.
3. Changement historique : le taux horaire coût des développeurs passe de 32,500 à 34,000 TND le 2026-08-01 (le coût d'une heure dépend de sa date : historiser les taux).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M10 --etape tout
python -m pytest
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
