from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from models import Biblioteca, Usuario, Rol, Asignacion
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db

libraries_bp = Blueprint('libraries', __name__, url_prefix='/libraries')

# GET /bibliotecas → lista pública.
@libraries_bp.route('', methods=['GET'])
def biblioteca():
    """
    Lista de librerías activas y publicas
    No requiere autenticación
    ---
    parameters:
      - name: address
        in: query
        required: false
        type: string
        description: direccion parcial a buscar
    responses:
      200:
        description: Lista de librerías
    """
    address = request.args.get('address')
    query = Biblioteca.query
    
    if address:
        query = query.filter(Biblioteca.address.ilike(f'%{address}%'))
    
    biblio = query.filter_by(is_public=True, is_active=True).all()
    return jsonify([b.to_dict() for b in biblio]), 200

# GET /bibliotecas/<id> → detalle público.
@libraries_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def perfil_biblioteca(id):
    """
    Información Completa de una librería
    requiere Autenticación
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: id de la biblioteca
    responses:
      200:
        description: Consulta exitosa
      401:
        description: El usuario ingresado NO existe
      404:
        description: La biblioteca No existe, no está dsponible, o no es publica
    """
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    if not usuario:
        return jsonify ({"error":"El usuario no existe"}),401
    
    biblioteca = Biblioteca.query.filter_by(id=id).first()
    
    if not biblioteca:
        return jsonify({"error":"La Biblioteca No Existe"}), 404
    
    if not biblioteca.is_active:
        return jsonify ({"error":"la Biblioteca no está disponible"}), 404
    
    if not biblioteca.is_public:
        return jsonify ({"error":"No puedes ver esta Biblioteca"}), 404
    
    return jsonify(biblioteca.to_dict()), 200

# POST /bibliotecas → solo admin (¿o bibliotecario?).
@libraries_bp.route('', methods=['POST'])
@jwt_required()
def crear_biblioteca():
    """
    Crear biblioteca
    Requiere Autenticación del Admin o usuario con perfil completo
    ---
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - address
            - phone
            - email
            - is_public
          properties:
            name:
              type: string
            address:
              type: string
            phone:
              type: string
            email:
              type: string
            is_public:
              type: boolean
          description: datos para crear una biblioteca
    responses:
      201:
        description: Creacion completada
      400:
        description: Datos no otorgados
      401:
        description: Usuario no existe
      403:
        description: Usuario sin permisos
      500:
        description: problemas en el servidor
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    if not usuario.perfil_completo():
        return jsonify({"error":"El usuario no tiene los datos completos"}), 403
    
    name = data.get('name')
    address = data.get('address')
    phone = data.get('phone')
    email = data.get('email')
    is_public = data.get('is_public')
    
    if not name or not address or not phone or not email or is_public is None:
        return jsonify({"error":"Uno de los datos no fue otorgados"}), 400
    
    name = name.strip()
    address = address.strip()
    phone = phone.strip()
    email = email.strip()
    
    for asignacion in usuario.asignaciones:
        if asignacion.is_owner and asignacion.biblioteca.is_active:
            return jsonify({"error":"El usuario ya es jefe de una biblioteca activa"}), 403

    rol_bibliotecario = Rol.query.filter_by(name="bibliotecario").first()
    
    if not rol_bibliotecario:
        return jsonify({"error":"El rol solicitado no está disponible"}), 500
    
    try:
        biblioteca = Biblioteca(
            name= name,
            address=address,
            phone=phone,
            email=email,
            is_public=is_public,
            created_by=usuario.id
        )
        
        db.session.add(biblioteca)
        db.session.flush()
        
        asignacion = Asignacion(
            usuario_id=usuario.id,
            rol_id=rol_bibliotecario.id,
            biblioteca_id=biblioteca.id,
            is_owner=True
        )
        db.session.add(asignacion)
        db.session.commit()
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo Salió mal durante el proceso de creacion de la biblioteca"}), 500
    
    return jsonify(biblioteca.to_dict()), 201

# PUT /bibliotecas/<id> → solo admin.
@libraries_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_biblioteca(id):
    """
    Actualizar datos de Biblioteca
    Requiere Autenticación del Admin o jefe de biblioteca
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: id existente de la biblioteca
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            address:
              type: string
            phone:
              type: string
            is_public:
              type: boolean
          description: datos para actualizar
    responses:
      200:
        description: actualización exitosa
      400:
        description: Error en los datos proporcionados
      401:
        description: Usuario No encontrado
      403:
        description: El usuario No tiene permiso de realizar esta accion
      404:
        description: La biblioteca No existe
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id= int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    biblioteca = Biblioteca.query.filter_by(id=id).first()
    
    if not biblioteca:
        return jsonify({"error":"La biblioteca NO existe"}), 404
    
    if not (usuario.es_admin() or usuario.es_jefe_de(biblioteca.id)):
        return jsonify({"error":"no tienes permiso para realizar esta accion"}), 403
    
    if 'name' in data:
        if data['name'].strip() == "":
            return jsonify({"error":"Dato de nombre invalido"}), 400
        if data['name'] == biblioteca.name:
            return jsonify({"error":"el nombre es el mismo que ya tenía"}), 400
        biblioteca.name = data['name']
    
    if 'address' in data:
        if data['address'].strip() == "":
            return jsonify({"error":"Dato de direccion invalido"}), 400
        if data['address'] == biblioteca.address:
            return jsonify({"error":"la direccion es la misma que ya tenía"}), 400
        biblioteca.address = data['address']
        
    if 'phone' in data:
        if data['phone'].strip() == "":
            return jsonify({"error":"Dato de telefono invalido"}), 400
        if data['phone'] == biblioteca.phone:
            return jsonify({"error":"el telefono es el mismo que ya tenía"}), 400
        biblioteca.phone = data['phone']
    
    if 'is_public' in data:
        if not isinstance(data['is_public'], bool):
            return jsonify({"error":"el valor debe ser bool"}), 400
        biblioteca.is_public = data['is_public']
        
    db.session.commit()
    return jsonify (biblioteca.to_dict()), 200

# DELETE /bibliotecas/<id> → solo admin.
@libraries_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_biblioteca(id):
    """
    Soft delete de la biblioteca
    Requiere Autenticación del Admin o jefe de biblioteca
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: id de la biblioteca a eliminar
    responses:
      204:
        description: Eliminación de la biblioteca completado
      401:
        description: El usuario no existe
      403:
        description: El usuario no tiene permiso
      404:
        description: La biblioteca no existe
    """
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    biblioteca = Biblioteca.query.filter_by(id=id).first()
    
    if not biblioteca:
        return jsonify({"error":f"La biblioteca NO existe"}), 404
    
    if not biblioteca.is_active:
        return jsonify({"error":"La biblioteca NO existe"}), 404

    if not (usuario.es_admin() or usuario.es_jefe_de(id)):
        return jsonify({"error":"no tienes permiso para realizar esta accion"}), 403

    biblioteca.is_active = False
    
    db.session.commit()
    return "", 204

# GET /biblioteca/mine
@libraries_bp.route('/mine', methods=['GET'])
@jwt_required()
def mis_bibliotecas():
    """
    Lista de bibliotecas a las que pertenece el usuario
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Consulta exitosa
      401:
        description: Usuario Inexistente
    """
    user_id= int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    lista = []
    for asignacion in usuario.asignaciones:
        lista.append(asignacion.biblioteca.to_dict())
    
    return jsonify(lista), 200