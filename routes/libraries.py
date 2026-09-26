from flask import jsonify, request, Blueprint
from models import Biblioteca
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

# POST /bibliotecas → solo admin (¿o bibliotecario?).


# PUT /bibliotecas/<id> → solo admin.

# DELETE /bibliotecas/<id> → solo admin.