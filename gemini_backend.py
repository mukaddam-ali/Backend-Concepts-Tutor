"""Google Gemini-backed embedding/chat implementation.

Used when RAG_BACKEND=gemini. Requires a GEMINI_API_KEY environment variable
(free tier: https://aistudio.google.com/apikey) -- the google-genai client
picks it up automatically, no need to pass it in code.

Unlike foundry_client.py (real but blocked on this dev machine) and
demo_backend.py (keyword-matching stand-in, deliberately crude), this talks
to a real hosted LLM and gives real generated answers -- the fix for
demo mode's short, extractive, one-sentence-only responses.
"""

from google import genai

CHAT_MODEL = "gemini-flash-latest"
EMBEDDING_MODEL = "gemini-embedding-001"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def _extract_values(embedding_obj) -> list[float]:
    """Normalize the embed_content response's per-item shape.

    Verified against the installed google-genai SDK's actual type
    definitions (EmbedContentResponse.embeddings: list[ContentEmbedding],
    ContentEmbedding.values: list[float]) -- not just docs, which gave
    inconsistent/wrong method names elsewhere for this same SDK. The
    isinstance fallback below is just defensive; the real shape is always
    a list per the type annotation.
    """
    if hasattr(embedding_obj, "values"):
        return list(embedding_obj.values)
    if isinstance(embedding_obj, (list, tuple)):
        return list(embedding_obj)
    raise TypeError(f"Unexpected embedding shape from Gemini API: {type(embedding_obj)!r}")


def embed(texts: list[str]) -> list[list[float]]:
    client = _get_client()
    response = client.models.embed_content(model=EMBEDDING_MODEL, contents=texts)
    embeddings = response.embeddings
    if not isinstance(embeddings, list):
        embeddings = [embeddings]
    return [_extract_values(e) for e in embeddings]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]


def _build_prompt(messages: list[dict]) -> str:
    """Combine system + user messages into one prompt string.

    Simpler and more robust than depending on an unverified
    system_instruction parameter shape -- works with any text-completion
    call regardless of whether structured role support exists.
    """
    parts = [m["content"] for m in messages if m["content"]]
    return "\n\n".join(parts)


def chat(messages: list[dict]) -> str:
    prompt = _build_prompt(messages)
    client = _get_client()
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text
