import os
import time
import json
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag import (
    ingest_text, ingest_url, retrieve, ollama_chat, ingest_pdf_bytes,
    PDF_SUPPORT, YOUTUBE_SUPPORT, WHISPER_SUPPORT, YTDLP_SUPPORT,
    ingest_video_bytes, ingest_video_url, ingest_audio_bytes
)

# ---- CONFIG ----
TOP_K = int(os.environ.get("TOP_K", "6"))
LOREBOOK_PATH = os.environ.get("LOREBOOK_PATH", "../LoreBook")
CHARACTERS_PATH = os.environ.get("CHARACTERS_PATH", "../characters")
# NOTE: CHAT_MODEL is read inside rag.py via env var CHAT_MODEL
# ----------------

# Dynamic character storage
CHARACTERS: Dict[str, dict] = {}
VIDEO_SOURCES: Dict[str, List[str]] = {}


def load_character_from_scenario(scenario_path: Path, char_folder_name: str = None, series_name: str = None) -> Optional[dict]:
    """Load a character scenario from a JSON file."""
    try:
        with open(scenario_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract scenario name from filename (e.g., "scenario_prologue" -> "prologue")
        scenario_name = scenario_path.stem.replace("scenario_", "")

        # Generate character_id: char_folder_name + scenario_name
        if char_folder_name:
            char_id = f"{char_folder_name}_{scenario_name}".replace(" ", "_").replace("-", "_").lower()
        else:
            char_id = data.get("character_id") or scenario_path.stem.lower()

        # Build character entry
        char_entry = {
            "name": data.get("character", data.get("name", char_folder_name or scenario_path.stem)),
            "gender": data.get("gender", "Unknown"),
            "title": data.get("title", ""),
            "avatar": data.get("avatar", ""),
            "scenario": data.get("context", data.get("scenario", "")),
            "greeting": data.get("greeting", data.get("sample_greeting", "")),
            "system": data.get("system_prompt", data.get("system", "")),
            "series": series_name or data.get("series", ""),
            "source_file": str(scenario_path)
        }

        # Get video sources if present
        video_sources = data.get("video_sources", [])

        return char_id, char_entry, video_sources
    except Exception as e:
        print(f"[Characters] Error loading {scenario_path}: {e}")
        return None


def load_character_from_profile(profile_path: Path, char_folder: Path) -> List[tuple]:
    """Load character from profile.json and all scenario files in the folder."""
    results = []

    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)

        series_name = profile.get("series", char_folder.parent.name)
        char_folder_name = char_folder.name
        video_sources = profile.get("video_sources", [])
        gender = profile.get("gender", "Unknown")

        # Load all scenario files in the folder
        for scenario_file in char_folder.glob("scenario_*.json"):
            result = load_character_from_scenario(scenario_file, char_folder_name, series_name)
            if result:
                char_id, char_entry, scenario_videos = result
                # Merge profile data
                char_entry["series"] = series_name
                char_entry["gender"] = gender  # Use gender from profile
                if not char_entry["avatar"] and profile.get("avatar"):
                    char_entry["avatar"] = profile.get("avatar")
                results.append((char_id, char_entry, video_sources + scenario_videos))

        # If no scenarios found, create one from profile
        if not results and profile:
            char_id = char_folder_name.lower().replace("-", "_")
            char_entry = {
                "name": profile.get("name", char_folder_name),
                "gender": gender,
                "title": profile.get("titles", [""])[0] if isinstance(profile.get("titles"), list) else profile.get("title", ""),
                "avatar": profile.get("avatar", ""),
                "scenario": profile.get("background", ""),
                "greeting": profile.get("greeting", ""),
                "system": profile.get("system", ""),
                "series": series_name,
                "source_file": str(profile_path)
            }
            results.append((char_id, char_entry, video_sources))

    except Exception as e:
        print(f"[Characters] Error loading profile {profile_path}: {e}")

    return results


def load_characters_from_folder():
    """Load all characters from the characters folder."""
    char_dir = Path(CHARACTERS_PATH)
    if not char_dir.exists():
        print(f"[Characters] Creating directory: {char_dir.absolute()}")
        char_dir.mkdir(parents=True, exist_ok=True)
        return

    loaded = []

    # Scan for character folders (e.g., characters/ingrid/, characters/curse_eater/*)
    for item in char_dir.iterdir():
        if item.is_dir():
            # Check if this is a series folder (contains character subfolders)
            subfolders = [f for f in item.iterdir() if f.is_dir()]

            if subfolders:
                # This is a series folder (like curse_eater/)
                for char_folder in subfolders:
                    profile_path = char_folder / "profile.json"
                    if profile_path.exists():
                        results = load_character_from_profile(profile_path, char_folder)
                        for char_id, char_entry, videos in results:
                            CHARACTERS[char_id] = char_entry
                            if videos:
                                VIDEO_SOURCES[char_id] = videos
                            loaded.append(f"{char_id} ({char_entry['name']})")
            else:
                # This is a direct character folder (like ingrid/)
                profile_path = item / "profile.json"
                if profile_path.exists():
                    results = load_character_from_profile(profile_path, item)
                    for char_id, char_entry, videos in results:
                        CHARACTERS[char_id] = char_entry
                        if videos:
                            VIDEO_SOURCES[char_id] = videos
                        loaded.append(f"{char_id} ({char_entry['name']})")

                # Also check for standalone scenario files
                for scenario_file in item.glob("scenario_*.json"):
                    result = load_character_from_scenario(scenario_file)
                    if result:
                        char_id, char_entry, videos = result
                        if char_id not in CHARACTERS:
                            CHARACTERS[char_id] = char_entry
                            if videos:
                                VIDEO_SOURCES[char_id] = videos
                            loaded.append(f"{char_id} ({char_entry['name']})")

    if loaded:
        print(f"[Characters] Loaded {len(loaded)} characters:")
        for item in loaded:
            print(f"  - {item}")
    else:
        print(f"[Characters] No characters found in {char_dir.absolute()}")


def load_lorebook_series():
    """
    Load lorebook series that have their own folder structure.
    Also ingests text content for RAG.
    """
    lorebook_dir = Path(LOREBOOK_PATH)
    if not lorebook_dir.exists():
        print(f"[Lorebook] Directory not found: {lorebook_dir.absolute()}")
        return

    loaded_lore = []

    # Scan for series folders (folders containing .txt files and possibly asset folders)
    for series_folder in lorebook_dir.iterdir():
        if series_folder.is_dir():
            series_name = series_folder.name

            # Load all .txt files in the series folder for RAG
            for txt_file in series_folder.glob("*.txt"):
                try:
                    with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()

                    if text.strip():
                        # Use series name as base character_id for lore
                        # This allows all characters from this series to access the lore
                        source = f"lorebook:{series_name}/{txt_file.name}"

                        # Ingest for the series base ID
                        base_id = series_name.replace("_series", "").replace("-", "_").lower()
                        n = ingest_text(base_id, text, source=source)
                        loaded_lore.append(f"{txt_file.name} -> {base_id} ({n} chunks)")

                        # Also ingest for any characters that match this series
                        for char_id, char_data in CHARACTERS.items():
                            char_series = char_data.get("series", "").lower().replace(" ", "_")
                            if base_id in char_series or char_series in base_id:
                                ingest_text(char_id, text, source=source)

                except Exception as e:
                    print(f"[Lorebook] Error loading {txt_file}: {e}")

    # Also load root-level .txt files (legacy support)
    for txt_file in lorebook_dir.glob("*.txt"):
        filename = txt_file.stem
        character_id = filename.split("_")[0].lower()

        try:
            with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            if text.strip():
                source = f"lorebook:{txt_file.name}"
                n = ingest_text(character_id, text, source=source)
                loaded_lore.append(f"{txt_file.name} -> {character_id} ({n} chunks)")
        except Exception as e:
            print(f"[Lorebook] Error loading {txt_file}: {e}")

    if loaded_lore:
        print(f"[Lorebook] Loaded {len(loaded_lore)} lore files:")
        for item in loaded_lore:
            print(f"  - {item}")


def load_video_sources(character_id: str = None):
    """
    Load video sources and transcribe them.
    Reads from VIDEO_SOURCES dictionary populated during character loading.
    """
    if not WHISPER_SUPPORT or not YTDLP_SUPPORT:
        print("[Video] Skipping video sources - whisper or yt-dlp not installed")
        return

    sources = VIDEO_SOURCES
    if character_id:
        sources = {character_id: sources.get(character_id, [])}

    for char_id, urls in sources.items():
        for url in urls:
            try:
                print(f"[Video] Processing: {url}")
                n = ingest_video_url(char_id, url)
                print(f"[Video] Ingested {n} chunks from {url}")
            except Exception as e:
                print(f"[Video] Error processing {url}: {e}")


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

# Mount static files for character assets
characters_path = Path(CHARACTERS_PATH)
if characters_path.exists():
    app.mount("/assets/characters", StaticFiles(directory=str(characters_path)), name="character_assets")

lorebook_path = Path(LOREBOOK_PATH)
if lorebook_path.exists():
    app.mount("/assets/lorebook", StaticFiles(directory=str(lorebook_path)), name="lorebook_assets")


@app.on_event("startup")
async def startup_event():
    """Load characters and lorebook files when server starts."""
    print("[Startup] Loading characters from folder...")
    load_characters_from_folder()
    print("[Startup] Loading lorebook files...")
    load_lorebook_series()
    print(f"[Startup] Ready! {len(CHARACTERS)} characters loaded.")


# in-memory session store
SESSIONS: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
# SESSIONS[session_id][character_id] = [ {role, content}, ... ]


class ChatReq(BaseModel):
    session_id: str
    character_id: str
    message: str
    temperature: Optional[float] = 0.7


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
    return {"status": "ok", "characters_loaded": len(CHARACTERS)}


@app.get("/characters")
def list_characters():
    return [
        {
            "id": k,
            "name": v["name"],
            "gender": v.get("gender", "Unknown"),
            "title": v.get("title", ""),
            "avatar": v.get("avatar", ""),
            "scenario": v.get("scenario", ""),
            "greeting": v.get("greeting", ""),
            "series": v.get("series", "")
        }
        for k, v in CHARACTERS.items()
    ]


@app.get("/characters/{character_id}")
def get_character(character_id: str):
    if character_id not in CHARACTERS:
        raise HTTPException(status_code=404, detail="Character not found")
    return {
        "id": character_id,
        **CHARACTERS[character_id]
    }


@app.post("/characters/reload")
def reload_characters():
    """Reload all characters from disk."""
    global CHARACTERS, VIDEO_SOURCES
    CHARACTERS = {}
    VIDEO_SOURCES = {}
    load_characters_from_folder()
    load_lorebook_series()
    return {"ok": True, "characters_loaded": len(CHARACTERS)}


@app.get("/ingest/status")
def ingest_status():
    """Check what file types are supported for ingestion."""
    supported_files = [".txt", ".md"]
    supported_urls = ["html pages"]

    if PDF_SUPPORT:
        supported_files.append(".pdf")
        supported_urls.append(".pdf URLs")
    if YOUTUBE_SUPPORT:
        supported_urls.extend(["youtube.com", "youtu.be"])
    if WHISPER_SUPPORT:
        supported_files.extend([".mp4", ".mkv", ".avi", ".webm", ".mp3", ".wav"])
    if WHISPER_SUPPORT and YTDLP_SUPPORT:
        supported_urls.extend(["hanime.tv", "video sites (with audio transcription)"])

    return {
        "pdf_support": PDF_SUPPORT,
        "youtube_support": YOUTUBE_SUPPORT,
        "whisper_support": WHISPER_SUPPORT,
        "ytdlp_support": YTDLP_SUPPORT,
        "supported_files": supported_files,
        "supported_urls": supported_urls,
        "video_sources": VIDEO_SOURCES
    }


@app.post("/ingest/video-sources")
def ingest_default_video_sources(character_id: str = None):
    """
    Ingest video sources defined in character profiles.
    This can take a long time - videos are downloaded and transcribed.
    """
    if not WHISPER_SUPPORT:
        raise HTTPException(status_code=400, detail="Whisper not installed. Run: pip install openai-whisper")
    if not YTDLP_SUPPORT:
        raise HTTPException(status_code=400, detail="yt-dlp not installed. Run: pip install yt-dlp")

    try:
        load_video_sources(character_id)
        return {"ok": True, "message": "Video sources processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/file")
async def ingest_file(character_id: str, file: UploadFile = File(...)):
    if character_id not in CHARACTERS:
        raise HTTPException(status_code=400, detail="Unknown character_id")

    content = await file.read()
    filename = file.filename or "unknown"
    source = f"upload:{filename}"
    lower_name = filename.lower()

    # Handle PDF files
    if lower_name.endswith(".pdf"):
        if not PDF_SUPPORT:
            raise HTTPException(status_code=400, detail="PDF support not installed. Run: pip install PyPDF2")
        n = ingest_pdf_bytes(character_id, content, source=source)

    # Handle video files
    elif lower_name.endswith((".mp4", ".mkv", ".avi", ".webm", ".mov", ".flv")):
        if not WHISPER_SUPPORT:
            raise HTTPException(status_code=400, detail="Video support requires: pip install openai-whisper (and ffmpeg)")
        n = ingest_video_bytes(character_id, content, filename)

    # Handle audio files
    elif lower_name.endswith((".mp3", ".wav", ".m4a", ".ogg", ".flac")):
        if not WHISPER_SUPPORT:
            raise HTTPException(status_code=400, detail="Audio support requires: pip install openai-whisper")
        n = ingest_audio_bytes(character_id, content, filename)

    else:
        # Handle text files
        text = content.decode("utf-8", errors="ignore")
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


def clean_response(text: str) -> str:
    """Clean up response without truncating or censoring."""
    t = (text or "").strip()
    if not t:
        return "..."
    return t


@app.post("/chat", response_model=ChatRes)
def chat(req: ChatReq):
    if req.character_id not in CHARACTERS:
        raise HTTPException(status_code=400, detail="Unknown character_id")

    char_data = CHARACTERS[req.character_id]
    persona = char_data.get("system", "")

    # If no system prompt in character, build a basic one
    if not persona:
        persona = f"""You are {char_data['name']}. Stay in character at all times.

CRITICAL - LORE RULES:
- The LORE EXCERPTS provided are CANON FACTS. Treat them as absolute truth.
- NEVER contradict the lore. NEVER invent facts that conflict with the lore.
- If asked about something NOT in the lore, give a vague in-character response.
- Use *asterisks* for actions in roleplay."""

    # Retrieve lore (RAG) - try character-specific first, then series-level
    lore = retrieve(req.character_id, req.message, top_k=TOP_K)

    # Also try to get lore from series base ID
    series = char_data.get("series", "")
    if series:
        series_id = series.replace(" ", "_").lower()
        series_lore = retrieve(series_id, req.message, top_k=TOP_K // 2)
        if series_lore:
            lore = lore + series_lore

    lore_block = "\n\n---\n\n".join(lore) if lore else "(none)"

    history = get_session_history(req.session_id, req.character_id)

    scenario = char_data.get("scenario", "")

    messages: List[Dict[str, str]] = []
    messages.append({"role": "system", "content": persona})
    if scenario:
        messages.append({"role": "system", "content": f"CURRENT SCENARIO:\n{scenario}"})

    lore_instruction = """=== CANON LORE (USE THIS AS TRUTH) ===
The following excerpts are FACTS about your character and world. Reference these when responding. Do not contradict them.

""" + lore_block + """

=== END LORE ===
Remember: Use this lore as your source of truth. Do not invent conflicting information."""
    messages.append({"role": "system", "content": lore_instruction})

    for m in history[-20:]:
        messages.append(m)

    messages.append({"role": "user", "content": req.message})

    reply = ollama_chat(messages)
    reply = clean_response(reply)

    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})

    return ChatRes(
        session_id=req.session_id,
        character_id=req.character_id,
        reply=reply,
        created=int(time.time()),
    )
