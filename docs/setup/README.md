# Préparer l’atelier Atlas

[Retour au parcours du cours](../../README.md)

Le parcours complet, avec les commandes à copier et les fenêtres à ouvrir, est dans [01_demarrer_windows_ubuntu.pdf](../../pdf/01_demarrer_windows_ubuntu.pdf).

- Windows : Windows 11 encore maintenu, WSL 2 pour Docker et Docker Desktop ouvert. Saisir les commandes du cours dans **PowerShell Windows normal**, après les réglages du guide ; WSL n’est pas le terminal de travail de cette route.
- Ubuntu : Ubuntu 24.04 LTS → dépôt APT officiel Docker → Engine et plugin Compose → Terminal avec `sudo docker …`.
- Sans virtualisation : Thonny/Python natifs, mêmes fichiers `projet/`, aucun paquet pip.
- IA : navigateur et aides locales pour le socle ; Codex CLI et Claude Code restent facultatifs, sur le PC hôte et seulement avec un accès éligible.

À la racine extraite du cours, `compose.yaml` et `projet/` doivent être visibles ensemble. Les commandes ci-dessous concernent **Windows / PowerShell**, après installation. Pour Ubuntu, suivre d’abord la section Ubuntu plus bas :

```powershell
docker compose build
docker compose run --rm atelier python --version
docker compose run --rm atelier python calcul.py
docker compose run --rm atelier python verifier.py 01
```

Le build et la vérification de version doivent réussir. Le fichier de départ reste à compléter pendant les missions : `calcul.py` et son contrôle demandent ensuite de construire la fonction. Ce message attendu ne signifie pas que l’installation a échoué. Après les missions, **toujours sous Windows / PowerShell** :

```powershell
docker compose run --rm atelier python executer.py
docker compose up -d
```

Ouvrez `http://localhost:8000/rapport_atlas.html` dans le navigateur. Le serveur peut démarrer avant la création du rapport : ce fichier renvoie alors 404. Pour arrêter : `docker compose down`. Vos fichiers restent dans `projet/`.

## Ubuntu — avant les commandes Docker

Suivre l’installation du guide 01, puis créer une fois `.env` à la racine, sans écraser un fichier existant :

```bash
test -e .env || printf 'LOCAL_UID=%s\nLOCAL_GID=%s\n' \
  "$(id -u)" "$(id -g)" > .env
```

Après ce réglage, utiliser les mêmes commandes Docker avec **`sudo docker compose`**, y compris pour `build`, `run`, `up -d` et `down`. Les saisir depuis la racine du cours.

Ce fichier ne doit contenir que les identifiants numériques du compte pour la propriété des fichiers. Aucun secret ni clé IA. Si `.env` existe déjà, vérifiez ses valeurs avec le professeur.

Le premier build télécharge l’image Python officielle : il demande Internet. Après construction, conservez cette image pour les exercices hors ligne. Le conteneur emploie Python 3.13 et sa bibliothèque standard ; il ne contient aucun agent IA, aucune authentification et aucun installateur de projet téléchargé automatiquement. Le dossier du cours est monté sous `/workspace`, avec `/workspace/projet` comme dossier de travail. Le serveur publie uniquement `127.0.0.1:8000` sur votre poste.

Docker Desktop est propriétaire, avec un usage éducatif gratuit sous ses [conditions](https://docs.docker.com/subscription-billing/desktop-license/). [Docker Engine](https://docs.docker.com/engine/) offre la route libre sur Ubuntu. L’accès à un chat gratuit ne prouve pas l’accès à son agent CLI : Claude Free n’inclut pas Claude Code ; l’accès universel Free à Codex CLI n’est pas établi par les sources consultées.

Les [sources officielles et leur correspondance avec les pages du guide](sources.json) ont été vérifiées le 27 octobre 2026. Les recherches documentaires et contrôles de syntaxe ne constituent pas une installation réalisée sur un PC Windows ou Ubuntu. Aucun compte gratuit ni quota n’est présenté comme testé.
