from models import Usuario, Libro
from extensions import db

# GET / prestamos
def test_prestamos_get_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.get('/prestamos', 
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El Usuario No existe"
    
def test_prestamos_get_usuario_sin_permiso(client, token_usuario_comun):
    resp = client.get('/prestamos', 
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "No puedes ver esta información"
    
def test_prestamos_get_todos_los_prestamos(client,token_admin, prestamos_de_prueba_bibliotecario, ):
    resp = client.get('/prestamos', 
    headers={
        "Authorization": f"Bearer {token_admin}"
    })
    
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1
    
def test_prestamos_get_todos_los_prestamos_bibliotecario(client,token_bibliotecario, prestamos_de_prueba_admin):
    resp = client.get('/prestamos', 
    headers={
        "Authorization": f"Bearer {token_bibliotecario}"
    })
    
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1
    
# Get / prestamos/mine
def test_prestamos_get_mine_usuario_inexistente(client, app,
        usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
    
    resp = client.get('/prestamos/mine',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_prestamos_get_mine_consulta_exitosa(client, prestamos_de_prueba_bibliotecario, biblioteca_de_prueba, libro_de_prueba, exemplares_de_prueba, token_usuario_comun):
    resp = client.get('/prestamos/mine', 
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1
    