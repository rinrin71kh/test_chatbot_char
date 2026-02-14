<script setup>
import { onMounted, computed } from "vue";
import { variantsByMsgId, variantIndex, loading } from "../store";
import { useVariants } from "../composables/useVariants";

const props = defineProps({
  assistantMsgId: { type: Number, required: true },
  userMsgId: { type: Number, required: true },
});

const { loadVariants, generateVariant, switchVariant, getVariantCount, getCurrentVariantIndex } = useVariants();

const variants = computed(() => variantsByMsgId.value[props.userMsgId] || []);
const currentIdx = computed(() => variantIndex.value[props.userMsgId] ?? 0);
const count = computed(() => variants.value.length);
const showControls = computed(() => count.value > 0 || !loading.value);

onMounted(() => {
  if (props.userMsgId) {
    loadVariants(props.userMsgId);
  }
});

function swipeLeft() {
  if (loading.value) return;
  const idx = currentIdx.value;
  if (idx > 0) {
    const variant = variants.value[idx - 1];
    switchVariant(variant.id, props.assistantMsgId, props.userMsgId);
  }
}

function swipeRight() {
  if (loading.value) return;
  const idx = currentIdx.value;
  if (idx < count.value - 1) {
    // Switch to next existing variant
    const variant = variants.value[idx + 1];
    switchVariant(variant.id, props.assistantMsgId, props.userMsgId);
  } else {
    // Generate new variant
    generateVariant(props.assistantMsgId, props.userMsgId);
  }
}
</script>

<template>
  <div class="swipe-controls" v-if="showControls">
    <button
      class="swipe-btn"
      :disabled="currentIdx <= 0 || loading"
      @click="swipeLeft"
      title="Previous variant"
    >
      <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
        <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
      </svg>
    </button>

    <span class="swipe-counter" v-if="count > 0">
      {{ currentIdx + 1 }} / {{ count }}
    </span>
    <span class="swipe-counter swipe-new" v-else>
      swipe for alt
    </span>

    <button
      class="swipe-btn"
      :disabled="loading"
      @click="swipeRight"
      :title="currentIdx >= count - 1 ? 'Generate new variant' : 'Next variant'"
    >
      <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
        <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
      </svg>
    </button>
  </div>
</template>

<style scoped>
.swipe-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  padding: 2px 4px;
}

.swipe-btn {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: 1px solid #2a2a3a;
  background: #1a1a24;
  color: #8b8b9f;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.swipe-btn:hover:not(:disabled) {
  background: #2a2a3a;
  color: #e4e4eb;
  border-color: #8b5cf6;
}

.swipe-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.swipe-counter {
  font-size: 11px;
  color: #6b6b80;
  min-width: 40px;
  text-align: center;
  font-family: monospace;
}

.swipe-new {
  font-family: inherit;
  font-style: italic;
  color: #4a4a5a;
}
</style>
