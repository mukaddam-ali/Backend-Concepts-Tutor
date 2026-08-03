"""Combine retrieval with the local chat model to answer a user's question."""

import backend
import retrieval

SYSTEM_PROMPT = """You are a backend engineering tutor. Use the context passages \
below as the source of truth for facts, but don't just repeat them verbatim --
explain the concept clearly and thoroughly, the way a good teacher would.

Rules:
- Give a complete, well-developed answer: cover what the concept is, why it \
matters in practice, and a concrete example or scenario where it applies. \
Multiple sentences or paragraphs are expected -- avoid one-line answers.
- Ground your answer in the provided context, but you may use general backend \
engineering knowledge to explain ideas more clearly, add examples, or connect \
concepts together.
- If the context truly does not cover the topic at all, say "I don't have \
information about that in my knowledge base" rather than guessing.
- Mention which source document(s) informed your answer, e.g. "(source: caching)".
"""


def build_context_block(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[source: {chunk['source']}]\n{chunk['content']}" for chunk in chunks
    )


def answer_query(question: str, k: int = 4) -> dict:
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
