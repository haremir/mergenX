"""
FastAPI Merkezi Giriş Noktası
"""
from fastapi import FastAPI
from fastapi.middleware import Middleware
from contextlib import asynccontextmanager

# Uygulamayı başlat
app = FastAPI(
    title="MergenX API",
    description="Merkezi Arama ve Ajans Yönetim Platformu",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
