from app import app
from extensions import db
from models import (
    Usuario,
    Rol,
    Biblioteca,
    Asignacion,
    Libro,
    Editorial,
    Autor,
    Ejemplar,
    Estado
)
from werkzeug.security import generate_password_hash


def get_or_create(model, defaults=None, **kwargs):
    """Busca un registro por kwargs; si no existe, lo crea con defaults."""
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    params = {**kwargs, **(defaults or {})}
    instance = model(**params)
    db.session.add(instance)
    db.session.flush()
    return instance, True


with app.app_context():
    # ---------- 3 Roles ----------
    roles_data = ["Administrador", "Bibliotecario", "Asistente"]
    roles = []
    for name in roles_data:
        rol, _ = get_or_create(Rol, name=name)
        roles.append(rol)

    # ---------- 3 Bibliotecas ----------
    bibliotecas_data = [
        {
            "name": "Biblioteca Central",
            "address": "Av. Principal 100",
            "phone": "+56223456789",
            "email": "central@biblioteca.cl",
        },
        {
            "name": "Biblioteca Norte",
            "address": "Calle Norte 250",
            "phone": "+56229876543",
            "email": "norte@biblioteca.cl",
        },
        {
            "name": "Biblioteca Sur",
            "address": "Av. Sur 500",
            "phone": "+56221112223",
            "email": "sur@biblioteca.cl",
        },
    ]
    bibliotecas = []
    for data in bibliotecas_data:
        bib, _ = get_or_create(Biblioteca, name=data["name"], defaults=data)
        bibliotecas.append(bib)

    # ---------- 3 Usuarios ----------
    usuarios_data = [
        {
            "rut": "12345678-9",
            "name": "Juan",
            "username": "juanp",
            "phone": "+56912345678",
            "email": "juan@example.com",
            "address": "Av. Siempre Viva 123",
            "password_hash": generate_password_hash("password123"),
        },
        {
            "rut": "98765432-1",
            "name": "María",
            "username": "mariag",
            "phone": "+56987654321",
            "email": "maria@example.com",
            "address": "Calle Falsa 456",
            "password_hash": generate_password_hash("password123"),
        },
        {
            "rut": "11223344-5",
            "name": "Pedro",
            "username": "pedrol",
            "phone": "+56911223344",
            "email": "pedro@example.com",
            "address": "Av. Libertad 789",
            "password_hash": generate_password_hash("password123"),
        },
    ]
    usuarios = []
    for data in usuarios_data:
        user, _ = get_or_create(Usuario, username=data["username"], defaults=data)
        usuarios.append(user)

    # ---------- Asignaciones ----------
    asignaciones_data = [
        (usuarios[0], roles[0], bibliotecas[0]),
        (usuarios[1], roles[1], bibliotecas[1]),
        (usuarios[2], roles[2], bibliotecas[2]),
    ]
    for usuario, rol, biblioteca in asignaciones_data:
        get_or_create(
            Asignacion,
            usuario_id=usuario.id,
            biblioteca_id=biblioteca.id,
            defaults={"rol_id": rol.id},
        )

    # ---------- 3 Editoriales ----------
    editoriales_data = [
        "Editorial Planeta",
        "Penguin Random House",
        "Editorial Anagrama",
    ]
    editoriales = []
    for nombre in editoriales_data:
        ed, _ = get_or_create(Editorial, nombre=nombre)
        editoriales.append(ed)

    # ---------- 2 Autores ----------
    autores_data = [
        "Gabriel García Márquez",
        "Isabel Allende",
    ]
    autores = []
    for nombre in autores_data:
        autor, _ = get_or_create(Autor, nombre=nombre)
        autores.append(autor)

    # ---------- 10 Libros ----------
    libros_data = [
        {
            "isbn": "9780307474728",
            "title": "Cien años de soledad",
            "year_publication": 1967,
            "clasificacion": "Novela",
            "editorial_id": editoriales[0].id,
            "autores": [autores[0]],
        },
        {
            "isbn": "9780060883287",
            "title": "La casa de los espíritus",
            "year_publication": 1982,
            "clasificacion": "Novela",
            "editorial_id": editoriales[1].id,
            "autores": [autores[1]],
        },
        {
            "isbn": "9788437604947",
            "title": "Crónica de una muerte anunciada",
            "year_publication": 1981,
            "clasificacion": "Novela",
            "editorial_id": editoriales[2].id,
            "autores": [autores[0]],
        },
        {
            "isbn": "9788401242364",
            "title": "El amor en los tiempos del cólera",
            "year_publication": 1985,
            "clasificacion": "Novela",
            "editorial_id": editoriales[0].id,
            "autores": [autores[0]],
        },
        {
            "isbn": "9789507311192",
            "title": "Eva Luna",
            "year_publication": 1987,
            "clasificacion": "Novela",
            "editorial_id": editoriales[1].id,
            "autores": [autores[1]],
        },
        {
            "isbn": "9780307389732",
            "title": "El otoño del patriarca",
            "year_publication": 1975,
            "clasificacion": "Novela",
            "editorial_id": editoriales[2].id,
            "autores": [autores[0]],
        },
        {
            "isbn": "9780061120092",
            "title": "Paula",
            "year_publication": 1994,
            "clasificacion": "Memorias",
            "editorial_id": editoriales[0].id,
            "autores": [autores[1]],
        },
        {
            "isbn": "9788437604978",
            "title": "Relato de un náufrago",
            "year_publication": 1970,
            "clasificacion": "Crónica",
            "editorial_id": editoriales[1].id,
            "autores": [autores[0]],
        },
        {
            "isbn": "9788401352356",
            "title": "La ciudad y los perros",
            "year_publication": 1963,
            "clasificacion": "Novela",
            "editorial_id": editoriales[2].id,
            "autores": [autores[0]],
        },
        {
            "isbn": "9789507311208",
            "title": "De amor y de sombra",
            "year_publication": 1984,
            "clasificacion": "Novela",
            "editorial_id": editoriales[0].id,
            "autores": [autores[1]],
        },
    ]
    libros = []
    for data in libros_data:
        autores_libro = data.pop("autores")
        libro, created = get_or_create(Libro, isbn=data["isbn"], defaults=data)
        if created:
            libro.autores = autores_libro
        libros.append(libro)

    # ---------- 3 Estados ----------
    estados_data = ["Disponible", "Prestado", "Dañado"]
    estados = []
    for nombre in estados_data:
        estado, _ = get_or_create(Estado, nombre=nombre)
        estados.append(estado)

    # ---------- 20 Ejemplares ----------
    for i in range(20):
        libro = libros[i % len(libros)]
        biblioteca = bibliotecas[i % len(bibliotecas)]
        estado = estados[i % len(estados)]
        creador = usuarios[i % len(usuarios)]
        numero_ejemplar = (i // len(libros)) + 1

        get_or_create(
            Ejemplar,
            libro_id=libro.id,
            numero_ejemplar=numero_ejemplar,
            defaults={
                "estado_id": estado.id,
                "biblioteca_id": biblioteca.id,
                "signatura": f"SIG-{libro.id:03d}-{i+1:03d}",
                "created_by": creador.id,
            },
        )

    db.session.commit()
    print("✅ Seeds ejecutados correctamente (idempotente).")