import math

import demo_backend


def test_embed_one_returns_unit_vector():
    vector = demo_backend.embed_one("caching reduces database load")
    norm = math.sqrt(sum(v * v for v in vector))
    assert math.isclose(norm, 1.0, rel_tol=1e-6)
    assert len(vector) == demo_backend.VECTOR_DIM


def test_embed_empty_string_returns_zero_vector():
    vector = demo_backend.embed_one("")
    assert vector == [0.0] * demo_backend.VECTOR_DIM


def test_embed_similar_texts_are_more_similar_than_unrelated():
    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb)

    v1 = demo_backend.embed_one("caching reduces database load and improves latency")
    v2 = demo_backend.embed_one("caching improves latency by reducing database load")
    v3 = demo_backend.embed_one("microservices split an application into services")

    assert cosine(v1, v2) > cosine(v1, v3)


def _build_messages(context_block: str, question: str) -> list[dict]:
    return [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": f"Context:\n{context_block}\n\nQuestion: {question}"},
    ]


def test_chat_picks_sentence_with_most_keyword_overlap():
    context = (
        "[source: caching]\n"
        "Caching stores a copy of expensive data. It reduces load on a database.\n\n"
        "[source: rest-apis]\n"
        "REST APIs use standard HTTP methods. GET reads a resource."
    )
    messages = _build_messages(context, "How does caching reduce database load?")

    answer = demo_backend.chat(messages)

    assert "DEMO MODE" in answer
    assert "reduces load on a database" in answer.lower()


def test_chat_returns_dont_know_when_no_overlap():
    context = "[source: caching]\nCaching stores a copy of expensive data."
    messages = _build_messages(context, "what is the capital of france")

    answer = demo_backend.chat(messages)

    assert "only answer questions about backend engineering" in answer.lower()


def test_chat_handles_unparseable_message():
    messages = [{"role": "user", "content": "no context or question format here"}]
    answer = demo_backend.chat(messages)
    assert "DEMO MODE" in answer
