# Construire une solution BI avec l’IA — Atlas Papeterie

**28 h · Licence BI · grands débutants · français · Windows et Ubuntu · 70 % pratique.**

À partir des ventes fictives de deux papeteries, vous construisez un projet utile : **fichiers CSV → ETL → entrepôt SQLite en étoile → rapport de ventes**. L’IA aide à écrire de petites fonctions ; vous définissez les règles, exécutez le code et vérifiez les résultats.

## Commencer ici

1. **[Télécharger le cours en ZIP](https://github.com/jodouma/leaders-bi-ia-etl-28h/archive/refs/heads/main.zip)**, ou choisir **Code → Download ZIP** en haut du dépôt. Extraire tout dans un nouveau dossier, puis renommer le dossier contenant ce README en `atlas-bi-ia-28h`. Aucun compte GitHub ni commande Git n’est nécessaire.
2. **Ouvrir [01_demarrer_windows_ubuntu.pdf](pdf/01_demarrer_windows_ubuntu.pdf)** dans le dossier extrait. Suivre la route de son poste : Windows **ou** Ubuntu. Installer les outils et vérifier leur fonctionnement avant de commencer les exercices.
3. **Ouvrir [02_cours_atlas_ia.pdf](pdf/02_cours_atlas_ia.pdf)** et commencer la mission 01. Modifier les fichiers dans **`projet/`**, en gardant le reste du cours autour de ce dossier.

Les fonctions de départ sont volontairement incomplètes. Le message « mission à construire » est attendu avant de les réaliser. **La construction de l’environnement Docker doit, elle, réussir** : une erreur d’installation est à résoudre avec le guide 01.

## Comment avancer

Pour chaque mission : **lire la consigne → demander une fonction à l’IA → enregistrer → exécuter → contrôler → expliquer le résultat**. Les [prompts prêts à copier](prompts/README.md) accompagnent le cours. Conserver une première tentative avant de consulter un corrigé.

Le parcours comprend **sept missions guidées sur 21 h**, puis **7 h de défi Campus Box**, en groupes de trois maximum. Le livret 03 sert pendant les missions ; le livret 05 apporte des indices après un essai ; le défi 04 commence après les sept missions.

| Quand l’ouvrir | Support |
|---|---|
| Avant toute manipulation | [01 — Installer son atelier sous Windows ou Ubuntu](pdf/01_demarrer_windows_ubuntu.pdf) |
| Pendant les sept missions | [02 — Construire sa BI avec l’IA](pdf/02_cours_atlas_ia.pdf) |
| Pour un mot, un prompt ou un problème | [03 — Prompts, repères et dépannage](pdf/03_prompts_reperes_depannage.pdf) |
| Après les sept missions | [04 — Défi Campus Box](pdf/04_defi_campus_box.pdf) |
| Après une première tentative, si besoin | [05 — Indices et corrigés](pdf/05_indices_et_corriges.pdf) |
| En complément du cours | Présentation : [PowerPoint modifiable](presentation/Atlas_BI_IA_28h.pptx) · [PDF](presentation/Atlas_BI_IA_28h.pdf) |
| Pour évaluer le parcours depuis zéro | [Fiche de test du cours](TESTER_LE_COURS.md) |

Les temps sont des estimations pédagogiques : **8 h 24 de théorie et 19 h 36 de pratique**, installation et dépannage compris ; pauses à organiser dans le volume de présence.

## Se repérer dans les dossiers

| Dossier | Ce qu’on y fait |
|---|---|
| `projet/` | Modifier et exécuter les fichiers des missions |
| `projet/data/` | Lire les CSV d’origine ; conserver ces fichiers intacts |
| `projet/outputs/` | Retrouver les fichiers produits au fil des missions : CSV, base et rapport |
| [prompts/](prompts/README.md) | Copier la demande correspondant à la mission en cours |
| [defi/](defi/student_challenge.md) | Découvrir le nouveau cas après le parcours guidé |
| `solutions/atlas/` | Consulter la référence après une tentative ; garder son propre travail dans `projet/` |

**Où saisir les commandes ?** Modifier les fichiers dans `projet/` dans tous les cas, mais choisir le bon dossier pour le terminal :

| Route choisie dans le guide 01 | Terminal | Dossier depuis lequel lancer les commandes |
|---|---|---|
| Docker sous Windows | PowerShell Windows | Racine du cours, où se trouve `compose.yaml` |
| Docker sous Ubuntu | Terminal Ubuntu, avec les commandes `sudo docker compose` du guide | Même racine du cours, après le réglage `.env` expliqué dans le guide |
| Python natif, sans Docker | Thonny ou terminal indiqué dans le guide | `projet/` pour les commandes Python ; dans Thonny, ouvrir le fichier de cette mission |

Sous Windows, WSL 2 sert au fonctionnement de Docker ; **les commandes Windows du cours se saisissent dans PowerShell**. Le [rappel d’environnement](docs/setup/README.md) complète le guide d’installation.

## Vérifier son résultat et trouver de l’aide

Le cours indique la commande de contrôle de chaque mission. Le vérificateur lit votre travail ; il ne termine pas les fonctions à votre place. En cas de blocage : consulter le livret 03, puis les indices du livret 05 si nécessaire. La reprise par jalon se fait dans **un nouveau dossier**, comme expliqué dans le cours.

À la fin, le rapport décrit **14 ventes élémentaires, 35 articles et 115.500 TND**. Le rejeu conserve ces totaux. Une ligne valide représente un produit vendu dans une boutique à une date ; les montants sont calculés et stockés en millimes entiers. Le chiffre d’affaires ne mesure ni le stock ni le bénéfice.

Le lien [rapport local](http://localhost:8000/rapport_atlas.html) fonctionne après création du rapport et démarrage du serveur, selon votre route d’installation. Pour tester la clarté du parcours ou signaler un blocage, suivre la [fiche de test](TESTER_LE_COURS.md).

## IA et outils

Le socle utilise un chat web gratuit disponible sur votre compte et des programmes locaux. **Aucune clé API ni abonnement payant n’est nécessaire au parcours principal.** Les demandes courtes limitent les échanges ; aucun quota fournisseur n’est garanti.

Codex CLI et Claude Code sont des options pour les comptes qui disposent déjà de l’accès nécessaire. Claude Free n’inclut pas Claude Code ; l’accès gratuit à un autre produit ne prouve pas celui du CLI. Le guide 01 explique les options et le repli vers le chat web.

Python et SQLite sont libres. Docker Engine fournit la route open source sous Ubuntu. Docker Desktop est gratuit pour l’éducation selon ses [conditions](https://docs.docker.com/subscription-billing/desktop-license/), avec des composants propriétaires. ChatGPT et Claude sont des services propriétaires à offre gratuite.

## Sources et maintenance

Les exercices utilisent uniquement la bibliothèque standard de Python. Les dépendances pour reconstruire les documents concernent l’édition des supports. Consulter le [guide de maintenance](authoring/README.md) pour les sources PDF, la présentation et les contrôles du dépôt.

Youssef Douma · Leaders University · édition du 27 octobre 2026
