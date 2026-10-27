# Construire une solution BI avec l’IA — Atlas Papeterie

**28 h · Licence BI · grands débutants · français · Windows d’abord, Ubuntu aussi.**

Vous pilotez le besoin, les règles et les contrôles. Un assistant IA peut aider à écrire une fonction ; vous l’enregistrez, l’exécutez et expliquez sa preuve. Le même projet grandit : fichiers de ventes → ETL → entrepôt SQLite en étoile → rapport local.

## Commencer

1. Recevoir le **ZIP de cette édition**, ou utiliser **Code → Download ZIP** si ce dépôt est publié. Dans l’Explorateur, **Extraire tout…** dans un nouveau dossier nommé `atlas-bi-ia-28h`. Aucun compte GitHub n’est requis pour un ZIP déjà fourni.
2. Ouvrir **[pdf/01_demarrer_windows_ubuntu.pdf](pdf/01_demarrer_windows_ubuntu.pdf)**. Suivre uniquement la route de son système : PowerShell sous Windows, terminal sous Ubuntu. Le guide fournit aussi un repli Python natif.
3. Ouvrir **[pdf/02_cours_atlas_ia.pdf](pdf/02_cours_atlas_ia.pdf)**. Votre travail se fait dans **`projet/`** ; conserver le dossier complet du cours autour de lui.
4. Commencer par la mission 01. Les fonctions sont volontairement incomplètes : un message « mission à construire » est attendu avant votre première construction.

**Ne pas lancer le corrigé comme point de départ.** Les indices et `solutions/atlas/` servent après un premier essai. Le vérificateur contrôle votre travail ; il ne lit jamais les solutions pour le terminer.

## Un environnement reproductible

Après installation et démarrage de Docker, depuis la racine du cours :

```text
docker compose build
docker compose run --rm atelier python calcul.py
docker compose run --rm atelier python verifier.py 01
```

Sous Ubuntu, suivre d’abord les réglages du guide ; ses commandes utilisent `sudo docker compose`. Les lignes ci-dessus échoueront avec une consigne tant que la fonction de la mission 01 n’est pas construite. C’est le comportement prévu.

Une fois les sept missions terminées :

```text
docker compose run --rm atelier python executer.py
docker compose run --rm atelier python verifier.py tout
docker compose up -d
```

Ouvrir **[le rapport local](http://localhost:8000/rapport_atlas.html)**. Le lien fonctionne après création du rapport et démarrage du serveur. Pour arrêter : `docker compose down` ; les fichiers du projet restent présents.

Docker n’est pas obligatoire pour terminer : le guide explique comment lancer les mêmes fichiers avec Python local, sans installation de paquet. Ne mélangez pas les commandes de Windows et celles d’Ubuntu.

## Les supports

| Support | Utilisation |
|---|---|
| [01_demarrer_windows_ubuntu.pdf](pdf/01_demarrer_windows_ubuntu.pdf) | Installation, Docker, repli natif, Codex/Claude CLI facultatifs |
| [02_cours_atlas_ia.pdf](pdf/02_cours_atlas_ia.pdf) | Le parcours guidé complet et ses preuves |
| [03_prompts_reperes_depannage.pdf](pdf/03_prompts_reperes_depannage.pdf) | Demandes IA courtes, notions et dépannage |
| [04_defi_campus_box.pdf](pdf/04_defi_campus_box.pdf) | Défi de transfert de 7 h, groupes de 3 maximum |
| [05_indices_et_corriges.pdf](pdf/05_indices_et_corriges.pdf) | Indices puis corrections expliquées, après un premier essai |
| [Atlas_BI_IA_28h.pptx](presentation/Atlas_BI_IA_28h.pptx) | Présentation modifiable, avec PDF voisin |
| [TESTER_LE_COURS.md](TESTER_LE_COURS.md) | Protocole pour essayer le parcours depuis un poste neuf |

## Sept missions, puis un défi

**21 h guidées** : calculer et contrôler → lire le CSV → nettoyer → modéliser → charger → ajouter et rejouer → expliquer le rapport.

**7 h de défi Campus Box** : nouvelle question, nouvelles données et nouveaux champs. L’IA reste autorisée ; chaque membre doit expliquer une contribution et un contrôle. Répartition prévue : **8 h 24 théorie / 19 h 36 pratique**. Les durées sont estimées, installation et dépannage compris ; pauses à organiser dans le volume de présence.

Le jeu Atlas est fictif. Une ligne valide décrit une vente élémentaire, pas un client ou une commande complète. Le lot initial donne **16 = 12 retenues + 1 doublon + 3 rejets**, **32 articles**, **99.000 TND**. Après ajout : **14 faits, 35 articles, 115.500 TND**. Le rejeu conserve ces totaux. Les montants sont stockés en **millimes entiers** ; le chiffre d’affaires ne donne ni stock ni bénéfice.

## IA gratuite et options CLI

Le socle utilise un **chat web gratuit disponible sur votre compte**, puis des programmes locaux. Aucune clé API, aucun abonnement ni agent payant n’est nécessaire. Les cibles de demandes sont pédagogiques, jamais une promesse de quota.

Le guide explique les installations Codex CLI et Claude Code **pour les comptes qui disposent déjà de l’accès nécessaire**. Claude Free n’inclut pas Claude Code ; l’accès gratuit à un autre produit ne prouve pas celui du CLI. Si l’accès manque, continuer avec le chat web et les étapes manuelles.

Python et SQLite sont libres. Docker Engine fournit la route open source sous Ubuntu. Docker Desktop est gratuit pour l’éducation selon ses conditions, avec des composants propriétaires. ChatGPT et Claude sont des services propriétaires à offre gratuite.

## Maintenir les supports

Le code des exercices utilise la bibliothèque standard. Pour ses contrôles :

```text
python -m unittest discover -s tests -v
```

Les sources PDF sont dans `authoring/content/`, le rendu dans `authoring/build_pdfs.py`, et les sources de la présentation dans `authoring/slides/`. Les dépendances d’édition sont séparées dans `authoring/requirements.txt` et `authoring/slides/package.json` ; elles ne sont pas nécessaires aux étudiants.

La configuration CI prépare des vérifications Windows, Ubuntu et macOS. Seul le résultat réel d’une exécution CI prouve qu’elle a passé ; sa présence dans le dépôt ne le garantit pas.

Youssef Douma · Leaders University · édition du 27 octobre 2026
