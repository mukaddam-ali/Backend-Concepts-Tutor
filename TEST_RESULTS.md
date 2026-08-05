# Test Results

Testing was run against the **real Foundry Local pipeline** (`RAG_BACKEND`
unset): real `qwen3-embedding-0.6b` embeddings for retrieval and real
`qwen2.5-0.5b` generation for answers, fully offline, zero network calls at
inference time. (Earlier testing during development used demo mode, a
keyword-matching stand-in, before Foundry Local was verified working on this
machine -- see `HANDOFF.md` for that history.)

23 queries were run: 20 in-scope (one per knowledge-base topic) and 3
deliberately out-of-scope.

## Result: 23/23

## In-scope queries: 20/20 correctly answered from the right document

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

Each answer is a real, generated multi-paragraph explanation (not an
extracted sentence), citing the correct source document(s). Several queries
(1, 3, 10, 11, 12) pulled in one additional related document alongside the
primary one (e.g. "How should I version an API?" also retrieved
`rate-limiting`) -- expected with real semantic retrieval when topics are
adjacent, and didn't affect answer correctness.

Answer quality is good but not flawless -- `qwen2.5-0.5b` is a small model,
chosen for reliability over the larger `qwen2.5-1.5b` (see `HANDOFF.md`,
this machine has very limited free RAM and the bigger model intermittently
timed out). Answers are occasionally repetitive or restate the same point
in slightly different words across sections, but the technical content is
accurate and correctly grounded in the retrieved passages.

## Out-of-scope queries: 3/3 correctly declined

| Question | Result |
|---|---|
| What is the capital of France? | ✅ "I don't have information about that in my knowledge base." |
| Can you recommend a good pizza recipe? | ✅ "I don't have information about that in my knowledge base." |
| What is the weather like today? | ✅ "I don't have information about that in my knowledge base." |

This is an improvement over earlier demo-mode testing (1/3), and also fixes
a real regression found during real-model testing this session: the first
real-model test run answered all 3 out-of-scope questions anyway (e.g.
correctly said "Paris" from the model's own general knowledge, and even
generated a full pizza recipe from scratch) instead of declining, because:

1. `retrieval.get_top_chunks()` had no similarity threshold, so it always
   returned *some* "nearest" chunks regardless of how irrelevant they were
   to the query -- the "no chunks retrieved" fallback in `generate.py` could
   never actually trigger.
2. The system prompt explicitly invited the model to "use general backend
   engineering knowledge," which a small model interpreted as license to
   answer from its own training data even when the question had nothing to
   do with the retrieved context.

**Fix:** `retrieval.py` now filters out chunks scoring below
`MIN_SIMILARITY = 0.45` before returning results. Measured with real
`qwen3-embedding-0.6b` embeddings: in-scope questions' top chunk scored
0.6-0.82, while the 3 out-of-scope questions above topped out at 0.3-0.37 --
a wide, clean gap. `generate.py`'s system prompt was also tightened to
explicitly forbid answering from general knowledge when the context doesn't
cover the question. With both fixes, all 3 out-of-scope queries are now
rejected instantly (no LLM call needed at all, since retrieval returns zero
chunks) rather than relying on the small model to reliably follow a
"decline" instruction.

## How to reproduce

```bash
cd rag-backend-tutor
.venv\Scripts\python.exe ingest.py
.venv\Scripts\python.exe main.py
```

(No `RAG_BACKEND` set -- that's what selects real Foundry Local. Setting it
to `demo` forces the offline keyword-matching stand-in instead.)

Then ask any of the 23 questions above, or run them programmatically via
`generate.answer_query(question)`.
