# Données fictives d'Atlas Papeterie

Aucun client ni aucune boutique réelle. Ces données ont été créées pour le cours ; elles ne décrivent pas l'activité de Leaders University.

Fichiers CSV en **UTF-8**, séparateur **virgule**, point pour les décimales. Utiliser **Thonny → Fichier → Ouvrir** pour lire un CSV comme du texte. Excel peut changer les dates, les séparateurs et les décimales : garder les originaux intacts.

| Colonne | Sens |
|---|---|
| `sale_id` | Identifiant unique d'une vente élémentaire ; ce n'est pas un client |
| `date` | Date au format `AAAA-MM-JJ` |
| `shop_id` | Boutique : NBE ou TUN, à comparer au catalogue `boutiques.csv` |
| `product_id` | Produit : P01 à P04, à comparer au catalogue `produits.csv` |
| `quantity` | Nombre entier strictement positif d'articles |
| `unit_price_tnd` | Prix par article en TND, jusqu'à trois décimales |

Une ligne valide = une vente d'un produit dans une boutique à une date. Montant = quantité × prix unitaire. **1 TND = 1000 millimes** ; le programme conserve les montants en millimes entiers dans SQLite.

- `ventes_initiales.csv` : 16 lignes sources, dont 12 ventes retenues, un doublon exact et trois rejets à expliquer. 32 articles, **99.000 TND** après contrôle.
- `ventes_ajout.csv` : deux nouvelles ventes et une vente déjà chargée. Après ajout : 14 ventes, 35 articles, **115.500 TND**.
- `ventes_defi.csv` : lot d'ajout plus S015 avec une quantité à réparer dans la copie créée par le script 10. Garder ce fichier source intact.
- `produits.csv`, `boutiques.csv` : catalogues des quatre produits et deux boutiques.

Le montant observé n'est pas une marge. Sans coût d'achat ni stock disponible, on ne peut calculer ni bénéfice ni quantité exacte à commander. Les dates sont des dates pédagogiques, pas le calendrier de cours.
