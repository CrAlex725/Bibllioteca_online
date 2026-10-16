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
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def usuario_de_prueba(app):
    with app.app_context():
        usuario = Usuario(
            email = "ab.cdef.123@gmail.com",
            username = "abcdefghij",
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