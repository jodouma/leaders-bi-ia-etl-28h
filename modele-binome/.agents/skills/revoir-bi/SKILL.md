---
name: revoir-bi
description: Relire en lecture seule le pipeline BI Solen de ce dépôt (règles de nettoyage, totaux, modèle en étoile, SCD2, rejeu, exports) et rapporter au plus trois défauts établis avec preuve, séparés des contrôles non réalisés.
---

Lecture seule stricte : aucune modification de fichier, aucun chargement qui
écrit dans `outputs/`, aucun commit. Tu peux lire le code, les sources, le
cahier des charges, et lancer des lectures (`git diff`, `sqlite3` en lecture,
`python -m controles.verifier` si la sortie existe déjà).

1. Lis `mission.txt`, le cahier des charges et le dictionnaire de la mission,
   puis le diff de la branche (`git diff main...HEAD`) et les fichiers touchés.
2. Selon la question, vérifie :
   - **Données** : doublons exacts gardés une fois ; `id_conflit`, `id_manquant`,
     `cle_inconnue`, `quantite_invalide` rejetés avec motif ; formats décimaux et
     dates normalisés ; montants en millimes entiers ; sources intactes.
   - **Totaux** : une somme recalculée à la main sur l'échantillon, puis
     comparée à `manifest.json` ou à la référence.
   - **Modèle** : grain du fait respecté ; dimensions avant faits ; clés `*_key`
     uniques côté dimension ; SQL paramétré.
   - **SCD2** : `valid_from` inclus, `valid_to` exclu, une seule version courante
     (`NULL`) ; un fait de part et d'autre de la date de changement pointe vers la
     bonne version.
   - **Rejeu** : relancer `increment` n'ajoute aucune ligne (comptes avant/après).
3. Rapporte **au maximum trois défauts établis**. Pour chacun :
   fichier et ligne · règle violée · exemple observable (valeur, ligne, compte) ·
   correction proposée en une phrase.
4. Puis une rubrique séparée **« Contrôles non réalisés »** : ce que tu n'as pas pu
   vérifier et ce qui manque pour le faire.

N'invente aucun défaut pour remplir la liste. Ne déclare jamais « tout est
correct » : écris « aucun défaut établi par cette lecture » et ce qui a été lu.
