# Reconstruire les supports

[Retour au cours](../README.md)

Les étudiants suivent les missions sans installer ces dépendances d’édition.

| Support | Sources | Résultat |
|---|---|---|
| Cinq livrets | `content/` et `build_pdfs.py` | `../pdf/` |
| Présentation éditable et PDF | [Guide des diapositives](slides/README.md) | `../presentation/` |
| Quatorze schémas | [Sources des visuels](visuals/README.md) | `../docs/images/diagrams/` |
| Logo et polices | [Provenance](ASSETS.md) | Ressources redistribuées avec licences |
| Installation | [Références officielles](../docs/setup/sources.json) | Guide 01 |

Avec Python 3.10 ou ultérieur dans un environnement d’édition séparé, depuis la racine :

```text
python3 -m pip install -r authoring/requirements.txt
python3 authoring/visuals/generate.py
python3 authoring/build_pdfs.py
python3 authoring/check_materials.py
python3 -m unittest discover -s tests -v
```

Le contrôle compare les panneaux de code imprimés, exécute les exemples avec leurs prérequis, parcourt les sept jalons et vérifie les exports. Inspecter aussi chaque page et chaque diapositive à taille lisible. Les contrôles automatiques ne prouvent ni une installation WSL, ni l’accès d’un compte Free, ni une manipulation Power BI.

Les [Actions GitHub](https://github.com/jodouma/leaders-bi-ia-etl-28h/actions) consignent les exécutions sur leurs systèmes. L’essai Power BI Desktop est un workflow séparé : son statut et ses captures doivent être lus avant d’en tirer une conclusion sur le chargement des données.

Après validation, `python3 authoring/package_course.py` crée `Atlas_CODEX_BI_15h_etudiants.zip` dans `livraison/`, à côté du dépôt. Tester ce ZIP extrait. Le dossier privé `formateur/` reste hors du dépôt et n’est jamais parcouru par le générateur d’archive.
