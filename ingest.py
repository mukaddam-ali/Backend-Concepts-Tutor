"""Chunk the docs/ knowledge base, embed each chunk, and store it in SQLite."""

import re
from pathlib import Path

import backend
import db

DOCS_DIR = Path(__file__).parent / "docs"

# Matches from a "## Free resources" heading to the end of the doc.
_FREE_RESOURCES_RE = re.compile(r"\n##\s*Free resources.*\Z", re.S | re.I)


def strip_free_resources(text: str) -> str:
    """Remove the "Free resources" section before chunking.

    Link titles there repeat the topic name (e.g. "Kubernetes documentation"),
    which gave those chunks an inflated keyword-overlap score in the demo
    backend's retrieval -- confirmed by testing, where "What is Kubernetes
    used for?" retrieved the resources list instead of the actual
    explanation. The section stays in the doc file for humans reading it
    directly; it's just excluded from what the assistant can retrieve.
    """
    return _FREE_RESOURCES_RE.sub("", text)


def chunk_text(text: str, source: str) -> list[str]:
    """Split a markdown doc into passage-level chunks (~1-3 paragraphs each)."""
    text = strip_free_resources(text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks = []
    buffer: list[str] = []
    for para in paragraphs:
        buffer.append(para)
        if len(buffer) >= 2:
            chunks.append("\n\n".join(buffer))
            buffer = []
    if buffer:
        chunks.append("\n\n".join(buffer))

    return chunks


# Chunks per embed() call. One API request per document (34+ documents)
# was enough on its own to trip Gemini's free-tier requests-per-minute
# quota, especially across repeated redeploys (Render's disk is ephemeral,
# so every restart re-ingests from scratch). Batching many chunks into a
# handful of calls cuts the request count drastically; kept comfortably
# under typical per-call batch-size limits.
_EMBED_BATCH_SIZE = 90


def run_ingestion() -> None:
    db.init_db()

    doc_paths = sorted(DOCS_DIR.glob("*.md"))
    if not doc_paths:
        raise RuntimeError(f"No .md files found in {DOCS_DIR}")

    sources: list[str] = []
    all_chunks: list[str] = []
    for doc_path in doc_paths:
        text = doc_path.read_text(encoding="utf-8")
        chunks = chunk_text(text, doc_path.stem)
        sources.extend([doc_path.stem] * len(chunks))
        all_chunks.extend(chunks)

    # Embed everything before touching the DB at all. If a later batch fails
    # (e.g. a rate limit), nothing has been written yet -- the existing
    # knowledge base (if any) stays intact instead of being wiped and left
    # half-populated, which previously caused count_chunks() > 0 to silently
    # skip retrying ingestion on a knowledge base missing whichever docs came
    # after the failed batch.
    all_embeddings: list[list[float]] = []
    for start in range(0, len(all_chunks), _EMBED_BATCH_SIZE):
        batch_chunks = all_chunks[start : start + _EMBED_BATCH_SIZE]
        all_embeddings.extend(backend.embed(batch_chunks))

    db.clear_chunks()
    for source, chunk, embedding in zip(sources, all_chunks, all_embeddings):
        db.insert_chunk(source=source, content=chunk, embedding=embedding)

    print(f"\nDone. {len(all_chunks)} chunks stored across {len(doc_paths)} documents.")


if __name__ == "__main__":
    run_ingestion()
