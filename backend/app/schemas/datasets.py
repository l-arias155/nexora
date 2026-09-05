from uuid import UUID

from pydantic import BaseModel, Field


class CreateUploadRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(pattern=r"^(text/csv|application/vnd\.openxmlformats-officedocument\.spreadsheetml\.sheet)$")


class UploadResponse(BaseModel):
    dataset_id: UUID
    path: str
    signed_url: str
    token: str


class DatasetResponse(BaseModel):
    id: UUID
    name: str
    status: str
    profile: dict | None
