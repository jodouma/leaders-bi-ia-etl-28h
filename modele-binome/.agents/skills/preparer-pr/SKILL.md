---
name: preparer-pr
description: Préparer une pull request du dépôt binôme Solen — vérifier contrôles, diff et journal, puis proposer un titre et une description en français avec le relecteur nommé. Ne commite, ne pousse et n'ouvre rien.
---

Tu prépares ; l'étudiant exécute Git et ouvre la PR lui-même. Ne lance ni
`git commit`, ni `git push`, ni `gh pr create`.

Vérifie dans l'ordre et réponds par une liste OK / À corriger / Non vérifié :

1. **Branche** : on n'est pas sur `main` (`git branch --show-current`).
2. **Contrôles** : lance le contrôle de l'étape (`python -m controles.verifier
   --mission $(cat mission.txt) --etape <étape>`) et `pytest controles` ;
   recopie la dernière ligne réelle de chaque sortie.
3. **Diff** : `git status` et `git diff --stat main...` ; signale tout fichier
   modifié hors de `solen/`, `tests/`, `powerbi/`, `notes/`, `.github/`
   (en particulier sources, références, `controles/`) et tout fichier `outputs/`,
   `.venv/` ou secret prêt à être commité.
4. **Lecture** : demande à l'étudiant quel fichier du diff il a lu et ce que fait
   la ligne la plus importante. N'accepte pas « j'ai tout lu » sans exemple.
5. **Journal** : `notes/JOURNAL.md` a une entrée datée pour cette PR, avec état
   actuel, décision, preuve (commande + résultat réel), prochain objectif. Si elle
   manque, propose le texte ; ne l'écris que si on te le demande.
6. **Relecteur** : le partenaire, pas l'auteur.

Propose ensuite, sans l'envoyer :

```text
Titre : <verbe à l'infinitif> <résultat observable>
        (ex. « Rejeter les lignes à quantité invalide »)

## Ce qui change
- <1 à 3 puces, fichiers principaux>

## Preuve
- `<commande>` → <résultat réel>

## À relire en priorité
- <fichier:ligne> — <pourquoi>

## Non vérifié
- <ce qui n'a pas été contrôlé>

Relecteur : <compte GitHub du partenaire>
```

Si un point est « À corriger », dis lequel régler avant d'ouvrir la PR.
