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
    
# PUT / profile/complete
def test_profile_complete_usuario_inexistente(client, app, usuario_de_prueba_perfil_incompleto, token_usuario_incompleto):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba_perfil_incompleto["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.put('/auth/profile/completer',
        json={
            "username":"Nuevo_Usuario",
            "phone":"988345002",
            "rut":"20.222.883-7",
            "address":"Direccion A113",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Usuario No existe"
    
def test_profile_complete_sin_token(client, app, token_usuario_incompleto, usuario_de_prueba_perfil_incompleto):
    resp = client.put('/auth/profile/completer',
        json={
            "phone":"988345002",
            "rut":"20.222.883-7",
            "address":"Direccion A113",
        })
    
    assert resp.status_code == 401

def test_profile_complete_json_invalido(client, token_usuario_incompleto):
    resp = client.put('/auth/profile/completer',
        json=None,
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_profile_complete_username_invalido(client, token_usuario_incompleto):
    resp = client.put('/auth/profile/completer',
        json={
            "username":"",
            "phone":"988345002",
            "rut":"20.222.883-7",
            "address":"Direccion A113",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El username debe ser valido"
    
def test_profile_complete_username_en_uso(client, token_usuario_incompleto, usuario_de_prueba):
    resp = client.put('/auth/profile/completer',
        json={
            "username": usuario_de_prueba["username"],
            "phone":"988345002",
            "rut":"20.222.883-7",
            "address":"Direccion A113",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El nombre de usuario Ya existe"
    
def test_profile_complete_phone_invalido(client, token_usuario_incompleto):
    resp = client.put('/auth/profile/completer',
        json={
            "username":"Nuevo_Usuario",
            "phone":"",
            "rut":"20.222.883-7",
            "address":"Direccion A113",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El telefono debe ser valido"
    
def test_profile_complete_phone_en_uso(client, token_usuario_incompleto, usuario_de_prueba):
    resp = client.put('/auth/profile/completer',
        json={
            "username":"Nuevo_Usuario",
            "phone":usuario_de_prueba["phone"],
            "rut":"20.222.883-7",
            "address":"Direccion A113",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El numero telefonico esta en uso"
    
def test_profile_complete_rut_invalido(client, token_usuario_incompleto):
    resp = client.put('/auth/profile/completer',
        json={
            "username":"Nuevo_Usuario",
            "phone":"988345002",
            "rut":"",
            "address":"Direccion A113",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El rut debe ser valido"
    
def test_profile_complete_rut_en_uso(client, token_usuario_incompleto, usuario_de_prueba):
    resp = client.put('/auth/profile/completer',
        json={
            "username":"Nuevo_Usuario",
            "phone":"988345002",
            "rut": usuario_de_prueba["rut"],
            "address":"Direccion A113",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El rut Ya esta en uso"
    
def test_profile_complete_address_invalido(client, token_usuario_incompleto):
    resp = client.put('/auth/profile/completer',
        json={
            "username":"Nuevo_Usuario",
            "phone":"988345002",
            "rut":"20.222.883-7",
            "address":"",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "La direccion debe ser valida"
    
def test_profile_complete_password_invalido(client, token_usuario_incompleto):
    resp = client.put('/auth/profile/completer',
        json={
            "username":"Nuevo_Usuario",
            "phone":"988345002",
            "rut":"20.222.883-7",
            "address":"Direccion A113",
            "password":""
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "La contraseña no puede estar vacía"
    
def test_profile_complete_actualizar_todos_los_campos(client, app, token_usuario_incompleto, usuario_de_prueba_perfil_incompleto):
    resp = client.put('/auth/profile/completer',
        json={
            "username":"Nuevo_Usuario",
            "phone":"988345002",
            "rut":"20.222.883-7",
            "address":"Direccion A113",
            "password":"Nueva_contraseña"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user_name"] == "Nuevo_Usuario"
    assert data["phone"] == "988345002"
    assert data["rut"] == "20.222.883-7"
    assert data["address"] == "Direccion A113"
    
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba_perfil_incompleto["id"])
        check = u.check_password("Nueva_contraseña")
        
    assert check == True
    
def test_profile_complete_actualizar_campos_parciales(client, app, token_usuario_incompleto, usuario_de_prueba_perfil_incompleto):
    resp = client.put('/auth/profile/completer',
        json={
            "phone":"988345002",
            "rut":"20.222.883-7",
            "address":"Direccion A113",
        },
        headers={
            "Authorization":f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba_perfil_incompleto["id"])
        phone = u.phone
        rut = u.rut
        address = u.address
        
    assert data["phone"] == phone
    assert data["rut"] == rut
    assert data["address"] == address
