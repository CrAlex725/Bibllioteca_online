from flask import jsonify, request, Blueprint
from models import Editorial

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

