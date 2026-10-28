# 02 — Demander un plan court avant de coder

**Quand l'utiliser** : avant toute étape qui touchera plus d'un fichier (lecture des
sources, nettoyage, chargement, incrément, app…). Le plan devient la liste de vos
prochaines branches.

**Avant d'envoyer** : écrivez en une phrase le **résultat observable** que vous voulez
à la fin (un fichier, un compte, un total).

## Le prompt

```text
Objectif : <résultat observable, ex. « outputs/rejets.csv existe et compte les rejets par motif »>.
Mission : lis mission.txt et les fichiers utiles de la mission. Ne modifie rien pour l'instant.
Propose un plan de 3 à 5 petites étapes. Pour chaque étape :
- le fichier de solen/ créé ou modifié ;
- la sortie observable ;
- la commande de contrôle à lancer et le résultat attendu ;
- un nom de branche court.
Signale ce qui est hors de mon objectif et ce que tu ne sais pas encore.
Attends mon choix de l'étape à réaliser.
```

## Vérifier dans la réponse

- Chaque étape est assez petite pour une PR relue en moins de 15 minutes.
- Chaque étape a une preuve exécutable (`python -m controles.verifier …`, un compte,
  `pytest`), pas « vérifier que ça marche ».
- Aucun fichier hors de `solen/`, `tests/`, `.github/`, `powerbi/` n'est prévu.

## Deux erreurs fréquentes

1. Dire « oui, fais tout » : Codex écrit alors un gros diff que personne ne lit.
   Choisissez **une** étape.
2. Garder un plan dont une étape modifie `controles/` ou une source : refusez-la.
