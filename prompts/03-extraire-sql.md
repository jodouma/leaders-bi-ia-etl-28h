# Séance 2 — Lire une vraie source SQL

Le CSV contient le lot initial. La base `atelier/data/source_operationnelle.sqlite` contient le lot du **8 janvier 2026**. Extraire signifie lire ; cela ne charge pas encore l'entrepôt.

Dans Codex, gardez la racine du cours sélectionnée :

```text
Lis atelier/lecture.py et son TODO 03. Ne lis pas les solutions.
Explique SQL_VENTES, SQL_CHANGEMENTS et le paramètre batch_id.
Propose un petit plan pour lire les deux tables en lecture seule,
convertir les lignes en dictionnaires et fermer la connexion même en cas d'erreur.
Ne modifie aucun fichier pour le moment.
```

Question avant le code : pourquoi lire le même lot avec un paramètre plutôt que fabriquer le SQL en assemblant des textes ? Puis :

```text
Complète seulement lire_increment_sql dans atelier/lecture.py.
Utilise connexion_source, les deux SQL fournis et (batch_id,) comme paramètres.
Convertis les sqlite3.Row avec dict(row) et ferme la connexion dans finally.
Renvoie (ventes, changements, preuve_source(chemin_source, batch_id)).
Une base absente doit rester une erreur : aucun fichier créé ni repli vers CSV.
Garde le reste intact. Depuis atelier/, exécute python3 verifier.py 03.
Rapporte les résultats réellement lus, sans inventer une extraction.
```

Dans le terminal, depuis `atelier/` :

```bash
python3 verifier.py 03
```

Attendu : **3 ventes** — S012, S013, S014 — et **1 changement de boutique**. Le lot contient une vente déjà connue et deux nouvelles ventes ; les trois lignes ne sont donc pas toutes à ajouter. NBE passe de Cap Bon à Grand Tunis le 8 janvier.

Expliquez la différence entre « trois ventes extraites » et « trois ventes ajoutées ». Retrouvez dans `preuve_source` la requête et ses paramètres : une lecture SQL réelle ne se remplace pas par une liste écrite à la main.
