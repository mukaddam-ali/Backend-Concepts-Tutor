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


def run_ingestion() -> None:
    db.init_db()
    db.clear_chunks()

    doc_paths = sorted(DOCS_DIR.glob("*.md"))
    if not doc_paths:
        raise RuntimeError(f"No .md files found in {DOCS_DIR}")

    total_chunks = 0
    for doc_path in doc_paths:
        text = doc_path.read_text(encoding="utf-8")
        chunks = chunk_text(text, doc_path.stem)
        if not chunks:
            continue

        embeddings = backend.embed(chunks)
        for chunk, embedding in zip(chunks, embeddings):
            db.insert_chunk(source=doc_path.stem, content=chunk, embedding=embedding)
            total_chunks += 1

        print(f"Ingested {doc_path.name}: {len(chunks)} chunks")

    print(f"\nDone. {total_chunks} chunks stored across {len(doc_paths)} documents.")


if __name__ == "__main__":
    run_ingestion()
