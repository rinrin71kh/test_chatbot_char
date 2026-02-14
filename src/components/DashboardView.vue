<script setup lang="ts">
import {
  searchQuery,
  allTags,
  activeTags,
  filteredCharacters,
  activePersona,
  currentView,
  nsfwMode,
  API,
} from "../store";
import { useCharacters } from "../composables/useCharacters";
import { usePersona } from "../composables/usePersona";

const { toggleTag, clearTagFilter, openCharacterChat, getAvatarUrl } =
  useCharacters();
const { openPersonaModal } = usePersona();

function openLorebook() {
  currentView.value = "lorebook";
}

function getPersonaAvatar(): { type: "emoji" | "image"; value: string } | null {
  const p = activePersona.value;
  if (!p) return null;
  if (p.avatar_image) return { type: "image", value: p.avatar_image.startsWith("/") ? `${API}${p.avatar_image}` : p.avatar_image };
  return { type: "emoji", value: p.avatar_emoji || "👤" };
}
</script>

<template>
  <div class="dashboard">
    <header class="dash-header">
      <div class="dash-header-top">
        <div class="header-spacer"></div>
        <div class="logo">
          <div class="logo-icon" :class="{ nsfw: nsfwMode }">{{ nsfwMode ? 'NF' : 'DR' }}</div>
          <span>{{ nsfwMode ? 'NoFilter Chat' : 'DramaRealm' }}</span>
        </div>
        <div class="header-actions">
          <button
            v-if="nsfwMode"
            class="action-btn"
            @click="openLorebook"
            title="Browse lorebook"
          >
            <span class="action-btn-emoji">&#128218;</span>
            <span class="action-btn-label">Lorebook</span>
          </button>
          <button
            class="action-btn"
            @click="openPersonaModal"
            :title="
              activePersona
                ? 'Playing as ' + activePersona.name
                : 'Set up your persona'
            "
          >
            <img
              v-if="getPersonaAvatar()?.type === 'image'"
              :src="getPersonaAvatar()!.value"
              class="action-btn-avatar"
            />
            <span v-else class="action-btn-emoji">{{
              getPersonaAvatar()?.value || "👤"
            }}</span>
            <span class="action-btn-label">{{
              activePersona ? activePersona.name : "Persona"
            }}</span>
          </button>
        </div>
      </div>
      <div class="dash-subtitle">{{ nsfwMode ? 'Choose a character to begin your story' : 'Choose a character for your drama' }}</div>
    </header>

    <!-- Search bar -->
    <div class="search-bar">
      <svg
        class="search-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.35-4.35" />
      </svg>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search characters by name, series, tags..."
        class="search-input"
      />
      <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
        &#10005;
      </button>
    </div>

    <!-- Tag filter bar -->
    <div class="tag-bar">
      <button
        class="tag-chip"
        :class="{ active: activeTags.length === 0 }"
        @click="clearTagFilter"
      >
        All
      </button>
      <button
        v-for="tag in allTags"
        :key="tag"
        class="tag-chip"
        :class="{ active: activeTags.includes(tag) }"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </button>
    </div>

    <!-- Character grid -->
    <div class="char-grid">
      <div
        v-for="c in filteredCharacters"
        :key="c.id"
        class="dash-card"
        @click="openCharacterChat(c.id)"
      >
        <div class="dash-card-avatar">
          <img
            v-if="getAvatarUrl(c.avatar)"
            :src="getAvatarUrl(c.avatar)"
            :alt="c.name"
            class="dash-avatar-img"
            @error="$event.target.style.display = 'none'"
          />
          <div v-if="!getAvatarUrl(c.avatar)" class="dash-avatar-letter">
            {{ c.name?.charAt(0) || "?" }}
          </div>
        </div>
        <div class="dash-card-body">
          <div class="dash-card-name">{{ c.name }}</div>
          <div class="dash-card-series">{{ c.series }}</div>
          <div v-if="c.title" class="dash-card-title">{{ c.title }}</div>
          <div class="dash-card-tags">
            <span v-for="tag in c.tags || []" :key="tag" class="dash-tag">{{
              tag
            }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredCharacters.length === 0" class="dash-empty">
      No characters match your search or filters.
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 24px;
  overflow-y: auto;
}

.dash-header {
  text-align: center;
  margin-bottom: 24px;
}

.dash-header .logo {
  justify-content: center;
  margin-bottom: 12px;
}

.dash-subtitle {
  color: #6b6b80;
  font-size: 15px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.logo-icon.nsfw {
  background: linear-gradient(135deg, #8b5cf6, #ec4899);
}

.logo span {
  font-size: 18px;
  font-weight: 600;
}

.dash-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1100px;
  margin-bottom: 12px;
}

.header-spacer {
  width: 220px;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
  width: 220px;
  flex-shrink: 0;
  justify-content: flex-end;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 10px;
  color: #c4c4d4;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  font-family: inherit;
  white-space: nowrap;
}

.action-btn:hover {
  background: #2a2a3a;
  border-color: #8b5cf6;
}

.action-btn-emoji {
  font-size: 18px;
}

.action-btn-label {
  font-weight: 500;
}

.action-btn-avatar {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  object-fit: cover;
}

@media (max-width: 768px) {
  .dash-header-top {
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
  }
  .header-spacer {
    display: none;
  }
  .header-actions {
    width: auto;
    justify-content: center;
    order: 3;
  }
}

/* Search bar */
.search-bar {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin-bottom: 20px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #4a4a5a;
  pointer-events: none;
}

.search-input {
  width: 100%;
  background: #111118;
  border: 1px solid #2a2a3a;
  color: #e4e4eb;
  padding: 12px 40px 12px 42px;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}

.search-input:focus {
  border-color: #8b5cf6;
}

.search-input::placeholder {
  color: #4a4a5a;
}

.search-clear {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b6b80;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}

.search-clear:hover {
  color: #e4e4eb;
}

/* Tag filter bar */
.tag-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 32px;
  max-width: 900px;
}

.tag-chip {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid #2a2a3a;
  background: #151520;
  color: #8b8b9f;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.tag-chip:hover {
  background: #1f1f2e;
  color: #c4c4d4;
}

.tag-chip.active {
  background: linear-gradient(135deg, #6d28d9, #4c1d95);
  color: white;
  border-color: #8b5cf6;
}

/* Character grid */
.char-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1100px;
}

.dash-card {
  background: #111118;
  border: 1px solid #1f1f2e;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.dash-card:hover {
  transform: translateY(-4px);
  border-color: #8b5cf6;
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
}

.dash-card-avatar {
  width: 100%;
  height: 180px;
  background: linear-gradient(135deg, #1a1a2e, #0f0f1a);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.dash-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dash-avatar-letter {
  font-size: 64px;
  font-weight: bold;
  background: linear-gradient(135deg, #8b5cf6, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dash-card-body {
  padding: 16px;
}

.dash-card-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 4px;
}

.dash-card-series {
  font-size: 13px;
  color: #8b5cf6;
  font-weight: 500;
  margin-bottom: 4px;
}

.dash-card-title {
  font-size: 12px;
  color: #6b6b80;
  margin-bottom: 8px;
}

.dash-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.dash-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #1b1b2e;
  color: #a78bfa;
  border: 1px solid #2d2d4a;
}

.dash-empty {
  color: #4a4a5a;
  font-size: 16px;
  margin-top: 48px;
  text-align: center;
}

/* Scrollbar */
.dashboard::-webkit-scrollbar {
  width: 6px;
}

.dashboard::-webkit-scrollbar-track {
  background: transparent;
}

.dashboard::-webkit-scrollbar-thumb {
  background: #2a2a3a;
  border-radius: 3px;
}

.dashboard::-webkit-scrollbar-thumb:hover {
  background: #3a3a4a;
}
</style>
