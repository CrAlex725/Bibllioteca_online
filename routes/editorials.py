from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from models import Editorial, Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db

editorial_bp = Blueprint('editorials', __name__, url_prefix='/editorials')

@editorial_bp.route('', methods=['GET'])
def editorial():
    """
    Todas las editoriales requistradas
    No requiere Autenticacion
    ---
    parameters:
      - name: nombre
        in: query
        type: string
        required: false
        description: nombre parcial para buscar
    responses:
      200:
        description: respuesta de la consulta
    """
    nombre = request.args.get('nombre')
    query = Editorial.query
    
    if nombre:
        query = query.filter(Editorial.nombre.ilike(f'%{nombre}%'))
    
    editorial = query.all()
    return jsonify([e.to_dict() for e in editorial]), 200

@editorial_bp.route('/<int:id>', methods=['GET'])
def editorial_info(id):
    """
    Información individual de cada editorial
    No requiere autenticacion
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: id de la editorial
    responses:
      200:
        description: Consulta exitosa
      404:
        description: No exste el id
    """
    editorial = Editorial.query.filter_by(id=id).first()
    
    if not editorial:
        return jsonify({"error":"La editorial no existe"}), 404
    
    return jsonify(editorial.to_dict()),200

@editorial_bp.route('', methods=['POST'])
@jwt_required()
def crear_editorial():
    """
    Crear editorial
    Requiere Autenticacion de Admin o Bibliotecario
    ---
    security:
      - Bearer: []
    parameters:
      - name: nombre
        in: body
        required: true
        schema:
          type: object
          required:
            - nombre
          properties:
            nombre:
              type: string
          description: nueva editorial
    responses:
      201:
        description: Creación exitosa
      400:
        description: Datos inválidos
      401:
        description: Usuario Inexistente
      403:
        description: Usuario sin permiso
      409:
        description: editorial ya existente
      500:
        description: Algo salió mal
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    if not usuario.es_bibliotecario() and not usuario.es_admin():
        return jsonify({"error":"No tienes permiso para realizar esta accion"}), 403
    
    nombre = data.get('nombre')
    
    if not nombre or nombre.strip() == "":
        return jsonify ({"error":"debes entregar un nombre para la nueva editorial"}), 400
    
    editorial = Editorial.query.filter(
        db.func.lower(Editorial.nombre) == db.func.lower(nombre)
    ).first()
    
    if editorial:
        return jsonify({"error":"LA editorial ya existe"}), 409
    
    try:
        nueva_editorial = Editorial(
            nombre = nombre
        )
        db.session.add(nueva_editorial)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo salió mal con el proceso de creacion"}), 500
    
    return jsonify(nueva_editorial.to_dict()), 201

@editorial_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def editar_editorial(id):
    """
    Actualizar editorial existente
    Requiere Autenticacion de Administrador
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Id de la editorial a actualizar
    responses:
      200:
        description: Actualización Exitosa
      400:
        description: Datos Invalidos
      401:
        description: Usuario Inexistente
      403:
        description: Usaurio sin permiso
      404:
        description: Editorial No encontrada
      409:
        description: Editorial Ya existente
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}),400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"El usuario no tiene permiso para crear esta accion"}), 403

    editorial = Editorial.query.filter_by(id=id).first()
    
    if not editorial:
        return jsonify({"error":"La editorial No existe"}), 404
    
    nombre = data.get('nombre')
    
    if not nombre or nombre.strip() == "":
        return jsonify({"error":"debes asignar un nombre a la editorial"}), 400
    
    existe = Editorial.query.filter(
        db.func.lower(Editorial.nombre) == db.func.lower(nombre),
        Editorial.id != id
    ).first()
    
    if existe:
        return jsonify({"error":"Ya existe otra editorial con ese nombre"}), 409
    
    editorial.nombre = nombre
    
    db.session.commit()
    return jsonify(editorial.to_dict()),200

@editorial_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_editorial(id):
    """
    Eliminar editorial NO asociada
    Requiere Autenticacion de Administrador
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: id de editorial para eliminar
    responses:
      204:
        description: Eliminacion completa
      401:
        description: Usuario Inexistente
      403:
        description: Usuario sin permisos
      404:
        description: Editorial NO encontrada
      409:
        description: Algo salió mal en la eliminacion
    """
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify ({"error":"El usuario no existe"}),401
    
    if not usuario.es_admin():
        return jsonify({"error":"No tienes permiso para realizar esta accion"}), 403
    
    editorial = Editorial.query.filter_by(id=id).first()
    
    if not editorial:
        return jsonify({"error":"La editorial No existe"}), 404
    
    try:
        db.session.delete(editorial)
        db.session.commit()
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo salió mal en la eliminación de la Editorial"}), 409
    
    return "", 204