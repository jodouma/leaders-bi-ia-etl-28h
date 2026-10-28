# Dépôt binôme — première mission chez Solen Digital

Ce dépôt est le vôtre, à deux. Vous y construisez, avec Codex, un petit
entrepôt de données puis un rapport : d'abord sur la mission d'entraînement
**Solen Commerce 360** (tronc commun, séances 1 à 4), ensuite sur la mission du
catalogue que vous aurez choisie.

Règle d'or : **vous n'écrivez jamais de code à la main**. Codex écrit Python,
SQL, DAX, tests et YAML. Vous rédigez les demandes, lisez le diff, lancez les
contrôles, expliquez, décidez — et vous faites Git et GitHub vous-mêmes.

Les explications détaillées sont dans les livrets du **dépôt du cours**
(dossier `pdf/`) :

| Livret | Quand le lire |
|---|---|
| `00_lire_moi.pdf` | avant la première séance |
| `01_demarrer.pdf` | installation : Windows + WSL2 Ubuntu, ou Ubuntu ; Codex ; Python |
| `02_tronc_commun.pdf` | séances 1 à 4, mission Solen Commerce 360 |
| `03_diriger_codex_et_git.pdf` | chaque fois que vous ouvrez une branche ou une PR |
| `04_catalogue_missions.pdf` | fin de séance 3 : choisir votre mission |
| `05_livrer_soutenir.pdf` | séance 5 et soutenance |
| `06_aide_memoire.pdf` | à garder ouvert |

## Qui est qui dans ce dépôt

| Chemin | Rôle | Qui modifie |
|---|---|---|
| `mission.txt` | la mission en cours : `tronc-commun`, puis `M01`…`M10` | vous |
| `tronc-commun/`, `catalogue/` | données sources et cahiers des charges | personne |
| `controles/` | vérificateur et tests fournis | personne |
| `solen/` | le pipeline Python | Codex, à votre demande |
| `outputs/` | entrepôt, rejets, exports, app (recréés, non versionnés) | le pipeline |
| `powerbi/` | guide Power BI et mesures DAX | vous (rapport), Codex (DAX) |
| `notes/JOURNAL.md` | une entrée par PR | vous |
| `AGENTS.md`, `.agents/skills/` | consignes et méthodes pour Codex | vous, avec soin |

## Parcours A → B → C

### A. Créer le dépôt et le cloner (séance 1, 30 min)

Une seule personne, **A**, crée le dépôt ; **B** le rejoint.

1. **A**, sur GitHub : **New repository**, nom `solen-<nomA>-<nomB>`, **Public**
   (données 100 % synthétiques), **sans** README ni .gitignore (ils sont fournis).
2. **A**, dans le terminal Ubuntu (ou Ubuntu/WSL2) :

   ```bash
   cd ~
   git clone https://github.com/<compteA>/solen-<nomA>-<nomB>.git solen-bi
   cd solen-bi
   cp -r ~/cours-bi/modele-binome/. .
   git add .
   git commit -m "Départ : modèle du dépôt binôme"
   git push -u origin main
   ```

   Adaptez `~/cours-bi` au dossier où vous avez cloné le cours.
3. **A**, sur GitHub : **Settings → Collaborators → Add people**, invite le compte de B.
   Puis protège `main` comme indiqué dans `03_diriger_codex_et_git.pdf` (une PR et une
   approbation avant fusion).
4. **B** accepte l'invitation (mail ou notification GitHub), puis clone le dépôt
   avec la même commande `git clone … solen-bi` : le dossier local s'appelle `~/solen-bi` chez les deux.
5. **Chacun** crée son environnement Python, dans le dossier du dépôt :

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   À chaque nouveau terminal : `source .venv/bin/activate` (le prompt affiche `(.venv)`).
6. **Chacun** ouvre l'application Codex, choisit ce dossier comme projet, modèle
   **GPT-6 Luna**, effort **High** pour commencer. Demandez :
   « Quelles instructions du projet as-tu lues ? Ne modifie rien. »
   Codex doit citer `AGENTS.md`.

### B. Lancer les contrôles une première fois (séance 1, 10 min)

```bash
python -m controles.verifier --mission $(cat mission.txt) --etape initial
pytest controles
```

**Prévoyez d'abord** : réussite ou échec ? Les deux commandes **échouent**, et
c'est normal : rien n'est encore construit, `solen/` est vide et
`outputs/entrepot.sqlite` n'existe pas. Lisez le message : il dit ce qui manque.
Ce premier échec est votre point de départ ; chaque PR doit en faire passer un
morceau au vert. Notez-le dans `notes/JOURNAL.md`.

Sur GitHub, l'onglet **Actions** exécute `.github/workflows/controles.yml` à chaque
PR. Au départ, il ne lance que l'installation (variable `ETAPE_CI: aucune`) ;
vous demanderez à Codex de l'avancer d'une étape quand le pipeline grandira.

### C. Le cycle, à chaque petite étape

Les rôles **alternent à chaque PR** : l'auteur d'aujourd'hui relit demain.

| # | Auteur | Relecteur |
|---|---|---|
| 1 | `git switch main` puis `git pull` | |
| 2 | `git switch -c <etape-courte>` (ex. `lecture-csv`) | |
| 3 | prévoit un résultat, puis demande à Codex (voir `prompts/` du cours) | |
| 4 | lance les contrôles ; lit le diff (`git diff`) ligne par ligne | |
| 5 | complète `notes/JOURNAL.md` | |
| 6 | `git add …` puis `git commit -m "…"` puis `git push -u origin <branche>` | |
| 7 | ouvre la PR (méthode `$preparer-pr`) et nomme le relecteur | |
| 8 | | `git fetch` puis `git switch <branche>` ; relance les contrôles |
| 9 | | revue Codex en lecture seule (`$revoir-bi`), puis sa propre lecture |
| 10 | | GitHub : **Files changed → Review changes → Approve** ou **Request changes** |
| 11 | corrige si demandé (même branche, nouveau commit, push) | relit la correction |
| 12 | | CI verte + approbation → **Merge pull request** |
| 13 | `git switch main` puis `git pull` | idem |

Un cycle réussi se voit : une PR fusionnée, une revue écrite, une CI verte, une
entrée de journal avec sa preuve.

## Ce qu'on ne fait pas

- modifier les sources, les références ou `controles/` pour « faire passer » ;
- fusionner sa propre PR ;
- mettre un mot de passe, un jeton ou une clé dans le dépôt ;
- présenter une commande proposée par Codex comme exécutée sans l'avoir lancée.
