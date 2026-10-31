from flask import jsonify, Blueprint, request
from sqlalchemy.exc import IntegrityError
from models import Usuario, Estado
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db

states_bp = Blueprint('states', __name__, url_prefix='/states')

@states_bp.route('', methods=['GET'])
def listar_estado():
    """
    Consulta de estados para libros
    no requiere Autenticacion
    ---
    parameters:
      - name: nombre
        in: query
        type: string
        description: Nombre del estado
    responses:
      200:
        description: Consulta exitosa
    """
    
    nombre = request.args.get('nombre')
    query = Estado.query
    
    if nombre:
        query = query.filter(Estado.nombre.ilike(f'%{nombre}%'))
    
    estado = query.all()
    return jsonify([e.to_dict() for e in estado]), 200

@states_bp.route('/<int:id>', methods=['GET'])
def estado_info(id):
    """
    Información Completa del estado
    No requiere Autenticacion
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: id del estado
    responses:
      200:
        description: Consulta exitosa
      404:
        description: Estado Inexistente
    """
    estado = Estado.query.filter_by(id=id).first()
    
    if not estado:
        return jsonify({"error":"El estado asociado al id no existe"}), 404
    
    return jsonify(estado.to_dict()), 200

@states_bp.route('', methods=['POST'])
@jwt_required()
def crear_estado():
    """
    Crear nuevo estado
    Requiere autenticacion Admin
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
            - nombre
          properties:
            nombre: 
              type: string
    responses:
      201:
        description: Creacion exitosa
      400:
        description: Datos inválidos
      401:
        description: Usuario Inexistente
      403:
        description: Usuario sin permiso
      409:
        description: Ya existe este estado
      500:
        description: Algo salió mal con este proceso
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No Existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"El usuario No tiene permiso para realizar esta accion"}), 403
    
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    
    existe = Estado.query.filter(
        db.func.lower(Estado.nombre) == db.func.lower(nombre)
    ).first()
    
    if existe:
        return jsonify({"error":"El estado ya existe"}), 409
        
    try:
        estado = Estado(
            nombre = nombre
        )
        db.session.add(estado)
        db.session.commit()
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo Salió mal durante el proceso de crear el estado"}), 500
    
    return jsonify(estado.to_dict()), 201

@states_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_modelo_estado(id):
    """
    Actualizar datos de estado 
    requiere autenticación de admin
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: id del estado
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nombre
          properties:
            nombre:
              type: string
    responses:
      200:
        description: actualización Exitosa
      400:
        description: Datos invalidos
      401:
        description: Usuario Inexistente
      403:
        description: Usuario sin permiso
      404:
        description: Estado No encontrado
      409:
        description: El nuevo estado Ya existe
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id= int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario NO existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"El usuario No tiene permisos para realizar esta accion"}), 403
    
    estado = Estado.query.filter_by(id=id).first()
    
    if not estado:
        return jsonify({"error":"El estado que buscas NO existe"}), 404
    
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({"error":"El nombre es obligatorio"}), 400
    
    existe = Estado.query.filter(
            db.func.lower(Estado.nombre) == db.func.lower(nombre),
            Estado.id != id
        ).first()
    
    if existe:
        return jsonify({"error":"El Estado ya existe"}), 409
    
    estado.nombre = nombre
    db.session.commit()
    
    return jsonify (estado.to_dict()), 200

@states_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_estado(id):
    """
    Eliminar estado 
    requiere autenticación de admin
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: id del estado
    responses:
      200:
        description: Eliminación Exitosa
      401:
        description: Usuario Inexistente
      403:
        description: Usuario sin permiso
      404:
        description: Estado Inexistente
      409:
        description: No se puede eliminar, tiene ejemplares asociados
    """
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"no tienes permiso para realizar esta accion"}), 403
    
    estado = Estado.query.filter_by(id=id).first()
    
    if not estado:
        return jsonify({"error":"El estado no existe"}), 404
    
    try:
        db.session.delete(estado)
        db.session.commit()
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo salió mal en la eliminación del estado"}), 409
    
    return "", 204