"""
SQLAlchemy ORM Models for Harezmi Intelligence.

Multi-Tenant Travel SaaS database schema with:
- Multi-tenancy support (tenant_id on all tables except Tenant)
- Geospatial queries (PostGIS/GeoAlchemy2)
- Vector embeddings (pgvector)
- Proper indexes for performance

Architecture:
- All models inherit from Base (DeclarativeBase)
- Common fields are in mixins (TimestampMixin, TenantMixin)
- UUIDs as primary keys with automatic generation
- Spatial indexes (GIST) on geography fields
- Vector indexes (IVFFlat) on embedding fields
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from geoalchemy2 import Geography
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


# ============================================================================
# Mixins for Common Fields
# ============================================================================

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when record was last updated"
    )


class TenantMixin:
    """Mixin for multi-tenancy support."""
    
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to tenant (for multi-tenancy isolation)"
    )


# ============================================================================
# Core Models
# ============================================================================

class Tenant(Base, TimestampMixin):
    """
    Tenant model for multi-tenancy.
    
    Each tenant represents a separate customer/organization using the platform.
    All other tables reference this via tenant_id for data isolation.
    """
    
    __tablename__ = "tenants"
    
    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for tenant"
    )
    
    # Core Fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Display name of the tenant organization"
    )
    
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        doc="URL-friendly identifier (e.g., 'bitur', 'jollytur')"
    )
    
    # Security
    api_key_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hashed API key for tenant authentication"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether tenant is active and can access the system"
    )
    
    # Metadata
    settings: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Tenant-specific configuration settings"
    )
    
    # Relationships
    hotels = relationship("Hotel", back_populates="tenant", cascade="all, delete-orphan")
    flights = relationship("Flight", back_populates="tenant", cascade="all, delete-orphan")
    transfers = relationship("Transfer", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, slug='{self.slug}', name='{self.name}')>"


class Hotel(Base, TenantMixin, TimestampMixin):
    """
    Hotel model with geospatial and vector embedding support.
    
    Features:
    - PostGIS Geography for precise location queries
    - pgvector embeddings for semantic search
    - Normalized location data (city, district, area)
    - JSONB for flexible amenities storage
    """
    
    __tablename__ = "hotels"
    
    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for hotel"
    )
    
    # Core Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Hotel name"
    )
    
    # Location Information (Normalized)
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Normalized city name (e.g., 'izmir', 'antalya')"
    )
    
    district: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Normalized district/county (e.g., 'cesme', 'alanya')"
    )
    
    area: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Normalized area/neighborhood (e.g., 'alacati', 'oludeniz')"
    )
    
    # Geospatial Data (PostGIS)
    location: Mapped[Optional[str]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
        doc="GPS coordinates (latitude, longitude) - SRID 4326 (WGS84)"
    )
    
    # Business Information
    concept: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Hotel concept (e.g., 'All Inclusive', 'Ultra All Inclusive', 'Bed & Breakfast')"
    )
    
    stars: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Star rating (1-5)"
    )
    
    # Pricing
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        doc="Base price per night (2 decimal places)"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="TRY",
        doc="Currency code (ISO 4217, e.g., 'TRY', 'EUR', 'USD')"
    )
    
    # Content
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Hotel description for display"
    )
    
    amenities: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        doc="List of amenities (e.g., ['wifi', 'pool', 'spa'])"
    )
    
    # AI/ML Features
    embedding: Mapped[Optional[list]] = mapped_column(
        Vector(768),
        nullable=True,
        doc="Vector embedding for semantic search (768 dimensions)"
    )
    
    # External References
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        doc="External system ID (e.g., from provider API)"
    )
    
    provider: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Data provider name"
    )
    
    # Metadata
    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Original raw data from provider"
    )
    
    # Relationships
    tenant = relationship("Tenant", back_populates="hotels")
    
    def __repr__(self) -> str:
        return f"<Hotel(id={self.id}, name='{self.name}', city='{self.city}')>"


class Flight(Base, TenantMixin, TimestampMixin):
    """
    Flight model for flight search results and bookings.
    
    Stores flight information with origin, destination, pricing,
    and carrier details.
    """
    
    __tablename__ = "flights"
    
    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for flight"
    )
    
    # Flight Information
    carrier: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Airline carrier name (e.g., 'Turkish Airlines', 'Pegasus')"
    )
    
    carrier_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        doc="IATA airline code (e.g., 'TK', 'PC')"
    )
    
    flight_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        doc="Flight number (e.g., 'TK1234')"
    )
    
    # Route
    origin: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Origin airport/city code (e.g., 'IST', 'SAW')"
    )
    
    destination: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Destination airport/city code (e.g., 'AYT', 'DLM')"
    )
    
    # Timing
    departure_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="Scheduled departure time"
    )
    
    arrival_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Scheduled arrival time"
    )
    
    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Flight duration in minutes"
    )
    
    # Pricing
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        doc="Flight price per person"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="TRY",
        doc="Currency code (ISO 4217)"
    )
    
    # Details
    cabin_class: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Cabin class (e.g., 'Economy', 'Business', 'First')"
    )
    
    baggage_allowance: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Baggage allowance details"
    )
    
    # External References
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        doc="External system ID"
    )
    
    provider: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Flight data provider"
    )
    
    # Metadata
    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Original raw data from provider"
    )
    
    # Relationships
    tenant = relationship("Tenant", back_populates="flights")
    
    def __repr__(self) -> str:
        return f"<Flight(id={self.id}, carrier='{self.carrier}', route='{self.origin}->{self.destination}')>"


class Transfer(Base, TenantMixin, TimestampMixin):
    """
    Transfer model for ground transportation services.
    
    Represents transfer services between airports, hotels, and other locations.
    """
    
    __tablename__ = "transfers"
    
    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for transfer"
    )
    
    # Transfer Information
    vehicle_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Vehicle type (e.g., 'Private Car', 'Shared Shuttle', 'VIP Van')"
    )
    
    capacity: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Maximum passenger capacity"
    )
    
    # Route
    pickup_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Pickup location name"
    )
    
    pickup_coordinates: Mapped[Optional[str]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
        doc="Pickup GPS coordinates"
    )
    
    dropoff_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Drop-off location name"
    )
    
    dropoff_coordinates: Mapped[Optional[str]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
        doc="Drop-off GPS coordinates"
    )
    
    # Timing
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Estimated transfer duration in minutes"
    )
    
    distance_km: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        doc="Distance in kilometers"
    )
    
    # Pricing
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        doc="Transfer price"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="TRY",
        doc="Currency code (ISO 4217)"
    )
    
    # Details
    amenities: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Transfer amenities (e.g., ['wifi', 'air_conditioning', 'child_seat'])"
    )
    
    # External References
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        doc="External system ID"
    )
    
    provider: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Transfer service provider"
    )
    
    # Metadata
    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Original raw data from provider"
    )
    
    # Relationships
    tenant = relationship("Tenant", back_populates="transfers")
    
    def __repr__(self) -> str:
        return f"<Transfer(id={self.id}, vehicle='{self.vehicle_type}', route='{self.pickup_location}->{self.dropoff_location}')>"


# ============================================================================
# Database Indexes for Performance
# ============================================================================

# Spatial Index (GIST) on Hotel.location for fast geospatial queries
Index(
    "idx_hotel_location_gist",
    Hotel.location,
    postgresql_using="gist",
)

# Spatial Index (GIST) on Transfer pickup/dropoff coordinates
Index(
    "idx_transfer_pickup_gist",
    Transfer.pickup_coordinates,
    postgresql_using="gist",
)

Index(
    "idx_transfer_dropoff_gist",
    Transfer.dropoff_coordinates,
    postgresql_using="gist",
)

# Vector Index (IVFFlat) on Hotel.embedding for fast semantic search
# Note: This requires pgvector extension and sufficient data
# The lists parameter (100) defines the number of inverted lists for clustering
Index(
    "idx_hotel_embedding_ivfflat",
    Hotel.embedding,
    postgresql_using="ivfflat",
    postgresql_with={"lists": 100},
    postgresql_ops={"embedding": "vector_cosine_ops"},
)

# Composite indexes for common query patterns
Index(
    "idx_hotel_tenant_city",
    Hotel.tenant_id,
    Hotel.city,
)

Index(
    "idx_hotel_tenant_city_price",
    Hotel.tenant_id,
    Hotel.city,
    Hotel.price,
)

Index(
    "idx_flight_tenant_route_date",
    Flight.tenant_id,
    Flight.origin,
    Flight.destination,
    Flight.departure_time,
)

Index(
    "idx_transfer_tenant_locations",
    Transfer.tenant_id,
    Transfer.pickup_location,
    Transfer.dropoff_location,
)
