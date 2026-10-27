"""La transaction et SCD2 sont fournis ; adapter la recherche d'une version."""
SQL_VERSION = "SELECT shop_key FROM dim_shop WHERE shop_id=? AND valid_from<=? AND (valid_to IS NULL OR ?<valid_to)"


def trouver_shop_key(conn, shop_id, sale_date):
    # TODO 05 : exécuter SQL_VERSION avec (shop_id, sale_date, sale_date).
    # Exiger exactement une ligne ; sinon lever ValueError. Renvoyer la clé entière.
    raise NotImplementedError("Compléter incremental.trouver_shop_key")
