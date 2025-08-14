def saludar(nombre):
    return f"Hola, {nombre}!"

def despedir(nombre):
    return f"Adiós, {nombre}!"

def aplaudir(nombre):
    return f"Aplausos, {nombre}!"

acciones = {
    "saludar": saludar,
    "despedir": despedir,
    "aplaudir": aplaudir
    }

def ejecutar_accion(accion, nombre):
    if accion in acciones:
        print(acciones[accion](nombre))
    else:
        print("Acción no reconocida.")
    
ejecutar_accion("saludar", "Juan")
ejecutar_accion("despedir", "Ana")
ejecutar_accion("aplaudir", "Luis")
ejecutar_accion("bailar", "Carlos")