import os
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

# .env dosyasındaki veritabanı adresini alıyoruz, yoksa standart olanı kullanıyoruz.
DB_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/mergenx")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        # 1. Ajansın adını 'Bitur Demo' olarak güncelliyoruz
        await conn.execute(text("UPDATE tenants SET name = 'Bitur Demo' WHERE slug = 'bitur'"))
        
        # 2. Bize lazım olan o gerçek UUID'yi çekiyoruz
        result = await conn.execute(text("SELECT id FROM tenants WHERE slug = 'bitur'"))
        tenant_id = result.scalar()
        
        print("\n" + "="*60)
        print("✅ Ajans Adı 'Bitur Demo' olarak güncellendi.")
        print(f"🔑 GERÇEK TENANT ID (BUNU KOPYALA): {tenant_id}")
        print("="*60 + "\n")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())