from flask import jsonify, request, Blueprint
from models import Usuario
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
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
    
@auth_bp.route('/login', methods=['POST'])
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
        
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No está Autorizado"}), 404
    
    return jsonify(usuario.to_dict()), 200