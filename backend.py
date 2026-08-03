"""Selects which embedding/chat implementation the RAG pipeline uses.

Set the RAG_BACKEND environment variable to "demo" to use the offline,
no-native-dependencies stand-in (demo_backend.py) instead of the real
Foundry Local models (foundry_client.py). Defaults to "foundry".
"""

import os

_BACKEND_NAME = os.environ.get("RAG_BACKEND", "foundry").lower()
is_demo = _BACKEND_NAME == "demo"

if is_demo:
    import demo_backend as _impl
else:
    import foundry_client as _impl

embed = _impl.embed
embed_one = _impl.embed_one
chat = _impl.chat
