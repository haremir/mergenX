"""
Embeddings service using sentence-transformers.

Provides async wrapper around sentence-transformers for generating
768-dimensional embeddings for semantic search.
"""

import asyncio
from typing import List

from sentence_transformers import SentenceTransformer


class MergenEmbedder:
    """
    Async wrapper for sentence-transformers embeddings.
    
    Uses the multilingual intfloat/multilingual-e5-base model (768 dimensions)
    for efficient semantic search in PostgreSQL with pgvector.
    """
    
    def __init__(self, model_name: str = "intfloat/multilingual-e5-base"):
        """
        Initialize the embedder.
        
        Args:
            model_name: HuggingFace model identifier
                Default: intfloat/multilingual-e5-base (768-dim, multilingual)
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text (query).
        
        Args:
            text: Input text to embed
            
        Returns:
            List of 768 floats representing the embedding vector
            
        Raises:
            ValueError: If text is empty or embedding generation fails
            
        Example:
            >>> embedder = MergenEmbedder()
            >>> embedding = await embedder.embed_text("5-star beachfront hotel in Antalya")
            >>> len(embedding)
            768
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # E5 models require "query: " prefix for queries
        prefixed_text = f"query: {text}"
        
        # Run in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self.model.encode(prefixed_text, convert_to_numpy=True)  # Force numpy for consistency
        )
        
        # Convert to list - handle both numpy arrays and tensors
        if hasattr(embedding, 'tolist'):
            result = embedding.tolist()
        else:
            result = list(embedding)
        
        # Ensure we return a list, not a scalar
        if not isinstance(result, list):
            raise ValueError(
                f"Embedding conversion failed: expected list, got {type(result).__name__}"
            )
        
        # Validate dimension
        if len(result) != self.embedding_dim:
            raise ValueError(
                f"Invalid embedding dimension: expected {self.embedding_dim}, got {len(result)}"
            )
        
        return result
    
    async def embed_texts(self, texts: List[str], prefix: str = "passage") -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            prefix: Prefix type - "passage" for documents or "query" for queries
            
        Returns:
            List of embedding vectors (each 768 floats)
            
        Raises:
            ValueError: If texts is empty or contains empty strings
            
        Example:
            >>> embedder = MergenEmbedder()
            >>> embeddings = await embedder.embed_texts([
            ...     "Luxury hotel in Antalya with beach access",
            ...     "Budget-friendly hotel in Izmir"
            ... ])
            >>> len(embeddings)
            2
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Filter out empty texts and keep track of indices
        valid_texts = [t for t in texts if t and t.strip()]
        if len(valid_texts) != len(texts):
            raise ValueError("All texts must be non-empty")
        
        # E5 models require prefix for all texts
        prefixed_texts = [f"{prefix}: {t}" for t in texts]
        
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(prefixed_texts, convert_to_numpy=True)  # Force numpy for consistency
        )
        
        # Convert to list of lists
        if hasattr(embeddings, 'tolist'):
            result = embeddings.tolist()
        else:
            result = [e.tolist() if hasattr(e, 'tolist') else list(e) for e in embeddings]
        
        # Validate result is a list of lists
        if not isinstance(result, list):
            raise ValueError(f"Expected list, got {type(result).__name__}")
        
        for i, emb in enumerate(result):
            if not isinstance(emb, list):
                raise ValueError(
                    f"Embedding {i} is not a list: {type(emb).__name__}"
                )
            if len(emb) != self.embedding_dim:
                raise ValueError(
                    f"Embedding {i} has wrong dimension: expected {self.embedding_dim}, got {len(emb)}"
                )
        
        return result
    
    def get_embedding_dimension(self) -> int:
        """Get the dimensionality of embeddings produced by this model."""
        return self.embedding_dim
