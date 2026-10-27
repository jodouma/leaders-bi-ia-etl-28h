# IA, Codex et BI — votre première mission chez Atlas

**15 h · 5 séances de 3 h · Licence BI · grands débutants · français.**

Vous venez de rejoindre **Atlas Papeterie**, une entreprise fictive. Votre responsable vous confie ses ventes : « Dites-moi combien nous vendons, où, et si je peux faire confiance aux chiffres. » Vous construisez la réponse avec **Codex**, puis vous la prouvez dans **Power BI**.

**CSV + base SQL → nettoyage Python → entrepôt en étoile → Power BI.**

## Commencer

1. **[Télécharger le ZIP](https://github.com/jodouma/leaders-bi-ia-etl-28h/archive/refs/heads/main.zip)** — bouton **Code → Download ZIP**. Extraire tout ; aucun compte GitHub n’est nécessaire.
2. Ouvrir **[01_demarrer_windows_ubuntu.pdf](pdf/01_demarrer_windows_ubuntu.pdf)**. Choisir Windows avec WSL2, ou Ubuntu pris en charge.
3. Ouvrir **[02_cours_atlas_ia.pdf](pdf/02_cours_atlas_ia.pdf)**. Créer votre dossier `atelier/` avec le jalon 01, puis commencer la séance 1.

**[Le parcours en images](docs/DEMARRER_EN_IMAGES.md)** explique les outils, les dossiers et les étapes.

## Cinq séances, un projet

| Séance | Votre mission | Preuve obtenue |
|---|---|---|
| 1 | Prendre son poste, découvrir Codex et la BI | Un atelier qui fonctionne et un résultat expliqué |
| 2 | Lire les CSV et une vraie base SQL ; nettoyer | Des ventes propres, des rejets compris |
| 3 | Charger l’entrepôt, ajouter un lot, garder l’historique | Un rejeu sans doublon et les anciennes zones conservées |
| 4 | Construire le tableau de bord et une méthode de revue | Quatre tables reliées dans Power BI ; une revue vérifiable |
| 5 | Réparer et livrer, en groupe de trois maximum | Une démonstration, des contrôles et une décision métier |

Le temps prévu comprend **255 min de théorie, 595 min de pratique et 50 min de pauses** : 70 % de pratique sur le temps de travail. Les durées sont des estimations pédagogiques.

## Les supports, dans l’ordre

| Besoin | Ouvrir |
|---|---|
| Installer et se repérer | [01 — Démarrer sous Windows ou Ubuntu](pdf/01_demarrer_windows_ubuntu.pdf) |
| Construire le projet | [02 — Cours et missions Atlas](pdf/02_cours_atlas_ia.pdf) |
| Comprendre un mot, préparer une demande, se débloquer | [03 — Prompts, repères et dépannage](pdf/03_prompts_reperes_depannage.pdf) |
| Réaliser la mission en groupe | [04 — Défi Atlas](pdf/04_defi_atlas.pdf) |
| Après une première tentative | [05 — Indices et corrigés](pdf/05_indices_et_corriges.pdf) |
| Suivre la présentation | [PowerPoint modifiable](presentation/Atlas_CODEX_BI_15h.pptx) · [PDF](presentation/Atlas_CODEX_BI_15h.pdf) |

Les [demandes prêtes à adapter](prompts/README.md) accompagnent les missions. On avance par petites étapes : **prévoir → demander → exécuter → contrôler → expliquer → faire relire → corriger**.

## Où travailler ?

| Élément | Rôle |
|---|---|
| `atelier/` | Votre copie de travail, créée avec `outils/jalon.py` ; les commandes Python se lancent ici |
| `projet/` | Le point de départ fourni ; certaines fonctions restent à construire |
| `atelier/data/` | Les sources fictives CSV et SQLite ; les conserver intactes |
| `atelier/outputs/` | La base, le rapport et les quatre CSV produits |
| `powerbi/` | Le guide du tableau de bord et le projet de reprise facultatif |
| `.agents/skills/` | Deux méthodes locales : expliquer une notion et relire la BI |
| `solutions/` | Les références à consulter après votre essai |

**Windows :** Codex s’ouvre dans une fenêtre Windows ; son agent et Python travaillent dans **Ubuntu WSL2**. Les commandes `python3` du cours se saisissent dans le terminal Ubuntu. **Power BI Desktop s’utilise sur Windows**, avec une copie des CSV exportés.

**Ubuntu :** Codex et Python travaillent directement dans Ubuntu. Pour la partie Power BI Desktop, transférer les CSV sur le poste Windows d’un binôme ou de la salle. Le guide 01 détaille ce passage.

## Codex gratuit : travailler avec méthode

L’offre Free annonce **GPT-6 Luna, vitesse Standard, dans l’application de bureau**, sous réserve du déploiement. Vérifier l’accès sur votre compte avant la séance. Le cours ne demande **ni abonnement, ni clé API** ; le CLI n’est pas un prérequis. [Source OpenAI](https://learn.chatgpt.com/docs/pricing).

Choisir **Luna** et commencer avec **High si ce réglage est proposé**. *Standard* désigne la vitesse ; l’effort de réflexion est un réglage différent. Le cours fait comparer les options réellement visibles, sans imposer de modèle payant. [Modèles et efforts](https://learn.chatgpt.com/docs/models).

Une séance de 3 h alterne de courtes demandes à Codex, des manipulations et des vérifications locales. **Trois heures de cours ne garantissent pas trois heures d’appels IA.** Consulter l’usage affiché ; si la limite est atteinte, poursuivre les activités locales et les jalons fournis. La revue avec deux sous-agents reste un essai borné si la fonction est disponible ; deux contrôles successifs permettent aussi d’apprendre la méthode.

## Ce que vous devez pouvoir prouver

Le projet final contient **14 ventes, 35 articles et 115.500 TND**. Une seconde exécution du même lot conserve ces valeurs. Nabeul change de **zone commerciale** le 8 janvier : les ventes anciennes restent rattachées à l’ancienne version de la boutique. Le total historique est **43.500 TND pour Cap Bon** et **72.000 TND pour Grand Tunis**.

Les scripts de vérification aident à trouver les erreurs ; vous devez aussi expliquer les résultats. En cas de blocage, conserver le message exact, consulter le livret 03, puis les indices du livret 05. Une reprise par jalon se fait dans un nouveau dossier, sans écraser votre travail.

Pour essayer le cours depuis zéro : **[TESTER_LE_COURS.md](TESTER_LE_COURS.md)**. Pour reconstruire les documents : [guide d’édition](authoring/README.md).

Python et SQLite sont libres. Codex et Power BI Desktop sont des logiciels propriétaires utilisables gratuitement dans le cadre décrit ; le cours ne demande aucun service payant.

Youssef Douma · Leaders University · édition du 27 octobre 2026
