from uuid import UUID

from pydantic import BaseModel, Field

from app.models import MembershipRole


class CreateOrganizationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    slug: str | None = Field(default=None, min_length=2, max_length=220, pattern=r"^[a-z0-9-]+$")


class InviteMemberRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: MembershipRole = MembershipRole.MEMBER


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    role: MembershipRole | None = None
