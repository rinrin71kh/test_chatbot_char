# NoFilter Chat — Backend

FastAPI-based backend for the NoFilter Chat application. Handles AI chat, RAG (Retrieval-Augmented Generation), character management, session persistence, and the Lorebook Reader API.

## How It Works

The backend connects your browser to a local Ollama LLM. When you send a message:

1. Your message is embedded and matched against the RAG database for relevant lore
2. The character's system prompt, lore excerpts, and conversation history are assembled
3. The full prompt is sent to Ollama, which streams back the response token-by-token
4. Messages are saved to SQLite for persistence across sessions

## Prerequisites

- **Python 3.10+**
- **Ollama** running locally (or remotely) with models pulled:
  ```bash
  ollama pull mannix/llama3.1-8b-abliterated
  ollama pull nomic-embed-text
  ```

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate it:**
   ```bash
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (or leave defaults for local use)
   ```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama server URL |
| `CHAT_MODEL` | `mannix/llama3.1-8b-abliterated` | LLM model for chat |
| `EMBED_MODEL` | `nomic-embed-text` | Model for text embeddings |
| `DB_PATH` | `lore_index.db` | SQLite database path |
| `LOREBOOK_PATH` | `../LoreBook` | Path to LoreBook directory |
| `CHARACTERS_PATH` | `../LoreBook/characters` | Path to character definitions |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8001` | Server port |
| `CORS_ORIGINS` | (localhost:5173/5174) | Comma-separated allowed origins |

## Running

```bash
# Development (with auto-reload)
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

# Or with the venv directly (Windows)
.venv\Scripts\python.exe -m uvicorn app:app --port 8001 --reload
```

The API will be available at `http://127.0.0.1:8001`.

On startup, the backend:
1. Loads all characters from `LoreBook/characters/` (cached after first scan)
2. Ingests lorebook text files into the RAG database (skipped if already ingested)
3. Reports startup time and character count

## Dataset Ingestion

Enrich the AI's knowledge by ingesting 27 curated HuggingFace datasets:

```bash
# List available datasets
python ingest_datasets.py --list

# Ingest all datasets + create characters
python ingest_datasets.py --all

# Ingest a specific dataset by name
python ingest_datasets.py --dataset nsfw_questions

# Create Aratako-derived characters only (no dataset download)
python ingest_datasets.py --characters
```

Datasets cover: roleplay dialogue, erotic literature, character descriptions, drama/romance, and image tag metadata.

## API Endpoints

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Stream chat with a character (SSE) |
| POST | `/chat/regenerate` | Regenerate the last AI response |
| POST | `/chat/continue` | Continue generating from where AI stopped |
| POST | `/chat/adapt-lore` | Extract lore adaptations from conversation |

### Characters
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/characters` | List all characters |
| GET | `/character/{id}` | Get character details + system prompt |

### Sessions & History
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sessions` | List chat sessions for a character |
| GET | `/history/{session_id}/{character_id}` | Get full chat history |
| DELETE | `/message/{id}` | Delete a specific message |
| PUT | `/message/{id}` | Edit a message's content |

### Lorebook
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/lorebook/series` | List all series with cover info |
| GET | `/lorebook/chapter` | Read a chapter's text + images |
| GET | `/lorebook/characters` | List lorebook characters |
| GET | `/lorebook/character/{id}/lore` | Get character's lore text |

### Persona & Memory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/persona-images` | List available avatar images |
| GET | `/memories` | Get character's memories |
| POST | `/memory` | Save a new memory |
| DELETE | `/memory/{id}` | Delete a memory |

### RAG Ingestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest/text` | Ingest raw text |
| POST | `/ingest/url` | Ingest from URL (HTML, PDF, YouTube, video sites) |
| POST | `/ingest/file` | Ingest file upload (PDF, TXT, video, audio) |

### Mood & Relationships
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mood/analyze` | Analyze emotional mood of conversation |
| GET | `/relationship` | Get relationship scores |

## Startup Performance

The backend uses caching to minimize startup time:
- **Character cache** — Characters are cached to `.character_cache.json`. Only rescans the filesystem when character files change.
- **Lorebook deduplication** — Checks if lore sources already exist in the DB before calling the embedding API. First startup may take minutes (embedding all lore); subsequent startups take seconds.

## Project Structure

```
backend/
  app.py              — Main FastAPI application (endpoints, character loading, lorebook)
  rag.py              — RAG engine (embeddings, retrieval, ingestion, chat history)
  ingest_datasets.py  — HuggingFace dataset ingestion framework (27 datasets)
  requirements.txt    — Python dependencies
  .env.example        — Environment configuration template
  lore_index.db       — SQLite database (auto-created on first run)
  .character_cache.json — Character cache (auto-created)
```
