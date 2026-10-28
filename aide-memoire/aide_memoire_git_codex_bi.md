# Aide-mémoire · Git, GitHub, Codex et BI

Solen BI 22 h · à garder ouvert pendant les séances. Les détails et les captures sont dans le livret `01_demarrer.pdf`.

Un mot entre `<chevrons>` est à remplacer en entier, chevrons compris. Toutes les commandes se tapent dans le **Terminal Ubuntu** (WSL ou natif), dans `~/solen-bi`, venv actif (`(.venv)` dans l’invite).

---

## 1. Le cycle Git, dans l’ordre

| # | Qui | Commande ou geste | Pourquoi |
|---|---|---|---|
| 1 | auteur | `cd ~/solen-bi` puis `source .venv/bin/activate` | bon dossier, bon Python |
| 2 | auteur | `git switch main` puis `git pull` | partir de la dernière version validée |
| 3 | auteur | `git switch -c <branche>` (ex. `lecture-csv`) | travailler à l’écart de `main` |
| 4 | auteur | demande à Codex (section 3) | un petit objectif à la fois |
| 5 | auteur | lancer les contrôles du dépôt | une preuve, pas une promesse |
| 6 | auteur | `git status` puis `git diff` | voir ce qui a changé, ligne par ligne |
| 7 | auteur | `git add <fichier>` puis `git commit -m "<message>"` | une photo nommée de l’état |
| 8 | auteur | `git push -u origin <branche>` (ensuite : `git push`) | envoyer la branche sur GitHub |
| 9 | auteur | GitHub : **Compare & pull request** → **Create pull request** | demander une revue |
| 10 | relecteur | `git fetch` puis `git switch <branche>` | récupérer la branche chez soi |
| 11 | relecteur | contrôles + revue Codex en lecture seule + sa lecture | vérifier sans modifier |
| 12 | relecteur | **Files changed → Review changes → Approve / Request changes → Submit review** | une revue écrite |
| 13 | auteur | corrections : même branche, `git commit`, `git push` | la PR se met à jour |
| 14 | relecteur | checks verts + approbation → **Merge pull request → Confirm merge** | entrer dans `main` |
| 15 | les deux | `git switch main && git pull` puis `git branch -d <branche>` | réaligner les deux copies |

Les rôles alternent à chaque PR. Chaque PR ajoute une entrée à `notes/JOURNAL.md` : état, décision, preuve, prochain objectif.

### Lire avant d’agir

| Commande | Ce qu’elle montre |
|---|---|
| `git status` | dossier, branche, fichiers modifiés ou nouveaux |
| `git diff` | lignes changées non encore ajoutées (`+` ajoutée, `-` retirée) |
| `git diff --staged` | ce qui partira au prochain commit |
| `git log --oneline -5` | les 5 derniers commits |
| `git branch` | branches locales ; `*` = branche courante |
| `gh auth status` | compte GitHub connecté |

### Réparer sans casser

**Interdits : `git push --force`, `git reset --hard`, supprimer `.git`.** Ils effacent du travail.

| Symptôme | Réparer |
|---|---|
| `fatal: not a git repository` | `cd ~/solen-bi` |
| commit fait sur `main` | `git switch -c <branche>`, push, PR ; après fusion, `git switch main && git pull` |
| `Your local changes ... would be overwritten` | commit sur la bonne branche, ou `git stash` → changer de branche → `git stash pop` |
| push refusé, `protected branch` | normal : branche + PR |
| push refusé, `fetch first` | `git pull` sur la branche, contrôles, `git push` |
| PR `out-of-date` | `git fetch`, puis sur la branche `git merge origin/main`, contrôles, push |
| `Not possible to fast-forward` | ne rien forcer ; montrer `git status` et `git log --oneline -5` |
| check rouge | **Details**, lire la fin, relancer la même commande chez soi, corriger le code (jamais les contrôles ni la référence) |
| `CONFLICT` | lire les deux versions, décider à deux, retirer `<<<<<<<` `=======` `>>>>>>>`, contrôles, `git add`, `git commit` ; annuler : `git merge --abort` |

---

## 2. Gestes GitHub

- **Créer le dépôt** (A) : **+ → New repository**, public, sans README.
- **Inviter** (A) : **Settings → Collaborators → Add people** ; B accepte l’invitation.
- **Protéger `main`** (A) : **Settings → Branches → Add classic branch protection rule** : `main`, PR requise, 1 approbation, **Do not allow bypassing the above settings**.
- **Ouvrir une PR** : titre court ; description **quoi / pourquoi / preuve / à relire** ; choisir le relecteur.
- **Relire** : citer un fichier et une ligne ; dire ce qui est vérifié et ce qui manque. « OK » seul n’est pas une revue.
- **Checks** : la CI rejoue les contrôles sur une machine Linux neuve. Vert avant de fusionner.
- **Fusionner** : jamais sa propre PR sans approbation. L’auteur ne peut pas approuver sa PR.
- **Secrets** : aucun mot de passe, jeton ou clé dans un fichier, un commit, une URL ou une demande à Codex.

---

## 3. Habitudes Codex

### Une bonne demande

1. **Un petit objectif** : un résultat observable (« compter les lignes du CSV de ventes du lot 1 »).
2. **Les fichiers** concernés, et ceux à ne pas toucher (sources, `controles/`, références).
3. **Le contrôle attendu** : la commande et ce qu’elle doit afficher.
4. **Plan d’abord** : « Propose ton plan en 3 étapes, attends mon accord » (ou `/plan`).

Puis : **lire le diff** (onglet de revue, Ctrl + Maj + G, ou `git diff`), **lancer soi-même** les contrôles, **écrire une note courte** dans le journal. Une commande annoncée par Codex n’est pas une preuve tant que vous ne l’avez pas lancée.

### Des contrôles déterministes

Un contrôle donne toujours le même résultat pour les mêmes fichiers : un nombre de lignes, une somme en millimes, un compte de rejets par motif. « Ça a l’air bon » n’en est pas un.

### Quatre mots à ne pas confondre

| Mot | Sens | Geste |
|---|---|---|
| **Token** | petit morceau de texte ; demandes, fichiers et réponses se comptent en tokens | demander peu de fichiers à la fois |
| **Contexte** | ce que Codex garde en tête dans ce chat | chat trop long : nouveau chat + résumé de 5 lignes |
| **Effort** | combien Codex réfléchit (Light, Medium, High, Extra High) | High pour commencer avec Luna ; Light pour une question simple |
| **Quota** | votre allocation d’usage sur une période ; elle varie | `/status` avant une grosse demande ; limite atteinte : commit, noter l’heure de reprise, continuer sans Codex |

### Revue : lecture seule → correction → nouveau contrôle

1. « Revue en lecture seule de `<branche>` par rapport à `main`. Au plus 3 remarques : fichier, ligne, risque. Ne modifie aucun fichier. »
2. Vous choisissez les remarques à traiter ; une demande de correction par remarque.
3. Vous relancez les mêmes contrôles et relisez le diff de la correction.

### Les fichiers qui guident Codex

- `AGENTS.md` : règles du dépôt, lues par Codex avant tout travail. Demandez « Quelles instructions as-tu lues ? » pour le vérifier.
- `.agents/skills/<nom>/SKILL.md` : une méthode réutilisable (`name` + `description`), par exemple `revoir-bi` ou `preparer-pr`. Nommez-la dans la demande pour l’utiliser.
- **Travailleurs parallèles** (sous-agents) : facultatifs, seulement si vous les demandez, et ils consomment plus de tokens. Une tâche à la fois suffit dans ce cours.

---

## 4. Vocabulaire BI · Solen Commerce 360 (Maison Zitouna)

Montants stockés en **millimes entiers** (1 TND = 1 000 millimes), affichés en TND à 3 décimales.

| Mot | Définition courte | Exemple Maison Zitouna |
|---|---|---|
| **ETL** | Extraire, Transformer, Charger | lire le CSV des ventes, nettoyer les formats, charger `entrepot.sqlite` |
| **Grain** | ce que représente une ligne de fait | une ligne de ticket : 2 savons P05 à 3,900 TND = 7 800 millimes |
| **Fait** | événement mesuré, avec des montants | `fact_vente` : quantité, montant brut, coût d’achat |
| **Dimension** | ce qui décrit le fait | `dim_boutique` (nom, zone commerciale), `dim_produit`, `dim_date` |
| **Clé métier** | identifiant du monde réel, en texte | `boutique_id = "SFX"` |
| **Clé technique** | entier créé par l’entrepôt | `boutique_key = 2` pour NBE avant le 2026-07-15, `boutique_key = 4` après : une nouvelle version, une nouvelle clé |
| **Schéma en étoile** | un fait au centre, relié à ses dimensions | `fact_vente` relié à date, produit, boutique |
| **Ventes nettes** | ventes brutes − retours | 120 000 − 6 000 = 114 000 millimes |
| **Marge sur coût d’achat** | ventes nettes − coût d’achat des unités nettes | 114 000 − 70 000 = 44 000 millimes (jamais « bénéfice ») |
| **Taux de retour** | retours / ventes brutes | 6 000 / 120 000 = 5 % |
| **Rejet** | ligne source écartée, avec un motif | même `vente_id` avec deux montants → `id_conflit` dans `outputs/rejets.csv` |
| **SCD2** | dimension qui garde son historique par versions datées | la boutique change de zone le 2026-07-15 : ancienne version `valid_to = 2026-07-15`, nouvelle `valid_from = 2026-07-15` |
| **Incrément** | charger seulement le nouveau lot | le lot 2 (juillet–août) s’ajoute au lot 1 sans le recharger |
| **Rejeu** | relancer le même lot sans créer de doublon | relancer le lot 2 : le nombre de lignes de `fact_vente` ne bouge pas |

Une vente de juin reste rattachée à l’ancienne zone de la boutique ; une vente d’août, à la nouvelle. C’est la question à poser à chaque graphique « par zone ».
