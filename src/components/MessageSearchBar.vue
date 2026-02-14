<script setup>
import { ref } from "vue";
import { searchOpen, messageSearchQuery } from "../store";
import { useMessageSearch } from "../composables/useMessageSearch";

const { searchResults, scrollToMessage } = useMessageSearch();
const currentResultIdx = ref(0);

function nextResult() {
  if (searchResults.value.length === 0) return;
  currentResultIdx.value = (currentResultIdx.value + 1) % searchResults.value.length;
  scrollToMessage(searchResults.value[currentResultIdx.value].index);
}

function prevResult() {
  if (searchResults.value.length === 0) return;
  currentResultIdx.value = (currentResultIdx.value - 1 + searchResults.value.length) % searchResults.value.length;
  scrollToMessage(searchResults.value[currentResultIdx.value].index);
}

function closeSearch() {
  searchOpen.value = false;
  messageSearchQuery.value = "";
}
</script>

<template>
  <div v-if="searchOpen" class="search-bar">
    <div class="search-input-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="search-icon">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        v-model="messageSearchQuery"
        placeholder="Search messages..."
        class="search-input"
        autofocus
        @keydown.enter="nextResult"
        @keydown.escape="closeSearch"
      />
      <span v-if="messageSearchQuery" class="search-count">
        {{ searchResults.length }} found
      </span>
    </div>
    <div class="search-nav">
      <button class="nav-btn" @click="prevResult" :disabled="searchResults.length === 0" title="Previous">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <polyline points="18 15 12 9 6 15"/>
        </svg>
      </button>
      <button class="nav-btn" @click="nextResult" :disabled="searchResults.length === 0" title="Next">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
      <button class="nav-btn" @click="closeSearch" title="Close">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 24px;
  background: #0d0d14;
  border-bottom: 1px solid #1f1f2e;
  animation: slideDown 0.15s ease;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.search-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  padding: 6px 12px;
}

.search-icon {
  color: #6b6b80;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #e4e4eb;
  font-size: 13px;
  font-family: inherit;
}

.search-input::placeholder {
  color: #4a4a5a;
}

.search-count {
  font-size: 11px;
  color: #8b5cf6;
  white-space: nowrap;
}

.search-nav {
  display: flex;
  gap: 2px;
}

.nav-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #8b8b9f;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.nav-btn:hover:not(:disabled) {
  background: #2a2a3a;
  color: #e4e4eb;
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: default;
}
</style>
