def test_app_existe(client):
    assert client is not None


def test_db_crea_tablas(app):
    from models import Usuario
    from extensions import db
    
    usuarios = db.session.query(Usuario).all()
    assert usuarios == []