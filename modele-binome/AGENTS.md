# Dépôt binôme — mission Solen Digital

Tu aides deux grands débutants en BI. Ils ne saisissent jamais de code : tu écris
Python, SQL, DAX, tests et YAML ; eux rédigent les demandes, lisent le diff,
lancent les contrôles, expliquent et décident. Réponds en français simple et court.

## Avant d'agir

- Lis `mission.txt` : `tronc-commun` → données dans `tronc-commun/` ;
  `Mxx` (ex. `M03`) → données dans `catalogue/Mxx/`. Lis le cahier des charges
  et le dictionnaire de la mission avant de proposer du code.
- Une demande = une petite étape avec un résultat observable (un fichier, un
  compte, un total). Avant un changement de plus d'un fichier ou de plus de
  ~50 lignes, propose d'abord un plan court (3 à 5 étapes, une preuve par étape)
  et attends l'accord.

## Ce que tu peux modifier

- Le code va **uniquement** dans `solen/` (paquet Python à la racine, lancé avec
  `python -m solen`) et, si on te le demande, dans `tests/`,
  `.github/workflows/controles.yml` et `powerbi/mesures.dax`. Pas de `pyproject.toml`
  ni d'installation du paquet : la racine du dépôt suffit.
- Ne modifie **jamais** : les sources (`tronc-commun/`, `catalogue/`), les valeurs
  de référence (`reference/`, `attendu*`), le dossier `controles/`. Si un contrôle
  échoue, corrige le code ; ne change pas le contrôle pour le faire passer.
- Demande avant de supprimer ou de remplacer un fichier existant.
- Ne fais ni `git commit`, ni `git push`, ni pull request, ni publication, ni envoi :
  les étudiants pratiquent Git et GitHub eux-mêmes. Tu peux expliquer une commande.

## Règles de données

- Point d'entrée : `python -m solen initial|increment|export|app`, qui lit
  `mission.txt`. Une commande de lecture `python -m solen sources` (nom, nombre
  de lignes, colonnes et 3 premières lignes de chaque source) est demandée en
  séance 2 et peut rester. `initial` recrée l'entrepôt depuis zéro avec `lot1` ; `increment`
  ajoute `lot2` ; relancer `increment` n'ajoute aucune ligne (rejeu) ; `export`
  écrit `outputs/export/<table>.csv` et `outputs/export/manifest.json` (comptes,
  sommes) ; `app` écrit `outputs/app/index.html` autonome, sans serveur.
- Entrepôt SQLite : `outputs/entrepot.sqlite`. Rejets : `outputs/rejets.csv` avec
  une colonne `motif` (`id_conflit`, `id_manquant`, `cle_inconnue`,
  `quantite_invalide`…). Les sources restent intactes.
- Argent en **millimes entiers** (1 TND = 1 000 millimes), jamais de float stocké ;
  affichage en TND à 3 décimales. Dates en ISO `YYYY-MM-DD`.
- Dimensions chargées avant les faits ; clés techniques `*_key` entières, clés
  métier `*_id` texte. SQL toujours paramétré (`?`), jamais de chaîne concaténée.
- SCD2 sur une seule dimension : `valid_from` inclus, `valid_to` exclu, `NULL` =
  version courante. Un fait ancien garde la version valable à sa date ; on ne
  réécrit jamais le passé.
- Les indicateurs suivent exactement le cahier des charges (« marge » = marge
  partielle nommée, jamais « bénéfice »).

## Contrôler et rendre compte

- Préfère les contrôles déterministes : `python -m controles.verifier --mission
  $(cat mission.txt) --etape rejets|initial|increment|rejeu|export|app|tout`, puis `pytest controles`.
- Lance le contrôle utile après chaque modification et rapporte le résultat réel.
  Sépare « exécuté et réussi », « exécuté et échoué » et « non exécuté ».
- Explique en 3 à 6 lignes ce que fait le changement et quel fichier lire dans le
  diff. Demande à l'étudiant de prévoir une valeur avant de la montrer.
- Une revue est en lecture seule. Si des sous-agents sont disponibles et demandés,
  fais deux lectures indépendantes ; un seul auteur corrige ensuite.
- Aucun secret, jeton ou identifiant de compte dans le dépôt ou dans tes réponses.
