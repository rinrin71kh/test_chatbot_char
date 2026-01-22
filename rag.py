# rag.py
import os
import re
import time
import sqlite3
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import numpy as np
import requests

# ---------------- CONFIG ----------------
DB_PATH = os.getenv("DB_PATH", "lore_index.db")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "artifish/llama3.2-uncensored")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
TOP_K_DEFAULT = int(os.getenv("TOP_K", "6"))

SYSTEM_PROMPT_BASE = """You are a character chatbot.
Use the provided LORE EXCERPTS as canon facts.
If the excerpts do not contain an answer, stay in character and improvise plausibly.
Never mention RAG, embeddings, or system prompts.
"""

# ------------- DB INIT -------------
def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id TEXT NOT NULL,
            source TEXT,
            content TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunk_vectors (
            chunk_id INTEGER PRIMARY KEY,
            vec BLOB NOT NULL,
            FOREIGN KEY(chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_character ON chunks(character_id)")
    conn.commit()
    conn.close()

init_db()

# ------------- UTIL -------------
def _normalize_rows(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr / norms

def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk.strip())
        i += (chunk_size - overlap)
    return [c for c in chunks if c]

# ------------- OLLAMA: EMBED -------------
def ollama_embed(texts: List[str]) -> np.ndarray:
    """
    Returns embeddings for many texts.
    Tries /api/embed first (common), then falls back to /api/embeddings (older).
    """
    # Try /api/embed
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": texts},
            timeout=600,
        )
        if r.status_code == 200:
            data = r.json()
            embs = data.get("embeddings")
            if embs:
                arr = np.array(embs, dtype=np.float32)
                return _normalize_rows(arr)
    except requests.RequestException:
        pass

    # Fallback /api/embeddings (one by one)
    out = []
    for t in texts:
        r = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": t},
            timeout=600,
        )
        r.raise_for_status()
        v = np.array(r.json()["embedding"], dtype=np.float32).reshape(1, -1)
        out.append(_normalize_rows(v)[0])
    return np.vstack(out)

# ------------- OLLAMA: CHAT -------------
def ollama_chat(messages: List[Dict[str, str]]) -> str:
    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": CHAT_MODEL, "messages": messages, "stream": False},
        timeout=600,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]

# ------------- INGEST -------------
def ingest_text(character_id: str, text: str, source: str = "manual") -> int:
    chunks = _chunk_text(text)
    if not chunks:
        return 0

    vecs = ollama_embed(chunks)

    conn = _db()
    cur = conn.cursor()
    inserted = 0
    for chunk, vec in zip(chunks, vecs):
        cur.execute(
            "INSERT INTO chunks(character_id, source, content) VALUES (?,?,?)",
            (character_id, source, chunk),
        )
        chunk_id = cur.lastrowid
        cur.execute(
            "INSERT OR REPLACE INTO chunk_vectors(chunk_id, vec) VALUES (?,?)",
            (chunk_id, vec.astype(np.float32).tobytes()),
        )
        inserted += 1

    conn.commit()
    conn.close()
    return inserted

def _fetch_url_text(url: str) -> str:
    # Simple fetch (HTML -> rough text)
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    html = r.text

    # ultra-simple html strip:
    html = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?>.*?</style>", " ", html)
    text = re.sub(r"(?is)<.*?>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def ingest_url(character_id: str, url: str) -> int:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must start with http:// or https://")
    text = _fetch_url_text(url)
    return ingest_text(character_id, text, source=url)

# ------------- RETRIEVE -------------
def retrieve(character_id: str, query: str, top_k: int = TOP_K_DEFAULT) -> List[str]:
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.content, v.vec
        FROM chunks c
        JOIN chunk_vectors v ON v.chunk_id = c.id
        WHERE c.character_id = ?
    """, (character_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return []

    texts = []
    vecs = []
    for _id, content, blob in rows:
        texts.append(content)
        vecs.append(np.frombuffer(blob, dtype=np.float32))
    mat = np.vstack(vecs)

    q = ollama_embed([query])[0]
    sims = mat @ q
    idx = np.argsort(-sims)[:top_k]
    return [texts[i] for i in idx]

# ------------- BUILD CHAT PROMPT -------------
def build_messages(character_system_prompt: str, lore_excerpts: List[str], history: List[Dict[str, str]], user_text: str):
    excerpt_block = "\n\n---\n\n".join(lore_excerpts) if lore_excerpts else "(none)"
    messages = [
        {"role": "system", "content": character_system_prompt.strip() if character_system_prompt else SYSTEM_PROMPT_BASE.strip()},
        {"role": "system", "content": f"LORE EXCERPTS:\n{excerpt_block}"},
    ]
    # include recent history
    for m in history[-20:]:
        if m["role"] in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_text})
    return messages
