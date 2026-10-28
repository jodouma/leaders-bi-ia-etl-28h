# 05 — Nettoyer et rejeter avec un motif

**Quand l'utiliser** : séance 2, après la lecture (prompt 04). Épisode « premier
résultat rassurant… faux ».

**Avant d'envoyer** : dans l'échantillon, repérez à la main chaque ligne qui doit
être gardée, normalisée ou rejetée, et son motif. Écrivez vos comptes
(acceptées / rejetées par motif).

## Le prompt

```text
Applique les règles de nettoyage du cahier des charges de <mission> aux faits de <lot1>,
dans solen/ seulement. Sources intactes.
- doublon exact : garder une occurrence ;
- même identifiant avec contenu différent : rejeter les deux, motif id_conflit ;
- identifiant vide : id_manquant ; produit ou boutique inconnus : cle_inconnue ;
- quantité ≤ 0 ou non entière : quantite_invalide ;
- montants en millimes entiers (12,500 / 12.5 / 12 500 → 12500), dates en YYYY-MM-DD,
  codes en strip + majuscules.
Écris outputs/rejets.csv avec la ligne d'origine et une colonne motif.
Teste d'abord sur l'échantillon : j'attends <mes comptes>. Puis sur lot1 : lance
python -m solen initial, puis
python -m controles.verifier --mission $(cat mission.txt) --etape rejets
Montre la fonction qui décide du motif et explique l'ordre des règles.
```

## Vérifier dans la réponse

- `--etape rejets` ne juge que le CSV de faits du lot 1 (en séance 2, les retours de la
  base SQLite viennent plus tard) ; chaque `numero_ligne` est une vraie ligne du CSV
  (en-tête = ligne 1), une seule fois.
- Vos comptes sur l'échantillon sont retrouvés exactement ; sinon, faites-vous
  expliquer **la** ligne qui diffère.
- `outputs/rejets.csv` a une colonne `motif` et ne contient que les motifs prévus.
- L'ordre des règles est justifié (un doublon exact n'est pas un `id_conflit`).

## Deux erreurs fréquentes

1. Supprimer les lignes fautives sans les écrire dans `rejets.csv` : la direction ne
   peut plus vérifier ce qui a été écarté.
2. Convertir `12,500` en `12.5` puis multiplier en flottant : `12.5 * 1000` peut
   donner `12499.999…`. Exigez un calcul en entiers.
