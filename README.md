# Backend Concepts Tutor

A little offline chatbot that knows about backend engineering — REST vs
GraphQL, caching, message queues, database sharding, CAP theorem, all of
it — and answers your questions about it without ever touching the
internet. No API key, no cloud bill, no "your request could not be
completed." It runs the whole thing — retrieval *and* generation — on your
own machine, using [Microsoft Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/what-is-foundry-local)
to run a real language model locally.

This started as a class project built around Retrieval-Augmented
Generation (RAG): instead of trusting a language model to just "know"
things, you give it a curated set of documents, let it search those
documents for whatever's relevant to the question being asked, and only
then let it write an answer — grounded in what it actually found, not
whatever it half-remembers from training. The assignment specifically
wanted this running fully offline with a real on-device model, not a
wrapper around ChatGPT or Gemini, which is exactly what this is.

## What it actually does

You ask it something like *"why would I use a message queue?"* and here's
what happens under the hood:

1. Your question gets turned into a vector (an embedding) — a list of
   numbers that captures what the question is *about*, semantically.
2. That vector gets compared against the vectors of every chunk of text in
   the knowledge base, and the closest matches win.
3. Those matching passages get stuffed into a prompt along with your
   question, and handed to a local LLM with instructions to answer
   *from that context* — and to admit it doesn't know rather than make
   something up if the context doesn't actually cover it.
4. You get back a real, generated, multi-paragraph answer, with the source
   document cited.

All of that — steps 1 through 4 — happens on your machine, via Foundry
Local. No network calls at inference time, at all. I confirmed this
directly by watching the network tab while asking questions: every request
goes to `127.0.0.1`, nothing else.

## The knowledge base

34 topics, written from scratch and shaped around
[roadmap.sh/backend](https://roadmap.sh/backend)'s actual structure (that
site renders its roadmap as an interactive SVG diagram, so getting the real
node list took pulling text directly out of the SVG in a browser — a plain
`fetch` just gets you an empty shell). Covers the fundamentals: REST APIs,
GraphQL, SQL vs NoSQL, database types, indexing, replication & sharding,
transactions & ACID, normalization, CAP theorem, auth, caching, CDNs,
message queues, load balancing, WebSockets, API versioning, rate limiting,
microservices vs monoliths, architectural patterns, observability,
Docker, Kubernetes, serverless, CI/CD, scaling, CORS, web security
fundamentals, testing, web servers & reverse proxies, resilience patterns,
internet fundamentals, Git, and — a little self-referentially — how RAG
itself works. Each doc that came from the roadmap pass also links a few
free resources for further reading, and every single one of those links
was actually checked to make sure it resolves (a surprising number of
"well-known" doc URLs don't, once you check).

That's a lot more than the "20 or so files" this needed to be, on purpose —
better to have real breadth than pad out 20 thin ones.

## Setup

### 1. Install Foundry Local

This is a separate runtime, not just a Python package — it has to be
installed on the machine itself:

```bash
winget install Microsoft.FoundryLocal
```

**If this fails with a DLL error** (`FileNotFoundError: Could not find
module '...onnxruntime.dll'`), you're missing the Microsoft Visual C++
2015–2022 Redistributable, which Foundry Local's native core depends on:

```bash
winget install Microsoft.VCRedist.2015+.x64
```

That one needs admin rights (a UAC prompt) — there's no way around it, it's
a hard dependency of the native runtime, not something the Python side can
route around.

Sanity check it worked:

```bash
foundry model list
```

If that prints a table of models with no error, you're good.

### 2. Set up Python

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 3. Run it

```bash
.venv\Scripts\python.exe main.py
```

First run will download two small models (a few hundred MB total) and
build the knowledge base — needs internet for that *one-time* download
only. After that, everything's local. Ask it a question, type `exit` when
you're done.

Prefer a browser instead of a terminal?

```bash
.venv\Scripts\python.exe app.py
```

then open `http://127.0.0.1:5000` — same brain, ChatGPT-style web UI with
conversation history (saved in your browser, not sent anywhere).

## Is it actually good?

I ran 23 real questions through the real pipeline — 20 that the knowledge
base should be able to answer, and 3 it deliberately shouldn't (like "can
you recommend a good pizza recipe?"). Final score: **23/23.** All 20
in-scope questions got answered correctly with the right source cited, and
all 3 out-of-scope ones got a clean "I don't have information about that"
instead of a guess.

That second part didn't work on the first try, and it's worth mentioning
honestly: the first real run answered *all three* of the trick questions
anyway — it correctly said "Paris" to "what's the capital of France," and
even wrote out a full pizza recipe from memory, both from its own general
knowledge, completely ignoring that neither had anything to do with the
retrieved context. Turned out retrieval was returning *some* passage no
matter how irrelevant the question was — there's always a "closest" chunk,
even when closest still isn't close — and the small model was happy to
just answer from what it already knew rather than admit it couldn't help.
Fixed by measuring the actual similarity scores (real matches scored
0.6–0.8, the irrelevant ones topped out around 0.35) and adding a cutoff
below which retrieval returns nothing at all, plus tightening the model's
instructions to explicitly forbid answering from outside knowledge. After
that, all three declined instantly.

Full transcripts and the story behind that fix are in
[TEST_RESULTS.md](TEST_RESULTS.md).

## About the model size (an honest tradeoff)

The chat model is `qwen2.5-0.5b` — small, as local LLMs go. That wasn't the
first choice. `phi-3.5-mini` (bigger, generally sharper) was tried first
and was unusably slow on this hardware — 55 seconds for a one-word answer,
and the real question-answering prompt reliably timed out before finishing
at all. `qwen2.5-1.5b` landed in a nicer middle ground — noticeably better
answers, and it actually passed 22 of the 23 test questions — but this
particular machine has very little free RAM, and under that pressure it
would occasionally hang on a question that had worked fine moments
earlier. Reliability won. `qwen2.5-0.5b` isn't going to write a PhD thesis,
but it's consistent, it cites its sources correctly, and it never leaves
you staring at a spinner. On a machine with more headroom, bumping
`CHAT_MODEL_ALIAS` in `foundry_client.py` up to `qwen2.5-1.5b` is worth
trying — the code doesn't care which model it's pointed at.

## About the live demo link

There's a public link — [backend-concepts-tutor.onrender.com](https://backend-concepts-tutor.onrender.com)
— but it's worth being upfront about what it actually is: a lighter
keyword-matching version, **not** the real offline LLM. Foundry Local is an
on-device runtime, not a web service, so it literally cannot run on a
cloud host like Render — there's no version of "host Foundry Local
online" that makes sense, the same way you can't "host" a program that
only runs on your own GPU driver. The public link exists so the UI and
retrieval pipeline are visible to anyone without needing to install
anything, but the actual assignment — a real local model doing real
generation — only exists by running this repo on your own machine as
described above.

## Project layout

```
docs/                   Knowledge base — the actual source material
db.py                   SQLite storage for chunks + their embeddings
ingest.py               Splits docs into chunks, embeds them, stores them
retrieval.py            Finds the most relevant chunks for a question
generate.py             Builds the prompt, calls the model, returns the answer
backend.py              Picks which model backend to use (see below)
foundry_client.py       Real on-device Foundry Local (the default)
demo_backend.py         Offline keyword-matching stand-in, no real model
gemini_backend.py       Optional real cloud LLM (Google Gemini) — not the graded path, see below
main.py                 CLI
app.py                  Flask API + web UI
static/                 The web UI itself (HTML/CSS/JS)
tests/                  30 unit tests, all pass without needing a real model
TEST_RESULTS.md         Real test transcripts, warts and all
HANDOFF.md              Full project history — every bug hit and how it got fixed
```

`backend.py` decides which of the three model implementations to use, via
the `RAG_BACKEND` environment variable:

- unset (default) → **Foundry Local** — real, on-device, this is the point
  of the project
- `demo` → keyword-matching stand-in, no model at all — what the public
  Render link runs, and useful for testing the plumbing without waiting on
  model downloads
- `gemini` → real hosted Gemini — built during development as a way to get
  real generated answers onto a cloud host before Foundry Local was
  confirmed working locally; not used going forward since the assignment
  specifically rules out cloud LLMs

## Running the tests

```bash
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest tests/ -v
```

30 tests, all passing, covering chunking, similarity math, the SQLite
layer, and source-citation logic — none of them need Foundry Local running,
so they're fast and don't require any model downloads. What they *don't*
cover is real answer quality, since that needs an actual model generating
actual text — that's what the 23-question suite in `TEST_RESULTS.md` is
for.

## A few design decisions, and why

- **Chunking**: two paragraphs per chunk. Small enough to keep retrieval
  precise, big enough to keep the context coherent.
- **Retrieval**: brute-force cosine similarity in Python, checked against
  every stored chunk. That's plenty fast at this scale (a few hundred
  chunks) — a real vector index would only start to matter with a
  knowledge base orders of magnitude bigger than this one.
- **The "I don't know" fallback**: not just prompt wording — a real
  similarity cutoff in `retrieval.py` (see "Is it actually good?" above).
  Prompt instructions alone weren't enough to stop a small model from
  answering off-topic questions from its own memory; the fix had to
  happen before the question ever reached the model.
- **Two interfaces, one brain**: the CLI and the web UI both call the exact
  same `generate.answer_query()` — no duplicated logic, no risk of them
  drifting apart in behavior.

## Known limitations

- Single-user, single-machine — there's no concurrency story here, and it
  doesn't need one for what this is.
- Retrieval scales to maybe a few hundred chunks comfortably before you'd
  actually need a real vector index instead of brute-force comparison.
- Answers are only as good as a 0.5B-parameter model gets — accurate, but
  occasionally repetitive in how it phrases things. See the model-size
  section above for why that tradeoff was made deliberately.
- The very first request after a fresh install (or after Foundry Local's
  local database gets wiped) will sit there for a few minutes while it
  builds the knowledge base from scratch — there's no loading indicator
  for that yet, so it can look stuck when it isn't.
