import sys
import asyncio

# 1. WINDOWS YAMASI: Her şeyden önce, en tepede çalışmalı! Yoksa API kilitlenir.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.v1.endpoints.search import router as search_router
from apps.api.v1.endpoints.tenants import router as tenants_router

# 2. Uygulamayı Başlat
app = FastAPI(
    title="MergenX API",
    description="Yapay Zeka Destekli Akıllı Seyahat Arama Motoru",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api/v1/search", tags=["Search"])
app.include_router(tenants_router, prefix="/api/v1/tenants", tags=["Tenants"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ai_search": "active"}

# 3. Kendi Motorumuzu Kendimiz Başlatıyoruz
if __name__ == "__main__":
    import uvicorn
    # Çalıştırırken uvicorn komutu yerine direkt python dosyası olarak tetikleyeceğiz
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8000, reload=True)