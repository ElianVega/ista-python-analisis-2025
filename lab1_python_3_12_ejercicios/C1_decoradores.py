def requiere_positivos(funcion):
    def wrapper(*args):
        try:
            for arg in args:
                if arg < 0:
                    raise ValueError("Todos los valores ingresados deben ser positivos")
            return funcion(*args)
        except ValueError as e:
            return f"Error: {e}"
    return wrapper
    
@requiere_positivos
def cacular_descuento(precio, porcentaje):
    return precio * (1 - porcentaje / 100)

@requiere_positivos
def escala(valor, factor):
    return valor * factor

print(cacular_descuento(100, 10))
print(cacular_descuento(-50, 20))
print(escala(5, 3))
print(escala(10, -2))