# `solen/` — le paquet que Codex va écrire

Ce dossier est volontairement vide. C'est ici, et seulement ici, que **Codex**
crée le code Python du pipeline Solen. Vous ne tapez aucune ligne de code : vous
demandez une petite étape, vous lisez le diff, vous lancez les contrôles.

Ce que le paquet devra offrir, une commande à la fois :

| Commande | Ce qu'elle doit produire |
|---|---|
| `python -m solen initial` | `outputs/entrepot.sqlite` recréé avec le lot 1, `outputs/rejets.csv` |
| `python -m solen increment` | le lot 2 ajouté ; relancée, elle n'ajoute rien (rejeu) |
| `python -m solen export` | `outputs/export/<table>.csv` + `outputs/export/manifest.json` |
| `python -m solen app` | `outputs/app/index.html`, à ouvrir dans le navigateur |

Toutes lisent `mission.txt` pour savoir quelles données traiter.

Aucune installation du paquet n'est nécessaire : lancé depuis la racine du dépôt,
`python -m solen …` trouve ce dossier tout seul. Le fichier `solen/__main__.py`
que Codex créera est le point d'entrée des quatre commandes.

Quand Codex a créé un fichier ici, ouvrez-le et cherchez : où le fichier source
est lu, où une ligne est rejetée, où les millimes sont calculés. Vous devez
pouvoir le montrer à l'oral.
