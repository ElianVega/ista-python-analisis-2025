def suma(num1, num2):
    return num1 + num2

def resta(num1, num2):
    return num1 - num2

def multiplicacion(num1, num2):
    return num1 * num2

def division(num1, num2):
    return num1 / num2

def validate_numbers(num1, num2):
    if not (isinstance(num1, (int, float)) and isinstance(num2, (int, float))):
        raise ValueError("Los valores deben ser numéricos.")