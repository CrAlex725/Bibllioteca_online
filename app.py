import os
from flask import Flask
from dotenv import load_dotenv
from flask_migrate import Migrate
from flasgger import Swagger

from flask_cors import CORS

from extensions import db, jwt
from routes.auth import auth_bp
from routes.books import books_bp
from routes.health import health_bp
from routes.libraries import libraries_bp
from routes.states import states_bp
from routes.exemplars import exemplars_bp
from routes.editorials import editorial_bp
from routes.prestamos import prestamos_bp
from routes.asignaciones import asignaciones_bp
from routes.authors import autores_bp

load_dotenv(override=False)

app = Flask(__name__)

CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500", "null"])

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']

swagger_template = {
    "securityDefinitions": {
        "Bearer": {
            "type" :"apiKey",
            "name" : "Authorization",
            "in" : "header"
        }
    }
}

db.init_app(app)
migrate = Migrate(app, db)
jwt.init_app(app)
Swagger(app, template=swagger_template)

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(health_bp)
app.register_blueprint(libraries_bp)
app.register_blueprint(states_bp)
app.register_blueprint(exemplars_bp)
app.register_blueprint(editorial_bp)
app.register_blueprint(prestamos_bp)
app.register_blueprint(asignaciones_bp)
app.register_blueprint(autores_bp)
    
if __name__ == '__main__':
    app.run(debug=True)
