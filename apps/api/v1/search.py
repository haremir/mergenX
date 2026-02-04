"""
Arama servisleri - v1 API
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
async def search(query: str):
    """
    Arama yapılan sorgu için sonuçlar döndür
    """
    return {
        "query": query,
        "results": []
    }
