# Séance 4 — Créer votre Skill local

Un Skill est une petite méthode réutilisable, rangée dans un dossier avec un fichier `SKILL.md`. Son en-tête contient `name` et `description`. Codex lit le détail quand il l'utilise. Un Skill n'ajoute ni modèle, ni outil, ni quota.

Deux modèles courts sont fournis **à la racine du cours** :

- `.agents/skills/revoir-bi/SKILL.md` pour une revue avec preuves ;
- `.agents/skills/expliquer-bi/SKILL.md` pour une explication en français simple.

Gardez la racine du cours sélectionnée dans Codex. Lisez les deux fichiers dans l'éditeur. Repérez le nom, la description et une règle qui change vraiment la réponse. Ne modifiez pas ces modèles.

## Fabriquer `ma-revue-bi`

À **la racine de votre copie du cours**, créez avec l'éditeur ce nouveau dossier de Skill, à côté des modèles fournis :

```text
.agents/
  skills/
    ma-revue-bi/
      SKILL.md
```

Copiez le texte du modèle `revoir-bi/SKILL.md` dans ce nouveau fichier. Changez `name: revoir-bi` en **`name: ma-revue-bi`**. Adaptez la description, puis ajoutez une règle précise, par exemple :

```text
Pour tout contrôle de l'historique, vérifie une vente du 7 janvier et
une vente du 8 janvier, puis explique la version de boutique retenue.
```

Gardez le mode lecture seule. Enregistrez. Vous venez de créer un Skill du projet, sans installation globale.

Ouvrez une nouvelle conversation avec **la racine du cours** sélectionnée. Vérifiez le sélecteur de Skills du client, s'il existe. Si votre Skill n'apparaît pas, redémarrer le client peut être nécessaire. Ne dites pas qu'il est découvert uniquement parce que son fichier existe.

Si le client propose l'appel explicite par nom, essayez :

```text
Utilise $ma-revue-bi pour relire l'historique des boutiques dans ma copie atelier.
Reste en lecture seule et ne lis pas les solutions.
```

Si le client ne le découvre pas, essayez une lecture explicite :

```text
Lis .agents/skills/ma-revue-bi/SKILL.md et applique sa méthode
pour relire l'historique des boutiques dans cette copie atelier.
Reste en lecture seule et ne lis pas les solutions.
```

Cette deuxième route prouve la réutilisation d'une méthode lue dans un fichier ; elle ne prouve pas la découverte automatique du Skill. Les fonctions disponibles dépendent du client et du compte : observez la route réellement obtenue.

Vérifiez l'effet de **votre règle** : la réponse contrôle-t-elle le 7 et le 8 janvier et explique-t-elle les versions ? Gardez une preuve du fichier et de la réponse, sans identifiant de compte. Une conclusion de revue n'est pas une garantie de justesse : comparez avec `python3 verifier.py 05` et `python3 verifier.py 06` depuis `atelier/`.

Source officielle, vérifiée le 27 octobre 2026 : [créer et utiliser les Skills](https://learn.chatgpt.com/docs/build-skills).
