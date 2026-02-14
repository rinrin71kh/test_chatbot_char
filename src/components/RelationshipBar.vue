<script setup>
import { computed, onMounted } from "vue";
import { relationship } from "../store";
import { useRelationship } from "../composables/useRelationship";

const { loadRelationship } = useRelationship();

onMounted(() => {
  loadRelationship();
});

const hasValues = computed(() => {
  const r = relationship.value;
  return r.affection > 0 || r.trust > 0 || r.intimacy > 0;
});
</script>

<template>
  <div v-if="hasValues" class="relationship-bar">
    <!-- Affection -->
    <div class="rel-stat">
      <span class="rel-icon" title="Affection">&#10084;&#65039;</span>
      <div class="rel-track affection">
        <div class="rel-fill" :style="{ width: relationship.affection + '%' }"></div>
      </div>
      <span class="rel-value">{{ relationship.affection }}</span>
    </div>

    <!-- Trust -->
    <div class="rel-stat">
      <span class="rel-icon" title="Trust">&#128737;&#65039;</span>
      <div class="rel-track trust">
        <div class="rel-fill" :style="{ width: relationship.trust + '%' }"></div>
      </div>
      <span class="rel-value">{{ relationship.trust }}</span>
    </div>

    <!-- Intimacy -->
    <div class="rel-stat">
      <span class="rel-icon" title="Intimacy">&#128293;</span>
      <div class="rel-track intimacy">
        <div class="rel-fill" :style="{ width: relationship.intimacy + '%' }"></div>
      </div>
      <span class="rel-value">{{ relationship.intimacy }}</span>
    </div>
  </div>
</template>

<style scoped>
.relationship-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 24px;
  background: #0d0d14;
  border-bottom: 1px solid #1f1f2e;
}

.rel-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.rel-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.rel-track {
  flex: 1;
  height: 6px;
  background: #1a1a24;
  border-radius: 3px;
  overflow: hidden;
}

.rel-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

.rel-track.affection .rel-fill {
  background: linear-gradient(90deg, #ec4899, #f472b6);
}

.rel-track.trust .rel-fill {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.rel-track.intimacy .rel-fill {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}

.rel-value {
  font-size: 11px;
  color: #6b6b80;
  min-width: 24px;
  text-align: right;
  font-weight: 500;
}
</style>
