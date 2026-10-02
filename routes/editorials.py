from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from models import Editorial, Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db

editorial_bp = Blueprint('editorials', __name__, url_prefix='/editorials')

@editorial_bp.route('', methods=['GET'])
def editorial():
    nombre = request.args.get('nombre')
    query = Editorial.query
    
    if nombre:
        query = query.filter(Editorial.nombre.ilike(f'%{nombre}%'))
    
    editorial = query.all()
    return jsonify([e.to_dict() for e in editorial]), 200

@editorial_bp.route('/<int:id>', methods=['GET'])
def editorial_info(id):
    editorial = Editorial.query.filter_by(id=id).first()
    
    if not editorial:
        return jsonify({"error":"La editorial no existe"}), 404
    
    return jsonify(editorial.to_dict()),200

@editorial_bp.route('', methods=['POST'])
@jwt_required()
def crear_editorial():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"No tienes permiso para realizar esta accion"}), 403
    
    nombre = data.get('nombre')
    
    if not nombre:
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
    
    if not nombre:
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