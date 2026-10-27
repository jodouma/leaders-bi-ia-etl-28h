# Séance 4 — Montrer les chiffres dans Power BI

L'entrepôt final doit déjà contenir 14 faits. Depuis **`atelier/`**, dans le terminal :

```bash
python3 verifier.py 07
python3 executer.py export
```

Le contrôle 07 utilise des sorties temporaires. La seconde commande crée votre livraison dans **`outputs/powerbi/livraison-…/`** et affiche son chemin réel. Le suffixe varie : utilisez le dossier affiché. Il contient quatre CSV et `manifest.json`.

Codex peut aider à comprendre la livraison :

```text
Lis les fichiers de ma dernière livraison complète sous atelier/outputs/powerbi/.
En lecture seule, explique pourquoi il faut transférer ensemble dim_date.csv,
dim_product.csv, dim_shop.csv, fact_sales.csv et manifest.json.
Pourquoi garder les trois versions de boutique et relier les tables par shop_key ?
Ne modifie rien. Ne prétends pas avoir ouvert Power BI.
```

Faites vous-même l'import, les types, les trois relations et les visuels dans **Power BI Desktop sur Windows**, selon le [guide Power BI](../powerbi/README.md). Sur Ubuntu, transférez la livraison complète vers le poste Windows prévu. Un rapport local Python ou un texte de Codex ne remplace pas cette manipulation.

Pour comprendre la mesure fournie :

```text
Explique en français simple, sans modifier le projet :
CA TND = DIVIDE(SUM(fact_sales[amount_millimes]), 1000)
Montre un calcul concret de millimes vers TND avant de parler de DAX.
Pose-moi une question sur le diviseur 1000 et attends ma réponse.
```

Dans le vrai rapport, vérifiez **115,500 TND** au total, puis le graphique par zone commerciale historique : **Cap Bon 43,500 TND** et **Grand Tunis 72,000 TND**. Faites un filtre, expliquez sa conséquence, retirez-le puis actualisez. Gardez une preuve des trois relations et des chiffres.

Créez ensuite votre Skill avec le [prompt 08](08-creer-skill.md), puis faites les revues du [prompt 06](06-revoir-corriger-revoir.md).
