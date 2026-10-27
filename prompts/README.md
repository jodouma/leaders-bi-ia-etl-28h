# Demandes Codex — Atlas, 15 h

[Retour au cours](../README.md)

Les cinq séances utilisent un même projet. Vous complétez seulement **trois petites fonctions** ; le chargement, les transactions, l'historique et les exports sont fournis. Lisez le prompt, prédisez un résultat, demandez un plan, puis exécutez et comparez. Conservez votre première tentative avant de consulter une solution.

| Quand | Demande | Résultat à vérifier |
| --- | --- | --- |
| Séance 1 : ouvrir l'atelier | [01 — Comprendre et planifier](01-comprendre-planifier.md) | Calcul de 9 000 millimes ; contrôle 01. |
| Séance 2 : nettoyer le CSV | [02 — Normaliser une vente](02-normaliser-vente.md) | 12 acceptées, 3 rejets, 1 doublon ; contrôle 02. |
| Séance 2 : lire SQL | [03 — Extraire le lot SQL](03-extraire-sql.md) | 3 ventes et 1 changement ; contrôle 03. |
| Séance 3 : charger et garder l'histoire | [04 — Charger, ajouter, rejouer](04-charger-histoire.md) | Contrôles 04 à 06 ; 14 faits et rejeu stable. |
| Séance 4 : montrer les chiffres | [05 — Exporter et comprendre Power BI](05-powerbi.md) | Contrôle 07, puis manipulation Power BI sur Windows. |
| Séances 2 à 5 : fiabiliser, puis réparer le défi | [06 — Revue, correction, deuxième revue](06-revoir-corriger-revoir.md) | Défaut établi, correction testée et résultat relu. |
| Fin de séance ou conversation trop longue | [07 — Résumer et reprendre](07-reprendre.md) | Bilan court vérifié ; prochaine petite action claire. |
| Séance 4 : créer une méthode locale | [08 — Créer et essayer un Skill](08-creer-skill.md) | Votre `ma-revue-bi`, une règle changée et un effet observé. |

Le guide d'installation crée **une seule fois** le dossier `atelier/`. Continuez dans cette copie existante ; ne relancez pas sa création au début du cours. Dans Codex, sélectionnez **la racine du cours** (`~/cours-bi`), qui contient `AGENTS.md`, `.agents/` et `atelier/`.

Dans le terminal Ubuntu ou Ubuntu/WSL2, depuis la racine :

```bash
cd atelier
```

Les commandes Python se lancent ensuite **dans `atelier/`**. Les demandes à Codex utilisent les chemins depuis la racine, par exemple **`atelier/nettoyage.py`**. Gardez la racine sélectionnée dans Codex pour les instructions et Skills locaux. Ne modifiez pas `projet/`, `solutions/`, les données sources ou les contrôles.

Un jalon de reprise crée du **code déjà complété jusqu'à ce point**, dans un dossier neuf. Il ne précharge aucune sortie et ne termine pas votre première tentative. Par exemple, depuis la racine : `python3 outils/jalon.py 03 reprise-sql`, puis `cd reprise-sql`. Gardez votre ancien dossier. Dans les demandes suivantes, remplacez alors `atelier/` par `reprise-sql/`. Les numéros 01 à 07 sont des points de contrôle, pas sept séances.

Les commandes `verifier.py` testent le code avec des sorties temporaires isolées. Elles ne remplissent pas `atelier/outputs/`. Les commandes `executer.py` créent réellement les sorties de travail.

Codex gratuit est annoncé dans l'application de bureau, sous réserve de déploiement : **GPT-6 Luna, vitesse Standard**. Standard n'est pas un niveau de réflexion. Choisissez **High si votre interface le propose**, sinon gardez le défaut. Le CLI n'est pas un prérequis ; aucune durée d'usage Free n'est garantie. Si le quota bloque, continuez les calculs, scripts et contrôles locaux puis attendez le reset affiché. Cela ne valide pas une manipulation de Codex qui reste à réaliser. [Offre officielle](https://learn.chatgpt.com/docs/pricing), [modèles](https://learn.chatgpt.com/docs/models) — vérifiés le 27 octobre 2026.
