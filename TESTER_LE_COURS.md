# Essayer le cours depuis zéro

[Retour au départ](README.md)

Suivre les livrets comme un binôme débutant, sans préparer les réponses. Conserver la première tentative avant de consulter une quelconque aide. Noter l'édition, le système, le compte et les étapes réellement essayées.

1. **Poste neuf.** Télécharger le ZIP ou cloner le cours dans `~/cours-bi`. Suivre `pdf/01_demarrer.pdf` : Windows avec WSL2 Ubuntu, ou Ubuntu pris en charge. Noter où se trouvent les fichiers et dans quel terminal se tapent les commandes.
2. **Codex avec un compte Free.** Vérifier l'accès effectif, le modèle, les efforts et l'usage affichés ; aucun identifiant ni secret dans les notes. Un essai avec un autre abonnement ne prouve pas l'accès Free.
3. **Deux comptes, deux copies.** A crée le dépôt public du binôme à partir de `modele-binome/`, invite B ; chacun clone dans `~/solen-bi`. Réaliser le premier cycle : branche, commit, push, PR, revue de l'autre, merge, pull des deux côtés.
4. **Tronc commun.** Suivre `pdf/02_tronc_commun.pdf` séance par séance. Calculer l'échantillon à la main avant toute demande à Codex. Conserver les demandes et les diffs. Les contrôles `python -m controles.verifier --mission tronc-commun --etape initial|increment|rejeu|export|app|tout` doivent devenir verts dans l'ordre ; relever chaque ÉCHEC avec son message exact.
5. **Historique et rejeu.** Prouver que NBE change de zone le 2026-07-15 sans réécrire le passé, et qu'une seconde exécution de l'incrément n'ajoute aucune ligne.
6. **Application et Power BI.** Ouvrir `outputs/app/index.html`, vérifier un chiffre filtré contre la référence. Sur un poste Windows, suivre `modele-binome/powerbi/README.md` : types, six relations, cinq mesures, un filtre, une actualisation après l'incrément. Un rapport HTML ne remplace pas cette manipulation.
7. **Mission du catalogue.** Choisir une mission dans `pdf/04_catalogue_missions.pdf`, suivre son guide, atteindre `--etape tout --strict` vert et la CI verte.
8. **Quota ou panne.** Essayer la reprise prévue quand Codex est indisponible : Git, revue, interprétation, préparation de la prochaine demande.

Pour chaque blocage, noter :

```text
Édition du cours :
Système et version :
Compte Free vérifié : oui / non ; modèle, effort, vitesse affichés :
Étape (livret, page) et action :
Résultat attendu :
Résultat observé / message exact :
Capture disponible (sans donnée personnelle) :
Aide nécessaire pour reprendre :
Temps approximatif :
Mot ou instruction difficile :
```

Terminer par ce qui est clair, ce qui bloque et la première amélioration utile. Un essai partiel est utile si son périmètre est précis ; un seul écran ne prouve pas que tout fonctionne.
