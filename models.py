from extensions import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(35), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(70))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False) #fecha servidor de Postgres
    
    asignaciones = db.relationship('Asignacion', back_populates='usuario')
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
class Rol(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    
    asignaciones = db.relationship('Asignacion', back_populates='rol')
    
    def __repr__(self):
        return f'<Rol {self.name}>'
    
class Biblioteca(db.Model):
    __tablename__ = 'bibliotecas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    
    asignaciones = db.relationship('Asignacion', back_populates='biblioteca')
    
    def __repr__(self):
        return f'<Biblioteca {self.name}>'
    
class Asignacion(db.Model):
    __tablename__ = 'asignaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    biblioteca_id = db.Column(db.Integer, db.ForeignKey('bibliotecas.id'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'biblioteca_id', name='uq_usuario_biblioteca'),
    )
    
    usuario = db.relationship('Usuario', back_populates='asignaciones')
    rol = db.relationship('Rol', back_populates='asignaciones')
    biblioteca = db.relationship('Biblioteca', back_populates='asignaciones')
    
    def __repr__(self):
        return f'<Asignacion u={self.usuario_id} r={self.rol_id} b={self.biblioteca_id}>'