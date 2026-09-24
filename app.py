import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from models import (Usuario,Libro, Editorial, Autor)
from helpers import normalizar_isbn
from extensions import db, jwt

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']

db.init_app(app)
migrate = Migrate(app, db)
jwt.init_app(app)

@app.route('/health', methods=['GET'])
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status":"ok"}), 200
    except Exception as e:
        return jsonify({"status":"error", "db": str(e)}), 500
    
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data :
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    email = data.get('email')
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    
    if not email or not username or not name or not password:
        return jsonify({"error":"Falta uno de los datos"}), 400
    
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error":"El Correo ya existe en la base de datos"}), 409
    
    if Usuario.query.filter_by(username=username).first():
        return jsonify({"error":"El Usuario No está Disponible"}), 409
    
    nuevo_usuario = Usuario(name=name, username=username,email=email)
    nuevo_usuario.set_password(password)
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    return jsonify({"status":f"El usuario {name}, con id {nuevo_usuario.id} Se creó Correctamente"}), 201
    
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"No se han proporcionado los datos Necesarios"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error":"El Correo y la contraseña deben completarse"}), 400
    
    # si encuentro el correo
    usuario =  Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.check_password(password):
        return jsonify({"error":"El Usuario o la contraseña Son incorrectos"}), 401
    
    token = create_access_token(identity=str(usuario.id))
    
    return jsonify({"token": token}), 200
        
@app.route('/auth/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No está Autorizado"}), 404
    
    return jsonify(usuario.to_dict()), 200
    
@app.route('/books', methods=['GET'])
def libros():
    titulo = request.args.get('Titulo')
    autor = request.args.get('Autor')
    editorial = request.args.get('Editorial')
    categoria = request.args.get('Categoria')
    anio = request.args.get('Year')
    
    query = Libro.query
    
    if titulo:
        query = query.filter(Libro.title.ilike(f'%{titulo}%'))
    
    if editorial:
        query = query.join(Libro.editorial).filter(
            Editorial.nombre.ilike(f'%{editorial}%'))
    
    if autor:
        query = query.filter(Libro.autores.any(
            Autor.nombre.ilike(f'%{autor}%')))
    
    if categoria:
        query = query.filter(Libro.clasificacion.ilike(f'%{categoria}%'))
        
    if anio:
        try:
            query = query.filter(Libro.year_publication == int(anio))
            
        except ValueError:
            return jsonify({'error':'Year Debe ser Numerico'}), 400
    
    libros = query.all()
    return jsonify([l.to_summary() for l in libros]), 200

@app.route('/books', methods=['POST'])
@jwt_required()
def crear_libro():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400

    isbn = data.get('isbn')
    title = data.get('title')
    editorial = data.get('editorial')
    autores = data.get('autores')
    
    if not isinstance(autores, list):
        return jsonify({"error":"autores debe ser una lista"}), 400
    
    if not isbn or not title or not editorial or not autores:
        return jsonify({"error":"Todos los campos mencionados son obligatorios"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    if not usuario.puede_crear_libros():
        return  jsonify({"error":"El Usuario No tiene Permiso para agregar Libros"}), 403
    
    isbn_normalizado = normalizar_isbn(isbn)
    
    if Libro.query.filter_by(isbn=isbn_normalizado).first():
        return jsonify({"error":f"El Libro con isbn: {isbn}, Ya existe"}), 409
    
    try:
        editoriall = Editorial.query.filter(
            db.func.lower(Editorial.nombre) == db.func.lower(editorial)
        ).first()

        if not editoriall:
            editoriall = Editorial(nombre=editorial)
            db.session.add(editoriall)
            db.session.flush()

        autores_obj = []
        nombres_procesados = set()
        
        for nombre in autores:
            if not nombre or nombre.strip() == "":
                continue
            
            clave = nombre.lower().strip()
            if clave in nombres_procesados:
                continue
            
            nombres_procesados.add(clave)
            
            autor = Autor.query.filter(
                db.func.lower(Autor.nombre) == db.func.lower(nombre)
            ).first()
            
            if not autor:
                autor = Autor(nombre=nombre.strip())
                db.session.add(autor)
                db.session.flush()
            
            autores_obj.append(autor)
            
        libro = Libro(
            isbn =isbn_normalizado,
            title=title,
            year_publication=data.get('year'),
            clasificacion=data.get('clasificacion'),
            editorial_id=editoriall.id
        )
        libro.autores = autores_obj
        
        db.session.add(libro)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo salió mal en la creación del libro"}), 409
    
    return jsonify(libro.to_dict()), 201

@app.route('/books/<string:isbn>', methods=['GET'])
@jwt_required(optional=True)
def libro_detalle(isbn):
    isbn_normalizado = normalizar_isbn(isbn)
    libro = Libro.query.filter_by(isbn=isbn_normalizado).first()
    if not libro:
        return jsonify({"error":"libro No encontrado"}), 404
    
    if get_jwt_identity():
        return jsonify(libro.to_dict()), 200

    return jsonify(libro.to_summary()),200

@app.route('/books/<string:isbn>', methods=['PUT'])
@jwt_required()
def actualizar_libro(isbn):
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"no tienes permiso para realizar esta accion"}), 403
    
    isbn_normalizado = normalizar_isbn(isbn)
    libro = Libro.query.filter_by(isbn=isbn_normalizado).first()
    
    if not libro:
        return jsonify({"error":f"El libro con isbn: {isbn} NO existe"}),404
    
    if 'title' in data:
        libro.title = data['title']
    
    if 'year_publication' in data:
        libro.year_publication = data['year_publication']
        
    if 'clasificacion' in data:
        libro.clasificacion = data['clasificacion']
    
    if 'editorial_id' in data:
        editorial = Editorial.query.filter_by(id=data['editorial_id']).first()
        if not editorial:
            return jsonify({"error":"Editorial No existe"}), 400
        libro.editorial_id = editorial.id
        
    if 'autor_ids' in data:
        if not isinstance(data['autor_ids'], list):
            return jsonify({"error":"aitor_ids debe ser una lista"}), 400
        
        autores_obj = []
        for autor_id in data['autor_ids']:
            autor = Autor.query.filter_by(id=autor_id).first()
            if not autor:
                return jsonify({"error":"El Autor NO Existe"}), 400
            autores_obj.append(autor)
        libro.autores = autores_obj
    
    db.session.commit()
    return jsonify(libro.to_dict()), 200
    
@app.route('/books/<string:isbn>', methods=['DELETE'])
@jwt_required()
def eliminar_libro(isbn):
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"no tienes permiso para realizar esta accion"}), 403    
    
    isbn_normalizado = normalizar_isbn(isbn)
    
    libro = Libro.query.filter_by(isbn=isbn_normalizado).first()
    
    if not libro:
        return jsonify({"error":f"El libro con ISBN {isbn} NO existe"}), 404
    try:
        db.session.delete(libro)
        db.session.commit()
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo salió mal en la eliminación del libro"}), 409
    
    return "", 204
    
if __name__ == '__main__':
    app.run(debug=True)
