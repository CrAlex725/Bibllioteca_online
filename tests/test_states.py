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
    resp = client.get(f'/states/{estados_de_prueba["disponible"]}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    assert resp.get_json()["id"] == estados_de_prueba["disponible"]
    assert resp.get_json()["nombre"] == "disponible"
    
def test_states_get_id_consulta_exitosa_sin_token(client, estados_de_prueba):
    resp = client.get(f'/states/{estados_de_prueba["disponible"]}')
    
    assert resp.status_code == 200
    assert resp.get_json()["id"] == estados_de_prueba["disponible"]
    assert resp.get_json()["nombre"] == "disponible"
    