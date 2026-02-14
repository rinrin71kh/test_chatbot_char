<script setup>
import { ref, onMounted, watch } from "vue";
import {
  currentView,
  characters,
  characterId,
  sessionId,
  msgs,
  nsfwMode,
  initNsfwMode,
  toggleNsfwMode,
} from "./store";
import { useCharacters } from "./composables/useCharacters";
import { useChat } from "./composables/useChat";
import { usePersona } from "./composables/usePersona";
import { useSessions } from "./composables/useSessions";

import DashboardView from "./components/DashboardView.vue";
import ChatView from "./components/ChatView.vue";
import LorebookReaderView from "./components/LorebookReaderView.vue";
import PersonaModal from "./components/PersonaModal.vue";

const { loadCharacters, loadTags, getLastCharacter } = useCharacters();
const { loadChatHistory } = useChat();
const { loadPersonas } = usePersona();
const { getStoredSession, loadSessionList } = useSessions();

// Apply theme class to body based on mode
function applyTheme() {
  document.body.classList.toggle("sfw-theme", !nsfwMode.value);
  document.body.classList.toggle("nsfw-theme", nsfwMode.value);
}

// ---- Draggable FAB ----
const fabRef = ref(null);
const fabPos = ref({ x: -1, y: -1 }); // -1 means use CSS default
let dragging = false;
let dragStartX = 0;
let dragStartY = 0;
let dragMoved = false;

function onFabPointerDown(e) {
  dragging = true;
  dragMoved = false;
  const el = fabRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  dragStartX = e.clientX - rect.left;
  dragStartY = e.clientY - rect.top;
  el.setPointerCapture(e.pointerId);
  e.preventDefault();
}

function onFabPointerMove(e) {
  if (!dragging) return;
  dragMoved = true;
  const x = e.clientX - dragStartX;
  const y = e.clientY - dragStartY;
  // Clamp to viewport
  const maxX = window.innerWidth - 40;
  const maxY = window.innerHeight - 40;
  fabPos.value = {
    x: Math.max(0, Math.min(x, maxX)),
    y: Math.max(0, Math.min(y, maxY)),
  };
}

function onFabPointerUp() {
  dragging = false;
}

function onFabClick() {
  // Only toggle if the user didn't drag
  if (!dragMoved) {
    toggleNsfwMode();
  }
}

// ---- Startup ----
onMounted(async () => {
  initNsfwMode();
  applyTheme();
  loadPersonas();
  await Promise.all([loadCharacters(), loadTags()]);

  // Auto-resume last session
  const lastChar = getLastCharacter();
  if (lastChar && characters.value.find((c) => c.id === lastChar)) {
    const sessId = getStoredSession(lastChar);
    if (sessId) {
      const history = await loadChatHistory(sessId, lastChar);
      if (history.length > 0) {
        characterId.value = lastChar;
        sessionId.value = sessId;
        msgs.value = history;
        loadSessionList(lastChar);
        currentView.value = "chat";
        return;
      }
    }
  }
});

// React to mode changes
watch(nsfwMode, () => applyTheme());
</script>

<template>
  <div class="app" :class="{ 'sfw': !nsfwMode, 'nsfw': nsfwMode }">
    <!-- Dashboard View -->
    <DashboardView v-if="currentView === 'dashboard'" />

    <!-- Chat View -->
    <template v-if="currentView === 'chat'">
      <ChatView />
    </template>

    <!-- Lorebook Reader View -->
    <LorebookReaderView v-if="currentView === 'lorebook'" />

    <!-- Persona Modal (global) -->
    <PersonaModal />

    <!-- Floating mode toggle button (draggable) -->
    <button
      ref="fabRef"
      class="mode-toggle-fab"
      :class="{ active: nsfwMode, dragged: fabPos.x >= 0 }"
      :style="fabPos.x >= 0 ? { left: fabPos.x + 'px', top: fabPos.y + 'px', right: 'auto', bottom: 'auto' } : {}"
      @pointerdown="onFabPointerDown"
      @pointermove="onFabPointerMove"
      @pointerup="onFabPointerUp"
      @click="onFabClick"
      :title="nsfwMode ? 'Switch to DramaRealm (SFW)' : 'Switch to NoFilter (18+)'"
    >
      <span class="fab-dot"></span>
    </button>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ===== NSFW Theme (default dark purple) ===== */
body {
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  background: #0a0a0f;
  color: #e4e4eb;
  transition: background 0.4s ease, color 0.4s ease;
}

body.nsfw-theme {
  background: #0a0a0f;
  color: #e4e4eb;
}

.app {
  display: flex;
  height: 100vh;
  background: #0a0a0f;
  transition: background 0.4s ease;
  position: relative;
}

.app.nsfw {
  background: #0a0a0f;
}

/* ===== SFW Theme (blue sky / light drama) ===== */
body.sfw-theme {
  background: #0e1628;
  color: #d8e2f0;
}

.app.sfw {
  background: linear-gradient(180deg, #0e1628 0%, #152238 40%, #1a2a45 100%);
}

/* ===== Floating Mode Toggle Button ===== */
.mode-toggle-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #2a2a3a;
  background: #1a1a24;
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
  z-index: 9999;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
  opacity: 0.6;
  touch-action: none;
  user-select: none;
}

.mode-toggle-fab:active {
  cursor: grabbing;
}

.mode-toggle-fab:hover {
  opacity: 1;
  transform: scale(1.15);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
}

.mode-toggle-fab .fab-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #444;
  transition: all 0.3s ease;
}

/* SFW state — dim grey dot */
.mode-toggle-fab:not(.active) .fab-dot {
  background: radial-gradient(circle, #666 0%, #333 100%);
}

.mode-toggle-fab:not(.active):hover .fab-dot {
  background: radial-gradient(circle, #ef4444 30%, #991b1b 100%);
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

/* NSFW active state — glowing red dot */
.mode-toggle-fab.active {
  border-color: #7f1d1d;
  background: #1a0a0a;
}

.mode-toggle-fab.active .fab-dot {
  background: radial-gradient(circle, #ef4444 30%, #b91c1c 100%);
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.6);
}

.mode-toggle-fab.active:hover .fab-dot {
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.8);
}
</style>
