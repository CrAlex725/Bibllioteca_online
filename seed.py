from app import app
from extensions import db
from models import (
    Usuario, Rol, Biblioteca, Asignacion,
    Libro, Editorial, Autor, Estado, Ejemplar,
)

from sqlalchemy import func


def get_or_create(model, lookup, defaults=None):
    """Devuelve (instancia, creada), buscando con los campos de lookup."""
    instance = model.query.filter_by(**lookup).first()
    if instance:
        return instance, False

    instance = model(**{**lookup, **(defaults or {})})
    db.session.add(instance)
    db.session.flush()
    return instance, True


def get_or_create_ci(model, field, value, defaults=None):
    """Búsqueda sin distinguir mayúsculas/minúsculas para campos de texto."""
    column = getattr(model, field)
    instance = model.query.filter(func.lower(column) == value.lower()).first()
    if instance:
        return instance, False

    instance = model(**{field: value, **(defaults or {})})
    db.session.add(instance)
    db.session.flush()
    return instance, True


def ensure_user(*, rut, name, username, email, password, phone, address, is_admin=False):
    user, created = get_or_create(
        Usuario,
        {"username": username},
        {
            "rut": rut,
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "is_admin": is_admin,
            # Se establece abajo solo al crear; nunca se sobrescribe una
            # contraseña existente al volver a ejecutar el seed.
            "password_hash": "placeholder",
        },
    )
    if created:
        user.set_password(password)
    else:
        # Mantiene actualizados los permisos del usuario reservado de prueba,
        # pero no reemplaza su contraseña si ya fue cambiada manualmente.
        user.is_admin = is_admin
    return user


def run_seed():
    with app.app_context():
        try:
            # Roles: los endpoints comparan estos nombres en minúsculas.
            rol_bibliotecario, _ = get_or_create_ci(Rol, "name", "bibliotecario")
            rol_lector, _ = get_or_create_ci(Rol, "name", "lector")
            rol_asistente, _ = get_or_create_ci(Rol, "name", "asistente")
            # Varias rutas hacen búsquedas exactas como name="bibliotecario".
            # Normalizamos los nombres existentes para que esas búsquedas funcionen.
            rol_bibliotecario.name = "bibliotecario"
            rol_lector.name = "lector"
            rol_asistente.name = "asistente"

            admin = ensure_user(
                rut="11111111-1", name="Admin Demo",
                username="admin_demo", email="admin@ailibrary.local",
                password="AdminDemo123!", phone="+56911111111",
                address="Dirección de prueba 101", is_admin=True,
            )
            bibliotecario = ensure_user(
                rut="22222222-2", name="Bibliotecario Demo",
                username="biblio_demo", email="bibliotecario@ailibrary.local",
                password="BiblioDemo123!", phone="+56922222222",
                address="Dirección de prueba 202",
            )
            lector = ensure_user(
                rut="33333333-3", name="Lector Demo",
                username="lector_demo", email="lector@ailibrary.local",
                password="LectorDemo123!", phone="+56933333333",
                address="Dirección de prueba 303",
            )

            biblioteca, _ = get_or_create(
                Biblioteca,
                {"name": "Biblioteca Demo"},
                {
                    "address": "Av. de Prueba 123, Santiago",
                    "phone": "+56223456789",
                    "email": "biblioteca@ailibrary.local",
                    "is_public": True,
                    "is_active": True,
                    "created_by": admin.id,
                },
            )
            # Si la biblioteca ya existía, asegurar que esté utilizable.
            biblioteca.is_public = True
            biblioteca.is_active = True

            asignacion_biblio, _ = get_or_create(
                Asignacion,
                {"usuario_id": bibliotecario.id, "biblioteca_id": biblioteca.id},
                {"rol_id": rol_bibliotecario.id, "is_owner": True},
            )
            asignacion_biblio.rol_id = rol_bibliotecario.id
            asignacion_biblio.is_owner = True

            asignacion_lector, _ = get_or_create(
                Asignacion,
                {"usuario_id": lector.id, "biblioteca_id": biblioteca.id},
                {"rol_id": rol_lector.id, "is_owner": False},
            )
            asignacion_lector.rol_id = rol_lector.id
            asignacion_lector.is_owner = False

            editorial, _ = get_or_create_ci(Editorial, "nombre", "Editorial Demo")
            autor, _ = get_or_create_ci(Autor, "nombre", "Autora de Prueba")

            libro, _ = get_or_create(
                Libro,
                {"isbn": "9780306406157"},
                {
                    "title": "Libro de Prueba para AiLibrary",
                    "year_publication": 2024,
                    "clasificacion": "Tecnología",
                    "editorial_id": editorial.id,
                    "is_complete": True,
                },
            )
            if autor not in libro.autores:
                libro.autores.append(autor)

            # Estos nombres son usados literalmente por la lógica de préstamos
            # y por la baja lógica de ejemplares.
            estados = {}
            for nombre in ("Disponible", "Prestado", "Dañado", "De baja"):
                estado, _ = get_or_create_ci(Estado, "nombre", nombre)
                estados[nombre.lower()] = estado

            # Dos copias disponibles para poder probar varios préstamos.
            for numero in (1, 2):
                get_or_create(
                    Ejemplar,
                    {
                        "libro_id": libro.id,
                        "biblioteca_id": biblioteca.id,
                        "numero_ejemplar": numero,
                    },
                    {
                        "estado_id": estados["disponible"].id,
                        "signatura": f"TEC-DEMO-{numero:03d}",
                        "created_by": bibliotecario.id,
                    },
                )

            db.session.commit()
            print("Seed completado.")
            print("Usuarios de prueba:")
            print("  admin@ailibrary.local / AdminDemo123!")
            print("  bibliotecario@ailibrary.local / BiblioDemo123!")
            print("  lector@ailibrary.local / LectorDemo123!")
            print(f"Biblioteca: id={biblioteca.id}; libro ISBN={libro.isbn}")
            print("Ejecuta 'flask routes' para ver las rutas registradas.")
        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    run_seed()
