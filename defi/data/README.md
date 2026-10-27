# Campus Box — contrat des données

Ces données sont **entièrement fictives**, créées pour le défi pédagogique Campus Box. Aucun nom d’étudiant, client, identifiant de compte ou secret n’y figure.

## Fichiers et conventions

- `ventes_initiales.csv` : 14 lignes de données, hors en-tête.
- `ventes_ajout.csv` : 4 lignes de données, hors en-tête. Certaines références peuvent avoir déjà été rencontrées.
- `menus.csv` : trois menus et leurs noms.
- `points.csv` : deux points de vente et leurs noms.

Encodage UTF-8 ; séparateur de colonnes virgule ; point décimal ; pas de séparateur de milliers. Une quantité est un nombre de portions. **1 TND = 1 000 millimes.** Les prix dans les ventes constituent les prix observés de ces ventes, pas un tarif universel à remplacer par un montant inventé.

| Champ | Sens et contrôle |
|---|---|
| `line_id` | Identifiant stable d’une vente élémentaire ; non vide. |
| `date` | Date réelle au format `AAAA-MM-JJ`. |
| `point_id` | Code présent dans `points.csv`, après normalisation. |
| `menu_id` | Code présent dans `menus.csv`, après normalisation. |
| `quantity` | Nombre entier strictement positif de portions du même menu. |
| `unit_price_tnd` | Prix positif d’une portion en TND ; au plus trois décimales significatives. |
| `status` | `SERVIE`, `ANNULEE` ou `EN_ATTENTE`. Seule SERVIE entre dans le rapport. |
| `channel` | `COMPTOIR` ou `EN_LIGNE`. |

La casse et les espaces autour des valeurs peuvent varier. Les normaliser ne doit pas modifier le sens métier. Une ligne valide décrit un menu dans un point à une date, pas nécessairement un client ni une commande complète.

## Exclusions et doublons

Les lignes hors périmètre ANNULEE/EN_ATTENTE sont conservées avec une raison, séparément des faits de ventes servies. Le journal des « rejets » distingue une erreur de données d’une exclusion métier.

Après normalisation, une référence répétée avec des valeurs identiques ne doit pas compter une nouvelle vente. Une même référence avec d’autres valeurs est un conflit explicite ; conserver une version au hasard est interdit.

Conserver les originaux. Une expérience modifie une copie, avec une base d’essai séparée si elle change une ligne déjà chargée. Ouvrir les CSV dans le Bloc-notes ou avec le programme du cours évite qu’un réenregistrement par un tableur transforme les dates ou séparateurs.

## Utilisation et droits

Jeu synthétique généré pour ce cours de Youssef Douma à Leaders University. Les données CSV sont fournies sous **CC0 1.0** : copie, modification et réutilisation autorisées. Cette mise à disposition concerne les données fictives du défi, pas les logos de l’université ni des données réelles ajoutées ultérieurement.

Consulter `../student_challenge.md` pour les règles, les livrables et les jalons ; aucune solution complète n’est fournie dans ce dossier.
