# De la demande de la direction au rapport : le parcours en images

[Commencer le cours](../README.md) · [Livret 00 — Lire-moi](../pdf/00_lire_moi.pdf) · [Livret 01 — Démarrer](../pdf/01_demarrer.pdf)

## A — Comprendre la mission

Vous rejoignez Solen Digital. Son client Maison Zitouna veut savoir où passe la marge. Chaque étape du cours se justifie par la précédente : une question métier, des données, un indicateur défini précisément, une décision.

![De la question de la direction à la décision](images/diagrams/v7-direction-decision.png)

## B — Qui fait quoi : Codex, vous, votre binôme

Codex écrit le code. Vous lisez le diff et lancez les contrôles. Votre binôme relit. L'équipe livre. Aucun code n'entre dans `main` sans ces trois regards.

![Codex propose, les humains décident](images/diagrams/v7-codex-controle.png)

Modèle, effort, vitesse, tokens, contexte et quota sont six choses différentes. Le cours n'utilise que les réglages visibles sur un compte Free.

![Tokens, contexte, effort, quota](images/diagrams/v7-tokens-contexte.png)

## C — Installer : Windows avec WSL2, ou Ubuntu

L'installation se fait **chez vous, avant la séance 1** : c'est la séance 0 (≈ 2 h), avec le livret 01, parties A à C. La séance 1 commence par 30 minutes de vérification des postes ; le dépôt du binôme est ensuite créé à deux, en séance.

Sous Windows, l'application ChatGPT reste une fenêtre Windows ; l'agent Codex, Python et Git travaillent dans Ubuntu WSL2 ; Power BI Desktop reste sur Windows. Sous Ubuntu natif, tout se fait dans Ubuntu sauf Power BI, sur un poste Windows de la salle ou du binôme.

![Qui fait quoi et sur quel système](images/diagrams/v7-postes-wsl.png)

## D — Travailler à deux avec Git et GitHub

Deux copies locales, une copie partagée sur GitHub. Les fichiers ne se synchronisent pas tout seuls : commit, push, pull, pull request. La première pull request du binôme (A auteur) est celle du livret 01 ; la deuxième, dès la séance 1, a B pour auteur.

![Trois emplacements pour un même dépôt](images/diagrams/v7-trois-emplacements.png)

![Le cycle d'une pull request](images/diagrams/v7-cycle-pr.png)

Deux choses portent le même nom de « workflow ». Le **workflow de travail** est la suite de vos gestes : branche → pull request → revue → merge. Le **workflow GitHub Actions** est le fichier `.github/workflows/controles.yml`, que GitHub exécute tout seul à chaque pull request sur une machine neuve (onglet Actions).

## E — Des quatre sources à l'entrepôt

CSV, Excel, JSON et une base SQLite opérationnelle entrent ; l'ETL écrit par Codex nettoie, harmonise, dédoublonne, charge les dimensions puis les faits ; les rejets vont dans `rejets.csv` avec leur motif.

![Des quatre sources au rapport](images/diagrams/v7-pipeline.png)

![Nettoyer sans toucher aux sources](images/diagrams/v7-nettoyage.png)

![L'étoile de la mission d'entraînement](images/diagrams/v7-etoile.png)

![Clé métier et clé technique](images/diagrams/v7-cles.png)

## F — Mettre à jour sans perdre le passé

Chargement initial, puis incrément, puis rejeu : le rejeu n'ajoute rien. Nabeul change de zone le 2026-07-15 ; une vente du 14 juillet garde l'ancienne version.

![Charger, compléter, rejouer](images/diagrams/v7-chargements.png)

![NBE change de zone le 2026-07-15](images/diagrams/v7-scd2-frise.png)

## G — Livrer et prouver

Un chiffre plausible n'est pas un chiffre juste : seul un contrôle les distingue. L'application locale et Power BI montrent les mêmes indicateurs, avec leurs unités.

![Un chiffre plausible n'est pas un chiffre juste](images/diagrams/v7-indicateur-controle.png)

![Application locale de référence, vue direction](images/captures/app-vue-direction.png)

*Capture réelle de l'application de référence (navigateur intégré, macOS, 28 octobre 2026). Les valeurs affichées sont les valeurs de référence après le lot 2. Le registre de provenance des captures est dans [images/captures/REGISTRE.json](images/captures/REGISTRE.json).*

## H — Le calendrier et la soutenance

Séance 0 chez vous (≈ 2 h), cinq séances de 4 h, puis la soutenance. Votre mission du catalogue, choisie en fin de séance 3, commence en séance : les 50 dernières minutes de la séance 4 servent à passer à votre mission, la première moitié de la séance 5 la mène jusqu'à l'application. Le travail personnel (≈ 8 h) se répartit en 2 h de séance 0, 4 h de mission et 2 h de finition, recommandation et préparation orale.

![Cinq séances, une mission, une soutenance](images/diagrams/v7-seances.png)

![Soutenance : 120 minutes à partager](images/diagrams/v7-soutenance.png)

Les schémas décrivent le fonctionnement et ne prétendent pas montrer l'interface réelle de votre poste. Les sources officielles vérifiées le 28 octobre 2026 sont dans [setup/sources.json](setup/sources.json).
