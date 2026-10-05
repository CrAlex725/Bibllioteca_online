from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from models import (Usuario,Ejemplar, Asignacion, Prestamo, Estado)
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from datetime import datetime, timedelta
from helpers import normalizar_rut

prestamos_bp = Blueprint('prestamos', __name__, url_prefix='/prestamos')

@prestamos_bp.route('', methods=['POST'])
@jwt_required()
def crear_prestamo():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    ejemplar_id = data.get('ejemplar_id')
    rut = data.get('rut')
    dias = data.get('dias')
    
    if not ejemplar_id or not  rut:
        return jsonify({"error":"los campos ejemplar y usuario son obligatorios"}), 400
    try:
        ejemplar_id = int(ejemplar_id)
    except (TypeError, ValueError):
        return jsonify({"error":"los vaolres deben ser de tipo entero"}), 400
    
    rut = normalizar_rut(rut)
    
    if not rut:
        return jsonify({"error":"El rut es obligatorio"}), 400
    
    if not dias:
        dias = 14
    else:
        try:
            dias =int(dias)
        except(TypeError, ValueError):
            return jsonify({"error":"dias debe ser un entero"}), 400
        
    if dias < 1 or dias > 30:
        return jsonify ({"error":"dias debe estar entre 1 y 30"}), 400
        
    user_id = int(get_jwt_identity())
    creador = Usuario.query.filter_by(id=user_id).first()
    
    if not creador:
        return jsonify({"error":"El usuario no existe"}), 401
    
    ejemplar = Ejemplar.query.filter_by(id=ejemplar_id).first()
    
    if not ejemplar:
        return jsonify({"error":"El ejemplar NO existe"}), 404
    
    if not creador.es_admin():
        if not creador.tiene_asignacion_en(ejemplar.biblioteca_id):
            return jsonify({"error":"No tienes permiso para realizar esta accion"}), 403
        
    biblioteca = ejemplar.biblioteca
    
    if not biblioteca.is_active:
        return jsonify({"error": "La biblioteca no está activa"}), 409
    
    if not biblioteca.is_public:
        return jsonify({"error":"La bivlioteca no es pública, no puede realizar prestamos"}), 409
    
    if ejemplar.estado.nombre.lower() != 'disponible':
        return jsonify({"error":"El ejemplar no está disponible"}), 409
    
    usuario_destinatario = Usuario.query.filter(
        db.func.replace(db.func.replace(
            Usuario.rut, '-', ""),".","") == rut
    ).first()
    if not usuario_destinatario:
        return jsonify({"error":"El destinatario No existe"}), 404
    
    if not usuario_destinatario.perfil_completo():
        return jsonify({"error":"El usuario No tiene los datos requeridos"}), 403
    
    asignacion = Asignacion.query.filter_by(usuario_id=usuario_destinatario.id, biblioteca_id=biblioteca.id).first()
    
    if not asignacion:
        return jsonify({"error":"El usuario No tiene asignacion en la biblioteca"}), 403
    
    if asignacion.rol.name.lower() not in ["lector", "bibliotecario", "asistente"]:
        return jsonify({"error":"El rol del usuario No tiene permiso para pedir prestado"}), 403
    
    ahora = datetime.utcnow()
    
    prestamo_vencido = Prestamo.query.filter(
        Prestamo.usuario_id == usuario_destinatario.id,
        Prestamo.fecha_devolucion.is_(None),
        Prestamo.fecha_vencimiento < ahora
    ).first()
    
    if prestamo_vencido:
        return jsonify({"error":"El usuario tiene uno o mas prestamos vencidos"}), 409
    
    prestamos_activos = Prestamo.query.filter(
        Prestamo.usuario_id == usuario_destinatario.id,
        Prestamo.fecha_devolucion.is_(None)
    ).count()
    
    if prestamos_activos >= 3:
        return jsonify({"error":"Ya tienes 3 prestamos activos a tu nombre, por favor revisa"}), 409
    
    vencimiento = ahora + timedelta(days=dias)
    
    estado_pendiente = Estado.query.filter(
        db.func.lower(Estado.nombre) == "prestado"
    ).first()
    
    if not estado_pendiente:
        return jsonify({"error":"El estado prestado No existe"}), 500
    
    prestamo = Prestamo(
        ejemplar_id=ejemplar_id,
        usuario_id=usuario_destinatario.id,
        biblioteca_id=biblioteca.id,
        fecha_prestamo=ahora,
        fecha_vencimiento =vencimiento,
        created_by=creador.id
    )
    
    try:
        db.session.add(prestamo)
        ejemplar.estado_id = estado_pendiente.id
        db.session.commit()
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo salió mal en la creacion del prestamo"}), 409
    
    return jsonify(prestamo.to_dict()), 201

@prestamos_bp.route('/<int:id>/devolver', methods=['POST'])
@jwt_required()
def devolver_prestamo(id):
    user_id = int(get_jwt_identity())
    creador = Usuario.query.filter_by(id=user_id).first()
    
    if not creador:
        return jsonify({"error":"El usuario No existe"}), 401
    
    prestamo = Prestamo.query.filter_by(id=id).first()
    
    if not prestamo:
        return jsonify({"error":"El prestamo No existe"}), 404
    
    if not creador.es_admin():
        if not creador.tiene_asignacion_en(prestamo.biblioteca_id):
            return jsonify({"error":"No tienes permisos para realizar esta accion"}), 403
    
    if prestamo.fecha_devolucion is not None:
        return jsonify({"error":"El prestamo ya está marcado como devuelto"}), 409
    
    estado_disponible = Estado.query.filter(
        db.func.lower(Estado.nombre) == "disponible"
    ).first()
    
    if not estado_disponible:
        return jsonify({"error":"El estado disponible No existe"}) ,500
    
    ahora = datetime.utcnow()
    
    try:
        prestamo.fecha_devolucion = ahora
        prestamo.ejemplar.estado_id = estado_disponible.id
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"algo salió mal en el proceso de devolucion"}), 500
    
    return jsonify(prestamo.to_dict()), 200

@prestamos_bp.route('/mine', methods=['GET'])
@jwt_required()
def mis_prestamos():
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    prestamos = Prestamo.query.filter_by(usuario_id=usuario.id).order_by(Prestamo.fecha_prestamo.desc()).all()
    
    return jsonify([p.to_dict() for p in prestamos]), 200