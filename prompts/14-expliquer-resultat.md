# 14 — Expliquer un résultat (ligne source → graphique)

**Quand l'utiliser** : quand un chiffre vous surprend, et pour préparer la
soutenance (suivre une ligne de la source jusqu'au graphique, expliquer un rejet,
une version historique, un indicateur et son unité).

**Avant d'envoyer** : choisissez une ligne précise d'une source (son identifiant)
et prévoyez où elle finit : rejetée ? dans quel fait, quelle zone, quel mois ?

## Le prompt

```text
Utilise $expliquer-bi. Ne modifie rien.
Suis la ligne <identifiant> de <fichier source> à travers notre pipeline :
lecture, nettoyage (gardée, normalisée ou rejetée et pourquoi), clé de date, de produit,
de boutique (quelle version SCD2 et pourquoi), ligne de fait, export CSV,
et contribution à l'indicateur <indicateur> dans le graphique <graphique>.
Donne chaque valeur avec son unité, et le fichier:ligne du code qui la produit.
Ma prévision : <où elle finit>. Dis si j'ai raison.
Termine par une question pour vérifier que j'ai compris.
```

## Vérifier dans la réponse

- Chaque étape cite une valeur que vous pouvez retrouver (dans la source, `rejets.csv`,
  `sqlite3`, le CSV exporté, Power BI).
- Retrouvez vous-même au moins une de ces valeurs ; répondez à la question finale
  **sans** relire la réponse.

## Deux erreurs fréquentes

1. Choisir une ligne « facile » : prenez aussi une ligne rejetée et une ligne de la
   boutique qui change de zone, ce sont les questions de soutenance.
2. Réciter l'explication de Codex : reformulez avec vos mots et votre exemple.
