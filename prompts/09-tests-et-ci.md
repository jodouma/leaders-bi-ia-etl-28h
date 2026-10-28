# 09 — Tests automatiques et CI

**Quand l'utiliser** : séance 4, quand `initial`, `increment` et `export` existent.
Objectif : une CI verte sur GitHub à chaque PR.

**Avant d'envoyer** : choisissez une règle (ex. « une quantité de -2 est rejetée »).
Prévoyez : si Codex casse cette règle dans le code, quel test doit devenir rouge ?

## Le prompt

```text
Dans tests/ (pas dans controles/), écris 3 à 5 tests pytest courts pour nos règles :
<règle 1>, <règle 2>, le rejeu, et la version SCD2 à la date frontière <date>.
Chaque test a un nom en français qui dit la règle, et utilise un petit jeu de données
construit dans le test (pas les sources complètes).
Lance pytest controles puis pytest -q et recopie les sorties.
Puis, sans le garder, montre-moi quel test échouerait si on supprimait la règle <règle 1>,
et pourquoi.
Ensuite mets à jour .github/workflows/controles.yml : passe ETAPE_CI de <valeur actuelle> à <nouvelle valeur>,
et explique en 5 lignes ce que la CI va exécuter. Ne fais ni commit ni push.
```

## Vérifier dans la réponse

- `pytest controles` et `pytest -q` passent en local avant de pousser.
- `ETAPE_CI` suit l'ordre `aucune` → `rejets` → `initial` → `increment` → `rejeu` →
  `export` → `tout`.
- Le diff de `controles.yml` ne change que ce que vous avez demandé ; aucun secret,
  aucune clé d'IA, aucun service externe n'y apparaît.
- Après le push, onglet **Actions** de la PR : la CI s'exécute ; ouvrez une étape
  et lisez sa sortie.

## Deux erreurs fréquentes

1. Écrire des tests qui recopient le résultat du code (`assert total == total`) :
   ils ne peuvent jamais échouer. Un bon test part d'un exemple calculé à la main.
2. Passer `ETAPE_CI` à `tout` alors que l'export n'existe pas encore : la CI est
   rouge pour une raison attendue, et l'équipe s'habitue à ignorer le rouge.
