<script setup>
import { onMounted } from "vue";
import {
  currentView,
  characters,
  characterId,
  sessionId,
  msgs,
  initNsfwMode,
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

// ---- Startup ----
onMounted(async () => {
  initNsfwMode();
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
</script>

<template>
  <div class="app">
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
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  background: #0a0a0f;
  color: #e4e4eb;
}

.app {
  display: flex;
  height: 100vh;
  background: #0a0a0f;
}
</style>
