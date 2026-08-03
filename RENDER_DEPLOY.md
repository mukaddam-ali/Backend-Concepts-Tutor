# Deploying to Render

## Important: this deploys demo mode, not real Foundry Local

Render runs Linux containers. Foundry Local is an **on-device** inference
runtime — it doesn't have a Linux build reachable this way, and
`foundry-local-sdk`'s own dependency (`foundry-local-core`) ships
**Windows-only** wheels (confirmed: `pip install` on Linux fails outright
trying to resolve it). So a Render deployment necessarily runs the offline
`demo_backend.py` stand-in (keyword-based retrieval, extractive answers) —
not the real embeddings/LLM. That's a real, structural limitation of what
Foundry Local *is* (a local runtime, not a hosted service), not something
fixable by configuration. Real Foundry Local answers still require running
this app on your own Windows/Mac/Linux machine directly.

`requirements-render.txt` reflects this: it deliberately excludes
`foundry-local-sdk` and `openai`, installing only `flask` + `waitress`.

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
5. **Environment Variables** → add:
   - `RAG_BACKEND` = `demo`
6. **Instance Type**: Free is fine for demoing.
7. Click **Create Web Service**.

## After it's deployed

- Visit the URL Render gives you — it should show the chat UI.
- Check `https://<your-app>.onrender.com/api/status` — should return
  `{"backend": "demo", "chunk_count": 219}` (or similar). If `chunk_count`
  is `0`, something went wrong with ingestion; check the Render logs.
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

## Updating the deployed app

Render auto-deploys on every push to `main` by default. Just:

```bash
git add .
git commit -m "your change"
git push
```

Render picks it up and redeploys automatically.
