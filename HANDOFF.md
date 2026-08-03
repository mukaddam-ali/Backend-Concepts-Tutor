# Handoff: Continue This Project on a New Machine

**If you are Claude, reading this at the start of a new chat:** this is a
continuation of an existing project. Read this whole file before doing
anything. Do not re-explain the project back to the user, do not re-plan
from scratch, and do not rebuild anything listed under "Already done" —
everything there is finished, tested, and should be treated as working
unless you find evidence otherwise. Your job is to pick up at "What's left."

## Project in one paragraph

A Q&A chatbot that answers questions about backend engineering concepts
(REST, GraphQL, databases, caching, auth, etc.) using RAG
(Retrieval-Augmented Generation). Originally built around Microsoft Foundry
Local for fully offline, on-device inference; now also supports Google
Gemini as a real hosted-LLM alternative that works in the cloud. Based on
`project guide.docx` (one directory up, if it was transferred) which
describes a Foundry Local RAG tutorial project. Lives in the
`rag-backend-tutor/` folder.

**Live status**: pushed to
[github.com/mukaddam-ali/Backend-Concepts-Tutor](https://github.com/mukaddam-ali/Backend-Concepts-Tutor)
and deployed on Render (user's own account/dashboard, not something this
repo can show you directly). The user was in the middle of switching the
Render deployment's `RAG_BACKEND` env var from `demo` to `gemini` (plus
adding a `GEMINI_API_KEY`) — check with the user whether that's done and
whether the live answers look right before assuming it still needs doing.

## Already done — do not redo

- **Full pipeline built and working**: `db.py` (SQLite), `ingest.py`
  (chunking + embedding), `retrieval.py` (cosine similarity search),
  `generate.py` (prompt assembly + answer), `main.py` (CLI), `backend.py`
  (dispatches between three implementations based on `RAG_BACKEND`:
  `foundry_client.py` real on-device Foundry Local, `gemini_backend.py`
  real hosted Google Gemini, `demo_backend.py` offline keyword-matching
  stand-in — see `backend.py`'s own docstring for the env var values).
- **34-topic knowledge base** in `docs/*.md`. Original 20: REST APIs,
  GraphQL, SQL vs NoSQL, auth, caching, CDNs, message queues, load
  balancing, WebSockets, API versioning, rate limiting, transactions/ACID,
  microservices vs monolith, DB indexing, observability, Docker, CI/CD,
  horizontal vs vertical scaling, DB replication/sharding, CORS. 14 more
  added by inspecting roadmap.sh/backend's actual node structure (the page
  is a JS-rendered diagram — plain text fetch misses it, had to pull node
  labels via `document.querySelectorAll('svg text, svg tspan, ...')` in a
  real browser) and filling genuine gaps: internet fundamentals
  (DNS/HTTP/hosting), Git/version control, database types overview
  (document/key-value/graph/column/time-series/search engines), ORMs & the
  N+1 problem, database normalization, CAP theorem, web security
  fundamentals (OWASP/TLS/hashing), testing fundamentals, architectural
  patterns (12-factor/service mesh/SOA), web servers & reverse proxies,
  resilience patterns (circuit breaker/backpressure/throttling), Kubernetes,
  serverless computing, and RAG/vectors/embeddings. Each of the 14 has a
  "Free resources" section — every single URL in it was individually
  fetched and verified to actually resolve before being included (found and
  fixed 3 stale MDN paths, replaced one dead AWS link, fixed one Redis docs
  path). Don't add a "Free resources" link without verifying it the same
  way — MDN and several other doc sites restructure URLs often enough that
  "this is a well-known site" is not sufficient confidence on its own.
- **30 automated unit tests**, all passing (`pytest tests/ -v`) — cover
  chunking, cosine similarity, the SQLite layer, the demo backend, and
  source-citation logic. These don't need Foundry Local to run.
- **Offline demo backend** (`demo_backend.py`, activated via
  `RAG_BACKEND=demo`): a pure-Python, no-native-deps stand-in (IDF-weighted
  hashing vectors + extractive sentence-picking) built specifically because
  real Foundry Local was blocked on the original dev machine (see below). It
  let the whole pipeline be exercised and validated end-to-end anyway.
  Confirmed working via 23 real test queries — see `TEST_RESULTS.md`.
- **Real bugs found and fixed during testing** (not hypothetical — actually
  hit and fixed): stopwords dominating similarity scores, hash-collision
  vector space too small once the knowledge base grew, sources shown under
  "I don't know" answers. All fixed, all covered by regression tests.
- **Documentation**: `README.md` (setup/architecture/usage),
  `PROJECT_REPORT.md` (presentation-style writeup), `TEST_RESULTS.md` (real
  test transcripts + honest failure analysis), `PRESENTATION.md` (demo
  script + talking points).
- **Web chat frontend** (`app.py` + `static/index.html`, `style.css`,
  `script.js`): a Flask API wrapping the exact same `generate.answer_query()`
  the CLI uses. `GET /api/status` and `POST /api/chat` are the two
  endpoints. Covered by `tests/test_app.py` (5 tests, included in the 30
  total). The CLI (`main.py`) was kept as-is per explicit instruction — both
  interfaces coexist, don't remove either.
- **Frontend design, v2 (current)**: a ChatGPT-style layout — left sidebar
  with New Chat + conversation history (client-side, `localStorage`-backed,
  key `ragChatState`), empty-state suggested-question chips, ChatGPT-style
  message rendering (user = right bubble, assistant = plain full-width text
  + avatar, no bubble). Theme is a shadcn/ui-style palette matching a
  reference site the user provided (`my-resume-ai-powered-resume-builder`):
  neutral grays, burnt-orange `#bf4d00` primary, `system-ui` font, 10px
  radius, light/dark via `prefers-color-scheme`. An earlier v1 design (dark
  slate + green "AI developer tool" aesthetic via the `ui-ux-pro-max` skill)
  was explicitly rejected by the user ("I didn't like the design") — don't
  revert to it. Actually driven through a real browser and verified: sent
  messages, switched between conversations, deleted one, confirmed
  `localStorage` persistence survives a page reload, confirmed the sidebar
  mobile-toggle/overlay behavior. Conversation history is UI-only — no
  conversational memory is fed back into retrieval or prompts; each question
  is still answered independently.
- **Production-readiness pass** (mobile, icons, deployment). Found and fixed
  a real bug: `ensure_knowledge_base_ready()` was only called inside
  `if __name__ == "__main__"`, which a production WSGI server never
  executes (it imports the `app` object directly) — on a real deployment
  the DB would have silently stayed empty forever. Fixed via a
  `@app.before_request` hook in `app.py`; verified by actually running the
  app through `waitress` (not just `python app.py`) and hitting
  `/api/chat` for real. Mobile responsiveness was checked directly (resize
  to 375/768px, inspect computed styles) rather than assumed — the
  sidebar breakpoint logic was already correct; added a `100dvh` fix for
  the classic mobile-toolbar viewport-height issue. Added a themed favicon
  (`static/favicon.svg` + generated PNG variants, same glyph as the header
  logo/avatar). Found and fixed a second real bug while testing Render
  deployability: the new docs' "Free resources" sections repeated the
  topic name in link titles often enough to outrank the actual explanation
  in demo-mode retrieval (caught via `generate.answer_query("What is
  Kubernetes used for?")` returning a link list instead of an
  explanation) — fixed by stripping that section before chunking
  (`ingest.strip_free_resources`), with a regression test.
- **Render deployment is set up and verified installable**, not just
  documented on faith: `requirements-render.txt` (flask + waitress only —
  `foundry-local-sdk` ships **Windows-only wheels** and cannot install on
  Linux at all, confirmed), `render.yaml` (Blueprint config,
  `RAG_BACKEND=demo` set there), `RENDER_DEPLOY.md` (guide). Actually
  built a fresh venv with only `requirements-render.txt`, ran the app
  under `waitress` in it, and hit real HTTP endpoints successfully before
  writing any of this up. Gunicorn was considered and rejected — it can't
  run natively on Windows (needs `fork()`), so it couldn't be tested on
  this dev machine; waitress is cross-platform and was actually verified.
- **User deployed to Render, found demo mode's answers too short/limited**
  (expected -- `demo_backend.chat()` returns one extracted sentence, not a
  generated response; it was only ever meant to validate the pipeline
  plumbing). Fixed by adding a **third backend**: `gemini_backend.py`
  (`RAG_BACKEND=gemini`), a real hosted LLM via Google's `google-genai`
  SDK, which works fine on Render (just an HTTPS call, no native-runtime
  constraint like Foundry Local). `backend.py` now exposes `backend.name`
  ("demo"/"gemini"/"foundry") instead of just the `is_demo` boolean --
  `main.py`, `app.py`'s `/api/status`, and `static/script.js`'s status
  pill all read this now. `generate.py`'s `SYSTEM_PROMPT` was rewritten to
  ask for thorough, multi-paragraph, example-driven answers (previously
  said "keep answers concise," which was fighting against what the user
  wanted). Chose Gemini over Groq specifically because Groq has no
  embeddings API -- would've meant two providers instead of one.
  **Important process note**: initial web-doc lookups for the google-genai
  SDK gave a wrong method name (`client.interactions.create`) that
  doesn't exist in the installed package -- caught by cross-referencing
  the PyPI README, the GitHub README, and finally the actual installed
  SDK's type signatures via `inspect.signature()` before writing any code
  against it. The real methods are `client.models.generate_content()` and
  `client.models.embed_content()`. If web docs and installed source ever
  disagree again, trust the installed source. Tests in
  `tests/test_gemini_backend.py` mock the client but construct real
  `google.genai.types` objects (not fake dicts), so the response-parsing
  logic is genuinely exercised -- what's *not* tested is real API call
  quality/behavior, which needs a real `GEMINI_API_KEY` the dev machine
  doesn't have.

## What's left — the actual next steps

**Priority 1 — confirm the live Gemini deployment actually gives good
answers.** As of the last session, the user had just switched (or was
switching) the live Render deployment to `RAG_BACKEND=gemini` with a real
`GEMINI_API_KEY`. This was never tested with a real key on the dev
machine — `tests/test_gemini_backend.py` only verifies request/response
*parsing* against mocked-but-real SDK types, not actual answer quality from
a live call. Ask the user: did you check the live site? What did an answer
actually look like? If something's off (wrong model name rejected by the
API, a parsing mismatch, a rate-limit error), the likely culprits are in
`gemini_backend.py` — see the API-verification notes above before changing
anything, and re-verify against `inspect.signature()` on the installed
`google-genai` package rather than trusting web docs (they were wrong once
already).

**Priority 2 (lower — a "nice to have," not blocking) — verify the real
Foundry Local models actually work locally.** This has never been done —
everything Foundry-Local-related was validated via the demo stand-in
because of a blocker on the original dev machine. Since Gemini now covers
the "I want real generated answers" need (and works on Render, unlike
Foundry Local), this is optional polish for the CLI's fully-offline story,
not urgent.

### The blocker (on the original machine, may not apply here)

Foundry Local's native core (`onnxruntime.dll`) requires the **Microsoft
Visual C++ 2015–2022 Redistributable (x64)**, whose installer needs
administrator rights. The original machine wasn't the user's own PC and had
no admin access, so this was never installed. Confirmed via a full Python
traceback ending in `FileNotFoundError: Could not find module
'...onnxruntime.dll' (or one of its dependencies)`. If you have admin rights
on this new machine, this should be a non-issue — just run the setup steps
below.

### Setup steps on the new machine

1. **Do not reuse the `.venv` folder if it was copied over** — Python
   virtualenvs embed absolute paths and won't work on a different machine
   path. Delete `.venv/` and recreate it:
   ```bash
   cd rag-backend-tutor
   python -m venv .venv
   .venv\Scripts\pip install -r requirements-dev.txt
   ```
2. **Install Foundry Local** (if not already installed on this machine):
   ```bash
   winget install Microsoft.FoundryLocal
   ```
3. **Install the VC++ Redistributable** (this is the step that was blocked
   before — should work fine with admin rights):
   ```bash
   winget install Microsoft.VCRedist.2015+.x64
   ```
   Approve the UAC prompt.
4. **Sanity-check Foundry Local works** before touching this project's code:
   ```bash
   foundry model list
   ```
   If this runs without a DLL error, the blocker is cleared.
5. **Run the real pipeline** (note: no `RAG_BACKEND=demo` — that flag forces
   the offline stand-in; omit it to use real Foundry Local). Either the CLI:
   ```bash
   .venv\Scripts\python.exe ingest.py
   .venv\Scripts\python.exe main.py
   ```
   or the web chat UI:
   ```bash
   .venv\Scripts\python.exe app.py
   ```
   then open `http://127.0.0.1:5000`. Both call the same
   `generate.answer_query()` — no separate ingestion step needed for the web
   UI, it ingests automatically on first request if the DB is empty.

   First run downloads two models automatically (`qwen3-embedding-0.6b`,
   `phi-3.5-mini`) — needs internet for that one-time download only.

### Once it's running, re-run the test suite

`TEST_RESULTS.md` has 23 test questions (20 in-scope, 3 out-of-scope) that
were run against the demo backend, including 2 documented false positives
that are specific to the demo backend's crude keyword matching. Re-run the
same 23 questions against the real model and update `TEST_RESULTS.md` with
real results — the 2 known-failing out-of-scope questions are the most
important ones to re-check, since a real LLM should handle them correctly
where keyword matching couldn't.

```python
import generate
result = generate.answer_query("What is the capital of France?")
print(result["answer"], result["sources"])
```

### After that, optional stretch goals (not started, not required)

- A Streamlit/Gradio or HTML+JS UI instead of CLI (mentioned as an option
  in the original project guide).
- Tune chunk size (`ingest.chunk_text`) or top-K (`retrieval.get_top_chunks`'s
  `k` parameter) if real-model answer quality suggests it.

## Don't do these things (already decided against, with reasons)

- Don't try to work around the VC++ Redistributable requirement with a
  portable DLL extraction, `/layout` extraction, or similar — all attempted
  already, all still require the same admin UAC prompt.
- Don't raise the demo backend's keyword-overlap threshold to fix the 2
  known false positives — tried, it broke other correctly-passing test
  cases. This is a documented, accepted limitation of the demo stand-in,
  not something to keep patching. Real embeddings are the actual fix.
- Don't rebuild the demo backend as a "better" fallback — it already served
  its purpose (validating the pipeline). Time is better spent getting the
  real models running now that admin access may be available.
- Don't trust web documentation for the `google-genai` SDK's exact method
  names without cross-checking the installed package — one doc page
  confidently described a `client.interactions.create()` method that does
  not exist in the actual SDK. If touching `gemini_backend.py`, verify
  against `inspect.signature(...)` on the real installed classes first.
