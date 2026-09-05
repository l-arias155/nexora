import re
import unicodedata
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession, require_membership
from app.models import AuditLog, Membership, MembershipRole, Organization, User
from app.schemas.organizations import CreateOrganizationRequest, InviteMemberRequest, OrganizationResponse

router = APIRouter()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    ascii_value = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return re.sub(r"(^-+|-+$)", "", re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()))


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(payload: CreateOrganizationRequest, user: CurrentUser, session: DbSession):
    base_slug = payload.slug or slugify(payload.name)
    if not base_slug:
        raise HTTPException(status_code=422, detail="El nombre no produce un slug válido.")
    slug = base_slug
    suffix = 1
    while await session.scalar(select(Organization.id).where(Organization.slug == slug)):
        suffix += 1
        slug = f"{base_slug}-{suffix}"

    organization = Organization(name=payload.name, slug=slug)
    session.add(organization)
    await session.flush()
    session.add(Membership(user_id=user.id, organization_id=organization.id, role=MembershipRole.OWNER))
    session.add(
        AuditLog(
            action="organization.created", target_type="Organization", target_id=str(organization.id),
            actor_user_id=user.id, organization_id=organization.id,
        )
    )
    await session.commit()
    return OrganizationResponse(id=organization.id, name=organization.name, slug=organization.slug, role=MembershipRole.OWNER)


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(user: CurrentUser, session: DbSession):
    rows = await session.execute(
        select(Organization, Membership.role)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Membership.user_id == user.id)
        .order_by(Organization.created_at)
    )
    return [OrganizationResponse(id=org.id, name=org.name, slug=org.slug, role=role) for org, role in rows]


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(organization_id: UUID, user: CurrentUser, session: DbSession):
    membership = await require_membership(organization_id, user, session)
    organization = await session.get(Organization, membership.organization_id)
    return OrganizationResponse(id=organization.id, name=organization.name, slug=organization.slug, role=membership.role)


@router.get("/{organization_id}/members")
async def list_members(organization_id: UUID, user: CurrentUser, session: DbSession):
    await require_membership(organization_id, user, session)
    rows = await session.execute(
        select(User.id, User.email, User.name, Membership.role)
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.organization_id == organization_id)
        .order_by(Membership.created_at)
    )
    return [{"id": str(id_), "email": email, "name": name, "role": role} for id_, email, name, role in rows]


@router.post("/{organization_id}/members", status_code=status.HTTP_201_CREATED)
async def invite_member(organization_id: UUID, payload: InviteMemberRequest, user: CurrentUser, session: DbSession):
    await require_membership(organization_id, user, session, {MembershipRole.OWNER, MembershipRole.ADMIN})
    member = await session.scalar(select(User).where(User.email == payload.email))
    if member is None:
        raise HTTPException(status_code=404, detail="El usuario debe registrarse primero en Supabase Auth.")
    membership = Membership(user_id=member.id, organization_id=organization_id, role=payload.role)
    session.add(membership)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(status_code=409, detail="El usuario ya pertenece a la organización.") from error
    return {"id": str(membership.id), "role": membership.role}
