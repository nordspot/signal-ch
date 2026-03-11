"""Embedding generation for sources and IOs."""

import hashlib

import structlog

from app.config import settings

logger = structlog.get_logger()


async def generate_embedding(text: str) -> list[float] | None:
    """Generate a 1024-dim embedding for the given text.

    Uses Cohere multilingual embed v3 if API key is available,
    otherwise returns a deterministic hash-based pseudo-embedding.
    """
    if not text or len(text.strip()) < 10:
        return None

    # Truncate to reasonable length
    text = text[:8000]

    if settings.cohere_api_key:
        return await _cohere_embed(text)

    # Fallback: deterministic pseudo-embedding for development
    return _hash_embedding(text)


async def _cohere_embed(text: str) -> list[float] | None:
    """Generate embedding using Cohere API."""
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.cohere.ai/v1/embed",
                headers={
                    "Authorization": f"Bearer {settings.cohere_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "texts": [text],
                    "model": "embed-multilingual-v3.0",
                    "input_type": "search_document",
                    "embedding_types": ["float"],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["embeddings"]["float"][0]

    except Exception as e:
        logger.error("cohere_embed_error", error=str(e))
        return _hash_embedding(text)


def _hash_embedding(text: str) -> list[float]:
    """Generate a deterministic pseudo-embedding from text hash.

    NOT for production — used only for development/testing.
    """
    import struct

    # Create deterministic hash-based embedding
    embedding = []
    for i in range(64):  # 64 chunks × 16 floats = 1024
        chunk_hash = hashlib.sha256(f"{text}:{i}".encode()).digest()
        floats = struct.unpack("16f", chunk_hash[:64])
        embedding.extend(floats)

    # Normalize
    norm = sum(x * x for x in embedding) ** 0.5
    if norm > 0:
        embedding = [x / norm for x in embedding]

    return embedding[:1024]


async def compute_similarity(embedding_a: list[float], embedding_b: list[float]) -> float:
    """Compute cosine similarity between two embeddings."""
    if not embedding_a or not embedding_b:
        return 0.0

    dot_product = sum(a * b for a, b in zip(embedding_a, embedding_b))
    norm_a = sum(a * a for a in embedding_a) ** 0.5
    norm_b = sum(b * b for b in embedding_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)
