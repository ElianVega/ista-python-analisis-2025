def contar_palabras(texto: str) -> int:
    if not isinstance(texto, str):
        raise TypeError("El argumento debe ser una cadena de texto.")
    return len(texto.split())

def es_palindromo(texto: str) -> bool:
    if not isinstance(texto, str):
        raise TypeError("El argumento debe ser una cadena de texto.")
    texto_limpio = ''.join(c.lower() for c in texto if c.isalnum())
    return texto_limpio == texto_limpio[::-1]

def mayusculas(texto: str) -> str:
    if not isinstance(texto, str):
        raise TypeError("El argumento debe ser una cadena de texto.")
    return texto.upper()