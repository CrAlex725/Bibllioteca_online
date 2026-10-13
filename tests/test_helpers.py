from helpers import normalizar_isbn, normalizar_rut

def test_normalizar_isbn_sin_guiones():
    assert normalizar_isbn("9780307474728") == "9780307474728"
    
def test_normalizar_isbn_con_guiones():
    assert normalizar_isbn("978-0-307-47472-8") == "9780307474728"
    
def test_normalizar_isbn_con_espacios():
    assert normalizar_isbn("  9780307474728  ") == "9780307474728"
    
def test_normalizar_isbn_con_espacios_internos():
    assert normalizar_isbn("9 7 8 0 3 0 7 4 7 4 7 2 8") == "9780307474728"
    
def test_normalizar_isbn_solo_con_espacios():
    assert normalizar_isbn("    ") is None
    
def test_normalizar_isbn_none():
    assert normalizar_isbn(None) is None

def test_normalizar_isbn_vacio():
    assert normalizar_isbn("") is None
    
def test_normalizar_rut_con_guion():
    assert normalizar_rut("15246092-5") == "152460925"
    
def test_normalizar_rut_con_guion_y_puntos():
    assert normalizar_rut("15.246.092-5") == "152460925"
    
def test_normalizar_rut_con_espacios():
    assert normalizar_rut("15 246   092 5") == "152460925"
    
def test_normalizar_rut_con_puntos_sin_guion():
    assert normalizar_rut("15.246.0925") == "152460925"
    
def test_normalizar_rut_con_espacios_al_inicio_y_al_final():
    assert normalizar_rut("    15.246.092-5    ") == "152460925"
    
def test_normalizar_rut_con_guiones_intermedios():
    assert normalizar_rut("-1-5-2-4-6-0-9-2-5-") == "152460925"
    
def test_normalizar_rut_solo_con_guiones():
    assert normalizar_rut("--------") is None
    
def test_normalizar_rut_solo_con_puntos():
    assert normalizar_rut("..........") is None
    
def test_normalizar_rut_none():
    assert normalizar_rut(None) is None
    
def test_normalizar_rut_vacio():
    assert normalizar_rut("") is None