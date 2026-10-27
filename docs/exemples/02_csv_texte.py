import csv
from io import StringIO
source = "quantity,unit_price_tnd\n2,4.500\n"
ligne = next(csv.DictReader(StringIO(source)))
print(ligne["quantity"])
print(type(ligne["quantity"]).__name__)
