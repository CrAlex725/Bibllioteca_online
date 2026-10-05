def normalizar_isbn(isbn):
    if not isbn:
        return None
    return isbn.replace("-","").replace(" ","").strip()

def normalizar_rut(rut):
    if not rut:
        return None
    return rut.replace("-","").replace(" ","").replace(".","") .strip()