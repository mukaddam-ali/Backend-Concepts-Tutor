"""Selects which embedding/chat implementation the RAG pipeline uses.

Set the RAG_BACKEND environment variable to:
- "demo"   -- offline, no-native-dependencies keyword-matching stand-in
              (demo_backend.py). Short, extractive answers; no API key
              needed; works anywhere including Render.
- "gemini" -- real hosted LLM via Google Gemini (gemini_backend.py). Real
              generated answers; needs a GEMINI_API_KEY environment
              variable (free tier: https://aistudio.google.com/apikey).
              Works on Render (it's just an HTTPS API call).
- unset / anything else -- real Foundry Local, on-device (foundry_client.py).
              Only works on a machine that can actually run Foundry Local.
"""

import os

_BACKEND_NAME = os.environ.get("RAG_BACKEND", "foundry").lower()
is_demo = _BACKEND_NAME == "demo"

if is_demo:
    import demo_backend as _impl

    name = "demo"
elif _BACKEND_NAME == "gemini":
    import gemini_backend as _impl

    name = "gemini"
else:
    import foundry_client as _impl

    name = "foundry"

embed = _impl.embed
embed_one = _impl.embed_one
chat = _impl.chat
