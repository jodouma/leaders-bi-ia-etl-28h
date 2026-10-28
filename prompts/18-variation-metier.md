# 18 — Réaliser une variation métier (mission du catalogue)

**Quand l'utiliser** : sur votre mission du catalogue (`mission.txt` = `Mxx`), quand
la direction fictive demande une **variante** de la fiche mission (nouvel indicateur,
nouvelle règle, nouvelle source ou changement historique). Bon entraînement pour la
question « résoudre une variation avec Codex et la contrôler ».

**Avant d'envoyer** : lisez la variante dans `catalogue/<Mxx>/fiche_mission.md`.
Prévoyez : quelles tables changent ? Quel indicateur bouge, dans quel sens, et
environ de combien sur l'échantillon ?

## Le prompt — analyser d'abord

```text
Mission <Mxx> : lis mission.txt, la fiche mission, le cahier des charges et le dictionnaire.
La direction demande la variante <n> : <recopier la variante>.
Ne modifie rien. Donne :
1. la règle métier exacte et ce qui reste ambigu (question à poser à la direction) ;
2. l'impact : fichiers de solen/, tables, colonnes, indicateurs, exports, DAX, app ;
3. le calcul à la main sur l'échantillon, avant / après la variante ;
4. un plan de 2 à 4 petites étapes, chacune avec sa preuve ;
5. le test pytest qui prouvera la nouvelle règle.
Ma prévision : <tables touchées, sens et ordre de grandeur>. Compare.
```

## Le prompt — réaliser une étape

Utilisez ensuite le prompt **03** pour chaque étape du plan, sur une branche dédiée,
puis **09** pour le test et **13** pour la PR.

## Vérifier dans la réponse

- L'ambiguïté est tranchée par **vous** (et notée dans `notes/JOURNAL.md`, rubrique
  Décision), pas par Codex.
- Les contrôles de référence de la mission restent verts : une variante ajoute, elle
  ne casse pas l'existant.
- Le nouveau chiffre est vérifié à la main sur l'échantillon.

## Deux erreurs fréquentes

1. Coder la variante avant d'avoir mesuré son impact : on oublie l'export, le DAX
   ou l'app, et le rapport contredit l'entrepôt.
2. Modifier la valeur de référence pour qu'elle colle au nouveau calcul : la
   référence décrit la mission de base ; la variante se prouve par **son** test.
