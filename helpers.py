def normalizar_isbn(isbn):
    if not isbn:
        return None
    return isbn.replace("-","").replace(" ","").strip()