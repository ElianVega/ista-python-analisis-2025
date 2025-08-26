import csv
import chardet

REQUIRED_COLUMNS = [
    "Squirrel ID",
    "Primary Fur Color",
    "Squirrel Latitude (DD.DDDDDD)",
    "Squirrel Longitude (-DD.DDDDDD)"
]

def leer_squirrels_csv(filepath):
    with open(filepath, "rb") as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result["encoding"]

    with open(filepath, newline='', encoding=encoding) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows, reader.fieldnames

def columnas_obligatorias(fieldnames):
    return all(col in fieldnames for col in REQUIRED_COLUMNS)

def ids_unicos(rows):
    ids = [row["Squirrel ID"] for row in rows]
    return len(ids) == len(set(ids))

def lat_lon_validos(rows):
    for row in rows:
        try:
            lat = float(row["Squirrel Latitude (DD.DDDDDD)"])
            lon = float(row["Squirrel Longitude (-DD.DDDDDD)"])
        except ValueError:
            return False
    return True

def alturas_no_negativas(rows):
    for row in rows:
        altura = row.get("Above Ground (Height in Feet)", "")
        if altura and altura.replace('<','').replace('>','').replace('���','').strip():
            try:
                # Puede haber rangos o símbolos, solo chequea si es número simple
                val = float(altura.split()[0].replace('<','').replace('>','').replace('���',''))
                if val < 0:
                    return False
            except ValueError:
                continue
    return True