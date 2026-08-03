"""Retrieve the most relevant stored chunks for a user query."""

import math

import backend
import db


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def get_top_chunks(query: str, k: int = 3) -> list[dict]:
    """Return the top-k most similar chunks to the query, each with a similarity score."""
    chunks = db.get_all_chunks()
    if not chunks:
        return []

    query_embedding = backend.embed_one(query)

    scored = [
        {**chunk, "score": cosine_similarity(query_embedding, chunk["embedding"])}
        for chunk in chunks
    ]
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:k]
