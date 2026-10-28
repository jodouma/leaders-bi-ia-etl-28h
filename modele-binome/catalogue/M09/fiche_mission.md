# Mission 09 — Événementiel — Scène Libre

**Client fictif :** Scène Libre (organisateur de spectacles : concerts, théâtre et festivals dans cinq salles). **Grain du fait :** un billet vendu.
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

Scène Libre organise des concerts, des pièces de théâtre et des festivals dans cinq salles (Tunis, Sousse, Sfax, Nabeul). Les billets sont vendus par quatre canaux : la billetterie en ligne, le guichet, des revendeurs et des partenaires. Chaque canal prend des frais de distribution. La billetterie exporte les billets dans un CSV, le programme et les tarifs vivent dans un classeur Excel, les canaux et leurs frais dans un fichier JSON, et les remboursements dans une petite base SQLite. Cette saison, un concert a été annulé, un autre reporté. La direction ne sait plus quels spectacles se vendent vraiment bien. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Nous vendons beaucoup de billets, mais après les annulations, les remboursements et les frais des canaux, que reste-t-il ? Je veux, par événement, par type de spectacle, par mois et par canal : les billets nets, le taux de remplissage et les recettes nettes. Dites-moi quels événements se vendent bien une fois les remboursements déduits, et ce que vous avez dû écarter dans les fichiers.
> 
> Pour information : à partir du 15 juillet, les revendeurs (canal REV) prennent 11 % au lieu de 9 %. Les billets vendus avant gardent l'ancien taux.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de Scène Libre)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_evenement, dim_canal, fact_billet, fact_remboursement).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. Le canal REV (revendeur) passe de 9 % (90 ‰) à 11 % (110 ‰) de frais de distribution le 2026-07-15 (inclus). Cette information arrive avec `lot2/canaux.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Billets nets** (nombre) : billets vendus − billets remboursés
- **Taux de remplissage** (ratio) : billets nets / capacité des événements (somme des capacités des événements concernés)
- **Recettes nettes** (TND) : recettes des billets − remboursements − frais de distribution

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial : billets vendus de janvier à juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 ; recopie les 16 derniers billets de juin ; 3 nouveaux événements ; REV passe à 11 % le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** 1) Un billet REV vendu le 10 juillet (frais 9 %) est remboursé le 20 juillet, après le passage à 11 %. Quels frais garde-t-on ? 2) Un spectacle reporté : une demande « report » compte-t-elle comme un remboursement ?

- 1A : frais de la version valable à la date de **vente** (9 %), jamais recalculés.
- 1B : frais recalculés à la date du remboursement (11 %).
- 1C : frais annulés quand le billet est remboursé.
- 2A : toute demande de motif `REPORT` est un remboursement.
- 2B : seul le statut `REMBOURSE` compte ; `CONSERVE` (billet gardé pour la nouvelle date) n'est pas un remboursement.

**Décision de la direction pour cette mission :** 1A et 2B. Les frais sont dus au canal le jour de la vente : ils restent au taux de la version valable à la date de vente et ne sont ni remboursés ni recalculés. Un report n'est pas un remboursement : seules les lignes `REMBOURSE` (argent rendu) réduisent les billets nets et les recettes, quel que soit le motif (`ANNULATION` ou `REPORT`).

## Les trois écrans de l'application

1. **Vue direction** — billets nets, taux de remplissage, recettes nettes ; recettes nettes par mois de l'événement et par type (barres empilées) ; filtre par événement et par type.
2. **Détail par canal** — chaque canal avec ses versions de frais : REV à 90 ‰ jusqu'au 2026-07-14, puis 110 ‰ ; recettes et frais par version.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; demandes non remboursées ignorées.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : recette nette moyenne par billet net = recettes nettes / billets nets, par événement.
2. Nouvelle règle : en cas d'annulation, le canal rend ses frais → frais nets = frais des billets non remboursés ; nouvelle colonne `frais_rendus_millimes` dans `fact_remboursement`.
3. Changement historique : le canal PAR (partenaire) passe de 6 % à 5 % le 2026-08-01 (deuxième version de PAR dans `dim_canal`).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M09 --etape tout
pytest controles
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
