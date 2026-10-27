# Atlas — le rapport doit résister à une erreur

La direction prépare une décision commerciale. Une règle du pipeline a été altérée et les quantités annoncées ne correspondent plus aux ventes. Votre équipe doit reproduire le problème, réparer la petite règle, puis prouver le rapport après actualisation. Groupe de trois personnes au maximum ; chacun explique sa contribution.

Depuis la racine, créer un dossier **neuf** :

```bash
python3 defi/preparer.py atelier-defi
cd atelier-defi
python3 verifier.py 02
```

La copie contient le pipeline complet, un seul défaut borné et aucune sortie. Les données originales restent les mêmes. Seul `nettoyage.py`, fonction `normaliser_vente`, est à réparer. Ne modifier ni données, ni vérificateur, ni sommes attendues. Demander une revue ciblée à Codex ou à un pair ; un seul membre écrit le correctif.

1. **15 min :** écrire le plan, répartir les contributions, prédire une quantité à partir d'une ligne originale.
2. **40 min :** reproduire et expliquer le premier écart ; réparer la petite règle dans le fichier autorisé.
3. **25 min :** faire relire le correctif, contrôler puis corriger si nécessaire. Refaire le contrôle concerné après correction.
4. **35 min :** produire les sorties et actualiser le rapport Power BI préparé en S4 sur Windows. Montrer le total, les trois relations et un filtre ; chaque personne explique une preuve.
5. **20 min :** comparer le rapport aux contrôles Python/SQL, conserver la capture et le fichier Power BI.
6. **20 min :** refaire le parcours dans un dossier de sortie neuf, terminer le journal et la remise.

Les 155 minutes de pratique comprennent 35 minutes consacrées à l'actualisation et à la présentation. La pause de 10 minutes et l'introduction de 15 minutes sont en dehors de ce budget. L'ordre des blocs peut s'adapter à l'attente du poste Windows.

Après correction, depuis `atelier-defi` :

```bash
python3 verifier.py tout
python3 executer.py initial
python3 executer.py increment
python3 executer.py increment
python3 executer.py rapport
python3 executer.py export
```

Résultats à expliquer : 14 faits, 35 unités, 115 500 millimes ; rejeu avec 0 insertion et 3 ventes déjà connues ; trois versions de boutique. La zone historique Cap Bon conserve 43 500 millimes et Grand Tunis rassemble 72 000 millimes. Une ancienne vente NBE conserve sa clé de version. Les bornes du 7 et du 8 janvier sont différentes.

Le contrôle utilise des sorties temporaires : il ne répare pas votre entrepôt. Si vous avez chargé avant la correction, conservez cet état comme preuve du symptôme et créez une nouvelle copie de votre code corrigé avec un dossier `outputs` vide pour la reconstruction ; ne contournez pas le refus d'écraser une vente différente. Pour remettre à jour Power BI, recopiez les quatre CSV et le manifeste de la nouvelle livraison dans le dossier Windows déjà utilisé en S4, puis cliquez sur Actualiser.

Livrer le code corrigé, le journal avant/après, les commandes et leurs résultats, la reconstruction de l'entrepôt, les quatre CSV avec manifeste et le fichier Power BI avec preuve d'actualisation. Une capture d'un tutoriel ne prouve pas votre manipulation. Un contrôle ETL local ne constitue pas une preuve Power BI.
