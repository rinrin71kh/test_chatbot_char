# NoFilter Chat — Backend

FastAPI-based backend for the NoFilter Chat application. Handles LLM chat, RAG (Retrieval-Augmented Generation), character management, session persistence, and the Lorebook Reader API.

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
   # Edit .env with your settings
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

# Or with the venv directly
.venv/Scripts/python.exe -m uvicorn app:app --port 8001 --reload
```

The API will be available at `http://127.0.0.1:8001`.

## Dataset Ingestion

Ingest HuggingFace datasets into the RAG system:

```bash
# List available datasets
python ingest_datasets.py --list

# Ingest all datasets + create characters
python ingest_datasets.py --all

# Ingest a specific dataset
python ingest_datasets.py --dataset nsfw_questions

# Create Aratako-derived characters only
python ingest_datasets.py --characters
```

## API Endpoints

### Chat
- `POST /chat` — Stream chat with a character
- `POST /chat/regenerate` — Regenerate a response
- `POST /chat/continue` — Continue generating
- `POST /chat/adapt-lore` — Extract lore adaptations

### Characters
- `GET /characters` — List all characters
- `GET /character/{id}` — Get character details

### Sessions
- `GET /sessions` — List chat sessions
- `GET /history/{session_id}/{character_id}` — Get chat history

### Lorebook
- `GET /lorebook/series` — List all series
- `GET /lorebook/chapter` — Read a chapter
- `GET /lorebook/characters` — List lorebook characters
- `GET /lorebook/character/{id}/lore` — Get character lore

### Persona
- `GET /persona-images` — List available avatar images

### RAG
- `POST /ingest/text` — Ingest text
- `POST /ingest/url` — Ingest from URL
- `POST /ingest/file` — Ingest file upload

## Project Structure

```
backend/
  app.py              — Main FastAPI application
  rag.py              — RAG engine (embeddings, retrieval, ingestion)
  ingest_datasets.py  — HuggingFace dataset ingestion framework
  requirements.txt    — Python dependencies
  .env.example        — Environment configuration template
  lore_index.db       — SQLite database (auto-created)
```
