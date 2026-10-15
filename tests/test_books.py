from models import (Usuario,Libro, Editorial, Autor, libro_autor)
from extensions import db

# Libro. /resolver-isbn/<isbn>
def test_books_informacion_del_libro_con_isbn_no_encontrada(client):
    isbn = "0788471532688"
    
    resp = client.get(f'/books/{isbn}')
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "libro No encontrado"
    
def test_books_informacion_del_libro__sin_token(client, app):
    with app.app_context():
        editorial = Editorial(
            nombre = "Zig-Zag"
        )
        db.session.add(editorial)
        db.session.commit()
        
        autores = Autor(
            nombre = "Anaya"
        )
        db.session.add(autores)
        db.session.commit()
        libro = Libro(
            isbn = "9788471532688",
            title = "Libro 1",
            year_publication = 2003,
            clasificacion = "Fantasía",
            is_complete = True,
            editorial_id = editorial.id
            )
        
        libro.autores.append(autores)
        db.session.add(libro)
        db.session.commit()
    
    isbn = "9788471532688"
    
    resp = client.get(f'/books/{isbn}')
    
    data = resp.get_json()
    assert resp.status_code == 200
    assert "isbn" in data
    assert "title" in data
    assert "autores" in data
    assert "year_publication" in data
    assert "editorial" not in data
    
def test_books_informacion_del_libro_con_token(client, app):
    with app.app_context():
        editorial = Editorial(
            nombre = "Zig-Zag"
        )
        db.session.add(editorial)
        db.session.commit()
        
        autores = Autor(
            nombre = "Anaya"
        )
        db.session.add(autores)
        db.session.commit()
        libro = Libro(
            isbn = "9788471532688",
            title = "Libro 1",
            year_publication = 2003,
            clasificacion = "Fantasía",
            is_complete = True,
            editorial_id = editorial.id
            )
        db.session.add(libro)
        db.session.commit()
        
        libro.autores.append(autores)
    
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789",
        "rut": "19.234.444-k",
        "phone": "+56987654321",
        "address": "Calle 1"
    }
    client.post('/auth/register', json=datos)
    
    resp_login = client.post('/auth/login', json={
        "email": "ab.cdef.123@gmail.com",
        "password": "123456789"
    })
    token = resp_login.get_json()["token"]
    
    isbn = "9788471532688"
    
    resp = client.get(f'/books/{isbn}', headers={
        "Authorization": f"Bearer {token}"})
    
    data = resp.get_json()
    
    assert resp.status_code == 200
    assert "isbn" in data
    assert "title" in data
    assert "year_publication" in data
    assert "clasificacion" in data
    assert "editorial" in data
    assert "autores" in data
    assert "created_at" in data
    assert "is_complete" in data