"""
Update hotel embeddings in PostgreSQL from text content.

This script:
1. Fetches all hotels from the database
2. Generates embeddings using MergenEmbedder for each hotel's
   combined text (name + concept + area + amenities)
3. Updates the embedding column in PostgreSQL
4. Tracks progress with tqdm

Usage:
    python scripts/update_embeddings.py [--limit N] [--tenant-id TENANT_ID]

Windows Compatibility:
    Automatically uses WindowsSelectorEventLoopPolicy on Windows.
"""

import asyncio
import sys
import os
from typing import Optional

# Windows event loop fix - MUST be at the very top before any other imports
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import argparse
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from tqdm.asyncio import tqdm

from core.config import settings
from core.models import Hotel
from services.ai.embeddings import MergenEmbedder


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


def combine_hotel_text(hotel: Hotel) -> str:
    """
    Combine all text fields of a hotel into a single string for embedding.
    
    Args:
        hotel: Hotel ORM object
        
    Returns:
        Combined text string
        
    Example:
        >>> text = combine_hotel_text(hotel)
        "Hotel Name Concept Area Downtown Pool Spa WiFi Restaurant"
    """
    parts = [hotel.name]
    
    if hotel.concept:
        parts.append(hotel.concept)
    
    if hotel.area:
        parts.append(hotel.area)
    
    if hotel.amenities:
        # amenities is a list, join them
        if isinstance(hotel.amenities, list):
            parts.extend(hotel.amenities)
        elif isinstance(hotel.amenities, dict):
            # If stored as dict, try to get values
            parts.extend(str(v) for v in hotel.amenities.values())
    
    return " ".join(parts)


async def update_embeddings_batch(
    session: AsyncSession,
    hotels: list,
    embedder: MergenEmbedder,
) -> int:
    """
    Update embeddings for a batch of hotels.
    
    Args:
        session: AsyncSession for database
        hotels: List of Hotel ORM objects
        embedder: MergenEmbedder instance
        
    Returns:
        Number of hotels updated
    """
    if not hotels:
        return 0
    
    # Generate embeddings for all hotels in batch
    texts = [combine_hotel_text(hotel) for hotel in hotels]
    embeddings = await embedder.embed_texts(texts)
    
    # Update hotels with embeddings
    for hotel, embedding in zip(hotels, embeddings):
        hotel.embedding = embedding
    
    # Commit all updates
    await session.commit()
    
    return len(hotels)


async def update_all_embeddings(
    limit: Optional[int] = None,
    tenant_id: Optional[str] = None,
    batch_size: int = 32,
):
    """
    Main function to update embeddings for all hotels.
    
    Args:
        limit: Optional limit on number of hotels to process
        tenant_id: Optional tenant ID to filter by
        batch_size: Number of hotels to process in each batch (default 32)
    """
    engine, async_session_factory = await get_async_session()
    
    try:
        async with async_session_factory() as session:
            # Build query
            query = select(Hotel)
            
            if tenant_id:
                query = query.where(Hotel.tenant_id == tenant_id)
            
            if limit:
                query = query.limit(limit)
            
            # Get total count for progress bar
            count_result = await session.execute(
                select(text("COUNT(*)")).select_from(Hotel)
            )
            total = count_result.scalar() or 0
            
            if tenant_id:
                count_query = select(text("COUNT(*)")).select_from(Hotel).where(
                    Hotel.tenant_id == tenant_id
                )
                count_result = await session.execute(count_query)
                total = count_result.scalar() or 0
            
            if limit:
                total = min(total, limit)
            
            print(f"\n📊 Processing {total} hotels...")
            print(f"   Batch size: {batch_size}")
            print(f"   Model: paraphrase-multilingual-MiniLM-L12-v2 (384-dim)\n")
            
            # Initialize embedder
            embedder = MergenEmbedder()
            print(f"✅ Loaded embedding model: {embedder.model_name}")
            print(f"   Embedding dimension: {embedder.get_embedding_dimension()}\n")
            
            # Fetch and process hotels matching the query
            result = await session.execute(query)
            all_hotels = result.scalars().all()
            
            # Process in batches with progress tracking
            updated_count = 0
            for i in tqdm(
                range(0, len(all_hotels), batch_size),
                desc="🔄 Updating embeddings",
                unit="batch",
                disable=False,
            ):
                batch = all_hotels[i : i + batch_size]
                batch_updated = await update_embeddings_batch(
                    session, batch, embedder
                )
                updated_count += batch_updated
                tqdm.write(
                    f"   Batch {i // batch_size + 1}: Updated {batch_updated} hotels"
                )
            
            print(f"\n✨ Embeddings updated successfully!")
            print(f"   Total updated: {updated_count}")
            print(f"   Completed at: {os.getcwd()}\n")
    
    finally:
        await engine.dispose()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Update hotel embeddings from text content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/update_embeddings.py
  python scripts/update_embeddings.py --limit 100
  python scripts/update_embeddings.py --tenant-id 550e8400-e29b-41d4-a716-446655440000
        """,
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of hotels to process",
    )
    parser.add_argument(
        "--tenant-id",
        type=str,
        default=None,
        help="Filter by tenant ID",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for processing (default: 32)",
    )
    
    args = parser.parse_args()
    
    # Run async main function
    asyncio.run(
        update_all_embeddings(
            limit=args.limit,
            tenant_id=args.tenant_id,
            batch_size=args.batch_size,
        )
    )


if __name__ == "__main__":
    main()
