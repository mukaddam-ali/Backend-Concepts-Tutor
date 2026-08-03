"""CLI entry point for the local backend-concepts RAG tutor."""

import backend
import db
import generate
import ingest


def ensure_knowledge_base_ready() -> None:
    db.init_db()
    if db.count_chunks() == 0:
        print("Knowledge base is empty. Running ingestion...\n")
        ingest.run_ingestion()
        print()


def main() -> None:
    print("=== Backend Concepts RAG Tutor ===")
    if backend.name == "demo":
        print(
            "Running in DEMO MODE (RAG_BACKEND=demo): keyword-based retrieval, "
            "no real embeddings or LLM. Unset RAG_BACKEND to use Foundry Local."
        )
    elif backend.name == "gemini":
        print("Backend: Google Gemini (RAG_BACKEND=gemini, real hosted LLM)")
    else:
        print("Backend: Foundry Local (offline on-device inference)")
    print("Ask a question about backend engineering. Type 'exit' to quit.\n")

    ensure_knowledge_base_ready()

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        result = generate.answer_query(question)
        print(f"\nTutor: {result['answer']}")
        if result["sources"]:
            print(f"(sources: {', '.join(result['sources'])})")
        print()


if __name__ == "__main__":
    main()
