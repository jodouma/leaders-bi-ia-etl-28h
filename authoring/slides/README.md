# Présentation Atlas BI avec l’IA — 28 h

[Retour à la maintenance](../README.md) · [Retour au cours](../../README.md)

65 diapositives françaises, 16:9. Navigation commune A → E, schémas et graphiques PowerPoint natifs éditables, captures authentiques explicitement légendées. Le PDF est une conversion du même PPTX.

## Reconstruire

Dépendances : Node.js 18 ou plus récent et `pptxgenjs` 4.0.1. Depuis la racine du cours :

```sh
npm install --prefix authoring/slides
python3 authoring/slides/make_content.py
node authoring/slides/build_slides.js
```

`slides.json` est la source de contenu unique. Le modifier directement, puis relancer le générateur. `make_content.py` vérifie et reformate ce JSON sans remplacer son contenu : les modifications directes et champs supplémentaires sont conservés.

Le générateur écrit `presentation/Atlas_BI_IA_28h.pptx` et le manifeste de zones de texte `authoring/slides/layout_manifest.json`. Ses chemins sont résolus depuis son dossier, donc il fonctionne aussi depuis un autre répertoire.

Les captures sont lues dans `docs/images/real/` et `docs/images/setup/`. Le build échoue si une capture manque. Le champ `pixelSize` décrit ses dimensions réelles pour préserver ses proportions ; le mettre à jour si son cadrage change. La variable facultative `ATLAS_ASSET_ROOT` permet au poste auteur de lire ces mêmes chemins relatifs depuis une autre copie complète du cours ; elle n’est pas nécessaire aux étudiants.

Pour le PDF, exporter le PPTX dans PowerPoint ou utiliser LibreOffice avec un profil temporaire distinct. Reconvertir le PDF après toute modification et vérifier visuellement les pages concernées.

## Provenance et repères

Thème adapté de la première édition Atlas ; palette Leaders navy/orange ; Arial et Courier New. Le logo carré fourni par Youssef Douma conserve ses proportions. Les captures ne sont pas des interfaces générées.

- Dépôt GitHub et rapport Atlas : captures réelles du projet, 27 octobre 2026 ; environnement indiqué dans les légendes et notes.
- Windows Features : capture officielle Docker Docs, interface historique en anglais, explicitement non réalisée sur notre poste. Attribution : Docker, Inc. et contributeurs Docker Docs — Apache 2.0 — capture originale inchangée. Voir [les crédits visuels](../../docs/images/setup/ATTRIBUTIONS.md) et la [licence](../../docs/images/setup/LICENSE-Docker-Apache-2.0.txt).
- Docker, montage, trois espaces, boucle IA, ETL, grain et étoile : schémas pédagogiques natifs éditables. Les graphiques natifs reprennent les valeurs réelles du cas Atlas avec leurs périodes distinctes.

Les notes donnent les sources publiques relatives à Docker, Python, SQLite et aux accès IA. L’exemple fautif 6 000 / 13 500 est construit pour l’enseignement ; aucune sortie d’une offre gratuite n’est prétendue observée. Les réponses numériques de CampusBox sont réservées au corrigé.

Le socle utilise le chat web et Python standard. Une CLI IA est facultative et demande un compte déjà éligible ; aucune gratuité CLI, clé API ni fonctionnalité payante n’est requise.
