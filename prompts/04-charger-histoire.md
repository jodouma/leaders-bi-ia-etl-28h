# Séance 3 — Charger puis garder l'histoire

L'ossature du chargement et des transactions est fournie. Vous complétez seulement la recherche d'une version de boutique. Toutes les commandes ci-dessous se saisissent dans le terminal, depuis **`atelier/`**.

## Charger le lot initial

Demandez en lecture seule :

```text
Lis atelier/modele.py et atelier/chargement.py sans les modifier
et sans lire les solutions.
Explique une ligne de fact_sales et ses liens avec les trois dimensions.
Pourquoi charger les dimensions avant les faits ?
Propose le plan pour contrôler puis exécuter le chargement initial fourni.
```

Prévoyez les totaux avant d'exécuter :

```bash
python3 verifier.py 04
python3 executer.py initial
```

Le contrôle doit indiquer **12 faits, 32 unités, 99 000 millimes**. `verifier.py` utilise une base temporaire ; `executer.py initial` crée réellement `outputs/atlas.sqlite`.

## Choisir la bonne version de boutique

NBE change de zone le 8 janvier. Dessinez deux périodes : du 5 au 8 janvier exclu, puis à partir du 8 janvier inclus. Une vente du 7 janvier garde Cap Bon. Celle du 8 janvier utilise Grand Tunis.

```text
Lis atelier/incremental.py et son TODO 05, sans lire les solutions.
Explique SQL_VERSION et la période [valid_from, valid_to), fin exclue.
Propose le plan de trouver_shop_key : exiger exactement une correspondance.
Ne modifie aucun fichier pour le moment.
```

Après lecture du plan :

```text
Complète seulement trouver_shop_key dans atelier/incremental.py.
Exécute SQL_VERSION avec (shop_id, sale_date, sale_date).
Exige exactement une ligne ; sinon lève ValueError. Renvoie la clé entière.
Garde les transactions et mécanismes d'historique fournis intacts.
Depuis atelier/, exécute python3 verifier.py 05 et rapporte le résultat observé.
```

Puis, dans le terminal :

```bash
python3 verifier.py 05
python3 verifier.py 06
python3 executer.py increment
python3 executer.py increment
python3 executer.py rapport
```

Le premier incrément ajoute **2 ventes**, retrouve **1 existante** et crée **1 version de boutique**. Le deuxième ajoute **0 vente**, retrouve **3 existantes** et crée **0 version**. Les deux passages gardent **14 faits, 35 unités et 115 500 millimes**.

Le rapport doit garder les zones historiques : **Cap Bon 43 500 millimes**, **Grand Tunis 72 000 millimes**. Un total correct ne suffit pas si les ventes sont liées à la mauvaise version. Pourquoi les anciennes ventes NBE ne changent-elles pas de zone ?

Faites relire les données et le modèle avec le [prompt 06](06-revoir-corriger-revoir.md), puis corrigez et relisez le résultat corrigé.
