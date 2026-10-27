# Séance 1 — Une première victoire

Le guide d'installation a déjà créé `atelier/`. Gardez **la racine du cours** sélectionnée dans Codex. Dans le terminal, depuis cette racine, entrez dans la copie existante :

```bash
cd atelier
```

Ne relancez pas la création du dossier. S'il manque, revenez au guide d'installation. Dans Codex, envoyez cette petite demande :

```text
Je débute. Travaille seulement dans ma copie atelier/ de ce projet.
Lis atelier/calcul.py et un petit exemple dans atelier/data/ventes_initiales.csv.
Explique ce que représente une ligne de vente et le montant en millimes.
Propose un plan de trois étapes pour rendre ces ventes fiables.
Indique une sortie et un contrôle par étape. Ne modifie aucun fichier.
```

Avant l'exécution, prévoyez : 2 carnets à 4 500 millimes donnent combien ? Dans le terminal, **depuis `atelier/`** :

```bash
python3 calcul.py
python3 verifier.py 01
```

Attendu : **9 000 millimes = 9 TND**, puis `OK 01`. Codex ne doit pas réécrire `calcul.py` : le premier calcul est fourni. Expliquez pourquoi on divise les millimes par 1 000 pour afficher des TND.

Le fichier `AGENTS.md` fourni à la racine contient des règles du projet. Dans Codex, demandez :

```text
Quelles instructions du projet as-tu lues ? Cite leurs fichiers.
Rappelle les limites utiles pour travailler uniquement dans atelier/.
Ne modifie rien. Si AGENTS.md n'est pas chargé, dis-le.
```

Lisez les règles avec un camarade. Distinguez « le fichier existe » de « Codex indique l'avoir lu ». Une lecture explicite du fichier peut aider si le client ne le découvre pas.

Notez le modèle réellement affiché, High si disponible, et l'indication d'usage visible ou « non affiché ». Un test Python réussi ne prouve ni un accès Free à Codex ni une installation sur un autre système.
