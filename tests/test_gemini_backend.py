"""Offline tests for gemini_backend.py -- mock the client so these run
without a real GEMINI_API_KEY or network access, but exercise the actual
google-genai response types so the parsing logic is genuinely verified."""

from google.genai import types

import gemini_backend


class _FakeModels:
    def __init__(self, embed_response=None, generate_response=None):
        self._embed_response = embed_response
        self._generate_response = generate_response
        self.embed_calls = []
        self.generate_calls = []

    def embed_content(self, *, model, contents):
        self.embed_calls.append({"model": model, "contents": contents})
        return self._embed_response

    def generate_content(self, *, model, contents):
        self.generate_calls.append({"model": model, "contents": contents})
        return self._generate_response


class _FakeClient:
    def __init__(self, models):
        self.models = models


def _install_fake_client(monkeypatch, models):
    monkeypatch.setattr(gemini_backend, "_client", None)
    monkeypatch.setattr(gemini_backend, "_get_client", lambda: _FakeClient(models))


def test_embed_extracts_float_values_from_real_response_type(monkeypatch):
    embed_response = types.EmbedContentResponse(
        embeddings=[
            types.ContentEmbedding(values=[0.1, 0.2, 0.3]),
            types.ContentEmbedding(values=[0.4, 0.5, 0.6]),
        ]
    )
    models = _FakeModels(embed_response=embed_response)
    _install_fake_client(monkeypatch, models)

    result = gemini_backend.embed(["first text", "second text"])

    assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    assert models.embed_calls[0]["model"] == gemini_backend.EMBEDDING_MODEL
    assert models.embed_calls[0]["contents"] == ["first text", "second text"]


def test_embed_one_returns_single_vector(monkeypatch):
    embed_response = types.EmbedContentResponse(
        embeddings=[types.ContentEmbedding(values=[1.0, 2.0])]
    )
    models = _FakeModels(embed_response=embed_response)
    _install_fake_client(monkeypatch, models)

    assert gemini_backend.embed_one("hello") == [1.0, 2.0]


def test_chat_combines_system_and_user_messages_into_one_prompt(monkeypatch):
    generate_response = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="Caching stores data for fast reuse.")],
                )
            )
        ]
    )
    models = _FakeModels(generate_response=generate_response)
    _install_fake_client(monkeypatch, models)

    messages = [
        {"role": "system", "content": "You are a tutor."},
        {"role": "user", "content": "Context:\n...\n\nQuestion: What is caching?"},
    ]
    answer = gemini_backend.chat(messages)

    assert answer == "Caching stores data for fast reuse."
    call = models.generate_calls[0]
    assert call["model"] == gemini_backend.CHAT_MODEL
    assert "You are a tutor." in call["contents"]
    assert "What is caching?" in call["contents"]
