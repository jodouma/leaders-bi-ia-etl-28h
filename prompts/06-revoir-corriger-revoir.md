# Relire, corriger, puis relire à nouveau

Travaillez sur la version actuelle de votre copie. Une revue cherche un défaut avec une preuve ; elle ne modifie pas le programme. Un seul auteur applique ensuite les corrections.

## Deux angles de lecture

Commencez par les données, dans une conversation de lecture :

```text
Relis ma copie atelier en lecture seule. Ne lis pas les solutions.
Vérifie les règles des commentaires et les étapes déjà construites :
identifiants textuels non nuls, rejets, doublons, unités, quantités et montants.
Donne au plus trois défauts prouvés : fichier, règle, exemple et correction proposée.
Ne modifie aucun fichier et ne lance aucun chargement ni export.
Sépare les défauts établis des contrôles non réalisés. N'invente aucun constat.
```

Puis relisez le modèle et l'histoire, dans une deuxième conversation ou avec un camarade :

```text
Relis ma copie atelier en lecture seule. Ne lis pas les solutions.
Vérifie les étapes déjà construites : grain du fait, clés, dimensions avant faits,
relance sans double comptage et version de boutique à la date de la vente.
Vérifie notamment la frontière entre le 7 et le 8 janvier.
Donne au plus trois défauts prouvés avec fichier, règle, exemple et correction proposée.
Ne modifie rien et ne lance aucun chargement ni export. Dis ce qui reste non vérifié.
```

Pour une lecture indépendante, donnez les fichiers et règles utiles sans raconter la conclusion attendue. Deux passages dans la même conversation sont deux angles successifs ; ils ne deviennent pas deux agents indépendants.

## Option : deux vrais sous-agents

Si votre client le permet et si le quota suffit, vous pouvez remplacer les deux conversations par cette demande :

```text
Délègue deux revues distinctes de ma copie atelier, en parallèle et en lecture seule.
A vérifie les données, rejets, doublons, unités et totaux des étapes construites.
B vérifie les clés, l'historique des boutiques et le rejeu des étapes construites.
Ils ne lisent pas les solutions et ne modifient aucun fichier ni aucune base.
Chaque relecteur rapporte au plus trois défauts établis avec preuve et fichier.
Attends les deux résultats et réunis les constats sans encore corriger.
Si les sous-agents sont indisponibles, dis-le ; ne simule pas deux personnages.
```

Vérifiez que le client affiche deux activités distinctes. Deux titres dans une réponse ne suffisent pas. Cette fonction consomme elle aussi de l'usage et n'est pas garantie pour chaque compte Free. Attendez la fin des lecteurs avant de modifier les fichiers. [Sous-agents documentés](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Corriger avec un seul auteur

Retournez à la conversation de travail. Transmettez les constats utiles, puis :

```text
Vérifie les constats de revue que je viens de donner contre le code actuel.
Propose la petite correction nécessaire, puis corrige seulement les défauts établis.
Ne change ni données sources, ni contrôles, ni résultats attendus.
Depuis atelier/, exécute le contrôle du jalon concerné ; rapporte le résultat réel.
Explique les constats rejetés avec une raison observable.
```

Choisissez le bon contrôle depuis votre copie : `python3 verifier.py 02` pour la normalisation, `03` pour SQL, `05` pour la frontière temporelle, `06` pour incrément/rejeu, `07` pour les exports. Une réparation peut nécessiter plusieurs contrôles. `python3 verifier.py tout` vérifie l'ensemble du code quand les trois fonctions sont complétées ; il ne reconstruit pas vos sorties de travail.

## Deuxième revue

Faites relire la **version corrigée**, avec le même angle :

```text
Relis la version corrigée de ma copie en lecture seule.
Revérifie les défauts signalés et cherche une erreur causée par la correction.
Pour chaque point : corrigé avec preuve, encore présent, ou non vérifié.
Ne modifie rien. Ne donne pas de garantie générale de justesse.
```

Gardez un bilan court : défaut initial, correction, commande exécutée, conclusion de la deuxième revue. « Pas de défaut trouvé » signifie seulement que cette lecture n'en a pas établi. Attendez la fin des agents et arrêtez toute activité encore en cours avant de quitter.

En séance 5, appliquez cette méthode au défaut fourni dans [le défi Atlas](../defi/student_challenge.md). Remplacez alors `atelier/` par **`atelier-defi/`** dans les demandes ; les commandes Python se lancent depuis `atelier-defi/`. Gardez la racine du cours sélectionnée dans Codex. Suivez l'ordre de reconstruction et d'actualisation Power BI du défi ; un contrôle temporaire réussi ne répare pas un ancien entrepôt de travail.
