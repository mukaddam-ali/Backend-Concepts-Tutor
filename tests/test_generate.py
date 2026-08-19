import backend
import db
import demo_backend
import generate


def _use_demo_backend(monkeypatch):
    # backend.py picks its implementation once at import time based on the
    # RAG_BACKEND env var, so tests patch its functions directly instead of
    # relying on the env var (avoids ever touching foundry_client's native
    # init, which isn't available in this test environment).
    monkeypatch.setattr(backend, "embed", demo_backend.embed)
    monkeypatch.setattr(backend, "embed_one", demo_backend.embed_one)
    monkeypatch.setattr(backend, "chat", demo_backend.chat)


def _seed(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    embedding = demo_backend.embed_one("caching stores data to reduce database load")
    db.insert_chunk(
        source="caching",
        content="Caching stores a copy of expensive data. It reduces load on a database.",
        embedding=embedding,
    )


def test_answer_query_returns_sources_when_answer_found(tmp_path, monkeypatch):
    _use_demo_backend(monkeypatch)
    _seed(tmp_path, monkeypatch)

    result = generate.answer_query("How does caching reduce database load?")

    assert "DEMO MODE" in result["answer"]
    assert result["sources"] == ["caching"]


def test_answer_query_hides_sources_when_answer_unknown(tmp_path, monkeypatch):
    _use_demo_backend(monkeypatch)
    _seed(tmp_path, monkeypatch)

    result = generate.answer_query("What is the capital of France?")

    assert "only answer questions about backend engineering" in result["answer"].lower()
    assert result["sources"] == []


def test_answer_query_empty_db_returns_no_sources(tmp_path, monkeypatch):
    _use_demo_backend(monkeypatch)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "empty.db")
    db.init_db()

    result = generate.answer_query("anything")

    assert result["sources"] == []
    assert "only answer questions about backend engineering" in result["answer"].lower()
