<script setup>
import {
  characterId,
  sessionId,
  charactersBySeries,
  showSessionHistory,
  sessionList,
  activePersona,
  currentView,
} from "../store";
import { useCharacters } from "../composables/useCharacters";
import { useChat } from "../composables/useChat";
import { useSessions } from "../composables/useSessions";
import { usePersona } from "../composables/usePersona";
import { ref } from "vue";

const {
  goToDashboard,
  selectCharacter,
  toggleSeries,
  isSeriesCollapsed,
  genderBadge,
  scenarioLabel,
  getAvatarUrl,
} = useCharacters();

const { uploadFile, ingestUrl } = useChat();
const { clearChat, switchSession, formatSessionDate } = useSessions();
const { openPersonaModal } = usePersona();

const urlToIngest = ref("");

async function handleIngestUrl() {
  await ingestUrl(urlToIngest.value);
  urlToIngest.value = "";
}
</script>

<template>
  <aside class="sidebar">
    <div class="logo">
      <div class="logo-icon">NF</div>
      <span>NoFilter Chat</span>
    </div>

    <!-- Persona button -->
    <button class="sidebar-persona-btn" @click="openPersonaModal">
      <span class="persona-btn-emoji">{{
        activePersona ? activePersona.avatar_emoji : "👤"
      }}</span>
      <div class="sidebar-persona-info" v-if="activePersona">
        <span class="sidebar-persona-name">{{ activePersona.name }}</span>
        <span class="sidebar-persona-gender">{{ activePersona.gender }}</span>
      </div>
      <span v-else class="sidebar-persona-placeholder">Set Persona</span>
    </button>

    <!-- Navigation -->
    <div class="sidebar-nav-btns">
      <button class="btn btn-back" @click="goToDashboard">
        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
          <path
            d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"
          />
        </svg>
        Dashboard
      </button>
      <button class="btn btn-back btn-lorebook" @click="currentView = 'lorebook'">
        &#128218; Lorebook
      </button>
    </div>

    <!-- Character Cards grouped by series -->
    <div class="sidebar-section characters-section">
      <label>Characters</label>
      <div class="character-list">
        <template
          v-for="(chars, series) in charactersBySeries"
          :key="series"
        >
          <div class="series-header" @click="toggleSeries(series)">
            <span
              class="series-arrow"
              :class="{ collapsed: isSeriesCollapsed(series) }"
              >&#9660;</span
            >
            <span class="series-name">{{ series }}</span>
            <span class="series-count">{{ chars.length }}</span>
          </div>
          <div v-if="!isSeriesCollapsed(series)" class="series-characters">
            <div
              v-for="c in chars"
              :key="c.id"
              class="character-card"
              :class="{ selected: c.id === characterId }"
              @click.stop="selectCharacter(c.id)"
            >
              <img
                v-if="getAvatarUrl(c.avatar)"
                :src="getAvatarUrl(c.avatar)"
                :alt="c.name"
                class="card-avatar-img"
                @error="$event.target.style.display = 'none'"
              />
              <div v-if="!getAvatarUrl(c.avatar)" class="card-avatar">
                {{ c.name?.charAt(0) || "?" }}
              </div>
              <div class="card-info">
                <div class="card-name">{{ c.name }}</div>
                <div class="card-meta">
                  <span v-if="genderBadge(c.gender)" class="gender-badge">{{
                    genderBadge(c.gender)
                  }}</span>
                  <span
                    v-if="scenarioLabel(c.id)"
                    class="scenario-badge"
                    >{{ scenarioLabel(c.id) }}</span
                  >
                </div>
                <div v-if="c.title" class="card-role">{{ c.title }}</div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Session section -->
    <div class="sidebar-section">
      <label>Session</label>
      <div class="session-id">
        {{ sessionId ? sessionId.slice(0, 8) + "..." : "None" }}
      </div>
      <div class="session-buttons">
        <button @click="clearChat" class="btn btn-secondary">
          New Session
        </button>
        <button
          @click="showSessionHistory = !showSessionHistory"
          class="btn btn-secondary"
          style="margin-top: 6px"
        >
          {{ showSessionHistory ? "Hide History" : "Session History" }}
        </button>
      </div>

      <!-- Session history dropdown -->
      <div v-if="showSessionHistory" class="session-history">
        <div v-if="sessionList.length === 0" class="session-empty">
          No past sessions
        </div>
        <div
          v-for="s in sessionList"
          :key="s.session_id"
          class="session-item"
          :class="{ active: s.session_id === sessionId }"
          @click="switchSession(s.session_id)"
        >
          <div class="session-item-id">
            {{ s.session_id.slice(0, 8) }}...
          </div>
          <div class="session-item-meta">
            <span>{{ s.message_count }} msgs</span>
            <span>{{ formatSessionDate(s.last_active) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="sidebar-section">
      <label>Add Lore</label>
      <input
        type="file"
        accept=".txt,.md,.pdf,.mp4,.mkv,.avi,.webm,.mp3,.wav"
        @change="uploadFile"
        class="file-input"
      />
    </div>

    <div class="sidebar-section">
      <label>Ingest URL</label>
      <input
        v-model="urlToIngest"
        placeholder="https://..."
        class="input"
        @keydown.enter="handleIngestUrl"
      />
      <button
        @click="handleIngestUrl"
        class="btn btn-secondary"
        :disabled="!urlToIngest.trim()"
      >
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
</template>

<style scoped>
.sidebar {
  width: 300px;
  background: #111118;
  border-right: 1px solid #1f1f2e;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
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

.sidebar-nav-btns {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  color: #8b8b9f;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  font-family: inherit;
  flex: 1;
  justify-content: center;
}

.btn-back:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.sidebar-persona-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 10px;
  color: #c4c4d4;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-family: inherit;
  width: 100%;
  margin-bottom: 12px;
}

.sidebar-persona-btn:hover {
  background: #2a2a3a;
  border-color: #8b5cf6;
}

.persona-btn-emoji {
  font-size: 20px;
}

.sidebar-persona-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.sidebar-persona-name {
  font-weight: 600;
  font-size: 13px;
  color: #e4e4eb;
}

.sidebar-persona-gender {
  font-size: 11px;
  color: #8b5cf6;
}

.sidebar-persona-placeholder {
  color: #6b6b80;
  font-size: 13px;
}

.sidebar-section {
  margin-bottom: 20px;
}

.sidebar-section label {
  display: block;
  font-size: 12px;
  text-transform: uppercase;
  color: #6b6b80;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.character-list {
  max-height: 40vh;
  overflow-y: auto;
  margin-right: -8px;
  padding-right: 8px;
}

.series-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  cursor: pointer;
  color: #8b8b9f;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  user-select: none;
  border-radius: 6px;
  transition: background 0.15s;
}

.series-header:hover {
  background: #1a1a24;
}

.series-arrow {
  font-size: 8px;
  transition: transform 0.2s;
}

.series-arrow.collapsed {
  transform: rotate(-90deg);
}

.series-name {
  flex: 1;
  font-weight: 600;
}

.series-count {
  background: #1f1f2e;
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 11px;
}

.series-characters {
  padding-left: 4px;
  margin-bottom: 8px;
}

.character-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  border: 1px solid transparent;
  margin-bottom: 2px;
  position: relative;
}

.character-card:hover {
  background: #1a1a24;
}

.character-card.selected {
  background: #1a1a2e;
  border-color: #8b5cf6;
}

.card-avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid #2a2a3a;
  flex-shrink: 0;
}

.card-avatar {
  width: 40px;
  height: 40px;
  min-width: 40px;
  background: linear-gradient(135deg, #dc2626, #7c2d12);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  color: white;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.card-name {
  font-size: 14px;
  font-weight: 600;
  color: #e4e4eb;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  gap: 4px;
  margin-top: 2px;
  flex-wrap: wrap;
}

.gender-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  background: #2d1b4e;
  color: #c084fc;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.scenario-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  background: #1b2e4e;
  color: #7dd3fc;
  font-weight: 500;
}

.card-role {
  font-size: 11px;
  color: #6b6b80;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.input {
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

.input:focus {
  border-color: #8b5cf6;
}

.session-id {
  font-family: monospace;
  font-size: 13px;
  color: #8b8b9f;
  margin-bottom: 10px;
}

.session-buttons {
  display: flex;
  flex-direction: column;
}

.session-history {
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #1f1f2e;
  border-radius: 8px;
  background: #0d0d14;
}

.session-empty {
  padding: 12px;
  text-align: center;
  color: #4a4a5a;
  font-size: 12px;
}

.session-item {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #1a1a24;
  transition: background 0.15s;
}

.session-item:last-child {
  border-bottom: none;
}

.session-item:hover {
  background: #1a1a24;
}

.session-item.active {
  background: #1a1a2e;
  border-left: 3px solid #8b5cf6;
}

.session-item-id {
  font-family: monospace;
  font-size: 12px;
  color: #c4c4d4;
  margin-bottom: 2px;
}

.session-item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #6b6b80;
}

.btn {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-family: inherit;
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
  padding-top: 12px;
  border-top: 1px solid #1f1f2e;
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
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Scrollbar */
.character-list::-webkit-scrollbar,
.sidebar::-webkit-scrollbar,
.session-history::-webkit-scrollbar {
  width: 6px;
}

.character-list::-webkit-scrollbar-track,
.sidebar::-webkit-scrollbar-track,
.session-history::-webkit-scrollbar-track {
  background: transparent;
}

.character-list::-webkit-scrollbar-thumb,
.sidebar::-webkit-scrollbar-thumb,
.session-history::-webkit-scrollbar-thumb {
  background: #2a2a3a;
  border-radius: 3px;
}

.character-list::-webkit-scrollbar-thumb:hover,
.sidebar::-webkit-scrollbar-thumb:hover,
.session-history::-webkit-scrollbar-thumb:hover {
  background: #3a3a4a;
}
</style>
