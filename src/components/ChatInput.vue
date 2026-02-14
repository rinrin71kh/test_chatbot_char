<script setup>
import {
  input,
  loading,
  suggestions,
  suggestionsLoading,
  autoContinueEnabled,
  autoContinueDelay,
} from "../store";
import { useChat } from "../composables/useChat";
import { useSuggestions } from "../composables/useSuggestions";

const { send, continueStory, onInputChange, toggleAutoContinue } = useChat();
const { fetchSuggestions, useSuggestion } = useSuggestions();
</script>

<template>
  <footer class="input-area">
    <!-- Suggestion chips -->
    <div v-if="suggestionsLoading" class="suggestion-row">
      <div
        class="suggestion-chip skeleton"
        v-for="n in 4"
        :key="n"
      >
        <span class="shimmer"></span>
      </div>
    </div>
    <div
      v-else-if="suggestions.length > 0 && !loading"
      class="suggestion-row"
    >
      <button
        v-for="(s, i) in suggestions"
        :key="i"
        class="suggestion-chip"
        @click="useSuggestion(s)"
      >
        {{ s }}
      </button>
      <button
        class="suggestion-refresh"
        @click="fetchSuggestions"
        title="Refresh suggestions"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          width="16"
          height="16"
        >
          <path d="M1 4v6h6" />
          <path d="M23 20v-6h-6" />
          <path
            d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"
          />
        </svg>
      </button>
    </div>

    <div class="input-container">
      <button
        @click="continueStory"
        :disabled="loading"
        class="continue-btn"
        title="Auto-continue the story (narrator mode)"
      >
        <svg
          viewBox="0 0 24 24"
          fill="currentColor"
          width="18"
          height="18"
        >
          <path d="M8 5v14l11-7z" />
        </svg>
        Continue
      </button>
      <textarea
        v-model="input"
        @keydown.enter.exact.prevent="send"
        @input="onInputChange"
        placeholder="Type to interact with the story... (Enter to send)"
        rows="1"
        class="chat-input"
      ></textarea>
      <button
        @click="send"
        :disabled="loading || !input.trim()"
        class="send-btn"
        title="Send as interaction (your actions/dialogue)"
      >
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
      </button>
    </div>

    <div class="mode-hint">
      <span class="mode-tag continue-tag">Continue</span> auto-narrates the
      next scene
      <span class="mode-sep">&middot;</span>
      <span class="mode-tag interact-tag">Send</span> lets you shape the story
      <span class="mode-sep">&middot;</span>
      <button
        class="auto-continue-toggle"
        :class="{ active: autoContinueEnabled }"
        @click="toggleAutoContinue"
        :title="autoContinueEnabled ? 'Auto-continue ON' : 'Auto-continue OFF'"
      >
        Auto {{ autoContinueDelay }}s
        <span class="auto-dot" :class="{ on: autoContinueEnabled }"></span>
      </button>
    </div>
  </footer>
</template>

<style scoped>
.input-area {
  padding: 16px 24px;
  border-top: 1px solid #1f1f2e;
  background: #0f0f16;
}

.input-container {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.continue-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 18px;
  background: linear-gradient(135deg, #059669, #047857);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s, opacity 0.15s;
  white-space: nowrap;
  height: 48px;
  font-family: inherit;
}

.continue-btn:hover:not(:disabled) {
  transform: scale(1.03);
}

.continue-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.continue-btn svg {
  width: 18px;
  height: 18px;
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
  flex-shrink: 0;
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

/* Mode hint */
.mode-hint {
  margin-top: 8px;
  font-size: 11px;
  color: #4a4a5a;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex-wrap: wrap;
}

.mode-tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.continue-tag {
  background: #0a3d2a;
  color: #34d399;
}

.interact-tag {
  background: #2d1b4e;
  color: #c084fc;
}

.mode-sep {
  color: #2a2a3a;
  margin: 0 2px;
}

/* Auto-continue toggle */
.auto-continue-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid #2a2a3a;
  background: #151520;
  color: #6b6b80;
  font-size: 10px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}

.auto-continue-toggle:hover {
  background: #1f1f2e;
  color: #8b8b9f;
}

.auto-continue-toggle.active {
  background: #0a3d2a;
  border-color: #059669;
  color: #34d399;
}

.auto-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4a4a5a;
  transition: background 0.2s;
}

.auto-dot.on {
  background: #22c55e;
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

/* Suggestion chips */
.suggestion-row {
  display: flex;
  gap: 8px;
  padding: 0 0 12px 0;
  overflow-x: auto;
  align-items: center;
}

.suggestion-row::-webkit-scrollbar {
  height: 4px;
}

.suggestion-row::-webkit-scrollbar-thumb {
  background: #2a2a3a;
  border-radius: 2px;
}

.suggestion-chip {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid transparent;
  background: #1a1a24;
  color: #c4c4d4;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  font-family: inherit;
  background-image: linear-gradient(#1a1a24, #1a1a24),
    linear-gradient(135deg, #8b5cf6, #ec4899);
  background-origin: border-box;
  background-clip: padding-box, border-box;
}

.suggestion-chip:hover {
  background-image: linear-gradient(#2a2a3a, #2a2a3a),
    linear-gradient(135deg, #a78bfa, #f472b6);
  color: #e4e4eb;
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.25);
}

.suggestion-chip.skeleton {
  width: 140px;
  height: 36px;
  position: relative;
  overflow: hidden;
  cursor: default;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  background-image: none;
}

.shimmer {
  display: block;
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(139, 92, 246, 0.08),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.suggestion-refresh {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  border: 1px solid #2a2a3a;
  background: #1a1a24;
  color: #6b6b80;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.suggestion-refresh:hover {
  background: #2a2a3a;
  color: #8b5cf6;
  border-color: #8b5cf6;
}
</style>
