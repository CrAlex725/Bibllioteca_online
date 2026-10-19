from models import (Usuario,Libro, Editorial, Autor, libro_autor)
from extensions import db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

# GET books/<isbn>
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
    
# GET books/
def test_books_year_string(client):
    year = "dos_mil_dos"
    
    resp = client.get(f'/books?Year={year}')
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Year Debe ser Numerico"
    
def test_books_correcto(client, libro_de_prueba):
    resp = client.get('/books', query_string={
        "Titulo": "lib",
        "Editorial": "zig",
        "Autor": "ana",
        "Categoria": "fantas",
        "Year": "2003",
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == "Libro 1"
    assert data[0]["year_publication"] == 2003
    
def test_books_filtro_titulo(client, libro_de_prueba):
    resp = client.get('/books', query_string={
        "Titulo": "lib",
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == "Libro 1"
    
def test_books_filtro_editorial(client, libro_de_prueba):
    resp = client.get('/books', query_string={
        "Editorial": "zig",
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    
def test_books_filtro_autor(client, libro_de_prueba):
    resp = client.get('/books', query_string={
        "Autor": "ana",
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["autores"][0]["nombre"] == "Anaya"
    
def test_books_filtro_categoría_year(client, libro_de_prueba):
    resp = client.get('/books', query_string={
        "Categoria": "fantas",
        "Year": "2003",
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["year_publication"] == 2003
    
def test_books_sin_filtros(client, libro_de_prueba):
    resp = client.get('/books')
    
    data = resp.get_json()
    
    assert resp.status_code == 200
    assert len(data) == 1

def test_books_sin_resultados(client):
    resp = client.get('/books', query_string={
        "Titulo": "Libro No existente"
    })
    
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_books_argumento_con_caracter_especial(client, libro_de_prueba):
    resp = client.get('/books', query_string={
        "Categoria": "fantasía"
        })
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    
# POST books/ sin permiso
def test_books_post_sin_permiso(client, token_usuario_comun):
    resp = client.post('/books', 
        json={
            "isbn": "9780123456789",
            "title": "Nuevo Libro",
            "editorial": "Nueva Editorial",
            "autores": ["Nuevo Autor"],
            "is_complete": True
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "El Usuario No tiene Permiso para agregar Libros"
    
def test_books_post_sin_body(client, token_usuario_comun):
    resp = client.post('/books', 
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_books_post_autores_Invalidos(client, token_usuario_comun):
    resp = client.post('/books',
        json={
            "isbn": "9780123456789",
            "title": "Nuevo Libro",
            "editorial": "Nueva Editorial",
            "autores": "Nuevo Autor",
            "is_complete": True
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "autores debe ser una lista"
    
def test_books_post_solo_autores_en_lista(client, token_usuario_comun):
    resp = client.post('/books',
        json={
            "autores": ["Nuevo Autor"],
            "is_complete": True
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Todos los campos mencionados son obligatorios"
    
def test_books_post_is_complete_booleano(client, token_usuario_comun):
    resp = client.post('/books', 
        json={
            "isbn": "9780123456789",
            "title": "Nuevo Libro",
            "editorial": "Nueva Editorial",
            "autores": ["Nuevo Autor"],
            "is_complete": "string"
        },
    headers={
        "Authorization": f"Bearer {token_usuario_comun}"
    })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "is_complete debe ser booleano"
    
def test_books_post_usuario_inexistente(client, usuario_de_prueba, token_usuario_comun, app):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.post('/books', 
        json={
            "isbn": "9780123456789",
            "title": "Nuevo Libro",
            "editorial": "Nueva Editorial",
            "autores": ["Nuevo Autor"],
            "is_complete": True
        },
    headers={
        "Authorization": f"Bearer {token_usuario_comun}"
    })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario no existe"
    
def test_books_post_libro_ya_existe(client, token_admin, libro_de_prueba):
    resp = client.post('/books', 
        json={
            "isbn": "9788471532688",
            "title": "Nuevo Libro",
            "editorial": "Nueva Editorial",
            "autores": ["Nuevo Autor"],
            "is_complete": True
        },
    headers={
        "Authorization": f"Bearer {token_admin}"
    })
    
    assert resp.status_code == 409
    assert "Ya existe" in resp.get_json()["error"]
    
def test_books_post_integrity_error(client, token_admin):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        resp = client.post('/books',
            json={
                "isbn": "9780123456789",
                "title": "Nuevo Libro",
                "editorial": "Nueva Editorial",
                "autores": ["Nuevo Autor"],
                "is_complete": True
            },
            headers={
                "Authorization":f"Bearer {token_admin}"
            })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Algo salió mal en la creación del libro"
    
def test_books_post_libro_creado(client, token_admin, app):
    resp = client.post('/books',
        json={
            "isbn": "9780123456789",
            "title": "Nuevo Libro",
            "editorial": "Nueva Editorial",
            "autores": ["Nuevo Autor1","Nuevo Autor2"],
            "is_complete": True
        },
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    data = resp.get_json()
    assert resp.status_code == 201, resp.get_data(as_text=True)
    lista_autores = [f["nombre"] for f in data["autores"]]
    
    with app.app_context():
        assert Libro.query.count() == 1
        assert Autor.query.count() == 2
        assert Editorial.query.count() == 1
        
    assert data["isbn"] == "9780123456789"
    assert data["editorial"]["nombre"] == "Nueva Editorial"
    assert "Nuevo Autor1" in lista_autores
    assert "Nuevo Autor2" in lista_autores
    
# PUT books/ sin permiso
def test_books_put_json_sin_body(client, token_usuario_comun, libro_de_prueba):
    resp = client.put(f'/books/{libro_de_prueba}', 
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_books_put_usuario_inexistente(client, usuario_de_prueba, token_usuario_comun, app, libro_de_prueba):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"",
            "year_publication":"",
            "clasificacion":"",
            "editorial_id":"",
            "autor_ids":[""]
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_books_put_usuario_no_admin(client, token_usuario_comun, libro_de_prueba):
        
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"",
            "year_publication":"",
            "clasificacion":"",
            "editorial_id":"",
            "autor_ids":[""]
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "no tienes permiso para realizar esta accion"
    
def test_books_put_usuario_libro_inexistente(client, token_admin):
        
    resp = client.put('/books/0000000000000',
        json={
            "title" :"",
            "year_publication":"",
            "clasificacion":"",
            "editorial_id":"",
            "autor_ids":[""]
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 404
    assert "NO existe" in resp.get_json()["error"]
    
def test_books_put_usuario_argumentos_vacios(client, token_admin, libro_de_prueba):
        
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"     ",
            "year_publication": 2000,
            "clasificacion":"     ",
            "editorial_id": 1,
            "autor_ids":[1]
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert "debe ser valido" in resp.get_json()["error"]
    
def test_books_put_year_no_numerico(client, token_admin, libro_de_prueba):
        
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"Nuevo Titulo",
            "year_publication": "f",
            "clasificacion":"Nueva Clasificacion",
            "editorial_id": "1",
            "autor_ids":["1", "2"]
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert "publicacion debe ser valido" in resp.get_json()["error"]
    
def test_books_put_clasificacion_vacia(client, token_admin, libro_de_prueba):
        
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"Nuevo Titulo",
            "year_publication": "2001",
            "clasificacion":"     ",
            "editorial_id": "1",
            "autor_ids":["1", "2"]
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert "clasificacion debe ser valido" in resp.get_json()["error"]
    
def test_books_put_editorial_id_inexistente(client, token_admin, libro_de_prueba):
        
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"Nuevo Titulo",
            "year_publication": "2001",
            "clasificacion":"Nueva Clasificacion",
            "editorial_id": "100",
            "autor_ids":["1", "2"]
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Editorial No existe"
    
def test_books_put_autores_ids_no_en_lista(client, token_admin, libro_de_prueba):
        
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"Nuevo Titulo",
            "year_publication": "2001",
            "clasificacion":"Nueva Clasificacion",
            "editorial_id": "1",
            "autor_ids": "1",
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "autor_ids debe ser una lista"
    
def test_books_put_autores_ids_inexistentes(client, token_admin, libro_de_prueba):
        
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"Nuevo Titulo",
            "year_publication": "2001",
            "clasificacion":"Nueva Clasificacion",
            "editorial_id": "1",
            "autor_ids": ["100"],
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El Autor NO Existe"
    
def test_books_put_completo(client, token_admin, libro_de_prueba, app):
    with app.app_context():
        autor = Autor(
            nombre = "Cain"
        )
        db.session.add(autor)
        db.session.commit()
        autors = autor.id
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"Nuevo Titulo",
            "year_publication": "2001",
            "clasificacion":"Nueva Clasificacion",
            "editorial_id": "1",
            "autor_ids": [autors],
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 8
    assert data["title"] == "Nuevo Titulo"
    assert data["clasificacion"] == "Nueva Clasificacion"
    assert data["autores"][0]["id"] == autors
    
    
def test_books_put_datos_parciales(client, token_admin, libro_de_prueba, app):
    resp = client.put(f'/books/{libro_de_prueba}',
        json={
            "title" :"Nuevo Titulo",
            "clasificacion":"Nueva Clasificacion",
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 8
    assert data["title"] == "Nuevo Titulo"
    assert data["clasificacion"] == "Nueva Clasificacion"
    
# DELETE books/<isbn>
def test_books_delete_usuario_no_exite(client, usuario_de_prueba, token_usuario_comun, app, libro_de_prueba):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
    
    resp = client.delete(f'/books/{libro_de_prueba}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_books_delete_usaurio_no_admin(client, token_usuario_comun, libro_de_prueba):
    resp = client.delete(f'/books/{libro_de_prueba}',
            headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "no tienes permiso para realizar esta accion"
    
def test_books_delete_libro_inexistente(client, token_admin):
    resp = client.delete('/books/0000000000000',
            headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 404
    assert "NO existe" in resp.get_json()["error"]
    
def test_books_delete_integrity_error(client, token_admin, libro_de_prueba):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        resp = client.delete(f'/books/{libro_de_prueba}',
            headers={
                "Authorization":f"Bearer {token_admin}"
            })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Algo salió mal en la eliminación del libro"
    
def test_books_delete_completo(client, token_admin, libro_de_prueba, app):
    resp = client.delete(f'/books/{libro_de_prueba}',
            headers={
                "Authorization": f"Bearer {token_admin}"
            })
    
    assert resp.status_code == 204
    with app.app_context():
        assert Libro.query.filter_by(isbn=libro_de_prueba).first() is None