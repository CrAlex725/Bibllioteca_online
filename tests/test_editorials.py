from models import (Editorial, Usuario)
from extensions import db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

# GET editorials/
def test_editorials_get_toda_las_editoriales_con_token(client, token_usuario_comun, editoriales_de_prueba):
    resp = client.get('/editorials',
        headers={
            "Authorization":f"Bearer {token_usuario_comun}"
        })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == len(editoriales_de_prueba)
    
def test_editorials_get_toda_las_editoriales_sin_token(client, editoriales_de_prueba):
    resp = client.get('/editorials',)
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == len(editoriales_de_prueba)
    
def test_editorials_get_con_filtro_parcial(client, editoriales_de_prueba):
    resp = client.get('/editorials', query_string={
        "nombre": "zig"
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    
def test_editorials_get_con_filtro_completo(client, editoriales_de_prueba):
    resp = client.get('/editorials', query_string={
        "nombre": editoriales_de_prueba["Zig Zag"]["nombre"]
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    
