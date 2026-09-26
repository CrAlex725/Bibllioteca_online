from flask import jsonify, request, Blueprint
from models import Biblioteca, Usuario
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db

libraries_bp = Blueprint('libraries', __name__, url_prefix='/libraries')

# GET /bibliotecas → lista pública.
@libraries_bp.route('', methods=['GET'])
def biblioteca():
    address = request.args.get('address')
    query = Biblioteca.query
    
    if address:
        query = query.filter(Biblioteca.address.ilike(f'%{address}%'))
    
    biblio = query.filter_by(is_public=True, is_active=True).all()
    return jsonify([b.to_dict() for b in biblio]), 200

# GET /bibliotecas/<id> → detalle público.
@libraries_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def perfil_biblioteca(id):
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    if not usuario:
        return jsonify ({"error":"El usuario no existe"}),401
    
    biblioteca = Biblioteca.query.filter_by(id=id).first()
    
    if not biblioteca:
        return jsonify({"error":"La Biblioteca No Existe"}), 404
    
    if not biblioteca.is_active:
        return jsonify ({"error":"la Biblioteca no está disponible"}), 404
    
    if not biblioteca.is_public:
        return jsonify ({"error":"No puedes ver esta Biblioteca"}), 404
    
    return jsonify(biblioteca.to_dict()), 200


# POST /bibliotecas → solo admin (¿o bibliotecario?).


# PUT /bibliotecas/<id> → solo admin.

# DELETE /bibliotecas/<id> → solo admin.