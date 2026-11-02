from models import (Libro)

# GET exemplars/ 
def test_exemplars_get_consulta_sin_filtros(client, exemplares_de_prueba, token_usuario_comun):
    resp = client.get('/exemplars',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    assert len(resp.get_json()) == len(exemplares_de_prueba)
    
def test_exemplars_get_filtros_parciales(client, app, exemplares_de_prueba, token_usuario_comun, libro_de_prueba):
    with app.app_context():
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        libro_id = libro.id
        
    resp = client.get('/exemplars', query_string={
        "libro_id": libro_id
    },
    headers={
        "Authorization": f"Bearer {token_usuario_comun}"
    })
    
    assert resp.status_code == 200
    assert len(resp.get_json()) > 0
    
def test_exemplars_get_todos_los_filtros(client, app, exemplares_de_prueba, token_usuario_comun, 
        biblioteca_de_prueba, libro_de_prueba, estados_de_prueba):
    with app.app_context():
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        
    resp = client.get('/exemplars', query_string={
        "libro_id": libro.id,
        "biblioteca_id": biblioteca_de_prueba["id"],
        "estado_id": estados_de_prueba["disponible"]["id"],
        "disponibilidad": True
    },
    headers={
        "Authorization": f"Bearer {token_usuario_comun}"
    })
    
    assert resp.status_code == 200
    assert len(resp.get_json()) > 0
    
# GET exemplars/<id> 
def test_exemplars_get_id_exemplar_inexistente(client, exemplares_de_prueba, token_usuario_comun):
    resp = client.get('/exemplars/9999',
        headers={
            "Authorization" : f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Ejemplar NO encontrado"
    
def test_exemplars_get_id_exemplar_existente(client, exemplares_de_prueba, token_usuario_comun):
    resp = client.get(f'/exemplars/{exemplares_de_prueba[1]["id"]}',
        headers={
            "Authorization" : f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["numero_ejemplar"] == exemplares_de_prueba[1]["numero"]