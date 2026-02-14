<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import {
  msgs,
  loading,
  streamingText,
  currentCharacter,
  showMemoryPanel,
  showSettingsPanel,
  characterMood,
  searchOpen,
} from "../store";
import { useChat } from "../composables/useChat";
import { useCharacters } from "../composables/useCharacters";

import ChatSidebar from "./ChatSidebar.vue";
import ChatHeader from "./ChatHeader.vue";
import MessageBubble from "./MessageBubble.vue";
import ChatInput from "./ChatInput.vue";
import TypingIndicator from "./TypingIndicator.vue";
import MemoryPanel from "./MemoryPanel.vue";
import ChatSettingsPanel from "./ChatSettingsPanel.vue";
import RelationshipBar from "./RelationshipBar.vue";
import MessageSearchBar from "./MessageSearchBar.vue";

const { setChatContainer } = useChat();
const { getAvatarUrl } = useCharacters();

const chatContainer = ref(null);

onMounted(() => {
  setChatContainer(chatContainer.value);
});

// Mood ambient color map
const moodColorMap: Record<string, string> = {
  aroused: "rgba(88, 28, 135, 0.08)",
  angry: "rgba(153, 27, 27, 0.08)",
  playful: "rgba(13, 148, 136, 0.06)",
  happy: "rgba(234, 179, 8, 0.05)",
  sad: "rgba(30, 64, 175, 0.06)",
  embarrassed: "rgba(219, 39, 119, 0.06)",
  loving: "rgba(244, 63, 94, 0.07)",
  lustful: "rgba(126, 34, 206, 0.1)",
  neutral: "transparent",
};

const moodBgColor = computed(() => {
  const mood = (characterMood.value?.mood || "neutral").toLowerCase();
  return moodColorMap[mood] || "transparent";
});
</script>

<template>
  <!-- Sidebar -->
  <ChatSidebar />

  <!-- Main Chat -->
  <main class="chat-area" :style="{ '--mood-bg': moodBgColor }">
    <ChatHeader />

    <!-- Relationship bars -->
    <RelationshipBar />

    <!-- Search bar -->
    <MessageSearchBar />

    <!-- Memory Panel (slide-out) -->
    <MemoryPanel v-if="showMemoryPanel" />

    <!-- Settings Panel (slide-out) -->
    <ChatSettingsPanel v-if="showSettingsPanel" />

    <div class="messages" ref="chatContainer">
      <MessageBubble
        v-for="(m, i) in msgs"
        :key="m.id || i"
        :msg="m"
        :index="i"
        :is-last="i === msgs.length - 1"
        :total-messages="msgs.length"
      />

      <TypingIndicator v-if="loading && !streamingText" />
    </div>

    <ChatInput />
  </main>
</template>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #0a0a0f;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

.messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--mood-bg, transparent);
  transition: background 2s ease;
}

.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: transparent;
}

.messages::-webkit-scrollbar-thumb {
  background: #2a2a3a;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: #3a3a4a;
}

/* Search highlight animation (global for child component) */
:deep(.search-highlight) {
  animation: highlightPulse 2s ease;
}

@keyframes highlightPulse {
  0%, 100% { background: transparent; }
  25% { background: rgba(139, 92, 246, 0.15); }
  50% { background: rgba(139, 92, 246, 0.1); }
}
</style>
