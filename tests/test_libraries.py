from models import (Biblioteca, Usuario, Asignacion)
from extensions import db

# GET libraries/
def test_libraries_get_all(client, biblioteca_de_prueba):
    resp = client.get('/libraries')
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == biblioteca_de_prueba["id"]
    assert data[0]["es_publica"] is True
    assert data[0]["estado_activo"] is True
    
def test_libraries_get_no_incluye_privadas(client, biblioteca_de_prueba, biblioteca_privada_de_prueba):
    resp = client.get('/libraries')
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1  # solo la pública
    
def test_libraries_get_con_filtro(client, biblioteca_de_prueba):
    resp = client.get('/libraries', query_string={
        "address": "calle 1"
    })
    
    data = resp.get_json()
    assert resp.status_code == 200
    assert data[0]["direccion"] == biblioteca_de_prueba["address"]
    
def test_libraries_get_sin_resultados(client, biblioteca_de_prueba):
    resp = client.get('/libraries', query_string={
        "address": "direccion inexistente"
    })
    assert resp.status_code == 200
    assert resp.get_json() == []
    
# GET libraries/<id>
def test_libraries_get_id_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun, biblioteca_de_prueba):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
    
    resp = client.get(f'/libraries/{biblioteca_de_prueba["id"]}',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario no existe"
    
def test_libraries_get_id_biblioteca_inexistente(client, token_usuario_comun):
    resp = client.get('/libraries/10000',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "La Biblioteca No Existe"
    
def test_libraries_get_id_biblioteca_inactiva(client, app, token_usuario_comun, biblioteca_de_prueba):
    with app.app_context():
        b=db.session.get(Biblioteca, biblioteca_de_prueba["id"])
        b.is_active = False
        db.session.commit()
        
    resp = client.get(f'/libraries/{biblioteca_de_prueba["id"]}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "la Biblioteca no está disponible"
    
def test_libraries_get_id_biblioteca_privada(client, token_usuario_comun, biblioteca_privada_de_prueba):
    resp = client.get(f'/libraries/{biblioteca_privada_de_prueba["id"]}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "No puedes ver esta Biblioteca"
    
def test_libraries_get_id_completo(client, token_usuario_comun, biblioteca_de_prueba):
    resp = client.get(f'/libraries/{biblioteca_de_prueba["id"]}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["id"] == biblioteca_de_prueba["id"]
    assert data["estado_activo"] == True
    assert data["es_publica"] == True
    
# GET libraries/mine
def test_libraries_get_mine_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.get('/libraries/mine',
        headers={
            "Authorization" : f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_libraries_get_mine_consulta_exitosa(client, app, 
        token_usuario_comun, usuario_de_prueba, biblioteca_de_prueba, roles_de_prueba):
    with app.app_context():
        asignacion = Asignacion(
            usuario_id = usuario_de_prueba["id"],
            rol_id = roles_de_prueba["lector"],
            biblioteca_id = biblioteca_de_prueba["id"]
        )
        db.session.add(asignacion)
        db.session.commit()
        
    resp = client.get('/libraries/mine',
            headers={
                "Authorization" : f"Bearer {token_usuario_comun}"
            })
        
    data = resp.get_json()
    assert resp.status_code == 200
    assert data[0]["id"] == biblioteca_de_prueba["id"]
    
    
def test_libraries_get_mine_consulta_exitosa_sin_asignaciones(client, 
        token_usuario_comun, biblioteca_de_prueba):
    resp = client.get('/libraries/mine',
            headers={
                "Authorization" : f"Bearer {token_usuario_comun}"
            })
        
    data = resp.get_json()
    assert resp.status_code == 200
    assert data == []