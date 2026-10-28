# Journal du binôme

Une entrée par pull request, la plus récente en haut. Quatre rubriques, courtes.
Écrivez ce que vous avez **vu**, pas ce que Codex a promis.

<!-- Modèle à copier pour chaque nouvelle PR :

## AAAA-MM-JJ — PR #<n> — <titre court>

Auteur : <prénom> · Relecteur : <prénom> · Mission : <contenu de mission.txt>

- **État actuel** : ce qui fonctionne maintenant (une ou deux phrases).
- **Décision** : ce que nous avons choisi et pourquoi (règle métier, refus d'une
  proposition de Codex, ordre des étapes…).
- **Preuve** : la commande lancée et son résultat réel
  (ex. `python -m controles.verifier --mission tronc-commun --etape initial` → OK ;
  12 rejets dont 3 `id_conflit`).
- **Prochain objectif** : la prochaine petite étape, avec son résultat observable.

-->

## AAAA-MM-JJ — PR #1 — Journal et présentation du binôme

Auteur : <prénom A> · Relecteur : <prénom B> · Mission : tronc-commun

- **État actuel** : dépôt créé, B invité et contributeur ; rien n'est encore construit.
- **Décision** : A crée la première PR, B relit ; les rôles alternent ensuite.
- **Preuve** : `python -m controles.verifier --mission tronc-commun --etape initial`
  → échec attendu, message : « <recopier la première ligne du message> ».
- **Prochain objectif** : lire les quatre sources du tronc commun et compter leurs lignes.
