from models import Usuario
from extensions import db

def test_register_sin_json(client):
    resp = client.post('/auth/register', json=None)
    assert resp.status_code == 400
    assert "JSON Invalido o vacío" in resp.get_json()['error']
    
def test_register_con_datos_vacios(client):
    datos = {
        "email": "",
        "username": "",
        "name": "",
        "password": ""
    }
    
    respuesta = client.post('/auth/register', json=datos)
    
    assert respuesta.status_code == 400
    assert respuesta.get_json()["error"] == 'Falta uno de los datos'
    
def test_register_con_datos_espaciados(client):
    datos = {
            "email": "     ",
            "username": "     ",
            "name": "     ",
            "password": "     "
        }
        
    respuesta = client.post('/auth/register', json=datos)
    
    assert respuesta.status_code == 400
    assert respuesta.get_json()["error"] == 'Campos invalidos'
    
def test_register_email_ya_existe(client, app):
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    with app.app_context():
        # Crear Usuario
        user = Usuario(
            email = "ab.cdef.123@gmail.com",
            username = "abcdefghij1",
            name = "Abcdefghij1",
        )
        user.set_password("123456789")
        db.session.add(user)
        db.session.commit()
        
    user2 = client.post('/auth/register', json=datos)
    assert user2.status_code == 409
    assert user2.get_json()["error"] == "El Correo ya existe en la base de datos"
    
def test_register_username_ya_existe(client, app):
    datos = {
        "email": "ab.cdef.123@gmail.com2",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    with app.app_context():
        # Crear Usuario
        user = Usuario(
            email = "ab.cdef.123@gmail.com",
            username = "abcdefghij",
            name = "Abcdefghij",
        )
        user.set_password("123456789")
        db.session.add(user)
        db.session.commit()
        
    user2 = client.post('/auth/register', json=datos)
    assert user2.status_code == 409
    assert user2.get_json()["error"] == "El Usuario No está Disponible"
    
def test_register_Completo(client):
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    
    resp = client.post('/auth/register', json=datos)
    assert resp.status_code == 201
    assert "Se creó Correctamente" in resp.get_json()['status']
    
def test_login_sin_json(client):
    resp = client.post('/auth/login', json=None)
    assert resp.status_code == 400
    assert "No se han proporcionado" in resp.get_json()["error"]
    
def test_login_email_y_password_none(client):
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    
    client.post('/auth/register', json=datos)
    
    datos_ingreso = {
        "email" : None,
        "password" : None
    }
    
    resp = client.post('/auth/login', json=datos_ingreso)
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El Correo y la contraseña deben completarse"
    
def test_login_correo_no_existe(client):
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    
    client.post('/auth/register', json=datos)
    
    datos_ingreso= {
        "email": "ab.cdef.000@gmail.com",
        "password": "123456789"
    }
    resp = client.post('/auth/login', json=datos_ingreso)
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El Usuario o la contraseña Son incorrectos"
    
def test_login_password_incorrecto(client):
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    
    client.post('/auth/register', json=datos)
    
    datos_ingreso= {
        "email": "ab.cdef.123@gmail.com",
        "password": "xxxxxxxxx"
    }
    resp = client.post('/auth/login', json=datos_ingreso)
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El Usuario o la contraseña Son incorrectos"
    
def test_login_email_password_espacios(client):
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    
    client.post('/auth/register', json=datos)
    
    datos_ingreso= {
        "email": "     ",
        "password": "     "
    }
    resp = client.post('/auth/login', json=datos_ingreso)
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El Correo y la contraseña deben ser campos validos"
    
def test_login_funcional(client):
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    
    client.post('/auth/register', json=datos)
    
    datos_ingreso= {
        "email": "ab.cdef.123@gmail.com",
        "password": "123456789"
    }
    resp = client.post('/auth/login', json=datos_ingreso)
    assert resp.status_code == 200
    assert len(resp.get_json()["token"]) > 25
    
def test_profile_usuario_sin_token(client):
    resp = client.get('/auth/profile')
        
    assert resp.status_code == 401
    
def test_profile_usuario_no_existe(client, app):
    # 1. Crear usuario
    client.post('/auth/register', json={
        "email": "temporal@test.com",
        "username": "temporal",
        "name": "Temporal",
        "password": "123456789"
    })
    
    # 2. Login
    resp_login = client.post('/auth/login', json={
        "email": "temporal@test.com",
        "password": "123456789"
    })
    token = resp_login.get_json()["token"]
    
    # 3. Borrar el usuario de la DB
    with app.app_context():
        user = Usuario.query.filter_by(email="temporal@test.com").first()
        db.session.delete(user)
        db.session.commit()
    
    # 4. Usar el token viejo
    resp = client.get('/auth/profile', headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert resp.status_code == 404
    
def test_profile_correcto(client):
    datos = {
            "email": "ab.cdef.123@gmail.com",
            "username": "abcdefghij",
            "name": "Abcdefghij",
            "password": "123456789"
        }
    client.post('/auth/register', json=datos)
    
    # 2. Login para obtener el token
    resp_login = client.post('/auth/login', json={
        "email": "ab.cdef.123@gmail.com",
        "password": "123456789"
    })
    token = resp_login.get_json()["token"]
    
    # 3. Llamar /profile con el token en el header
    resp = client.get('/auth/profile', headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "ab.cdef.123@gmail.com"