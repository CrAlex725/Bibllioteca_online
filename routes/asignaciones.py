from flask import jsonify, request, Blueprint
from models import (Usuario, Asignacion)
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