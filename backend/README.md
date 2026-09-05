# Nexora API

Backend de Nexora en **Python 3.12 + FastAPI**. Gestiona organizaciones y permisos multi-tenant, usa **Supabase Auth** como proveedor de identidad, PostgreSQL de Supabase mediante **SQLAlchemy/Alembic**, y Supabase Storage para los archivos privados de clientes.

## Arquitectura

- `app/api`: rutas HTTP y dependencias de autenticación/autorización.
- `app/models`: entidades SQLAlchemy y reglas de persistencia.
- `app/services`: adaptadores hacia Supabase.
- `app/workers`: tareas Celery para procesamiento fuera del request.
- `alembic`: migraciones versionadas de las tablas propias de Nexora.

Supabase Auth conserva contraseñas y sesiones. La tabla local `users` es solo un perfil sincronizado con `auth.users`; organizaciones, membresías, datasets y auditoría son datos propios de Nexora.

## Configuración

```bash
cp .env.example .env
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell
pip install -e ".[dev]"
```

Completa `DATABASE_URL`, `DATABASE_MIGRATION_URL` y las tres variables de Supabase en `.env`. No subas ese archivo. Crea en Supabase un bucket privado llamado `raw-data` (o cambia `SUPABASE_STORAGE_BUCKET`).

## Ejecutar

```bash
alembic upgrade head
fastapi dev app/main.py
```

La API queda en `http://localhost:8000/api`; la documentación interactiva está en `http://localhost:8000/docs`.

Para ejecutar infraestructura y servicios en contenedores:

```bash
docker compose up --build
```

## Endpoints iniciales

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/api/health` | Estado de la API. |
| POST | `/api/organizations` | Crea una organización; el creador queda como `OWNER`. |
| GET | `/api/organizations` | Lista las organizaciones del usuario autenticado. |
| GET | `/api/organizations/{id}/members` | Lista miembros de una organización autorizada. |
| POST | `/api/organizations/{id}/members` | Añade un usuario existente de Supabase Auth. |
| POST | `/api/organizations/{id}/datasets/uploads` | Genera URL temporal para cargar CSV/XLSX al bucket privado. |
| POST | `/api/organizations/{id}/datasets/{datasetId}/complete` | Encola el perfilado. |

Todas las rutas salvo health requieren `Authorization: Bearer <access_token>` emitido por Supabase Auth. El backend valida ese token antes de consultar datos de la organización.

## Pruebas y calidad

```bash
pytest
ruff check .
```
