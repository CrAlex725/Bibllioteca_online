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
    
def test_register_Completo(client, app):
    datos = {
        "email": "ab.cdef.123@gmail.com",
        "username": "abcdefghij",
        "name": "Abcdefghij",
        "password": "123456789"
    }
    
    resp = client.post('/auth/register', json=datos)
    assert resp.status_code == 201
    assert "Se creó Correctamente" in resp.get_json()['status']