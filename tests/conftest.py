TEST_DATABASE_URL = "postgresql://postgres:f3l1p3_725@localhost:5432/prueba_test"

import os
os.environ['DATABASE_URL'] = TEST_DATABASE_URL

import pytest
from app import app as flask_app
from extensions import db

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