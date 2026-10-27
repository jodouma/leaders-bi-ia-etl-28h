# Construire le rapport Atlas dans Power BI Desktop

Objectif : répondre à « quel chiffre d'affaires attribuer à chaque zone commerciale au moment de la vente ? ». On garde les quatre tables de l'entrepôt : les dimensions décrivent, la table de faits mesure. `shop_key` identifie une **version** de boutique ; `shop_id` identifie la boutique dans le métier.

Power BI Desktop est une application Windows gratuite pour créer et enregistrer un rapport local. Ce TP ne demande ni publication en ligne, ni licence Pro, ni essai Fabric. Sous Ubuntu, préparez les données puis utilisez un vrai poste Windows (ou le poste Windows d'un binôme). WSL exécute Python ; Desktop reste dans Windows.

## 1. Préparer un dossier Windows stable

Après l'export Python de la séance 4, trouvez le dossier `outputs/powerbi/<delivery_id>/` indiqué par la commande. Il doit contenir `dim_product.csv`, `dim_shop.csv`, `dim_date.csv`, `fact_sales.csv` et `manifest.json`. Prenez les quatre CSV d'une **même livraison complète**.

Dans le terminal Ubuntu WSL, placez-vous dans ce dossier puis tapez :

```bash
explorer.exe .
```

L'Explorateur Windows s'ouvre. Copiez les cinq fichiers dans `Documents\AtlasPapeterie\export`. Sous Ubuntu natif, transférez ce même paquet vers le poste Windows. Notez le chemin Windows réel : il peut inclure OneDrive ou le nom de l'utilisateur. Conservez ce dossier pour les actualisations suivantes.

## 2. Importer les quatre tables depuis un rapport vide

Ouvrez Power BI Desktop, puis **Rapport vide**. Pour chaque fichier : **Accueil → Obtenir des données → Texte/CSV**, choisir le CSV dans le dossier Windows. Dans l'aperçu, choisir **65001 : Unicode (UTF-8)** et séparateur **Virgule**, puis **Transformer les données**. Les noms de tables doivent être exactement les noms de fichiers sans `.csv`. Après la première importation, restez dans Power Query et utilisez **Accueil → Nouvelle source → Texte/CSV** pour les trois autres fichiers.

Dans l'éditeur Power Query, vérifiez la première ligne d'en-têtes. Pour chaque colonne, cliquez l'icône du type à gauche du nom et fixez les types suivants ; supprimez ou corrigez une éventuelle étape automatique « Type modifié » erronée.

| Table | Nombre entier | Date | Texte |
|---|---|---|---|
| `dim_product` | `product_key` | — | `product_id`, `product_name` |
| `dim_shop` | `shop_key` | `valid_from`, `valid_to` | `shop_id`, `shop_name`, `commercial_zone` |
| `dim_date` | `date_key`, `year`, `month`, `day` | `full_date` | — |
| `fact_sales` | `date_key`, `product_key`, `shop_key`, `quantity`, `unit_price_millimes`, `amount_millimes` | — | `sale_id` |

Si une date ISO comme `2026-01-08` produit une erreur, utilisez **Modifier le type → Utiliser les paramètres régionaux → Date → Anglais (États-Unis)**. Dans `valid_to`, un champ vide représente une borne ouverte : il doit devenir `null`, jamais la date du jour. Les champs CSV vides deviennent normalement `null` ; si une erreur persiste, contrôlez que le CSV contient une case vide et non le texte `NULL` ou une date inventée. Vérifiez l'absence d'erreurs, puis **Fermer et appliquer**. Le manifeste sert à contrôler la livraison ; il ne devient pas une cinquième table.

## 3. Relier les tables par les clés substituts

Ouvrez la vue **Modèle**, puis **Gérer les relations**. Supprimez toute relation automatique qui ne correspond pas à la liste ci-dessous. Créez les trois relations ; dans chaque fenêtre, vérifiez **Un à plusieurs (1:*)**, filtre croisé **Simple**, relation **active**.

| Côté « 1 » : clé unique | Côté « * » : plusieurs ventes |
|---|---|
| `dim_product[product_key]` | `fact_sales[product_key]` |
| `dim_shop[shop_key]` | `fact_sales[shop_key]` |
| `dim_date[date_key]` | `fact_sales[date_key]` |

Le filtre part de la dimension vers les faits. Il n'y a aucune relation entre dimensions. Ne reliez pas les boutiques par `shop_id` : NBE apparaît deux fois après son changement de zone, alors que chaque `shop_key` est unique. Les dates de validité ne sont pas des relations Power BI ; Python a déjà choisi la bonne version à la date de chaque vente.

## 4. Créer trois mesures, puis les visuels

Sélectionnez `fact_sales`, **Modélisation → Nouvelle mesure**. Entrez une formule à la fois (également disponible dans `mesures.dax`) :

```dax
CA TND = DIVIDE(SUM(fact_sales[amount_millimes]), 1000)
```

```dax
Quantité vendue = SUM(fact_sales[quantity])
```

```dax
Nombre de ventes = COUNTROWS(fact_sales)
```

Une mesure se recalcule quand on filtre le rapport. On additionne les millimes entiers puis on divise par 1 000 : `115500 / 1000 = 115,500 TND`. Si Desktop utilise les séparateurs DAX locaux, la virgule entre les arguments de `DIVIDE` devient un point-virgule.

Dans la vue **Rapport**, ajoutez trois **Cartes**, une mesure par carte. Pour le CA, choisissez trois décimales et des **unités d'affichage : Aucune**. Mettez « CA · TND » dans le titre. Ajoutez un **graphique à barres groupées** : axe des catégories = `dim_shop[commercial_zone]`, valeur = `[CA TND]`. Ajoutez un **Tableau** : `shop_name`, `commercial_zone`, `valid_from` et `[CA TND]`. Les champs descriptifs viennent des dimensions.

## 5. Prouver le résultat et l'actualisation

| Contrôle sans filtre | Export initial | Export après incrément |
|---|---:|---:|
| Nombre de ventes | 12 | 14 |
| Quantité vendue | 32 | 35 |
| CA en TND | 99,000 | 115,500 |

Après l'incrément, le CA historique doit être **Cap Bon : 43,500 TND** et **Grand Tunis : 72,000 TND**. Dans le tableau, Nabeul garde 43,500 TND sur sa version du 5 janvier et porte 4,500 TND sur sa version du 8 janvier ; Tunis porte 67,500 TND. Selon la langue, Desktop peut afficher un point décimal. La valeur est identique.

Cliquez sur Cap Bon : le CA filtré devient 43,500. Cliquez à nouveau pour retirer la sélection et retrouvez 115,500. Expliquez à votre binôme pourquoi le changement de zone n'a pas déplacé les anciennes ventes de Nabeul.

Pour prouver l'actualisation, commencez avec l'export initial. Exécutez ensuite l'incrément et un nouvel export Python, copiez les **quatre** nouveaux CSV ensemble dans le même dossier Windows (en remplaçant les anciens), puis cliquez **Accueil → Actualiser** dans Desktop. Vérifiez le passage 12→14, 32→35, 99,000→115,500. Modifier SQLite sans refaire export et copie laisse Desktop lire les anciens CSV.

Enregistrez votre rapport sous `Atlas_mon_nom.pbix`, fermez-le puis rouvrez-le. Conservez deux captures authentiques : le modèle avec ses trois relations lisibles, et le rapport final sans filtre. À ce stade, je sais importer quatre tables, choisir leurs types, construire une étoile, créer une mesure et expliquer un résultat filtré.

## Si je suis bloqué

- **Une seule colonne à l'import** : choisir explicitement la virgule, puis vérifier l'UTF-8.
- **CA multiplié ou relation plusieurs-à-plusieurs** : vérifier les trois clés substituts et l'unicité côté dimension. Ne pas agréger pour cacher le problème.
- **CA 115 500** : le visuel utilise peut-être `amount_millimes` directement. Remplacer ce champ par la mesure `[CA TND]`.
- **99,000 après actualisation** : vérifier le chemin source de chaque requête et la copie de la nouvelle livraison complète.
- **Carte vide ou erreur de source** : vérifier les quatre fichiers, leurs noms et le chemin Windows. Avec le projet de secours ci-dessous, lancer la première actualisation.

## Projet de secours facultatif

Le parcours ci-dessus commence depuis un rapport vide. Si vous avez besoin d'une base éditable, copiez **tout** ce dossier `powerbi` sous Windows puis ouvrez `AtlasPapeterie.pbip` avec Desktop. Les sous-dossiers `.Report` et `.SemanticModel` doivent rester à côté du fichier. Dans **Transformer les données → Gérer les paramètres**, donnez à `CSVFolder` le chemin Windows du dossier des quatre CSV, **sans barre oblique finale**, puis **Fermer et appliquer** et **Actualiser**. Le chemin initial proposé est `C:\AtlasPapeterie\export`.

Ce projet contient les requêtes, le modèle, les mesures et une page modifiable. Les données ne sont pas incluses dans un cache : **la première actualisation charge réellement les CSV**. Si Desktop demande de confirmer un accès local aux fichiers, contrôlez le chemin. Aucun compte en ligne n'est nécessaire pour ce rapport local. Reprenez ensuite les étapes 3 à 5 et expliquez ce que chaque relation et mesure fait.

Sources techniques : [Desktop](https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop), [CSV](https://learn.microsoft.com/power-query/connectors/text-csv), [étoile et historique](https://learn.microsoft.com/power-bi/guidance/star-schema), [projets PBIP](https://learn.microsoft.com/power-bi/developer/projects/projects-overview). La validation des fichiers sources du kit est distincte d'une exécution réelle dans Desktop Windows ; elle ne mesure pas le temps de réalisation d'un débutant.
