"""06 — Réutiliser le nettoyage et le chargement pour un nouveau lot."""
from pathlib import Path
from chargement import charger, total_base
from lecture import DATA, OUTPUTS, catalogues, ecrire_csv, lire_csv
from nettoyage import CHAMPS_SOURCE, CHAMPS_VENTES, nettoyer


def ajouter(chemin_source, chemin_base, chemin_data):
    # TODO — mission 06 : construire cette fonction avec aide de l’IA, puis vérifier.
    raise NotImplementedError("Compléter incremental.py : ajouter.")


def main():
    base = OUTPUTS / "atlas.sqlite"
    resultat = ajouter(DATA / "ventes_ajout.csv", base, DATA)
    print(f"Ajout : {resultat['inserted']} nouvelles, {resultat['existing']} existantes.")
    print(f"Qualité ajout : {resultat['accepted']} retenues, {resultat['rejected']} rejets, "
          f"{resultat['duplicates']} doublons.")
    faits, quantite, montant = total_base(base)
    print(f"Base actuelle : {faits} faits, {quantite} unités, {montant / 1000:.3f} TND.")
    rejeu = ajouter(DATA / "ventes_ajout.csv", base, DATA)
    print(f"Rejeu : {rejeu['inserted']} nouvelle(s), {rejeu['existing']} existantes.")


if __name__ == "__main__":
    main()
