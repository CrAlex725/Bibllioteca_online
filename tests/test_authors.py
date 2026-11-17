from  models import Autor, Usuario
from extensions import db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

# GET /authors
def test_authors_get_sin_filtro(client, autores_de_prueba, token_usuario_comun):
    resp = client.get('/authors',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    assert len(resp.get_json()) == len(autores_de_prueba)
    
def test_authors_get_con_filtro(client, autores_de_prueba, token_usuario_comun):
    resp = client.get('/authors',
        query_string={
            "nombre":"1"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1
    
# GET /authors/id
def test_authors_id_get_autor_inexistente(client, autores_de_prueba, token_usuario_comun):
    resp = client.get('/authors/100',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El Autor No existe"
    
def test_authors_id_get_autor_existente(client, autores_de_prueba, token_usuario_comun):
    resp = client.get(f'/authors/{autores_de_prueba[1]["id"]}',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    assert resp.status_code == 200
    assert resp.get_json()["nombre"] == autores_de_prueba[1]["nombre"]
    
# POST /authors
def test_authors_post_json_invalido(client, autores_de_prueba, token_usuario_comun):
    resp = client.post('/authors',
        json=None,
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_authors_post_sin_datos(client, autores_de_prueba, token_usuario_comun):
    resp = client.post('/authors',
        json={
            "n": "nuevo Autor"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El nombre de autor es requerido"
    
def test_authors_post_usuario_inexistente(client, app, autores_de_prueba, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.post('/authors',
        json={
            "nombre": "Nuevo Autor"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_authors_post_usuario_sin_permiso(client, autores_de_prueba, token_usuario_comun):
    resp = client.post('/authors',
        json={
            "nombre": "Nuevo Autor"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "No tienes permiso" in resp.get_json()["error"]
    
def test_authors_post_autor_ya_existente(client, autores_de_prueba, token_admin):
    resp = client.post('/authors',
        json={
            "nombre": "Autor 3"
        },
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El autor Ya existe en la db"
    
def test_authors_post_IntegrityError(client, autores_de_prueba, token_admin):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        resp = client.post('/authors',
            json={
                "nombre": "Nuevo Autor"
            },
            headers={
                "Authorization":f"Bearer {token_admin}"
            })
    
    assert resp.status_code == 409
    assert "Algo salió mal" in resp.get_json()["error"]
    
def test_authors_post_exitoso(client, app, autores_de_prueba, token_admin):
    resp = client.post('/authors',
        json={
            "nombre": "Nuevo Autor"
        },
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 201
    with app.app_context():
        au = Autor.query.filter_by(nombre="Nuevo Autor").first()
        assert au is not None
    
# PUT /authors
def test_authors_put_json_invalido(client, autores_de_prueba, token_usuario_comun):
    resp = client.put(f'/authors/{autores_de_prueba[1]["id"]}',
        json=None,
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_authors_put_sin_datos(client, autores_de_prueba, token_usuario_comun):
    resp = client.put(f'/authors/{autores_de_prueba[1]["id"]}',
        json={
            "n": "nuevo Autor"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El nombre de autor es requerido"
    
def test_authors_put_usuario_inexistente(client, app, autores_de_prueba, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.put(f'/authors/{autores_de_prueba[1]["id"]}',
        json={
            "nombre": "Nuevo Autor"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_authors_put_usuario_sin_permiso(client, autores_de_prueba, token_usuario_comun):
    resp = client.put(f'/authors/{autores_de_prueba[1]["id"]}',
        json={
            "nombre": "Nuevo Autor"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "No tienes permiso" in resp.get_json()["error"]
    
def test_authors_put_autor_inexistente(client, autores_de_prueba, token_admin):
    resp = client.put(f'/authors/999',
        json={
            "nombre": "Autor 3"
        },
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El autor No existe en la db"
    
def test_authors_put_autor_existente_en_la_db(client, autores_de_prueba, token_admin):
    resp = client.put(f'/authors/{autores_de_prueba[1]["id"]}',
        json={
            "nombre": "Autor 3"
        },
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El autor Ya existe en la db"
    
def test_authors_put_exitoso(client, app, autores_de_prueba, token_admin):
    resp = client.put(f'/authors/{autores_de_prueba[1]["id"]}',
        json={
            "nombre": "Nuevo Autor"
        },
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 200
    with app.app_context():
        au = Autor.query.filter_by(id=1).first()
        assert au.nombre == "Nuevo Autor"
    
# DELETE /authors
def test_authors_delete_usuario_inexistente(client, app, autores_de_prueba, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.delete(f'/authors/{autores_de_prueba[1]["id"]}',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_authors_delete_usuario_sin_permiso(client, autores_de_prueba, token_usuario_comun):
    resp = client.delete(f'/authors/{autores_de_prueba[1]["id"]}',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "No tienes permiso" in resp.get_json()["error"]
    
def test_authors_delete_autor_inexistente(client, autores_de_prueba, token_admin):
    resp = client.delete(f'/authors/999',
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El autor No existe en la db"
    
def test_authors_delete_IntegrityError(client, autores_de_prueba, token_admin):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        resp = client.delete(f'/authors/{autores_de_prueba[1]["id"]}',
            headers={
                "Authorization":f"Bearer {token_admin}"
            })
    
    assert resp.status_code == 409
    assert "No se puede eliminar" in resp.get_json()["error"]
    
def test_authors_delete_exitoso(client, autores_de_prueba, token_admin):
    resp = client.delete(f'/authors/{autores_de_prueba[1]["id"]}',
        headers={
            "Authorization":f"Bearer {token_admin}"
            })
        
    assert resp.status_code == 204
    au = Autor.query.filter_by(id=autores_de_prueba[1]["id"]).first()
    assert au is None