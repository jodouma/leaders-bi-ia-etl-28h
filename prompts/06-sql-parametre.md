# 06 — Interroger la base opérationnelle en SQL paramétré

**Quand l'utiliser** : séance 3, pour lire les retours (ou remboursements, avoirs…)
dans la base SQLite opérationnelle de la mission.

**Avant d'envoyer** : choisissez un mois (ex. `2026-03`). Combien de retours
pensez-vous y trouver : aucun, une dizaine, une centaine ? Notez-le.

## Le prompt

```text
Dans solen/, ajoute une fonction qui lit les <retours> de la base SQLite
<chemin de la base dans lot1> avec le module sqlite3, en lecture seule.
La requête SQL doit être paramétrée avec ? (jamais de f-string ni de concaténation)
et accepter une date de début et une date de fin.
Lance-la pour le mois <AAAA-MM> et affiche : nombre de lignes, somme des montants en millimes.
Montre la requête SQL et explique chaque clause (SELECT, FROM, WHERE, ORDER BY).
Explique en 3 lignes pourquoi un paramètre ? protège mieux qu'une chaîne construite.
Puis dis si une même requête avec « fin » exclue ou incluse change le résultat sur ce mois.
```

## Vérifier dans la réponse

- La requête contient des `?` et la fonction passe un tuple de paramètres.
- La base est ouverte en lecture seule (rien n'est écrit dans la source).
- Comparez le compte à votre estimation et refaites la requête pour un autre mois.

## Deux erreurs fréquentes

1. Comparer des dates texte de formats différents (`04/03/2026` contre `2026-03-04`) :
   la comparaison SQL devient fausse. Vérifiez le format stocké.
2. Oublier si la borne de fin est incluse ou exclue : un retour du dernier jour
   disparaît ou compte deux fois d'un mois à l'autre.
