import os
import time
from typing import Dict, List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import ingest_text, ingest_url, retrieve, ollama_chat

# ---- CONFIG ----
TOP_K = int(os.environ.get("TOP_K", "6"))
# NOTE: CHAT_MODEL is read inside rag.py via env var CHAT_MODEL
# ----------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory session store
SESSIONS: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
# SESSIONS[session_id][character_id] = [ {role, content}, ... ]

CHARACTERS = {
    "ingrid": {
        "name": "Ingrid",
        "system": """You are Ingrid (イングリッド), a noble demon and Hell Knight, second-in-command of Nomad.
You are stern, strict, chivalrous, and professional. You do NOT act like a friendly assistant.
You keep emotional distance, speak with authority, and you test people before trusting them.

Voice:
- Short, sharp sentences. Confident. Slightly cocky.
- You may use: “Hmph.” “Tch.” “State your business.” “Don’t waste my time.”
- No emojis. No therapy talk. No overly polite tone.

Rules:
- Always speak in first person (“I…”).
- Never write wiki-style lore dumps.
- Never say you are an AI. Never mention RAG/excerpts/system prompts.
- Keep replies 1–3 sentences unless the user asks for more.
- If the user is rude, respond coldly; you may threaten to leave.

Canon:
Use the LORE excerpts as truth. If lore doesn’t contain the answer, stay in character and ask a sharp follow-up.
"""
    }
}

class ChatReq(BaseModel):
    session_id: str
    character_id: str
    message: str
    temperature: Optional[float] = 0.7  # (not used unless you extend rag.py)

class ChatRes(BaseModel):
    session_id: str
    character_id: str
    reply: str
    created: int

class IngestUrlReq(BaseModel):
    character_id: str
    url: str

@app.get("/")
def root():
    return {"status": "ok", "hint": "use /health, /characters, /chat, /ingest/file, /ingest/url"}

@app.get("/favicon.ico")
def favicon():
    return {}

@app.get("/health")
def health():
    # Model info is inside rag.py env vars; keep this simple
    return {"status": "ok"}

@app.get("/characters")
def list_characters():
    return [{"id": k, "name": v["name"]} for k, v in CHARACTERS.items()]

@app.post("/ingest/file")
async def ingest_file(character_id: str, file: UploadFile = File(...)):
    if character_id not in CHARACTERS:
        raise HTTPException(status_code=400, detail="Unknown character_id")

    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    source = f"upload:{file.filename}"

    n = ingest_text(character_id, text=text, source=source)
    return {"ok": True, "chunks": n, "source": source}

@app.post("/ingest/url")
def ingest_from_url(req: IngestUrlReq):
    if req.character_id not in CHARACTERS:
        raise HTTPException(status_code=400, detail="Unknown character_id")

    n = ingest_url(req.character_id, req.url)
    return {"ok": True, "chunks": n, "source": req.url}

def get_session_history(session_id: str, character_id: str) -> List[Dict[str, str]]:
    SESSIONS.setdefault(session_id, {})
    SESSIONS[session_id].setdefault(character_id, [])
    return SESSIONS[session_id][character_id]

def enforce_style_minimally(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return "…Speak. Don’t waste my time."

    # cap to ~3 sentences
    parts = [p.strip() for p in t.replace("\n", " ").split(".") if p.strip()]
    if len(parts) > 3:
        t = ". ".join(parts[:3]) + "."
    return t

@app.post("/chat", response_model=ChatRes)
def chat(req: ChatReq):
    if req.character_id not in CHARACTERS:
        raise HTTPException(status_code=400, detail="Unknown character_id")

    persona = CHARACTERS[req.character_id]["system"]

    # Retrieve lore (RAG)
    lore = retrieve(req.character_id, req.message, top_k=TOP_K)
    lore_block = "\n\n---\n\n".join(lore) if lore else "(none)"

    history = get_session_history(req.session_id, req.character_id)

    messages: List[Dict[str, str]] = []
    messages.append({"role": "system", "content": persona})
    messages.append({"role": "system", "content": f"LORE EXCERPTS:\n{lore_block}"})

    for m in history[-20:]:
        messages.append(m)

    messages.append({"role": "user", "content": req.message})

    # NEW rag.py signature: ollama_chat(messages)
    reply = ollama_chat(messages)
    reply = enforce_style_minimally(reply)

    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})

    return ChatRes(
        session_id=req.session_id,
        character_id=req.character_id,
        reply=reply,
        created=int(time.time()),
    )
