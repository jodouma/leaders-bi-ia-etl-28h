"""Mission 06. Dimensions = contexte ; faits = ventes et mesures."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import OUTPUTS, SCHEMA, connect, create_schema, write_csv

# À VOUS : observer dim_product, puis dim_shop et dim_date.
TABLE_A_OBSERVER = "fact_sales"
TABLES = ("dim_product", "dim_shop", "dim_date", "fact_sales")
if TABLE_A_OBSERVER not in TABLES:
    raise ValueError("Choisir un des quatre noms de TABLES.")

dossier = OUTPUTS / "06"
base = connect(dossier / "modele.sqlite")
# Le SQL complet est enregistré pour le lire à côté du schéma en étoile.
create_schema(base)
(dossier / "schema.sql").write_text(SCHEMA, encoding="utf-8")
print("Tables créées :", ", ".join(TABLES))
print("Colonnes de", TABLE_A_OBSERVER)
# Le nom est limité ci-dessus à quatre noms connus.
colonnes = base.execute(f"PRAGMA table_info({TABLE_A_OBSERVER})").fetchall()
for numero, nom, type_sql, obligatoire, defaut, cle in colonnes:
    print(nom, type_sql, "clé primaire" if cle else "")
write_csv(dossier / "colonnes.csv", ["column_name", "sql_type"],
          [{"column_name": c[1], "sql_type": c[2]} for c in colonnes])
print("Cette base est vide : le chargement arrive à la mission 07.")
base.close()
