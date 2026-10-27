# Séance 2 — Nettoyer une vente

Une ligne brute doit devenir une vente cohérente ou un rejet expliqué. Avant Codex, prévoyez ce que deviennent un identifiant entouré d'espaces et un identifiant absent (`None`). Les identifiants doivent être de vrais textes non vides : `None` ne doit jamais devenir le texte `"NONE"`.

Dans Codex, racine du cours sélectionnée, demandez d'abord une lecture de votre copie **`atelier/`** :

```text
Lis atelier/nettoyage.py et son TODO 02, sans lire les solutions.
Explique la sortie attendue de normaliser_vente(ligne).
Propose un plan court en réutilisant date_iso, entier_positif et millimes.
Montre comment refuser un identifiant nul ou non textuel.
Ne modifie aucun fichier pour le moment.
```

Comparez le plan aux commentaires du fichier, puis :

```text
Complète seulement normaliser_vente dans atelier/nettoyage.py.
Exige des textes non vides pour sale_id, shop_id et product_id : strip puis upper.
Refuse None et les autres types, sans les convertir en texte.
Utilise les helpers fournis pour date, quantité et prix ; aucun float monétaire.
Renvoie les sept champs CHAMPS_VENTES, dont amount_millimes = quantité × prix.
Garde les autres fonctions, données et vérificateurs intacts.
Depuis atelier/, exécute python3 verifier.py 02 et rapporte le résultat réel.
```

Contrôle à relancer vous-même dans le terminal, depuis `atelier/` :

```bash
python3 verifier.py 02
```

Attendu : **12 acceptées + 3 rejets + 1 doublon = 16 lignes**, quantité **32**, montant **99 000 millimes**. Le contrôle utilise des sorties temporaires ; il ne crée pas encore votre entrepôt dans `outputs/`.

Une réponse « tout passe » ne suffit pas : lisez l'observation du terminal. Si le contrôle échoue, gardez votre tentative, copiez l'erreur exacte et utilisez la méthode du [prompt 06](06-revoir-corriger-revoir.md). Ne changez pas les résultats attendus pour rendre le contrôle vert.

Expliquez à un camarade une règle d'harmonisation et une règle de rejet. Pourquoi le doublon n'est-il pas une vente supplémentaire ?
