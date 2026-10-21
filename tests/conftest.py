TEST_DATABASE_URL = "postgresql://postgres:f3l1p3_725@localhost:5432/prueba_test"

import os
os.environ['DATABASE_URL'] = TEST_DATABASE_URL
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-that-is-at-least-32-bytes-long'

import pytest
from app import app as flask_app
from extensions import db
from models import (
    Usuario, Rol, Biblioteca, Asignacion, libro_autor,
    Libro, Editorial, Autor, Estado, Ejemplar, Prestamo
)

@pytest.fixture
def app():
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URL
    flask_app.config['TESTING'] = True
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.rollback()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def usuario_de_prueba(app):
    with app.app_context():
        usuario = Usuario(
            email = "ab.cdef.123@user.com",
            username = "abcedfghij",
            name = "Abcdefghij",
            rut = "19.234.444-k",
            phone = "+56987654321",
            address = "Calle 1",
        )
        usuario.set_password("123456789")
        db.session.add(usuario)
        db.session.commit()
    
        return {
            'id': usuario.id,
            'email': usuario.email,
            'username' : usuario.username,
            'name' : usuario.name,
            'rut' : usuario.rut,
            'phone' : usuario.phone,
            'address' : usuario.address,
            'password' : "123456789"
        }
    
@pytest.fixture
def token_usuario_comun(client, usuario_de_prueba):
    resp_user = client.post('/auth/login', json={
            "email": usuario_de_prueba["email"],
            "password": usuario_de_prueba["password"]
        })
    return resp_user.get_json()["token"]
        
@pytest.fixture
def usuario_de_prueba_admin(app):
    with app.app_context():
        usuario = Usuario(
            email = "ab.cdef.123@admin.com",
            username = "lfcdefghij",
            name = "Abcdefghij",
            rut = "20.234.444-k",
            phone = "+56987654321",
            address = "Calle 1",
            is_admin = True
        )
        usuario.set_password("123456789")
        db.session.add(usuario)
        db.session.commit()
    
        return {
            'id': usuario.id,
            'email': usuario.email,
            'password' : "123456789"
        }

@pytest.fixture
def token_admin(client, usuario_de_prueba_admin):
    resp_user = client.post('/auth/login', json={
            "email": usuario_de_prueba_admin["email"],
            "password": usuario_de_prueba_admin["password"]
        })
    return resp_user.get_json()["token"]
        
@pytest.fixture
def roles_de_prueba(app):
    with app.app_context():
        roles = {}
        for nombre in ["bibliotecario", "lector", "asistente"]:
            rol = Rol(name=nombre)
            db.session.add(rol)
            roles[nombre] = rol.id
        db.session.commit()
        
        return roles  # {"bibliotecario": 1, "lector": 2, "asistente": 3}
        
@pytest.fixture
def usuario_de_prueba_bibliotecario(app):
    with app.app_context():
        usuario = Usuario(
            email="biblio@test.com",
            username="biblio",
            name="Bibliotecario",
            rut="22.222.222-2",
            phone="+56911111111",
            address="Calle Biblio 1"
        )
        usuario.set_password("1234567890")
        db.session.add(usuario)
        db.session.commit()
        
        return {
            "id": usuario.id,
            "username": usuario.username,
            "name": usuario.name,
            "email": usuario.email,
            "password": "1234567890"
        }
        
@pytest.fixture
def token_bibliotecario(client, usuario_de_prueba_bibliotecario, asignacion_bibliotecario_de_prueba):
    resp = client.post('/auth/login', 
        json={
            "email": usuario_de_prueba_bibliotecario["email"],
            "password": usuario_de_prueba_bibliotecario["password"]
        })
    return resp.get_json()["token"]
    
@pytest.fixture
def biblioteca_de_prueba(app, usuario_de_prueba_bibliotecario):
    with app.app_context():
        biblioteca = Biblioteca(
            name="Biblioteca Test",
            address = "address calle 1",
            phone = "922749027",
            email = "biblio_test@test.com",
            created_by=usuario_de_prueba_bibliotecario["id"]
        )
        db.session.add(biblioteca)
        db.session.commit()
    
        return {
            "id": biblioteca.id,
            "name" :biblioteca.name,
            "address" : biblioteca.address,
            "phone" : biblioteca.phone,
            "email" : biblioteca.email,
            "created_by": usuario_de_prueba_bibliotecario["id"],
            "is_public" : True
        }
    
@pytest.fixture
def asignacion_bibliotecario_de_prueba(app, roles_de_prueba, usuario_de_prueba_bibliotecario, biblioteca_de_prueba):
    with app.app_context():
        asignacion = Asignacion(
        usuario_id = usuario_de_prueba_bibliotecario["id"],
        rol_id = roles_de_prueba["bibliotecario"],
        biblioteca_id = biblioteca_de_prueba["id"],
        is_owner=True
        )
        db.session.add(asignacion)
        db.session.commit()
    
        return {
            "id": asignacion.id,
            "usuario_id": asignacion.usuario_id,
            "rol_id": asignacion.rol_id,
            "biblioteca_id": asignacion.biblioteca_id
        }
    
@pytest.fixture
def libro_de_prueba(app):
    with app.app_context():
        editorial = Editorial(nombre="Zig-Zag")
        db.session.add(editorial)
        
        autor = Autor(nombre="Anaya")
        db.session.add(autor)
        db.session.commit()
        
        libro = Libro(
            isbn="9788471532688",
            title="Libro 1",
            year_publication=2003,
            clasificacion="Fantasía",
            is_complete=True,
            editorial_id=editorial.id
        )
        libro.autores.append(autor)
        db.session.add(libro)
        db.session.commit()
        
        return libro.isbn
    
@pytest.fixture
def biblioteca_privada_de_prueba(app, usuario_de_prueba_bibliotecario):
    with app.app_context():
        biblioteca = Biblioteca(
            name="Biblioteca privada Test",
            address = "address calle 1",
            phone = "922749027",
            email = "biblio_test@test.com",
            created_by=usuario_de_prueba_bibliotecario["id"],
            is_public = False
        )
        db.session.add(biblioteca)
        db.session.commit()
        
        return {
            "id": biblioteca.id,
            "name" :biblioteca.name,
            "address" : biblioteca.address,
            "phone" : biblioteca.phone,
            "email" : biblioteca.email,
            "created_by": usuario_de_prueba_bibliotecario["id"],
            "is_public" : False
        }