import duckdb

result = duckdb.sql("""
    SELECT department, gender
    FROM 'lab_analisis_pandas/train.csv'
    WHERE length_of_service > 10
""").df()

count = duckdb.sql("""
    SELECT COUNT(*) AS total
    FROM 'lab_analisis_pandas/train.csv'
    WHERE length_of_service > 10
""").fetchone()[0]

print(result.head())
print(f"Total de filas con length_of_service > 10: {count}")


import duckdb

duckdb.sql("""
    CREATE TABLE summary AS
    SELECT
        department,
        AVG(avg_training_score) AS avg_training_score,
        SUM(is_promoted) AS promoted_count,
        -- Columna derivada: año de nacimiento
        (2025 - age) AS birthday,
        -- Columna derivada: género completo
        CASE WHEN gender = 'm' THEN 'Masculino' ELSE 'Femenino' END AS complete_gender
    FROM 'lab_analisis_pandas/train.csv'
    WHERE previous_year_rating IS NOT NULL
      AND length_of_service > 5
    GROUP BY department, age, gender
""")

duckdb.sql("""
    COPY (SELECT * FROM summary) TO 'lab_analisis_pandas/summary_by_department_duckdb.csv' (HEADER, DELIMITER ',')
""")

result = duckdb.sql("SELECT * FROM summary LIMIT 5").df()
print(result)