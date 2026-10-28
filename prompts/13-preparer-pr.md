# 13 — Préparer la pull request

**Quand l'utiliser** : l'auteur, quand l'étape est terminée et avant
`git add` / `git commit` / `git push`.

**Avant d'envoyer** : écrivez, sans aide, la phrase « Cette PR permet de … » et la
commande qui le prouve.

## Le prompt

```text
Utilise $preparer-pr pour la branche <branche>.
Étape à contrôler : <rejets|initial|increment|rejeu|export|app|tout>.
Relecteur : <prénom et compte GitHub du partenaire>.
Ma phrase : « Cette PR permet de <…> », preuve : <commande>.
Fais la liste de contrôle, puis propose un titre et une description en français.
Ne commite pas, ne pousse pas, n'ouvre pas la PR.
```

Si `$preparer-pr` n'est pas reconnu : « Lis .agents/skills/preparer-pr/SKILL.md et
applique sa méthode. »

Ensuite, vous-même :

```bash
git status
git add <fichiers listés>
git commit -m "<titre proposé>"
git push -u origin <branche>
```

Sur GitHub : **Compare & pull request**, collez la description, désignez le
relecteur dans **Reviewers**, puis **Create pull request**.

## Vérifier dans la réponse

- Toutes les lignes de la liste sont OK, ou vous savez pourquoi l'une ne l'est pas.
- Aucun fichier `outputs/`, `.venv/` ou secret dans `git status` avant `git add`.
- L'entrée de `notes/JOURNAL.md` contient une preuve réelle (commande + résultat).

## Deux erreurs fréquentes

1. `git add .` sans relire `git status` : un fichier inattendu part dans la PR.
2. Ouvrir la PR depuis `main` : il n'y a rien à comparer, ou pire, on a commité sur
   `main` directement.
