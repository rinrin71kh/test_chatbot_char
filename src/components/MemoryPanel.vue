<script setup lang="ts">
import { onMounted, computed } from "vue";
import { memories, showMemoryPanel } from "../store";
import { useMemory } from "../composables/useMemory";

const { loadMemories, deleteMemory, extractMemoriesNow } = useMemory();

onMounted(() => {
  loadMemories();
});

const categoryColors: Record<string, string> = {
  personal: "#8b5cf6",
  preference: "#ec4899",
  event: "#f59e0b",
  relationship: "#ef4444",
};

const groupedMemories = computed(() => {
  const groups: Record<string, typeof memories.value> = {};
  for (const m of memories.value) {
    const cat = m.category || "other";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(m);
  }
  return groups;
});

function formatTime(ts: number) {
  if (!ts) return "";
  const d = new Date(ts * 1000);
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
}
</script>

<template>
  <div class="memory-panel">
    <div class="panel-header">
      <h3>Memories</h3>
      <div class="panel-header-actions">
        <button class="extract-btn" @click="extractMemoriesNow" title="Extract memories from recent conversation">
          Extract Now
        </button>
        <button class="close-btn" @click="showMemoryPanel = false">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="panel-body">
      <div v-if="memories.length === 0" class="empty-state">
        No memories yet. Chat with the character and memories will be extracted automatically.
      </div>

      <div v-for="(items, category) in groupedMemories" :key="category" class="memory-group">
        <div class="group-header">
          <span
            class="category-badge"
            :style="{ background: categoryColors[category] || '#6b6b80' }"
          >{{ category }}</span>
          <span class="group-count">{{ items.length }}</span>
        </div>

        <div v-for="mem in items" :key="mem.id" class="memory-item">
          <div class="memory-fact">{{ mem.fact }}</div>
          <div class="memory-meta">
            <span class="memory-time">{{ formatTime(mem.created_at) }}</span>
            <button class="memory-delete" @click="deleteMemory(mem.id)" title="Delete memory">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.memory-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 360px;
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

.panel-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.extract-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #8b5cf6;
  background: transparent;
  color: #8b5cf6;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}

.extract-btn:hover {
  background: #8b5cf6;
  color: white;
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
  padding: 16px 20px;
}

.empty-state {
  color: #6b6b80;
  font-size: 13px;
  text-align: center;
  padding: 40px 20px;
  line-height: 1.6;
}

.memory-group {
  margin-bottom: 20px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.category-badge {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 8px;
  border-radius: 4px;
  color: white;
}

.group-count {
  font-size: 11px;
  color: #6b6b80;
}

.memory-item {
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 6px;
}

.memory-fact {
  font-size: 13px;
  color: #c4c4d4;
  line-height: 1.4;
}

.memory-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
}

.memory-time {
  font-size: 10px;
  color: #4a4a5a;
}

.memory-delete {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: #6b6b80;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.memory-delete:hover {
  background: #3d1515;
  color: #f87171;
}

.panel-body::-webkit-scrollbar {
  width: 4px;
}

.panel-body::-webkit-scrollbar-thumb {
  background: #2a2a3a;
  border-radius: 2px;
}
</style>
