# Nexora — Backend

API en NestJS + TypeScript (ESM) con Prisma/PostgreSQL. Implementa la base de
identidad, organizaciones (multi-tenant) y autenticación descrita en el
[README del proyecto](../README.md).

## Qué hay implementado

- **Auth** (`src/auth`): registro, login, refresh con rotación y logout.
  Access token JWT de corta duración + refresh token opaco (hash SHA-256 en
  base de datos, nunca en claro).
- **Organizaciones** (`src/organizations`): creación de organización (el
  creador queda como `OWNER`), listado de "mis organizaciones", listado de
  miembros e invitación de un usuario existente con un rol.
- **RBAC multi-tenant** (`src/common/guards/membership.guard.ts`): toda ruta
  con `:organizationId` puede protegerse con `MembershipGuard` +
  `@Roles(...)` para exigir pertenencia a la organización y, opcionalmente,
  un rol mínimo.
- **Auditoría mínima** (`AuditLog` en el esquema): se registran altas de
  usuario, login y creación de organización.

Lo que falta (siguientes pasos naturales): datasets, carga de archivos,
dashboards — todo lo que cuelga de una organización ya puede apoyarse en
`MembershipGuard`.

## Requisitos

- Node.js 22+ (probado con 24).
- PostgreSQL accesible (local o remoto).

## Configuración

```bash
cp .env.example .env
```

Completa `DATABASE_URL` con las credenciales de tu Postgres local y genera un
`JWT_ACCESS_SECRET` propio:

```bash
node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"
```

## Levantar Postgres

Con Docker (una vez que tengas Docker Desktop + WSL2 activos, ver
`../docker-compose.yml`):

```bash
docker compose -f ../docker-compose.yml up -d postgres
```

O usa una instancia de PostgreSQL nativa ya instalada — solo ajusta
`DATABASE_URL`.

## Migraciones

```bash
npx prisma migrate dev --name init
```

Esto crea las tablas (`users`, `organizations`, `memberships`,
`refresh_tokens`, `audit_logs`) y regenera el cliente en
`src/generated/prisma` (ignorado en git, se regenera con `npx prisma
generate`).

## Correr el backend

```bash
npm install
npm run start:dev
```

Queda escuchando en `http://localhost:3000/api` (prefijo `/api` global).
Health check: `GET /api/health`.

## Pruebas

```bash
npm test        # unitarias (vitest)
npm run test:e2e   # requiere Postgres accesible vía DATABASE_URL
```

## Endpoints principales

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | — | Crea la cuenta y devuelve tokens. |
| POST | `/api/auth/login` | — | Devuelve access + refresh token. |
| POST | `/api/auth/refresh` | — | Rota el refresh token. |
| POST | `/api/auth/logout` | — | Revoca un refresh token. |
| GET | `/api/auth/me` | Bearer | Perfil del usuario autenticado. |
| POST | `/api/organizations` | Bearer | Crea una organización (creador = OWNER). |
| GET | `/api/organizations` | Bearer | Organizaciones del usuario autenticado. |
| GET | `/api/organizations/:organizationId` | Bearer + membresía | Detalle de la organización. |
| GET | `/api/organizations/:organizationId/members` | Bearer + membresía | Miembros de la organización. |
| POST | `/api/organizations/:organizationId/members` | Bearer + rol OWNER/ADMIN | Agrega un usuario existente como miembro. |
