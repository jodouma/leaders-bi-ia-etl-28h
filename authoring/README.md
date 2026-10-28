# Reconstruire les supports et les données

[Retour au cours](../README.md)

Les étudiants n'ont pas besoin de ce dossier. Il contient les sources éditables et les scripts qui reconstruisent tout ce qui est publié.

| Support | Sources | Résultat |
|---|---|---|
| Sept livrets étudiants | `content/0N_*.json` + `build_pdfs.py` | `../pdf/0N_*.pdf` |
| Dix guides de mission | `content/missions/M0N.json` + `build_pdfs.py --missions` | `../pdf/missions/M0N_guide.pdf` |
| Données des onze missions et valeurs de référence | `generateurs/mission*.py` + `generateurs/common.py` | `../modele-binome/tronc-commun/`, `../modele-binome/catalogue/M0N/` |
| Seize schémas | `visuals/generate.py` | `../docs/images/diagrams/v7-*.svg|png` |
| Présentation éditable et PDF | `slides/` (voir son README) | `../presentation/` |
| Logos et polices | `assets/` ; provenance dans `ASSETS.md` | redistribués avec leurs licences |
| Sources officielles | `../docs/setup/sources.json` (vérifiées le 28 octobre 2026) | livret 01 |

## Environnement d'édition

Python 3.11 ou plus récent, dans un environnement virtuel séparé du poste étudiant :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r modele-binome/requirements.txt -r authoring/requirements.txt
```

## Commandes

```bash
python authoring/generateurs/mission00_commerce360.py      # régénère le tronc commun (déterministe)
python authoring/generateurs/verifier_reproductibilite.py  # chaque générateur reproduit les fichiers publiés
python authoring/visuals/generate.py                       # schémas
python authoring/build_pdfs.py --missions                  # livrets + guides de mission ; rapport de mise en page
```

Les générateurs écrivent les sources (CSV, Excel, JSON, SQLite), l'échantillon calculable à la main, les cahiers des charges et les valeurs de référence `reference/attendu_*.json` **calculées depuis la vérité terrain**, sans passer par un ETL. Le vérificateur étudiant `modele-binome/controles/verifier.py` lit ces références et `reference/contrat_entrepot.json` ; il ne connaît aucune implémentation.

Le rapport `pdf_layout_report.json` liste, par page, la position du bas de page et les figures manquantes. Une figure absente est rendue comme un cadre « capture à réaliser » et signalée ; la CI du cours refuse un livret publié avec une figure manquante.

Les solutions de référence, les lots d'évaluation privés, le guide du jury et les reçus de QA sont conservés hors du dépôt, dans le dossier privé du formateur. `package_course.py` crée le ZIP étudiant à partir d'une liste explicite de dossiers publics et refuse tout fichier privé.
