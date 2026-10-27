# Visuels Atlas — V5

Les six schémas sont originaux, en français. Aucun ne simule une interface logicielle. Les SVG contiennent des glyphes vectorisés ; les PNG haute résolution utilisent les mêmes positions et les mêmes fontes du kit Leaders. La palette est `#2B3180`, `#07152F`, `#FF9A3C`.

## Reproduire

Depuis la racine du dépôt, avec Python, Pillow et fontTools :

```sh
python authoring/visuals/generate.py
```

Le script résout ses chemins par rapport à son emplacement. Il ne modifie aucun CSV. Il vérifie les comptes et les périodes réelles des données publiques, calcule les montants en millimes entiers, simule le rejeu par identifiant et refuse une différence avec le contrat. Il rejette aussi les textes sortant du canevas. L’inspection visuelle complète ce contrôle de bornes.

Pour produire une planche de contrôle dans un dossier privé :

```sh
python authoring/visuals/generate.py --contact-sheet /chemin/prive/contact-sheet.png
```

## Fichiers et intégration

Chaque nom correspond à `docs/images/diagrams/<nom>.svg` et `.png`. Depuis les JSON d’`authoring/content/`, le renderer PDF utilise `path: "../docs/images/diagrams/<nom>.png"` (sa racine est `authoring/`). Les SVG sont destinés au web ou à une composition vectorielle ; les blocs `figure` du renderer actuel attendent un PNG.

| Nom | Canevas SVG | Utilisation / légende proposée |
| --- | --- | --- |
| `parcours-a-e` | 1600 × 540 | A→E : comprendre, préparer, construire, contrôler puis réutiliser la méthode. |
| `trois-espaces` | 1600 × 700 | Écrire dans l’éditeur, exécuter dans le terminal, consulter dans le navigateur. |
| `poste-docker` | 1600 × 820 | Compose monte le dossier du cours sous `/workspace` ; Python travaille dans `/workspace/projet`. Les résultats restent accessibles sur le PC. |
| `boucle-ia` | 1600 × 620 | Une petite fonction, un résultat exécuté et une preuve avant de poursuivre. |
| `etl-qualite` | 1600 × 780 | Lot initial : 16 lignes = 12 retenues + 1 doublon + 3 rejets. Grain : une vente élémentaire. |
| `ca-ajout-rejeu` | 1600 × 780 | CA chargé : 99,000 TND, puis 115,500 TND après ajout et après rejeu. Les périodes différentes sont indiquées. |

Les PNG mesurent 2400 px de large (1,5 × le canevas). Pour un livret A4, les utiliser sur toute la largeur utile, avec une hauteur autorisée adaptée au rapport largeur/hauteur. Ne pas les réduire à une vignette. Le schéma étoile natif déjà présent dans le cours est conservé ; un deuxième schéma étoile apporterait une répétition sans bénéfice.

## Provenance et licences

`manifest.json` fournit les descriptions alternatives, dimensions, sources, assertions et SHA-256 des CSV. Les seules polices utilisées sont celles du kit existant :

- `authoring/assets/fonts/Inter-400.ttf`, `Inter-700.ttf` — notice `authoring/assets/fonts/Inter-OFL.txt`.
- `authoring/assets/fonts/PlusJakartaSans-800.ttf` — notice `authoring/assets/fonts/PlusJakartaSans-OFL.txt`.

Conserver ces notices avec les sources du cours redistribuées. Aucun logo tiers ni capture d’écran n’entre dans ces illustrations. Les nombres monétaires à trois décimales représentent des TND, pas des milliers de TND. L’axe du graphique part de zéro. Le passage de 99,000 à 115,500 étend le cumul du 5–7 au 5–8 janvier 2026 ; il ne compare pas une performance sur des périodes égales.
