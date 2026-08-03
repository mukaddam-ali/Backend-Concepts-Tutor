"""Combine retrieval with the local chat model to answer a user's question."""

import backend
import retrieval

SYSTEM_PROMPT = """You are a backend engineering tutor. Answer the user's question \
using ONLY the context passages provided below. Each passage is labeled with its \
source document name.

Rules:
- If the context does not contain enough information to answer, say "I don't have \
information about that in my knowledge base" instead of guessing.
- Keep answers concise and clear, suitable for a beginner learning backend concepts.
- When you use information from a passage, mention which source document it came \
from, e.g. "(source: caching)".
"""


def build_context_block(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[source: {chunk['source']}]\n{chunk['content']}" for chunk in chunks
    )


def answer_query(question: str, k: int = 3) -> dict:
    top_chunks = retrieval.get_top_chunks(question, k=k)

    if not top_chunks:
        return {
            "answer": "I don't have information about that in my knowledge base.",
            "sources": [],
        }

    context_block = build_context_block(top_chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context_block}\n\nQuestion: {question}",
        },
    ]

    answer_text = backend.chat(messages)
    answered_from_context = "don't have information" not in answer_text.lower()

    return {
        "answer": answer_text,
        "sources": sorted({c["source"] for c in top_chunks}) if answered_from_context else [],
    }
