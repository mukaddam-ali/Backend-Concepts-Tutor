"""Flask API + static chat frontend for the backend-concepts RAG tutor.

Wraps the same generate.answer_query() used by the CLI (main.py) — both
interfaces share the exact same retrieval/generation pipeline.
"""

from flask import Flask, jsonify, request, send_from_directory

import backend
import db
import generate
import ingest

app = Flask(__name__, static_folder="static", static_url_path="")


def ensure_knowledge_base_ready() -> None:
    db.init_db()
    if db.count_chunks() == 0:
        print("Knowledge base is empty. Running ingestion...")
        ingest.run_ingestion()


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/status")
def status():
    return jsonify(
        {
            "backend": "demo" if backend.is_demo else "foundry",
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


if __name__ == "__main__":
    ensure_knowledge_base_ready()
    app.run(debug=True, port=5000)
