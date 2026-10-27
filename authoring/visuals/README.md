# Visuels Atlas — V6 · cours de 15 h

Quatorze schémas originaux en français, au style Leaders : blanc, navy, orange, Inter et Plus Jakarta Sans. Aucun ne simule une interface ou une capture logicielle. Les SVG utilisent des glyphes en contours ; les PNG de 2400 px de large utilisent les mêmes positions et fontes. Chaque schéma doit occuper la largeur utile du PDF ou une grande partie de la diapositive, sans déformation.

## Régénération

Avec Python 3, Pillow et fontTools :

```sh
python3 authoring/visuals/generate.py
python3 authoring/visuals/generate.py --contact-sheet /tmp/atlas-v6-contact.png
```

Le script résout les chemins depuis son propre emplacement, vérifie les bornes de texte du canevas et les blocs de texte, puis génère les PNG, SVG et le manifeste. `--only v6-etoile v6-scd2` limite les fichiers image régénérés ; le manifeste décrit toujours toute la bibliothèque.

Sur le poste auteur, la génération vérifiée a utilisé Python 3.12 fourni par Codex, Pillow du venv de préparation des slides et fontTools du venv Leaders existant. Aucun paquet ni service de télémétrie n'a été installé ou contacté.

## Intégration

Chaque nom ci-dessous correspond à `docs/images/diagrams/<nom>.png` et `.svg`. Le PDF actuel attend le PNG avec `path: "../docs/images/diagrams/<nom>.png"` depuis `authoring/content/`. Le manifeste contient dimensions, descriptions alternatives, palette et provenance.

| Nom | Sujet |
| --- | --- |
| `v6-pipeline` | CSV + extraction SQL réelle → nettoyage → entrepôt → quatre CSV → Power BI. |
| `v6-postes-wsl` | Codex hôte Windows / agent WSL ; Ubuntu natif ; transfert vers Power BI Windows. |
| `v6-codex-boucle` | Planifier, modifier petit, exécuter localement, revoir et corriger. |
| `v6-dossiers` | Dossier distribué et copie `atelier/` créée par le jalon 01 ; données et sorties dans cette copie. |
| `v6-etoile` | Trois dimensions et trois relations actives 1:* ; relation Boutique par `shop_key`. |
| `v6-scd2` | NBE : Cap Bon jusqu'au 8 janvier exclu ; Grand Tunis dès le 8 inclus ; anciennes clés stables. |
| `v6-chiffres-zones` | Barres à échelle exacte : 43,500 et 72,000 TND ; Grand Tunis combine 67,500 + 4,500. |
| `v6-millimes` | Entiers dans l'entrepôt ; division par 1000 pour présenter les TND. |
| `v6-contexte-quota` | Contexte/tokens et limite d'usage ; seulement les indicateurs réellement affichés. |
| `v6-modele-effort` | Modèle, effort de raisonnement et vitesse Standard, sans coût ou disponibilité inventés. |
| `v6-revue` | Deux lecteurs sur des cibles distinctes, un auteur ; repli séquentiel si nécessaire. |
| `v6-parcours` | Cinq séances de trois heures, pauses comprises ; cinq résultats visibles. |
| `v6-qualite` | 16 lignes = 12 retenues + 1 doublon + 3 rejets. |
| `v6-ajout-rejeu` | Initial 12 faits, puis 14 après ajout ; rejeu stable à 14. |

## Chiffres et provenance

`v6-data.json` est l'extrait public des valeurs attendues du contrat V6 figé. Il conserve son SHA-256 de provenance. Les assertions vérifient les totaux, le partage par zone et version de boutique, le diviseur monétaire et les comptes du rejeu. Le graphique calcule toutes ses longueurs depuis ces valeurs. Les valeurs attendues du contrat ne constituent pas une preuve d'exécution ETL ou Power BI.

La répartition finale attendue est 14 faits, 35 unités et 115 500 millimes. Cap Bon reçoit 43 500 ; Grand Tunis reçoit 67 500 (TUN) + 4 500 (NBE dès le changement) = 72 000 millimes. Les nombres à trois décimales représentent des TND, jamais des milliers de TND. L'axe commence à zéro. L'exemple monétaire 2 × 4 500 = 9 000 est une illustration explicite de la conversion, distincte de ces totaux.

Les mentions Free/modèle reprennent le plan pédagogique daté du 27 octobre 2026 ; elles demandent de vérifier le compte et le poste réels. Aucun quota, coût, nombre de tokens ou accès Free n'est simulé.

## Vérification et licences

Les 14 PNG ont été inspectés individuellement, puis en planche : accents, contraste, bords, texte, unités, flèches, cardinalités, fin de validité exclue et dates. Les limites de carte sont vérifiées par le générateur ; l'inspection a corrigé plusieurs retours de ligne. L'intégration finale aux PDF et slides reste à inspecter à leur taille réelle par leurs auteurs.

Le dépôt courant conserve uniquement les quatorze schémas V6 utilisés par cette édition.

Polices : `authoring/assets/fonts/Inter-400.ttf`, `Inter-700.ttf` et `PlusJakartaSans-800.ttf`. Conserver `Inter-OFL.txt` et `PlusJakartaSans-OFL.txt` avec les sources redistribuées. Illustrations originales ; fontes sous SIL OFL 1.1 ; aucun logo tiers ou élément d'interface repris.
