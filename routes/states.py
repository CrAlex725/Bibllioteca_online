from models import Estado
from flask import jsonify, Blueprint,request

states_bp = Blueprint('states', __name__, url_prefix='/states')

@states_bp.route('', methods=['GET'])
def listar_estado():
    nombre = request.args.get('nombre')
    query = Estado.query
    
    if nombre:
        query = query.filter(Estado.nombre.ilike(f'%{nombre}%'))
    
    estado = query.all()
    return jsonify([e.to_dict() for e in estado]), 200