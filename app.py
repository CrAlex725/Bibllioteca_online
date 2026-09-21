import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from models import (Usuario,Libro)
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
    
    nuevo_usuario = Usuario(rut=None,name=name, username=username,phone=None,email=email,address=None)
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
    user_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No está Autorizado"}), 404
    
    return jsonify(usuario.to_dict()), 200
    
@app.route('/books', methods=['GET'])
def libros():
    libros = Libro.query.all()
    result = [libro.to_summary() for libro in libros]
    return jsonify(result), 200

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

if __name__ == '__main__':
    app.run(debug=True)
