<script setup lang="ts">
import { watch } from "vue";
import { chatSettings, showSettingsPanel } from "../store";

// Auto-save settings to localStorage
watch(chatSettings, (val) => {
  localStorage.setItem("chat_settings", JSON.stringify(val));
}, { deep: true });
</script>

<template>
  <div class="settings-panel">
    <div class="panel-header">
      <h3>Chat Settings</h3>
      <button class="close-btn" @click="showSettingsPanel = false">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <div class="panel-body">
      <!-- Temperature -->
      <div class="setting-group">
        <label class="setting-label">
          Temperature
          <span class="setting-value">{{ chatSettings.temperature.toFixed(1) }}</span>
        </label>
        <input
          type="range"
          min="0.1"
          max="1.5"
          step="0.1"
          v-model.number="chatSettings.temperature"
          class="slider"
        />
        <div class="slider-labels">
          <span>Focused</span>
          <span>Creative</span>
        </div>
      </div>

      <!-- Max Tokens -->
      <div class="setting-group">
        <label class="setting-label">
          Max Tokens
          <span class="setting-value">{{ chatSettings.maxTokens }}</span>
        </label>
        <input
          type="range"
          min="256"
          max="8192"
          step="256"
          v-model.number="chatSettings.maxTokens"
          class="slider"
        />
        <div class="slider-labels">
          <span>256</span>
          <span>8192</span>
        </div>
      </div>

      <!-- Response Length -->
      <div class="setting-group">
        <label class="setting-label">Response Length</label>
        <div class="toggle-group">
          <button
            v-for="opt in ['short', 'medium', 'long']"
            :key="opt"
            class="toggle-btn"
            :class="{ active: chatSettings.responseLength === opt }"
            @click="chatSettings.responseLength = opt as any"
          >{{ opt }}</button>
        </div>
      </div>

      <!-- Writing Style -->
      <div class="setting-group">
        <label class="setting-label">Writing Style</label>
        <div class="toggle-group">
          <button
            v-for="opt in ['dialogue', 'balanced', 'descriptive']"
            :key="opt"
            class="toggle-btn"
            :class="{ active: chatSettings.writingStyle === opt }"
            @click="chatSettings.writingStyle = opt as any"
          >{{ opt }}</button>
        </div>
      </div>

      <!-- NSFW Level -->
      <div class="setting-group">
        <label class="setting-label">NSFW Level</label>
        <div class="toggle-group">
          <button
            v-for="opt in ['mild', 'moderate', 'explicit']"
            :key="opt"
            class="toggle-btn"
            :class="{ active: chatSettings.nsfwLevel === opt }"
            @click="chatSettings.nsfwLevel = opt as any"
          >{{ opt }}</button>
        </div>
      </div>

      <!-- Perspective -->
      <div class="setting-group">
        <label class="setting-label">Perspective</label>
        <div class="toggle-group">
          <button
            class="toggle-btn"
            :class="{ active: chatSettings.perspective === 'first-person' }"
            @click="chatSettings.perspective = 'first-person'"
          >First-person</button>
          <button
            class="toggle-btn"
            :class="{ active: chatSettings.perspective === 'third-person' }"
            @click="chatSettings.perspective = 'third-person'"
          >Third-person</button>
        </div>
      </div>

      <!-- Typing Speed -->
      <div class="setting-group">
        <label class="setting-label">
          Typing Speed
          <span class="setting-value">{{ chatSettings.typingSpeedMs === 0 ? 'Instant' : chatSettings.typingSpeedMs + 'ms' }}</span>
        </label>
        <input
          type="range"
          min="0"
          max="50"
          step="5"
          v-model.number="chatSettings.typingSpeedMs"
          class="slider"
        />
        <div class="slider-labels">
          <span>Instant</span>
          <span>Slow</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 340px;
  height: 100%;
  background: #0f0f16;
  border-left: 1px solid #2a2a3a;
  z-index: 20;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #1f1f2e;
}

.panel-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
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

.close-btn:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-label {
  font-size: 13px;
  font-weight: 600;
  color: #c4c4d4;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-value {
  font-size: 12px;
  color: #8b5cf6;
  font-weight: 500;
}

.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  background: #2a2a3a;
  border-radius: 2px;
  outline: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #8b5cf6;
  cursor: pointer;
  border: 2px solid #0f0f16;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #4a4a5a;
}

.toggle-group {
  display: flex;
  gap: 4px;
  background: #1a1a24;
  border-radius: 8px;
  padding: 3px;
}

.toggle-btn {
  flex: 1;
  padding: 6px 8px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #8b8b9f;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  text-transform: capitalize;
  transition: all 0.15s;
}

.toggle-btn.active {
  background: #6d28d9;
  color: white;
}

.toggle-btn:hover:not(.active) {
  background: #2a2a3a;
  color: #c4c4d4;
}

.panel-body::-webkit-scrollbar {
  width: 4px;
}

.panel-body::-webkit-scrollbar-thumb {
  background: #2a2a3a;
  border-radius: 2px;
}
</style>
