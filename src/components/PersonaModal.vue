<script setup>
import {
  showPersonaModal,
  personas,
  activePersonaId,
  personaForm,
  editingPersonaId,
  EMOJI_OPTIONS,
} from "../store";
import { usePersona } from "../composables/usePersona";

const {
  editPersona,
  savePersonaForm,
  deletePersona,
  setActivePersona,
  cancelEditing,
} = usePersona();
</script>

<template>
  <div
    v-if="showPersonaModal"
    class="modal-overlay"
    @click.self="showPersonaModal = false"
  >
    <div class="modal persona-modal">
      <div class="modal-header">
        <h2>User Personas</h2>
        <button class="modal-close" @click="showPersonaModal = false">
          &times;
        </button>
      </div>

      <div class="persona-modal-body">
        <!-- Persona List -->
        <div class="persona-list">
          <div
            v-for="p in personas"
            :key="p.id"
            class="persona-card"
            :class="{ active: p.id === activePersonaId }"
            @click="setActivePersona(p.id)"
          >
            <div class="persona-card-emoji">{{ p.avatar_emoji }}</div>
            <div class="persona-card-info">
              <div class="persona-card-name">{{ p.name }}</div>
              <div class="persona-card-meta">
                <span class="persona-gender-badge">{{ p.gender }}</span>
              </div>
              <div v-if="p.appearance" class="persona-card-preview">
                {{ p.appearance.slice(0, 60)
                }}{{ p.appearance.length > 60 ? "..." : "" }}
              </div>
            </div>
            <div class="persona-card-actions">
              <button
                class="persona-action-btn"
                @click.stop="editPersona(p)"
                title="Edit"
              >
                &#9998;
              </button>
              <button
                class="persona-action-btn delete"
                @click.stop="deletePersona(p.id)"
                title="Delete"
              >
                &times;
              </button>
            </div>
            <div
              v-if="p.id === activePersonaId"
              class="persona-active-indicator"
            >
              Active
            </div>
          </div>

          <div v-if="personas.length === 0" class="persona-empty">
            No personas yet. Create one below!
          </div>
        </div>

        <!-- Create / Edit Form -->
        <div class="persona-form">
          <div class="persona-form-title">
            {{ editingPersonaId ? "Edit Persona" : "Create New Persona" }}
          </div>

          <label class="form-label">Name</label>
          <input
            v-model="personaForm.name"
            class="input"
            placeholder="Your character's name"
          />

          <label class="form-label">Gender</label>
          <div class="gender-selector">
            <button
              v-for="g in ['Male', 'Female', 'Futa']"
              :key="g"
              class="gender-option"
              :class="{ active: personaForm.gender === g }"
              @click="personaForm.gender = g"
            >
              {{ g }}
            </button>
          </div>

          <label class="form-label">Appearance</label>
          <textarea
            v-model="personaForm.appearance"
            class="input persona-textarea"
            placeholder="Describe how you look..."
            rows="3"
          ></textarea>

          <label class="form-label">Personality (optional)</label>
          <textarea
            v-model="personaForm.personality"
            class="input persona-textarea"
            placeholder="How you act, speak, your attitude..."
            rows="2"
          ></textarea>

          <label class="form-label">Avatar</label>
          <div class="emoji-picker">
            <button
              v-for="e in EMOJI_OPTIONS"
              :key="e"
              class="emoji-option"
              :class="{ active: personaForm.avatar_emoji === e }"
              @click="personaForm.avatar_emoji = e"
            >
              {{ e }}
            </button>
          </div>

          <div class="persona-form-actions">
            <button
              v-if="editingPersonaId"
              class="btn btn-secondary"
              @click="cancelEditing"
            >
              Cancel
            </button>
            <button
              class="btn btn-primary"
              @click="savePersonaForm"
              :disabled="!personaForm.name.trim()"
            >
              {{ editingPersonaId ? "Save Changes" : "Create Persona" }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal {
  background: #111118;
  border: 1px solid #2a2a3a;
  border-radius: 16px;
  max-width: 640px;
  width: 90vw;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #1f1f2e;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #8b5cf6, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.modal-close {
  background: none;
  border: none;
  color: #6b6b80;
  font-size: 24px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #e4e4eb;
}

.persona-modal-body {
  padding: 20px 24px;
}

.persona-list {
  margin-bottom: 24px;
}

.persona-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #1f1f2e;
  background: #0d0d14;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.persona-card:hover {
  border-color: #3a3a5a;
  background: #151520;
}

.persona-card.active {
  border-color: #8b5cf6;
  background: #1a1a2e;
}

.persona-card-emoji {
  font-size: 28px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a24;
  border-radius: 10px;
  flex-shrink: 0;
}

.persona-card-info {
  flex: 1;
  min-width: 0;
}

.persona-card-name {
  font-size: 15px;
  font-weight: 600;
  color: #e4e4eb;
}

.persona-card-meta {
  margin-top: 2px;
}

.persona-gender-badge {
  font-size: 10px;
  padding: 1px 8px;
  border-radius: 6px;
  background: #2d1b4e;
  color: #c084fc;
  font-weight: 600;
  text-transform: uppercase;
}

.persona-card-preview {
  font-size: 12px;
  color: #6b6b80;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.persona-card-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.persona-action-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: #1a1a24;
  color: #8b8b9f;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.persona-action-btn:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.persona-action-btn.delete:hover {
  background: #3d1515;
  color: #f87171;
}

.persona-active-indicator {
  position: absolute;
  top: 6px;
  right: 8px;
  font-size: 9px;
  padding: 2px 8px;
  border-radius: 6px;
  background: #6d28d9;
  color: white;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.persona-empty {
  text-align: center;
  color: #4a4a5a;
  padding: 24px;
  font-size: 14px;
}

.persona-form {
  background: #0d0d14;
  border: 1px solid #1f1f2e;
  border-radius: 12px;
  padding: 20px;
}

.persona-form-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #c4c4d4;
}

.form-label {
  display: block;
  font-size: 12px;
  text-transform: uppercase;
  color: #6b6b80;
  margin-bottom: 6px;
  margin-top: 14px;
  letter-spacing: 0.5px;
}

.form-label:first-of-type {
  margin-top: 0;
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

.persona-textarea {
  resize: vertical;
  min-height: 60px;
  font-family: inherit;
  line-height: 1.5;
}

.gender-selector {
  display: flex;
  gap: 8px;
}

.gender-option {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #2a2a3a;
  background: #1a1a24;
  color: #8b8b9f;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  font-family: inherit;
  text-align: center;
}

.gender-option:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.gender-option.active {
  background: linear-gradient(135deg, #6d28d9, #4c1d95);
  color: white;
  border-color: #8b5cf6;
}

.emoji-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.emoji-option {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid #2a2a3a;
  background: #1a1a24;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.emoji-option:hover {
  background: #2a2a3a;
  border-color: #4a4a5a;
  transform: scale(1.1);
}

.emoji-option.active {
  background: #2d1b4e;
  border-color: #8b5cf6;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.3);
}

.persona-form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  justify-content: flex-end;
}

.btn {
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

.btn-primary {
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
  border: none;
  padding: 10px 24px;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: scale(1.02);
}

.btn-primary:disabled {
  opacity: 0.4;
}
</style>
