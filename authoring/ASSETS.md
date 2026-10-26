# Provenance et reconstruction

- `assets/leaders-logo.jpeg` : copie inchangée du fichier `logo.jpeg` fourni par Youssef Douma à la racine du projet Leaders, le 26 octobre 2026. Le logo reste soumis aux droits de son titulaire ; il n’implique pas une validation institutionnelle du programme.
- `assets/fonts/` : Inter Regular/Bold et Plus Jakarta Sans ExtraBold issus du kit personnel `leaders-pdf-design`. Les licences OFL sont fournies à côté des polices.
- Textes, exemples et schémas : construits pour ce parcours académique. Données entièrement fictives ; aucun fichier d’étudiant.
- `build_pdfs.py` : générateur autonome ReportLab ; pagination, signets et rapport des limites des blocs. Les sources de contenu sont les quatre fichiers JSON voisins.
- `slides.json`, `build_slides.js` et `README_slides.md` : contenu et générateur de la présentation ; consulter ce README pour les dépendances d’édition.

Pour reconstruire les PDF : Python 3.10 ou ultérieur, environnement virtuel séparé, puis `python -m pip install -r authoring/requirements.txt` et `python authoring/build_pdfs.py`. L’exécution des travaux pratiques ne nécessite aucune de ces dépendances.

La date imprimée identifie cette édition ; elle ne constitue pas une mesure du temps nécessaire aux étudiants.
