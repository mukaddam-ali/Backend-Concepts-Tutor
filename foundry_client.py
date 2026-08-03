"""Thin wrapper around Foundry Local: model setup and client access."""

from foundry_local_sdk import Configuration, FoundryLocalManager

EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"
CHAT_MODEL_ALIAS = "phi-3.5-mini"

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


def get_chat_client():
    return _get_ready_model(CHAT_MODEL_ALIAS).get_chat_client()


def embed(texts: list[str]) -> list[list[float]]:
    client = get_embedding_client()
    response = client.generate_embeddings(texts)
    return [item.embedding for item in response.data]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]


def chat(messages: list[dict]) -> str:
    completion = get_chat_client().complete_chat(messages)
    return completion.choices[0].message.content
