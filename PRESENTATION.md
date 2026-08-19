# Presentation / Demo Script

A short structure for presenting this project, following the project guide's
suggested format: problem statement → key features → live demo → lessons
learned.

## 1. Problem statement (30 seconds)

"General-purpose chatbots either don't know about a specific, narrow domain,
or they hallucinate a plausible-sounding but wrong answer. This project
builds a Q&A assistant that only answers from a curated knowledge base —
here, core backend engineering concepts — and explicitly says 'I don't know'
rather than guessing. It runs entirely offline, on-device, via Microsoft
Foundry Local — no cloud API, no internet needed at runtime."

## 2. Key features / how it works (1-2 minutes)

- **RAG pattern**: Retrieve relevant chunks → Augment the prompt with them →
  Generate an answer grounded in that context.
- **34-topic knowledge base**: REST, GraphQL, databases, auth, caching,
  message queues, load balancing, WebSockets, CI/CD, Kubernetes, serverless,
  web security, RAG/vectors/embeddings, and more — see
  [PROJECT_REPORT.md](PROJECT_REPORT.md) for the full list. Topic selection
  cross-referenced [roadmap.sh/backend](https://roadmap.sh/backend), and
  each newer doc links free, individually-verified resources for further
  reading — a nice detail to mention if asked how the content was sourced.
- **Local-only**: SQLite for storage, Foundry Local for on-device embeddings
  and chat inference. No data leaves the machine.
- **Source citations**: answers say which document they came from, so a user
  can verify the claim isn't fabricated.
- **Swappable backend** (a nice technical aside if asked): the embedding/chat
  layer is abstracted so the same pipeline can run against a lightweight
  offline stand-in for development/testing, or the real Foundry Local models
  for production quality — zero code changes to switch.

## 3. Live demo script

Run:
```bash
cd rag-backend-tutor
.venv\Scripts\python.exe main.py
```
(or prefix with `RAG_BACKEND=demo` — see note below on which to use.)

Ask, in order:

1. **An easy in-scope question** — establishes the baseline:
   > What is the difference between SQL and NoSQL databases?

2. **A more specific in-scope question** — shows it's not just keyword
   spotting on the title:
   > When should I use microservices instead of a monolith?

3. **An out-of-scope question** — the "doesn't hallucinate" moment:
   > What is the capital of France?

   Expect: "I only answer questions about backend engineering -- ask me
   something about that instead."
   *(Note: this specific fallback is proven reliable on the real model's
   language understanding; see TEST_RESULTS.md if presenting in demo mode,
   where 2 of 3 out-of-scope test questions triggered false positives — pick
   your live out-of-scope question from the ones already confirmed working,
   or present this as an honest "here's a limitation we found and why"
   moment rather than hiding it.)*

4. **Show a source citation** — point out the `(sources: ...)` line under an
   answer, and connect it back to the problem statement: "this is how a user
   could verify the answer instead of just trusting it."

## 4. Lessons learned (talking points)

- **Chunking strategy matters more than it seems.** Splitting documents into
  passage-level chunks (not whole documents, not single sentences) was the
  difference between retrieval finding the right, focused piece of context
  versus either too little or too much.
- **Testing against real data finds real bugs.** Expanding the knowledge
  base from 10 to 20 docs and then actually running test queries — rather
  than assuming the code was correct — surfaced two concrete bugs: stopwords
  dominating similarity scores, and a vector space too small for the
  vocabulary size, both invisible from reading the code alone.
- **A crude keyword-matching fallback isn't a fair test of the real system.**
  Building an offline stand-in to unblock development was valuable, but its
  false-positive rate on out-of-scope questions is a property of *keyword
  matching*, not of the RAG architecture — worth explaining clearly if asked
  "why did it just make something up?" during a demo run in fallback mode.
- **(If applicable) Environment blockers are real engineering constraints.**
  Foundry Local's native runtime dependency (a missing system library
  requiring admin rights to install) blocked running the real models on the
  original development machine — a reminder that "works in theory, matches
  the SDK's documented API" and "verified working" are different claims,
  worth being explicit about rather than conflating.

## Notes for whoever is presenting

- If Foundry Local is working on the presentation machine, use the real
  models — the "I don't know" fallback and answer quality will be more
  robust than demo mode's keyword matching.
- If only demo mode is available, that's fine — be upfront that it's a
  pipeline-validation stand-in, not the real model, and use TEST_RESULTS.md's
  findings as a feature (shows real testing happened) rather than a bug to
  hide.
