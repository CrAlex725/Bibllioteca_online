from extensions import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(35), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(70))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False) #fecha servidor de Postgres
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), unique=True)
    
    rol = db.relationship('Rol', back_populates='usuario', uselist=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Rol(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), unique=True, nullable=False)
    
    usuario = db.relationship('Usuario', back_populates='rol', uselist=False)
    
    def __repr__(self):
        return f'<Rol {self.nombre}>'