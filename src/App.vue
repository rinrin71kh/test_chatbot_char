<script setup>
import { ref, onMounted, nextTick, watch, computed } from "vue";
import axios from "axios";
import ingridAvatar from "./assets/ingrid.webp";

const API = "http://127.0.0.1:8001";

const sessionId = ref(crypto.randomUUID());
const characters = ref([]);
const characterId = ref("ingrid");

const input = ref("");
const loading = ref(false);
const msgs = ref([]);

const chatContainer = ref(null);
const showScenario = ref(true);

// Get current character data
const currentCharacter = computed(() => {
  return characters.value.find(c => c.id === characterId.value) || {
    name: "Character",
    title: "",
    scenario: "",
    greeting: ""
  };
});

// Avatar mapping - add more characters here as needed
const avatarMap = {
  "ingrid.webp": ingridAvatar,
};

function getAvatar(avatarFile) {
  return avatarMap[avatarFile] || null;
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
}

watch(msgs, scrollToBottom, { deep: true });

async function loadCharacters() {
  try {
    const res = await axios.get(`${API}/characters`);
    characters.value = res.data;
    if (!characters.value.find(c => c.id === characterId.value) && characters.value.length) {
      characterId.value = characters.value[0].id;
    }
    // Set initial greeting
    initializeChat();
  } catch (e) {
    console.error("Failed to load characters:", e);
    // Fallback greeting
    msgs.value = [
      { role: "assistant", content: "*Ingrid glances up from her desk.*\n\n…State your business." }
    ];
  }
}

function initializeChat() {
  const char = currentCharacter.value;
  msgs.value = [];
  if (char.greeting) {
    msgs.value.push({ role: "assistant", content: char.greeting });
  }
}

// Watch for character changes
watch(characterId, () => {
  sessionId.value = crypto.randomUUID();
  initializeChat();
});

async function send() {
  const text = input.value.trim();
  if (!text || loading.value) return;

  msgs.value.push({ role: "user", content: text });
  input.value = "";
  loading.value = true;

  try {
    const res = await axios.post(`${API}/chat`, {
      session_id: sessionId.value,
      character_id: characterId.value,
      message: text,
      temperature: 0.8,
    });
    msgs.value.push({ role: "assistant", content: res.data.reply });
  } catch (e) {
    msgs.value.push({ role: "assistant", content: "*Expression darkens.*\n\n…Tch. Something interfered with our connection. Try again." });
  } finally {
    loading.value = false;
  }
}

async function uploadFile(ev) {
  const file = ev.target.files?.[0];
  if (!file) return;

  const form = new FormData();
  form.append("file", file);

  loading.value = true;
  msgs.value.push({ role: "system", content: `Uploading lore: ${file.name}...` });

  try {
    const res = await axios.post(`${API}/ingest/file?character_id=${encodeURIComponent(characterId.value)}`, form, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    msgs.value.push({ role: "assistant", content: `*Absorbs the new information.*\n\nHmph. ${res.data.chunks} fragments of knowledge acquired. Continue.` });
  } catch (e) {
    msgs.value.push({ role: "assistant", content: "…The lore failed to integrate. Check your file." });
  } finally {
    loading.value = false;
    ev.target.value = "";
  }
}

const urlToIngest = ref("");
async function ingestUrl() {
  const url = urlToIngest.value.trim();
  if (!url) return;

  loading.value = true;
  msgs.value.push({ role: "system", content: `Ingesting: ${url}...` });

  try {
    const res = await axios.post(`${API}/ingest/url`, {
      character_id: characterId.value,
      url
    });
    msgs.value.push({ role: "assistant", content: `*Processes the external knowledge.*\n\n${res.data.chunks} fragments absorbed. What else?` });
  } catch (e) {
    msgs.value.push({ role: "assistant", content: "…Failed to retrieve that location. Verify your link." });
  } finally {
    loading.value = false;
    urlToIngest.value = "";
  }
}

function clearChat() {
  sessionId.value = crypto.randomUUID();
  initializeChat();
}

function formatMessage(content) {
  // Convert *text* to italic spans for roleplay actions
  return content.replace(/\*([^*]+)\*/g, '<span class="action">*$1*</span>');
}

onMounted(loadCharacters);
</script>

<template>
  <div class="app">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">NF</div>
        <span>NoFilter Chat</span>
      </div>

      <div class="sidebar-section">
        <label>Character</label>
        <select v-model="characterId" class="select">
          <option v-for="c in characters" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
      </div>

      <div class="sidebar-section">
        <label>Session</label>
        <div class="session-id">{{ sessionId.slice(0, 8) }}...</div>
        <button @click="clearChat" class="btn btn-secondary">New Session</button>
      </div>

      <div class="sidebar-section">
        <label>Add Lore</label>
        <input type="file" accept=".txt,.md,.pdf,.mp4,.mkv,.avi,.webm,.mp3,.wav" @change="uploadFile" class="file-input" />
      </div>

      <div class="sidebar-section">
        <label>Ingest URL</label>
        <input
          v-model="urlToIngest"
          placeholder="https://..."
          class="input"
          @keydown.enter="ingestUrl"
        />
        <button @click="ingestUrl" class="btn btn-secondary" :disabled="!urlToIngest.trim()">
          Fetch
        </button>
      </div>

      <div class="sidebar-footer">
        <div class="status-badge">
          <span class="status-dot"></span>
          Local & Uncensored
        </div>
      </div>
    </aside>

    <!-- Main Chat -->
    <main class="chat-area">
      <header class="chat-header">
        <div class="character-info">
          <img
            v-if="getAvatar(currentCharacter.avatar)"
            :src="getAvatar(currentCharacter.avatar)"
            :alt="currentCharacter.name"
            class="avatar-img"
          />
          <div v-else class="avatar">{{ currentCharacter.name?.charAt(0) || '?' }}</div>
          <div>
            <div class="character-name">{{ currentCharacter.name }}</div>
            <div class="character-title">{{ currentCharacter.title }}</div>
          </div>
        </div>
        <button
          v-if="currentCharacter.scenario"
          @click="showScenario = !showScenario"
          class="scenario-toggle"
          :class="{ active: showScenario }"
        >
          Scenario
        </button>
      </header>

      <!-- Scenario Panel -->
      <div v-if="showScenario && currentCharacter.scenario" class="scenario-panel">
        <div class="scenario-label">Current Scenario</div>
        <div class="scenario-text">{{ currentCharacter.scenario }}</div>
      </div>

      <div class="messages" ref="chatContainer">
        <div v-for="(m, i) in msgs" :key="i" class="message" :class="m.role">
          <div class="message-content">
            <template v-if="m.role === 'assistant'">
              <img
                v-if="getAvatar(currentCharacter.avatar)"
                :src="getAvatar(currentCharacter.avatar)"
                :alt="currentCharacter.name"
                class="msg-avatar-img"
              />
              <div v-else class="msg-avatar">{{ currentCharacter.name?.charAt(0) || '?' }}</div>
            </template>
            <div class="bubble" v-html="formatMessage(m.content)"></div>
          </div>
        </div>

        <div v-if="loading" class="message assistant">
          <div class="message-content">
            <img
              v-if="getAvatar(currentCharacter.avatar)"
              :src="getAvatar(currentCharacter.avatar)"
              :alt="currentCharacter.name"
              class="msg-avatar-img"
            />
            <div v-else class="msg-avatar">{{ currentCharacter.name?.charAt(0) || '?' }}</div>
            <div class="bubble typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <footer class="input-area">
        <div class="input-container">
          <textarea
            v-model="input"
            @keydown.enter.exact.prevent="send"
            placeholder="Type your message... (Enter to send)"
            rows="1"
            class="chat-input"
          ></textarea>
          <button @click="send" :disabled="loading || !input.trim()" class="send-btn">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </footer>
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: #0a0a0f;
  color: #e4e4eb;
}

.app {
  display: flex;
  height: 100vh;
  background: #0a0a0f;
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: #111118;
  border-right: 1px solid #1f1f2e;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8b5cf6, #ec4899);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.logo span {
  font-size: 18px;
  font-weight: 600;
}

.sidebar-section {
  margin-bottom: 24px;
}

.sidebar-section label {
  display: block;
  font-size: 12px;
  text-transform: uppercase;
  color: #6b6b80;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.select, .input {
  width: 100%;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  color: #e4e4eb;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.select:focus, .input:focus {
  border-color: #8b5cf6;
}

.session-id {
  font-family: monospace;
  font-size: 13px;
  color: #8b8b9f;
  margin-bottom: 10px;
}

.btn {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: #1f1f2e;
  color: #e4e4eb;
  border: 1px solid #2a2a3a;
}

.btn-secondary:hover {
  background: #2a2a3a;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.file-input {
  width: 100%;
  font-size: 13px;
  color: #8b8b9f;
}

.file-input::file-selector-button {
  background: #1f1f2e;
  border: 1px solid #2a2a3a;
  color: #e4e4eb;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 10px;
}

.sidebar-footer {
  margin-top: auto;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6b6b80;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Chat Area */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #0a0a0f;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #1f1f2e;
  background: #0f0f16;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.character-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #dc2626, #7c2d12);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 20px;
  color: white;
}

.avatar-img {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid #2a2a3a;
}

.character-name {
  font-size: 18px;
  font-weight: 600;
}

.character-title {
  font-size: 13px;
  color: #6b6b80;
}

.scenario-toggle {
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  color: #8b8b9f;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.scenario-toggle:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.scenario-toggle.active {
  background: #6d28d9;
  border-color: #8b5cf6;
  color: white;
}

/* Scenario Panel */
.scenario-panel {
  background: linear-gradient(135deg, #1a1a24, #13131a);
  border-bottom: 1px solid #2a2a3a;
  padding: 16px 24px;
}

.scenario-label {
  font-size: 11px;
  text-transform: uppercase;
  color: #8b5cf6;
  margin-bottom: 8px;
  letter-spacing: 1px;
  font-weight: 600;
}

.scenario-text {
  font-size: 14px;
  color: #a0a0b0;
  line-height: 1.6;
  font-style: italic;
}

/* Messages */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.system {
  justify-content: center;
}

.message-content {
  display: flex;
  gap: 12px;
  max-width: 75%;
}

.message.user .message-content {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  background: linear-gradient(135deg, #dc2626, #7c2d12);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.msg-avatar-img {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid #2a2a3a;
}

.bubble {
  padding: 14px 18px;
  border-radius: 18px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message.assistant .bubble {
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-top-left-radius: 4px;
}

.message.user .bubble {
  background: linear-gradient(135deg, #6d28d9, #4c1d95);
  border-top-right-radius: 4px;
}

.message.system .bubble {
  background: transparent;
  color: #6b6b80;
  font-size: 13px;
  padding: 8px 16px;
}

.bubble :deep(.action) {
  color: #a78bfa;
  font-style: italic;
}

/* Typing indicator */
.typing {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
}

.typing span {
  width: 8px;
  height: 8px;
  background: #6b6b80;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing span:nth-child(1) { animation-delay: 0s; }
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
}

/* Input Area */
.input-area {
  padding: 20px 24px;
  border-top: 1px solid #1f1f2e;
  background: #0f0f16;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  color: #e4e4eb;
  padding: 14px 18px;
  border-radius: 14px;
  font-size: 15px;
  resize: none;
  outline: none;
  font-family: inherit;
  line-height: 1.4;
  max-height: 120px;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #8b5cf6;
}

.chat-input::placeholder {
  color: #4a4a5a;
}

.send-btn {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, opacity 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 22px;
  height: 22px;
}

/* Scrollbar */
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
</style>
