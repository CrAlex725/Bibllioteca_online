from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from models import Ejemplar, Estado, Usuario, Libro, Biblioteca
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db

exemplars_bp = Blueprint('exemplars', __name__, url_prefix='/exemplars')

@exemplars_bp.route('', methods=['GET'])
@jwt_required()
def listar_ejemplares():
    libro_id = request.args.get('libro_id')
    biblioteca_id = request.args.get('biblioteca_id')
    estado_id = request.args.get('estado_id')
    disponibilidad = request.args.get('disponibilidad')
    
    query = Ejemplar.query

    if libro_id:
        query = query.filter(Ejemplar.libro_id == int(libro_id))
        
    if biblioteca_id:
        query = query.filter(Ejemplar.biblioteca_id == int(biblioteca_id))
        
    if estado_id:
        query = query.filter(Ejemplar.estado_id == int(estado_id))
        
    if disponibilidad and disponibilidad.lower() == "true":
        query = query.filter(Ejemplar.estado.has(db.func.lower(Estado.nombre) == "disponible"))
        
    ejemplar = query.all()
    
    return jsonify([e.to_dict() for e in ejemplar]), 200

@exemplars_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def ejemplar_detallado(id):
    ejemplar = Ejemplar.query.filter_by(id=id).first()
    
    if not ejemplar:
        return jsonify({"error":"Ejemplar NO encontrado"}), 404
    
    return jsonify(ejemplar.to_dict()), 200

@exemplars_bp.route('', methods=['POST'])
@jwt_required()
def agregar_ejemplar():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON invalido o vacío"}), 400
    
    biblioteca_id = data.get('biblioteca_id')
    libro_id = data.get('libro_id')
    numero_ej = data.get('numero_ejemplar')
    
    if not biblioteca_id:
        return jsonify({"error":"Debes agregar una biblioteca a la peticion"}), 400
    
    if not libro_id:
        return jsonify({"error":"Debes agregar un libro a la peticion"}), 400

    try:
        biblioteca_id = int(biblioteca_id)
        libro_id = int(libro_id)
    except (TypeError, ValueError):
        return jsonify({"error":"Ambos ID deben ser enteros"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    if not usuario.es_admin():
        if not usuario.tiene_asignacion_en(biblioteca_id):
            return jsonify({"error":"El usuario No tiene permisos para realizar esta accion"}), 403
        
    libro = Libro.query.filter_by(id=libro_id).first()
    if not libro:
        return jsonify({"error":"El libro no existe"}), 404
    
    biblioteca = Biblioteca.query.filter_by(
        id=biblioteca_id, is_active=True
        ).first()
    
    if not biblioteca:
        return jsonify({"error":"La biblioteca no existe"}), 404
    
    estado = Estado.query.filter(db.func.lower(Estado.nombre) == "disponible").first()
    
    if not estado:
        return jsonify({"error":"Estado 'Disponible' no configurado"}), 500
    
    if numero_ej is not None:
        try:
            numero_ej = int(numero_ej)
            
        except (TypeError, ValueError):
            return jsonify({"error":"El numero de ejemplar debe ser entero"}), 400
        
        if numero_ej < 0:
            return jsonify({"error":"El numero de ejemplar debe ser mayor a 0"}), 400
        
        ejemplar = Ejemplar.query.filter_by(
            libro_id=libro_id, biblioteca_id=biblioteca_id, 
            numero_ejemplar=numero_ej
            ).first()
        
        if ejemplar:
            ejemplares = Ejemplar.query.filter_by(
            libro_id=libro_id, biblioteca_id=biblioteca_id
            ).order_by(Ejemplar.numero_ejemplar).all()
            
            lista = [e.numero_ejemplar for e in ejemplares]
            return jsonify({
                "error":f"El numero de ejemplar YA existe", 
                "numeros_ocupados":lista
                }), 409
        
        numero_final = numero_ej
        
    else:
        max_actual = db.session.query(
            db.func.max(Ejemplar.numero_ejemplar)
            ).filter(
                Ejemplar.libro_id == libro_id,
                Ejemplar.biblioteca_id == biblioteca_id
            ).scalar()
        
        numero_final = (max_actual or 0) + 1
    
    nuevo_ejemplar = Ejemplar(
        libro_id = libro_id,
        biblioteca_id = biblioteca_id,
        numero_ejemplar = numero_final,
        estado_id = estado.id,
        created_by = usuario.id,
        signatura = None
    )
    
    try:
        db.session.add(nuevo_ejemplar)
        db.session.commit()
        
    except IntegrityError:
        db.session.rollback()
        ocupados = [e.numero_ejemplar for e in Ejemplar.query.filter_by(
            libro_id=libro_id, biblioteca_id=biblioteca_id
        ).order_by(Ejemplar.numero_ejemplar).all()]
        return jsonify({
            "error":"Conflicto al asignar el número de ejemplar, vuelve a intentarlo",
            "numeros_ocupados": ocupados
        }), 409
    
    return jsonify(nuevo_ejemplar.to_dict()), 201