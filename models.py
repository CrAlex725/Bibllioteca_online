from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(35), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(60), nullable=False, unique=True)
    address = db.Column(db.String(70))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False) #fecha servidor de Postgres
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    bibliotecas_creadas = db.relationship('Biblioteca', back_populates='creador')
    asignaciones = db.relationship('Asignacion', back_populates='usuario')
    
    ejemplares_creados = db.relationship('Ejemplar', back_populates='creador')
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id" : self.id,
            "rut": self.rut,
            "name": self.name,
            "user_name": self.username,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "created_at": self.created_at.isoformat()
        }
    
    def es_admin(self):
        return self.is_admin
    
    def es_bibliotecario(self):
        for asignacion in self.asignaciones:
            if asignacion.rol.name.lower() in ["bibliotecario", "asistente"]:
                return True
        return False
    
    def puede_crear_libros(self):
        return self.es_admin() or self.es_bibliotecario()
        
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
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    creador = db.relationship('Usuario', back_populates='bibliotecas_creadas')
    
    asignaciones = db.relationship('Asignacion', back_populates='biblioteca')
    
    ejemplares = db.relationship('Ejemplar', back_populates='biblioteca')
    
    def to_dict(self):
        return{
            "id": self.id,
            "biblioteca": self.name,
            "direccion": self.address,
            "telefono": self.phone,
            "correo": self.email,
            "estado_activo": self.is_active,
            "es_publica":self.is_public,
            "creado_por": self.creador.name if self.creador else None
        }
    
    def __repr__(self):
        return f'<Biblioteca {self.name}>'
    
class Asignacion(db.Model):
    __tablename__ = 'asignaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    biblioteca_id = db.Column(db.Integer, db.ForeignKey('bibliotecas.id'), nullable=False)
    is_owner = db.Column(db.Boolean, default=False, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'biblioteca_id', name='uq_usuario_biblioteca'),
    )
    
    usuario = db.relationship('Usuario', back_populates='asignaciones')
    rol = db.relationship('Rol', back_populates='asignaciones')
    biblioteca = db.relationship('Biblioteca', back_populates='asignaciones')
    
    def __repr__(self):
        return f'<Asignacion u={self.usuario_id} r={self.rol_id} b={self.biblioteca_id}>'
    
libro_autor = db.Table(
    'libro_autor',
    db.Column('libro_id', db.Integer, db.ForeignKey('libros.id'), primary_key=True),
    db.Column('autor_id', db.Integer, db.ForeignKey('autores.id'), primary_key=True),
)

class Libro(db.Model):
    __tablename__ = 'libros'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False) 
    title = db.Column(db.String(200), nullable=False)
    year_publication = db.Column(db.Integer)
    clasificacion = db.Column(db.String(100))
    created_at =db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    
    editorial_id = db.Column(db.Integer, db.ForeignKey('editoriales.id'), nullable=False)
    editorial = db.relationship('Editorial', back_populates='libros')
    
    autores = db.relationship('Autor', secondary=libro_autor, back_populates='libros')
    
    ejemplares = db.relationship('Ejemplar', back_populates='libro')
    
    def to_summary(self):
        return{
            "isbn": self.isbn,
            "title" : self.title,
            "year_publication": self.year_publication,
            "autores": [{"id":a.id, "nombre":a.nombre} for a in self.autores]
        }
        
    def to_dict(self):
        return {
        "isbn": self.isbn,
        "title": self.title,
        "year_publication": self.year_publication,
        "clasificacion": self.clasificacion,
        "editorial": {
            "id": self.editorial.id,
            "nombre": self.editorial.nombre
        },
        "autores": [
            {"id": autor.id, "nombre": autor.nombre}
            for autor in self.autores
        ],
        "created_at": self.created_at.isoformat()
    }

    def __repr__(self):
        return f'<Libro {self.isbn}>'
    
class Editorial(db.Model):
    __tablename__ = 'editoriales'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    
    libros = db.relationship('Libro', back_populates='editorial')
    
    def __repr__(self):
        return f'<Editorial {self.nombre}>'

class Autor(db.Model):
    __tablename__ = 'autores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    
    libros = db.relationship('Libro', secondary=libro_autor, back_populates='autores')
    
    def __repr__(self):
        return f'<Autor {self.nombre}>'
    
class Estado(db.Model):
    __tablename__ = 'estados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    
    ejemplares = db.relationship('Ejemplar', back_populates='estado')
    
    def __repr__(self):
        return f'<Estado: {self.nombre}>'

class Ejemplar(db.Model):
    __tablename__ = 'ejemplares'
    
    id = db.Column(db.Integer, primary_key=True)
    libro_id = db.Column(db.Integer, db.ForeignKey('libros.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
    biblioteca_id = db.Column(db.Integer, db.ForeignKey('bibliotecas.id'), nullable=False)
    signatura = db.Column(db.String(100))
    numero_ejemplar = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default = db.func.current_timestamp(), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('libro_id', 'numero_ejemplar', name='uq_libro_numero_ejemplar'),
    )
    
    estado = db.relationship('Estado', back_populates='ejemplares')
    
    libro = db.relationship('Libro', back_populates='ejemplares')
    
    creador = db.relationship('Usuario', back_populates='ejemplares_creados')
    
    biblioteca = db.relationship('Biblioteca', back_populates='ejemplares')
    
    def __repr__(self):
        return f'<Ejemplar libro={self.libro_id} num={self.numero_ejemplar}>'
    