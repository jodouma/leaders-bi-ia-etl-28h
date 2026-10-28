# Démarrer · Solen BI 22 h

[Retour au cours](../../README.md) · Livret complet : [`pdf/01_demarrer.pdf`](../../pdf/01_demarrer.pdf) · [Aide-mémoire Git · Codex · BI](../../aide-memoire/aide_memoire_git_codex_bi.md)

Ce dossier résume l’installation. Le livret 01 détaille chaque étape, les sorties attendues et les erreurs courantes. Comptez 60 à 120 min en début de séance 1 ; c’est une estimation.

## Ce que chacun prépare

- un compte **ChatGPT Free** (aucun paiement, aucune clé API) ;
- un compte **GitHub** personnel ;
- **Windows 10 (version 2004+) ou 11**, ou **Ubuntu 24.04 / 26.04 LTS** ;
- un accès **Windows** pour Power BI Desktop en séance 5.

Le binôme décide qui est **A** (crée le dépôt GitHub et invite B) et qui est **B**.

## Windows : Ubuntu dans WSL2

Dans **PowerShell (Windows)** ouvert en administrateur, puis redémarrer le PC :

```powershell
wsl --install
```

Ouvrir **Ubuntu** depuis le menu Démarrer, créer l’utilisateur Linux, puis dans le **Terminal Ubuntu** :

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git
```

Application ChatGPT pour Windows (Microsoft Store) : **Settings → Agent environment → Windows Subsystem for Linux (WSL)**, **Integrated terminal shell → WSL**, puis quitter et rouvrir l’application. Les projets s’ouvrent avec **Add new project** (Ctrl + O) en tapant `\\wsl$\` puis Ubuntu → home → votre utilisateur.

## Ubuntu natif

Mêmes commandes `apt` dans le Terminal. Application Linux (preview) : télécharger le `.deb` officiel, puis `sudo apt install ./chatgpt_amd64.deb` (ou `chatgpt_arm64.deb`) depuis le dossier de téléchargement, et lancer `chatgpt`.

## Les deux dossiers

| Dossier | Contenu | Créé par |
|---|---|---|
| `~/cours-bi` | ce dépôt de cours (lecture) | `git clone <adresse-du-cours> ~/cours-bi` |
| `~/solen-bi` | le dépôt GitHub du binôme | `git clone https://github.com/<compteA>/<depot>.git ~/solen-bi` |

Remplacez chaque `<mot>` entre chevrons, chevrons compris. Les deux dossiers vivent dans Linux, jamais sous `C:\`.

## Codex Free

Mode **Codex**, modèle **GPT-6 Luna**, effort **High** pour commencer (Ctrl + Maj + M). `/status` affiche le contexte et les limites d’usage. La page officielle des tarifs annonce pour Free « GPT-6 Luna at Standard speed in the desktop app, subject to rollout » : vérifiez ce que **votre** compte affiche. Aucun quota n’est garanti. Le **Codex CLI est facultatif** et non confirmé sur Free.

## GitHub

1. Chacun : compte GitHub, adresse noreply, `git config --global user.name` / `user.email`.
2. Chacun : GitHub CLI (dépôt apt officiel, voir livret), puis `gh auth login` (HTTPS, navigateur) et `gh auth setup-git`.
3. A : dépôt **public** `solen-<nomA>-<nomB>` sans README ; invite B (**Settings → Collaborators → Add people**).
4. A : clone, copie `~/cours-bi/modele-binome/.`, premier commit, `git push -u origin main`.
5. A : protège `main` (**Settings → Branches → Add classic branch protection rule** : PR requise, 1 approbation, pas de contournement).
6. Chacun : `python3 -m venv .venv`, `source .venv/bin/activate`, `python -m pip install -r requirements.txt`.
7. Le binôme : premier cycle branche → commit → push → PR → revue → merge → `git switch main && git pull`.

Jamais de `git push --force` ni de `git reset --hard` ; jamais de mot de passe ou de jeton dans le dépôt.

## Sources

Les [sources officielles](sources.json) (OpenAI, Microsoft, Ubuntu, Python, Git, GitHub) ont été lues le **28 octobre 2026**, avec les libellés et citations utilisés. Cette lecture n’est ni une installation réelle ni un test de compte Free.
