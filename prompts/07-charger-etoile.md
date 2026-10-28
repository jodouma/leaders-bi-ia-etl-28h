# 07 — Charger l'entrepôt en étoile (lot 1)

**Quand l'utiliser** : séance 3, quand lecture, nettoyage et SQL fonctionnent.

**Avant d'envoyer** : dessinez l'étoile sur papier (faits au centre, dimensions
autour, clés sur les flèches). Prévoyez le nombre de lignes de `dim_boutique` et
de `fact_vente` après le lot 1.

## Le prompt

```text
Lis le cahier des charges de <mission>. Dans solen/, crée une classe Entrepot qui
gère outputs/entrepot.sqlite, et la commande python -m solen initial.
initial recrée l'entrepôt depuis zéro avec <lot1> : d'abord les dimensions
(<dim_date, dim_produit, dim_boutique>), puis les faits (<fact_vente, fact_retour>),
avec des clés techniques *_key entières, des clés métier *_id texte, des montants en millimes entiers,
et une transaction pour que tout ou rien soit écrit.
La dimension SCD2 <dim_boutique> reçoit valid_from et valid_to (NULL = courante).
Lance python -m solen initial puis python -m controles.verifier --mission $(cat mission.txt) --etape initial
et recopie les sorties. J'attends <n> boutiques et <n> lignes de faits : compare.
Explique le grain de chaque table de faits en une phrase.
```

## Vérifier dans la réponse

- Ordre de chargement : dimensions avant faits ; aucune clé de fait sans dimension.
- `sqlite3 outputs/entrepot.sqlite "SELECT COUNT(*) FROM fact_vente;"` donne le même
  compte que la réponse et que la référence.
- Le vérificateur est réellement **OK** sur `initial` ; sinon, lisez la première
  ligne d'échec (prompt 10).

## Deux erreurs fréquentes

1. Relier les faits par `boutique_id` : dès qu'une boutique aura deux versions,
   les ventes seront comptées deux fois.
2. Lancer `initial` deux fois et voir les faits doubler : `initial` doit **recréer**
   l'entrepôt, pas ajouter.
