# Nexora

Nexora es un SaaS B2B para transformar datos crudos compartidos por clientes en análisis claros, dashboards interactivos y hallazgos accionables. Su objetivo es reducir el tiempo entre recibir información dispersa y tomar decisiones respaldadas por datos.

> Estado: fase de definición y construcción inicial.

## Problema

Los equipos suelen recibir archivos y fuentes de datos con formatos, estructuras y niveles de calidad distintos. Convertirlos en información útil requiere procesos manuales, repetitivos y difíciles de escalar. Nexora centraliza ese flujo: ingestión segura, validación, modelado y visualización.

## Objetivos del producto

- Permitir a cada cliente cargar y gestionar sus fuentes de datos de forma segura.
- Detectar estructura, calidad y posibles inconsistencias en los datos importados.
- Convertir datos preparados en métricas, filtros y dashboards reutilizables.
- Facilitar la creación de visualizaciones sin requerir conocimientos técnicos avanzados.
- Mantener aislamiento estricto entre organizaciones, trazabilidad y control de acceso.

## Alcance inicial (MVP)

1. Registro e inicio de sesión de usuarios.
2. Organizaciones y espacios de trabajo aislados por cliente.
3. Carga de archivos tabulares (CSV y XLSX).
4. Perfilado básico: columnas, tipos inferidos, valores nulos y filas duplicadas.
5. Dataset preparado a partir de una carga validada.
6. Creación de dashboards con visualizaciones y filtros básicos.
7. Compartición de dashboards dentro de la organización, según permisos.

Las integraciones con fuentes externas, transformaciones avanzadas, consultas en lenguaje natural y alertas automáticas quedan fuera del MVP, pero la arquitectura debe permitir incorporarlas posteriormente.

## Arquitectura propuesta

Nexora seguirá una arquitectura modular orientada a servicios, con límites claros entre la experiencia de usuario, la API transaccional y el procesamiento de datos.

```text
┌───────────────────────────────────────────────────────────────────┐
│                         Aplicación web                             │
│  Autenticación · Carga de datos · Exploración · Constructor BI    │
└───────────────────────────────┬───────────────────────────────────┘
                                │ HTTPS / API
┌───────────────────────────────▼───────────────────────────────────┐
│                       Backend de aplicación                        │
│ Auth · Organizaciones · RBAC · Datasets · Dashboards · Auditoría  │
└───────────────┬─────────────────────────┬─────────────────────────┘
                │                         │
     ┌──────────▼──────────┐   ┌──────────▼────────────────────────┐
     │ Base transaccional  │   │ Cola y workers de procesamiento   │
     │ usuarios, permisos, │   │ importación · perfilado ·        │
     │ metadatos y layouts │   │ validación · transformaciones     │
     └─────────────────────┘   └──────────┬────────────────────────┘
                                           │
                 ┌─────────────────────────▼──────────────────────┐
                 │ Almacenamiento de objetos y capa analítica      │
                 │ archivos originales · datos preparados · cache  │
                 └────────────────────────────────────────────────┘
```

### Componentes y responsabilidades

| Componente | Responsabilidad |
| --- | --- |
| Aplicación web | Interfaz de carga, exploración, construcción y consumo de dashboards. |
| API de aplicación | Gestiona identidad, organizaciones, permisos, metadatos y operaciones del producto. |
| Workers de datos | Ejecutan procesos asíncronos y repetibles de importación, validación, perfilado y transformación. |
| Base transaccional | Conserva entidades de negocio, configuraciones, permisos, auditoría y metadatos; no almacena archivos pesados. |
| Almacenamiento de objetos | Guarda archivos fuente y artefactos generados con acceso privado y temporal. |
| Capa analítica | Sirve consultas agregadas para dashboards sobre datos preparados y gobernados. |

## Flujo de datos

1. Un usuario autorizado carga un archivo en el espacio de trabajo de su organización.
2. El backend registra los metadatos y envía el procesamiento a una cola.
3. Un worker valida el archivo, infiere el esquema y genera un reporte de calidad.
4. Tras la aprobación o resolución de incidencias, se crea una versión preparada del dataset.
5. Los dashboards consultan únicamente datasets preparados y respetan los permisos de la organización.
6. Cada carga, transformación y publicación conserva su origen y versión para auditoría.

## Principios técnicos y de seguridad

- **Aislamiento por tenant:** todas las entidades y consultas deben estar acotadas por organización.
- **Mínimo privilegio:** acceso basado en roles y permisos explícitos; nunca confiar solo en controles de la interfaz.
- **Protección de datos:** cifrado en tránsito y en reposo, enlaces de descarga temporales y secretos fuera del repositorio.
- **Procesamiento asíncrono:** las cargas y transformaciones no deben bloquear las solicitudes de usuario.
- **Trazabilidad:** registrar autor, tiempo, fuente, versión y resultado de cada operación relevante.
- **Versionado de datos:** preservar el archivo original y versionar datasets y transformaciones derivadas.
- **Observabilidad:** logs estructurados, métricas y alertas para errores de importación y rendimiento de consultas.
- **Diseño evolutivo:** mantener contratos de API y módulos desacoplados para adoptar nuevos conectores o motores analíticos.

## Modelo de dominio inicial

```text
Organización
  └── Miembros (rol)
       └── Espacios de trabajo
            └── Fuentes de datos
                 └── Versiones de dataset
                      └── Dashboards
                           └── Visualizaciones
```

Entidades transversales: auditoría, permisos, tareas de procesamiento y configuraciones de transformación.

## Stack tecnológico

> Propuesta inicial, sujeta a revisión conforme avance el diseño técnico.

| Capa | Tecnología | Justificación |
| --- | --- | --- |
| Frontend | Next.js (React) + TypeScript | SSR/SSG para carga inicial rápida y dashboards interactivos. |
| Backend / API | Python 3.12 + FastAPI | API tipada, documentación OpenAPI automática y ecosistema natural para procesamiento de datos. |
| Persistencia | Supabase Postgres + SQLAlchemy + Alembic | PostgreSQL gestionado, modelo de dominio explícito y migraciones versionadas. |
| Cola y workers de procesamiento | Redis + Celery + Polars | Perfilado y transformación asíncrona de archivos sin bloquear solicitudes HTTP. |
| Identidad y archivos | Supabase Auth + Supabase Storage | Sesiones gestionadas y objetos privados con URLs firmadas desde el backend. |
| Capa analítica | PostgreSQL (vistas materializadas) en el MVP; evaluar ClickHouse o DuckDB al escalar | Mantiene el MVP simple sin bloquear una futura migración de solo la capa analítica. |
| Autenticación | Supabase Auth + validación Bearer en FastAPI | Un único proveedor de identidad; el backend conserva los permisos multi-tenant. |
| Infraestructura y entornos | Docker y Docker Compose para desarrollo; despliegue en contenedores | Consistencia entre entornos y portabilidad hacia el proveedor cloud que se elija. |

## Convenciones de desarrollo

- Usar ramas cortas con el prefijo `codex/` y mensajes de commit imperativos y descriptivos.
- Proteger `main` mediante revisiones y validaciones automatizadas antes de fusionar cambios.
- Documentar decisiones de arquitectura que afecten a varios módulos mediante ADRs en `docs/adr/`.
- Añadir pruebas unitarias para lógica de dominio y pruebas de integración para API, permisos y flujos de datos.
- Evitar datos reales de clientes en el repositorio, pruebas, logs y capturas de pantalla.
- Mantener variables de entorno documentadas en un archivo de ejemplo sin secretos.

## Próximos pasos

1. Configurar Supabase Auth, el bucket privado `raw-data` y las variables de entorno del backend.
2. Aplicar la primera migración de Alembic a Supabase Postgres.
3. Conectar el frontend a Supabase Auth y a las rutas protegidas de FastAPI.
4. Completar el worker de perfilado CSV/XLSX con Polars cuando la carga finalice.
5. Crear el primer dashboard basado en un dataset preparado.

## Licencia

Pendiente de definición.
