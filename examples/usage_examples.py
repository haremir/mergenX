"""
Example usage of AI & Search API components.

This file demonstrates how to use MergenEmbedder, GroqService, and the search endpoint.
"""

import asyncio
import os

from services.ai.embeddings import MergenEmbedder
from services.ai.llm import GroqService


async def example_embeddings():
    """Example 1: Generate embeddings."""
    print("\n" + "="*70)
    print("Example 1: Text Embeddings with MergenEmbedder")
    print("="*70)
    
    # Initialize embedder
    embedder = MergenEmbedder()
    
    # Single embedding
    text1 = "Luxury beachfront hotel in Antalya with pool and spa"
    embedding1 = await embedder.embed_text(text1)
    print(f"\n✅ Text: {text1}")
    print(f"   Embedding dimension: {len(embedding1)}")
    print(f"   First 5 values: {embedding1[:5]}")
    
    # Batch embeddings
    texts = [
        "5-star all-inclusive resort in Bodrum",
        "Budget-friendly hotel in Istanbul",
        "Boutique hotel in Cappadocia",
    ]
    embeddings = await embedder.embed_texts(texts)
    print(f"\n✅ Batch embeddings for {len(texts)} hotels:")
    for text, emb in zip(texts, embeddings):
        print(f"   • {text[:50]}...")
        print(f"     Dimension: {len(emb)}")


async def example_llm():
    """Example 2: Generate responses with GroqService."""
    print("\n" + "="*70)
    print("Example 2: LLM Responses with GroqService")
    print("="*70)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("\n⚠️  GROQ_API_KEY not set!")
        print("   Set it with: $env:GROQ_API_KEY='gsk_xxxxxxxxxxxxx'")
        return
    
    # Initialize service
    groq = GroqService(api_key=api_key)
    
    # Example 1: Simple generation
    print("\n✅ Generating response...")
    response = await groq.generate(
        system_prompt="You are a helpful travel assistant for Turkish hotels.",
        user_query="What's the best hotel for a family beach vacation?",
        context="Available: 5-star resort with kids club, 3-star family hotel, budget beachfront",
        max_tokens=256,
    )
    print(f"\n📝 Response:\n{response}")
    
    # Example 2: Hotel summary
    print("\n✅ Generating hotel summary...")
    hotels = [
        {
            "name": "Antalya Palace",
            "concept": "5-Star All Inclusive",
            "stars": 5,
            "price": 500,
            "currency": "TRY",
            "area": "Konyaalti Beach",
            "amenities": ["pool", "spa", "beach", "restaurant", "kids_club"],
            "distance_km": 0.0,
        },
        {
            "name": "Blue Lagoon Hotel",
            "concept": "4-Star Resort",
            "stars": 4,
            "price": 300,
            "currency": "TRY",
            "area": "Oludeniz",
            "amenities": ["pool", "beach", "restaurant"],
            "distance_km": 25.0,
        },
    ]
    
    summary = await groq.generate_summary(
        hotels=hotels,
        user_query="Best beachfront hotels in Antalya?",
    )
    print(f"\n📝 Summary:\n{summary}")


async def example_fastapi_integration():
    """Example 3: FastAPI integration."""
    print("\n" + "="*70)
    print("Example 3: FastAPI Integration Instructions")
    print("="*70)
    
    print("""
✅ To use the search endpoint in your FastAPI app:

1. Add to apps/api/main.py:
   
   from fastapi import FastAPI
   from apps.api.v1.endpoints import search
   
   app = FastAPI()
   app.include_router(search.router, prefix="/api/v1")

2. Run the server:
   
   uvicorn apps.api.main:app --reload

3. Test with curl:
   
   curl -X POST http://localhost:8000/api/v1/search/hybrid \\
     -H "Content-Type: application/json" \\
     -d '{
       "query": "Denize sıfır antalya oteli",
       "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
     }'

4. Or test with Python:
   
   import requests
   response = requests.post(
       "http://localhost:8000/api/v1/search/hybrid",
       json={
           "query": "Best hotels in Antalya",
           "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
           "limit": 5,
           "include_ai_summary": True
       }
   )
   print(response.json())
    """)


async def main():
    """Run all examples."""
    print("\n" + "🚀 "*35)
    print("MergenX AI & Search API - Usage Examples")
    print("🚀 "*35)
    
    # Example 1: Embeddings
    await example_embeddings()
    
    # Example 2: LLM
    await example_llm()
    
    # Example 3: FastAPI
    await example_fastapi_integration()
    
    print("\n" + "="*70)
    print("✨ Examples complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
