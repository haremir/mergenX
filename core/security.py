"""
Security utilities for API authentication.

Implements API Key authentication for multi-tenant access.
"""

import hashlib
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Tenant


# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using SHA256.
    
    Args:
        api_key: Raw API key string
        
    Returns:
        SHA256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


async def get_current_tenant(
    api_key: Optional[str] = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """
    Dependency to get the current tenant from API key.
    
    Validates the API key and returns the associated tenant.
    Raises 401 if the API key is invalid or tenant is inactive.
    
    Args:
        api_key: API key from X-API-Key header
        db: Database session
        
    Returns:
        Tenant object if authentication succeeds
        
    Raises:
        HTTPException: 401 Unauthorized if API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Hash the provided API key
    api_key_hash = hash_api_key(api_key)
    
    # Query for tenant with matching API key hash
    stmt = select(Tenant).where(
        Tenant.api_key_hash == api_key_hash,
        Tenant.is_active == True,
    )
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key or inactive tenant",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return tenant
