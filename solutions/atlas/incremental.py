"""La transaction et SCD2 sont fournis ; adapter la recherche d'une version."""
SQL_VERSION = "SELECT shop_key FROM dim_shop WHERE shop_id=? AND valid_from<=? AND (valid_to IS NULL OR ?<valid_to)"


def trouver_shop_key(conn, shop_id, sale_date):
    versions = conn.execute(SQL_VERSION, (shop_id, sale_date, sale_date)).fetchall()
    if len(versions) != 1:
        raise ValueError(f"Version temporelle unique attendue : {shop_id} au {sale_date}")
    return versions[0][0]
