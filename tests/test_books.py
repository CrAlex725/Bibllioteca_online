from models import (Usuario,Libro, Editorial, Autor, libro_autor)
from extensions import db

# books/<isbn>
def test_books_informacion_del_libro_con_isbn_no_encontrada(client):
    isbn = "0788471532688"
    
    resp = client.get(f'/books/{isbn}')
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "libro No encontrado"
    
def test_books_informacion_del_libro_sin_token(client, libro_de_prueba):
    resp = client.get(f'/books/{libro_de_prueba}')
    
    assert resp.status_code == 200, resp.get_data(as_text = True)
    data = resp.get_json()
    
    assert "isbn" in data
    assert "title" in data
    assert "autores" in data
    assert "year_publication" in data
    assert "editorial" not in data
    
def test_books_informacion_del_libro_con_token(client, libro_de_prueba, usuario_de_prueba):
    resp_login = client.post('/auth/login', json={
        "email": usuario_de_prueba["email"],
        "password": usuario_de_prueba["password"],
    })

    assert resp_login.status_code == 200, resp_login.get_data(as_text=True)
    token = resp_login.get_json()["token"]

    resp = client.get(f'/books/{libro_de_prueba}', headers={
        "Authorization": f"Bearer {token}"
    })

    assert resp.status_code == 200, resp.get_data(as_text=True)
    data = resp.get_json()

    assert "isbn" in data
    assert "title" in data
    assert "year_publication" in data
    assert "clasificacion" in data
    assert "editorial" in data
    assert "autores" in data
    assert "created_at" in data
    assert "is_complete" in data