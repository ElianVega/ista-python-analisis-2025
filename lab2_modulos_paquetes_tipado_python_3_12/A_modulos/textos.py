from A_modulos.operaciones_aritmeticas import suma

def obtener_texto_suma(num1, num2):
    resultado = suma(num1, num2)
    return f"La suma de {num1} y {num2} es {resultado}"