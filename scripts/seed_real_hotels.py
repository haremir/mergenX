"""
Seed database with real hotel data from JSON file.

This script:
1. Reads hotel data from data/hotels.json
2. Filters out junk data (description < 20 characters)
3. Generates 768-dim embeddings using MergenEmbedder with e5-base model
4. Clears existing hotels for the tenant
5. Inserts valid hotels into the database

Usage:
    python scripts/seed_real_hotels.py

Windows Compatibility:
    Automatically uses WindowsSelectorEventLoopPolicy on Windows.
"""

import asyncio
import sys
import os
import json
from typing import List, Dict, Any
from uuid import UUID, uuid4
from decimal import Decimal

# Windows event loop fix - MUST be at the very top before any other imports
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from tqdm.asyncio import tqdm

from core.config import settings
from core.models import Hotel
from services.ai.embeddings import MergenEmbedder


# Tenant ID for the real hotels
TENANT_ID = "5b770cd3-b8c8-405e-91fb-64f553a0b0ab"


async def get_async_session() -> tuple:
    """
    Create async SQLAlchemy engine and session factory.
    
    Returns:
        Tuple of (engine, async_session_factory)
    """
    # Convert sync database URL to async
    database_url = str(settings.DATABASE_URL)
    if not database_url.startswith("postgresql+asyncpg://"):
        # Replace postgresql:// with postgresql+asyncpg://
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    return engine, async_session


def load_hotels_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load hotel data from JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of hotel dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_valid_hotels(hotels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out junk data - hotels with description < 20 characters.
    
    Args:
        hotels: List of hotel dictionaries
        
    Returns:
        Filtered list of valid hotels
    """
    valid_hotels = []
    for hotel in hotels:
        description = hotel.get('description', '')
        if description and len(description.strip()) >= 20:
            valid_hotels.append(hotel)
    
    return valid_hotels


def combine_hotel_text(hotel: Dict[str, Any]) -> str:
    """
    Combine hotel fields into a single string for embedding.
    
    Args:
        hotel: Hotel dictionary
        
    Returns:
        Combined text string
    """
    parts = []
    
    # Add hotel name
    if hotel.get('hotel_name'):
        parts.append(hotel['hotel_name'])
    
    # Add location info
    location = hotel.get('location', {})
    if location.get('city'):
        parts.append(location['city'])
    if location.get('district'):
        parts.append(location['district'])
    if location.get('area'):
        parts.append(location['area'])
    
    # Add concept
    if hotel.get('concept'):
        parts.append(hotel['concept'])
    
    # Add amenities
    amenities = hotel.get('amenities', [])
    if amenities:
        parts.extend(amenities)
    
    # Add description
    if hotel.get('description'):
        parts.append(hotel['description'])
    
    return " ".join(parts)


async def clear_existing_hotels(session: AsyncSession, tenant_id: str):
    """
    Clear all existing hotels for the given tenant.
    
    Args:
        session: AsyncSession for database
        tenant_id: Tenant UUID string
    """
    print(f"\n🗑️  Clearing existing hotels for tenant {tenant_id}...")
    
    stmt = delete(Hotel).where(Hotel.tenant_id == tenant_id)
    result = await session.execute(stmt)
    await session.commit()
    
    print(f"   ✅ Deleted {result.rowcount} existing hotels\n")


async def insert_hotels_batch(
    session: AsyncSession,
    hotels: List[Dict[str, Any]],
    embeddings: List[List[float]],
    tenant_id: str,
) -> int:
    """
    Insert a batch of hotels into the database.
    
    Args:
        session: AsyncSession for database
        hotels: List of hotel dictionaries
        embeddings: List of embedding vectors
        tenant_id: Tenant UUID string
        
    Returns:
        Number of hotels inserted
    """
    if not hotels:
        return 0
    
    hotel_objects = []
    for hotel_data, embedding in zip(hotels, embeddings):
        location = hotel_data.get('location', {})
        
        hotel = Hotel(
            id=uuid4(),
            tenant_id=tenant_id,
            name=hotel_data.get('hotel_name', 'Unknown Hotel'),
            city=location.get('city', 'Unknown'),
            district=location.get('district'),
            area=location.get('area'),
            concept=hotel_data.get('concept'),
            price=Decimal(str(hotel_data.get('price_per_night', 0))),
            currency='TRY',
            amenities=hotel_data.get('amenities', []),
            description=hotel_data.get('description'),
            embedding=embedding,
            stars=None,  # Not provided in JSON
            external_id=None,
            provider=None,
        )
        hotel_objects.append(hotel)
    
    session.add_all(hotel_objects)
    await session.commit()
    
    return len(hotel_objects)


async def seed_real_hotels(batch_size: int = 32):
    """
    Main function to seed the database with real hotel data.
    
    Args:
        batch_size: Number of hotels to process in each batch (default 32)
    """
    # Load JSON file
    json_path = os.path.join(os.getcwd(), 'data', 'hotels.json')
    print(f"\n📂 Loading hotels from {json_path}...")
    
    all_hotels = load_hotels_from_json(json_path)
    print(f"   ✅ Loaded {len(all_hotels)} hotels from JSON\n")
    
    # Filter valid hotels
    print("🔍 Filtering valid hotels (description >= 20 characters)...")
    valid_hotels = filter_valid_hotels(all_hotels)
    print(f"   ✅ {len(valid_hotels)} valid hotels found")
    print(f"   ❌ {len(all_hotels) - len(valid_hotels)} hotels filtered out\n")
    
    # Initialize embedder
    print("🤖 Initializing embedding model...")
    embedder = MergenEmbedder()
    print(f"   ✅ Loaded model: {embedder.model_name}")
    print(f"   ✅ Embedding dimension: {embedder.get_embedding_dimension()}\n")
    
    # Connect to database
    engine, async_session_factory = await get_async_session()
    
    try:
        async with async_session_factory() as session:
            # Clear existing hotels for this tenant
            await clear_existing_hotels(session, TENANT_ID)
            
            # Process hotels in batches
            print(f"📊 Processing {len(valid_hotels)} hotels in batches of {batch_size}...")
            print(f"   Tenant ID: {TENANT_ID}\n")
            
            total_inserted = 0
            
            for i in tqdm(
                range(0, len(valid_hotels), batch_size),
                desc="🔄 Seeding hotels",
                unit="batch",
            ):
                batch = valid_hotels[i : i + batch_size]
                
                # Generate embeddings for batch
                # E5 models require "passage: " prefix for documents
                texts = [combine_hotel_text(hotel) for hotel in batch]
                embeddings = await embedder.embed_texts(texts, prefix="passage")
                
                # Insert batch into database
                inserted = await insert_hotels_batch(
                    session, batch, embeddings, TENANT_ID
                )
                total_inserted += inserted
                
                tqdm.write(f"   Batch {i // batch_size + 1}: Inserted {inserted} hotels")
            
            print(f"\n✨ Successfully seeded database!")
            print(f"   Total hotels inserted: {total_inserted}")
            print(f"   Tenant ID: {TENANT_ID}")
            print(f"   Embedding model: {embedder.model_name}")
            print(f"   Embedding dimension: {embedder.get_embedding_dimension()}\n")
    
    finally:
        await engine.dispose()


def main():
    """CLI entry point."""
    print("=" * 70)
    print("🏨 REAL HOTEL DATA SEEDING SCRIPT")
    print("=" * 70)
    
    # Run async main function
    asyncio.run(seed_real_hotels(batch_size=32))
    
    print("=" * 70)
    print("✅ SEEDING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
