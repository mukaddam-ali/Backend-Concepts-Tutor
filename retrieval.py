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


# Below this, a chunk is "closest available" but not actually about the
# query -- observed empirically with real qwen3-embedding-0.6b embeddings:
# in-scope questions' top chunks scored 0.6-0.82, while genuinely
# out-of-scope questions ("What is the capital of France?", "Can you
# recommend a good pizza recipe?") topped out at 0.3-0.37, a wide, clean
# gap. Without this cutoff, get_top_chunks always returns *something*
# (there's always a "nearest" chunk), so generate.py's "no chunks -> I
# don't know" fallback never fires, and small local models don't reliably
# follow an instruction to ignore irrelevant context and decline instead
# of answering from their own general knowledge.
MIN_SIMILARITY = 0.45


def get_top_chunks(query: str, k: int = 3) -> list[dict]:
    """Return the top-k most similar chunks to the query, each with a similarity score.

    Chunks scoring below MIN_SIMILARITY are excluded even if they'd otherwise
    make the top-k cut -- an irrelevant "closest" chunk is still irrelevant.
    """
    chunks = db.get_all_chunks()
    if not chunks:
        return []

    query_embedding = backend.embed_one(query)

    scored = [
        {**chunk, "score": cosine_similarity(query_embedding, chunk["embedding"])}
        for chunk in chunks
    ]
    scored.sort(key=lambda c: c["score"], reverse=True)
    return [c for c in scored if c["score"] >= MIN_SIMILARITY][:k]
