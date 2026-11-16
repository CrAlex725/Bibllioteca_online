from flask import jsonify, request, Blueprint
from models import (Autor, Usuario)
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

autores_bp = Blueprint('authors', __name__, url_prefix='/authors')

@autores_bp.route('', methods=['GET'])
def todos_los_autores():
    nombre = request.args.get('nombre')
    
    query = Autor.query
    
    if nombre:
        query = query.filter(Autor.nombre.ilike(f'%{nombre}%'))
        
    autores = query.all()
    return jsonify([a.to_dict() for a in autores]), 200

@autores_bp.route('/<int:id>', methods=['GET'])
def detalle_autor(id):
    autor = Autor.query.filter_by(id=id).first()
    
    if not autor:
        return jsonify({"error":"El Autor No existe"}), 404
    
    return jsonify(autor.to_dict()), 200
    
@autores_bp.route('', methods=['POST'])
@jwt_required()
def crear_autor():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    nombre = data.get('nombre')
    if not nombre or not nombre.strip():
        return jsonify({"error": "El nombre de autor es requerido"}), 400
    nombre = nombre.strip()
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"No tienes permiso para realizar esta accion"}), 403
    
    autor = Autor.query.filter(
        func.lower(Autor.nombre) == nombre.lower()
        ).first()
    
    if autor:
        return jsonify({"error":f"El autor Ya existe en la db"}), 409
    try:
        autor_crear = Autor(nombre=nombre)
        db.session.add(autor_crear)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo salió mal en la creación del autor"}), 409
        
    
    return jsonify(autor_crear.to_dict()), 201
    
@autores_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_autor(id):
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    nombre = data.get('nombre')
    if not nombre or not nombre.strip():
        return jsonify({"error": "El nombre de autor es requerido"}), 400
    nombre = nombre.strip()
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"No tienes permiso para realizar esta accion"}), 403
    
    autor = Autor.query.filter_by(id=id).first()
    
    if not autor:
        return jsonify({"error":f"El autor No existe en la db"}), 404
    
    autor_nombre = Autor.query.filter(
        func.lower(Autor.nombre) == nombre.lower(),
        Autor.id != id
        ).first()

    if autor_nombre:
        return jsonify({"error": f"El autor Ya existe en la db"}), 409
    
    autor.nombre = nombre
    
    db.session.commit()
    
    return jsonify(autor.to_dict()), 200
    
@autores_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_autor(id):
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    if not usuario.es_admin():
        return jsonify({"error":"No tienes permiso para realizar esta accion"}), 403
    
    autor = Autor.query.filter_by(id=id).first()
    
    if not autor:
        return jsonify({"error":f"El autor No existe en la db"}), 404
    
    try:
        db.session.delete(autor)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"No se puede eliminar, el autor tiene libros asociados"}), 409
    
    return "", 204