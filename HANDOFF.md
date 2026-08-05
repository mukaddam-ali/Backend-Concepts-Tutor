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

## ⚠️ Constraint that changed everything (2026-08-03): must run fully offline, no cloud LLM at all

The professor requires this project to run **fully offline with a real
on-device LLM** — not just "no explicit API key," but no calls to Gemini,
ChatGPT, or any cloud model at all — and to answer *only* from a fixed,
bounded set of local files (our 34 `docs/*.md` files satisfy "read from a
bounded set of ~20+ files and answer only from those" — no content swap
needed, just confirm retrieval never leaves `docs/`, which it doesn't).

**This makes `gemini_backend.py` and the whole Render/Gemini saga below
(section "Live status as of 2026-08-02") no longer the priority** — it's
kept as history because the bugs fixed there (batching, ingestion
atomicity, the `.strip().lower()` fix) are real and still apply to
`ingest.py`/`app.py`/`backend.py` regardless of which backend is active.
But the assistant now needs to actually run on **Foundry Local**
(`RAG_BACKEND` unset/anything other than `demo`/`gemini`), not Gemini.
**Foundry Local cannot run on Render** (it's an on-device runtime, not an
HTTPS API — confirmed, see "Render deployment" section below) — if the
professor needs to see it live rather than in a local demo, that's an
open question to raise with them, not something to solve in code.

**Status as of 2026-08-04: project is functionally complete.** Foundry
Local runs end-to-end, fully offline, and the real 23-question test suite
passes **23/23** (20/20 in-scope answered correctly, 3/3 out-of-scope
correctly declined) — see `TEST_RESULTS.md` for the real transcripts. Full
story in "Already done" below under "Real Foundry Local pipeline verified
end-to-end" and "Out-of-scope hallucination fixed, 23/23 achieved" — read
both before touching `foundry_client.py`, `retrieval.py`, or `generate.py`'s
`SYSTEM_PROMPT` again. The user decided to **stop maintaining the Render
deployment** (Foundry Local can't run there anyway) — it's not part of what
gets submitted/graded going forward; no further Render work is expected
unless the user brings it up again.

## Live status as of 2026-08-02 (Render/Gemini — now secondary, kept for history)

Pushed to
[github.com/mukaddam-ali/Backend-Concepts-Tutor](https://github.com/mukaddam-ali/Backend-Concepts-Tutor)
and deployed on Render (user's own account/dashboard, not something this
repo can show you directly). Currently running `RAG_BACKEND=demo` —
**deliberately reverted back from `gemini`, not a regression**. Full story:

1. Switching to `gemini` initially crashed the whole site (500 on every
   route, including static files) because `RAG_BACKEND`'s value in
   Render's dashboard silently didn't match `"gemini"` at various points
   (missing `GEMINI_API_KEY`, then the var disappearing from the
   dashboard entirely at one point, then a stray `render.yaml` Blueprint
   default of `demo` possibly reconciling it back) — `backend.py`'s
   `_BACKEND_NAME` comparison now does `.strip().lower()` to guard
   against invisible whitespace too, but the dashboard var itself is the
   actual source of truth for this service, not `render.yaml`.
2. Once that was sorted, hit `google.genai.errors.ClientError: 404` —
   `gemini-2.5-flash` was deprecated for new users. Fixed by switching
   `gemini_backend.CHAT_MODEL` to the `"gemini-flash-latest"` alias
   instead of a pinned version, specifically to avoid this exact class of
   breakage recurring.
3. Then hit `429 RESOURCE_EXHAUSTED` on `embed_content` (free tier,
   `gemini-embedding-001`, limit 100). Root cause was two compounding
   bugs, both fixed:
   - `app.py`'s `@app.before_request` hook checked
     `db.count_chunks() == 0` with **no locking**, so concurrent requests
     on first page load could each see an empty DB and kick off a full
     parallel re-ingestion. Fixed with a `threading.Lock` in
     `ensure_knowledge_base_ready()` (double-checked after acquiring the
     lock).
   - `ingest.run_ingestion()` made **one `embed()` call per document**
     (34+ calls). Refactored to batch all chunks across all docs into
     calls of `_EMBED_BATCH_SIZE = 90` instead, cutting total requests to
     a handful.
   - Neither fix was enough on its own: Render's disk is **ephemeral**,
     so every restart/redeploy wipes `knowledge.db` and forces a full
     re-ingestion from scratch. Repeated testing/redeploying in the same
     session stacked enough embedding calls to exhaust what looks like a
     very low daily quota for `gemini-embedding-001` on this Google Cloud
     project's free tier (Google labels the quota "PerMinute" but
     behavior strongly suggested a longer-lived — likely daily — window;
     confirmed via the AI Studio Usage page showing only ~70 total
     requests but still hitting 429 on a fresh restart).
   - There's also a **latent bug, not yet fixed**: if `run_ingestion()`
     raises partway through (e.g. a later batch hits a 429), earlier
     batches already committed to `knowledge.db` stay there, and
     `count_chunks() > 0` means the `before_request` guard never retries
     — silently leaving the knowledge base permanently incomplete. This
     is exactly what caused a real observed symptom: the live gemini
     deployment answered "I don't have information about that" for
     "When should I use microservices instead of a monolith?" even
     though `docs/microservices-vs-monolith.md` exists and clearly
     covers it — that doc's chunks were likely never embedded because an
     earlier batch failed first. **Do not re-enable `gemini` mode without
     either fixing this (e.g. don't commit partial results, or delete
     `knowledge.db` on any ingestion failure) or verifying a full clean
     ingestion completed (check `chunk_count` at `/api/status` against
     an expected total).**
4. Reverted `RAG_BACKEND` to `demo` (both in the Render dashboard, which
   is authoritative, and in `render.yaml` as the matching default) so the
   site is usable again while waiting for the Gemini quota to reset.

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

**Nothing blocking.** The core deliverable works: fully offline, real
on-device LLM, answers only from `docs/*.md`, 23/23 on the real test suite.
Remaining items are polish/optional, not required to consider this done:

- **Optional quality upgrade**: `qwen2.5-0.5b` is reliable but small
  (occasionally repetitive phrasing). `qwen2.5-1.5b` gives noticeably
  better answers but was reverted due to intermittent timeouts on *this*
  machine specifically (only ~1.2GB RAM free — see "Real Foundry Local
  pipeline verified end-to-end" below). If a future session runs on a
  machine with meaningfully more free RAM, re-try `qwen2.5-1.5b` in
  `foundry_client.CHAT_MODEL_ALIAS` and re-run the full 23-question suite
  (script pattern: warm `foundry_client.get_chat_client()` once, then loop
  `generate.answer_query(...)` over the 23 questions from
  `TEST_RESULTS.md`, checking none raise `FoundryLocalException`).
- **`app.py` first-load latency isn't surfaced to the user**: when
  `knowledge.db` doesn't exist yet, the *first* HTTP request of any kind
  blocks synchronously for as long as full ingestion takes (confirmed:
  several minutes for 219 chunks on this machine) with no loading
  indicator — the browser just hangs. Not a bug (ingestion completes
  correctly), but a rough edge if the user demos this cold. A nice-to-have
  fix would be showing a "warming up" state in `static/script.js`, or
  running ingestion at process startup instead of lazily on first request.
- **Render deployment**: user decided to stop maintaining it (see above).
  If they ask about it later, it's still live on `demo` mode last we
  checked — up to the user whether to suspend/delete it via their Render
  dashboard.

### Foundry Local setup — already done on this machine, keep for reference

If a future session runs on yet another new machine, repeat this:

1. Recreate `.venv` (don't reuse a copied one — embeds absolute paths):
   ```bash
   python -m venv .venv
   .venv\Scripts\pip install -r requirements-dev.txt
   ```
   Note: plain `python`/`py` may not exist even after this if only the
   Windows Store execution-alias stub is present (confirmed on this
   machine — it printed "Python was not found; run without arguments to
   install from the Microsoft Store" despite `python` resolving to a
   *real* path). Install a real interpreter first if so:
   ```bash
   winget install Python.Python.3.12
   ```
   then use the full path, e.g.
   `C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe`.
2. Install Foundry Local:
   ```bash
   winget install Microsoft.FoundryLocal
   ```
   (On this machine the VC++ Redistributable dependency was already
   satisfied automatically — the admin-rights blocker documented on the
   *original* dev machine did not recur here. If it does recur elsewhere:
   `winget install Microsoft.VCRedist.2015+.x64`, approve the UAC prompt.)
3. Sanity check: `foundry model list` should print a model table with no
   DLL error.
4. Run the real pipeline (no `RAG_BACKEND` set — that's what selects
   Foundry Local by default):
   ```bash
   .venv\Scripts\python.exe ingest.py
   .venv\Scripts\python.exe main.py
   ```
   or `app.py` for the web UI. First run downloads
   `qwen3-embedding-0.6b` and the configured chat model alias — needs
   internet for that one-time download only.

### Real Foundry Local pipeline verified end-to-end (2026-08-03) — read before touching `foundry_client.py` or `ingest.py`'s batch size

This had never actually been run before this session — everything
Foundry-Local-related was previously validated only via the demo stand-in,
because of an admin-rights blocker on the *original* dev machine (see
above; did not recur on this machine). Two real bugs were found and fixed
getting a genuine end-to-end answer, both specific to **local CPU
inference**, distinct from the Gemini rate-limit issues above:

- `ingest.py`'s `_EMBED_BATCH_SIZE` was `90` (sized to cut down Gemini API
  call *count* against a cloud rate limit). Against local Foundry Local
  CPU inference this reliably raised
  `foundry_local_sdk.exception.FoundryLocalException: ... Operation was
  cancelled` — an internal timeout, not something configurable via the SDK
  (checked `ChatClientSettings`, `Configuration`, `core_interop.py`; no
  exposed timeout parameter). Measured: 30 texts alone took over a minute.
  **Lowered to `20`.** If you crank this back up for any reason, re-verify
  it doesn't reintroduce the cancellation on whatever hardware you're on.
- `foundry_client.CHAT_MODEL_ALIAS` was `"phi-3.5-mini"`. On this machine's
  CPU, a **one-word** completion took ~55 seconds, and the full RAG prompt
  (retrieved context + the multi-paragraph answer `SYSTEM_PROMPT` asks for)
  consistently hit the same "Operation was cancelled" timeout before
  finishing. **Swapped to `"qwen2.5-0.5b"`**, which completes the same full
  RAG prompt in single digits to ~40s and does not hit the timeout. This is
  a real speed/quality tradeoff, not a free win — see Priority 1 above.

Verified via an actual `ingest.py` run (`219 chunks stored across 34
documents`, all genuine `qwen3-embedding-0.6b` embeddings, no shortcuts)
and a real `generate.answer_query("How does RAG (Retrieval-Augmented
Generation) work?")` call, which returned a real generated multi-paragraph
answer correctly sourced from `rag-vectors-embeddings` — confirming
retrieval, generation, and source-citation all work with zero network
calls at inference time. Also confirmed both real entry points work, not
just the raw function: `main.py` (piped a real question through the CLI)
and `app.py` (started the Flask dev server, drove it through an actual
browser, clicked a suggested-question chip, got a real generated answer
back in the UI).

### Out-of-scope hallucination fixed, 23/23 achieved (2026-08-04)

Running the real `TEST_RESULTS.md` 23-question suite against the real
pipeline for the first time surfaced a genuine regression: all 20 in-scope
questions were answered correctly, but **0/3 out-of-scope questions were
declined** (worse than the old demo backend's 1/3) — the model answered
"What is the capital of France?" correctly from its own training knowledge,
and even generated a full pizza recipe from scratch for "Can you recommend
a good pizza recipe?", instead of saying "I don't have information about
that in my knowledge base." Two compounding causes, both fixed:

1. `retrieval.get_top_chunks()` had no relevance cutoff — it always
   returned the *k* nearest chunks no matter how irrelevant, so
   `generate.py`'s "no chunks retrieved → decline" fallback could never
   fire. Measured real `qwen3-embedding-0.6b` cosine similarity scores:
   in-scope questions' top chunk scored 0.6-0.82; the 3 out-of-scope
   questions topped out at 0.3-0.37 — a clean, wide gap. Added
   `retrieval.MIN_SIMILARITY = 0.45` to filter below that.
2. `generate.py`'s `SYSTEM_PROMPT` explicitly said the model "may use
   general backend engineering knowledge," which a small model read as
   license to answer off-topic questions from its own training data
   rather than declining. Tightened to explicitly forbid this.

After both fixes: all 23 questions pass, and out-of-scope ones now resolve
**instantly** (no LLM call at all, since retrieval returns zero chunks) —
see `TEST_RESULTS.md` for full transcripts. **If you touch `SYSTEM_PROMPT`
or `MIN_SIMILARITY` again, re-run the 23-question suite before considering
it done** — this exact failure mode (in-scope works, out-of-scope silently
regresses) is easy to reintroduce without noticing, since it only shows up
on questions outside the knowledge base.

Separately, while chasing better answer quality, `qwen2.5-1.5b` was tried
as an upgrade from `qwen2.5-0.5b` (see the model swap history above) and
got 22/23 on its first run, but `foundry status` revealed this machine has
only ~1.2GB RAM free of 7.3GB total, and under that pressure the bigger
model intermittently re-hit the "Operation was cancelled" timeout even on
a question that had just succeeded — 2 retries didn't reliably fix it.
Reverted to `qwen2.5-0.5b` for reliability. Also added a retry-on-
cancellation wrapper in `foundry_client.chat()` (`_CHAT_RETRIES = 2`) as
defense in depth regardless of which model is configured.

### After that, optional stretch goals (not started, not required)

- A Streamlit/Gradio or HTML+JS UI instead of CLI (mentioned as an option
  in the original project guide) — likely moot now, the Flask+static-HTML
  web UI already exists and satisfies this.
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
