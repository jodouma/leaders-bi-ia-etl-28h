# IA, Codex et BI — votre première mission chez Solen Digital

**22 h en présence · 5 séances de 4 h + soutenance de 2 h · ≈ 8 h de travail personnel · licence Business Intelligence · grands débutants · binômes · français.**

Vous venez d'être recrutés à deux chez **Solen Digital**, société de services numériques (fictive). Son client **Maison Zitouna**, un petit réseau de boutiques (fictif), demande : « nos ventes montent, mais où passe la marge ? » Vous construisez la réponse avec **Codex**, vous la prouvez avec des contrôles, vous la livrez dans une application locale et dans **Power BI**, puis vous la défendez devant un jury.

**CSV + Excel + JSON + base SQL → nettoyage Python → entrepôt en étoile → application locale et Power BI → décision.**

Règle d'or : **aucune ligne de code à la main.** Codex écrit Python, SQL, DAX, tests et CI. Vous rédigez les demandes, lisez les changements, exécutez les contrôles, expliquez les résultats, décidez — et vous pratiquez Git et GitHub vous-mêmes.

## Commencer : A → B → C

1. **A — Lire et installer.** Ouvrir [00_lire_moi.pdf](pdf/00_lire_moi.pdf) (8 pages), puis [01_demarrer.pdf](pdf/01_demarrer.pdf) : Windows avec WSL2 Ubuntu, ou Ubuntu ; Python ; l'application Codex avec un compte Free ; deux comptes GitHub ; le dépôt du binôme créé à partir de [modele-binome/](modele-binome/).
2. **B — Tronc commun (séances 1 à 4).** Suivre [02_tronc_commun.pdf](pdf/02_tronc_commun.pdf) sur la mission d'entraînement *Solen Commerce 360*. Garder [03_diriger_codex_et_git.pdf](pdf/03_diriger_codex_et_git.pdf) et [06_aide_memoire.pdf](pdf/06_aide_memoire.pdf) ouverts.
3. **C — Votre mission du catalogue (fin de séance 3 → soutenance).** Choisir une des dix missions dans [04_catalogue_missions.pdf](pdf/04_catalogue_missions.pdf) et son guide dans [pdf/missions/](pdf/missions/). Livrer et préparer la soutenance avec [05_livrer_soutenir.pdf](pdf/05_livrer_soutenir.pdf).

Pour récupérer le cours : bouton **Code → Download ZIP**, ou `git clone https://github.com/jodouma/leaders-bi-ia-etl-28h.git ~/cours-bi` dans le terminal Ubuntu. Le nom historique du dépôt (`28h`) ne correspond pas à la durée de cette édition ; la durée fait foi dans les livrets.

[Le parcours en images](docs/DEMARRER_EN_IMAGES.md) · [Présentation PowerPoint modifiable](presentation/Solen_CODEX_BI_22h.pptx) · [Présentation PDF](presentation/Solen_CODEX_BI_22h.pdf)

## Cinq séances, une mission, une soutenance

| Séance | Épisode Solen | Preuve visible à la fin |
|---|---|---|
| S1 · 4 h | La demande de la direction, le cadrage, les outils | Dépôt du binôme créé, partenaire invité, première pull request relue et fusionnée ; échantillon calculé à la main |
| S2 · 4 h | Un premier résultat rassurant… et faux | Sources lues avec pandas ; lignes acceptées et rejetées = référence ; correction après revue |
| S3 · 4 h | La base opérationnelle des retours et l'étoile | Entrepôt en étoile chargé ; faits reliés aux dimensions ; choix de la mission du catalogue |
| S4 · 4 h | Le besoin change : nouveau lot, une boutique change de zone | Incrément, historique SCD2 préservé, rejeu sans doublon, tests et CI verts, conflit résolu |
| S5 · 4 h | Livrer | Application locale et rapport Power BI actualisé ; recommandation ; répétition |
| Perso · ≈ 8 h | La mission du catalogue | Dépôt du binôme complet avec les preuves individuelles |
| Soutenance · 2 h | Démonstration et questions individuelles | Compréhension métier, maîtrise du workflow, justification des résultats |

Chaque séance alterne environ 30 % d'explications et 70 % de pratique hors pauses. Les durées sont des estimations de conception, à confirmer par un essai humain.

## Le dépôt, dossier par dossier

| Dossier | Rôle |
|---|---|
| `pdf/` | Les sept livrets étudiants (00 → 06) et les dix guides de mission dans `pdf/missions/` |
| `modele-binome/` | **Le modèle du dépôt de chaque binôme** : données du tronc commun et des dix missions, cahiers des charges, valeurs de référence, contrôles, consignes Codex (`AGENTS.md`, `.agents/skills/`), CI, guide Power BI |
| `prompts/` | Dix-huit demandes prêtes à adapter : cadrage, plan, implémentation, erreur, revue, correction, PR, explication… |
| `aide-memoire/` | L'aide-mémoire Git · Codex · BI (source du livret 06) |
| `presentation/` | La présentation PowerPoint et son PDF |
| `docs/` | Le parcours en images, les sources officielles vérifiées, les schémas et les captures réelles avec leur registre |
| `authoring/` | Les sources des livrets, des diapositives, des schémas et des **générateurs de données** ; instructions de reconstruction |

Les données sont entièrement synthétiques et reproductibles : les générateurs calculent aussi les valeurs de référence depuis la vérité terrain, indépendamment de tout code de solution. Les solutions, les lots d'évaluation et le guide du jury restent hors de ce dépôt.

## Ce qui est gratuit, ce qui est libre

Python, pandas, SQLite, Git et les générateurs sont libres. **Codex** (compte ChatGPT Free, application de bureau) et **Power BI Desktop** (Windows) sont des logiciels propriétaires utilisables gratuitement dans le cadre décrit ; leur accès gratuit dépend de leur éditeur. Le cours ne demande ni carte bancaire, ni abonnement, ni clé API. Sur GitHub Free, les protections de branche et les revues requises existent sur les dépôts **publics** : le dépôt du binôme est public et ne contient que des données synthétiques.

L'offre Free annonce, à la date de vérification du 28 octobre 2026, **GPT-6 Luna à vitesse Standard dans l'application de bureau, sous réserve de déploiement**. Le CLI Codex n'est pas un prérequis. Chaque étudiant vérifie sur son compte le modèle, l'effort et l'usage réellement affichés ; le livret 01 détaille ce qui est annoncé et ce qui reste à vérifier.

Pour essayer le cours depuis zéro : [TESTER_LE_COURS.md](TESTER_LE_COURS.md). Pour reconstruire les documents et les données : [authoring/README.md](authoring/README.md).

Youssef Douma · Leaders University · édition du 28 octobre 2026 · noms, entreprises et données fictifs
