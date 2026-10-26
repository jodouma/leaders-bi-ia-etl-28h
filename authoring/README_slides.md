# Reconstruire la présentation Atlas

Le fichier `slides.json` contient le contenu éditable des **52 diapositives**. `build_slides.js` produit la présentation PowerPoint avec des textes, tableaux, diagrammes et un graphique natifs, modifiables dans PowerPoint ou LibreOffice Impress.

## Reconstruction

Installer Node.js 18 ou plus récent et, depuis la racine du dépôt :

```text
npm install --prefix authoring
node authoring/build_slides.js
```

Le résultat est `presentation/Atlas_ETL_28h.pptx`. Aucune dépendance Node.js n’est nécessaire pour suivre les exercices Python du cours.

Pour produire aussi le PDF, ouvrir le PPTX dans PowerPoint et choisir **Fichier → Exporter → Créer un document PDF**, ou utiliser LibreOffice :

```text
soffice --headless --convert-to pdf --outdir presentation presentation/Atlas_ETL_28h.pptx
```

Le PDF fourni a été produit par LibreOffice sur macOS. Une modification du PPTX impose de refaire le PDF pour que les deux versions concordent.

## Sources et identité visuelle

- Logo : copie du fichier `logo.jpeg` fourni par Youssef Douma dans le dossier principal du projet, le 26 octobre 2026 ; proportions conservées. Ce fichier n’est pas un téléchargement officiel indépendant.
- Données : scénario pédagogique fictif Atlas Papeterie ; aucune donnée personnelle.
- Graphique : ventes initiales du 5 au 7 janvier 2026, avant l’ajout incrémental. Carnet : 22.500 ; Stylo : 18.000 ; Classeur : 36.000 ; Surligneur : 22.500 TND. Total : 99.000 TND.
- Références techniques : [Thonny](https://thonny.org/), [Python CSV](https://docs.python.org/3/library/csv.html), [Python Decimal](https://docs.python.org/3/library/decimal.html), [SQLite SELECT](https://www.sqlite.org/lang_select.html).
- Les notes de certaines diapositives précisent les sources et le statut des exemples illustratifs.

Le graphique initial et les indicateurs après ajout couvrent des périodes différentes : garder leurs libellés de période lors d’une adaptation.
