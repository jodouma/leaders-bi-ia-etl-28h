"""Enchaîner les sept missions terminées, sans remettre la base à zéro."""
from pathlib import Path
from lecture import DATA, OUTPUTS, catalogues, ecrire_csv, lire_csv
from calcul import calculer_total
from nettoyage import CHAMPS_SOURCE, CHAMPS_VENTES, nettoyer
from modele import creer_modele
from chargement import charger
from incremental import ajouter
from rapport import formater_tnd, generer


def executer(chemin_data=DATA, chemin_outputs=OUTPUTS):
    chemin_data, chemin_outputs = Path(chemin_data), Path(chemin_outputs)
    chemin_outputs.mkdir(parents=True, exist_ok=True)
    produits, boutiques = catalogues(chemin_data)
    retenues, rejets, doublons = nettoyer(lire_csv(chemin_data / "ventes_initiales.csv"), produits, boutiques)
    print(f"Qualité initiale : {len(retenues)} retenues, {len(rejets)} rejets, {len(doublons)} doublon(s).")
    ecrire_csv(chemin_outputs / "ventes_nettoyees.csv", retenues, CHAMPS_VENTES)
    ecrire_csv(chemin_outputs / "rejets.csv", rejets, CHAMPS_SOURCE + ["motif"])
    ecrire_csv(chemin_outputs / "doublons.csv", doublons, CHAMPS_VENTES)
    print(f"Montant du lot initial : {formater_tnd(calculer_total(retenues))} TND.")
    base = chemin_outputs / "atlas.sqlite"
    creer_modele(base)
    initial = charger(retenues, produits, boutiques, base)
    print(f"Lot initial : {initial['inserted']} nouvelles, {initial['existing']} existantes.")
    ajout = ajouter(chemin_data / "ventes_ajout.csv", base, chemin_data)
    print(f"Ajout : {ajout['inserted']} nouvelles, {ajout['existing']} existantes.")
    rejeu = ajouter(chemin_data / "ventes_ajout.csv", base, chemin_data)
    print(f"Rejeu : {rejeu['inserted']} nouvelle(s), {rejeu['existing']} existantes.")
    bilan = generer(base, chemin_outputs / "rapport_atlas.html")
    print(f"Rapport : {bilan['facts']} faits, {bilan['quantity']} unités, "
          f"{formater_tnd(bilan['amount_millimes'])} TND.")
    return bilan


if __name__ == "__main__":
    try:
        executer()
    except NotImplementedError as erreur:
        print(f"Mission à construire : {erreur}")
        raise SystemExit(1)
