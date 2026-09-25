import os
from flask import Flask
from dotenv import load_dotenv
from flask_migrate import Migrate


from extensions import db, jwt
from routes.auth import auth_bp
from routes.books import books_bp
from routes.health import health_bp

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']

db.init_app(app)
migrate = Migrate(app, db)
jwt.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(health_bp)
    
if __name__ == '__main__':
    app.run(debug=True)
