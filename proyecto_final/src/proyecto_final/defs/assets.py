import pandas as pd
import requests
from dagster import asset, AssetCheckResult

URL = "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv"

# ---------------------------
# Paso 1: Lectura de datos
# ---------------------------
@asset
def leer_datos() -> pd.DataFrame:
    r = requests.get(URL)
    r.raise_for_status()
    import io
    df = pd.read_csv(io.StringIO(r.text))
    return df

# ---------------------------
# Paso 1B: Perfilado manual
# ---------------------------
@asset
def tabla_perfilado(leer_datos: pd.DataFrame):
    perfil = {
        "columnas": list(leer_datos.columns),
        "tipos": leer_datos.dtypes.astype(str).to_dict(),
        "min_new_cases": leer_datos["new_cases"].min(),
        "max_new_cases": leer_datos["new_cases"].max(),
        "pct_nulos_new_cases": leer_datos["new_cases"].isna().mean() * 100,
        "pct_nulos_people_vaccinated": leer_datos["people_vaccinated"].isna().mean() * 100,
        "fecha_min": leer_datos["date"].min(),
        "fecha_max": leer_datos["date"].max(),
    }

    df_perfil = pd.DataFrame([perfil])
    df_perfil.to_csv("tabla_perfilado.csv", index=False)
    return df_perfil

# ---------------------------
# Paso 2: Chequeos de entrada
# ---------------------------
@asset
def chequeos_entrada(leer_datos: pd.DataFrame):
    checks = []

    # No fechas futuras
    passed = bool(leer_datos["date"].max() <= pd.Timestamp.today().strftime("%Y-%m-%d"))
    checks.append(AssetCheckResult(passed=passed, description="No fechas futuras"))

    # Columnas clave no nulas
    for col in ["country", "date", "population"]:
        passed = bool(leer_datos[col].notna().all())
        checks.append(AssetCheckResult(passed=passed, description=f"{col} no nulo"))

    # Unicidad country+date
    passed = bool(not leer_datos.duplicated(["country", "date"]).any())
    checks.append(AssetCheckResult(passed=passed, description="Unicidad country+date"))

    # Population > 0
    passed = bool((leer_datos["population"] > 0).all())
    checks.append(AssetCheckResult(passed=passed, description="Population > 0"))

    # new_cases >= 0
    passed = bool((leer_datos["new_cases"].dropna() >= 0).all())
    checks.append(AssetCheckResult(passed=passed, description="new_cases >= 0 (no negativos)"))

    return checks

# ---------------------------
# Paso 3: Procesamiento
# ---------------------------
@asset
def datos_procesados(leer_datos: pd.DataFrame) -> pd.DataFrame:
    df = leer_datos.dropna(subset=["new_cases", "people_vaccinated"])
    df = df.drop_duplicates(subset=["country", "date"])
    df = df[df["country"].isin(["Ecuador", "Peru"])]
    return df[["country", "date", "new_cases", "people_vaccinated", "population"]]

# ---------------------------
# Paso 4A: Incidencia acumulada 7 días
# ---------------------------
@asset
def metrica_incidencia_7d(datos_procesados: pd.DataFrame) -> pd.DataFrame:
    df = datos_procesados.copy()
    df["incidencia_diaria"] = (df["new_cases"] / df["population"]) * 100000
    df["incidencia_7d"] = (
        df.groupby("country")["incidencia_diaria"]
        .transform(lambda x: x.rolling(7).mean())
    )
    return df[["date", "country", "incidencia_7d"]]

# ---------------------------
# Paso 4B: Factor de crecimiento semanal
# ---------------------------
@asset
def metrica_factor_crec_7d(datos_procesados: pd.DataFrame) -> pd.DataFrame:
    df = datos_procesados.copy()
    df["semana"] = pd.to_datetime(df["date"]).dt.to_period("W").apply(lambda r: r.end_time)

    resumen = (
        df.groupby(["country", "semana"])["new_cases"]
        .sum()
        .reset_index(name="casos_semana")
    )

    resumen["casos_semana_prev"] = resumen.groupby("country")["casos_semana"].shift(1)
    resumen["factor_crec_7d"] = resumen["casos_semana"] / resumen["casos_semana_prev"]

    return resumen

# ---------------------------
# Paso 5: Chequeos de salida
# ---------------------------
@asset
def chequeos_salida(metrica_incidencia_7d: pd.DataFrame):
    passed = bool(((metrica_incidencia_7d["incidencia_7d"] >= 0) &
                   (metrica_incidencia_7d["incidencia_7d"] <= 2000)).all())
    return [AssetCheckResult(passed=passed, description="Incidencia en rango válido")]

# ---------------------------
# Paso 6: Exportación a Excel
# ---------------------------
@asset
def reporte_excel_covid(
    metrica_incidencia_7d: pd.DataFrame,
    metrica_factor_crec_7d: pd.DataFrame,
    datos_procesados: pd.DataFrame
):
    with pd.ExcelWriter("reporte_covid.xlsx") as writer:
        datos_procesados.to_excel(writer, sheet_name="datos_procesados", index=False)
        metrica_incidencia_7d.to_excel(writer, sheet_name="incidencia_7d", index=False)
        metrica_factor_crec_7d.to_excel(writer, sheet_name="factor_crec_7d", index=False)