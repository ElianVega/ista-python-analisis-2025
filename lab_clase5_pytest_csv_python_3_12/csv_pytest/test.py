import pytest

from leer_csv import (
    leer_squirrels_csv,
    columnas_obligatorias,
    ids_unicos,
    lat_lon_validos,
    alturas_no_negativas,
)

CSV_PATH = "lab_clase5_pytest_csv_python_3_12/csv_pytest/squirrel-data.csv"

def test_columnas_obligatorias():
    _, fieldnames = leer_squirrels_csv(CSV_PATH)
    assert columnas_obligatorias(fieldnames)

def test_ids_unicos():
    rows, _ = leer_squirrels_csv(CSV_PATH)
    assert ids_unicos(rows)

def test_lat_lon_validos():
    rows, _ = leer_squirrels_csv(CSV_PATH)
    assert lat_lon_validos(rows)

def test_alturas_no_negativas():
    rows, _ = leer_squirrels_csv(CSV_PATH)
    assert alturas_no_negativas(rows)