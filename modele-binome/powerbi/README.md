# Power BI Desktop — rapport Solen Commerce 360

Question de la direction : **« les ventes montent, mais où passe la marge ? »**
Vous allez montrer les ventes nettes et la marge par zone commerciale et par mois,
avec la zone **valable au moment de la vente**.

Power BI Desktop est une application **Windows** gratuite. Pour construire et
enregistrer un rapport local, aucune connexion à un compte, aucune licence Pro et
aucun essai Fabric ne sont nécessaires (si une fenêtre de connexion s'ouvre, fermez-la).
Rien n'est publié en ligne. Python et le pipeline tournent dans Ubuntu ; Desktop
lit seulement les CSV exportés.

Prérequis : `python -m controles.verifier --mission $(cat mission.txt) --etape export`
réussit sur votre poste.

## 1. Produire un export de départ (lot 1 seul)

Pour voir plus tard l'actualisation changer les chiffres, on commence par l'état
**après le lot 1**. Dans le terminal Ubuntu, à la racine du dépôt, venv activé :

```bash
python -m solen initial
python -m solen export
ls outputs/export
```

Vous devez voir `dim_date.csv`, `dim_produit.csv`, `dim_boutique.csv`,
`fact_vente.csv`, `fact_retour.csv` et `manifest.json`. Ouvrez `manifest.json` et
notez le nombre de lignes de `fact_vente` et la somme de `montant_brut_millimes`.
**Prévoyez** : combien de TND la carte « Ventes brutes » devra-t-elle afficher ?

## 2. Copier l'export vers Windows

**Windows + WSL2** : dans le terminal Ubuntu, tapez

```bash
cd outputs/export
explorer.exe .
cd ../..
```

L'Explorateur Windows s'ouvre sur le dossier. Copiez les six fichiers dans un
dossier Windows stable, par exemple `Documents\Solen\export`. Notez le chemin
exact (il peut contenir OneDrive ou votre nom d'utilisateur). Gardez **ce même
dossier** pour toutes les actualisations.

**Ubuntu natif** (Desktop n'y fonctionne pas) : utilisez un poste Windows, par
exemple celui de votre binôme. Deux routes :

- copier les six fichiers sur une clé USB ou un dossier partagé, vers
  `Documents\Solen\export` du poste Windows ;
- ou, mieux, sur le poste Windows (avec WSL2) : `git pull` dans le dépôt, puis
  relancer vous-même `python -m solen initial` et `python -m solen export`, puis
  `explorer.exe .` comme ci-dessus. Les `outputs/` ne sont pas versionnés : on les
  reconstruit, on ne les transporte pas par Git.

## 3. Importer les cinq tables

Ouvrez Power BI Desktop, puis **Rapport vide**. Pour le premier fichier :
**Accueil → Obtenir des données → Texte/CSV**, choisissez `dim_date.csv`. Dans
l'aperçu, **Origine du fichier : 65001 : Unicode (UTF-8)**, délimiteur **Virgule**,
puis **Transformer les données**. Dans Power Query, ajoutez les quatre autres avec
**Accueil → Nouvelle source → Texte/CSV**. Chaque requête doit porter exactement le
nom du fichier sans `.csv`. `manifest.json` n'est pas importé : il sert au contrôle.

Pour chaque colonne, cliquez l'icône de type à gauche de son nom et fixez :

| Table | Nombre entier | Date | Texte |
|---|---|---|---|
| `dim_date` | `date_key`, `annee`, `mois`, `jour` | `date_complete` | — |
| `dim_produit` | `produit_key`, `prix_millimes`, `cout_achat_millimes` | — | `produit_id`, `nom`, `famille` |
| `dim_boutique` | `boutique_key` | `valid_from`, `valid_to` | `boutique_id`, `nom`, `zone` |
| `fact_vente` | `date_key`, `produit_key`, `boutique_key`, `quantite`, `prix_unitaire_millimes`, `montant_brut_millimes` | — | `ligne_id` |
| `fact_retour` | `date_key`, `produit_key`, `boutique_key`, `quantite`, `montant_millimes` | — | `retour_id` |

Les montants restent en **nombre entier** de millimes : ne les passez pas en
décimal. Si une date ISO (`2026-07-15`) donne une erreur : **Modifier le type →
Utiliser les paramètres régionaux → Date → Anglais (États-Unis)**. Dans
`valid_to`, une case vide signifie « version courante » et doit rester `null`,
jamais la date du jour. Vérifiez qu'aucune colonne n'affiche d'erreur, puis
**Fermer et appliquer**.

## 4. Relier les tables (vue Modèle)

Ouvrez la vue **Modèle**, puis **Gérer les relations**. Supprimez les relations
détectées automatiquement qui ne sont pas dans la liste. Il faut **six relations**
(trois dimensions × deux tables de faits). Pour chacune : **Un à plusieurs (1:\*)**,
filtre croisé **Simple**, relation **active**.

| Côté « 1 » (clé unique) | Côté « \* » |
|---|---|
| `dim_date[date_key]` | `fact_vente[date_key]` |
| `dim_date[date_key]` | `fact_retour[date_key]` |
| `dim_produit[produit_key]` | `fact_vente[produit_key]` |
| `dim_produit[produit_key]` | `fact_retour[produit_key]` |
| `dim_boutique[boutique_key]` | `fact_vente[boutique_key]` |
| `dim_boutique[boutique_key]` | `fact_retour[boutique_key]` |

Power BI n'accepte qu'un seul chemin actif entre deux tables. Ici, chaque
dimension filtre directement chaque fait, et les deux faits ne sont pas reliés
entre eux : il n'y a qu'un chemin, toutes les relations peuvent être actives.
Ne reliez **jamais** par `boutique_id` : la boutique qui change de zone a deux
lignes (deux versions), alors que chaque `boutique_key` est unique. Python a déjà
choisi la bonne version pour chaque vente et chaque retour.

## 5. Créer les cinq mesures

Sélectionnez `fact_vente`, puis **Modélisation → Nouvelle mesure**. Collez **une**
formule à la fois depuis `powerbi/mesures.dax`, validez, recommencez :

1. `Ventes brutes TND`
2. `Retours TND`
3. `Ventes nettes TND` = brutes − retours
4. `Marge sur coût d'achat TND` = ventes nettes − coût d'achat des unités nettes
   (quantité vendue − quantité retournée) × `cout_achat_millimes`
5. `Taux de retour` = retours / ventes brutes (format Pourcentage)

On additionne des millimes entiers, puis on divise par 1 000. Si Desktop refuse la
virgule entre les arguments de `DIVIDE`, utilisez un point-virgule. Avec une
mesure sélectionnée, vous pouvez régler son format (3 décimales pour les TND,
Pourcentage pour le taux) ; l'emplacement exact du réglage varie selon la version.

**Expliquez à votre binôme**, avant de continuer : pourquoi la marge utilise le
coût d'achat des unités **nettes** et pas des unités vendues ?

## 6. Construire la page

Cliquez l'icône **Rapport** dans la barre de gauche, puis dans une zone vide du
canevas avant chaque nouveau visuel.

1. **Cartes** : quatre cartes, avec `Ventes brutes TND`, `Ventes nettes TND`,
   `Marge sur coût d'achat TND` et `Taux de retour` dans **Valeurs**.
   Comparez « Ventes brutes » à votre prévision de l'étape 1.
2. **Graphique à barres groupées** : `dim_boutique[zone]` en axe, `Ventes nettes TND`
   en valeurs. Titre : « Ventes nettes par zone (TND) ».
3. **Graphique en courbes** : `dim_date[mois]` en axe X, `Ventes nettes TND` et
   `Marge sur coût d'achat TND` en valeurs. Titre : « Ventes nettes et marge par mois ».
4. **Segment** : `dim_boutique[nom]`. Cliquez une boutique : tous les visuels se
   filtrent. Recliquez pour retirer le filtre.

Si un visuel affiche un très grand nombre (×1 000), il utilise sans doute la
colonne `montant_brut_millimes` au lieu de la mesure : remplacez-la par la mesure.

Enregistrez sous `Documents\Solen\Solen_<nomA>_<nomB>.pbix`. Notez les valeurs des
quatre cartes sans filtre. Pour versionner le rapport, copiez ce `.pbix` dans le
dossier `powerbi/` du dépôt (par l'Explorateur ouvert avec `explorer.exe .`) s'il
fait moins de 10 Mo, puis commitez-le dans une PR comme le reste.

## 7. Actualiser après l'incrément

**Prévoyez** d'abord : après le lot 2, les ventes brutes montent-elles ou
baissent-elles ? Dans le graphique par zone, les ventes **anciennes** de la
boutique qui change de zone au 2026-07-15 changent-elles de barre ?

Dans Ubuntu, à la racine du dépôt :

```bash
python -m solen increment
python -m solen export
python -m controles.verifier --mission $(cat mission.txt) --etape export
```

Recopiez les six fichiers dans **le même** dossier Windows, en remplaçant les
anciens (même route qu'à l'étape 2). Dans Desktop : **Accueil → Actualiser**.

- Les cartes changent et correspondent au nouveau `manifest.json` (somme ÷ 1 000).
- Les mois de juillet et août apparaissent dans la courbe.
- Les ventes de la boutique avant le 2026-07-15 restent dans son ancienne zone ;
  celles d'après vont dans la nouvelle.

Cliquez **Actualiser** une deuxième fois sans rien changer : les valeurs restent
identiques.

**Ce que « Actualiser » prouve** : le rapport relit les fichiers CSV du dossier à
chaque actualisation ; il est branché sur les données, pas sur des chiffres
recopiés. Ce que cela **ne** prouve **pas** : que les CSV sont justes (c'est le rôle
du vérificateur), ni que l'entrepôt a changé si vous n'avez pas relancé `export`
et recopié les fichiers — Desktop relirait alors les anciens CSV.

Gardez deux captures réelles, légendées : la vue Modèle avec ses six relations
lisibles, et la page du rapport après actualisation, sans filtre.

## Si je suis bloqué

- **Une seule colonne à l'import** : choisir la virgule comme délimiteur, vérifier UTF-8.
- **Accents illisibles** (`Ã©`) : l'origine n'est pas 65001 : Unicode (UTF-8).
- **Relation plusieurs-à-plusieurs proposée** : la dimension a une clé en double ;
  vérifier qu'on relie par `*_key` et non par `*_id`. Ne masquez pas le problème.
- **Les chiffres n'ont pas bougé après actualisation** : vérifier que `export` a
  été relancé, que les nouveaux fichiers sont dans **le même** dossier, et le chemin
  de chaque requête (dans **Transformer les données**, première étape **Source**).
- **Erreur dans `valid_to`** : la case doit être vide, pas le texte `NULL` ;
  demandez à Codex de corriger l'export, pas de contourner dans Power BI.

## À ce stade, je sais…

- importer cinq tables CSV en UTF-8 et fixer leurs types ;
- construire une étoile à deux tables de faits avec six relations 1:\* ;
- créer cinq mesures DAX et dire l'unité de chacune ;
- expliquer pourquoi une ancienne vente reste dans l'ancienne zone ;
- actualiser un rapport et dire ce que cette actualisation prouve — et ce qu'elle ne prouve pas.

Sources techniques : [Desktop](https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop),
[CSV](https://learn.microsoft.com/power-query/connectors/text-csv),
[schéma en étoile](https://learn.microsoft.com/power-bi/guidance/star-schema),
[relations](https://learn.microsoft.com/power-bi/transform-model/desktop-create-and-manage-relationships).
Ce guide reprend les libellés vérifiés de l'édition précédente ; les autres
(Segment, Graphique en courbes, format de mesure) restent à confirmer dans un essai
réel sous Windows.
