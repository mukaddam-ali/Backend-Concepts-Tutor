# Test Results

Testing was run against **demo mode** (`RAG_BACKEND=demo`), since the real
Foundry Local models can't run yet on this machine (see README's "VC++
Redistributable" note). These results validate the pipeline's plumbing —
chunking, storage, retrieval, prompt assembly, and the "don't know" fallback
— not real embedding/generation quality, which still needs verification once
Foundry Local is unblocked.

23 queries were run: 20 in-scope (one per knowledge-base topic) and 3
deliberately out-of-scope.

## In-scope queries: 20/20 correctly retrieved the right document

| # | Question | Correct source? |
|---|----------|:---:|
| 1 | What is a REST API and what are its core principles? | ✅ |
| 2 | How is GraphQL different from REST? | ✅ |
| 3 | What is the difference between SQL and NoSQL databases? | ✅ |
| 4 | What is the difference between authentication and authorization? | ✅ |
| 5 | Why would I use caching? | ✅ |
| 6 | What is a CDN used for? | ✅ |
| 7 | Why would I use a message queue? | ✅ |
| 8 | What does a load balancer do? | ✅ |
| 9 | What is a WebSocket used for? | ✅ |
| 10 | How should I version an API? | ✅ |
| 11 | What does a rate limiter do? | ✅ |
| 12 | What does ACID mean in databases? | ✅ |
| 13 | When should I use microservices instead of a monolith? | ✅ |
| 14 | Why would I add a database index? | ✅ |
| 15 | What is database sharding? | ✅ |
| 16 | What are the three pillars of observability? | ✅ |
| 17 | What is a Docker container? | ✅ |
| 18 | Continuous delivery vs continuous deployment? | ✅ |
| 19 | When should I scale horizontally instead of vertically? | ✅ |
| 20 | What is CORS and why does it exist? | ✅ |

Several queries (5, 8, 12, 19, 20) pulled 1-2 extra, partially-irrelevant
chunks alongside the correct one — expected for keyword-based retrieval
without real semantic understanding — but the correct chunk was always
present, so the answer was still accurate.

## Out-of-scope queries: 1/3 correctly declined

| Question | Expected | Actual | Result |
|---|---|---|---|
| What is the capital of France? | "I don't have information..." | "I don't have information..." | ✅ PASS |
| Can you recommend a good pizza recipe? | "I don't have information..." | Answered from `microservices-vs-monolith` ("Most experienced teams recommend starting with a monolith") | ❌ FAIL |
| What is the weather like today? | "I don't have information..." | Answered from `database-replication-sharding` (matched the literal word "today" inside an unrelated example sentence) | ❌ FAIL |

## Finding: false-positive answers on out-of-scope questions

**Root cause:** the demo backend's fallback threshold is "at least one
non-stopword keyword overlaps between the question and a retrieved chunk."
A single coincidental word match — "good" in "recommend...good pizza recipe"
happening to also appear in an unrelated doc, or the literal word "today"
inside an unrelated example sentence — is enough to trigger a confident-
looking answer instead of correctly saying "I don't know."

**Why it wasn't simply fixed:** raising the overlap threshold to require 2+
matching keywords was tried and reverted — it broke several legitimately
correct answers above (e.g. "What is a WebSocket used for?" only overlaps on
the single word "websocket" in its best-matching sentence). The demo
backend's keyword-overlap approach has no way to distinguish "this word
match is topically meaningful" from "this word match is coincidental" —
that distinction requires actual semantic understanding of what the
question is asking, which is precisely what real embeddings (Foundry Local)
and a real LLM (which would recognize "pizza recipe" has nothing to do with
its instructions regardless of stray word overlap) provide and this
lexical stand-in fundamentally cannot.

**What this means for the real system:** this failure mode is specific to
the demo backend's keyword-matching design, not the RAG architecture itself.
The system prompt in `generate.py` already instructs the real model to
answer only from context and say "I don't know" when it's insufficient —
that instruction is meaningful to an actual LLM in a way it can't be to a
regex-based keyword matcher. Re-running this exact test suite once Foundry
Local is unblocked is the next validation step, and the 3 out-of-scope
questions above are good candidates to re-check first.

## How to reproduce

```bash
cd rag-backend-tutor
RAG_BACKEND=demo .venv\Scripts\python.exe ingest.py
RAG_BACKEND=demo .venv\Scripts\python.exe main.py
```

Then ask any of the 23 questions above, or run them programmatically via
`generate.answer_query(question)`.
