# Maintenir les supports du cours

[Retour au parcours étudiant](../README.md)

Ce dossier sert à modifier et reconstruire les documents. Les étudiants peuvent suivre les missions sans installer les dépendances d’édition ci-dessous.

## Retrouver les sources

| Élément | Source | Résultat |
|---|---|---|
| Cinq livrets PDF | `content/` et `build_pdfs.py` | `../pdf/` |
| Présentation PowerPoint et conversion PDF | [Guide des slides](slides/README.md) | `../presentation/` |
| Logo, polices et droits | [Provenance des assets](ASSETS.md) | Ressources utilisées dans les documents |
| Installation et références logicielles | [Guide d’environnement](../docs/setup/README.md) · [sources officielles](../docs/setup/sources.json) | Guide 01 |

## Reconstruire les PDF

Avec Python 3.10 ou ultérieur et un environnement virtuel d’édition séparé, depuis la racine du cours :

```text
python -m pip install -r authoring/requirements.txt
python authoring/build_pdfs.py
python authoring/check_materials.py
```

`build_pdfs.py` lit les cinq fichiers JSON de `content/` et écrit les cinq PDF. Le contrôle suivant compare le code imprimé aux sources et exécute les exemples avec leurs prérequis. Inspecter aussi chaque page modifiée à taille lisible ; un contrôle automatique ne remplace pas la revue visuelle.

## Vérifier les exercices et distribuer

Depuis la racine, les tests des exercices utilisent uniquement la bibliothèque standard :

```text
python -m unittest discover -s tests -v
```

Les résultats réellement exécutés par GitHub sont consultables dans [Actions](https://github.com/jodouma/leaders-bi-ia-etl-28h/actions). Ils vérifient le code sur Windows, Ubuntu et macOS et la référence Docker sur Ubuntu ; ils ne prouvent pas une installation réalisée sur un poste étudiant neuf.

Après les modifications et leurs vérifications, `python authoring/package_course.py` reconstruit le ZIP étudiant dans le dossier `livraison/` adjacent au dépôt. Vérifier ce ZIP extrait et conserver les guides privés hors du dépôt public. Le [protocole d’essai depuis zéro](../TESTER_LE_COURS.md) décrit les retours attendus des testeurs.
