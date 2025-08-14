class CantidadInvalida(Exception):
    def __init__(self, cantidad, mensaje="La cantidad debe ser mayor que cero"):
        self.cantidad = cantidad
        self.mensaje = mensaje
        super().__init__(self.mensaje)
        
def calcular_total(precio_unitario, cantidad):
    try:
        if cantidad < 0:
            raise ValueError()
        elif cantidad <= 0:
            raise CantidadInvalida(cantidad)
        total = precio_unitario * cantidad
        return total
    except ValueError as e:
        return f"Error: {e.mensaje} (cantidad: {e.cantidad})"
    except CantidadInvalida as e:
        return f"Error: {e.mensaje} (cantidad: {e.cantidad})"

print(calcular_total(10, 3))
print(calcular_total(10, 0))
