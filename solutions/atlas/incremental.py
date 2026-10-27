"""06 — Réutiliser le nettoyage et le chargement pour un nouveau lot."""
from pathlib import Path
from chargement import charger, total_base
from lecture import DATA, OUTPUTS, catalogues, ecrire_csv, lire_csv
from nettoyage import CHAMPS_SOURCE, CHAMPS_VENTES, nettoyer


def ajouter(chemin_source, chemin_base, chemin_data):
    """Traiter le lot fourni ; aucun effacement et aucun chargement initial caché."""
    produits, boutiques = catalogues(chemin_data)
    lignes = lire_csv(chemin_source)
    retenues, rejets, doublons = nettoyer(lignes, produits, boutiques)
    compteurs = charger(retenues, produits, boutiques, chemin_base)
    # Les journaux ne sont remplacés qu'après validation de la transaction.
    dossier = Path(chemin_base).parent
    ecrire_csv(dossier / "rejets_ajout.csv", rejets, CHAMPS_SOURCE + ["motif"])
    ecrire_csv(dossier / "doublons_ajout.csv", doublons, CHAMPS_VENTES)
    return {"raw": len(lignes), "accepted": len(retenues), "rejected": len(rejets),
            "duplicates": len(doublons), **compteurs}


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
