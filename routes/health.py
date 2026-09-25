from flask import jsonify, Blueprint
from extensions import db

health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('', methods=['GET'])
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status":"ok"}), 200
    except Exception as e:
        return jsonify({"status":"error", "db": str(e)}), 500