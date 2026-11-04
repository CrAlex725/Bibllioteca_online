from models import (Libro, Usuario, Asignacion, Biblioteca, Estado, Ejemplar)
from extensions import db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

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
    
# POST exemplars/
def test_exemplars_post_json_invalido(client, token_usuario_comun, exemplares_de_prueba):
    resp = client.post('/exemplars',
        json= None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON invalido o vacío"
    
def test_exemplars_post_biblioteca_None(client, app, token_usuario_comun, exemplares_de_prueba,
        libro_de_prueba):
    with app.app_context():
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": None,
            "libro_id": libro.id
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Debes agregar una biblioteca a la peticion"
    
def test_exemplars_post_libro_None(client, app, token_usuario_comun, exemplares_de_prueba,
        biblioteca_de_prueba):
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": None
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Debes agregar un libro a la peticion"
    
def test_exemplars_post_biblioteca_y_libro_string_invalido(client, app, token_usuario_comun, exemplares_de_prueba):
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": "biblioteca 1",
            "libro_id":  "libro 1"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Ambos ID deben ser enteros"
    
def test_exemplars_post_usuario_inexistente(client, app, usuario_de_prueba, token_usuario_comun, exemplares_de_prueba,
        libro_de_prueba, biblioteca_de_prueba):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro.id
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "El usuario No existe"
    
def test_exemplars_post_usuario_invalido(client, app, token_usuario_comun, exemplares_de_prueba,
        libro_de_prueba, biblioteca_de_prueba):
    with app.app_context():
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro.id
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "El usuario No tiene permisos para realizar esta accion"
    
def test_exemplars_post_usuario_de_biblioteca_no_bibliotecario(client, app, token_usuario_comun, exemplares_de_prueba,
        libro_de_prueba, biblioteca_de_prueba, roles_de_prueba, usuario_de_prueba):
    with app.app_context():
        asignacion = Asignacion(
            biblioteca_id = biblioteca_de_prueba["id"],
            rol_id =roles_de_prueba["lector"],
            usuario_id = usuario_de_prueba["id"]
        )
        db.session.add(asignacion)
        db.session.commit()
        
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro.id
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "El usuario No tiene permisos para realizar esta accion"
    
def test_exemplars_post_libro_inexistente(client,
        libro_de_prueba, biblioteca_de_prueba, token_bibliotecario):
    libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": "99999"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El libro no existe"
    
def test_exemplars_post_biblioteca_inexistente(client, app, token_admin,
        libro_de_prueba, biblioteca_de_prueba):
    with app.app_context():
        bib = db.session.get(Biblioteca, biblioteca_de_prueba["id"])
        db.session.delete(bib)
        db.session.commit()
        
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        libro_id=libro.id
        
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro_id
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "La biblioteca no existe"
    
def test_exemplars_post_estado_disponible_inexistente(client, app, token_bibliotecario,
        libro_de_prueba, biblioteca_de_prueba, estados_de_prueba):
    with app.app_context():
        estado = Estado.query.filter_by(id=estados_de_prueba["disponible"]["id"]).first()
        db.session.delete(estado)
        db.session.commit()
        
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        libro_id = libro.id
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro_id
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 500
    assert resp.get_json()["error"] == "Estado 'Disponible' no configurado"
    
def test_exemplars_post_numero_ejemplar_string_invalido(client, token_bibliotecario,
        libro_de_prueba, biblioteca_de_prueba, estados_de_prueba):
    
    libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
    libro_id = libro.id
    
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro_id,
            "numero_ejemplar": "numero 1"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El numero de ejemplar debe ser entero"
    
def test_exemplars_post_numero_ejemplar_negativo(client, token_bibliotecario,
        libro_de_prueba, biblioteca_de_prueba, estados_de_prueba):
    
    libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
    libro_id = libro.id
        
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro_id,
            "numero_ejemplar": "-1"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El numero de ejemplar debe ser mayor a 0"
    
def test_exemplars_post_numero_ejemplar_existente(client, token_bibliotecario,
        libro_de_prueba, biblioteca_de_prueba, estados_de_prueba, exemplares_de_prueba):
    
    libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
    libro_id = libro.id
        
    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro_id,
            "numero_ejemplar": exemplares_de_prueba[1]["numero"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 409
    assert "YA existe" in resp.get_json()["error"]
    
def test_exemplars_post_IntegrityError(client, token_bibliotecario,
        libro_de_prueba, biblioteca_de_prueba, estados_de_prueba, exemplares_de_prueba):
    with patch.object(
        db.session, 'commit',
        side_effect=IntegrityError("stmt", "params", "orig")
    ):
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        libro_id = libro.id
            
        resp = client.post('/exemplars',
            json={
                "biblioteca_id": biblioteca_de_prueba["id"],
                "libro_id": libro_id,
                "numero_ejemplar": "4"
            },
            headers={
                "Authorization": f"Bearer {token_bibliotecario}"
            })
    
    assert resp.status_code == 409
    assert "Conflicto al asignar" in resp.get_json()["error"]
    
def test_exemplars_post_creacion_exitosa_sin_numero_ejemplar(
        client, app, token_bibliotecario,
        libro_de_prueba, biblioteca_de_prueba,
        estados_de_prueba, exemplares_de_prueba):

    bib_id = biblioteca_de_prueba["id"]

    with app.app_context():
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        libro_id = libro.id

        total_antes = Ejemplar.query.filter_by(
            biblioteca_id=bib_id, libro_id=libro_id
        ).count()

        numeros_antes = {
            e.numero_ejemplar
            for e in Ejemplar.query.filter_by(
                biblioteca_id=bib_id, libro_id=libro_id
            ).all()
        }

    resp = client.post('/exemplars',
        json={
            "biblioteca_id": bib_id, 
             "libro_id": libro_id
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })

    assert resp.status_code == 201
    data = resp.get_json()

    assert "numero_ejemplar" in data
    assert isinstance(data["numero_ejemplar"], int)
    assert data["numero_ejemplar"] not in numeros_antes
    assert data["numero_ejemplar"] == max(numeros_antes, default=0) + 1

    with app.app_context():
        total_despues = Ejemplar.query.filter_by(
            biblioteca_id=bib_id, libro_id=libro_id
        ).count()
    assert total_despues == total_antes + 1
    
def test_exemplars_post_creacion_exitosa_con_numero_ejemplar(
        client, app, token_bibliotecario,
        libro_de_prueba, biblioteca_de_prueba,
        estados_de_prueba, exemplares_de_prueba):

    with app.app_context():
        libro = Libro.query.filter_by(isbn=libro_de_prueba).first()
        libro_id = libro.id

        max_actual = db.session.query(
            db.func.max(Ejemplar.numero_ejemplar)
        ).filter_by(
            biblioteca_id=biblioteca_de_prueba["id"],
            libro_id=libro_id
        ).scalar() or 0
        nuevo_numero = max_actual + 1

    resp = client.post('/exemplars',
        json={
            "biblioteca_id": biblioteca_de_prueba["id"],
            "libro_id": libro_id,
            "numero_ejemplar": nuevo_numero
        },
        headers={"Authorization": f"Bearer {token_bibliotecario}"})

    assert resp.status_code == 201
    data = resp.get_json()
    assert data["numero_ejemplar"] == nuevo_numero
    
# PUT exemplers/<id>
def test_exemplars_put_json_invalido(client, exemplares_de_prueba, token_usuario_comun):
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json=None,
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "JSON invalido o vacío"
    
def test_exemplars_put_ejemplar_inexistente(client, exemplares_de_prueba, token_usuario_comun, estados_de_prueba):
    resp = client.put(f"/exemplars/999999",
        json={
            "estado_id": estados_de_prueba["dañado"]["id"],
            "signatura": "Signatura Nueva"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El ejemplar No existe"
    
def test_exemplars_put_usuario_inexistente(client, app, exemplares_de_prueba, 
        usuario_de_prueba, token_usuario_comun,
    estados_de_prueba):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "estado_id": estados_de_prueba["dañado"]["id"],
            "signatura": "Signatura Nueva"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "el usuario no existe"
    
def test_exemplars_put_usuario_sin_permiso(client, exemplares_de_prueba, 
    estados_de_prueba, token_usuario_comun):
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "estado_id": estados_de_prueba["dañado"]["id"],
            "signatura": "Signatura Nueva"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "no tiene permiso" in resp.get_json()["error"]
    
def test_exemplars_put_usuario_lector_sin_permiso(client, app, exemplares_de_prueba, biblioteca_de_prueba,
    estados_de_prueba, token_usuario_comun, usuario_de_prueba, roles_de_prueba):
    with app.app_context():
        asignacion = Asignacion(
            usuario_id = usuario_de_prueba["id"],
            biblioteca_id = biblioteca_de_prueba["id"],
            rol_id = roles_de_prueba["lector"]
        )
        db.session.add(asignacion)
        db.session.commit()
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "estado_id": estados_de_prueba["dañado"]["id"],
            "signatura": "Signatura Nueva"
        },
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "no tiene permiso" in resp.get_json()["error"]
    
def test_exemplars_put_sin_datos(client, exemplares_de_prueba,
    estados_de_prueba, token_bibliotecario):
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "estado": estados_de_prueba["dañado"]["id"],
            "singatura": "Signatura Nueva"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert "Debes mandar al menos un campo" in resp.get_json()["error"]
    
def test_exemplars_put_estado_entero(client, exemplares_de_prueba,
    estados_de_prueba, token_bibliotecario):
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "estado_id": "uno"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "El id del estado debe ser un entero"
    
def test_exemplars_put_estado_inexistente(client, exemplares_de_prueba,
    estados_de_prueba, token_bibliotecario):
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "estado_id": "90000"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "el estado no existe"
    
def test_exemplars_put_actualizacion_signatura(client, exemplares_de_prueba,
    estados_de_prueba, token_bibliotecario):
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "signatura": "Nueva Signatura"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["signatura"] == "Nueva Signatura"
    
def test_exemplars_put_actualizacion_estado(client, exemplares_de_prueba,
    estados_de_prueba, token_bibliotecario):
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "estado_id": estados_de_prueba["dañado"]["id"]
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["estado"]["id"] == estados_de_prueba["dañado"]["id"]
    
def test_exemplars_put_actualizacion_completa(client, exemplares_de_prueba,
    estados_de_prueba, token_bibliotecario):
    
    resp = client.put(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        json={
            "estado_id": estados_de_prueba["dañado"]["id"],
            "signatura": "Nueva Signatura"
        },
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["signatura"] == "Nueva Signatura"
    assert data["estado"]["id"] == estados_de_prueba["dañado"]["id"]
    
# DELETE exemplars/<id>
def test_exemplars_delete_ejemplar_inexistente(client, exemplares_de_prueba, token_usuario_comun):
    resp = client.delete(f"/exemplars/999999",
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "El ejemplar No existe"
    
def test_exemplars_delete_usuario_inexistente(client, app, exemplares_de_prueba, usuario_de_prueba, token_usuario_comun):
    with app.app_context():
        u = db.session.get(Usuario, usuario_de_prueba["id"])
        db.session.delete(u)
        db.session.commit()
        
    resp = client.delete(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "el usuario no existe"
    
def test_exemplars_delete_usuario_sin_permiso(client, exemplares_de_prueba, token_usuario_comun):
    resp = client.delete(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "no tiene permiso" in resp.get_json()["error"]
    
def test_exemplars_delete_usuario_lector_sin_permiso(client, app, exemplares_de_prueba, token_usuario_comun,
    usuario_de_prueba, biblioteca_de_prueba, roles_de_prueba):
    with app.app_context():
        asignacion = Asignacion(
            usuario_id = usuario_de_prueba["id"],
            biblioteca_id = biblioteca_de_prueba["id"],
            rol_id = roles_de_prueba["lector"]
        )
        db.session.add(asignacion)
        db.session.commit()
        
    resp = client.delete(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        headers={
            "Authorization": f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 403
    assert "no tiene permiso" in resp.get_json()["error"]
    
def test_exemplars_delete_estado_inexistente(client, app, exemplares_de_prueba, token_bibliotecario,
    estados_de_prueba):
    with app.app_context():
        estado = Estado.query.filter_by(id=estados_de_prueba["de baja"]["id"]).first()
        db.session.delete(estado)
        db.session.commit()
        
    resp = client.delete(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 500
    assert resp.get_json()["error"] == "El estado 'de baja' no existe"
    
def test_exemplars_delete_completo(client, app, exemplares_de_prueba, token_bibliotecario):
    resp = client.delete(f"/exemplars/{exemplares_de_prueba[1]["id"]}",
        headers={
            "Authorization": f"Bearer {token_bibliotecario}"
        })
    
    assert resp.status_code == 204
    data = resp.get_json()
    data is None
    with app.app_context():
        ejemplar = db.session.get(Ejemplar, exemplares_de_prueba[1]["id"])
        assert ejemplar.estado.nombre.lower() == "de baja"
