# Préparer Atlas BI avec Codex

[Retour au cours](../../README.md) · [Guide de démarrage complet](../../pdf/01_demarrer_windows_ubuntu.pdf)

Le guide 01 accompagne les manipulations depuis zéro : dossiers, ZIP, terminal, installation, connexion et première demande. Le cours dure **15 h, en cinq séances de 3 h**. Les installations sont préparées avec le professeur au début du parcours ; aucun travail d’installation caché à faire seul n’est requis.

- **Windows** : application de bureau sur Windows, agent et terminal dans **Ubuntu WSL2**. Dans les paramètres de l’application, le choix de l’agent et celui du terminal sont distincts ; le changement d’agent demande un redémarrage. Le dossier du cours reste dans `~/cours-bi`, dans Linux.
- **Ubuntu natif** : application Linux officielle en preview, Ubuntu **24.04 ou 26.04 LTS** et paquet `.deb` adapté au processeur. Python s’exécute dans ce même Ubuntu.
- **Codex gratuit** : compte personnel Free, disponibilité réelle et usage à contrôler avant la mission. Luna Standard est annoncé sous déploiement. Standard désigne la vitesse ; High est l’effort de départ conseillé pour Luna si le compte affiche ce réglage. N’inventez pas une option absente.
- **Power BI** : un vrai poste Windows avec Power BI Desktop ouvert doit être prêt avant la séance 4. Depuis Ubuntu natif, prévoyez le transfert du dossier d’export sur ce poste.

Après extraction du ZIP, la racine `~/cours-bi` contient notamment `README.md`, `AGENTS.md`, `projet/` et `outils/`. `projet/` est le modèle fourni. Ouvrez cette racine dans Codex. Le guide explique la copie dans Linux pour WSL ; ne travaillez pas dans le ZIP.

Dans le **Terminal Ubuntu**, vérifiez Python puis créez la copie de travail :

```bash
cd ~/cours-bi
python3 --version
python3 -c "import csv, sqlite3, decimal; print('OK Python')"
python3 outils/jalon.py 01 atelier
cd atelier
python3 calcul.py
python3 verifier.py 01
```

Les deux premiers contrôles doivent afficher une version Python 3 puis `OK Python`. La création du jalon annonce `Jalon 01 créé`. `calcul.py` doit afficher `2 × 4500 = 9000 millimes = 9.000 TND` ; le contrôle doit afficher `OK 01`. Si `atelier` existe déjà, conservez votre travail avant toute reprise. Ne modifiez pas les vérificateurs ou les données pour masquer une erreur.

`atelier/` contient votre copie de travail, dont `data/` et `outputs/`. Python utilise sa bibliothèque standard : aucun paquet pip n’est requis. Si `python3` manque, le guide décrit l’installation Ubuntu avec `apt` et le nouveau contrôle.

Votre première demande dans **Codex / New chat**, projet `cours-bi` :

```text
Je débute. Lis uniquement README.md et AGENTS.md,
puis liste les fichiers du dossier atelier.
Explique en français où sera mon travail en 5 phrases.
Ne modifie aucun fichier et ne lance aucune installation.
```

Comparez la réponse aux fichiers réels avant de demander un changement. Pour les missions suivantes : une tâche limitée, des fichiers précis, lecture du changement, exécution locale, puis explication de ce que vous avez observé.

Si Codex est indisponible ou si le quota est épuisé, gardez votre essai et notez l’heure de reprise affichée. Continuez avec les consignes, les indices du PDF 03, les scripts et les contrôles locaux ; reprenez Codex après le rétablissement de l’usage. Un jalon fourni peut aider à reprendre avec le professeur. Aucune quantité de messages ni durée d’inférence gratuite n’est garantie. Aucun achat ni clé API n’est demandé.

Après les missions de chargement, les commandes `python3 executer.py initial`, `increment` puis `export` produisent la livraison attendue. Depuis le dossier d’export réussi, `explorer.exe .` ouvre ses fichiers dans Windows avec WSL. Copiez **le dossier entier**, avec les quatre CSV et `manifest.json`, dans un dossier local Windows ; Power BI utilise cette copie. Depuis Ubuntu natif, transférez le même dossier sur le poste Windows prévu.

Les [sources officielles](sources.json) ont été vérifiées le **27 octobre 2026**. Cette recherche ne constitue pas une installation Windows/Ubuntu ni un test de compte Free. Les schémas décrivent le fonctionnement et ne prétendent pas montrer l’interface réelle de votre poste.
