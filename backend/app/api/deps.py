from typing import Annotated
from uuid import UUID

import anyio
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models import Membership, MembershipRole, User
from app.services.supabase import get_supabase_public_client

bearer_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: DbSession,
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta el token de acceso.")

    try:
        result = await anyio.to_thread.run_sync(
            get_supabase_public_client().auth.get_user, credentials.credentials
        )
        auth_user = result.user
        if auth_user is None or auth_user.email is None:
            raise ValueError("Token sin usuario válido")
        user_id = UUID(auth_user.id)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.") from error

    user = await session.get(User, user_id)
    if user is None:
        user = User(id=user_id, email=auth_user.email, name=auth_user.user_metadata.get("name"))
        session.add(user)
    else:
        user.email = auth_user.email
        user.name = auth_user.user_metadata.get("name", user.name)
    await session.commit()
    await session.refresh(user)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_membership(
    organization_id: UUID,
    user: CurrentUser,
    session: DbSession,
    allowed_roles: set[MembershipRole] | None = None,
) -> Membership:
    membership = await session.scalar(
        select(Membership).where(
            Membership.user_id == user.id, Membership.organization_id == organization_id
        )
    )
    if membership is None or (allowed_roles and membership.role not in allowed_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta organización.")
    return membership
