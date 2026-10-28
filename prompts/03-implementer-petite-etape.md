# 03 — Réaliser une petite étape

**Quand l'utiliser** : sur une branche neuve, pour l'étape choisie dans le plan
(prompt 02). Sert aussi en séance 5 pour l'application locale (`python -m solen app`).

**Avant d'envoyer** : `git switch -c <branche>`. Écrivez la valeur que vous
attendez (ex. « 1 482 lignes acceptées »), ou au moins son ordre de grandeur.

## Le prompt

```text
Réalise seulement l'étape <n> du plan : <rappel de l'étape en une phrase>.
Écris le code uniquement dans solen/. Ne touche ni aux sources, ni aux références, ni à controles/.
Garde les montants en millimes entiers.
Ensuite :
1. lance <commande de contrôle> et recopie la sortie réelle ;
2. résume le diff en 3 à 6 lignes : fichiers, fonctions, rôle de chacune ;
3. indique les 3 lignes que je dois lire en priorité, avec leur numéro ;
4. je prévois <ma valeur> : dis si le résultat obtenu est égal, et sinon pourquoi.
Ne fais ni commit ni push.
```

## Vérifier dans la réponse

- La sortie de contrôle est **recopiée**, pas résumée par « ça passe ». Relancez la
  commande vous-même dans votre terminal.
- `git diff` ne montre que les fichiers annoncés. Lisez les 3 lignes indiquées et
  expliquez-les à votre binôme.
- Les montants sont des `int` (pas de `float` stocké dans l'entrepôt).

## Deux erreurs fréquentes

1. Enchaîner trois étapes dans la même conversation sans commit entre elles : le
   diff devient illisible. Une étape = un commit, au plus une PR.
2. Croire que la commande « a été lancée » parce que Codex l'a écrite : vérifiez
   qu'il montre une vraie sortie, ou lancez-la.
