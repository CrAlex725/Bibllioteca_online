from models import (Usuario, Estado)
from extensions import db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

# GET /states
def test_states_get_todos_los_estados(client, token_usuario_comun, estados_de_prueba):
    resp = client.get('/states',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == len(estados_de_prueba)
    
def test_states_get_filtro_estado_encontrado(client, app,token_usuario_comun, estados_de_prueba):
    resp = client.get('/states', query_string={
        "nombre" : "disponible"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    
def test_states_get_filtro_estado_inexistente(client, token_usuario_comun, estados_de_prueba):
    resp = client.get('/states', query_string={
        "nombre" : "estado_inexistente"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 0
    
def test_states_get_sin_token(client, estados_de_prueba):
    resp = client.get('/states')
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == len(estados_de_prueba)
    
# GET /states/<id>
def test_states_get_id_inexistente(client, token_usuario_comun, estados_de_prueba):
    resp = client.get('/states/999',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El estado asociado al id no existe"
    
def test_states_get_id_consulta_exitosa_con_token(client, token_usuario_comun, estados_de_prueba):
    resp = client.get(f'/states/{estados_de_prueba["disponible"]["id"]}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    assert resp.get_json()["id"] == estados_de_prueba["disponible"]["id"]
    assert resp.get_json()["nombre"] == estados_de_prueba["disponible"]["nombre"]
    
def test_states_get_id_consulta_exitosa_sin_token(client, estados_de_prueba):
    resp = client.get(f'/states/{estados_de_prueba["disponible"]["id"]}')
    
    assert resp.status_code == 200
    assert resp.get_json()["id"] == estados_de_prueba["disponible"]["id"]
    assert resp.get_json()["nombre"] == estados_de_prueba["disponible"]["nombre"]
    
#POST /states/
def test_states_post_json_invalido(client, token_usuario_comun):
    resp = client.post('/states',
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_states_post_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
    
    resp = client.post('/states', 
        json={
            "nombre": "Nuevo_estado"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No Existe"
    
def test_states_post_usuario_invalido(client, token_usuario_comun):
    resp = client.post('/states', 
        json={
            "nombre": "Nuevo_estado"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "No tiene permiso" in resp.get_json()["error"]
    
def test_states_post_dato_no_entregado(client, token_admin):
    resp = client.post('/states', 
        json={
            "parametro_incorrecto": "Nuevo_estado"
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El nombre es obligatorio"
    
def test_states_post_dato_ya_existente(client, token_admin, estados_de_prueba):
    resp = client.post('/states', 
        json={
            "nombre": estados_de_prueba["disponible"]["nombre"]
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El estado ya existe"
    
def test_states_post_IntegrityError(client, app, token_admin, estados_de_prueba):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        
        resp = client.post('/states', 
            json={
                "nombre": "Nuevo Estado"
            },
            headers={
                "Authorization": f"Bearer {token_admin}"
            })
    
    assert resp.status_code == 500
    assert "Algo Salió mal" in resp.get_json()["error"]
    
def test_states_post_creacion_exitosa(client, token_admin, estados_de_prueba):
    resp = client.post('/states', 
        json={
            "nombre": "Nuevo Estado"
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["nombre"] == "Nuevo Estado"
    
# PUT /states/<id>
def test_states_put_id_json_invalido(client, token_usuario_comun, estados_de_prueba):
    resp = client.put(f'/states/{estados_de_prueba["disponible"]["id"]}',
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_states_put_id_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun, estados_de_prueba):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.put(f'/states/{estados_de_prueba["disponible"]["id"]}',
        json={
            "nombre": "Estado Actualizado"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario NO existe"
    
def test_states_put_id_usuario_invalido(client, token_usuario_comun, estados_de_prueba):
    resp = client.put(f'/states/{estados_de_prueba["disponible"]["id"]}',
        json={
            "nombre": "Estado Actualizado"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "No tiene permisos" in resp.get_json()["error"]
    
def test_states_put_id_estado_inexistente(client, token_admin):
    resp = client.put(f'/states/999',
        json={
            "nombre": "Estado Actualizado"
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El estado que buscas NO existe"
    
def test_states_put_id_estado_invalido(client, token_admin, estados_de_prueba):
    resp = client.put(f'/states/{estados_de_prueba["disponible"]["id"]}',
        json={
            "nombre": None
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El nombre es obligatorio"
    
def test_states_put_id_estado_ya_existente(client, token_admin, estados_de_prueba):
    resp = client.put(f'/states/{estados_de_prueba["prestado"]["id"]}',
        json={
            "nombre": estados_de_prueba["disponible"]["nombre"]
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El Estado ya existe"
    
def test_states_put_id_correcto(client, token_admin, estados_de_prueba):
    resp = client.put(f'/states/{estados_de_prueba["disponible"]["id"]}',
        json={
            "nombre": "Accesible"
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 200
    assert resp.get_json()["nombre"] == "Accesible"
    
