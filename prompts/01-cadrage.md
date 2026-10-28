# 01 — Cadrer les indicateurs avec la direction

**Quand l'utiliser** : séance 1, après le mail de la direction (« les ventes montent,
mais où passe la marge ? »), et au début de chaque mission du catalogue. Aucun code
n'est écrit à cette étape.

**Avant d'envoyer** : ouvrez l'échantillon de la mission (`echantillon/`) et calculez
**à la main**, sur papier, les ventes brutes en TND. Notez votre résultat.

## Le prompt

```text
Lis mission.txt, le cahier des charges et le dictionnaire de la mission <mission>,
ainsi que les fichiers de <dossier echantillon>.
Ne modifie aucun fichier et n'écris pas de code.
Pour chaque indicateur demandé par la direction, donne en tableau :
nom, définition en une phrase, formule, unité (millimes, TND, %, quantité),
grain du fait utilisé, et le calcul sur l'échantillon ligne par ligne.
Mon calcul à la main des ventes brutes donne <ma valeur> TND : compare et explique l'écart s'il y en a un.
Liste ensuite au plus 3 questions ambiguës à poser à la direction
(ex. un retour sans ticket compte-t-il ?), avec la conséquence de chaque réponse sur un chiffre.
```

## Vérifier dans la réponse

- Chaque indicateur a une **unité** et une formule identique au cahier des charges
  (« marge sur coût d'achat », jamais « bénéfice »).
- Le calcul sur l'échantillon est détaillé ligne par ligne et retombe sur `attendu.md`.
- Les questions sont de vraies ambiguïtés métier, pas des questions techniques.
- Notez vos décisions de cadrage dans `notes/JOURNAL.md` (rubrique Décision).

## Deux erreurs fréquentes

1. Accepter la valeur de Codex sans avoir fait son propre calcul : vous ne saurez
   pas l'expliquer à l'oral.
2. Mélanger millimes et TND dans le même tableau (12500 « TND » au lieu de 12,500 TND).
