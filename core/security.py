"""
API Key ve Multi-tenant kimlik doğrulaması
"""
from fastapi import HTTPException, Header
from typing import Optional


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """API anahtarını doğrula"""
    if not x_api_key:
        raise HTTPException(status_code=403, detail="API anahtarı gerekli")
    
    # Veritabanında doğrulamayı gerçekle
    return True


async def verify_tenant_access(tenant_id: str, x_api_key: Optional[str] = Header(None)):
    """Kiracı erişimini doğrula"""
    await verify_api_key(x_api_key)
    
    # Tenant erişimini kontrol et
    return True
