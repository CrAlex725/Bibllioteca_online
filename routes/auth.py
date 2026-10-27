from flask import jsonify, request, Blueprint
from models import Usuario
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registrar Usuarios
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - username
            - name
            - password
          properties:
            email:
              type: string
            username:
              type: string
            name:
              type: string
            password:
              type: string
            rut:
              type: string
            phone:
              type: string
            address:
              type: string
          description: |
            Parametros requeridos y opcionales para crear un usuario
            sin estos el usuario queda incompleto
    responses:
      201:
        description: Usuario creado correctamente
      400:
        description: datos inválidos o faltantes
      409:
        description: Usuario o Correo ya existentes
    """
    data = request.get_json(silent=True)
    if not data :
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    email = data.get('email')
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    
    if not email or not username or not name or not password:
        return jsonify({"error":"Falta uno de los datos"}), 400
    
    if email.strip() == "" or username.strip() == "" or name.strip() == "" or password.strip() == "":
        return jsonify({"error":"Campos invalidos"}), 400
    
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
    """
    Loguear Usuario existente
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
          description: contraseña y correo del usuario
    responses:
      200:
        description: usuario logueado Correctamente
      400:
        description: Datos necesarios inválidos
      401:
        description: Usuario y/o contraseña incorrectos
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"No se han proporcionado los datos Necesarios"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error":"El Correo y la contraseña deben completarse"}), 400
    
    if email.strip() == "" or password.strip() == "":
        return jsonify({"error":"El Correo y la contraseña deben ser campos validos"}), 400
    
    # si encuentro el correo
    usuario =  Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.check_password(password):
        return jsonify({"error":"El Usuario o la contraseña Son incorrectos"}), 401
    
    token = create_access_token(identity=str(usuario.id))
    
    return jsonify({"token": token}), 200
        
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    perfil del Usuario
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Perfil encontrado
      401:
        description: Token faltante o inválido
      404:
        description: Usuario No autorizado
    """
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No está Autorizado"}), 404
    
    return jsonify(usuario.to_dict()), 200