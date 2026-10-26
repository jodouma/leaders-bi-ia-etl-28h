# Atlas Papeterie — Python, ETL et entrepôts de données

**Un parcours de 28 h pour débuter en licence Business Intelligence, sur Windows.**
Vous partez de fichiers de ventes et construisez un entrepôt de données, puis un rapport qui aide à préparer les achats de deux boutiques fictives.

## Commencer ici

1. Récupérer le **ZIP du cours fourni par votre enseignant**, puis clic droit → **Extraire tout…**. Travailler dans le dossier extrait, jamais dans le ZIP.
2. Ouvrir **[pdf/01_demarrer_windows.pdf](pdf/01_demarrer_windows.pdf)** : installation de Thonny, premiers gestes et dépannage. Aucun compte GitHub ni Git à installer.
3. Ouvrir **[pdf/02_cours_atlas.pdf](pdf/02_cours_atlas.pdf)** : le cours se suit dans l’ordre, mission après mission.
4. Dans Thonny : **Fichier → Ouvrir → scripts/01_premiers_pas.py**, puis **F5**. Lire le résultat dans la zone Shell.

**Python ≥ 3.10, bibliothèque standard uniquement.** Après téléchargement du logiciel et du dossier, le parcours fonctionne hors connexion. Aucun paquet à installer, aucun serveur à configurer.

## Un seul projet qui grandit

| Mission | Ce que vous construisez |
|---|---|
| 01 · Premiers gestes | Un calcul de vente et votre première modification de code |
| 02 · Extraction | La lecture d’un fichier CSV et un aperçu des lignes |
| 03 · Qualité | Des données nettoyées, des rejets expliqués et des doublons identifiés |
| 04 · Transformation | Des montants calculés et contrôlés, en millimes |
| 05 · SQL | Vos premières questions à une base de données |
| 06 · Modélisation | Un entrepôt en étoile : faits, dimensions et clés |
| 07 · Chargement | Des dimensions puis des faits dans `outputs/atlas.sqlite` |
| 08 · Incrémental | De nouvelles ventes, sans compter deux fois les anciennes |
| 09 · Rapport | `outputs/rapport_atlas.html`, à ouvrir dans votre navigateur |
| 10 · Défi | Une réparation, une nouvelle exécution et une décision expliquée |

À chaque étape : **comprendre → prédire → essayer → vérifier → expliquer**. Une courte variante vérifie votre compréhension ; les extensions sont facultatives. Les durées sont des estimations pédagogiques, pas des temps mesurés auprès d’étudiants.

## Vos supports

| Fichier | Utilisation |
|---|---|
| [01_demarrer_windows.pdf](pdf/01_demarrer_windows.pdf) | Commencer et installer les outils |
| [02_cours_atlas.pdf](pdf/02_cours_atlas.pdf) | Comprendre les notions et suivre les travaux pratiques |
| [03_reperes_et_depannage.pdf](pdf/03_reperes_et_depannage.pdf) | Retrouver le vocabulaire, les gestes et les solutions aux erreurs courantes |
| [04_indices_et_corriges.pdf](pdf/04_indices_et_corriges.pdf) | Chercher un indice après un premier essai, puis comparer une correction expliquée |
| [Atlas_ETL_28h.pptx](presentation/Atlas_ETL_28h.pptx) | Présentation modifiable ; version PDF dans le même dossier |

Les `scripts/` sont les fichiers à ouvrir dans Thonny. Les `examples/` reproduisent les courts exemples du cours. `atelier.py` contient les fonctions communes, expliquées progressivement. Garder les fichiers de `data/` intacts ; les résultats vont dans `outputs/`.

## Les données, sans ambiguïté

Une ligne valide décrit **une vente élémentaire d’un produit, dans une boutique, à une date**. Elle ne compte ni un client ni une commande complète. Toutes les données sont fictives.

- Lot initial : **16 lignes = 12 ventes retenues + 1 doublon + 3 rejets**.
- Ces ventes représentent **32 articles** et **99.000 TND** ; le point est le séparateur décimal des fichiers.
- Lot suivant : **2 nouvelles ventes + 1 vente déjà présente** ; après ajout : **14 ventes, 35 articles, 115.500 TND**.
- Rejouer le même lot ne doit pas augmenter ces totaux. Une même référence de vente avec un autre contenu provoque un conflit explicite.

**1 TND = 1 000 millimes.** Les montants en base sont des entiers en millimes. Le chiffre d’affaires décrit les seules ventes acceptées ; il ne donne ni le bénéfice, ni le stock disponible, ni une prévision.

## Reconstruire et vérifier le dépôt

Pour les personnes qui maintiennent le cours, depuis la racine du dossier :

```text
python -m unittest discover -s tests -v
python authoring/check_materials.py
```

Les quatre PDF se reconstruisent avec `python authoring/build_pdfs.py` après installation, dans un environnement séparé, des dépendances de `authoring/requirements.txt`. La présentation possède son propre générateur `authoring/build_slides.js` ; les instructions sont dans `authoring/README_slides.md`. Ces outils d’édition ne sont pas nécessaires aux étudiants.

Le dépôt contient une configuration de vérification Windows, macOS et Ubuntu. La présence de ce fichier ne signifie pas que ces vérifications distantes ont déjà été exécutées.

Youssef Douma · Leaders University · édition du 26 octobre 2026
