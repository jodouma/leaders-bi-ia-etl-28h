# Corrigés ciblés Atlas

Ces trois fichiers remplacent les trois fonctions à construire. Les modules de schéma, transactions, SCD2, export et vérification restent ceux de `projet/` ; ils sont fournis et partagés afin de conserver une seule ossature.

Depuis la racine, créer une référence autonome dans un **nouveau** dossier :

```bash
python3 outils/jalon.py 07 reference-atlas
cd reference-atlas
python3 verifier.py tout
python3 executer.py initial
python3 executer.py increment
python3 executer.py increment
python3 executer.py rapport
python3 executer.py export
```

Pour reprendre un point précis, utiliser un autre dossier neuf. Un jalon signifie que les petites fonctions jusqu'à ce contrôle sont déjà complétées ; aucune sortie n'est préchargée.

| Jalon | État du code créé | Contrôle correspondant |
|---|---|---|
| 01 | Trois fonctions à compléter ; lecture CSV et calcul fournis | Sources disponibles, calcul 9 000 millimes |
| 02 | `nettoyage.normaliser_vente` complétée | Qualité CSV et sommes initiales |
| 03 | + `lecture.lire_increment_sql` complétée | Extraction réelle de 3 ventes et 1 changement |
| 04 | Même code que 03 ; chargement initial fourni prêt | Étoile initiale : 12 faits |
| 05 | + `incremental.trouver_shop_key` complétée | Bornes temporelles : 7 / 8 janvier |
| 06 | Toutes les fonctions complétées | Incrément, zones historiques et rejeu |
| 07 | Toutes les fonctions complétées | Quatre exports CSV et manifeste |

`normaliser_vente(ligne)` renvoie un dictionnaire avec `sale_id`, `date`, `shop_id`, `product_id`, `quantity`, `unit_price_millimes`, `amount_millimes`. Les identifiants sont des textes sans espaces aux extrémités et en majuscules ; les quantités et montants sont des entiers ; la date est un texte ISO. Les helpers `date_iso`, `entier_positif`, `millimes` sont fournis.

`lire_increment_sql(chemin_source, batch_id="2026-01-08")` renvoie `(ventes, changements, preuve)` : deux listes de dictionnaires et un dictionnaire de traçabilité. La connexion est en lecture seule ; les deux requêtes utilisent `(batch_id,)`. Le fichier absent est une erreur.

`trouver_shop_key(conn, shop_id, sale_date)` renvoie une clé entière lorsqu'une seule version couvre la date `[valid_from, valid_to)`. Aucune correspondance ou plusieurs correspondances sont des erreurs.

Les contrôles utilisent des dossiers temporaires isolés. Ils testent le code courant sans modifier `outputs/`. Les commandes `executer.py` produisent réellement les sorties de travail. Les résultats ETL ne prouvent ni une installation Codex, ni un compte Free, ni une manipulation Power BI Desktop.
