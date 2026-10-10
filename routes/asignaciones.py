from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from models import (Usuario, Asignacion, Biblioteca, Rol)
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers import normalizar_rut
from extensions import db

asignaciones_bp = Blueprint('asignaciones', __name__, url_prefix='/asignaciones')

@asignaciones_bp.route('', methods=['GET'])
@jwt_required()
def asignaciones():
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    query = Asignacion.query
    
    if not usuario.es_admin():
        bibliotecas_gestionadas =[
            a.biblioteca_id for a in usuario.asignaciones
            if a.rol.name.lower() in ["bibliotecario","asistente"]
        ]
        if bibliotecas_gestionadas:
            query = query.filter(Asignacion.biblioteca_id.in_(bibliotecas_gestionadas))
            
        elif usuario.asignaciones:
            query = query.filter(Asignacion.usuario_id == usuario.id)
        
        else:
            return jsonify({"error":"No tienes permiso"}), 403
        
    usuario_id = request.args.get('usuario_id')
    biblioteca_id = request.args.get('biblioteca_id')
    rol_id = request.args.get('rol_id')
    is_owner = request.args.get('is_owner')
    rut = request.args.get('usuario_rut')
    
    if usuario_id:
        try:
            usuario_id = int(usuario_id)
            query = query.filter_by(usuario_id=usuario_id)
        except ValueError:
            return jsonify({"error":"el valor solicitado debe ser entero"}), 400
    
    if rut:
        rut_norm = normalizar_rut(rut)
        query = query.filter(
            Asignacion.usuario.has(
                db.func.replace(db.func.replace(Usuario.rut, '-', ''), '.', '') == rut_norm
            )
        )
    
    if biblioteca_id:
        try:
            biblioteca_id = int(biblioteca_id)
            query = query.filter_by(biblioteca_id=biblioteca_id)
        except ValueError:
            return jsonify({"error":"el valor solicitado debe ser entero"}), 400
        
    if rol_id:
        try:
            rol_id= int(rol_id)
            query = query.filter_by(rol_id=rol_id)
        except ValueError:
            return jsonify({"error":"el valor solicitado debe ser entero"}), 400
    
    
        
    if is_owner is not None:
        if is_owner.lower() in ("true","1"):
            query = query.filter(Asignacion.is_owner == True)
        elif is_owner.lower() in ("false","0"):
            query = query.filter(Asignacion.is_owner == False)
        else:
            return jsonify({"error":"is_owner, debe ser true o false"}), 400
    asignaciones = query.order_by(Asignacion.id.asc()).all()
    return jsonify([a.to_dict() for a in asignaciones]), 200

@asignaciones_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def una_asignacion(id):
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}),401
    
    asignacion = Asignacion.query.filter_by(id=id).first()
    
    if not asignacion:
        return jsonify({"error":"La asignacion No existe"}), 404
    
    if usuario.es_admin():
        return jsonify(asignacion.to_dict()),200
    
    bibliotecas =[
        a.biblioteca_id for a in usuario.asignaciones
        if a.rol.name.lower() in ["bibliotecario","asistente"]
    ]
    
    if asignacion.biblioteca_id in bibliotecas:
        return jsonify(asignacion.to_dict()), 200
    
    if asignacion.usuario_id == usuario.id:
        return jsonify(asignacion.to_dict()), 200
    
    return jsonify({"error":"La asignacion no existe"}), 404

@asignaciones_bp.route('', methods=['POST'])
@jwt_required()
def crear_asignacion():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON inválido o vacío"}), 400
    
    usuario_id = data.get('usuario_id')
    biblioteca_id = data.get('biblioteca_id')
    rol_id = data.get('rol_id')
    
    if None in (usuario_id, biblioteca_id, rol_id):
        return jsonify({"error": "Faltan campos obligatorios: usuario_id, biblioteca_id, rol_id"}), 400
    
    try:
        usuario_id = int(usuario_id)
        biblioteca_id = int(biblioteca_id)
        rol_id = int(rol_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Todos los datos deben ser enteros"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    usuario_valido = (
        usuario.es_admin() or 
        usuario.es_jefe_de(biblioteca_id)
        )
    
    if not usuario_valido:
        return jsonify({"error":"No tienes permiso para realizar esta accion"}), 403
    
    biblioteca_asignacion = Biblioteca.query.filter_by(
        id=biblioteca_id
        ).first()
    if not biblioteca_asignacion:
        return jsonify({"error":"La biblioteca NO existe"}), 404
    
    usuario_asignacion = Usuario.query.filter_by(
        id=usuario_id
        ).first()
    if not usuario_asignacion:
        return jsonify({"error":"El usuario NO existe"}), 404
    
    if not biblioteca_asignacion.is_active:
        return jsonify({"error":"La biblioteca NO está activa"}), 409
    
    rol_asignacion = Rol.query.filter_by(
        id=rol_id
        ).first()
    if not rol_asignacion:
        return jsonify({"error":"El rol NO existe"}), 400
    
    if rol_asignacion.name.lower() == "bibliotecario":
        return jsonify({"error":"El rol NO puede ser bibliotecario"}), 403
    
    verificar_asignacion = Asignacion.query.filter_by(
            usuario_id=usuario_id,
            biblioteca_id=biblioteca_id,
        ).first()
    
    if verificar_asignacion:
        return jsonify({"error":"Ya existe una asignacion en esta biblioteca"}), 409
    
    nueva_asignacion = Asignacion(
                usuario_id=usuario_id,
                biblioteca_id=biblioteca_id,
                rol_id=rol_id,
                is_owner=False
            )
    
    try:
        db.session.add(nueva_asignacion)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo salió mal durante el proceso de asignar"}),409
    
    return jsonify(nueva_asignacion.to_dict()), 201