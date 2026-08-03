# Deploying to Render

## Important: Foundry Local specifically can't run here

Render runs Linux containers. Foundry Local is an **on-device** inference
runtime — it doesn't have a Linux build reachable this way, and
`foundry-local-sdk`'s own dependency (`foundry-local-core`) ships
**Windows-only** wheels (confirmed: `pip install` on Linux fails outright
trying to resolve it). That's a structural limitation of what Foundry Local
*is* (a local runtime, not a hosted service), not something fixable by
configuration.

That still leaves two options for a Render deployment, chosen via the
`RAG_BACKEND` environment variable:

- **`RAG_BACKEND=demo`** — no API key, no cost, but short/extractive
  keyword-matched answers (see `TEST_RESULTS.md` for what to expect).
- **`RAG_BACKEND=gemini`** — real generated answers via Google's hosted
  Gemini API. Needs a free `GEMINI_API_KEY`. **Recommended** — this is
  what actually fixes the "answers are too short" problem, since it's a
  real LLM rather than sentence extraction.

`requirements-render.txt` reflects this: it deliberately excludes
`foundry-local-sdk` and `openai` (Windows-only/irrelevant here), but
includes `google-genai` for the Gemini option.

## Option A: One-click via `render.yaml` (recommended)

This repo includes `render.yaml`, which Render can read automatically.

1. Go to [dashboard.render.com](https://dashboard.render.com), sign in
   (GitHub login is easiest).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub account if you haven't, then select the
   `Backend-Concepts-Tutor` repo.
4. Render detects `render.yaml` and shows the `backend-concepts-tutor`
   service it will create — review and click **Apply**.
5. Wait for the build + deploy to finish (a few minutes). Render gives you
   a URL like `https://backend-concepts-tutor.onrender.com`.

## Option B: Manual setup via the dashboard

If you'd rather configure it by hand instead of using the blueprint:

1. **New +** → **Web Service** → connect the `Backend-Concepts-Tutor` repo.
2. **Runtime**: Python 3.
3. **Build Command**: `pip install -r requirements-render.txt`
4. **Start Command**: `python -m waitress --host=0.0.0.0 --port=$PORT app:app`
5. **Environment Variables** → add either:
   - `RAG_BACKEND` = `demo` (no key needed), **or**
   - `RAG_BACKEND` = `gemini` **and** `GEMINI_API_KEY` = *(your key from
     [aistudio.google.com/apikey](https://aistudio.google.com/apikey))* —
     paste the key directly into Render's Environment Variables field, not
     anywhere that gets committed to git.
6. **Instance Type**: Free is fine for demoing.
7. Click **Create Web Service**.

## Switching an already-deployed service between modes

If you already deployed (e.g. with `RAG_BACKEND=demo`) and want to switch to
Gemini:

1. Go to your service in the Render dashboard.
2. **Environment** (left sidebar) → **Environment Variables**.
3. Change `RAG_BACKEND` from `demo` to `gemini`.
4. Add a new variable: `GEMINI_API_KEY` = your key.
5. Save — Render redeploys automatically with the new variables.
6. Re-check `/api/status`: `backend` should now say `"gemini"`.

## After it's deployed

- Visit the URL Render gives you — it should show the chat UI.
- Check `https://<your-app>.onrender.com/api/status` — should return
  `{"backend": "demo"|"gemini", "chunk_count": 219}` (or similar). If
  `chunk_count` is `0`, something went wrong with ingestion; check the
  Render logs. If `backend` isn't what you expect, double check the
  `RAG_BACKEND` environment variable value (it's case-insensitive but must
  be exactly `demo` or `gemini`, nothing else, to not silently fall through
  to the Foundry Local path which will fail on Render).
- Ask a question through the UI to confirm end-to-end.

## Things to expect (not bugs)

- **Cold starts**: Render's free tier spins down a service after ~15
  minutes of inactivity. The first request after that takes 30-60 seconds
  to wake back up — normal free-tier behavior, not an error.
- **Ephemeral filesystem**: `knowledge.db` is rebuilt from `docs/*.md` on
  first request after every deploy or restart (Render's free tier doesn't
  persist disk between deploys). This is intentional — the `before_request`
  hook in `app.py` checks and re-ingests automatically if the DB is empty,
  so this self-heals with no manual step. It just means the very first
  request after a cold start/redeploy is a bit slower (has to ingest ~34
  docs first).
- **Demo-mode answers**: expect the same keyword-matching behavior and
  limitations documented in `TEST_RESULTS.md` — this is the same code path
  already tested locally, not a different, less-tested one.
- **Gemini free-tier rate limits**: Google's free tier caps requests per
  minute/day. Fine for personal use and demoing; heavy or automated testing
  could hit the limit and return an error from `gemini_backend.chat()` —
  not a bug in this app, just the free tier's ceiling.

## Updating the deployed app

Render auto-deploys on every push to `main` by default. Just:

```bash
git add .
git commit -m "your change"
git push
```

Render picks it up and redeploys automatically.
