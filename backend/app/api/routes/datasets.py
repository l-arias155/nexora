from pathlib import PurePath
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, require_membership
from app.core.config import get_settings
from app.models import AuditLog, Dataset, DatasetStatus, MembershipRole
from app.schemas.datasets import CreateUploadRequest, DatasetResponse, UploadResponse
from app.services.supabase import get_supabase_admin_client
from app.workers.tasks import profile_dataset

router = APIRouter()


@router.post("/{organization_id}/datasets/uploads", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def create_upload_url(organization_id: UUID, payload: CreateUploadRequest, user: CurrentUser, session: DbSession):
    await require_membership(organization_id, user, session, {MembershipRole.OWNER, MembershipRole.ADMIN, MembershipRole.MEMBER})
    safe_name = PurePath(payload.file_name).name
    if safe_name != payload.file_name:
        raise HTTPException(status_code=422, detail="El nombre del archivo no es válido.")
    dataset = Dataset(
        organization_id=organization_id,
        uploaded_by_user_id=user.id,
        name=payload.name,
        content_type=payload.content_type,
        source_path=f"{organization_id}/sources/{uuid4()}-{safe_name}",
    )
    session.add(dataset)
    await session.flush()
    signed_upload = get_supabase_admin_client().storage.from_(get_settings().supabase_storage_bucket).create_signed_upload_url(dataset.source_path)
    session.add(AuditLog(action="dataset.upload_requested", target_type="Dataset", target_id=str(dataset.id), actor_user_id=user.id, organization_id=organization_id))
    await session.commit()
    return UploadResponse(dataset_id=dataset.id, path=dataset.source_path, signed_url=signed_upload.signed_url, token=signed_upload.token)


@router.post("/{organization_id}/datasets/{dataset_id}/complete", response_model=DatasetResponse)
async def complete_upload(organization_id: UUID, dataset_id: UUID, user: CurrentUser, session: DbSession):
    await require_membership(organization_id, user, session)
    dataset = await session.scalar(select(Dataset).where(Dataset.id == dataset_id, Dataset.organization_id == organization_id))
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset no encontrado.")
    if dataset.status is DatasetStatus.PENDING_UPLOAD:
        dataset.status = DatasetStatus.QUEUED
        session.add(AuditLog(action="dataset.profile_queued", target_type="Dataset", target_id=str(dataset.id), actor_user_id=user.id, organization_id=organization_id))
        await session.commit()
        profile_dataset.delay(str(dataset.id))
    return DatasetResponse(id=dataset.id, name=dataset.name, status=dataset.status.value, profile=dataset.profile)


@router.get("/{organization_id}/datasets", response_model=list[DatasetResponse])
async def list_datasets(organization_id: UUID, user: CurrentUser, session: DbSession):
    await require_membership(organization_id, user, session)
    datasets = await session.scalars(select(Dataset).where(Dataset.organization_id == organization_id).order_by(Dataset.created_at.desc()))
    return [DatasetResponse(id=item.id, name=item.name, status=item.status.value, profile=item.profile) for item in datasets]
