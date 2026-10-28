# 17 — Créer et essayer un Skill local

**Quand l'utiliser** : extension **facultative** (fin de séance 4 si le temps le permet,
ou travail personnel), après avoir utilisé `$revoir-bi` au moins une fois.
Un **Skill** est une méthode réutilisable rangée dans `.agents/skills/<nom>/SKILL.md`,
avec un en-tête `name` et `description`. Il n'ajoute ni modèle, ni outil, ni quota.

**Avant d'envoyer** : lisez `.agents/skills/revoir-bi/SKILL.md`. Choisissez **une**
règle que vous voudriez toujours voir vérifiée sur votre mission (ex. « contrôler
une vente la veille et le jour du changement SCD2 »). Prévoyez comment la réponse
changera avec cette règle.

## Le prompt — créer

```text
Crée .agents/skills/<ma-revue-mission>/SKILL.md, en partant de .agents/skills/revoir-bi/SKILL.md.
En-tête : name: <ma-revue-mission>, et une description d'une phrase qui dit quand l'utiliser.
Garde la lecture seule et la limite de 3 défauts établis.
Ajoute cette règle précise : <ma règle>.
Ne modifie pas les Skills fournis. Montre le fichier complet.
```

## Le prompt — essayer, dans une nouvelle conversation

```text
Utilise $<ma-revue-mission> pour relire <angle> sur la branche <branche>. Lecture seule.
```

Si le Skill n'est pas proposé : redémarrez l'application et rouvrez le dossier du
dépôt. Sinon, essayez : « Lis .agents/skills/<ma-revue-mission>/SKILL.md et
applique sa méthode. » Notez quelle route a marché : la seconde prouve qu'on peut
réutiliser une méthode écrite, pas que le Skill est découvert automatiquement.

## Vérifier dans la réponse

- La réponse applique **votre** règle de façon visible (ex. les deux dates sont
  contrôlées et la version retenue est expliquée).
- Le Skill est versionné : il passe par une branche et une PR comme le reste.

## Deux erreurs fréquentes

1. Une règle vague (« vérifie bien tout ») : elle ne change rien à la réponse.
   Une bonne règle est observable.
2. Croire qu'un Skill remplace les contrôles : comparez toujours avec
   `python -m controles.verifier`.

Source officielle : [créer et utiliser les Skills](https://learn.chatgpt.com/docs/build-skills).
