# 04 — Lire les sources CSV, Excel et JSON

**Quand l'utiliser** : séance 2, premier contact avec les sources de `lot1/`.

**Avant d'envoyer** : dans le terminal, `wc -l tronc-commun/sources/lot1/*.csv` (ou `catalogue/<mission>/sources/lot1/*.csv`). Combien de
lignes de données attendez-vous (en-tête exclu) ? Ouvrez le JSON dans l'éditeur :
combien de boutiques ? Notez vos deux nombres.

## Le prompt

```text
Lis mission.txt. Crée dans solen/ un module de lecture des sources de <lot1>
(le CSV de faits, le classeur Excel, le JSON) avec pandas, sans nettoyer encore.
Lis chaque fichier avec son vrai encodage et le bon séparateur ; ne modifie pas les fichiers sources.
Ajoute une commande temporaire ou une fonction qui affiche pour chaque source :
nom du fichier, nombre de lignes, noms des colonnes, 3 premières lignes.
Lance-la et recopie la sortie.
J'attends <n lignes CSV> lignes dans le CSV et <n boutiques> boutiques : compare.
Explique en 4 lignes la différence entre un DataFrame et le fichier d'origine,
et une exception qui peut arriver à la lecture (fichier absent, encodage).
```

## Vérifier dans la réponse

- Les comptes affichés sont égaux aux vôtres (sinon : en-tête ? ligne vide ? encodage ?).
- Les accents s'affichent correctement (pas de `Ã©`).
- Aucune ligne n'est déjà supprimée ou corrigée : la lecture ne nettoie pas.

## Deux erreurs fréquentes

1. Laisser pandas convertir les montants en nombres décimaux dès la lecture :
   `12,500` devient faux. Mieux vaut lire en texte puis normaliser au nettoyage.
2. Lire l'Excel sans préciser la feuille alors que le classeur en a plusieurs.
