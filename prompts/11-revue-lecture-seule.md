# 11 — Revue Codex en lecture seule

**Quand l'utiliser** : le relecteur, après `git fetch` puis `git switch <branche>`,
avant sa propre revue écrite sur GitHub. En séance 4, sur la branche qui contient le
défaut planté.

**Avant d'envoyer** : relancez les contrôles de l'étape. Lisez le diff vous-même
5 minutes et notez **un** point qui vous paraît douteux.

## Le prompt

```text
Utilise $revoir-bi. Branche : <branche>. Mission : lis mission.txt.
Relis en lecture seule le diff de cette branche par rapport à main : ne modifie rien,
ne lance aucun chargement ni export.
Angle de la revue : <données et rejets | totaux | modèle et clés | SCD2 | rejeu>.
Rapporte au plus 3 défauts établis (fichier:ligne, règle violée, exemple observable,
correction proposée), puis les contrôles non réalisés.
J'ai moi-même un doute sur : <mon point>. Dis s'il est fondé, avec une preuve.
```

Si votre client propose des sous-agents et que vous le demandez, vous pouvez
ajouter : « Fais deux lectures indépendantes, l'une sur les données, l'autre sur
le modèle et l'historique, puis fusionne sans doublon. » Sans sous-agents, faites
deux conversations successives, une par angle : c'est la méthode de base.

Si `$revoir-bi` n'est pas reconnu, remplacez la première ligne par :
« Lis .agents/skills/revoir-bi/SKILL.md et applique sa méthode. »

## Vérifier dans la réponse

- Chaque défaut a un **exemple observable** (une valeur, une ligne, un compte) que
  vous pouvez reproduire.
- Les « contrôles non réalisés » sont séparés des défauts.
- `git status` est inchangé après la revue : rien n'a été modifié.

## Deux erreurs fréquentes

1. Coller la conclusion de Codex comme revue GitHub : votre revue écrite doit dire
   ce que **vous** avez vérifié et reproduit.
2. Prendre « aucun défaut établi » pour « tout est juste » : ce n'est que le
   résultat d'une lecture sous un angle.
