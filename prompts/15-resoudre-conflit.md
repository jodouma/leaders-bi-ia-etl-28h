# 15 — Résoudre un conflit Git

**Quand l'utiliser** : `git pull` ou un **Merge** affiche `CONFLICT`. En séance 4,
le conflit est provoqué volontairement : A et B modifient la même ligne de
`notes/JOURNAL.md` dans deux branches.

**Avant d'envoyer** : tapez `git status`. Quels fichiers sont « both modified » ?
Ouvrez-en un et repérez `<<<<<<<`, `=======`, `>>>>>>>`. Qu'est-ce que chacun des
deux blocs voulait dire ?

## Le prompt

```text
J'ai un conflit Git. Voici la sortie exacte de git status :
<coller>
Explique en mots simples ce qui s'est passé (quelles deux versions se rencontrent).
Pour chaque fichier en conflit, montre les deux blocs et dis ce que chacun voulait garder.
Propose une résolution qui garde l'intention des deux, sans perdre de contrôle ni de règle.
Ne modifie un fichier qu'après mon accord, et seulement les fichiers en conflit.
Ne lance ni git add, ni git commit, ni git push : je les fais moi-même.
Après résolution, indique les contrôles à relancer.
```

Puis, vous-même : relire le fichier (plus aucun marqueur), relancer les contrôles,
`git add <fichier>`, `git commit` (message proposé par Git), `git push`.

## Vérifier dans la réponse

- La résolution proposée contient les deux intentions, ou explique clairement
  pourquoi l'une est abandonnée — c'est **votre** décision, pas celle de Codex.
- `grep -n "<<<<<<<\|>>>>>>>" <fichier>` ne trouve plus rien.
- Les contrôles passent après la résolution, pas seulement avant.

## Deux erreurs fréquentes

1. Garder « ma version » d'un clic sans lire l'autre : le travail du binôme disparaît.
2. Laisser un marqueur `=======` dans un fichier Python : le code ne s'exécute plus.
