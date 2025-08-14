def parsear_enteros(lista_str):
    valores = []
    errores = []
    for entrada in lista_str:
        try:
            valor = int(entrada)
            valores.append(valor)
        except ValueError:
            errores.append(entrada)
    return {"enteros": valores, "errores": errores }

print(parsear_enteros(['1', '2', 'tres', '4', 'cinco']))
print(parsear_enteros(['10', '20', '30', 'cuarenta', '50']))