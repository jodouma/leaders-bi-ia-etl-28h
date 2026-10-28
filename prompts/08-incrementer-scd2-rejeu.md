# 08 — Incrément, historique SCD2 et rejeu

**Quand l'utiliser** : séance 4, épisode « changement de besoin » : le lot 2 arrive,
une boutique change de zone commerciale au 2026-07-15.

**Avant d'envoyer** : prévoyez trois valeurs et notez-les :
(1) nombre de lignes de `dim_boutique` après le lot 2 ;
(2) la zone d'une vente de cette boutique datée du 2026-07-14, puis du 2026-07-15 ;
(3) le nombre de lignes de `fact_vente` après avoir lancé `increment` **deux fois**.

## Le prompt

```text
Ajoute la commande python -m solen increment qui charge <lot2> dans l'entrepôt existant.
Règles :
- SCD2 sur <dim_boutique> : quand la zone change, fermer l'ancienne version (valid_to = date du changement,
  exclue) et créer une nouvelle version (valid_from = même date, incluse, valid_to NULL) ;
- un fait est rattaché à la version valable à SA date ; ne jamais modifier les faits anciens ;
- rejeu : relancer le même lot n'ajoute aucune ligne (clé métier unique, insertion idempotente).
Lance : initial, increment, increment, puis les vérifications --etape increment et --etape rejeu,
et recopie les sorties. Montre la requête qui choisit la version de boutique pour une date.
Mes prévisions : <1>, <2>, <3>. Compare chacune avec le résultat réel.
```

## Vérifier dans la réponse

- La version choisie utilise `valid_from <= date AND (valid_to IS NULL OR date < valid_to)`.
- Les comptes avant et après le deuxième `increment` sont **identiques**.
- Une vente ancienne de la boutique reste dans l'ancienne zone (contrôle à la main
  avec `sqlite3`).

## Deux erreurs fréquentes

1. Mettre à jour la zone dans la ligne existante (`UPDATE … SET zone`) : tout
   l'historique bascule dans la nouvelle zone, le passé est réécrit.
2. Prendre `valid_to` inclus : la vente du jour du changement est rattachée à deux
   versions, ou à la mauvaise.
