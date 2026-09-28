from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from models import Biblioteca, Usuario, Rol, Asignacion
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
@libraries_bp.route('', methods=['POST'])
@jwt_required()
def crear_biblioteca():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    if not usuario.perfil_completo():
        return jsonify({"error":"El usuario no tiene los datos completos"}), 403
    
    name = data.get('name')
    address = data.get('address')
    phone = data.get('phone')
    email = data.get('email')
    is_public = data.get('is_public')
    
    if not name or not address or not phone or not email or is_public is None:
        return jsonify({"error":"Uno de los datos no fue otorgados"}), 400
    
    name = name.strip()
    address = address.strip()
    phone = phone.strip()
    email = email.strip()
    
    for asignacion in usuario.asignaciones:
        if asignacion.is_owner and asignacion.biblioteca.is_active:
            return jsonify({"error":"El usuario ya es jefe de una biblioteca activa"}), 403

    rol_bibliotecario = Rol.query.filter_by(name="bibliotecario").first()
    
    if not rol_bibliotecario:
        return jsonify({"error":"El rol solicitado no está disponible"}), 500
    
    try:
        biblioteca = Biblioteca(
            name= name,
            address=address,
            phone=phone,
            email=email,
            is_public=is_public,
            created_by=usuario.id
        )
        
        db.session.add(biblioteca)
        db.session.flush()
        
        asignacion = Asignacion(
            usuario_id=usuario.id,
            rol_id=rol_bibliotecario.id,
            biblioteca_id=biblioteca.id,
            is_owner=True
        )
        db.session.add(asignacion)
        db.session.commit()
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":"Algo Salió mal durante el proceso de creacion de la biblioteca"}), 500
    
    return jsonify(biblioteca.to_dict()), 201

# PUT /bibliotecas/<id> → solo admin.
@libraries_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_biblioteca(id):
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error":"JSON Invalido o vacío"}), 400
    
    user_id= int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario no existe"}), 401
    
    biblioteca = Biblioteca.query.filter_by(id=id).first()
    
    if not biblioteca:
        return jsonify({"error":"La biblioteca NO existe"}), 404
    
    if not (usuario.es_admin() or usuario.es_jefe_de(biblioteca.id)):
        return jsonify({"error":"no tienes permiso para realizar esta accion"}), 403
    
    if 'name' in data:
        biblioteca.name = data['name']
    
    if 'address' in data:
        biblioteca.address = data['address']
        
    if 'phone' in data:
        biblioteca.phone = data['phone']
    
    if 'is_public' in data:
        biblioteca.is_public = data['is_public']
        
    db.session.commit()
    return jsonify (biblioteca.to_dict()), 200

# DELETE /bibliotecas/<id> → solo admin.
@libraries_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_biblioteca(id):
    user_id = int(get_jwt_identity())
    usuario = Usuario.query.filter_by(id=user_id).first()
    
    if not usuario:
        return jsonify({"error":"El usuario No existe"}), 401
    
    biblioteca = Biblioteca.query.filter_by(id=id).first()
    
    if not biblioteca:
        return jsonify({"error":f"La biblioteca NO existe"}), 404
    
    if not biblioteca.is_active:
        return jsonify({"error":"La biblioteca NO existe"}), 404

    if not (usuario.es_admin() or usuario.es_jefe_de(id)):
        return jsonify({"error":"no tienes permiso para realizar esta accion"}), 403

    biblioteca.is_active = False
    
    db.session.commit()
    return "", 204