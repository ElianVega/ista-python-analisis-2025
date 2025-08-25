from . import operaciones_aritmeticas as op


"""
Este módulo utiliza funciones aritméticas importadas desde 'operaciones_aritmeticas' para ejecutar operaciones básicas (suma, resta, multiplicación y división) entre dos números.
"""

def ejecutar_operaciones(num1, num2):
    try:
        op.validate_numbers(num1, num2)
        print(f"El resultado de la suma es: {op.suma(num1, num2)}")
        print(f"El resultado de la resta es: {op.resta(num1, num2)}")
        print(f"El resultado de la multiplicación es: {op.multiplicacion(num1, num2)}")
        if num2 == 0:
            print("Error: División por cero no está permitida.")
        else:
            print(f"El resultado de la división es: {op.division(num1, num2)}")
    except ValueError as e:
        print(f"Error: {e}")


""""
Casos de prueba:
1. ejecutar_operaciones(10, 5)
    - Realiza suma, resta, multiplicación y división entre 10 y 5.
    - Espera resultados numéricos válidos para todas las operaciones.
"""
ejecutar_operaciones(10, 5)
"""
2. ejecutar_operaciones(10, 0)
    - Realiza suma, resta y multiplicación entre 10 y 0.
    - Para la división, detecta el caso de división por cero y muestra un mensaje de error correspondiente.
"""
ejecutar_operaciones(10, 0)
"""
3. ejecutar_operaciones(10, 'a')
    - Intenta realizar operaciones entre un número y un valor no numérico ('a').
    - Espera que la función 'validate_numbers' lance una excepción ValueError, la cual es capturada y mostrada como mensaje de error.
"""
ejecutar_operaciones(10, 'a')