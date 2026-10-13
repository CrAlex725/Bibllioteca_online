def normalizar_isbn(isbn):
    if not isbn:
        return None
    limpio = isbn.replace("-","").replace(" ","").strip()
    return limpio if limpio else None

def normalizar_rut(rut):
    if not rut:
        return None
    limpio = rut.replace("-", "").replace(".", "").replace(" ", "").strip()
    return limpio if limpio else None