"""
Hybrid search endpoint combining vector embeddings and geospatial queries.

POST /search/hybrid
- Vectorizes user query using sentence-transformers
- Finds top 5 semantically similar hotels using pgvector
- Passes results to Groq LLM for natural language response
- Returns structured JSON + AI summary
"""

from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, cast, Float, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Hotel
from core.config import settings
from services.ai.embeddings import MergenEmbedder
from services.ai.llm import GroqService

router = APIRouter(tags=["search"])


# ============================================================================
# Request/Response Models
# ============================================================================

class HybridSearchRequest(BaseModel):
    """Request model for hybrid search endpoint."""
    
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Search query (e.g., 'Denize sıfır antalya oteli')",
        example="Luxury beachfront hotel in Antalya"
    )
    
    tenant_id: str = Field(
        ...,
        description="Tenant ID for multi-tenant isolation",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of hotels to return (default: 5, max: 20)"
    )
    
    include_ai_summary: bool = Field(
        default=True,
        description="Include AI-generated summary of results"
    )
    
    city: Optional[str] = Field(default=None)
    district: Optional[str] = Field(default=None)


class HotelResult(BaseModel):
    """Hotel result in search response."""
    
    id: str = Field(description="Hotel ID (UUID)")
    name: str = Field(description="Hotel name")
    concept: Optional[str] = Field(description="Hotel concept (e.g., 'All Inclusive')")
    city: str = Field(description="City name")
    district: Optional[str] = Field(description="District/region")
    area: Optional[str] = Field(description="Neighborhood/area")
    stars: Optional[int] = Field(description="Star rating (1-5)")
    price: Decimal = Field(description="Price per night")
    currency: str = Field(description="Currency code (e.g., 'TRY')")
    amenities: Optional[List[str]] = Field(description="List of amenities")
    description: Optional[str] = Field(description="Hotel description")
    similarity_score: float = Field(
        description="Vector similarity score (0-1, higher = more similar)"
    )
    
    class Config:
        from_attributes = True


class HybridSearchResponse(BaseModel):
    """Response model for hybrid search endpoint."""
    
    query: str = Field(description="Original search query")
    hotels: List[HotelResult] = Field(description="Top matching hotels")
    total_results: int = Field(description="Number of hotels returned")
    ai_summary: Optional[str] = Field(
        default=None,
        description="AI-generated natural language summary of results"
    )
    
    class Config:
        from_attributes = True


# ============================================================================
# Service Dependencies
# ============================================================================

_embedder: Optional[MergenEmbedder] = None
_groq_service: Optional[GroqService] = None


def get_embedder() -> MergenEmbedder:
    """Get or initialize the embedder (lazy loading)."""
    global _embedder
    if _embedder is None:
        _embedder = MergenEmbedder()
    return _embedder


def get_groq_service() -> GroqService:
    """Get or initialize the Groq service (lazy loading)."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/hybrid",
    response_model=HybridSearchResponse,
    summary="Hybrid Hotel Search",
    description="""
    Perform hybrid search combining:
    1. Vector similarity (semantic search with pgvector)
    2. Natural language generation (Groq LLM)
    
    Returns top matching hotels + AI-generated summary.
    """,
)
async def hybrid_search(
    request: HybridSearchRequest,
    db: AsyncSession = Depends(get_db),
    embedder: MergenEmbedder = Depends(get_embedder),
    groq_service: GroqService = Depends(get_groq_service),
) -> HybridSearchResponse:
    """
    Hybrid hotel search using vector embeddings and LLM.
    
    1. Vectorizes the user's query
    2. Searches PostgreSQL with pgvector for semantic similarity
    3. Uses Groq LLM to generate natural language response
    4. Returns structured results + AI summary
    
    Args:
        request: HybridSearchRequest containing query and options
        db: AsyncSession for database queries
        embedder: MergenEmbedder service for generating embeddings
        groq_service: GroqService for LLM response generation
        
    Returns:
        HybridSearchResponse with hotels and AI summary
        
    Raises:
        HTTPException: If query is empty, DB error occurs, or Groq API fails
    """
    
    # Validate query
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    # Step 1: Vectorize the user's query
    try:
        query_embedding = await embedder.embed_text(request.query)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query for embedding generation: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation failed: {str(e)}"
        )
    
    # Step 2: Find similar hotels using pgvector
    # Using the <=> operator for cosine distance (default for pgvector)
    # Lower distance = higher similarity
    # We use LIMIT with ORDER BY distance to get top N matches
    
    stmt = select(
        Hotel.id,
        Hotel.name,
        Hotel.concept,
        Hotel.city,
        Hotel.district,
        Hotel.area,
        Hotel.stars,
        Hotel.price,
        Hotel.currency,
        Hotel.amenities,
        Hotel.description,
        # Calculate similarity as 1 - distance (since pgvector uses distance)
        # The <=> operator returns cosine distance, we convert to similarity
        cast(Hotel.embedding.op('<=>')(query_embedding), Float).label("similarity_score"),
    ).where(
        Hotel.tenant_id == request.tenant_id,
        Hotel.embedding.isnot(None),  # Only hotels with embeddings
    )
    
    if request.city:
        stmt = stmt.where(func.lower(Hotel.city) == request.city.lower())
    if request.district:
        stmt = stmt.where(func.lower(Hotel.district) == request.district.lower())
    
    stmt = stmt.order_by(
        Hotel.embedding.op('<=>')(query_embedding).asc()  # Closest first
    ).limit(request.limit)
    
    result = await db.execute(stmt)
    rows = result.fetchall()
    
    if not rows:
        # No results with embeddings, try without embedding filter
        stmt = select(Hotel).where(
            Hotel.tenant_id == request.tenant_id
        ).limit(request.limit)
        
        result = await db.execute(stmt)
        hotels = result.scalars().all()
        
        hotel_results = [
            HotelResult(
                id=str(h.id),
                name=h.name,
                concept=h.concept,
                city=h.city,
                district=h.district,
                area=h.area,
                stars=h.stars,
                price=h.price,
                currency=h.currency,
                amenities=h.amenities,
                description=h.description,
                similarity_score=0.0,
            )
            for h in hotels
        ]
    else:
        # Convert rows to HotelResult objects
        hotel_results = [
            HotelResult(
                id=str(row[0]),
                name=row[1],
                concept=row[2],
                city=row[3],
                district=row[4],
                area=row[5],
                stars=row[6],
                price=row[7],
                currency=row[8],
                amenities=row[9],
                description=row[10],
                similarity_score=max(0.0, 1.0 - float(row[11])),
            )
            for row in rows
        ]
    
    # Step 3: Generate AI summary if requested
    ai_summary = None
    if request.include_ai_summary and hotel_results:
        try:
            # Convert HotelResult to dict for Groq service
            hotel_dicts = [h.model_dump() for h in hotel_results]
            
            ai_summary = await groq_service.generate_summary(
                hotels=hotel_dicts,
                user_query=request.query,
            )
        except Exception as e:
            # Log error but don't fail the entire request
            print(f"⚠️  Error generating AI summary: {e}")
            # Continue with results even if AI summary fails
    
    # Step 4: Return response
    return HybridSearchResponse(
        query=request.query,
        hotels=hotel_results,
        total_results=len(hotel_results),
        ai_summary=ai_summary,
    )


@router.get(
    "/health",
    summary="Search Service Health Check",
    description="Check if the search service is operational",
)
async def search_health() -> dict:
    """
    Health check endpoint for the search service.
    
    Verifies:
    - Embedder model is loaded
    - Groq API credentials are available
    
    Returns:
        Status information
    """
    try:
        embedder = get_embedder()
        groq_service = get_groq_service()
        
        return {
            "status": "healthy",
            "embedder": {
                "model": embedder.model_name,
                "dimension": embedder.get_embedding_dimension(),
            },
            "llm": {
                "service": "groq",
                "model": groq_service.model,
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Search service unhealthy: {str(e)}"
        )
