# Backend Concepts RAG Tutor

An offline Q&A chatbot that answers questions about core backend engineering
concepts, using Retrieval-Augmented Generation (RAG) and
[Microsoft Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/what-is-foundry-local)
for fully on-device LLM inference. No internet connection or cloud account is
needed at runtime.

**34 topics** across: REST APIs, GraphQL, SQL vs NoSQL, database types
(document/key-value/graph/column/time-series/search), ORMs & the N+1
problem, database normalization, CAP theorem, indexing, replication &
sharding, transactions & ACID, auth, caching, CDNs, message queues, load
balancing, WebSockets, API design & versioning, rate limiting,
microservices vs monolith, architectural patterns (12-factor, service
mesh), observability, containerization, Kubernetes, serverless, CI/CD,
horizontal vs vertical scaling, CORS, web security fundamentals (OWASP,
TLS, hashing), testing fundamentals, web servers & reverse proxies,
resilience patterns (circuit breakers, backpressure), internet
fundamentals (DNS/HTTP/hosting), version control with Git, and RAG/vectors/
embeddings. Topic selection is informed by [roadmap.sh/backend](https://roadmap.sh/backend)'s
structure, and each doc added from that pass links free, verified
resources for further reading.

See [PROJECT_REPORT.md](PROJECT_REPORT.md) for a presentation-style writeup,
[TEST_RESULTS.md](TEST_RESULTS.md) for real test transcripts and findings,
and [PRESENTATION.md](PRESENTATION.md) for a demo script.

## How it works

1. `docs/*.md` — a small knowledge base of backend-concept articles.
2. `ingest.py` — splits each doc into passage-level chunks, embeds each chunk,
   and stores `(source, content, embedding)` rows in a local SQLite database
   (`knowledge.db`).
3. `retrieval.py` — embeds a user's question and does a brute-force cosine
   similarity search over the stored embeddings to find the top-K most
   relevant chunks.
4. `generate.py` — builds a prompt from the retrieved chunks (instructing the
   model to answer only from context, cite the source doc, and say "I don't
   know" if the answer isn't covered) and calls the chat model.
5. Two interfaces share the same pipeline:
   - `main.py` — a CLI loop: ask a question, get an answer, repeat.
   - `app.py` — a Flask API + web chat UI (`static/`), see "Web frontend"
     below.

Steps 2–4 call through `backend.py`, which picks the actual embedding/chat
implementation:

- **`foundry_client.py`** (default) — real embeddings and generation via
  Microsoft Foundry Local, fully on-device.
- **`gemini_backend.py`** (`RAG_BACKEND=gemini`) — real embeddings and
  generation via Google's hosted Gemini API. Real generated answers (long,
  well-explained, not just extracted sentences), and works anywhere with
  internet access, including Render. Needs a `GEMINI_API_KEY`. See "Gemini
  backend" below.
- **`demo_backend.py`** (`RAG_BACKEND=demo`) — a pure-Python stand-in with no
  native dependencies: hashing-based keyword vectors instead of real
  embeddings, and extractive sentence-picking instead of real generation.
  Short, literal-keyword-match answers only. See "Demo mode" below.

## Setup

### 1. Install Foundry Local

Foundry Local is a separate runtime from the Python SDK — it must be
installed on the machine (not just `pip install`-ed):

```bash
winget install Microsoft.FoundryLocal
```

**Known issue on this machine:** Foundry Local's native core depends on
`onnxruntime.dll`, which in turn requires the **Microsoft Visual C++
2015–2022 Redistributable (x64)**. If `foundry model list` (or running this
app) fails with `FileNotFoundError: Could not find module '...onnxruntime.dll'
(or one of its dependencies)`, that redistributable is missing. Install it
with:

```bash
winget install Microsoft.VCRedist.2015+.x64
```

This installer requires **administrator rights** (a UAC prompt). On a machine
where you don't have admin access, ask whoever administers it to run that one
command — no other workaround exists, since both the `foundry` CLI daemon and
the Python SDK's embedded native core link the same DLL.

### 2. Set up the Python environment

```bash
cd rag-backend-tutor
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 3. Run

```bash
.venv\Scripts\python main.py
```

On first run, it will automatically download the embedding model
(`qwen3-embedding-0.6b`) and chat model (`phi-3.5-mini`) via Foundry Local
(requires internet for this one-time download only), ingest `docs/*.md` into
`knowledge.db`, then start the Q&A loop.

To re-run ingestion manually (e.g. after editing `docs/`):

```bash
.venv\Scripts\python ingest.py
```

## Web frontend

A chat-style web UI is available as an alternative to the CLI, sharing the
exact same `generate.answer_query()` pipeline underneath:

```bash
.venv\Scripts\python app.py
```

Then open `http://127.0.0.1:5000`. It's a Flask API (`app.py`) serving a
static HTML/JS/Tailwind chat UI (`static/`) with a ChatGPT-style layout:

- Left sidebar with a **New Chat** button and a list of past conversations
  (stored in the browser's `localStorage`, titled after each conversation's
  first message).
- Empty-state suggested-question chips (randomized from a pool of topics) to
  kick off a conversation.
- ChatGPT-style message layout: user messages as right-aligned bubbles,
  assistant messages as plain full-width text with an avatar, no bubble.
- Conversations persist across page reloads and can be deleted individually.

Theme: a shadcn/ui-style palette (neutral grays, burnt-orange `#bf4d00`
primary/accent, `system-ui` font stack, 10px border radius) matching a
reference site the user provided, with light/dark variants following the
OS's `prefers-color-scheme`.

The status pill in the sidebar footer shows which backend is active (Foundry
Local vs demo) and how many chunks are loaded. `RAG_BACKEND=demo` works the
same way here as with the CLI. Conversation history is a UI/organizational
feature only — each question is still answered independently by
`generate.answer_query()`, with no conversational memory fed back into
retrieval or the prompt.

API surface, if building against it directly:
- `GET /api/status` → `{backend, chunk_count}`
- `POST /api/chat` with `{"message": "..."}` → `{answer, sources}`

The UI is responsive (mobile/tablet/desktop breakpoints, a collapsible
sidebar with a mobile overlay/hamburger toggle) and uses `100dvh` rather
than `100vh` so content isn't cut off behind mobile browser toolbars. A
themed favicon (`static/favicon.svg` + PNG variants) reuses the same
circle-and-cross glyph as the header logo and chat avatar.

On Windows, `run.bat` / `run_demo.bat` do the same thing as the commands
above without needing to remember `cmd` vs PowerShell environment-variable
syntax.

## Deploying

`run.bat`/`app.py` are for local use. To put this online, see
[RENDER_DEPLOY.md](RENDER_DEPLOY.md). Foundry Local itself can't run there
(on-device runtime, no Linux build) — but `RAG_BACKEND=gemini` works fine on
Render, since it's just an HTTPS API call. Use `RAG_BACKEND=demo` only if you
don't want to set up a Gemini API key.

## Gemini backend (real answers, works on Render)

Set `RAG_BACKEND=gemini` and a `GEMINI_API_KEY` environment variable to use
a real hosted LLM instead of the extractive demo stand-in — proper
multi-paragraph, well-explained answers, not single sentences.

**Get a free API key:** [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
(no credit card needed for the free tier). Treat it like a password —
**never commit it to git or paste it into a chat**. Set it as an environment
variable only:

```bash
# Windows cmd
set RAG_BACKEND=gemini
set GEMINI_API_KEY=your-key-here
.venv\Scripts\python.exe app.py

# PowerShell
$env:RAG_BACKEND = "gemini"
$env:GEMINI_API_KEY = "your-key-here"
.venv\Scripts\python.exe app.py
```

On Render, add both as **Environment Variables** in the dashboard instead
(Settings → Environment) rather than putting them in any file that gets
committed.

Uses `gemini-2.5-flash` for chat and `gemini-embedding-001` for embeddings
(see `gemini_backend.py`). `generate.py`'s system prompt was rewritten to
ask for thorough, example-driven, multi-paragraph answers — grounded in the
retrieved context, but allowed to use general backend knowledge to explain
and elaborate, rather than restricted to quoting the docs verbatim.

## Demo mode (no Foundry Local required)

If Foundry Local isn't runnable yet (e.g. the VC++ Redistributable above
isn't installed), set `RAG_BACKEND=demo` to exercise the full pipeline with
`demo_backend.py` instead — real chunking, real SQLite storage, real
retrieval, just no real embeddings or LLM:

```bash
# Windows cmd
set RAG_BACKEND=demo
.venv\Scripts\python ingest.py
.venv\Scripts\python main.py

# PowerShell
$env:RAG_BACKEND = "demo"
.venv\Scripts\python ingest.py
.venv\Scripts\python main.py

# bash
RAG_BACKEND=demo .venv/Scripts/python ingest.py
RAG_BACKEND=demo .venv/Scripts/python main.py
```

Demo mode uses an IDF-weighted hashing bag-of-words vector for "embeddings"
(so retrieval is lexical/keyword overlap, not real semantic similarity) and
extractive sentence-picking for "generation" (so answers are quoted straight
from a doc, not composed by a model). It's useful for confirming the
chunking → storage → retrieval → prompt-assembly pipeline works, but it is
**not** a substitute for the real models — unset `RAG_BACKEND` (or set it to
`foundry`) once Foundry Local can actually run.

Note: IDF weighting (down-weighting terms that appear in most docs, e.g.
"server", "request") was added after testing showed plain term-frequency
vectors ranked irrelevant chunks above the actually-relevant one once the
knowledge base grew past ~10 docs. Even with that fix, demo mode occasionally
pulls in a partially-irrelevant chunk alongside the correct one (it's exact
keyword matching, not real semantic understanding) — the extractive `chat()`
step usually still picks the right sentence from whichever retrieved chunk
is actually relevant, but don't expect this to behave like a real model.

## Project structure

```
rag-backend-tutor/
├── docs/                # Knowledge base (markdown source documents)
├── db.py                # SQLite schema + helpers
├── backend.py            # Picks foundry/gemini/demo backend (RAG_BACKEND env var)
├── foundry_client.py    # Real Foundry Local model setup (embedding + chat clients)
├── gemini_backend.py     # Real Google Gemini API (embedding + chat), needs GEMINI_API_KEY
├── demo_backend.py       # Offline stand-in: hashing vectors + extractive "chat"
├── ingest.py             # Chunk + embed + store pipeline
├── retrieval.py          # get_top_chunks(query, k) via cosine similarity
├── generate.py            # answer_query(question) — retrieval + chat call
├── main.py               # CLI entry point
├── app.py                # Flask API + web chat UI entry point
├── static/               # index.html, style.css, script.js, favicon assets
├── run.bat, run_demo.bat # Windows one-liners for `python app.py` (with/without demo mode)
├── requirements.txt      # Full deps (includes Windows-only foundry-local-sdk)
├── requirements-render.txt  # Lean deps for cloud/Linux deployment (no Foundry SDK)
├── requirements-dev.txt  # adds pytest
├── render.yaml           # Render Blueprint config
├── RENDER_DEPLOY.md      # Deployment guide
├── tests/                # unit tests (all pass without Foundry Local)
└── knowledge.db          # created on first ingestion run
```

## Tests

The full pipeline's *logic* is covered by unit tests that don't need Foundry
Local running, real network access, or a real API key — chunking, cosine
similarity, the SQLite layer, the demo backend's vectors/extraction,
`answer_query`'s source-citation behavior, and `gemini_backend`'s
request/response parsing (mocked against the actual `google-genai` SDK
types, not a fake shape, so the parsing logic is genuinely exercised):

```bash
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest tests/ -v
```

All 30 tests pass as of this writing (includes `tests/test_app.py` for the
Flask API). What's *not* covered by automated tests — because it requires a
real network call and a real API key/model — is actual answer quality from
Foundry Local or Gemini. The `gemini_backend.py` tests verify the
request/response *parsing* is correct against real SDK types, not that a
live call produces a good answer. Verify that manually once you have a key
or a runnable Foundry Local: ask a mix of in-scope and out-of-scope
questions through `main.py` and confirm retrieval finds the right doc and
the fallback message
appears for out-of-scope ones.

## Design decisions

- **Models**: `qwen3-embedding-0.6b` for embeddings, `phi-3.5-mini` for chat
  — both small enough to run responsively on a laptop CPU.
- **Chunking**: paragraphs are grouped two at a time to form passage-level
  chunks (~1–3 paragraphs), matching what the RAG pattern typically expects.
- **Retrieval**: brute-force cosine similarity over all stored vectors in
  Python. Fine at this scale (a few dozen chunks); would need an actual
  vector index for a much larger document set.
- **Prompting**: the system prompt instructs the model to answer only from
  retrieved context, cite the source document, and explicitly say it doesn't
  know rather than guessing — reducing hallucination.

## Known limitations

- Single-machine, single-user — no concurrency handling.
- Retrieval is brute-force, not indexed — won't scale past a few hundred
  chunks without a real vector index.
- Foundry Local's embedding/generation quality is unverified on this machine
  pending the VC++ Redistributable install — the demo backend confirms the
  *pipeline* works, not the real model output.
