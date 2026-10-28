# 10 — Comprendre une erreur avant de la corriger

**Quand l'utiliser** : une commande échoue (Python, vérificateur, pytest, Git, CI).

**Avant d'envoyer** : recopiez le message **exact**, en entier, depuis le terminal
ou depuis l'étape de la CI. Lisez la dernière ligne : quelle est votre hypothèse ?

## Le prompt

```text
J'ai lancé : <commande exacte>
Depuis le dossier : <résultat de pwd>
J'attendais : <résultat attendu>
J'ai obtenu ce message exact :
<coller le message complet, sans le raccourcir>
Mon hypothèse : <une phrase>.
Avant de modifier quoi que ce soit : explique ce que dit la dernière ligne, quel fichier
et quelle ligne sont en cause, et si mon hypothèse est juste.
Propose ensuite la plus petite correction, dans solen/ seulement, et la commande
qui prouvera qu'elle marche. Attends mon accord avant de modifier.
```

## Vérifier dans la réponse

- Le diagnostic cite un fichier et une ligne présents dans **votre** message.
- La correction proposée ne touche ni `controles/`, ni les sources, ni les références.
- Après correction, relancez exactement la même commande : même dossier, même venv.

## Deux erreurs fréquentes

1. Résumer l'erreur (« ça marche pas ») au lieu de la coller : Codex devine, et
   corrige autre chose.
2. Oublier d'activer le venv (`source .venv/bin/activate`) : `ModuleNotFoundError`
   ne vient alors pas du code.
