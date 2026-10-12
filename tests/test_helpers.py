from helpers import normalizar_isbn

def test_normalizar_isbn_sin_guiones():
    assert normalizar_isbn("9780307474728") == "9780307474728"
    

def test_normalizar_isbn_con_guiones():
    assert normalizar_isbn("978-0-307-47472-8") == "9780307474728"
    

def test_normalizar_isbn_con_espacios():
    assert normalizar_isbn("  9780307474728  ") == "9780307474728"


def test_normalizar_isbn_none():
    assert normalizar_isbn(None) is None


def test_normalizar_isbn_vacio():
    assert normalizar_isbn("") is None