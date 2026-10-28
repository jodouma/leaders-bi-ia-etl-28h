# 12 — Corriger après revue, puis faire relire

**Quand l'utiliser** : l'auteur, quand la PR a reçu « Request changes » ou des
constats de revue.

**Avant d'envoyer** : pour chaque constat, prévoyez : défaut réel ou faux constat ?
Quelle valeur changera après correction ?

## Le prompt

```text
Voici les constats de revue reçus sur ma PR <n> :
<coller les constats>
Pour chacun, vérifie d'abord contre le code actuel : établi, non établi, ou non vérifiable,
avec une preuve observable.
Corrige seulement les défauts établis, dans solen/ (ou tests/), sans toucher
aux sources, aux références ni à controles/.
Lance <contrôles de l'étape>, pytest controles et pytest -q ; recopie les sorties.
Explique pour chaque constat rejeté pourquoi, en une phrase.
Je prévois que <valeur> passera de <avant> à <après> : compare.
Ne fais ni commit ni push.
```

Puis, dans une **nouvelle** conversation (ou par le relecteur) :

```text
Utilise $revoir-bi sur la version corrigée de la branche <branche>, en lecture seule.
Pour chaque constat initial : corrigé avec preuve, encore présent, ou non vérifié.
Cherche aussi une erreur introduite par la correction. Ne modifie rien.
```

## Vérifier dans la réponse

- Une correction = un défaut ; le diff ne contient pas de « nettoyage » non demandé.
- Le contrôle qui échouait passe maintenant, et les autres restent verts.
- Répondez à chaque commentaire GitHub (« corrigé dans <commit> » ou « non retenu
  parce que… ») avant de redemander une revue.

## Deux erreurs fréquentes

1. Corriger en modifiant le contrôle ou la valeur attendue : c'est interdit, et le
   relecteur le verra dans le diff.
2. Pousser la correction sans relancer **tous** les contrôles : une correction en
   casse souvent une autre (ex. le rejeu).
