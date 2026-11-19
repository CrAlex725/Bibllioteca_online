# Bibllioteca_online

API REST para gestión de biblioteca: libros, autores, ejemplares, usuarios y préstamos.

## Requisitos

- Docker Desktop (con Docker Compose v2)
- Git (para clonar)

## Instalación y ejecución

1. Clonar el repositorio
```bash
git clone https://github.com/CrAlex725/Bibllioteca_online
cd Bibllioteca_online
```

2. Levantar los contenedores
```bash
docker-compose up --build
```

3. En otra terminal, aplicar migraciones
```bash
docker-compose exec backend flask db upgrade
```

4. Cargar datos de prueba
```bash
docker-compose exec backend python seed.py
```

## Uso

La API está disponible en `http://localhost:5000`.

Documentación interactiva (Swagger): `http://localhost:5000/apidocs/`

Endpoints principales:

- `GET /health` — estado del servicio
- `GET /books` — listar libros
- `POST /auth/login` — obtener token JWT
- `GET /exemplars` — listar ejemplares (requiere JWT)

## Tests
Los tests corren en el entorno local (no dentro de Docker):

### 1. Crear el entorno virtual

```bash
python -m venv .venv
```

### 2. Activar el entorno

- Windows
```bash
.venv\Scripts\activate
```
- Linux/Mac
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo con el nombre `.env` en la raíz del proyecto con las siguientes líneas:
```env
DATABASE_URL=postgresql+psycopg2://<usuario_de_la_db>:<contraseña_de_la_db>@localhost:5432/<nombre_de_la_db>?client_encoding=utf8
JWT_SECRET_KEY=reemplazar_por_clave_de_al_menos_32_caracteres
```
Para generar `JWT_SECRET_KEY`, ejecuta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
``` 
y pega el resultado en el `.env`, reemplazando reemplazar_por_clave_de_al_menos_32_caracteres.

### 5. Correr los tests

```bash
pytest
```

## Usuarios de prueba

El script `seed.py` crea los siguientes usuarios:

|             Email             |          Password          |          Rol          |
|-------------------------------|----------------------------|-----------------------|
| admin@ailibrary.local         | AdminDemo123!              | admin                 |
| bibliotecario@ailibrary.local | BiblioDemo123!             | bibliotecario         |
| lector@ailibrary.local        | LectorDemo123!             | lector                |

Para endpoints protegidos, primero hacer login:

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ailibrary.local","password":"AdminDemo123!"}'
```

## Nota sobre seguridad

Las credenciales en `docker-compose.yml` son para desarrollo local.
En producción, deben moverse a variables de entorno o un gestor de secretos.

## Notas

- **Puerto 5432 ocupado**: si tienes PostgreSQL local corriendo, el contenedor no puede usar ese puerto. Páralo antes o cambia el mapeo en `docker-compose.yml` a `"5433:5432"`.
- **Persistencia de datos**: `docker-compose down` no borra los datos. Para borrarlos, usa `docker-compose down -v` (⚠️ elimina el volumen y todos los datos).
- **Migraciones**: hay que correr `flask db upgrade` después del primer `up`. Si no, la app arranca pero falla en cualquier endpoint que toque la DB.

## Detener

```bash
docker-compose down
```
