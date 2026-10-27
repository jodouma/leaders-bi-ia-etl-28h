---
name: revoir-bi
description: Relire en lecture seule un petit projet BI Atlas pour vérifier ses règles de données, ses totaux et son modèle de ventes avec des preuves.
---

Lis le contrat et les fichiers de la mission avant de conclure. Reste en lecture
seule : aucune correction, aucun chargement qui écrit dans une base, aucun export.

Selon la question, vérifie les données (doublons, rejets, quantités, montants en
millimes) ou le modèle (une ligne de fait, clés, dimensions avant faits, version
de boutique à la date de vente). Pour l'incrémental, cherche une preuve de relance
sans double comptage. Pour l'historique, vérifie les bornes [debut, fin) et le passé.

Rapporte au maximum trois défauts utiles. Pour chacun : fichier, règle violée,
exemple observable et correction proposée. Sépare défaut établi et contrôle non
réalisé. Si tu ne peux pas vérifier, dis ce qui manque. N'invente aucun défaut
pour remplir la liste et ne déclare pas tout correct sans preuve.
