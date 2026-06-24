"""Client configuration API routes — CRUD from database."""

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from agent.api.schemas import (
    ClientArtifactListResponse,
    ClientArtifactResponse,
    ClientDetailResponse,
    ClientListResponse,
    ClientResourceResponse,
    ClientSummary,
    CreateClientRequest,
    CreateResourceRequest,
    UpdateClientRequest,
    UpdateResourceRequest,
)
from agent.marketing.client_service import ClientService
from agent.persistence.client_repository import ClientRepository
from agent.persistence.database import get_session
from agent.persistence.models import ClientResource
from agent.persistence.repository import ExecutionRepository

router = APIRouter(prefix="/agent/clients", tags=["clients"])


def _resource_response(resource: ClientResource) -> ClientResourceResponse:
    return ClientResourceResponse(
        id=resource.id,
        client_id=resource.client_id,
        resource_type=resource.resource_type,  # type: ignore[arg-type]
        category=resource.category,
        title=resource.title,
        content=resource.content,
        url=resource.url,
        extracted_text=resource.extracted_text,
        scraped_at=resource.scraped_at,
        metadata=resource.metadata_,
        sort_order=resource.sort_order,
        created_at=resource.created_at,
        updated_at=resource.updated_at,
    )


def _detail_response(client, resources: list[ClientResource]) -> ClientDetailResponse:
    return ClientDetailResponse(
        id=client.id,
        slug=client.slug,
        name=client.name,
        product=client.product,
        description=client.description,
        profile=client.profile,
        is_active=client.is_active,
        resources=[_resource_response(r) for r in resources],
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


async def _get_service(session: AsyncSession = Depends(get_session)) -> ClientService:
    return ClientService(session)


async def _resolve_client_id(service: ClientService, client_ref: str) -> uuid.UUID:
    resolved = await service.resolve_client_id(client_ref)
    if resolved is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return resolved


@router.get("", response_model=ClientListResponse)
async def list_available_clients(
    service: ClientService = Depends(_get_service),
) -> ClientListResponse:
    clients = await service.list_clients()
    summaries: list[ClientSummary] = []
    for client in clients:
        count = await service.repo.count_resources(client.id)
        summaries.append(
            ClientSummary(
                id=str(client.id),
                slug=client.slug,
                name=client.name,
                product=client.product,
                description=(client.description or "").strip(),
                resource_count=count,
                is_active=client.is_active,
            )
        )
    return ClientListResponse(clients=summaries)


@router.post("", response_model=ClientDetailResponse, status_code=201)
async def create_client(
    body: CreateClientRequest,
    service: ClientService = Depends(_get_service),
) -> ClientDetailResponse:
    existing = await service.repo.get_client_by_slug(body.slug or body.name)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Client slug already exists")
    client = await service.create_client(
        name=body.name,
        product=body.product,
        description=body.description,
        slug=body.slug,
        profile=body.profile,
    )
    return _detail_response(client, [])


@router.get("/{client_id}", response_model=ClientDetailResponse)
async def get_client_detail(
    client_id: str,
    service: ClientService = Depends(_get_service),
) -> ClientDetailResponse:
    resolved = await _resolve_client_id(service, client_id)
    client = await service.get_client(resolved)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    resources = await service.repo.list_resources(resolved)
    return _detail_response(client, resources)


@router.patch("/{client_id}", response_model=ClientDetailResponse)
async def update_client(
    client_id: str,
    body: UpdateClientRequest,
    service: ClientService = Depends(_get_service),
) -> ClientDetailResponse:
    resolved = await _resolve_client_id(service, client_id)
    client = await service.update_client(
        resolved,
        slug=body.slug,
        name=body.name,
        product=body.product,
        description=body.description,
        profile=body.profile,
        is_active=body.is_active,
    )
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    resources = await service.repo.list_resources(resolved)
    return _detail_response(client, resources)


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: str,
    service: ClientService = Depends(_get_service),
) -> None:
    resolved = await _resolve_client_id(service, client_id)
    deleted = await service.delete_client(resolved)
    if not deleted:
        raise HTTPException(status_code=404, detail="Client not found")


@router.post("/{client_id}/resources", response_model=ClientResourceResponse, status_code=201)
async def create_resource(
    client_id: str,
    body: CreateResourceRequest,
    service: ClientService = Depends(_get_service),
) -> ClientResourceResponse:
    resolved = await _resolve_client_id(service, client_id)
    resource = await service.create_resource_json(
        resolved,
        resource_type=body.resource_type,
        title=body.title,
        category=body.category,
        content=body.content,
        url=body.url,
        metadata=body.metadata,
    )
    if resource is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return _resource_response(resource)


@router.post("/{client_id}/resources/upload", response_model=ClientResourceResponse, status_code=201)
async def upload_resource_file(
    client_id: str,
    title: str = Form(...),
    category: str | None = Form(default=None),
    file: UploadFile = File(...),
    service: ClientService = Depends(_get_service),
) -> ClientResourceResponse:
    resolved = await _resolve_client_id(service, client_id)
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    content = await file.read()
    resource = await service.create_resource_file(
        resolved,
        title=title,
        filename=file.filename,
        content=content,
        category=category,
    )
    if resource is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return _resource_response(resource)


@router.patch("/{client_id}/resources/{resource_id}", response_model=ClientResourceResponse)
async def update_resource(
    client_id: str,
    resource_id: uuid.UUID,
    body: UpdateResourceRequest,
    service: ClientService = Depends(_get_service),
) -> ClientResourceResponse:
    await _resolve_client_id(service, client_id)
    resource = await service.update_resource(
        resource_id,
        title=body.title,
        category=body.category,
        content=body.content,
        url=body.url,
        metadata=body.metadata,
        sort_order=body.sort_order,
    )
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return _resource_response(resource)


@router.delete("/{client_id}/resources/{resource_id}", status_code=204)
async def delete_resource(
    client_id: str,
    resource_id: uuid.UUID,
    service: ClientService = Depends(_get_service),
) -> None:
    await _resolve_client_id(service, client_id)
    deleted = await service.delete_resource(resource_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resource not found")


@router.post("/{client_id}/resources/{resource_id}/refresh", response_model=ClientResourceResponse)
async def refresh_link_resource(
    client_id: str,
    resource_id: uuid.UUID,
    service: ClientService = Depends(_get_service),
) -> ClientResourceResponse:
    await _resolve_client_id(service, client_id)
    resource = await service.repo.get_resource(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    updated = await service.scrape_link_resource(resource)
    if updated is None:
        raise HTTPException(status_code=400, detail="Failed to refresh link")
    return _resource_response(updated)


@router.get("/{client_id}/artifacts", response_model=ClientArtifactListResponse)
async def list_client_artifacts(
    client_id: str,
    artifact_type: str | None = None,
    session: AsyncSession = Depends(get_session),
    service: ClientService = Depends(_get_service),
) -> ClientArtifactListResponse:
    resolved = await _resolve_client_id(service, client_id)
    client_id_str = str(resolved)

    repo = ExecutionRepository(session)
    artifacts = await repo.list_client_artifacts(client_id_str, artifact_type=artifact_type)
    return ClientArtifactListResponse(
        client_id=client_id_str,
        artifacts=[
            ClientArtifactResponse(
                id=artifact.id,
                client_id=artifact.client_id,
                artifact_type=artifact.artifact_type,
                title=artifact.title,
                content=artifact.content,
                version=artifact.version,
                created_at=artifact.created_at,
            )
            for artifact in artifacts
        ],
    )
