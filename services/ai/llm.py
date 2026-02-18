"""
LLM service using Groq API.

Provides async wrapper around Groq's official Python client for
text generation using fast open-source models like Llama 3.
"""

from typing import Optional

from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

class GroqService:
    """
    Groq LLM service for natural language generation.
    
    Uses Groq's fast inference API with models like llama-3.3-70b-versatile
    for generating natural language responses based on search context.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """
        Initialize Groq service.
        
        Args:
            api_key: Groq API key (if None, uses GROQ_API_KEY env var)
            model: Model name. Options:
                - llama-3.3-70b-versatile (recommended, ~70B parameters)
                - llama-3.2-90b-vision-preview
                - mixtral-8x7b-32768
            temperature: Sampling temperature (0.0-2.0), default 0.7
                Lower = more deterministic, Higher = more creative
            max_tokens: Maximum tokens to generate, default 1024
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    async def generate(
        self,
        system_prompt: str,
        user_query: str,
        context: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a natural language response using Groq.
        
        Args:
            system_prompt: System instruction for the model behavior
                Example: "You are a helpful travel assistant..."
            user_query: The user's original query
                Example: "Recommend a beachfront hotel in Antalya"
            context: Search results context to base response on
                Example: "Found 5 hotels: [hotel details...]"
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            Generated response string
            
        Example:
            >>> service = GroqService()
            >>> response = await service.generate(
            ...     system_prompt="You are a travel expert...",
            ...     user_query="Best hotels in Antalya?",
            ...     context="Hotel 1: Luxury Resort...\nHotel 2: Budget...",
            ... )
        """
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        # Build the full prompt
        full_prompt = f"""System: {system_prompt}

User Query: {user_query}

Search Results Context:
{context}

Please provide a helpful, natural language response based on the search results above."""
        
        # Call Groq API (sync API, but we can use it in async context)
        message = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"Query: {user_query}\n\nContext:\n{context}",
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return message.choices[0].message.content
    
    async def generate_summary(
        self,
        hotels: list,
        user_query: str,
    ) -> str:
        """
        Generate a summary response for hotel search results.
        
        Args:
            hotels: List of hotel dictionaries with name, concept, price, amenities, etc.
            user_query: The user's search query
            
        Returns:
            Natural language summary of the hotels
            
        Example:
            >>> service = GroqService()
            >>> hotels = [
            ...     {"name": "Hotel A", "concept": "5-Star", "price": 500, ...},
            ...     {"name": "Hotel B", "concept": "3-Star", "price": 200, ...}
            ... ]
            >>> summary = await service.generate_summary(hotels, "Best beachfront hotels")
        """
        system_prompt = """You are an expert Turkish travel assistant helping users find the perfect hotel.
You have access to search results and should provide a personalized, helpful summary.
- Be concise but informative (2-3 sentences)
- Highlight key features (star rating, concept, amenities)
- Avoid generic responses
- Use Turkish if the query is in Turkish, English if the query is in English"""
        
        # Format hotel information for context
        hotel_context = "Found hotels:\n\n"
        for i, hotel in enumerate(hotels, 1):
            amenities_str = ", ".join(hotel.get("amenities", [])) if hotel.get("amenities") else "N/A"
            hotel_context += f"{i}. {hotel['name']}\n"
            hotel_context += f"   - Concept: {hotel.get('concept', 'N/A')}\n"
            hotel_context += f"   - Stars: {hotel.get('stars', 'N/A')}/5\n"
            hotel_context += f"   - Price: {hotel['price']} {hotel['currency']}/night\n"
            hotel_context += f"   - Area: {hotel.get('area', 'N/A')}\n"
            hotel_context += f"   - Amenities: {amenities_str}\n"
            hotel_context += f"   - Distance to center: {hotel.get('distance_km', 'N/A')} km\n\n"
        
        return await self.generate(
            system_prompt=system_prompt,
            user_query=user_query,
            context=hotel_context,
            max_tokens=512,
        )
