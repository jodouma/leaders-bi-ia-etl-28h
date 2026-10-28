# Prompts prêts à adapter — Solen BI 22 h

Ces demandes servent dans **votre dépôt binôme**, ouvert comme projet dans
l'application Codex. Vous ne tapez jamais de code : vous adaptez une demande,
Codex écrit, vous contrôlez.

## La méthode, à chaque demande

1. **Prévoir** : avant d'envoyer, notez la valeur ou le résultat attendu
   (chaque fiche vous dit quoi prévoir).
2. **Adapter** : remplacez chaque `<…>` par votre cas réel. Une demande qui garde
   des `<…>` n'est pas prête.
3. **Envoyer** une seule petite étape.
4. **Contrôler** : relancez vous-même la commande dans le terminal ; comparez
   avec votre prévision.
5. **Lire le diff** (`git diff`) et **expliquer** à votre binôme les lignes clés.
6. **Décider** : garder, demander une correction, ou refuser.

Chaque fiche contient : quand l'utiliser, la demande, ce qu'il faut vérifier dans
la réponse, et deux erreurs fréquentes.

## Les fiches

| Séance | Fiche | Preuve attendue |
|---|---|---|
| S1 | [01 — Cadrer les indicateurs](01-cadrage.md) | indicateurs avec unité ; calcul à la main = `attendu.md` |
| S1 → S5 | [02 — Plan court](02-plan-court.md) | 3 à 5 étapes, une preuve chacune |
| S2 → S5 | [03 — Réaliser une petite étape](03-implementer-petite-etape.md) | contrôle relancé ; diff lu |
| S2 | [04 — Lire CSV, Excel, JSON](04-lire-csv-excel-json.md) | comptes de lignes = vos comptes |
| S2 | [05 — Nettoyer et rejeter](05-nettoyer-et-rejeter.md) | `outputs/rejets.csv` ; rejets par motif = référence |
| S3 | [06 — SQL paramétré](06-sql-parametre.md) | requête avec `?` ; compte d'un mois |
| S3 | [07 — Charger l'étoile](07-charger-etoile.md) | `--etape initial` OK |
| S4 | [08 — Incrément, SCD2, rejeu](08-incrementer-scd2-rejeu.md) | `--etape increment` et `--etape rejeu` OK |
| S4 | [09 — Tests et CI](09-tests-et-ci.md) | `pytest -q` vert ; CI verte sur la PR |
| toujours | [10 — Erreur](10-erreur.md) | diagnostic avant correction |
| S2 → S5 | [11 — Revue en lecture seule](11-revue-lecture-seule.md) | ≤ 3 défauts établis, contrôles non réalisés séparés |
| S2 → S5 | [12 — Corriger après revue](12-corriger-apres-revue.md) | défaut corrigé, deuxième revue |
| chaque PR | [13 — Préparer la PR](13-preparer-pr.md) | liste OK ; titre et description ; relecteur nommé |
| S5, soutenance | [14 — Expliquer un résultat](14-expliquer-resultat.md) | une ligne suivie jusqu'au graphique |
| S4 | [15 — Résoudre un conflit](15-resoudre-conflit.md) | plus aucun marqueur ; contrôles verts |
| fin de séance | [16 — Note d'état et reprise](16-reprendre.md) | note de 8 lignes vérifiée |
| S4, facultatif | [17 — Skill local](17-skill-local.md) | votre Skill, une règle, un effet observé |
| mission catalogue | [18 — Variation métier](18-variation-metier.md) | impact mesuré ; test de la variante |

**Fin de S4 — passer à votre mission** : livret 04, « Passer à votre mission » (livraison
du tronc commun dans `livraison/`, `outputs/` vidé, `mission.txt`, code généralisé).
**S5 — application locale de votre mission** : fiche 02 puis 03, avec la demande complète
du livret 05, partie 1 (trois écrans, filtres, journal des chargements).
**S5 — Power BI** : suivez `powerbi/README.md` sur la livraison du tronc commun
(`powerbi/mesures.dax`). Pour votre mission, demandez à Codex `powerbi/mesures_<Mxx>.dax`
(étape C du guide).

## Les commandes que vous lancez vous-même

```bash
source .venv/bin/activate          # à chaque nouveau terminal
python -m solen sources            # S2 : lire les sources, sans rien charger
python -m solen initial            # puis increment, export, app, quand Codex les a créées
python -m controles.verifier --mission $(cat mission.txt) --etape initial
                                   # étapes : rejets|initial|increment|rejeu|export|app|tout
                                   # rejeu : increment, --etape increment, increment, --etape rejeu
pytest controles                   # tests fournis
pytest -q                          # tous les tests, y compris les vôtres
```

Et pour Git : `git switch`, `git pull`, `git status`, `git diff`, `git add`,
`git commit`, `git push` (voir `03_diriger_codex_et_git.pdf`).

## Réglages Codex Free

Application de bureau Codex, modèle **GPT-6 Luna**. Effort visible : Light, Medium,
High, Extra High — **commencez par High** (recommandation officielle pour Luna).
« Standard » est la vitesse, pas l'effort. Le CLI est facultatif. Aucune durée
d'usage n'est garantie : si le quota bloque, continuez les actions locales
(contrôles, lecture du diff, calcul à la main) et attendez le reset affiché, sans
achat. Les sous-agents, s'ils sont disponibles, permettent « deux lectures
indépendantes » en revue ; sans eux, deux conversations successives suffisent.
[Offre](https://learn.chatgpt.com/docs/pricing), [modèles](https://learn.chatgpt.com/docs/models).

## Ce que Codex ne fait pas à votre place

`git commit`, `git push`, ouvrir ou fusionner une PR, écrire votre revue GitHub,
modifier les sources, les références ou `controles/`. Si une réponse le propose,
refusez et reformulez.
