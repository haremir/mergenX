"""
Ajans yönetim servisleri - v1 API
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/")
async def list_tenants():
    """Tüm ajansları listele"""
    return {"tenants": []}


@router.post("/")
async def create_tenant(name: str):
    """Yeni ajans oluştur"""
    return {
        "id": 1,
        "name": name,
        "created": True
    }
