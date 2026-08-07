"""Thin wrapper around Foundry Local: model setup and client access."""

from foundry_local_sdk import Configuration, FoundryLocalManager
from foundry_local_sdk.exception import FoundryLocalException

EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"
# phi-3.5-mini was tried first: on this machine's CPU-only inference it took
# ~55s for even a one-word completion, and the full RAG prompt (retrieved
# context + a multi-paragraph answer) reliably hit an internal "Operation
# was cancelled" timeout before finishing.
#
# qwen2.5-1.5b was tried next -- noticeably better answer quality and
# succeeded on 22/23 real test questions -- but `foundry status` revealed
# this machine has only ~1.2 GB RAM free out of 7.3 GB total, and under
# that pressure qwen2.5-1.5b intermittently hit the same cancellation even
# on questions that had succeeded moments earlier, in a way 2 retries
# didn't reliably fix. Reliability matters more than the quality bump here,
# so settled on qwen2.5-0.5b, which stayed 100% reliable across all 23 real
# test questions (see TEST_RESULTS.md) despite smaller/shakier answers.
# If you're running this on a machine with meaningfully more free RAM,
# qwen2.5-1.5b is worth re-trying for the quality improvement.
CHAT_MODEL_ALIAS = "qwen2.5-0.5b"

_manager = None


def get_manager() -> FoundryLocalManager:
    global _manager
    if _manager is None:
        FoundryLocalManager.initialize(Configuration(app_name="rag-backend-tutor"))
        _manager = FoundryLocalManager.instance
    return _manager


def _get_ready_model(alias: str):
    manager = get_manager()
    model = manager.catalog.get_model(alias)
    if model is None:
        raise RuntimeError(f"Model alias '{alias}' not found in Foundry Local catalog.")
    if not model.is_cached:
        print(f"Downloading model '{alias}' (first run only)...")
        model.download()
    if not model.is_loaded:
        model.load()
    return model


def get_embedding_client():
    return _get_ready_model(EMBEDDING_MODEL_ALIAS).get_embedding_client()


_chat_client = None


def get_chat_client():
    global _chat_client
    if _chat_client is None:
        _chat_client = _get_ready_model(CHAT_MODEL_ALIAS).get_chat_client()
        # Left unset, completions default to a short cutoff -- not enough
        # room for the multi-paragraph, example-driven answers the system
        # prompt asks for. Cached on the client instance so this only needs
        # setting once per process, not per call.
        _chat_client.settings.max_tokens = 1024
    return _chat_client


def embed(texts: list[str]) -> list[list[float]]:
    client = get_embedding_client()
    response = client.generate_embeddings(texts)
    return [item.embedding for item in response.data]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]


# Even well within its typical completion time, this model occasionally hits
# the same "Operation was cancelled" internal timeout (observed intermittently
# on a question that succeeded in every other run) -- a transient hiccup, not
# a consistent failure, so one retry resolves it rather than surfacing an
# error to the user.
_CHAT_RETRIES = 2


def chat(messages: list[dict]) -> str:
    last_error = None
    for attempt in range(_CHAT_RETRIES + 1):
        try:
            completion = get_chat_client().complete_chat(messages)
            return completion.choices[0].message.content
        except FoundryLocalException as exc:
            last_error = exc
            if "cancelled" not in str(exc).lower():
                raise
    raise last_error
