# NoFilter Chat — Frontend

Vue 3 + TypeScript + Vite frontend for the NoFilter Chat application. Features character selection, real-time streaming chat, persona management, lorebook reader, and a dark-themed UI.

## Prerequisites

- **Node.js 18+** and npm

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env if your backend is on a different URL
   ```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://127.0.0.1:8001` | Backend API URL |

## Running

```bash
# Development server (hot reload)
npm run dev
# or
npx vite

# Build for production
npm run build
# or
npx vite build

# Preview production build
npx vite preview
```

The dev server runs at `http://localhost:5173` by default.

## Features

- **Dashboard** — Character grid with search and tag filtering
- **Chat** — Real-time streaming chat with characters, message editing, regeneration, variant swipe
- **Persona** — Create user personas with emoji or image avatars
- **Lorebook Reader** — Browse series, chapters, and character lore in a manga-reader-inspired UI
- **Memory** — Per-character memory system
- **Mood Analysis** — AI-powered mood/relationship tracking
- **Chat Export** — Export conversations to txt/json

## Project Structure

```
frontend/
  src/
    store.ts                    — Central reactive state
    App.vue                     — Root component with view routing
    composables/
      useChat.ts                — Core chat logic (send, stream, auto-continue)
      useStreaming.ts            — SSE streaming and scroll management
      useCharacters.ts           — Character loading and selection
      usePersona.ts              — User persona CRUD
      useSessions.ts             — Session management
      useLorebook.ts             — Lorebook data loading
      usePayloads.ts             — API payload builders
      useFormatting.ts           — Message formatting
      useMood.ts                 — Mood analysis
      useMemory.ts               — Memory CRUD
      useVariants.ts             — Response variant swipe
      useSuggestions.ts          — AI suggestion chips
      useMessageActions.ts       — Edit, delete, copy, regenerate
      useMessageSearch.ts        — Client-side message search
      useChatExport.ts           — Chat export
      useIngestion.ts            — File/URL ingestion
      useRelationship.ts         — Relationship tracking
    components/
      DashboardView.vue          — Character selection dashboard
      ChatView.vue               — Main chat interface
      ChatInput.vue              — Message input area
      ChatSidebar.vue            — Session and navigation sidebar
      MessageBubble.vue          — Individual message display
      PersonaModal.vue           — Persona creation/editing modal
      LorebookReaderView.vue     — Lorebook reader UI
      MemoryPanel.vue            — Memory management panel
      ChatSettingsPanel.vue      — Chat settings
      RelationshipBar.vue        — Relationship status display
      MessageSearchBar.vue       — Message search UI
  index.html
  vite.config.ts
  tsconfig.json
  .env.example                  — Environment configuration template
```
