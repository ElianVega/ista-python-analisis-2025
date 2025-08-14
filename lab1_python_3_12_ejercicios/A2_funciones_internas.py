def crear_descuento(porcentaje):
    def aplicar_descuento(precio):
        return precio * (1 - porcentaje / 100)
    return aplicar_descuento

descuento_10 = crear_descuento(10)
descuento_25 = crear_descuento(25)
print(f"Su precio final es de: {descuento_10(100)}")
print(f"Su precio final es de: {descuento_25(80)}")