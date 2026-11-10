from models import Usuario, Libro, Biblioteca, Ejemplar, Prestamo, Asignacion, Rol, Estado
from extensions import db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

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
    
# GET /prestamos/<id>
def test_prestamos_get_id_usuario_inexistente(client, app,
        usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
    
    resp = client.get(f'/prestamos/1',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El Usuario No existe"
    
def test_prestamos_get_id_prestamo_inexistente(client, token_usuario_comun):
    resp = client.get(f'/prestamos/9999',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El Prestamo no Existe"
    
def test_prestamos_get_id_sin_permiso(client, prestamos_de_prueba_bibliotecario, token_usuario_incompleto):
    resp = client.get(f'/prestamos/{prestamos_de_prueba_bibliotecario}',
        headers={
            "Authorization": f"Bearer {token_usuario_incompleto}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "No tienes permiso de realizar esta accion"
    
def test_prestamos_get_id_exitoso(client, prestamos_de_prueba_bibliotecario, token_usuario_comun):
    resp = client.get(f'/prestamos/{prestamos_de_prueba_bibliotecario}',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    assert resp.get_json()["id"] == prestamos_de_prueba_bibliotecario
    
# POST /prestamos
def test_prestamos_post_json_invalido(client, token_usuario_comun):
    resp = client.post('/prestamos',
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON Invalido o vacío"
    
def test_prestamos_post_campos_no_otorgados(client, token_usuario_comun, usuario_de_prueba):
    resp = client.post('/prestamos',
        json={
            "rut": usuario_de_prueba["rut"]
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El campo ejemplar es obligatorios"
    
def test_prestamos_post_ejemplares_id_string(client, usuario_de_prueba, token_usuario_comun):
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": "uno",
            "rut": usuario_de_prueba["rut"]
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "los vaolres deben ser de tipo entero"
    
def test_prestamos_post_rut_no_otorgado(client, usuario_de_prueba, token_usuario_comun, exemplares_de_prueba):
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"]
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El rut es obligatorio"
    
def test_prestamos_post_dias_invalido_texto(client, usuario_de_prueba, token_usuario_comun, exemplares_de_prueba):
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "quince"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "dias debe ser un entero"
    
def test_prestamos_post_dias_en_el_rango(client, usuario_de_prueba, token_usuario_comun, exemplares_de_prueba):
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "-2"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "dias debe estar entre 1 y 30"
    
def test_prestamos_post_dias_invalido(client, usuario_de_prueba, token_usuario_comun, exemplares_de_prueba):
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "35"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "dias debe estar entre 1 y 30"
    
def test_prestamos_post_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun, exemplares_de_prueba):
    with app.app_context():
        u= db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario no existe"
    
def test_prestamos_post_ejemplar_inexistente(client, app, usuario_de_prueba, token_usuario_comun, exemplares_de_prueba):
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": "999",
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El ejemplar NO existe"
    
def test_prestamos_post_usuario_sin_permiso(client, app, usuario_de_prueba, token_usuario_comun, exemplares_de_prueba):
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "No tienes permiso para realizar esta accion"
    
def test_prestamos_post_biblioteca_inactiva(client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba, biblioteca_de_prueba):
    with app.app_context():
        bibl = db.session.get(Biblioteca, biblioteca_de_prueba["id"])
        bibl.is_active = False
        db.session.commit()
        
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "La biblioteca no está activa"
    
def test_prestamos_post_biblioteca_privada(client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba, biblioteca_de_prueba):
    with app.app_context():
        bibl = db.session.get(Biblioteca, biblioteca_de_prueba["id"])
        bibl.is_public = False
        db.session.commit()
        
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "La biblioteca no es pública, no puede realizar prestamos"
    
def test_prestamos_post_ejemplar_no_disponible(client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba, biblioteca_de_prueba,
    estados_de_prueba):
    with app.app_context():
        ejem = db.session.get(Ejemplar, exemplares_de_prueba[1]["id"])
        ejem.estado_id = estados_de_prueba["prestado"]["id"]
        db.session.commit()
        
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El ejemplar no está disponible"
    
def test_prestamos_post_libro_incompleto(client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba, biblioteca_de_prueba,
    estados_de_prueba, libro_de_prueba):
    with app.app_context():
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        libro.is_complete = False
        db.session.commit()
        
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El libro no está completo, no se puede prestar"
    
def test_prestamos_post_usuario_destinatario_inexistente(client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba):
    with app.app_context():
        u= db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El destinatario No existe"
    
def test_prestamos_post_usuario_destinatario_incompleto(client, app, usuario_de_prueba_perfil_incompleto, token_bibliotecario, exemplares_de_prueba):
    with app.app_context():
        us = db.session.get(Usuario, usuario_de_prueba_perfil_incompleto["id"])
        us.rut= "213947845"
        db.session.commit()
        us_rut = us.rut
        
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": us_rut,
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "El usuario No tiene los datos requeridos"
    
def test_prestamos_post_usuario_sin_asignacion(client, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba):
    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"],
            "dias": "14"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "El usuario No tiene asignacion en la biblioteca"
    
def test_prestamos_post_usuario_sin_asignacion_bibliotecario(
    client, app, usuario_de_prueba_bibliotecario, token_admin,
    exemplares_de_prueba, biblioteca_de_prueba, roles_de_prueba,
    asignacion_bibliotecario_de_prueba,   # ← esto faltaba
):
    with app.app_context():
        rol_invalido = Rol(name="invitado")
        db.session.add(rol_invalido)
        db.session.commit()

        asignacion = Asignacion.query.filter_by(
            usuario_id=usuario_de_prueba_bibliotecario["id"],
            biblioteca_id=biblioteca_de_prueba["id"]
        ).first()

        # sanity check: si esto falla, el fixture no se ejecutó
        assert asignacion is not None, "La asignación del bibliotecario no existe"

        asignacion.rol_id = rol_invalido.id
        db.session.commit()

    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba_bibliotecario["rut"],
            "dias": "14"
        },
        headers={"Authorization": f"Bearer {token_admin}"})

    assert resp.status_code == 403
    assert resp.get_json()["error"] == "El rol del usuario No tiene permiso para pedir prestado"
    
def test_prestamos_post_destinatario_con_rol_no_permitido(
    client, app, usuario_de_prueba_perfil_incompleto, token_bibliotecario,
    exemplares_de_prueba, biblioteca_de_prueba, usuario_de_prueba_bibliotecario,
    roles_de_prueba
):
    with app.app_context():
        # 1) Completar perfil
        us = db.session.get(Usuario, usuario_de_prueba_perfil_incompleto["id"])
        us.rut = "213947845"
        us.phone = "+56911112222"
        us.address = "Calle Destino 1"
        db.session.commit()
        us_id, us_rut = us.id, us.rut

        # 2) Asignación con rol permitido en la biblioteca del ejemplar
        db.session.add(Asignacion(
            usuario_id=us_id,
            rol_id=roles_de_prueba["lector"],
            biblioteca_id=biblioteca_de_prueba["id"],
            is_owner=False,
        ))
        db.session.commit()

        # 3) Tres préstamos VENCIDOS del destinatario correcto
        for i in [1, 2, 3]:
            db.session.add(Prestamo(
                ejemplar_id=exemplares_de_prueba[i]["id"],
                usuario_id=us_id,
                biblioteca_id=biblioteca_de_prueba["id"],
                created_by=usuario_de_prueba_bibliotecario["id"],
                fecha_vencimiento=datetime.utcnow() - timedelta(days=5),
            ))
        db.session.commit()

    resp = client.post('/prestamos',
        json={"ejemplar_id": exemplares_de_prueba[4]["id"],
              "rut": us_rut, "dias": "14"},
        headers={"Authorization": f"Bearer {token_bibliotecario}"})

    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El usuario tiene uno o mas prestamos vencidos"
    
def test_prestamos_post_usuario_con_tres_prestamos_activos(
    client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba,
    biblioteca_de_prueba, usuario_de_prueba_bibliotecario, roles_de_prueba
):
    with app.app_context():
        # El destinatario necesita asignación con rol permitido para llegar a esta rama
        db.session.add(Asignacion(
            usuario_id=usuario_de_prueba["id"],
            rol_id=roles_de_prueba["lector"],
            biblioteca_id=biblioteca_de_prueba["id"],
            is_owner=False,
        ))
        db.session.commit()

        # 3 préstamos ACTIVOS (sin devolución, vencimiento futuro → no vencidos)
        for i in [1, 2, 3]:
            db.session.add(Prestamo(
                ejemplar_id=exemplares_de_prueba[i]["id"],
                usuario_id=usuario_de_prueba["id"],
                biblioteca_id=biblioteca_de_prueba["id"],
                created_by=usuario_de_prueba_bibliotecario["id"],
                fecha_vencimiento=datetime.utcnow() + timedelta(days=10),
            ))
        db.session.commit()

    resp = client.post('/prestamos',
        json={"ejemplar_id": exemplares_de_prueba[4]["id"],
              "rut": usuario_de_prueba["rut"], "dias": "14"},
        headers={"Authorization": f"Bearer {token_bibliotecario}"})

    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Ya tienes 3 prestamos activos a tu nombre, por favor revisa"
    
def test_prestamos_post_estado_prestado_inexistente(
    client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba,
    biblioteca_de_prueba, roles_de_prueba, monkeypatch
):
    with app.app_context():
        db.session.add(Asignacion(
            usuario_id=usuario_de_prueba["id"],
            rol_id=roles_de_prueba["lector"],
            biblioteca_id=biblioteca_de_prueba["id"],
            is_owner=False,
        ))
        db.session.commit()

    # Forzamos que la query del estado "prestado" devuelva None
    class _QueryFalsa:
        def filter(self, *args, **kwargs): return self
        def first(self): return None

    monkeypatch.setattr(Estado, "query", _QueryFalsa())

    resp = client.post('/prestamos',
        json={"ejemplar_id": exemplares_de_prueba[1]["id"],
              "rut": usuario_de_prueba["rut"], "dias": "14"},
        headers={"Authorization": f"Bearer {token_bibliotecario}"})

    assert resp.status_code == 500
    assert resp.get_json()["error"] == "El estado prestado No existe"
    
def test_prestamos_post_integrity_error(
    client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba,
    biblioteca_de_prueba, roles_de_prueba, monkeypatch
):
    from sqlalchemy.exc import IntegrityError

    with app.app_context():
        db.session.add(Asignacion(
            usuario_id=usuario_de_prueba["id"],
            rol_id=roles_de_prueba["lector"],
            biblioteca_id=biblioteca_de_prueba["id"],
            is_owner=False,
        ))
        db.session.commit()

    # Guardamos el commit real y lo hacemos fallar
    commit_real = db.session.commit
    llamadas = {"n": 0}

    def commit_que_falla(*args, **kwargs):
        llamadas["n"] += 1
        raise IntegrityError("stmt", {}, Exception("boom"))

    monkeypatch.setattr(db.session, "commit", commit_que_falla)

    resp = client.post('/prestamos',
        json={"ejemplar_id": exemplares_de_prueba[1]["id"],
              "rut": usuario_de_prueba["rut"], "dias": "14"},
        headers={"Authorization": f"Bearer {token_bibliotecario}"})

    # Restauramos el commit real antes de comprobar el estado de la BD
    monkeypatch.setattr(db.session, "commit", commit_real)

    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Algo salió mal en la creacion del prestamo"
    assert llamadas["n"] >= 1

    # Tras el rollback, ni el préstamo ni el cambio de estado persisten
    with app.app_context():
        assert Prestamo.query.count() == 0
        ejemplar = db.session.get(Ejemplar, exemplares_de_prueba[1]["id"])
        # Sigue en "disponible" (el objeto en sesión sí se modificó antes del commit,
        # pero el rollback de la ruta descarta ese cambio)
        from models import Estado as _Estado
        estado_disponible = _Estado.query.filter(
            db.func.lower(_Estado.nombre) == "disponible"
        ).first()
        assert ejemplar.estado_id == estado_disponible.id
    
def test_prestamos_post_exitoso_con_dias(
    client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba,
    biblioteca_de_prueba, usuario_de_prueba_bibliotecario, roles_de_prueba,
    estados_de_prueba
):
    with app.app_context():
        db.session.add(Asignacion(
            usuario_id=usuario_de_prueba["id"],
            rol_id=roles_de_prueba["lector"],
            biblioteca_id=biblioteca_de_prueba["id"],
            is_owner=False,
        ))
        db.session.commit()

    antes = datetime.utcnow()

    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"], 
            "dias": "18"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })

    despues = datetime.utcnow()

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ejemplar"]["id"] == exemplares_de_prueba[1]["id"]
    assert body["usuario"]["id"] == usuario_de_prueba["id"]
    assert body["biblioteca"]["id"] == biblioteca_de_prueba["id"]
    assert body["creador"]["id"] == usuario_de_prueba_bibliotecario["id"]
    assert body["fecha_devolucion"] is None

    with app.app_context():
        # 1) El ejemplar quedó en estado "prestado"
        ejemplar = db.session.get(Ejemplar, exemplares_de_prueba[1]["id"])
        assert ejemplar.estado_id == estados_de_prueba["prestado"]["id"]

        # 2) El préstamo existe y sus fechas son coherentes
        prestamo = db.session.get(Prestamo, body["id"])
        assert prestamo is not None
        assert prestamo.created_by == usuario_de_prueba_bibliotecario["id"]
        assert prestamo.usuario_id == usuario_de_prueba["id"]
        assert prestamo.fecha_devolucion is None

        # fecha_vencimiento ≈ ahora + 18 días (tolerancia de 5 s por ejecución)
        delta = (prestamo.fecha_vencimiento - (antes + timedelta(days=18))).total_seconds()
        assert abs(delta) < 5

        # fecha_prestamo dentro del intervalo del request
        assert antes - timedelta(seconds=1) <= prestamo.fecha_prestamo <= despues + timedelta(seconds=1)
        
def test_prestamos_post_exitoso_sin_dias(
    client, app, usuario_de_prueba, token_bibliotecario, exemplares_de_prueba,
    biblioteca_de_prueba, usuario_de_prueba_bibliotecario, roles_de_prueba,
    estados_de_prueba
):
    with app.app_context():
        db.session.add(Asignacion(
            usuario_id=usuario_de_prueba["id"],
            rol_id=roles_de_prueba["lector"],
            biblioteca_id=biblioteca_de_prueba["id"],
            is_owner=False,
        ))
        db.session.commit()

    antes = datetime.utcnow()

    resp = client.post('/prestamos',
        json={
            "ejemplar_id": exemplares_de_prueba[1]["id"],
            "rut": usuario_de_prueba["rut"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })

    despues = datetime.utcnow()

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ejemplar"]["id"] == exemplares_de_prueba[1]["id"]
    assert body["usuario"]["id"] == usuario_de_prueba["id"]
    assert body["biblioteca"]["id"] == biblioteca_de_prueba["id"]
    assert body["creador"]["id"] == usuario_de_prueba_bibliotecario["id"]
    assert body["fecha_devolucion"] is None

    with app.app_context():
        # 1) El ejemplar quedó en estado "prestado"
        ejemplar = db.session.get(Ejemplar, exemplares_de_prueba[1]["id"])
        assert ejemplar.estado_id == estados_de_prueba["prestado"]["id"]

        # 2) El préstamo existe y sus fechas son coherentes
        prestamo = db.session.get(Prestamo, body["id"])
        assert prestamo is not None
        assert prestamo.created_by == usuario_de_prueba_bibliotecario["id"]
        assert prestamo.usuario_id == usuario_de_prueba["id"]
        assert prestamo.fecha_devolucion is None

        # fecha_vencimiento ≈ ahora + 14 días (tolerancia de 5 s por ejecución)
        delta = (prestamo.fecha_vencimiento - (antes + timedelta(days=14))).total_seconds()
        assert abs(delta) < 5

        # fecha_prestamo dentro del intervalo del request
        assert antes - timedelta(seconds=1) <= prestamo.fecha_prestamo <= despues + timedelta(seconds=1)
        
# POST /prestamos/<id>/devolver
def test_prestamos_post_id_devolver_usuario_inexistente(client, app, usuario_de_prueba_admin, 
    prestamos_de_prueba_bibliotecario, token_admin):
    with app.app_context():
        u= db.session.get(Usuario, usuario_de_prueba_admin["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.post(f'/prestamos/{prestamos_de_prueba_bibliotecario}/devolver',
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_prestamos_post_id_devolver_prestamo_inexistente(client, prestamos_de_prueba_bibliotecario, usuario_de_prueba, token_usuario_comun):
    resp = client.post(f'/prestamos/500/devolver',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El prestamo No existe"
    
def test_prestamos_post_id_devolver_usuario_sin_permiso(client, prestamos_de_prueba_bibliotecario, usuario_de_prueba, token_usuario_comun):
    resp = client.post(f'/prestamos/{prestamos_de_prueba_bibliotecario}/devolver',
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "No tienes permisos para realizar esta accion"
    
def test_prestamos_post_id_devolver_prestamo_ya_devuelto(client, app, prestamos_de_prueba_bibliotecario, token_bibliotecario):
    with app.app_context():
        prest = db.session.get(Prestamo, prestamos_de_prueba_bibliotecario)
        prest.fecha_prestamo = datetime.utcnow() - timedelta(days=5)
        prest.fecha_devolucion = datetime.utcnow() - timedelta(days=2)
        db.session.commit()
        
    resp = client.post(f'/prestamos/{prestamos_de_prueba_bibliotecario}/devolver',
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "El prestamo ya está marcado como devuelto"
    
def test_prestamos_post_id_devolver_estado_disponible_inexistente(client, app, prestamos_de_prueba_bibliotecario, 
    estados_de_prueba, token_bibliotecario):
    with app.app_context():
        
        estado_danado = db.session.get(Estado, estados_de_prueba["dañado"]["id"])
        Ejemplar.query.filter_by(
            estado_id=estados_de_prueba["disponible"]["id"]
        ).update({"estado_id": estado_danado.id})
        db.session.commit()
        
        est = db.session.get(Estado, estados_de_prueba["disponible"]["id"])
        db.session.delete(est)
        db.session.commit()
        
    resp = client.post(f'/prestamos/{prestamos_de_prueba_bibliotecario}/devolver',
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 500
    assert resp.get_json()["error"] == "El estado disponible No existe"
    
def test_prestamos_post_id_devolver_IntegrityError(client, prestamos_de_prueba_bibliotecario, token_bibliotecario):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        
        resp = client.post(f'/prestamos/{prestamos_de_prueba_bibliotecario}/devolver',
            headers={
                "Authorization": f"Bearer {token_bibliotecario}"
            })
    
    assert resp.status_code == 500
    assert "algo salió mal" in resp.get_json()["error"]
    
def test_prestamos_post_id_devolver_correcto(client, 
    prestamos_de_prueba_bibliotecario, token_bibliotecario):
    resp = client.post(f'/prestamos/{prestamos_de_prueba_bibliotecario}/devolver',
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 200
    
