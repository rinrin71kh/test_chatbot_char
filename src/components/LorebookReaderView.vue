<script setup lang="ts">
import { onMounted } from "vue";
import { currentView } from "../store";
import { useLorebook } from "../composables/useLorebook";

const {
  loading,
  activeTab,
  searchQuery,
  selectedSeries,
  selectedCharacter,
  characterLore,
  readerContent,
  readerTitle,
  readerChapterIndex,
  readerImages,
  showReader,
  displayItems,
  loadAll,
  openSeries,
  openCharacterLore,
  readChapter,
  readLoreText,
  readScenario,
  closeReader,
  goBack,
  navigateChapter,
  getAvatarUrl,
} = useLorebook();

onMounted(() => {
  loadAll();
});

function goToDashboard() {
  currentView.value = "dashboard";
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function formatContent(text: string): string {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
  const paragraphs = html.split(/\n\n+/);
  html = paragraphs.map((p: string) => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");
  html = html.replace(/<p>---<\/p>/g, "<hr>");
  return html;
}
</script>

<template>
  <div class="lorebook">
    <!-- ===== READER VIEW ===== -->
    <div v-if="showReader" class="reader-view">
      <header class="reader-header">
        <button class="reader-back-btn" @click="closeReader">
          <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
          </svg>
          Chapters
        </button>
        <div class="reader-title">{{ readerTitle }}</div>
        <div class="reader-nav" v-if="selectedSeries">
          <button
            class="reader-nav-btn"
            :disabled="readerChapterIndex <= 0"
            @click="navigateChapter(-1)"
          >
            Prev
          </button>
          <span class="reader-nav-info">
            {{ readerChapterIndex + 1 }} / {{ selectedSeries.chapters.length }}
          </span>
          <button
            class="reader-nav-btn"
            :disabled="readerChapterIndex >= selectedSeries.chapters.length - 1"
            @click="navigateChapter(1)"
          >
            Next
          </button>
        </div>
      </header>
      <div class="reader-body">
        <div v-if="readerImages.length" class="reader-images">
          <img
            v-for="(img, idx) in readerImages"
            :key="idx"
            :src="img"
            class="reader-chapter-img"
            @error="($event.target as HTMLImageElement).style.display = 'none'"
          />
        </div>
        <div class="reader-content" v-html="formatContent(readerContent)"></div>
      </div>
      <footer class="reader-footer" v-if="selectedSeries">
        <button
          class="reader-footer-btn"
          :disabled="readerChapterIndex <= 0"
          @click="navigateChapter(-1)"
        >
          Previous Chapter
        </button>
        <button
          class="reader-footer-btn"
          :disabled="readerChapterIndex >= selectedSeries.chapters.length - 1"
          @click="navigateChapter(1)"
        >
          Next Chapter
        </button>
      </footer>
    </div>

    <!-- ===== CHAPTER LIST VIEW (series selected) ===== -->
    <div v-else-if="selectedSeries" class="chapter-list-view">
      <header class="section-header">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
          </svg>
          Back
        </button>
        <h2 class="section-title">{{ selectedSeries.name }}</h2>
        <span class="chapter-count">{{ selectedSeries.chapter_count }} chapters</span>
      </header>
      <div class="chapter-list">
        <div
          v-for="(ch, idx) in selectedSeries.chapters"
          :key="ch.path"
          class="chapter-item"
          @click="readChapter(ch, idx)"
        >
          <div class="chapter-icon">&#128214;</div>
          <div class="chapter-info">
            <div class="chapter-name">{{ ch.name }}</div>
            <div class="chapter-meta">
              {{ formatSize(ch.size) }}
              <span v-if="ch.images && ch.images.length" class="chapter-img-badge">{{ ch.images.length }} img</span>
            </div>
          </div>
          <div class="chapter-arrow">&#8594;</div>
        </div>
      </div>
    </div>

    <!-- ===== CHARACTER LORE VIEW (character selected) ===== -->
    <div v-else-if="selectedCharacter && characterLore" class="character-lore-view">
      <header class="section-header">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
          </svg>
          Back
        </button>
        <div class="char-lore-header">
          <img
            v-if="getAvatarUrl(selectedCharacter.avatar)"
            :src="getAvatarUrl(selectedCharacter.avatar)"
            class="char-lore-avatar"
          />
          <div>
            <h2 class="section-title">{{ selectedCharacter.name }}</h2>
            <div class="char-lore-series">{{ selectedCharacter.series }}</div>
          </div>
        </div>
      </header>

      <!-- Background -->
      <div v-if="selectedCharacter.background" class="lore-section">
        <h3>Background</h3>
        <p class="lore-text">{{ selectedCharacter.background }}</p>
      </div>

      <!-- Scenarios -->
      <div v-if="characterLore.scenarios.length > 0" class="lore-section">
        <h3>Scenarios</h3>
        <div
          v-for="sc in characterLore.scenarios"
          :key="sc.name"
          class="chapter-item"
          @click="readScenario(sc)"
        >
          <div class="chapter-icon">&#127917;</div>
          <div class="chapter-info">
            <div class="chapter-name">{{ sc.title || sc.name }}</div>
            <div class="chapter-meta">Scenario</div>
          </div>
          <div class="chapter-arrow">&#8594;</div>
        </div>
      </div>

      <!-- Lore files -->
      <div v-if="characterLore.lore_texts.length > 0" class="lore-section">
        <h3>Lore Files</h3>
        <div
          v-for="lt in characterLore.lore_texts"
          :key="lt.filename"
          class="chapter-item"
          @click="readLoreText(lt)"
        >
          <div class="chapter-icon">&#128196;</div>
          <div class="chapter-info">
            <div class="chapter-name">{{ lt.filename }}</div>
            <div class="chapter-meta">{{ formatSize(lt.content.length) }}</div>
          </div>
          <div class="chapter-arrow">&#8594;</div>
        </div>
      </div>
    </div>

    <!-- ===== MAIN GRID VIEW ===== -->
    <div v-else class="grid-view">
      <header class="main-header">
        <div class="header-left">
          <button class="back-btn" @click="goToDashboard">
            <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
              <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
            </svg>
            Dashboard
          </button>
        </div>
        <h1 class="main-title">Lorebook Reader</h1>
        <div class="header-right"></div>
      </header>

      <!-- Search + tabs -->
      <div class="filter-bar">
        <div class="search-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search series, chapters, characters..."
            class="search-input"
          />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">&#10005;</button>
        </div>
        <div class="tab-bar">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'all' }"
            @click="activeTab = 'all'"
          >All</button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'series' }"
            @click="activeTab = 'series'"
          >Series</button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'characters' }"
            @click="activeTab = 'characters'"
          >Characters</button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">Loading lorebook data...</div>

      <!-- Grid -->
      <div v-else class="card-grid">
        <div
          v-for="item in displayItems"
          :key="item.type + '-' + item.data.id"
          class="lb-card"
          @click="item.type === 'series' ? openSeries(item.data) : openCharacterLore(item.data)"
        >
          <div class="lb-card-cover">
            <img
              v-if="item.type === 'series' && item.data.cover"
              :src="item.data.cover.startsWith('/') ? 'http://127.0.0.1:8001' + item.data.cover : item.data.cover"
              class="lb-cover-img"
              @error="($event.target as HTMLImageElement).style.display = 'none'"
            />
            <img
              v-else-if="item.type === 'character' && getAvatarUrl(item.data.avatar)"
              :src="getAvatarUrl(item.data.avatar)"
              class="lb-cover-img"
              @error="($event.target as HTMLImageElement).style.display = 'none'"
            />
            <div v-else class="lb-cover-placeholder">
              <span v-if="item.type === 'series'">&#128218;</span>
              <span v-else>{{ item.data.name?.charAt(0) || '?' }}</span>
            </div>
            <div class="lb-card-type-badge" :class="item.type">
              {{ item.type === 'series' ? 'Series' : 'Character' }}
            </div>
          </div>
          <div class="lb-card-body">
            <div class="lb-card-name">{{ item.data.name }}</div>
            <div class="lb-card-meta" v-if="item.type === 'series'">
              {{ item.data.chapter_count }} chapter{{ item.data.chapter_count !== 1 ? 's' : '' }}
            </div>
            <div class="lb-card-meta" v-else>
              {{ item.data.series }}
              <span v-if="item.data.scenario_count"> &middot; {{ item.data.scenario_count }} scenario{{ item.data.scenario_count !== 1 ? 's' : '' }}</span>
            </div>
            <div class="lb-card-tags" v-if="item.type === 'character' && item.data.tags">
              <span v-for="tag in item.data.tags.slice(0, 4)" :key="tag" class="lb-tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!loading && displayItems.length === 0" class="empty-state">
        No lorebook entries found.
      </div>
    </div>
  </div>
</template>


<style scoped>
.lorebook {
  width: 100%;
  min-height: 100vh;
  background: #0a0a0f;
  color: #e4e4eb;
  overflow-y: auto;
}

/* ===== MAIN HEADER ===== */
.main-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px 0;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.main-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #8b5cf6, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-left, .header-right {
  width: 140px;
}

/* ===== BACK BUTTON ===== */
.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  color: #8b8b9f;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  font-family: inherit;
}

.back-btn:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.back-btn svg {
  width: 16px;
  height: 16px;
}

/* ===== FILTER BAR ===== */
.filter-bar {
  max-width: 1200px;
  margin: 20px auto 0;
  padding: 0 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
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
  padding: 10px 40px 10px 42px;
  border-radius: 10px;
  font-size: 14px;
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
  font-size: 14px;
  cursor: pointer;
}

.tab-bar {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.tab-btn {
  padding: 6px 20px;
  border-radius: 20px;
  border: 1px solid #2a2a3a;
  background: #151520;
  color: #8b8b9f;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.tab-btn:hover {
  background: #1f1f2e;
  color: #c4c4d4;
}

.tab-btn.active {
  background: linear-gradient(135deg, #6d28d9, #4c1d95);
  color: white;
  border-color: #8b5cf6;
}

/* ===== CARD GRID ===== */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 32px 32px;
}

.lb-card {
  background: #111118;
  border: 1px solid #1f1f2e;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.lb-card:hover {
  transform: translateY(-4px);
  border-color: #8b5cf6;
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
}

.lb-card-cover {
  width: 100%;
  height: 180px;
  background: linear-gradient(135deg, #1a1a2e, #0f0f1a);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.lb-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.lb-cover-placeholder {
  font-size: 56px;
  opacity: 0.3;
}

.lb-card-type-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.lb-card-type-badge.series {
  background: rgba(139, 92, 246, 0.8);
  color: white;
}

.lb-card-type-badge.character {
  background: rgba(236, 72, 153, 0.8);
  color: white;
}

.lb-card-body {
  padding: 14px;
}

.lb-card-name {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lb-card-meta {
  font-size: 12px;
  color: #8b5cf6;
  font-weight: 500;
}

.lb-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.lb-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #1b1b2e;
  color: #a78bfa;
  border: 1px solid #2d2d4a;
}

/* ===== CHAPTER LIST ===== */
.chapter-list-view, .character-lore-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 32px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.section-title {
  font-size: 22px;
  font-weight: 700;
}

.chapter-count {
  font-size: 13px;
  color: #8b5cf6;
  background: #1b1b2e;
  padding: 4px 12px;
  border-radius: 12px;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chapter-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: #111118;
  border: 1px solid #1f1f2e;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.chapter-item:hover {
  background: #1a1a2e;
  border-color: #8b5cf6;
}

.chapter-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.chapter-info {
  flex: 1;
  min-width: 0;
}

.chapter-name {
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-meta {
  font-size: 12px;
  color: #6b6b80;
  margin-top: 2px;
}

.chapter-arrow {
  color: #6b6b80;
  font-size: 18px;
  flex-shrink: 0;
}

/* ===== CHARACTER LORE VIEW ===== */
.char-lore-header {
  display: flex;
  align-items: center;
  gap: 14px;
}

.char-lore-avatar {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid #8b5cf6;
}

.char-lore-series {
  font-size: 13px;
  color: #8b5cf6;
}

.lore-section {
  margin-bottom: 24px;
}

.lore-section h3 {
  font-size: 14px;
  text-transform: uppercase;
  color: #6b6b80;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.lore-text {
  font-size: 14px;
  line-height: 1.7;
  color: #c4c4d4;
  background: #111118;
  padding: 16px;
  border-radius: 10px;
  border: 1px solid #1f1f2e;
}

/* ===== CHAPTER IMAGE BADGE ===== */
.chapter-img-badge {
  display: inline-block;
  margin-left: 8px;
  padding: 1px 6px;
  border-radius: 8px;
  background: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
  font-size: 10px;
  font-weight: 600;
}

/* ===== READER IMAGES ===== */
.reader-images {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  max-width: 700px;
  width: 100%;
}

.reader-chapter-img {
  max-width: 100%;
  max-height: 600px;
  border-radius: 8px;
  border: 1px solid #2a2a3a;
  object-fit: contain;
}

/* ===== READER VIEW ===== */
.reader-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.reader-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 32px;
  background: #111118;
  border-bottom: 1px solid #1f1f2e;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-wrap: wrap;
}

.reader-back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  color: #8b8b9f;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  font-family: inherit;
  flex-shrink: 0;
}

.reader-back-btn:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.reader-back-btn svg {
  width: 16px;
  height: 16px;
}

.reader-title {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reader-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.reader-nav-btn {
  padding: 6px 14px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  color: #c4c4d4;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  font-family: inherit;
}

.reader-nav-btn:hover:not(:disabled) {
  background: #2a2a3a;
  border-color: #8b5cf6;
}

.reader-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.reader-nav-info {
  font-size: 12px;
  color: #6b6b80;
  min-width: 50px;
  text-align: center;
}

.reader-body {
  flex: 1;
  padding: 40px 32px;
  display: flex;
  justify-content: center;
}

.reader-content {
  max-width: 700px;
  width: 100%;
  font-size: 16px;
  line-height: 1.9;
  color: #d4d4df;
  font-family: "Georgia", "Times New Roman", serif;
}

.reader-content :deep(p) {
  margin-bottom: 1.2em;
  text-indent: 0;
}

.reader-content :deep(em) {
  color: #c4a0ff;
  font-style: italic;
}

.reader-content :deep(strong) {
  color: #e4e4eb;
  font-weight: 700;
}

.reader-content :deep(hr) {
  border: none;
  border-top: 1px solid #2a2a3a;
  margin: 2em 0;
}

.reader-footer {
  display: flex;
  justify-content: space-between;
  padding: 20px 32px;
  border-top: 1px solid #1f1f2e;
  background: #111118;
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
}

.reader-footer-btn {
  padding: 10px 24px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 10px;
  color: #c4c4d4;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-family: inherit;
}

.reader-footer-btn:hover:not(:disabled) {
  background: #2a2a3a;
  border-color: #8b5cf6;
}

.reader-footer-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ===== STATES ===== */
.loading-state, .empty-state {
  text-align: center;
  padding: 48px;
  color: #6b6b80;
  font-size: 16px;
}

/* ===== SCROLLBAR ===== */
.lorebook::-webkit-scrollbar {
  width: 6px;
}

.lorebook::-webkit-scrollbar-track {
  background: transparent;
}

.lorebook::-webkit-scrollbar-thumb {
  background: #2a2a3a;
  border-radius: 3px;
}

.lorebook::-webkit-scrollbar-thumb:hover {
  background: #3a3a4a;
}

.grid-view {
  padding-bottom: 40px;
}
</style>
