"""Combine retrieval with the local chat model to answer a user's question."""

import backend
import retrieval

SYSTEM_PROMPT = """You are a backend engineering tutor. Use the context passages \
below as the source of truth for facts, but don't just repeat them verbatim --
explain the concept clearly and thoroughly, the way a good teacher would.

Rules:
- Give a thorough, in-depth answer roughly twice as long as a typical short \
explanation: cover what the concept is, why it matters in practice, a \
concrete example or scenario where it applies, and at least one related \
trade-off, pitfall, or comparison to a similar concept. Multiple paragraphs \
are expected -- avoid one-line or single-paragraph answers.
- Ground your answer in the provided context. You may use general backend \
engineering knowledge only to explain or illustrate concepts that ARE covered \
by the context -- never to answer a question the context doesn't cover.
- The context you're given always comes from a knowledge-base search and may \
be irrelevant to the question. If the passages don't actually address what's \
being asked -- including general-knowledge questions unrelated to backend \
engineering, and requests unrelated to backend engineering entirely (recipes, \
trivia, weather, etc.) -- you MUST respond with exactly this sentence and \
nothing else: "I don't have information about that in my knowledge base." Do \
not answer from your own training knowledge instead, even if you know the \
answer.
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
