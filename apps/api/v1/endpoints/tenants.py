"""
Tenant management endpoints.

Handles tenant creation and API key generation.
"""

import secrets
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Tenant
from core.security import hash_api_key


router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateTenantRequest(BaseModel):
    """Request model for creating a new tenant."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Tenant organization name",
        example="BiTur Travel Agency"
    )
    
    slug: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="URL-friendly identifier (must be unique)",
        example="bitur"
    )


class CreateTenantResponse(BaseModel):
    """Response model for tenant creation."""
    
    id: str = Field(description="Tenant UUID")
    name: str = Field(description="Tenant name")
    slug: str = Field(description="Tenant slug")
    api_key: str = Field(description="API key (ONLY shown once - save it securely!)")
    
    class Config:
        from_attributes = True


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/",
    response_model=CreateTenantResponse,
    status_code=201,
    summary="Create New Tenant",
    description="""
    Create a new tenant and generate an API key.
    
    **IMPORTANT:** The API key is only returned once during creation.
    Save it securely - it cannot be retrieved later.
    
    The API key must be passed in the `X-API-Key` header for all authenticated requests.
    """,
)
async def create_tenant(
    request: CreateTenantRequest,
    db: AsyncSession = Depends(get_db),
) -> CreateTenantResponse:
    """
    Create a new tenant with a generated API key.
    
    Args:
        request: CreateTenantRequest with name and slug
        db: Database session
        
    Returns:
        CreateTenantResponse with tenant details and API key
        
    Raises:
        HTTPException: 400 if slug already exists
    """
    # Check if slug already exists
    stmt = select(Tenant).where(Tenant.slug == request.slug)
    result = await db.execute(stmt)
    existing_tenant = result.scalar_one_or_none()
    
    if existing_tenant:
        raise HTTPException(
            status_code=400,
            detail=f"Tenant with slug '{request.slug}' already exists"
        )
    
    # Generate a secure API key
    raw_api_key = secrets.token_urlsafe(32)
    api_key_hash = hash_api_key(raw_api_key)
    
    # Create new tenant
    tenant = Tenant(
        id=uuid4(),
        name=request.name,
        slug=request.slug,
        api_key_hash=api_key_hash,
        is_active=True,
    )
    
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    
    # Return tenant info with raw API key (only time it's shown)
    return CreateTenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        slug=tenant.slug,
        api_key=raw_api_key,
    )
