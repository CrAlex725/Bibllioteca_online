from models import (Biblioteca, Usuario, Asignacion, Rol)
from extensions import db
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError

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
    
# POST libraries/
def test_libraries_post_sin_token(client):
    resp = client.post('/libraries', json={})
    assert resp.status_code == 401
    
def test_libraries_post_json_invalido(client, token_usuario_incompleto):
    resp = client.post('/libraries', 
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_libraries_post_usuario_inexistente(client, app, usuario_de_prueba_perfil_incompleto, token_usuario_incompleto):
    with app.app_context():
        u=db.session.get(Usuario, usuario_de_prueba_perfil_incompleto["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.post('/libraries', 
        json={
            "name" :"Nombre1",
            "address" :"Direccion1",
            "phone" :"982234567",
            "email" :"email@gmail.com",
            "is_public" : True
        },
        headers={
            "Authorization": f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario no existe"
    
def test_libraries_post_usuario_incompleto(client, token_usuario_incompleto):
    resp = client.post('/libraries', 
        json={
            "name" :"Nombre1",
            "address" :"Direccion1",
            "phone" :"982234567",
            "email" :"email@gmail.com",
            "is_public" : True
        },
        headers={
            "Authorization": f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "El usuario no tiene los datos completos"
    
def test_libraries_post_datos_incompletos(client, token_usuario_comun):
    resp = client.post('/libraries', 
        json={
            "name" : None,
            "address" :"Direccion1",
            "phone" : "982234567",
            "email" :"email@gmail.com",
            "is_public" : True
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Uno de los datos no fue otorgados"
    
def test_libraries_post_is_public_ausente(client, token_usuario_comun):
    resp = client.post('/libraries', 
        json={
            "name" :"Nombre1",
            "address" :"Direccion1",
            "phone" :"982234567",
            "email" :"email@gmail.com",
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Uno de los datos no fue otorgados"
    
def test_libraries_post_verificar_propietario(client, token_bibliotecario, biblioteca_de_prueba):
    resp = client.post('/libraries', 
        json={
            "name" :"Nombre1",
            "address" :"Direccion1",
            "phone" :"982234567",
            "email" :"email@gmail.com",
            "is_public": True
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "El usuario ya es jefe de una biblioteca activa"
    
def test_libraries_post_rol_inexistente(client, token_usuario_comun, roles_de_prueba):
    with patch('routes.libraries.Rol') as mock_rol:
        mock_rol.query.filter_by.return_value.first.return_value = None
        
        resp = client.post('/libraries', 
            json={
                "name" :"Nombre1",
                "address" :"Direccion1",
                "phone" :"982234567",
                "email" :"email@gmail.com",
                "is_public": True
            },
            headers={
                "Authorization": f"Bearer {token_usuario_comun}"
            })
        
        assert resp.status_code == 500
        assert resp.get_json()["error"] == "El rol solicitado no está disponible"
    
def test_libraries_post_integrity_error(client, token_usuario_comun, roles_de_prueba):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        
        resp = client.post('/libraries', 
            json={
                "name" :"Nombre1",
                "address" :"Direccion1",
                "phone" :"982234567",
                "email" :"email@gmail.com",
                "is_public": True
            },
            headers={
                "Authorization": f"Bearer {token_usuario_comun}"
            })
    
    assert resp.status_code == 500
    assert "Algo Salió mal" in resp.get_json()["error"]
    
def test_libraries_post_con_biblioteca_inactiva(client, app, token_bibliotecario, biblioteca_de_prueba):
    with app.app_context():
        b = db.session.get(Biblioteca, biblioteca_de_prueba["id"])
        b.is_active = False
        db.session.commit()
        
    resp = client.post('/libraries', 
        json={
            "name" :"Nombre1",
            "address" :"Direccion1",
            "phone" :"982234567",
            "email" :"email@gmail.com",
            "is_public": True
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    data = resp.get_json()
    assert resp.status_code == 201
    assert data["biblioteca"] == "Nombre1"
    assert data["es_publica"] == True
    assert data["estado_activo"] == True
    
def test_libraries_post_primera_creacion_del_usuario(client, app, token_usuario_comun, roles_de_prueba, usuario_de_prueba):
    resp = client.post('/libraries', 
        json={
            "name" :"Nombre1",
            "address" :"Direccion1",
            "phone" :"982234567",
            "email" :"email@gmail.com",
            "is_public": True
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 201, resp.get_data(as_text=True)
    data = resp.get_json()
    assert data["biblioteca"] == "Nombre1"
    assert data["direccion"] == "Direccion1"
    assert data["telefono"] == "982234567"
    assert data["correo"] == "email@gmail.com"
    assert data["es_publica"] is True
    assert data["estado_activo"] is True
    assert data["creado_por"] == usuario_de_prueba["name"]
    
    with app.app_context():
        b = Biblioteca.query.filter_by(name="Nombre1").first()
        assert b is not None
        a = Asignacion.query.filter_by(
            biblioteca_id=b.id, usuario_id=usuario_de_prueba["id"]
        ).first()
        assert a is not None
        assert a.is_owner is True
        assert a.rol_id == roles_de_prueba["bibliotecario"]
    
# PUT libraries/<id>
def test_libraries_put_json_inválido(client, biblioteca_de_prueba, token_usuario_comun):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}', 
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_libraries_put_usuario_inexistente(client, app, biblioteca_de_prueba, token_usuario_comun, usuario_de_prueba):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "name" : "Nuevo Nombre"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario no existe"
    
def test_libraries_put_Biblioteca_inexistente(client, token_usuario_comun):
    resp = client.put('/libraries/99999',
        json={
            "name" : "Nuevo Nombre"
        },
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "La biblioteca NO existe"
    
def test_libraries_put_usuario_sin_permiso(client, biblioteca_de_prueba, token_usuario_comun):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "name": "Nuevo Nombre"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "no tienes permiso para realizar esta accion"
    
def test_libraries_put_usuario_sin_permiso_con_otra_biblioteca(client, app, biblioteca_de_prueba, usuario_de_prueba, token_usuario_comun, roles_de_prueba):
    with app.app_context():
        # crear nueva biblioteca
        bib = Biblioteca(
            name = "Biblioteca u comun",
            address = "Direccion comun",
            phone = "977445550",
            email = "bibliotecaUcomun@test.com",
            created_by = usuario_de_prueba["id"]
        )
        db.session.add(bib)
        db.session.commit()
        # crear nueva asignacion
        asig = Asignacion(
            usuario_id = usuario_de_prueba["id"],
            rol_id = roles_de_prueba["bibliotecario"],
            biblioteca_id = bib.id,
            is_owner = True
        )
        db.session.add(asig)
        db.session.commit()
        
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "name" : "Nuevo Nombre"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "no tienes permiso para realizar esta accion"
    
def test_libraries_put_nombre_vacio(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "name" : "     "
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Dato de nombre invalido"
    
def test_libraries_put_mismo_nombre(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "name" : biblioteca_de_prueba["name"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "el nombre es el mismo que ya tenía"
    
def test_libraries_put_direccion_vacio(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "address" : "     "
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Dato de direccion invalido"
    
def test_libraries_put_misma_direccion(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "address" : biblioteca_de_prueba["address"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "la direccion es la misma que ya tenía"
    
def test_libraries_put_telefono_vacio(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "phone" : "     "
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Dato de telefono invalido"
    
def test_libraries_put_mismo_telefono(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "phone" : biblioteca_de_prueba["phone"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "el telefono es el mismo que ya tenía"
    
def test_libraries_put_no_booleano(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "is_public" : "no booleano"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "el valor debe ser bool"
    
def test_libraries_put_admin(client, biblioteca_de_prueba, token_admin):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "name" : "Nuevo Nombre"
        },
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["biblioteca"] == "Nuevo Nombre"
    
def test_libraries_put_bibliotecario(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "name" : "Nuevo Nombre"
        },
        headers={
            "Authorization":f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["biblioteca"] == "Nuevo Nombre"
    
def test_libraries_put_bibliotecario_multiples_datos(client, biblioteca_de_prueba, token_bibliotecario):
    resp = client.put(f'/libraries/{biblioteca_de_prueba["id"]}',
        json={
            "name" : "Nuevo Nombre",
            "address" : "Nueva Direccion",
            "phone" : "900044478",
            "is_public" : False
        },
        headers={
            "Authorization":f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["biblioteca"] == "Nuevo Nombre"
    assert data["direccion"] == "Nueva Direccion"
    assert data["telefono"] == "900044478"
    assert data["es_publica"] == False