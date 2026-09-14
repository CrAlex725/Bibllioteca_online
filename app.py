import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_migrate import Migrate

import models
from extensions import db

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/health', methods=['GET'])
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status":"ok"}), 200
    except Exception as e:
        return jsonify({"status":"error", "db": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
