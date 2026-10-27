# Construire le rapport Atlas dans Power BI Desktop

Objectif : répondre à « quel chiffre d'affaires attribuer à chaque zone commerciale au moment de la vente ? ». On garde les quatre tables de l'entrepôt : les dimensions décrivent, la table de faits mesure. `shop_key` identifie une **version** de boutique ; `shop_id` identifie la boutique dans le métier.

Power BI Desktop est une application Windows gratuite pour créer et enregistrer un rapport local. Ce TP ne demande ni publication en ligne, ni licence Pro, ni essai Fabric. Sous Ubuntu, préparez les données puis utilisez un vrai poste Windows (ou le poste Windows d'un binôme). WSL exécute Python ; Desktop reste dans Windows.

## 1. Préparer un dossier Windows stable

Le parcours principal utilise l'export **final**, après l'incrément : 14 ventes, 35 unités, 115 500 millimes. Après l'export Python de la séance 4, trouvez le dossier `outputs/powerbi/<delivery_id>/` indiqué par la commande et notez son chemin exact pour pouvoir le retrouver. Il doit contenir `dim_product.csv`, `dim_shop.csv`, `dim_date.csv`, `fact_sales.csv` et `manifest.json`. Prenez les quatre CSV d'une **même livraison complète**. Dans `manifest.json`, contrôlez `files["fact_sales.csv"].rows = 14`, `sums.quantity = 35` et `sums.amount_millimes = 115500`.

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

Pour quitter la vue Modèle, cliquez sur l'icône **Rapport** dans la barre de gauche (petit graphique). Vous arrivez sur le canevas de la page. Cliquez dans une zone vide du canevas pour créer un nouveau visuel.

Dans le volet **Visualisations**, onglet **Générer un visuel / Build visual**, choisissez **Carte**. Une carte vide apparaît. Dans le volet **Données**, développez `fact_sales`, puis faites glisser la **mesure** `CA TND` vers le champ **Valeurs** de la carte. Avec la carte sélectionnée, ouvrez **Mettre en forme le visuel** ; sous **Visuel → Valeurs de légende / Callout values → Valeurs**, réglez les **unités d'affichage sur Aucune** et les **décimales sur 3**. Les libellés peuvent varier selon la version ou la langue. Donnez-lui le titre « CA · TND ». Après ce réglage et sans filtre, vérifiez 115,500 TND.

Cliquez à nouveau dans une zone vide, choisissez une nouvelle **Carte**, puis déposez `Quantité vendue` dans **Valeurs** ; recommencez pour `Nombre de ventes`. Vous devez obtenir trois cartes distinctes : 115,500 TND, 35 unités, 14 ventes.

Cliquez dans une zone vide avant chaque nouveau visuel. Ajoutez un **graphique à barres groupées** : `dim_shop[commercial_zone]` dans l'axe des catégories, `[CA TND]` dans les valeurs. Ajoutez ensuite un **Tableau** et déposez `shop_name`, `commercial_zone`, `valid_from` et `[CA TND]` dans ses colonnes. Les champs descriptifs viennent des dimensions. Si vous changez seulement le type du visuel déjà sélectionné, utilisez **Ctrl+Z**, puis cliquez sur le canevas vide avant de recommencer.

## 5. Prouver le résultat et l'actualisation

Le dossier final importé en début de TP donne les contrôles suivants, sans filtre :

| Contrôle | Export final |
|---|---:|
| Nombre de ventes | 14 |
| Quantité vendue | 35 |
| CA en TND | 115,500 |

Après l'incrément, le CA historique doit être **Cap Bon : 43,500 TND** et **Grand Tunis : 72,000 TND**. Dans le tableau, Nabeul garde 43,500 TND sur sa version du 5 janvier et porte 4,500 TND sur sa version du 8 janvier ; Tunis porte 67,500 TND. Selon la langue, Desktop peut afficher un point décimal. La valeur est identique.

Cliquez sur Cap Bon : le CA filtré devient 43,500. Cliquez à nouveau pour retirer la sélection et retrouvez 115,500. Expliquez à votre binôme pourquoi le changement de zone n'a pas déplacé les anciennes ventes de Nabeul.

Cliquez **Accueil → Actualiser** dans Desktop. Si les CSV n'ont pas changé, les valeurs restent **14 ventes, 35 unités et 115,500 TND** : c'est le résultat attendu. Ce contrôle vérifie la relecture de la source finale ; il ne démontre pas une variation de données. Modifier SQLite sans refaire l'export et la copie laisse Desktop lire les anciens CSV. Le bonus suivant permet d'observer une variation contrôlée.

Enregistrez votre rapport sous `Atlas_mon_nom.pbix`, fermez-le puis rouvrez-le. Conservez deux captures authentiques : le modèle avec ses trois relations lisibles, et le rapport final sans filtre. À ce stade, je sais importer quatre tables, choisir leurs types, construire une étoile, créer une mesure et expliquer un résultat filtré.

## Bonus facultatif : observer le passage de 12 à 14 ventes

Le parcours principal est terminé. Ce bonus utilise une copie de référence séparée et une copie du rapport. Gardez le chemin du **dossier de livraison final** noté à l'étape 1 : il permettra de restaurer les quatre CSV finaux. Votre dossier de travail étudiant reste disponible.

1. Dans Desktop, utilisez **Fichier → Enregistrer sous** pour créer `Atlas_test_actualisation.pbix`. Faites le test dans cette copie du rapport.
2. Dans Ubuntu, ouvrez un terminal à la **racine du cours** (le dossier contenant `outils/`, `projet/` et `solutions/`). Créez un dossier neuf puis chargez et exportez seulement l'état initial :

   ```bash
   python3 outils/jalon.py 07 atelier-initial
   cd atelier-initial
   python3 executer.py initial
   python3 executer.py export
   ```

   Si `atelier-initial` existe déjà, la commande refuse de l'écraser : choisissez un autre nom neuf et adaptez le `cd`. **Ne lancez pas `increment` dans cette copie.** La commande `export` affiche le chemin exact de sa livraison ; utilisez ce chemin, sans inventer l'identifiant du dossier. Dans son `manifest.json`, vérifiez **12** lignes pour `fact_sales.csv`, quantité **32**, montant **99000** millimes.
3. Depuis le dossier de cette livraison initiale, tapez `explorer.exe .` sous WSL, ou transférez le paquet vers Windows sous Ubuntu natif. Copiez ses **quatre CSV ensemble** et son manifeste dans le **même dossier Windows de source** qu'à l'étape 1, en remplaçant uniquement ces fichiers. Les chemins source des requêtes restent identiques.
4. Dans `Atlas_test_actualisation.pbix`, cliquez **Accueil → Actualiser** et attendez la fin. Sans filtre, observez **12 ventes, 32 unités et 99,000 TND**. Le changement est attendu parce que le contenu des CSV a changé.
5. Retrouvez le **dossier final d'origine**, dans votre atelier étudiant, grâce au chemin noté à l'étape 1. Copiez de nouveau ses **quatre CSV ensemble** et son manifeste dans ce même dossier Windows. Cliquez **Actualiser** dans le rapport de test : les cartes doivent revenir à **14 ventes, 35 unités et 115,500 TND**. Vérifiez aussi les zones : Cap Bon 43,500 TND et Grand Tunis 72,000 TND.

Conservez, si vous le souhaitez, les captures avant/après de ce rapport de test, puis rouvrez votre rapport principal. Cette procédure constitue un exercice à réaliser sous Windows ; la réussite du chargement Python ne prouve pas à elle seule l'actualisation dans Desktop.

## Si je suis bloqué

- **Une seule colonne à l'import** : choisir explicitement la virgule, puis vérifier l'UTF-8.
- **CA multiplié ou relation plusieurs-à-plusieurs** : vérifier les trois clés substituts et l'unicité côté dimension. Ne pas agréger pour cacher le problème.
- **CA 115 500** : le visuel utilise peut-être `amount_millimes` directement. Remplacer ce champ par la mesure `[CA TND]`.
- **99,000 après actualisation** : vérifier le chemin source de chaque requête et la copie de la nouvelle livraison complète.
- **Carte vide ou erreur de source** : vérifier les quatre fichiers, leurs noms et le chemin Windows. Avec le projet de secours ci-dessous, lancer la première actualisation.

## Projet de secours facultatif

Le parcours ci-dessus commence depuis un rapport vide. Si vous avez besoin d'une base éditable, copiez **tout** ce dossier `powerbi` sous Windows puis ouvrez `AtlasPapeterie.pbip` avec Desktop. Les sous-dossiers `.Report` et `.SemanticModel` doivent rester à côté du fichier. Dans **Transformer les données → Gérer les paramètres**, donnez à `CSVFolder` le chemin Windows du dossier des quatre CSV, **sans barre oblique finale**, puis **Fermer et appliquer** et **Actualiser**. Le chemin initial proposé est `C:\AtlasPapeterie\export`.

Ce projet contient les requêtes, le modèle, les mesures et une page modifiable. Les données ne sont pas incluses dans un cache : **la première actualisation charge réellement les CSV**. Si Desktop demande de confirmer un accès local aux fichiers, contrôlez le chemin. Aucun compte en ligne n'est nécessaire pour ce rapport local. Reprenez ensuite les étapes 3 à 5 et expliquez ce que chaque relation et mesure fait.

Sources techniques : [Desktop](https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop), [CSV](https://learn.microsoft.com/power-query/connectors/text-csv), [étoile et historique](https://learn.microsoft.com/power-bi/guidance/star-schema), [projets PBIP](https://learn.microsoft.com/power-bi/developer/projects/projects-overview), [vue Rapport](https://learn.microsoft.com/power-bi/create-reports/desktop-report-view), [créer une carte](https://learn.microsoft.com/power-bi/visuals/power-bi-visualization-card). La validation des fichiers sources du kit est distincte d'une exécution réelle dans Desktop Windows ; elle ne mesure pas le temps de réalisation d'un débutant.
