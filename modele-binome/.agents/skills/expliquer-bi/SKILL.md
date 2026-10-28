---
name: expliquer-bi
description: Expliquer en français simple, à un débutant, une notion BI/ETL/Git ou un morceau de code généré dans ce dépôt Solen, avec un petit exemple chiffré de la mission, sans rien modifier.
---

Tu expliques ; tu ne modifies aucun fichier et tu ne lances aucune commande qui
écrit (pas de chargement, pas d'export, pas de commit).

1. Lis `mission.txt`, puis seulement les fichiers utiles à la question (le code
   cité, le cahier des charges, une ou deux lignes de source).
2. Commence par un exemple Solen de deux ou trois lignes (un ticket, un retour,
   une boutique) et fais le calcul à la main avant de parler du code. Donne
   toujours l'unité : quantité, millimes ou TND (1 TND = 1 000 millimes).
3. Explique chaque mot nouveau au moment où il apparaît (grain, fait, dimension,
   clé technique, rejet, SCD2, rejeu, diff, branche…). Une notion à la fois :
   celle qui sert à la prochaine étape.
4. Pour un code généré : dis en une phrase ce que fait le fichier, puis montre
   les 3 à 5 lignes importantes avec leur numéro et ce qu'elles font. Signale ce
   qu'un débutant doit savoir montrer à l'oral (où la ligne est rejetée, où les
   millimes sont calculés, où la version de boutique est choisie).
5. Pour l'historique : montre une vente avant et une vente après le changement
   de zone, avec la version retenue pour chacune (`valid_from` inclus,
   `valid_to` exclu).

Termine par **une** question où l'étudiant prévoit une valeur, compare deux cas
ou reformule. Attends sa réponse avant de donner la solution. Si un fichier ou
un résultat manque, dis-le au lieu d'inventer une valeur.
