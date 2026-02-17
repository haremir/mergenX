"""
Database Seeding Script for MergenX Platform
==============================================

Seeds the PostgreSQL database with legacy JSON data from:
- data/hotels.json
- data/flights.json  
- data/transfers.json

Features:
- Async SQLAlchemy operations
- Progress tracking with tqdm
- Deduplication by external_id
- Mock vector embeddings (384-dimensional)
- PostGIS geospatial support
- Robust error handling

Usage:
    uv run python scripts/seed_db.py
"""
import asyncio
import json
import random
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import AsyncSessionLocal
from core.models import Flight, Hotel, Tenant, Transfer


# ============================================================================
# Configuration
# ============================================================================
DATA_DIR = project_root / "data"
HOTELS_FILE = DATA_DIR / "hotels.json"
FLIGHTS_FILE = DATA_DIR / "flights.json"
TRANSFERS_FILE = DATA_DIR / "transfers.json"

TENANT_SLUG = "bitur"
TENANT_NAME = "Bitur Travel Agency"

EMBEDDING_DIMENSIONS = 384  # For mock embeddings


# ============================================================================
# Utility Functions
# ============================================================================

def generate_mock_embedding(dim: int = EMBEDDING_DIMENSIONS) -> List[float]:
    """
    Generate a random vector embedding for testing.
    
    In production, this would be replaced with actual AI model embeddings
    (e.g., sentence-transformers, OpenAI embeddings).
    
    Args:
        dim: Embedding dimensions (default: 384)
        
    Returns:
        List of random floats normalized to unit vector
    """
    # Generate random values between -1 and 1
    vec = [random.uniform(-1.0, 1.0) for _ in range(dim)]
    
    # Normalize to unit vector (common practice for embeddings)
    magnitude = sum(x ** 2 for x in vec) ** 0.5
    if magnitude > 0:
        vec = [x / magnitude for x in vec]
    
    return vec


def create_point_wkt(lon: float, lat: float, srid: int = 4326) -> WKTElement:
    """
    Create a PostGIS POINT from longitude and latitude.
    
    Args:
        lon: Longitude (x-coordinate)
        lat: Latitude (y-coordinate)
        srid: Spatial Reference System Identifier (default: 4326 for WGS84)
        
    Returns:
        WKTElement for insertion into PostGIS Geography column
    """
    return WKTElement(f'POINT({lon} {lat})', srid=srid)


def parse_iso_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Safely parse ISO format datetime string.
    
    Args:
        date_str: ISO datetime string (e.g., "2026-06-15T08:30:00")
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        # Try parsing with fromisoformat
        return datetime.fromisoformat(date_str)
    except (ValueError, AttributeError):
        # Fallback to manual parsing
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None


# ============================================================================
# Database Operations
# ============================================================================

async def get_or_create_tenant(session, slug: str, name: str) -> Tenant:
    """
    Get existing tenant or create a new one.
    
    Args:
        session: Async database session
        slug: Tenant slug (unique identifier)
        name: Tenant display name
        
    Returns:
        Tenant instance
    """
    # Check if tenant exists
    result = await session.execute(
        select(Tenant).where(Tenant.slug == slug)
    )
    tenant = result.scalar_one_or_none()
    
    if tenant:
        print(f"✓ Found existing tenant: {tenant.name} (slug={tenant.slug})")
        return tenant
    
    # Create new tenant with dummy API key
    tenant = Tenant(
        name=name,
        slug=slug,
        api_key_hash="dummy_hash_for_seeding",  # Replace with real hash in production
        is_active=True,
        settings={"seeded": True, "seeded_at": datetime.utcnow().isoformat()}
    )
    
    session.add(tenant)
    await session.flush()  # Get the ID without committing
    
    print(f"✓ Created new tenant: {tenant.name} (slug={tenant.slug})")
    return tenant


async def seed_hotels(session, tenant_id: str, file_path: Path) -> int:
    """
    Seed hotels from JSON file.
    
    Args:
        session: Async database session
        tenant_id: UUID of the tenant
        file_path: Path to hotels.json
        
    Returns:
        Number of hotels successfully inserted
    """
    if not file_path.exists():
        print(f"⚠ Warning: {file_path} not found. Skipping hotels.")
        return 0
    
    # Load JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        hotels_data = json.load(f)
    
    inserted_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"\n📍 Processing {len(hotels_data)} hotels...")
    
    for idx, hotel_json in enumerate(tqdm(hotels_data, desc="Hotels", unit="hotel")):
        try:
            # Generate external_id from hotel name if not present
            external_id = hotel_json.get("external_id") or f"hotel_{idx}_{hotel_json.get('hotel_name', 'unknown').lower().replace(' ', '_')}"
            
            # Check for duplicates
            result = await session.execute(
                select(Hotel).where(
                    Hotel.tenant_id == tenant_id,
                    Hotel.external_id == external_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                skipped_count += 1
                continue
            
            # Extract location data
            location_data = hotel_json.get("location", {})
            city = location_data.get("city", "").lower()
            district = location_data.get("district", "").lower() if location_data.get("district") else None
            area = location_data.get("area", "").lower() if location_data.get("area") else None
            
            # Generate mock embedding
            embedding = generate_mock_embedding()
            
            # Create hotel instance
            hotel = Hotel(
                tenant_id=tenant_id,
                name=hotel_json.get("hotel_name", "Unknown Hotel"),
                city=city,
                district=district,
                area=area,
                location=None,  # No lat/lon in source data - set to None
                concept=hotel_json.get("concept"),
                stars=hotel_json.get("stars"),  # May be None
                price=Decimal(str(hotel_json.get("price_per_night", 0))),
                currency="TRY",
                description=hotel_json.get("description"),
                amenities=hotel_json.get("amenities", []),
                embedding=embedding,
                external_id=external_id,
                provider="legacy_import",
                raw_data=hotel_json  # Store original data
            )
            
            session.add(hotel)
            inserted_count += 1
            
            # Commit in batches to avoid memory issues
            if inserted_count % 100 == 0:
                await session.flush()
        
        except Exception as e:
            error_count += 1
            print(f"\n⚠ Error processing hotel {idx}: {str(e)}")
            continue
    
    # Final commit
    await session.flush()
    
    print(f"✓ Hotels: {inserted_count} inserted, {skipped_count} skipped, {error_count} errors")
    return inserted_count


async def seed_flights(session, tenant_id: str, file_path: Path) -> int:
    """
    Seed flights from JSON file.
    
    Args:
        session: Async database session
        tenant_id: UUID of the tenant
        file_path: Path to flights.json
        
    Returns:
        Number of flights successfully inserted
    """
    if not file_path.exists():
        print(f"⚠ Warning: {file_path} not found. Skipping flights.")
        return 0
    
    # Load JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract flights array from the JSON structure
    flights_data = data.get("flights", [])
    
    if not flights_data:
        print(f"⚠ Warning: No flights found in {file_path}")
        return 0
    
    inserted_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"\n✈️  Processing {len(flights_data)} flights...")
    
    for idx, flight_json in enumerate(tqdm(flights_data, desc="Flights", unit="flight")):
        try:
            # Generate external_id
            external_id = flight_json.get("flight_id") or f"flight_{idx}"
            
            # Check for duplicates
            result = await session.execute(
                select(Flight).where(
                    Flight.tenant_id == tenant_id,
                    Flight.external_id == external_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                skipped_count += 1
                continue
            
            # Extract leg information
            leg = flight_json.get("leg", {})
            pricing = flight_json.get("pricing", {})
            
            # Parse datetimes
            departure_time = parse_iso_datetime(leg.get("departure"))
            arrival_time = parse_iso_datetime(leg.get("arrival"))
            
            # Calculate duration if both times available
            duration_minutes = None
            if departure_time and arrival_time:
                duration_minutes = int((arrival_time - departure_time).total_seconds() / 60)
            
            # Get carrier info
            carrier_code = flight_json.get("carrier", "")
            carrier_name = carrier_code  # Could map to full names if needed
            
            # Create flight instance
            flight = Flight(
                tenant_id=tenant_id,
                carrier=carrier_name,
                carrier_code=carrier_code,
                flight_number=flight_json.get("flight_no"),
                origin=leg.get("origin", ""),
                destination=leg.get("destination", ""),
                departure_time=departure_time,
                arrival_time=arrival_time,
                duration_minutes=duration_minutes,
                price=Decimal(str(pricing.get("amount", 0))),
                currency=pricing.get("currency", "TRY"),
                cabin_class=pricing.get("cabin"),
                baggage_allowance={"info": flight_json.get("baggage")} if flight_json.get("baggage") else None,
                external_id=external_id,
                provider="legacy_import",
                raw_data=flight_json
            )
            
            session.add(flight)
            inserted_count += 1
            
            # Commit in batches
            if inserted_count % 100 == 0:
                await session.flush()
        
        except Exception as e:
            error_count += 1
            print(f"\n⚠ Error processing flight {idx}: {str(e)}")
            continue
    
    # Final commit
    await session.flush()
    
    print(f"✓ Flights: {inserted_count} inserted, {skipped_count} skipped, {error_count} errors")
    return inserted_count


async def seed_transfers(session, tenant_id: str, file_path: Path) -> int:
    """
    Seed transfers from JSON file.
    
    Args:
        session: Async database session
        tenant_id: UUID of the tenant
        file_path: Path to transfers.json
        
    Returns:
        Number of transfers successfully inserted
    """
    if not file_path.exists():
        print(f"⚠ Warning: {file_path} not found. Skipping transfers.")
        return 0
    
    # Load JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract transfer routes from the JSON structure
    transfers_data = data.get("transfer_routes", [])
    
    if not transfers_data:
        print(f"⚠ Warning: No transfers found in {file_path}")
        return 0
    
    inserted_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"\n🚐 Processing {len(transfers_data)} transfers...")
    
    for idx, transfer_json in enumerate(tqdm(transfers_data, desc="Transfers", unit="transfer")):
        try:
            # Generate external_id
            external_id = transfer_json.get("service_code") or f"transfer_{idx}"
            
            # Check for duplicates
            result = await session.execute(
                select(Transfer).where(
                    Transfer.tenant_id == tenant_id,
                    Transfer.external_id == external_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                skipped_count += 1
                continue
            
            # Extract route and vehicle information
            route = transfer_json.get("route", {})
            vehicle_info = transfer_json.get("vehicle_info", {})
            
            # Create transfer instance
            transfer = Transfer(
                tenant_id=tenant_id,
                vehicle_type=vehicle_info.get("category", "Unknown"),
                capacity=vehicle_info.get("max_pax"),
                pickup_location=route.get("from_name", ""),
                pickup_coordinates=None,  # No coordinates in source data
                dropoff_location=route.get("to_area_name", ""),
                dropoff_coordinates=None,  # No coordinates in source data
                estimated_duration_minutes=route.get("estimated_duration"),
                distance_km=None,  # Not provided in source data
                price=Decimal(str(transfer_json.get("total_price", 0))),
                currency=transfer_json.get("currency", "TRY"),
                amenities=vehicle_info.get("features", []),
                external_id=external_id,
                provider=transfer_json.get("operator_id", "legacy_import"),
                raw_data=transfer_json
            )
            
            session.add(transfer)
            inserted_count += 1
            
            # Commit in batches
            if inserted_count % 100 == 0:
                await session.flush()
        
        except Exception as e:
            error_count += 1
            print(f"\n⚠ Error processing transfer {idx}: {str(e)}")
            continue
    
    # Final commit
    await session.flush()
    
    print(f"✓ Transfers: {inserted_count} inserted, {skipped_count} skipped, {error_count} errors")
    return inserted_count


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """
    Main async function to orchestrate database seeding.
    """
    print("=" * 70)
    print("MergenX Database Seeding Script")
    print("=" * 70)
    print(f"Environment: {sys.platform}")
    print(f"Data directory: {DATA_DIR}")
    print()
    
    try:
        # Create async session
        async with AsyncSessionLocal() as session:
            # Step 1: Get or create tenant
            print("Step 1: Setting up tenant...")
            tenant = await get_or_create_tenant(session, TENANT_SLUG, TENANT_NAME)
            await session.commit()
            
            # Step 2: Seed hotels
            print("\nStep 2: Seeding hotels...")
            hotels_count = await seed_hotels(session, tenant.id, HOTELS_FILE)
            await session.commit()
            
            # Step 3: Seed flights
            print("\nStep 3: Seeding flights...")
            flights_count = await seed_flights(session, tenant.id, FLIGHTS_FILE)
            await session.commit()
            
            # Step 4: Seed transfers
            print("\nStep 4: Seeding transfers...")
            transfers_count = await seed_transfers(session, tenant.id, TRANSFERS_FILE)
            await session.commit()
            
            # Summary
            print("\n" + "=" * 70)
            print("✅ Seeding Complete!")
            print("=" * 70)
            print(f"Tenant: {tenant.name} ({tenant.slug})")
            print(f"Hotels inserted: {hotels_count}")
            print(f"Flights inserted: {flights_count}")
            print(f"Transfers inserted: {transfers_count}")
            print(f"Total records: {hotels_count + flights_count + transfers_count}")
            print("=" * 70)
    
    except SQLAlchemyError as e:
        print(f"\n❌ Database error: {str(e)}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # CRITICAL: Windows asyncio event loop policy fix
    # This prevents "Event loop is closed" errors on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the async main function
    asyncio.run(main())
