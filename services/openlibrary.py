import requests
from requests.exceptions import RequestException
import re

def buscar_por_isbn(isbn):
    url_isbn = f"https://openlibrary.org/isbn/{isbn}.json"
    
    try:
        response = requests.get(url_isbn, timeout=5)
    except RequestException:
        return None
    
    if response.status_code != 200:
        return None
    
    try:
        datos = response.json()
    except ValueError:
        return None
    
    titulo = datos.get("title")
    publisher_date = datos.get("publish_date", "")
    match = re.search(r'\d{4}', publisher_date)
    year_publication = int(match.group()) if match else None
    publish = datos.get("publishers") or []
    editorial = publish[0] if publish else None
    
    autores_api = datos.get("authors", [])
    autores = [a["key"] for a in autores_api if "key" in a] # resultado '/authors/xxxxxxx'
    
    autor_nombres=[]
    for elemento in autores:
        url_autor = f"https://openlibrary.org{elemento}.json"
        try:
            autor = requests.get(url_autor, timeout=5)
            if autor.status_code != 200:
                continue
            datos_autor = autor.json()
            nombre = datos_autor.get("name")
            if nombre:
                autor_nombres.append(nombre)
                
        except (RequestException, ValueError):
            continue
        
    return {
        "isbn": isbn,
        "title": titulo,
        "year_publication": year_publication,
        "editorial": editorial,
        "autores": autor_nombres
    }