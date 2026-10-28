# 16 — Faire une note d'état et reprendre

**Quand l'utiliser** : en fin de séance, quand la conversation devient longue, ou
quand le partenaire reprend la main. Le **contexte** est ce que la conversation
contient ; le **quota** est la limite d'usage du compte. Une conversation neuve ne
remet pas le quota à zéro, mais elle évite que Codex oublie les règles.

**Avant d'envoyer** : sans regarder, écrivez la dernière commande réussie et la
prochaine petite étape. Vous comparerez avec la note.

## Le prompt — fin de séance

```text
Rédige une note d'état de 8 lignes maximum, que je copierai moi-même. Ne modifie aucun fichier.
Contenu : mission (mission.txt), branche actuelle, ce qui fonctionne,
commandes réellement exécutées et leur résultat, défaut encore ouvert,
prochaine petite étape et sa preuve de réussite.
Sépare clairement : réalisé / à faire / non vérifié. Aucun identifiant de compte.
```

Vérifiez une ligne de la note contre le terminal ou un fichier, puis reportez
l'essentiel dans `notes/JOURNAL.md` si une PR est concernée.

## Le prompt — reprise, dans une nouvelle conversation

```text
Je reprends le dépôt binôme. Lis AGENTS.md, mission.txt et notes/JOURNAL.md.
Voici ma note d'état :
<coller la note>
Vérifie les fichiers cités et l'état Git (branche, fichiers modifiés) ;
ne suppose pas qu'une commande a été exécutée.
Propose la prochaine petite action et sa preuve. Ne modifie rien pour l'instant.
```

## Vérifier dans la réponse

- La note distingue ce qui a été **exécuté** de ce qui a été **proposé**.
- À la reprise, Codex constate l'état réel (branche, `git status`) au lieu de
  répéter la note.
- Relevez ce qui est affiché : modèle, effort, indication de contexte ou d'usage
  (« non affiché » sinon). Ne demandez pas à Codex de deviner son quota.

## Deux erreurs fréquentes

1. Recoller toute l'ancienne conversation : on retrouve le même contexte surchargé.
2. Quota atteint, abandonner la séance : continuez les actions locales (lire le diff,
   relancer un contrôle, calculer à la main, préparer la prochaine demande) et
   attendez le reset affiché, sans achat.
