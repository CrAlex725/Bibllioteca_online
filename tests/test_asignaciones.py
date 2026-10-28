from models import (Usuario, Asignacion, Biblioteca)
from extensions import db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

# GET asignaciones/
def test_asignaciones_get_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.get('/asignaciones',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario no existe"
    
def test_asignaciones_get_usuario_sin_asignaciones(client, token_usuario_comun):
    resp = client.get('/asignaciones',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "No tienes permiso"
    
def test_asignaciones_get_consulta_de_usuario_fallida(client, token_admin):
    resp = client.get('/asignaciones', query_string={
        "usuario_id" : "usuarioX"
    },
    headers={
        "Authorization":f"Bearer {token_admin}"
    })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"]== "el valor solicitado debe ser entero"
    
def test_asignaciones_get_consulta_de_bibliotecas(client, token_admin):
    resp = client.get('/asignaciones', query_string={
        "biblioteca_id" : "BibliotecaY"
    },
    headers={
        "Authorization":f"Bearer {token_admin}"
    })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"]== "el valor solicitado debe ser entero"
    
def test_asignaciones_get_consulta_de_rol(client, token_admin):
    resp = client.get('/asignaciones', query_string={
        "rol_id" : "RolZ"
    },
    headers={
        "Authorization":f"Bearer {token_admin}"
    })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"]== "el valor solicitado debe ser entero"
    
def test_asignaciones_get_consulta_exitosa_con_todos_los_parametros_admin(client, 
        token_admin, usuario_de_prueba_bibliotecario, biblioteca_de_prueba, asignacion_bibliotecario_de_prueba, roles_de_prueba):
    resp = client.get('/asignaciones', query_string={
        "usuario_id" : usuario_de_prueba_bibliotecario["id"],
        "biblioteca_id": biblioteca_de_prueba["id"],
        "rol_id": roles_de_prueba["bibliotecario"],
        "usuario_rut": "22.222.222-2",
        "is_owner": True
    },
    headers={
        "Authorization":f"Bearer {token_admin}"
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["biblioteca"]["id"] == biblioteca_de_prueba["id"]
    assert data[0]["usuario"]["id"] == usuario_de_prueba_bibliotecario["id"]
    assert data[0]["rol"]["id"] == roles_de_prueba["bibliotecario"]

def test_asignaciones_get_admin_ve_todas(client, token_admin, 
        asignacion_bibliotecario_de_prueba):
    resp = client.get('/asignaciones', 
    headers={
        "Authorization": f"Bearer {token_admin}"
    })
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1
    
def test_asignaciones_get_jefe_ve_su_biblioteca(client, token_bibliotecario, 
        asignacion_bibliotecario_de_prueba):
    resp = client.get('/asignaciones', 
    headers={
        "Authorization": f"Bearer {token_bibliotecario}"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(a["biblioteca"]["id"] == asignacion_bibliotecario_de_prueba["biblioteca_id"] for a in data)
    
def test_asignaciones_get_lector_de_bibliotecas(client, app,
    usuario_de_prueba, token_usuario_comun, biblioteca_de_prueba, roles_de_prueba):
    with app.app_context():
        asignacion = Asignacion(
            usuario_id = usuario_de_prueba["id"],
            biblioteca_id = biblioteca_de_prueba["id"],
            rol_id = roles_de_prueba["lector"]
        )
        db.session.add(asignacion)
        db.session.commit()
    resp = client.get('/asignaciones', 
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["biblioteca"]["id"] == biblioteca_de_prueba["id"]
    assert data[0]["usuario"]["id"] == usuario_de_prueba["id"]
    assert data[0]["rol"]["id"] == roles_de_prueba["lector"]
    
def test_asignaciones_get_admin_filtro_is_owner(client, app, token_admin, 
        asignacion_bibliotecario_de_prueba):
    with app.app_context():
        asi = db.session.get(Asignacion, asignacion_bibliotecario_de_prueba["id"])
        asi.is_owner =False
        db.session.commit()
        
    resp = client.get('/asignaciones', query_string={
        "is_owner" : False
    },
    headers={
        "Authorization": f"Bearer {token_admin}"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data[0]["is_owner"] == False
    
def test_asignaciones_get_admin_ve_todas_filtro_error_is_owner(client, token_admin, 
        asignacion_bibliotecario_de_prueba):
    resp = client.get('/asignaciones', query_string={
        "is_owner" : "verdadero"
    },
    headers={
        "Authorization": f"Bearer {token_admin}"
    })
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "is_owner, debe ser true o false"
    
# GET asignaciones/<id>
def test_asignaciones_get_id_usuario_inexistente(client, app, usuario_de_prueba, 
    asignacion_bibliotecario_de_prueba, token_usuario_comun):
    with app.app_context():
        u=db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
    
    resp = client.get(f'/asignaciones/{asignacion_bibliotecario_de_prueba["id"]}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_asignaciones_get_id_asignacion_inexistente(client, token_usuario_comun):
    resp = client.get('/asignaciones/99999',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
        
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "La asignacion No existe"
    
def test_asignaciones_get_id_consulta_exitosa_bibliotecario(client, biblioteca_de_prueba, 
        token_bibliotecario, usuario_de_prueba_bibliotecario, roles_de_prueba):
    resp = client.get(f'/asignaciones/{biblioteca_de_prueba["id"]}',
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["usuario"]["id"] == usuario_de_prueba_bibliotecario["id"]
    assert data["biblioteca"]["id"] == biblioteca_de_prueba["id"]
    assert data["rol"]["id"] == roles_de_prueba["bibliotecario"]
    
def test_asignaciones_get_id_consulta_fallida_bibliotecario_otra_biblioteca(client, app, biblioteca_de_prueba, 
        token_bibliotecario, roles_de_prueba, usuario_de_prueba):
    with app.app_context():
        biblioteca = Biblioteca(
            name = "Nueva Biblioteca2",
            address = "Direccion 2",
            phone = "+56999345123",
            email = "email_nueva_biblioteca@gmail.com",
            is_public = False,
            is_active = True,
            created_by = usuario_de_prueba["id"]
        )
        db.session.add(biblioteca)
        db.session.commit()
        asignacion = Asignacion(
            usuario_id = usuario_de_prueba["id"],
            biblioteca_id = biblioteca.id,
            rol_id=roles_de_prueba["bibliotecario"]
        )
        db.session.add(asignacion)
        db.session.commit()
        asignacion_id = asignacion.id
        
    resp = client.get(f"/asignaciones/{asignacion_id}",
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "No tienes permiso para realizar esta accion"
    
def test_asignaciones_get_id_consulta_exitosa_lector(client, app, biblioteca_de_prueba, 
        token_usuario_comun, usuario_de_prueba, roles_de_prueba):
    with app.app_context():
        asignacion = Asignacion(
            usuario_id = usuario_de_prueba["id"],
            biblioteca_id = biblioteca_de_prueba["id"],
            rol_id = roles_de_prueba["lector"]
        )
        db.session.add(asignacion)
        db.session.commit()
        
        resp = client.get(f'/asignaciones/{asignacion.id}',
            headers={
                "Authorization": f"Bearer {token_usuario_comun}"
            })
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["usuario"]["id"] == usuario_de_prueba["id"]
        assert data["biblioteca"]["id"] == biblioteca_de_prueba["id"]
        assert data["rol"]["id"] == roles_de_prueba["lector"]
    
def test_asignaciones_get_id_consulta_exitosa_admin(client, biblioteca_de_prueba, roles_de_prueba,
        token_admin, asignacion_bibliotecario_de_prueba, usuario_de_prueba_bibliotecario):
    resp = client.get(f'/asignaciones/{asignacion_bibliotecario_de_prueba["id"]}',
        headers={
            "Authorization":f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["usuario"]["id"] == usuario_de_prueba_bibliotecario["id"]
    assert data["biblioteca"]["id"] == biblioteca_de_prueba["id"]
    assert data["rol"]["id"] == roles_de_prueba["bibliotecario"]
    
def test_asignaciones_get_id_usuario_sin_asignacion(client, token_usuario_comun, asignacion_bibliotecario_de_prueba):
    resp = client.get(f'/asignaciones/{asignacion_bibliotecario_de_prueba["id"]}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "No tienes permiso para realizar esta accion"
    
# POST /asignaciones
def test_asignaciones_post_json_invalido(client, token_usuario_comun):
    resp = client.post('/asignaciones', 
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON inválido o vacío"
    
def test_asignaciones_post_datos_faltantes(client, token_usuario_comun, usuario_de_prueba, biblioteca_de_prueba, roles_de_prueba):
    resp = client.post('/asignaciones', 
        json={
            "usuario_id": None,
            "biblioteca_id": biblioteca_de_prueba["id"],
            "rol_id": roles_de_prueba["bibliotecario"]
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert "Faltan campos obligatorios" in resp.get_json()["error"]
    
def test_asignaciones_post_datos_enteros(client, token_usuario_comun, biblioteca_de_prueba, roles_de_prueba):
    resp = client.post('/asignaciones', 
        json={
            "usuario_id":"uno",
            "biblioteca_id": biblioteca_de_prueba["id"],
            "rol_id": roles_de_prueba["lector"],
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Todos los datos deben ser enteros"
    
def test_asignaciones_post_consulta_usaurio_inexistente(client, app, usuario_de_prueba, biblioteca_de_prueba, roles_de_prueba, token_usuario_comun):
    with app.app_context():
        u=db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.post('/asignaciones', 
        json={
            "usuario_id": usuario_de_prueba["id"],
            "biblioteca_id": biblioteca_de_prueba["id"],
            "rol_id": roles_de_prueba["lector"]
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_asignaciones_post_usuario_sin_permiso(client, usuario_de_prueba, biblioteca_de_prueba, roles_de_prueba, token_usuario_comun):
    resp = client.post('/asignaciones', 
        json={
            "usuario_id": usuario_de_prueba["id"],
            "biblioteca_id": biblioteca_de_prueba["id"],
            "rol_id": roles_de_prueba["lector"]
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "No tienes permiso para realizar esta accion"
    
def test_asignaciones_post_biblioteca_inexistente(client, usuario_de_prueba, token_admin, roles_de_prueba):
    resp = client.post('/asignaciones',
        json={
            "usuario_id": usuario_de_prueba["id"],
            "biblioteca_id": 999,
            "rol_id": roles_de_prueba["lector"]
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "La biblioteca NO existe"
    
def test_asignaciones_post_usaurio_inexistente(client, token_bibliotecario, biblioteca_de_prueba, roles_de_prueba):
    resp = client.post('/asignaciones',
        json={
            "usuario_id": 9999,
            "biblioteca_id": biblioteca_de_prueba["id"],
            "rol_id": roles_de_prueba["lector"]
        },
        headers={
            "Authorization":f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El usuario NO existe"
    
def test_asignaciones_post_biblioteca_inactiva(client, app, token_bibliotecario, roles_de_prueba, usuario_de_prueba, biblioteca_de_prueba):
    with app.app_context():
        b = db.session.get(Biblioteca, biblioteca_de_prueba["id"])
        b.is_active = False
        db.session.commit()
        
    resp = client.post('/asignaciones',
        json={
            "usuario_id" : usuario_de_prueba["id"],
            "biblioteca_id" : biblioteca_de_prueba["id"],
            "rol_id" : roles_de_prueba["lector"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "La biblioteca NO está activa"
    
def test_asignaciones_post_rol_inexistente(client, usuario_de_prueba, biblioteca_de_prueba, token_bibliotecario, roles_de_prueba):
    resp = client.post('/asignaciones',
        json={
            "usuario_id": usuario_de_prueba["id"],
            "biblioteca_id": biblioteca_de_prueba["id"],
            "rol_id": 10
        },
        headers={
            "Authorization":f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El rol NO existe"
    
def test_asignaciones_post_no_bibliotecario(client, usuario_de_prueba, biblioteca_de_prueba, token_bibliotecario, roles_de_prueba):
    resp = client.post('/asignaciones',
        json={
            "usuario_id": usuario_de_prueba["id"],
            "biblioteca_id": biblioteca_de_prueba["id"],
            "rol_id": roles_de_prueba["bibliotecario"]
        },
        headers={
            "Authorization":f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"]== "El rol NO puede ser bibliotecario"
    
def test_asignaciones_post_asignacion_ya_existente(client, app, usuario_de_prueba, biblioteca_de_prueba, roles_de_prueba, token_bibliotecario):
    with app.app_context():
        asig = Asignacion(
            usuario_id = usuario_de_prueba["id"],
            biblioteca_id = biblioteca_de_prueba["id"],
            rol_id = roles_de_prueba["lector"]
        )
        db.session.add(asig)
        db.session.commit()
    
    resp = client.post('/asignaciones',
        json={
            "usuario_id" : usuario_de_prueba["id"],
            "biblioteca_id" : biblioteca_de_prueba["id"],
            "rol_id" : roles_de_prueba["lector"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Ya existe una asignacion en esta biblioteca"
    
def test_asignaciones_post_Integrity_error(client, token_bibliotecario, usuario_de_prueba, biblioteca_de_prueba, roles_de_prueba):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        resp = client.post('/asignaciones',
            json={
                "usuario_id" : usuario_de_prueba["id"],
                "biblioteca_id" : biblioteca_de_prueba["id"],
                "rol_id" : roles_de_prueba["lector"]
            },
            headers={
                "Authorization": f"Bearer {token_bibliotecario}"
            })
        
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Algo salió mal durante el proceso de asignar"
    
def test_asignaciones_post_asignacion_completa(client, usuario_de_prueba, biblioteca_de_prueba, roles_de_prueba, token_bibliotecario):
    resp = client.post('/asignaciones',
        json={
            "usuario_id" : usuario_de_prueba["id"],
            "biblioteca_id" : biblioteca_de_prueba["id"],
            "rol_id" : roles_de_prueba["lector"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 201
    data = resp.get_json()
    assert len(data) == 5
    assert data["biblioteca"]["name"] == biblioteca_de_prueba["name"]
    assert data["usuario"]["name"] == usuario_de_prueba["name"]
    
