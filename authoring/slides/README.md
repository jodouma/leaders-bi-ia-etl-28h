# Présentation Atlas BI avec l’IA — 28 h

62 diapositives françaises, 16:9, avec texte et schémas PowerPoint éditables, deux graphiques PowerPoint natifs et le logo fourni par Youssef Douma. Le PDF est une conversion du PPTX.

## Reconstruire

Dépendance : Node.js 18 ou plus récent et `pptxgenjs` 4.0.1. Depuis la racine du cours :

```sh
npm install --prefix authoring/slides
node authoring/slides/build_slides.js
```

Le générateur lit `slides.json` et écrit `presentation/Atlas_BI_IA_28h.pptx`. Le fichier `layout_manifest.json` conserve les zones de texte pour la vérification. Les chemins sont relatifs au générateur : le lancement fonctionne depuis un autre dossier.

Pour modifier le contenu : éditer `slides.json`, puis relancer le générateur. `make_content.py` est une source structurée facultative qui régénère ce JSON avec Python standard ; ne pas le relancer après une modification directe du JSON sans y reporter la modification.

Pour obtenir le PDF, utiliser LibreOffice avec un profil temporaire distinct, ou la commande Exporter au format PDF de PowerPoint. Le PDF doit être reconverti après chaque changement du PPTX, puis vérifié visuellement.

## Provenance et repères

Thème adapté du générateur de la première édition Atlas, palette Leaders approuvée (navy / orange), Arial et Courier New. `assets/leaders-logo.jpeg` est le logo carré fourni par l’utilisateur ; ses proportions sont conservées. Aucun écran d’installation reconstitué et aucune marque tierce utilisée comme caution.

Les notes de diapositives contiennent les sources publiques relatives à Docker, Python, SQLite et aux accès IA. Les valeurs Atlas et CampusBox suivent les fichiers du cours. L’exemple fautif 6 000 / 13 500 est construit pour l’enseignement : il ne représente pas une sortie observée d’un produit gratuit.

Le socle emploie le chat web et Python standard. Une CLI IA reste facultative et exige un compte déjà éligible ; aucune gratuité CLI ou fonctionnalité payante n’est promise. Les conditions d’accès peuvent changer.
