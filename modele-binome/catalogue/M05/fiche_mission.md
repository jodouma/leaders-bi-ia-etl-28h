# Mission 05 — Centre de formation

**Client fictif :** Académie Nour (centre de formations professionnelles courtes (bureautique, données, gestion, langues) à Tunis, Sousse et Sfax). **Grain du fait :** une présence : un participant inscrit × une séance d'une session (présent 0 ou 1).
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

L'Académie Nour propose des formations courtes pour les salariés et les jeunes diplômés : Excel, Power BI, comptabilité, anglais professionnel, gestion de projet, marketing digital, Python. Chaque formation est donnée en **sessions** (un groupe, un formateur, un centre, un nombre fixe de séances). Les formateurs remplissent une feuille d'émargement (CSV), le catalogue vit dans un classeur Excel, le planning des sessions dans un fichier JSON, et les inscriptions, paiements et remboursements dans une petite base SQLite. La direction ne sait pas quelles sessions remplissent leurs objectifs.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Nous ouvrons beaucoup de sessions, mais je ne sais pas lesquelles marchent. Je veux, par session, par centre, par formation et par mois : le nombre d'inscrits, le taux d'assiduité, le taux de remplissage et les encaissements nets (paiements moins remboursements). Nos objectifs : remplissage d'au moins 70 %, assiduité d'au moins 80 %, et au moins 95 % de l'encaissement attendu (inscrits × prix). Dites-moi aussi quelles lignes vous avez écartées, et pourquoi.
> 
> Pour information : à partir du 15 juillet, la session d'anglais SES-2619 (classe du mardi soir, à distance) est rattachée au centre de Sfax au lieu de Sousse. Ce qui s'est passé avant reste à Sousse.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de l'Académie Nour)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_formation, dim_session, fact_presence, fact_paiement).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. La session SES-2619 (anglais professionnel, mardi soir, à distance) passe du centre « Sousse » au centre « Sfax » le 2026-07-15 (inclus). Cette information arrive avec `lot2/sessions.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Inscrits** (nombre) : nombre d'inscriptions distinctes de la session (participants de la feuille d'émargement), compté une fois par session, à la date de début de la session
- **Taux d'assiduité** (ratio) : présences / (inscrits × séances), soit la somme de `present` divisée par le nombre de lignes de présence (chaque inscrit figure à chaque séance tenue)
- **Taux de remplissage** (ratio) : inscrits / capacité (capacité du catalogue, une fois par session)
- **Encaissements nets** (TND) : paiements − remboursements

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, janvier → juin 2026 (20 sessions)
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 (5 nouvelles sessions + la fin de SES-2619) ; recopie la séance du 30 juin et les mouvements depuis le 1er juin ; SES-2619 passe à Sfax le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** (1) Un participant a payé mais n'est jamais venu (présent = 0 à toutes les séances) : compte-t-il dans les inscrits ? (2) Un participant de SES-2619 est remboursé le 20 juillet, après le changement de centre : le remboursement compte-t-il à Sousse (centre de son inscription) ou à Sfax (centre le jour du remboursement) ?

- (1) A : oui, il occupe une place et il a payé ; ses absences font baisser l'assiduité.
- (1) B : non, on ne compte que les participants venus au moins une fois (le remplissage baisse, l'assiduité monte).
- (2) A : version de la session à la date de l'inscription (Sousse).
- (2) B : version valable à la date du remboursement (Sfax), comme chaque mouvement.

**Décision de la direction pour cette mission :** (1) A : il compte dans les inscrits et dans le dénominateur de l'assiduité ; son paiement compte dans les encaissements. (2) B : chaque présence, paiement ou remboursement est rattaché à la version de la session valable à SA date et compté dans SON mois ; le remboursement du 20 juillet compte donc à Sfax.

## Les trois écrans de l'application

1. **Vue direction** — inscrits, assiduité, remplissage, encaissements nets et taux d'encaissement, puis les encaissements nets par mois et par centre (barres empilées).
2. **Détail par session** — chaque session avec ses versions : SES-2619 à Sousse jusqu'au 2026-07-14, puis à Sfax.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : taux d'abandon = inscrits absents aux deux dernières séances de leur session / inscrits.
2. Nouvelle règle : une présence datée d'un jour qui n'est pas une séance de la session (hors rythme du planning) est rejetée avec un nouveau motif `seance_inconnue`.
3. Changement historique : la session SES-2622 est rattachée à Tunis à partir du 2026-07-20 (deuxième session historisée dans `dim_session`).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M05 --etape tout
pytest controles
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
