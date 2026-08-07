"""Flask API + static chat frontend for the backend-concepts RAG tutor.

Wraps the same generate.answer_query() used by the CLI (main.py) — both
interfaces share the exact same retrieval/generation pipeline.
"""

import os
import threading
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

import backend
import db
import generate
import ingest

app = Flask(__name__, static_folder="static", static_url_path="")

DOCS_DIR = Path(__file__).parent / "docs"

_ingestion_lock = threading.Lock()


def ensure_knowledge_base_ready() -> None:
    db.init_db()
    if db.count_chunks() > 0:
        return
    with _ingestion_lock:
        # Re-check after acquiring the lock -- another thread may have
        # finished ingestion while this one was waiting, and re-running it
        # would re-embed everything and burn through the API rate limit.
        if db.count_chunks() == 0:
            print("Knowledge base is empty. Running ingestion...")
            ingest.run_ingestion()


@app.before_request
def _ensure_knowledge_base_before_request():
    # Runs under any WSGI server (waitress, gunicorn), not just `python app.py` --
    # a plain `if __name__ == "__main__"` check never fires when a production
    # server imports this module and calls the `app` object directly.
    ensure_knowledge_base_ready()


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/status")
def status():
    return jsonify(
        {
            "backend": backend.name,
            "chunk_count": db.count_chunks(),
        }
    )


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("message") or "").strip()

    if not question:
        return jsonify({"error": "message is required"}), 400

    result = generate.answer_query(question)
    return jsonify(result)


@app.get("/api/source/<name>")
def source(name: str):
    # name comes from a source citation we generated ourselves (a doc_path.stem
    # from ingest.py), but it's still attacker-controllable input from the
    # client -- resolve against DOCS_DIR and confirm the result is still
    # inside it before reading, rather than trusting the filename directly.
    path = (DOCS_DIR / f"{name}.md").resolve()
    if DOCS_DIR.resolve() not in path.parents or not path.is_file():
        abort(404)
    return jsonify({"name": name, "content": path.read_text(encoding="utf-8")})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
