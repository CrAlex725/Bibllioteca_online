from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from models import Ejemplar, Estado
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