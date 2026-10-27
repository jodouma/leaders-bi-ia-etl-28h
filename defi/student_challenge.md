# Défi CampusBox — ventes servies et rejeu fiable

## CampusBox : un rapport qui résiste au prochain lot

CampusBox vend des repas sur deux campus fictifs : Nabeul et Tunis. Les ventes arrivent au comptoir ou en ligne ; certaines sont servies, d’autres annulées ou en attente. Un identifiant peut revenir dans le lot suivant.

**La question à résoudre** — Quel montant de ventes servies observons-nous, par point de vente et par canal, sans compter deux fois la même vente ?

Vous disposez de 7 heures dans les 28 heures du cours. Réutiliser les idées et les fichiers Atlas est permis ; copier le code sans traiter les nouvelles règles ne répondra pas au besoin. Aucun outil payant n’est requis : le navigateur IA reste la route de base.

- Produire un programme local, un entrepôt SQLite et un rapport HTML depuis cette base.
- Conserver les décisions de qualité et prouver l’ajout puis le rejeu.
- Chaque membre explique une décision, une trace et une limite.

**Une conclusion à limiter** — Les montants de ventes servies ne décrivent ni bénéfice, ni coût, ni nombre de clients uniques, ni demande future.

## Lire les quatre fichiers avant d’adapter le code

| Fichier dans defi/data/ | Contenu |
| --- | --- |
| ventes_initiales.csv | 14 lignes reçues, sans compter l’en-tête. |
| ventes_ajout.csv | 4 lignes reçues dans un second lot. |
| menus.csv | Trois menus reconnus et leurs noms. |
| points.csv | Deux points de vente et leurs noms. |

Les CSV sont en UTF-8, séparés par des virgules, avec un point décimal. Conserver les fichiers d’origine. Ouvrir dans l’éditeur plutôt que réenregistrer dans un tableur. Les données sont synthétiques et disponibles sous CC0 1.0 ; les logos sont exclus de cette licence.

| Champ | Sens |
| --- | --- |
| line_id / date | Identité stable d’une vente élémentaire et date réelle. |
| point_id / menu_id | Codes reconnus dans les catalogues. |
| quantity / unit_price_tnd | Portions du même menu et prix par portion. |
| status / channel | État de service et canal à conserver. |

**Le grain est une vente élémentaire** — Une ligne décrit un menu vendu dans un point à une date, avec plusieurs portions possibles. Ce n’est pas nécessairement un client, un paiement ou une commande contenant plusieurs menus.

## Le contrat métier : ce qui entre dans les indicateurs

- Enlever les espaces ; normaliser la casse des identifiants, codes, statut et canal.
- Vérifier identifiant présent, date réelle AAAA-MM-JJ, point/menu connus, quantité entière positive, prix Decimal fini positif représentant un entier de millimes.
- Canaux reconnus : COMPTOIR et EN_LIGNE. Un autre canal, comme FAX, est une erreur à journaliser.
- Statuts reconnus : SERVIE, ANNULEE, EN_ATTENTE. Seules les lignes SERVIE alimentent les faits de ventes du rapport.
- ANNULEE et EN_ATTENTE restent dans les lignes non retenues, avec « hors périmètre : statut … ». Ne pas inventer une règle de remboursement.
- Même line_id et contenu normalisé identique : répétition. Même identifiant avec contenu différent : conflit explicite, sans remplacement silencieux.

**Deux raisons d’être non retenue** — Une ligne mal formée est une erreur de qualité ; une ligne ANNULEE bien formée est hors périmètre métier. Votre journal peut réunir ces lignes, mais la colonne motif doit rendre la distinction lisible.

Dans un fichier : reçu = retenu + doublon interne + non retenu. Au chargement : retenues = nouvelles + déjà présentes si aucun conflit n’interrompt le lot. Les deux bilans décrivent deux étapes distinctes.

## Prédire avant de générer

| Ligne / variation | Prédiction |
| --- | --- |
| L001 : 2 portions à 8.500 TND | 17.000 TND = 17 000 millimes. |
| Même vente avec 3 portions | 25.500 TND ; écart 8.500 TND. |
| Une ligne ANNULEE | 0 dans les ventes servies ; une raison hors périmètre dans le journal. |
| Une ligne SERVIE avec canal FAX | 0 dans les faits ; canal inconnu dans le journal. |
| Une vente chargée revient identique | 0 nouveau fait ; une ligne already existing au chargement. |

Sans IA, choisir dans le CSV une vente servie, une exclusion métier et une erreur de donnée. Écrire pour chacune sa destination et son effet sur les indicateurs. Ces prédictions devront encore être vraies après la construction du programme.

**La variation ne doit pas devenir une corruption** — Pour modifier L001, utiliser un mini-fichier d’essai et une base d’essai séparés. Ne pas modifier les fichiers officiels. Avec son identifiant inchangé dans une base déjà remplie, cette variation devient un conflit à refuser, pas un ajout légitime.

Dessiner ensuite le fait et ses dimensions. Vous pouvez conserver channel dans le fait ou créer une dimension canal. Justifier le choix et garantir qu’une jointure ne multiplie pas les ventes. Le statut sert à choisir le périmètre, pas à additionner les repas non servis.

## Installer le défi sans mélanger les deux cas

À la racine du cours, créer le dossier campusbox/. Copier dedans les fichiers Python nécessaires depuis votre projet Atlas, puis créer campusbox/data/ et campusbox/outputs/. Copier les quatre CSV de defi/data/ vers campusbox/data/. Aucun fichier Atlas ne doit être utilisé comme source du rapport CampusBox.

- Adapter les chemins et les noms : menus.csv et points.csv remplacent produits.csv et boutiques.csv.
- Adapter le grain et les colonnes : line_id, point_id, menu_id, status et channel.
- Construire une base campusbox/outputs/campusbox.sqlite et un rapport campusbox/outputs/rapport_campusbox.html.
- Prévoir un programme de relance campusbox/executer.py qui lit les deux lots, montre les bilans et rejoue le lot d’ajout.

```text
docker compose run --rm -w /workspace/campusbox atelier python executer.py
```

La commande précédente se saisit sur une seule ligne sous Windows comme sous Ubuntu. En natif, ouvrir le terminal dans campusbox/ puis utiliser py -3 executer.py ou python3 executer.py. Pour ouvrir le rapport, double-cliquer le HTML produit ; le serveur Atlas habituel sert seulement projet/outputs/.

**Le vérificateur Atlas reste Atlas** — verifier.py 01 à 07 vérifie le cas guidé et ses colonnes. Pour CampusBox, créer vos propres contrôles à partir de ce brief ; ne renommer pas ses constantes pour obtenir un succès artificiel.

## Quatre jalons et des rôles qui tournent

| Jalon | Durée | Preuve pour continuer |
| --- | --- | --- |
| 1 · Définir | 60 min | Contrat d’une page, calcul manuel, modèle, trois critères de réussite. |
| 2 · Construire | 150 min | Lecture → qualité → montant → base ; journal et bilans. |
| 3 · Éprouver | 120 min | Ajout, rejeu et conflit contrôlé dans une copie d’essai. |
| 4 · Expliquer | 90 min | Rapport, consigne de relance et explication individuelle. |

Le cadrage, les démonstrations et les retours conceptuels représentent 126 minutes ; la pratique 294 minutes. Les durées incluent les demandes IA, les essais, les réparations et les traces ; elles ne sont pas des mesures issues d’un pilote débutant.

| Rôle tournant | Action vérifiable |
| --- | --- |
| Demandeur | Annonce entrée/sortie, prépare une demande bornée. |
| Opérateur | Enregistre, exécute et conserve une vraie sortie. |
| Testeur | Prédit, compare et cherche un contre-exemple. |

**À deux ou seul** — À deux, cumuler deux rôles puis inverser. Seul, noter les trois points de vue. À trois, changer à chaque jalon. Le titulaire du compte saisit ses demandes ; les autres ne partagent pas ses identifiants.

## Des preuves qui résistent à un second lancement

- Réconcilier toutes les lignes du lot initial : retenues, doublons et non retenues avec motif.
- Vérifier quantité et montant d’une vente à la main puis le total des faits par SQL.
- Vérifier que les montants par point et par canal retrouvent chacun le montant global.
- Avant le lot d’ajout, prédire ce qui sera nouveau, déjà présent ou non retenu.
- Après le rejeu de l’ajout, comparer le nombre de faits, les portions et le montant : tous doivent rester stables.
- Sur une copie, provoquer un identifiant conflictuel puis montrer l’erreur et le retour arrière du lot.

Le rapport final indique sa période réelle, le nombre de ventes élémentaires, les portions et les montants TND à trois décimales. Il montre les campus et les canaux avec des libellés lisibles, puis une observation et une limite. Tous les chiffres proviennent de la base.

**La bonne granularité de demande IA** — « Adapte uniquement ma fonction de validation aux huit colonnes CampusBox. Distingue statut hors périmètre et donnée invalide, conserve channel et motif. Voici trois lignes fictives et leurs issues attendues. Ne reconstruis pas le projet entier. »

Les indices sont gradués dans le livre 05. Les totaux de correction y sont séparés pour vous permettre de prédire d’abord les résultats à partir des sources.

## Livrer le dossier et montrer sa compréhension

- Code, quatre CSV et README court avec dossier de départ, commande et sorties.
- Base SQLite et rapport HTML issus de l’exécution réelle.
- Journaux : initial, ajout, rejeu, exclusions avec motif et trace de conflit contrôlé.
- journal_ia.md : demandes importantes, choix acceptés/refusés et contrôles ayant décidé.
- Tableau des rôles par jalon et une phrase de contribution par membre.

Chaque personne prépare une explication orale courte ou écrite : suivre une ligne jusqu’au rapport, expliquer une décision de périmètre et une preuve de rejeu. Le code et les notes restent consultables ; aucune nouvelle réponse IA n’est nécessaire pour cette explication.

**Mini-variation individuelle** — Prédire l’effet d’une portion supplémentaire sur une vente servie, puis dire pourquoi le même changement sous un identifiant déjà chargé ne doit pas être accepté silencieusement. Expliquer aussi ce qui changerait si le statut devenait EN_ATTENTE.

Une réalisation partielle peut être expliquée honnêtement : montrer ce qui fonctionne, le blocage reproduit et le prochain contrôle. Ne pas fabriquer une sortie pour masquer un défaut.

**À ce stade, je sais…** — adapter le contrat d’un cas à un autre, éprouver le résultat et distinguer ma compréhension personnelle de la production collective.
