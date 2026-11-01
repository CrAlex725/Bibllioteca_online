from models import (Editorial, Usuario)
from extensions import db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

# GET editorials/
def test_editorials_get_toda_las_editoriales_con_token(client, token_usuario_comun, editoriales_de_prueba):
    resp = client.get('/editorials',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == len(editoriales_de_prueba)
    
def test_editorials_get_toda_las_editoriales_sin_token(client, editoriales_de_prueba):
    resp = client.get('/editorials',)
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == len(editoriales_de_prueba)
    
def test_editorials_get_con_filtro_parcial(client, editoriales_de_prueba):
    resp = client.get('/editorials', query_string={
        "nombre": "zig"
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    
def test_editorials_get_con_filtro_completo(client, editoriales_de_prueba):
    resp = client.get('/editorials', query_string={
        "nombre": editoriales_de_prueba["Zig Zag"]["nombre"]
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    
# GET editorials/<id>
def test_editorials_get_id_exitosa_con_token(client, editoriales_de_prueba, token_usuario_comun):
    resp = client.get(f'/editorials/{editoriales_de_prueba["Zig Zag"]["id"]}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["nombre"] == editoriales_de_prueba["Zig Zag"]["nombre"]
    assert data["id"] == editoriales_de_prueba["Zig Zag"]["id"]
    
def test_editorials_get_id_exitosa_sin_token(client, editoriales_de_prueba):
    resp = client.get(f'/editorials/{editoriales_de_prueba["Zig Zag"]["id"]}')
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["nombre"] == editoriales_de_prueba["Zig Zag"]["nombre"]
    assert data["id"] == editoriales_de_prueba["Zig Zag"]["id"]
    
def test_editorials_get_id_inexistente(client, token_usuario_comun):
    resp = client.get(f'/editorials/999999',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "La editorial no existe"
    
# POST editorials/
def test_editorials_post_sin_token(client):
    resp = client.post('/editorials', json={
        "nombre": "Nueva Editorial"
    })
    
    assert resp.status_code == 401
    
def test_editorials_post_json_invalido(client, token_admin):
    resp = client.post('/editorials',
        json=None,
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_editorials_post_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.post('/editorials',
        json={
            "nombre" : "Nueva Editorial"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario no existe"
    
def test_editorials_post_usuario_sin_permiso(client, token_usuario_comun):
    resp = client.post('/editorials',
        json={
            "nombre": "Nueva Editorial"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "No tienes permiso" in resp.get_json()["error"]
    
def test_editorials_post_sin_dato_entregado(client, token_bibliotecario):
    resp = client.post('/editorials',
        json={
            "nombre" : "     "
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "debes entregar un nombre para la nueva editorial"
    
def test_editorials_post_editorial_existente(client, token_bibliotecario, editoriales_de_prueba):
    resp = client.post('/editorials',
        json={
            "nombre": editoriales_de_prueba["Zig Zag"]["nombre"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "LA editorial ya existe"
    
def test_editorials_post_IntegrityError(client, token_bibliotecario):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        resp = client.post('/editorials',
            json={
                "nombre": "Nueva editorial"
            },
            headers={
                "Authorization": f"Bearer {token_bibliotecario}"
            })
        
    assert resp.status_code == 500
    assert "Algo salió mal" in resp.get_json()["error"]
    
def test_editorials_post_creacion_exitosa(client, token_bibliotecario):
    resp = client.post('/editorials',
        json={
            "nombre" : "Nueva Editorial"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["nombre"] == "Nueva Editorial"
    
