<script setup>
import { ref } from "vue";
import {
  currentCharacter,
  characterMood,
  activePersona,
  showScenario,
  showMemoryPanel,
  showSettingsPanel,
  searchOpen,
} from "../store";
import { useCharacters } from "../composables/useCharacters";
import { useChatExport } from "../composables/useChatExport";

const { goToDashboard, genderBadge, getAvatarUrl } = useCharacters();
const { exportAsText, exportAsJson } = useChatExport();
const showExportMenu = ref(false);
</script>

<template>
  <header class="chat-header">
    <div class="character-info">
      <button
        class="back-btn-mobile"
        @click="goToDashboard"
        title="Back to Dashboard"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path
            d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"
          />
        </svg>
      </button>
      <img
        v-if="getAvatarUrl(currentCharacter.avatar)"
        :src="getAvatarUrl(currentCharacter.avatar)"
        :alt="currentCharacter.name"
        class="avatar-img"
        @error="$event.target.style.display = 'none'"
      />
      <div v-if="!getAvatarUrl(currentCharacter.avatar)" class="avatar">
        {{ currentCharacter.name?.charAt(0) || "?" }}
      </div>
      <div class="header-details">
        <div class="header-top-row">
          <div class="character-name">{{ currentCharacter.name }}</div>
          <span
            v-if="genderBadge(currentCharacter.gender)"
            class="header-gender-badge"
            >{{ genderBadge(currentCharacter.gender) }}</span
          >
        </div>
        <div class="character-title">
          <span v-if="currentCharacter.series" class="header-series">{{
            currentCharacter.series
          }}</span>
          <span
            v-if="currentCharacter.series && currentCharacter.title"
            class="header-sep"
            >&middot;</span
          >
          <span v-if="currentCharacter.title">{{
            currentCharacter.title
          }}</span>
        </div>
      </div>
    </div>
    <div class="header-right">
      <!-- Mood indicator (always visible) -->
      <div
        v-if="characterMood"
        class="mood-badge"
        :title="characterMood.description"
      >
        <span class="mood-emoji">{{ characterMood.emoji }}</span>
        <span class="mood-text">{{ characterMood.mood }}</span>
        <div
          class="mood-bar"
          :style="{ width: (characterMood.intensity || 5) * 10 + '%' }"
        ></div>
      </div>

      <div v-if="activePersona" class="playing-as-badge">
        <span class="playing-as-emoji">{{
          activePersona.avatar_emoji
        }}</span>
        <span
          >Playing as <strong>{{ activePersona.name }}</strong></span
        >
      </div>

      <!-- Memory button -->
      <button
        class="header-icon-btn"
        :class="{ active: showMemoryPanel }"
        @click="showMemoryPanel = !showMemoryPanel"
        title="Memories"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"/>
          <line x1="10" y1="22" x2="14" y2="22"/>
        </svg>
      </button>

      <!-- Search button -->
      <button
        class="header-icon-btn"
        :class="{ active: searchOpen }"
        @click="searchOpen = !searchOpen"
        title="Search Messages"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
      </button>

      <!-- Export button -->
      <div class="export-wrapper">
        <button
          class="header-icon-btn"
          @click="showExportMenu = !showExportMenu"
          title="Export Chat"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        </button>
        <div v-if="showExportMenu" class="export-menu">
          <button @click="exportAsText(); showExportMenu = false">Export as .txt</button>
          <button @click="exportAsJson(); showExportMenu = false">Export as .json</button>
        </div>
      </div>

      <!-- Settings button -->
      <button
        class="header-icon-btn"
        :class="{ active: showSettingsPanel }"
        @click="showSettingsPanel = !showSettingsPanel"
        title="Chat Settings"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>

      <button
        v-if="currentCharacter.scenario"
        @click="showScenario = !showScenario"
        class="scenario-toggle"
        :class="{ active: showScenario }"
      >
        Scenario
      </button>
    </div>
  </header>

  <!-- Scenario Panel -->
  <div
    v-if="showScenario && currentCharacter.scenario"
    class="scenario-panel"
  >
    <div class="scenario-label">Current Scenario</div>
    <div class="scenario-text">{{ currentCharacter.scenario }}</div>
  </div>
</template>

<style scoped>
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

.header-details {
  display: flex;
  flex-direction: column;
}

.header-top-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-gender-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 6px;
  background: #2d1b4e;
  color: #c084fc;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.header-series {
  color: #8b5cf6;
  font-weight: 500;
}

.header-sep {
  color: #3a3a4a;
  margin: 0 2px;
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
  flex-shrink: 0;
}

.avatar-img {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid #2a2a3a;
  flex-shrink: 0;
}

.character-name {
  font-size: 18px;
  font-weight: 600;
}

.character-title {
  font-size: 13px;
  color: #6b6b80;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Mood indicator */
.mood-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  font-size: 12px;
  color: #c4c4d4;
  position: relative;
  overflow: hidden;
}

.mood-emoji {
  font-size: 16px;
}

.mood-text {
  text-transform: capitalize;
  font-weight: 500;
}

.mood-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: linear-gradient(90deg, #8b5cf6, #ec4899);
  transition: width 0.5s ease;
}

.playing-as-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #1a1a2e, #2d1b4e);
  border: 1px solid #4c1d95;
  border-radius: 8px;
  font-size: 12px;
  color: #c4b5fd;
  white-space: nowrap;
}

.playing-as-emoji {
  font-size: 16px;
}

.playing-as-badge strong {
  color: #e4e4eb;
}

.header-icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #2a2a3a;
  background: #1a1a24;
  color: #8b8b9f;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.header-icon-btn:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.header-icon-btn.active {
  background: #6d28d9;
  border-color: #8b5cf6;
  color: white;
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
  font-family: inherit;
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

.back-btn-mobile {
  display: none;
  background: none;
  border: none;
  color: #8b8b9f;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: color 0.2s;
}

.back-btn-mobile:hover {
  color: #e4e4eb;
}

/* Export menu */
.export-wrapper {
  position: relative;
}

.export-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 6px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  overflow: hidden;
  z-index: 30;
  min-width: 150px;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.export-menu button {
  display: block;
  width: 100%;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #c4c4d4;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;
}

.export-menu button:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}
</style>
