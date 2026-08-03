# Project Report: Backend Concepts RAG Tutor

## Purpose

An offline Q&A assistant that teaches backend engineering concepts by
answering questions grounded in a curated knowledge base, rather than a
general-purpose model's possibly-outdated or hallucinated recollection. It's
a local implementation of the RAG (Retrieval-Augmented Generation) pattern
described in Microsoft's ["Building Your First Local RAG Application with
Foundry Local"](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968),
using [Microsoft Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/what-is-foundry-local)
for on-device inference — no cloud API, no internet dependency at runtime,
no account or API key required.

## How it works

```
User question
     │
     ▼
[retrieval.py] embed the question, cosine-similarity search
     │            against all stored chunk embeddings in SQLite
     ▼
Top-K relevant chunks (with source doc names)
     │
     ▼
[generate.py] build a prompt: "answer only from this context,
     │           cite sources, say 'I don't know' if not covered"
     ▼
[Foundry Local chat model] generates the answer
     │
     ▼
Answer + source citations shown to the user
```

Before any of this runs, `ingest.py` does the one-time setup: split each
document in `docs/` into passage-level chunks, embed each chunk, and store
`(source, content, embedding)` in a local SQLite database.

## Knowledge base

34 topics covering core backend engineering, spanning two rounds: an
initial 20 (REST APIs, GraphQL, SQL vs NoSQL, auth, caching, CDNs, message
queues, load balancing, WebSockets, API versioning, rate limiting,
transactions/ACID, microservices vs monolith, DB indexing, observability,
Docker, CI/CD, horizontal vs vertical scaling, DB replication/sharding,
CORS), plus 14 more added by cross-referencing [roadmap.sh/backend](https://roadmap.sh/backend)'s
topic structure for gaps: internet fundamentals, Git/version control,
database types overview, ORMs & the N+1 problem, database normalization,
CAP theorem, web security fundamentals, testing fundamentals, architectural
patterns, web servers/reverse proxies, resilience patterns, Kubernetes,
serverless computing, and RAG/vectors/embeddings. Each of the 14 includes a
"Free resources" section — every link individually verified to actually
resolve, not assumed.

## Design decisions

- **Models**: `qwen3-embedding-0.6b` for embeddings, `phi-3.5-mini` for
  chat — both small enough to respond quickly on a laptop CPU without a GPU.
- **Chunking**: paragraphs grouped two at a time (~1–3 paragraphs per chunk),
  matching the passage-level granularity RAG typically expects — small
  enough to be topically focused, large enough to retain context.
- **Retrieval**: brute-force cosine similarity over all stored vectors,
  computed in Python. Appropriate at this scale (dozens to low hundreds of
  chunks); a real vector index (e.g. FAISS, or a SQL vector extension) would
  be needed well before this reaches production scale.
- **Prompting**: the system prompt explicitly instructs the model to answer
  only from retrieved context, cite the source document, and say "I don't
  know" rather than guess — directly targeting hallucination, RAG's central
  value proposition.
- **Swappable backend**: `backend.py` abstracts embedding/chat behind a
  common interface, with two implementations — real Foundry Local
  (`foundry_client.py`) and a pure-Python offline stand-in
  (`demo_backend.py`, via `RAG_BACKEND=demo`) with no native dependencies.
  This let the full pipeline be built, tested, and validated end-to-end
  before Foundry Local's runtime dependency was available on the
  development machine (see Blockers below).

## Testing

23 test queries (20 in-scope, 3 out-of-scope) were run against the full
pipeline in demo mode. Full results and a specific failure analysis are in
[TEST_RESULTS.md](TEST_RESULTS.md). Summary: retrieval correctly found the
right document for all 20 in-scope questions; 1 of 3 out-of-scope questions
correctly triggered the "I don't know" fallback, and 2 produced false-
positive answers due to a limitation specific to the demo backend's
keyword-matching approach (see TEST_RESULTS.md for the detailed root-cause
analysis; the 20-topic KB has since grown to 34, see Knowledge base above).
Separately, 26 automated unit tests cover chunking, cosine similarity, the
SQLite layer, the demo backend, source-citation logic, and the Flask API
(`pytest tests/ -v`).

## Known limitations

- **Foundry Local is unverified on this machine.** Its native runtime
  (`onnxruntime.dll`) requires the Microsoft Visual C++ 2015–2022
  Redistributable, whose installer needs administrator rights not available
  in this environment. The code is written against Foundry Local's actual
  SDK API and runs correctly up to that exact dependency (confirmed via a
  full traceback), but real embedding/generation quality has not yet been
  measured — only the demo backend's has, and that's explicitly not a stand-
  in for real model quality.
- **Retrieval is brute-force**, not indexed — fine for this knowledge base's
  size, would need a real vector index at larger scale.
- **Single-machine, single-user** — no concurrency handling.
- **Demo mode's false-positive rate on out-of-scope questions** (see Testing
  above) is a known, documented gap specific to lexical keyword matching,
  not expected to reproduce with a real LLM's actual language understanding.

## Next steps

1. Install the VC++ Redistributable (requires admin rights) and re-run the
   23-query test suite against real Foundry Local models — the 2 documented
   false positives are the first thing to re-check.
2. If retrieval or answer quality needs tuning, the two knobs are chunk size
   (`ingest.chunk_text`) and top-K (`retrieval.get_top_chunks`'s `k`
   parameter, currently 3).
3. Optional stretch goals per the original project guide: a Streamlit/Gradio
   UI instead of CLI, or source-citation formatting in the answer text
   itself rather than a separate line.
