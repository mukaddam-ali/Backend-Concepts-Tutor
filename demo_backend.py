"""Offline, pure-Python stand-in for Foundry Local.

Uses a hashing-based bag-of-words vector instead of real semantic embeddings,
and picks the most keyword-overlapping sentence instead of generating an
answer with an LLM. This exists only so the retrieval pipeline can be
exercised end-to-end while Foundry Local's native runtime is unavailable
(see README's "VC++ Redistributable" note). It is not a substitute for real
embeddings or real generation -- switch RAG_BACKEND back to "foundry" once
that dependency is installed.
"""

import hashlib
import math
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"

# Large enough that hash collisions between unrelated terms stay rare even as
# the knowledge base grows to a few hundred unique keywords (a small VECTOR_DIM
# collapses distinct terms into the same bucket, making cosine similarity
# nearly random -- this was tested and confirmed as the cause of bad retrieval
# results before this was bumped up from 256).
VECTOR_DIM = 8192

# Overrides retrieval.MIN_SIMILARITY, which is calibrated for real embedding
# models (0.45) -- these hashing vectors score on a much lower, narrower
# scale (measured: a genuinely in-scope question like "What is CORS?" only
# scores ~0.27; applying the real-embedding threshold unchanged made this
# backend wrongly decline almost everything). Set low enough to only filter
# out true zero-overlap queries (e.g. "capital of France" scores 0.0 here) --
# chat() below does its own independent keyword-overlap check per passage,
# which is the actual, already-tested decline mechanism for this backend.
MIN_SIMILARITY = 0.05

# Excluded from both the embed() vectors and chat()'s keyword-overlap matching.
# Without this, common words dominate the hashing vector (making cosine
# similarity nearly meaningless once the corpus has more than a few docs) and
# cause false-positive keyword matches (e.g. "of" matching everything), which
# stops the "I don't know" fallback from ever triggering.
_STOPWORDS = frozenset(
    """
    a an the this that these those is are was were be been being
    of in on at to for with from by as and or but if then so than
    it its it's what who whom which how why when where do does did
    can could will would should may might must not no
    """.split()
)


def _stem(token: str) -> str:
    """Crude plural stripping (no real stemmer, no dependencies) so e.g.
    "websockets" in a doc matches "websocket" in a question."""
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and token.endswith("es") and token[-3] in "sxz":
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _tokenize(text: str) -> list[str]:
    return [_stem(t) for t in re.findall(r"[a-z0-9]+", text.lower())]


def _content_tokens(text: str) -> list[str]:
    """Tokens with stopwords removed, keeping repeats (term frequency matters
    for the embedding vector, unlike the overlap-counting in chat())."""
    return [t for t in _tokenize(text) if t not in _STOPWORDS]


def _keywords(text: str) -> set[str]:
    return set(_content_tokens(text))


def _hash_index(token: str) -> int:
    digest = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(digest, 16) % VECTOR_DIM


_idf_cache: dict[str, float] | None = None


def _compute_idf() -> dict[str, float]:
    """Inverse document frequency across docs/*.md, so generic terms that show
    up in most documents (e.g. "server", "request") don't drown out rare,
    topic-specific ones (e.g. "websocket", "sharding") in the similarity score.
    Without this, cosine similarity over plain term counts ranked irrelevant
    chunks above the actually-relevant one once the knowledge base grew past
    a handful of docs (confirmed while testing retrieval quality)."""
    doc_paths = list(DOCS_DIR.glob("*.md"))
    if not doc_paths:
        return {}

    doc_frequency: dict[str, int] = {}
    for path in doc_paths:
        for term in _keywords(path.read_text(encoding="utf-8")):
            doc_frequency[term] = doc_frequency.get(term, 0) + 1

    n_docs = len(doc_paths)
    return {term: math.log((n_docs + 1) / (df + 1)) + 1.0 for term, df in doc_frequency.items()}


def _get_idf() -> dict[str, float]:
    global _idf_cache
    if _idf_cache is None:
        _idf_cache = _compute_idf()
    return _idf_cache


def _vectorize(text: str) -> list[float]:
    idf = _get_idf()
    vector = [0.0] * VECTOR_DIM
    for token in _content_tokens(text):
        vector[_hash_index(token)] += idf.get(token, 1.0)

    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def embed(texts: list[str]) -> list[list[float]]:
    return [_vectorize(t) for t in texts]


def embed_one(text: str) -> list[float]:
    return _vectorize(text)


_CONTEXT_RE = re.compile(r"Context:\n(.*?)\n\nQuestion:", re.S)
_QUESTION_RE = re.compile(r"Question:\s*(.*)", re.S)
_PASSAGE_RE = re.compile(r"\[source: (.*?)\]\n(.*?)(?=\n\n\[source:|\Z)", re.S)

# How many of the retrieved passages to show in full, ranked by keyword
# overlap with the question. Showing the whole passage(s) rather than a
# single cherry-picked sentence gives a much more complete-looking answer
# on the public demo (which has no real model at all) while staying pure
# search -- no generation, no LLM, nothing invented.
_MAX_PASSAGES_SHOWN = 4


def chat(messages: list[dict]) -> str:
    """Extractive stand-in for a real chat model.

    Parses the same "Context:\\n...\\n\\nQuestion: ..." user message that
    generate.py builds, and returns the full text of the retrieved
    passage(s) with the most keyword overlap with the question -- verbatim
    from the knowledge base, never rewritten or summarized, since there's
    no real model here to do that safely.
    """
    user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

    context_match = _CONTEXT_RE.search(user_message)
    question_match = _QUESTION_RE.search(user_message)
    if not context_match or not question_match:
        return "[DEMO MODE] Could not parse context/question from the prompt."

    question = question_match.group(1).strip()
    query_tokens = _keywords(question)

    passages = _PASSAGE_RE.findall(context_match.group(1))
    if not passages:
        return "[DEMO MODE] No context passages found."

    scored = [
        (source, content, len(query_tokens & _keywords(content)))
        for source, content in passages
    ]
    scored.sort(key=lambda triple: triple[2], reverse=True)

    if scored[0][2] <= 0:
        return "I don't have information about that in my knowledge base."

    shown = [
        f"**{source}**\n\n{content.strip()}"
        for source, content, score in scored[:_MAX_PASSAGES_SHOWN]
        if score > 0
    ]

    return "[DEMO MODE - keyword retrieval only, no real LLM]\n" + "\n\n---\n\n".join(shown)
