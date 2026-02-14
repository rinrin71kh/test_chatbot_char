# NoFilter Chat — Frontend

Vue 3 + TypeScript + Vite frontend for the NoFilter Chat application. Features a character selection dashboard, real-time streaming chat, persona management, lorebook reader, and a dark-themed UI.

## How to Access

After starting both the backend and frontend:

| Mode | URL | Description |
|------|-----|-------------|
| **DramaRealm** (SFW) | `http://localhost:5173` | Default mode — drama/romance characters only, blue/cyan theme |
| **NoFilter Chat** (NSFW) | `http://localhost:5173/#/18` | Full mode — all characters, lorebook, purple/pink theme |

Switch between modes by adding or removing `#/18` from the URL. No page reload needed.

## What You'll See

### Dashboard
The landing page shows a grid of available characters. Search by name, series, or tags. Click a character to start chatting.

### Chat View
- **Real-time streaming** — AI responses appear word-by-word as they're generated
- **Message actions** — Edit, delete, copy, or regenerate any message
- **Response variants** — Swipe left/right to see alternative AI responses
- **Auto-continue** — AI keeps generating if a response ends mid-scene
- **Suggestion chips** — AI-generated reply suggestions below the input
- **Sidebar** — Switch characters, manage sessions, access settings

### Persona
Click the persona button in the header to create your identity:
- Set your name, gender, appearance, and personality
- Choose an emoji avatar or pick from imported dataset images
- Characters will address you by name and reference your traits

### Lorebook Reader (NSFW mode only)
A manga-reader-inspired UI for browsing:
- Light novel series with chapter navigation
- Character lore and backstories
- Chapter images and illustrations
- Previous/next chapter navigation

### Settings Panel
Customize AI behavior per-session:
- Temperature (creativity)
- Response length (short/medium/long)
- Writing style (dialogue/balanced/descriptive)
- Perspective (first-person/third-person)
- Typing speed animation

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

# Build for production
npm run build

# Preview production build
npx vite preview
```

The dev server runs at `http://localhost:5173` by default.

## Project Structure

```
frontend/
  src/
    store.ts                    — Central reactive state (shared across all modules)
    App.vue                     — Root component with view routing
    composables/
      useChat.ts                — Core chat logic (send, stream, auto-continue)
      useStreaming.ts           — SSE streaming and scroll management
      useCharacters.ts          — Character loading and selection
      usePersona.ts             — User persona CRUD
      useSessions.ts            — Session management
      useLorebook.ts            — Lorebook data loading
      usePayloads.ts            — API payload builders
      useFormatting.ts          — Message formatting (markdown, timestamps)
      useMood.ts                — Mood analysis
      useMemory.ts              — Memory CRUD
      useVariants.ts            — Response variant swipe
      useSuggestions.ts         — AI suggestion chips
      useMessageActions.ts      — Edit, delete, copy, regenerate
      useMessageSearch.ts       — Client-side message search
      useChatExport.ts          — Chat export (TXT/JSON)
      useIngestion.ts           — File/URL ingestion
      useRelationship.ts        — Relationship tracking
    components/
      DashboardView.vue         — Character selection dashboard
      ChatView.vue              — Main chat interface
      ChatInput.vue             — Message input area
      ChatSidebar.vue           — Session and navigation sidebar
      MessageBubble.vue         — Individual message display
      PersonaModal.vue          — Persona creation/editing modal
      LorebookReaderView.vue    — Lorebook reader UI
      MemoryPanel.vue           — Memory management panel
      ChatSettingsPanel.vue     — Chat settings
      RelationshipBar.vue       — Relationship status display
      MessageSearchBar.vue      — Message search UI
  index.html
  vite.config.ts
  tsconfig.json
  .env.example                  — Environment configuration template
```
