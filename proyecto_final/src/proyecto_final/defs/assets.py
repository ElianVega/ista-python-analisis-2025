"""
Pipeline de análisis de datos de COVID-19 para Ecuador y Perú
Implementa un flujo completo de ETL con Dagster para análisis epidemiológico
"""

import io
import pandas as pd
import requests
from datetime import datetime, timedelta
from dagster import asset, AssetCheckResult, asset_check, AssetExecutionContext
from pathlib import Path

# Configuración global
URL_DATOS_COVID = "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv"
PAISES_ANALISIS = ["Ecuador", "Peru"]

# ===============================================================================
# PASO 2: LECTURA DE DATOS SIN TRANSFORMAR + CHEQUEOS DE ENTRADA  
# ===============================================================================

@asset(
    description="Descarga datos crudos de COVID-19 desde Our World in Data",
    group_name="ingesta_datos"
)
def leer_datos(context: AssetExecutionContext) -> pd.DataFrame:
    """
    Descarga el dataset completo de COVID-19 desde la URL canónica de OWID.
    
    Returns:
        DataFrame con todos los datos sin procesar
    """
    try:
        context.log.info(f"Descargando datos desde: {URL_DATOS_COVID}")
        response = requests.get(URL_DATOS_COVID, timeout=60)
        response.raise_for_status()
        
        # Cargar datos en DataFrame
        df = pd.read_csv(io.StringIO(response.text))
        
        context.log.info(f"Datos descargados exitosamente: {len(df)} filas, {len(df.columns)} columnas")
        context.log.info(f"Países únicos: {df['country'].nunique()}")
        context.log.info(f"Rango de fechas: {df['date'].min()} a {df['date'].max()}")
        
        return df
        
    except requests.RequestException as e:
        context.log.error(f"Error al descargar datos: {e}")
        raise
    except KeyError as e:
        context.log.error(f"Error al procesar datos: {e}")
        raise


@asset(
    description="Genera tabla de perfilado básico de los datos",
    group_name="exploracion"
)
def tabla_perfilado(context: AssetExecutionContext, leer_datos: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza perfilado básico de los datos descargados según especificaciones del proyecto.
    
    Args:
        leer_datos: DataFrame con datos crudos
        
    Returns:
        DataFrame con métricas de perfilado
    """
    context.log.info("Generando tabla de perfilado...")
    
    # Crear diccionario con métricas de perfilado
    perfilado = {
        "total_filas": [len(leer_datos)],
        "total_columnas": [len(leer_datos.columns)],
        "columnas_disponibles": [", ".join(leer_datos.columns.tolist())],
        "tipos_datos": [str(leer_datos.dtypes.to_dict())],
        "min_new_cases": [leer_datos["new_cases"].min()],
        "max_new_cases": [leer_datos["new_cases"].max()],
        "pct_nulos_new_cases": [round(leer_datos["new_cases"].isna().mean() * 100, 2)],
        "pct_nulos_people_vaccinated": [round(leer_datos["people_vaccinated"].isna().mean() * 100, 2)],
        "fecha_minima": [leer_datos["date"].min()],
        "fecha_maxima": [leer_datos["date"].max()],
        "paises_unicos": [leer_datos["country"].nunique()],
        "filas_ecuador": [len(leer_datos[leer_datos["country"] == "Ecuador"])],
        "filas_peru": [len(leer_datos[leer_datos["country"] == "Peru"])]
    }
    
    df_perfilado = pd.DataFrame(perfilado)
    
    # Guardar archivo CSV como se requiere en el proyecto
    ruta_archivo = Path("tabla_perfilado.csv")
    df_perfilado.to_csv(ruta_archivo, index=False, encoding='utf-8')
    
    context.log.info(f"Tabla de perfilado guardada en: {ruta_archivo.absolute()}")
    
    return df_perfilado

@asset_check(asset="leer_datos", description="Verificar que no hay fechas futuras")
def check_no_fechas_futuras(leer_datos: pd.DataFrame) -> AssetCheckResult:
    """Valida que no existan fechas futuras en los datos"""
    fecha_max = pd.to_datetime(leer_datos["date"]).max()
    fecha_hoy = pd.Timestamp.now()
    
    passed = bool(fecha_max <= fecha_hoy)
    filas_futuras = len(leer_datos[pd.to_datetime(leer_datos["date"]) > fecha_hoy])
    
    return AssetCheckResult(
        passed=passed,
        description=f"Fecha máxima: {fecha_max.strftime('%Y-%m-%d')}, Filas futuras: {filas_futuras}"
    )


@asset_check(asset="leer_datos", description="Verificar columnas clave no nulas")
def check_columnas_clave_no_nulas(leer_datos: pd.DataFrame) -> AssetCheckResult:
    """Valida que las columnas clave no tengan valores nulos"""
    columnas_clave = ["country", "date", "population"]
    
    resultados = []
    for col in columnas_clave:
        if col in leer_datos.columns:
            nulos = leer_datos[col].isna().sum()
            total = len(leer_datos)
            resultados.append(f"{col}: {nulos}/{total} nulos")
        else:
            resultados.append(f"{col}: COLUMNA NO EXISTE")
    
    passed = bool(all(leer_datos[col].notna().all() for col in columnas_clave if col in leer_datos.columns))
    
    return AssetCheckResult(
        passed=passed,
        description=f"Validación columnas clave: {'; '.join(resultados)}"
    )


@asset_check(asset="leer_datos", description="Verificar unicidad de (country, date)")
def check_unicidad_country_date(leer_datos: pd.DataFrame) -> AssetCheckResult:
    """Valida la unicidad de la combinación country-date"""
    duplicados = leer_datos.duplicated(subset=["country", "date"]).sum()
    total_filas = len(leer_datos)
    
    return AssetCheckResult(
        passed=bool(duplicados == 0),
        description=f"Duplicados encontrados: {duplicados} de {total_filas} filas"
    )


@asset_check(asset="leer_datos", description="Verificar que population > 0")
def check_population_positiva(leer_datos: pd.DataFrame) -> AssetCheckResult:
    """Valida que los valores de población sean positivos"""
    filas_poblacion_valida = (leer_datos["population"] > 0).sum()
    filas_poblacion_invalida = (leer_datos["population"] <= 0).sum()
    total_filas = len(leer_datos)
    
    return AssetCheckResult(
        passed=bool(filas_poblacion_invalida == 0),
        description=f"Población válida: {filas_poblacion_valida}/{total_filas}, inválida: {filas_poblacion_invalida}"
    )


# ===============================================================================
# PASO 3: PROCESAMIENTO DE DATOS
# ===============================================================================

@asset(
    description="Datos procesados y filtrados para análisis de Ecuador y Perú",
    group_name="procesamiento"
)
def datos_procesados(context: AssetExecutionContext, leer_datos: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa y limpia los datos según especificaciones del proyecto.
    
    Args:
        leer_datos: DataFrame con datos crudos
        
    Returns:
        DataFrame procesado listo para análisis
    """
    context.log.info("Iniciando procesamiento de datos...")
    
    df = leer_datos.copy()
    filas_iniciales = len(df)
    
    # 1. Filtrar por países de interés
    df = df[df["country"].isin(PAISES_ANALISIS)]
    context.log.info(f"Después de filtrar países {PAISES_ANALISIS}: {len(df)} filas")
    
    # 2. Eliminar filas con valores nulos en columnas críticas
    columnas_criticas = ["new_cases", "people_vaccinated"]
    filas_antes_nulos = len(df)
    df = df.dropna(subset=columnas_criticas)
    context.log.info(f"Después de eliminar nulos en {columnas_criticas}: {len(df)} filas")
    
    # 3. Eliminar duplicados
    filas_antes_duplicados = len(df)
    df = df.drop_duplicates(subset=["country", "date"])
    context.log.info(f"Después de eliminar duplicados: {len(df)} filas")
    
    # 4. Convertir fecha a datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # 5. Ordenar por país y fecha
    df = df.sort_values(["country", "date"])
    
    # 6. Seleccionar columnas esenciales
    columnas_esenciales = ["country", "date", "new_cases", "people_vaccinated", "population"]
    df = df[columnas_esenciales]
    
    # Renombrar columna country por consistencia
    df = df.rename(columns={"country": "pais"})
    
    context.log.info(f"Procesamiento completado: {filas_iniciales} → {len(df)} filas")
    context.log.info(f"Países procesados: {df['pais'].value_counts().to_dict()}")
    
    return df


# ===============================================================================
# PASO 4: CÁLCULO DE MÉTRICAS
# ===============================================================================

@asset(
    description="Métrica de incidencia acumulada a 7 días por 100mil habitantes",
    group_name="metricas"
)
def metrica_incidencia_7d(context: AssetExecutionContext, datos_procesados: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la incidencia acumulada a 7 días por 100,000 habitantes.
    
    Fórmula:
    1. incidencia_diaria = (new_cases / population) * 100,000
    2. incidencia_7d = promedio móvil de 7 días de incidencia_diaria
    
    Args:
        datos_procesados: DataFrame con datos limpios
        
    Returns:
        DataFrame con métricas de incidencia
    """
    context.log.info("Calculando métrica de incidencia acumulada 7 días...")
    
    df = datos_procesados.copy()
    
    # Calcular incidencia diaria por 100,000 habitantes
    df["incidencia_diaria"] = (df["new_cases"] / df["population"]) * 100000
    
    # Calcular promedio móvil de 7 días por país
    df["incidencia_7d"] = (
        df.groupby("pais")["incidencia_diaria"]
        .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    )
    
    # Formatear resultado final
    resultado = df[["date", "pais", "incidencia_7d"]].copy()
    resultado["incidencia_7d"] = resultado["incidencia_7d"].round(2)
    
    # Eliminar filas con valores NaN en la métrica
    resultado = resultado.dropna(subset=["incidencia_7d"])
    
    context.log.info(f"Incidencia 7d calculada para {len(resultado)} registros")
    context.log.info(f"Rango incidencia: {resultado['incidencia_7d'].min():.2f} - {resultado['incidencia_7d'].max():.2f}")
    
    return resultado


@asset(
    description="Métrica de factor de crecimiento semanal de casos",
    group_name="metricas"
)
def metrica_factor_crec_7d(context: AssetExecutionContext, datos_procesados: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el factor de crecimiento semanal de casos.
    
    Fórmula:
    1. casos_semana_actual = suma(new_cases últimos 7 días)
    2. casos_semana_anterior = suma(new_cases 7 días previos)
    3. factor_crec_7d = casos_semana_actual / casos_semana_anterior
    
    Args:
        datos_procesados: DataFrame con datos limpios
        
    Returns:
        DataFrame con métricas de factor de crecimiento
    """
    context.log.info("Calculando métrica de factor de crecimiento semanal...")
    
    df = datos_procesados.copy()
    df = df.sort_values(["pais", "date"])
    
    # Crear columna de semana (fin de semana)
    df["semana_fin"] = df["date"].dt.to_period("W").apply(lambda r: r.end_time.date())
    
    # Agrupar por país y semana, sumando casos
    resumen_semanal = (
        df.groupby(["pais", "semana_fin"])["new_cases"]
        .sum()
        .reset_index()
        .rename(columns={"new_cases": "casos_semana"})
    )
    
    # Calcular casos semana anterior por país
    resumen_semanal["casos_semana_prev"] = (
        resumen_semanal.groupby("pais")["casos_semana"].shift(1)
    )
    
    # Calcular factor de crecimiento
    resumen_semanal["factor_crec_7d"] = (
        resumen_semanal["casos_semana"] / resumen_semanal["casos_semana_prev"]
    )
    
    # Limpiar resultados
    resultado = resumen_semanal.dropna(subset=["factor_crec_7d"])
    resultado["factor_crec_7d"] = resultado["factor_crec_7d"].round(3)
    
    # Reordenar columnas
    resultado = resultado[["semana_fin", "pais", "casos_semana", "factor_crec_7d"]]
    
    context.log.info(f"Factor crecimiento calculado para {len(resultado)} semanas")
    context.log.info(f"Rango factor: {resultado['factor_crec_7d'].min():.3f} - {resultado['factor_crec_7d'].max():.3f}")
    
    return resultado


# ===============================================================================
# PASO 5: CHEQUEOS DE SALIDA
# ===============================================================================

@asset_check(asset="metrica_incidencia_7d", description="Validar rango de incidencia 7d")
def check_incidencia_rango_valido(metrica_incidencia_7d: pd.DataFrame) -> AssetCheckResult:
    """Valida que la incidencia esté en un rango razonable (0-2000)"""
    incidencia_valida = (
        (metrica_incidencia_7d["incidencia_7d"] >= 0) & 
        (metrica_incidencia_7d["incidencia_7d"] <= 2000)
    )
    
    filas_validas = incidencia_valida.sum()
    total_filas = len(metrica_incidencia_7d)
    
    return AssetCheckResult(
        passed=bool(incidencia_valida.all()),
        description=f"Incidencia en rango [0-2000]: {filas_validas}/{total_filas} filas válidas"
    )


@asset_check(asset="metrica_factor_crec_7d", description="Validar factor de crecimiento")
def check_factor_crecimiento_valido(metrica_factor_crec_7d: pd.DataFrame) -> AssetCheckResult:
    """Valida que el factor de crecimiento sea positivo"""
    factores_positivos = (metrica_factor_crec_7d["factor_crec_7d"] > 0)
    
    filas_validas = factores_positivos.sum()
    total_filas = len(metrica_factor_crec_7d)
    
    return AssetCheckResult(
        passed=bool(factores_positivos.all()),
        description=f"Factores positivos: {filas_validas}/{total_filas} filas"
    )


# ===============================================================================
# PASO 6: EXPORTACIÓN DE RESULTADOS
# ===============================================================================

@asset(
    description="Reporte final en Excel con todas las métricas calculadas",
    group_name="reportes"
)
def reporte_excel_covid(
    context: AssetExecutionContext,
    datos_procesados: pd.DataFrame,
    metrica_incidencia_7d: pd.DataFrame,
    metrica_factor_crec_7d: pd.DataFrame,
    tabla_perfilado: pd.DataFrame
) -> str:
    """
    Genera reporte final en Excel con todos los resultados del análisis.
    
    Args:
        datos_procesados: Datos limpios
        metrica_incidencia_7d: Métrica de incidencia
        metrica_factor_crec_7d: Métrica de factor de crecimiento
        tabla_perfilado: Tabla de perfilado de datos
        
    Returns:
        Ruta del archivo Excel generado
    """
    context.log.info("Generando reporte final en Excel...")
    
    archivo_excel = "reporte_covid_ecuador_peru.xlsx"
    
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        # Hoja 1: Datos procesados
        datos_procesados.to_excel(
            writer, 
            sheet_name="Datos_Procesados", 
            index=False
        )
        
        # Hoja 2: Métrica incidencia 7d
        metrica_incidencia_7d.to_excel(
            writer, 
            sheet_name="Incidencia_7d", 
            index=False
        )
        
        # Hoja 3: Métrica factor crecimiento 7d
        metrica_factor_crec_7d.to_excel(
            writer, 
            sheet_name="Factor_Crec_7d", 
            index=False
        )
        
        # Hoja 4: Tabla de perfilado
        tabla_perfilado.to_excel(
            writer, 
            sheet_name="Perfilado_Datos", 
            index=False
        )
        
        # Hoja 5: Resumen del análisis
        resumen = crear_resumen_analisis(datos_procesados, metrica_incidencia_7d, metrica_factor_crec_7d)
        resumen.to_excel(
            writer, 
            sheet_name="Resumen_Analisis", 
            index=False
        )
    
    context.log.info(f"Reporte Excel generado: {archivo_excel}")
    context.log.info(f"Hojas incluidas: Datos_Procesados, Incidencia_7d, Factor_Crec_7d, Perfilado_Datos, Resumen_Analisis")
    
    return archivo_excel


def crear_resumen_analisis(
    datos_procesados: pd.DataFrame,
    metrica_incidencia_7d: pd.DataFrame,
    metrica_factor_crec_7d: pd.DataFrame
) -> pd.DataFrame:
    """Crea un resumen estadístico del análisis realizado"""
    
    resumen_data = []
    
    for pais in PAISES_ANALISIS:
        # Datos básicos por país
        datos_pais = datos_procesados[datos_procesados["pais"] == pais]
        incidencia_pais = metrica_incidencia_7d[metrica_incidencia_7d["pais"] == pais]
        factor_pais = metrica_factor_crec_7d[metrica_factor_crec_7d["pais"] == pais]
        
        resumen_data.append({
            "pais": pais,
            "total_registros": len(datos_pais),
            "fecha_inicio": datos_pais["date"].min().strftime("%Y-%m-%d"),
            "fecha_fin": datos_pais["date"].max().strftime("%Y-%m-%d"),
            "casos_totales": datos_pais["new_cases"].sum(),
            "incidencia_7d_promedio": incidencia_pais["incidencia_7d"].mean(),
            "incidencia_7d_maxima": incidencia_pais["incidencia_7d"].max(),
            "factor_crec_promedio": factor_pais["factor_crec_7d"].mean(),
            "semanas_analizadas": len(factor_pais)
        })
    
    return pd.DataFrame(resumen_data)