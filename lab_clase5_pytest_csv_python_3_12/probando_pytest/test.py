import pytest
from modulo_simple_probando_pytest import contar_palabras, es_palindromo, mayusculas

def test_contar_palabras():
    assert contar_palabras("Hola mundo") == 2
    assert contar_palabras("") == 0
    with pytest.raises(TypeError):
        contar_palabras(123)

def test_es_palindromo():
    assert es_palindromo("Anita lava la tina") is True
    assert es_palindromo("Hola mundo") is False
    assert es_palindromo("") is True
    with pytest.raises(TypeError):
        es_palindromo(None)

def test_mayusculas():
    assert mayusculas("hola") == "HOLA"
    assert mayusculas("") == "" 
    with pytest.raises(TypeError):
        mayusculas(['hola'])