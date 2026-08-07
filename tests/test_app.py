import app as app_module
import backend
import db
import demo_backend


def _use_demo_backend(monkeypatch):
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


def _client():
    app_module.app.testing = True
    return app_module.app.test_client()


def test_index_serves_html(tmp_path, monkeypatch):
    _use_demo_backend(monkeypatch)
    _seed(tmp_path, monkeypatch)

    response = _client().get("/")

    assert response.status_code == 200
    assert b"Backend Concepts Tutor" in response.data


def test_status_reports_demo_backend_and_chunk_count(tmp_path, monkeypatch):
    _use_demo_backend(monkeypatch)
    monkeypatch.setattr(backend, "name", "demo")
    _seed(tmp_path, monkeypatch)

    response = _client().get("/api/status")

    assert response.status_code == 200
    data = response.get_json()
    assert data["backend"] == "demo"
    assert data["chunk_count"] == 1


def test_chat_returns_answer_and_sources(tmp_path, monkeypatch):
    _use_demo_backend(monkeypatch)
    _seed(tmp_path, monkeypatch)

    response = _client().post("/api/chat", json={"message": "How does caching reduce database load?"})

    assert response.status_code == 200
    data = response.get_json()
    assert "DEMO MODE" in data["answer"]
    assert data["sources"] == ["caching"]


def test_chat_rejects_empty_message(tmp_path, monkeypatch):
    _use_demo_backend(monkeypatch)
    _seed(tmp_path, monkeypatch)

    response = _client().post("/api/chat", json={"message": "   "})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_chat_rejects_missing_body(tmp_path, monkeypatch):
    _use_demo_backend(monkeypatch)
    _seed(tmp_path, monkeypatch)

    response = _client().post("/api/chat")

    assert response.status_code == 400


def test_source_returns_doc_content_for_a_real_source():
    response = _client().get("/api/source/caching")

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "caching"
    assert "Caching" in data["content"]


def test_source_rejects_path_traversal():
    response = _client().get("/api/source/..%2Fapp")

    assert response.status_code == 404


def test_source_rejects_unknown_name():
    response = _client().get("/api/source/not-a-real-doc")

    assert response.status_code == 404
