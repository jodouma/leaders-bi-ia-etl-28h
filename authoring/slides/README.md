# Présentation Atlas · Codex et BI · 15 h

[Retour au cours](../../README.md)

84 diapositives françaises au format 16:9. Le parcours suit cinq séances de 180 minutes : prendre en main Codex, fiabiliser les ventes, charger et garder l’histoire, construire le rapport Power BI, puis réparer et défendre la livraison. Les pauses et les temps de pratique font partie de la navigation.

Les fichiers courants sont `presentation/Atlas_CODEX_BI_15h.pptx` et `presentation/Atlas_CODEX_BI_15h.pdf`. Le PDF est une conversion du même PPTX. Les titres, consignes, tableaux, chiffres, graphique par zone et modèle en étoile sont éditables dans PowerPoint. Les schémas du kit visuel sont insérés en PNG ; leurs sources vectorielles et leur générateur restent dans `authoring/visuals/` et `docs/images/diagrams/`.

## Reconstruire

Dépendances d’édition : Node.js 18 ou plus récent, `pptxgenjs` 4.0.1 et Python 3. Depuis la racine du cours :

```sh
npm install --prefix authoring/slides
python3 authoring/slides/make_content.py
node authoring/slides/build_slides.js
```

`slides.json` est la source de contenu. `make_content.py` valide la structure, les cinq pauses, les cinq horaires et le graphique des zones ; il ne remplace pas le contenu. Le générateur écrit le PPTX et le manifeste de zones de texte `layout_manifest.json`.

Les chemins sont résolus depuis le dossier du générateur. `ATLAS_ASSET_ROOT` peut désigner une autre copie complète du cours pour l’assemblage ; il n’est pas nécessaire aux étudiants. Un schéma ou une capture manquants font échouer la construction. Aucun téléchargement ni appel IA ne fait partie du build.

Exporter le PPTX en PDF dans PowerPoint ou LibreOffice après chaque modification. Les scripts d’auteur ne sont pas des prérequis pour suivre le cours. Inspecter le PDF régénéré, pas une ancienne conversion.

## Sources et provenance

Thème Leaders : navy/orange, logo carré fourni par Youssef Douma, proportions conservées. Arial et Courier New pour les objets PowerPoint ; Inter et Plus Jakarta Sans dans les schémas, avec notices OFL du kit visuel. Les schémas représentent des concepts, pas des captures d’interfaces. Les montants sont issus du contrat Atlas V6 et du cas fictif.

État documentaire : 27 octobre 2026. Les liens de la dernière diapositive sont cliquables et les notes conservent le contexte des affirmations.

- [Application Codex](https://learn.chatgpt.com/docs/app), [offre Free](https://learn.chatgpt.com/docs/pricing), [modèles et réflexion](https://learn.chatgpt.com/docs/models).
- [Application Windows et agent WSL2](https://learn.chatgpt.com/docs/app/windows), [application Ubuntu en preview](https://learn.chatgpt.com/docs/linux/linux-app).
- [Instructions AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Skills locaux](https://learn.chatgpt.com/docs/build-skills), [sous-agents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
- Pour Power BI, les références Microsoft et la procédure complète figurent dans [le kit du rapport](../../powerbi/README.md).

L’offre documentée Free annonce Luna à vitesse Standard sous déploiement. Standard est une vitesse, pas un effort de réflexion. High est conseillé pour Luna si ce réglage est visible ; Luna ne propose pas Ultra. Chaque étudiant relève les choix réellement affichés. La présence d’une documentation ne prouve pas l’accès d’un compte Free, la découverte d’un Skill ou l’exécution de sous-agents sur ce compte.

La route Windows distingue l’application hôte, l’agent Ubuntu/WSL2 et Power BI Desktop sur Windows. La route Ubuntu utilise l’ETL natif et un transfert réel vers un poste Windows pour Power BI. Le cours ne requiert pas de CLI, clé API, achat ou publication cloud.

## Vérification de cette édition

Le PPTX a été construit depuis `slides.json`, validé avec le vérificateur OOXML de la compétence PPTX et converti en PDF par LibreOffice sur macOS. Les 84 pages ont été rendues, relues en planches et contrôlées pour les calculs, unités, consignes et temps. Les schémas ont été agrandis après le premier rendu ; la conversion TND et les libellés trop longs ont été corrigés. Le graphique natif totalise 43,500 + 72,000 = 115,500 TND. La fonction de normalisation et les deux SELECT extraits du PDF ont été exécutés : codes NBE/TUN attendus, entrées None/0/False refusées, et trois ventes SQL plus un changement de zone attendus. Aucun bloc de texte extrait ne dépasse les limites d’une page ; les liens de sources et de navigation sont présents dans le PDF. Les sources officielles sont conservées en notes et sur la page de références.

La revue a aussi corrigé l’ordre de S3 : chargement initial 04, recherche temporelle 05 sur un cas isolé, puis incrément/rejeu 06. Les deux extractions SQL ont des diapositives distinctes et correspondent chacune à leur résultat. Le travail Codex garde `AGENTS.md` et les Skills à la racine du cours ; le terminal exécute les scripts dans `atelier/`. Les pages modifiées ont été rendues et relues après correction.

Ces contrôles d’édition ne constituent pas un essai d’installation Windows/Ubuntu, un test d’accès Free étudiant, une manipulation Power BI sur Windows ou un pilote humain chronométré. Les horaires restent des estimations de conception. Les preuves de manipulation réelle se conservent séparément dans le journal de travail.
