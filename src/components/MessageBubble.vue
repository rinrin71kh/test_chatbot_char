<script setup>
import { ref, computed } from "vue";
import {
  streamingText,
  editingMessageIndex,
  editingMessageContent,
  loading,
  currentCharacter,
  activePersona,
  pinnedMessageIds,
  characterId,
  savePinnedMessages,
} from "../store";
import { useChat } from "../composables/useChat";
import { useCharacters } from "../composables/useCharacters";
import { useLorebook } from "../composables/useLorebook";

const props = defineProps({
  msg: { type: Object, required: true },
  index: { type: Number, required: true },
  isLast: { type: Boolean, default: false },
  totalMessages: { type: Number, default: 0 },
});

const { getAvatarUrl } = useCharacters();
const {
  startEditMessage,
  cancelEditMessage,
  saveEditAndRegenerate,
  regenerateResponse,
  regenerateAtIndex,
  deleteMessage,
  copyMessage,
  formatMessage,
  formatTimestamp,
} = useChat();
const { saveChapter, loadUserSeries, savingToLorebook } = useLorebook();

const showActions = ref(false);
const copied = ref(false);

function handleCopy() {
  copyMessage(props.index);
  copied.value = true;
  setTimeout(() => (copied.value = false), 2000);
}

const isEditing = ref(false);

function startEdit() {
  startEditMessage(props.index);
  isEditing.value = true;
}

function cancelEdit() {
  cancelEditMessage();
  isEditing.value = false;
}

function saveEdit() {
  saveEditAndRegenerate();
  isEditing.value = false;
}

function handleRegenerate() {
  if (props.isLast) {
    regenerateResponse();
  } else {
    regenerateAtIndex(props.index);
  }
}

// Pinning
const isPinned = computed(() => {
  return props.msg.id && pinnedMessageIds.value.has(props.msg.id);
});

function togglePin() {
  if (!props.msg.id) return;
  if (pinnedMessageIds.value.has(props.msg.id)) {
    pinnedMessageIds.value.delete(props.msg.id);
  } else {
    if (pinnedMessageIds.value.size >= 10) return; // cap at 10
    pinnedMessageIds.value.add(props.msg.id);
  }
  // Force reactivity
  pinnedMessageIds.value = new Set(pinnedMessageIds.value);
  savePinnedMessages(characterId.value);
}

// Reactions
const reaction = ref(null);
function setReaction(type) {
  reaction.value = reaction.value === type ? null : type;
}

// Save to Lorebook
const isWritingAssistant = computed(() => {
  const tags = currentCharacter.value?.tags || [];
  return tags.includes("writing assistant");
});
const showSaveForm = ref(false);
const saveSeriesName = ref("");
const saveChapterTitle = ref("");
const existingSeries = ref([]);
const saveFeedback = ref("");

async function openSaveForm() {
  showSaveForm.value = true;
  saveFeedback.value = "";
  existingSeries.value = await loadUserSeries();
}

function closeSaveForm() {
  showSaveForm.value = false;
  saveSeriesName.value = "";
  saveChapterTitle.value = "";
  saveFeedback.value = "";
}

async function doSaveChapter() {
  if (!saveSeriesName.value.trim() || !saveChapterTitle.value.trim()) {
    saveFeedback.value = "Please fill in both fields";
    return;
  }
  const ok = await saveChapter(
    saveSeriesName.value.trim(),
    saveChapterTitle.value.trim(),
    props.msg.content
  );
  if (ok) {
    saveFeedback.value = "Saved!";
    setTimeout(closeSaveForm, 1500);
  } else {
    saveFeedback.value = "Save failed";
  }
}
</script>

<template>
  <div
    class="message"
    :class="[
      msg.role,
      {
        streaming: streamingText && isLast && msg.role === 'assistant',
        pinned: isPinned,
      },
    ]"
    @mouseenter="showActions = true"
    @mouseleave="showActions = false"
  >
    <div class="message-content">
      <!-- Assistant avatar -->
      <template v-if="msg.role === 'assistant'">
        <img
          v-if="getAvatarUrl(currentCharacter.avatar)"
          :src="getAvatarUrl(currentCharacter.avatar)"
          :alt="currentCharacter.name"
          class="msg-avatar-img"
          @error="$event.target.style.display = 'none'"
        />
        <div
          v-if="!getAvatarUrl(currentCharacter.avatar)"
          class="msg-avatar"
        >
          {{ currentCharacter.name?.charAt(0) || "?" }}
        </div>
      </template>

      <!-- User avatar -->
      <template v-if="msg.role === 'user'">
        <div v-if="activePersona" class="msg-user-avatar">
          {{ activePersona.avatar_emoji }}
        </div>
      </template>

      <!-- Message bubble -->
      <div class="bubble-wrapper">
        <!-- Editing mode -->
        <div v-if="isEditing && editingMessageIndex === index" class="edit-area">
          <textarea
            v-model="editingMessageContent"
            class="edit-textarea"
            rows="3"
            @keydown.ctrl.enter="saveEdit"
            @keydown.escape="cancelEdit"
          ></textarea>
          <div class="edit-actions">
            <button class="edit-btn save" @click="saveEdit">
              Save & Resend
            </button>
            <button class="edit-btn cancel" @click="cancelEdit">Cancel</button>
          </div>
        </div>

        <!-- Normal display -->
        <div v-else class="bubble" v-html="formatMessage(msg.content)"></div>

        <!-- Timestamp -->
        <div v-if="msg.created_at && !isEditing" class="msg-timestamp">
          {{ formatTimestamp(msg.created_at) }}
        </div>

        <!-- Reactions -->
        <div v-if="reaction && !isEditing" class="msg-reaction">
          <span class="reaction-emoji">{{ reaction === 'love' ? '❤️' : reaction === 'like' ? '👍' : '👎' }}</span>
        </div>

        <!-- Always-visible edit button for user messages -->
        <button
          v-if="msg.role === 'user' && msg.id && !isEditing && !loading"
          class="edit-float-btn"
          @click="startEdit"
          title="Edit & Resend"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>

        <!-- Pin indicator -->
        <div v-if="isPinned" class="pin-indicator" title="Pinned">
          <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
            <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Action buttons (hover) -->
    <div
      v-if="showActions && !loading && msg.role !== 'system' && !isEditing"
      class="msg-actions"
      :class="msg.role"
    >
      <!-- Edit (user messages only) -->
      <button
        v-if="msg.role === 'user' && msg.id"
        class="action-btn"
        @click="startEdit"
        title="Edit & Resend"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </button>

      <!-- Regenerate (ALL assistant messages with IDs) -->
      <button
        v-if="msg.role === 'assistant' && msg.id"
        class="action-btn"
        @click="handleRegenerate"
        :title="isLast ? 'Regenerate response' : 'Regenerate from here'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <path d="M1 4v6h6"/><path d="M23 20v-6h-6"/>
          <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
        </svg>
      </button>

      <!-- Pin -->
      <button
        v-if="msg.id"
        class="action-btn"
        :class="{ active: isPinned }"
        @click="togglePin"
        :title="isPinned ? 'Unpin' : 'Pin to context'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
        </svg>
      </button>

      <!-- Copy -->
      <button
        class="action-btn"
        @click="handleCopy"
        :title="copied ? 'Copied!' : 'Copy'"
      >
        <svg v-if="!copied" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" width="14" height="14">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </button>

      <!-- Save to Lorebook (writing assistants only) -->
      <button
        v-if="msg.role === 'assistant' && isWritingAssistant"
        class="action-btn save-lb"
        @click="openSaveForm"
        title="Save to Lorebook"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
          <polyline points="17 21 17 13 7 13 7 21"/>
          <polyline points="7 3 7 8 15 8"/>
        </svg>
      </button>

      <!-- Reactions -->
      <button
        class="action-btn"
        :class="{ active: reaction === 'love' }"
        @click="setReaction('love')"
        title="Love"
      >❤️</button>
      <button
        class="action-btn"
        :class="{ active: reaction === 'like' }"
        @click="setReaction('like')"
        title="Like"
      >👍</button>
      <button
        class="action-btn"
        :class="{ active: reaction === 'dislike' }"
        @click="setReaction('dislike')"
        title="Dislike"
      >👎</button>

      <!-- Delete -->
      <button
        v-if="msg.id"
        class="action-btn delete"
        @click="deleteMessage(index)"
        title="Delete message"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
      </button>
    </div>

    <!-- Save to Lorebook inline form -->
    <div v-if="showSaveForm" class="save-lb-form">
      <div class="save-lb-header">
        <span>Save to Lorebook</span>
        <button class="save-lb-close" @click="closeSaveForm">&times;</button>
      </div>
      <div class="save-lb-fields">
        <input
          v-model="saveSeriesName"
          type="text"
          placeholder="Series name (e.g. My Novel)"
          class="save-lb-input"
          list="series-list"
        />
        <datalist id="series-list">
          <option v-for="s in existingSeries" :key="s" :value="s" />
        </datalist>
        <input
          v-model="saveChapterTitle"
          type="text"
          placeholder="Chapter title (e.g. Prologue)"
          class="save-lb-input"
          @keydown.enter="doSaveChapter"
        />
      </div>
      <div class="save-lb-actions">
        <span v-if="saveFeedback" class="save-lb-feedback" :class="{ error: saveFeedback.includes('fail') || saveFeedback.includes('fill') }">{{ saveFeedback }}</span>
        <button class="save-lb-btn" @click="doSaveChapter" :disabled="savingToLorebook">
          {{ savingToLorebook ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message {
  display: flex;
  position: relative;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.system {
  align-items: center;
}

.message.pinned {
  border-left: 2px solid #8b5cf6;
  padding-left: 8px;
}

.message-content {
  display: flex;
  gap: 12px;
  max-width: 75%;
}

.message.user .message-content {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  background: linear-gradient(135deg, #dc2626, #7c2d12);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.msg-avatar-img {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid #2a2a3a;
  flex-shrink: 0;
}

.msg-user-avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: linear-gradient(135deg, #6d28d9, #4c1d95);
  flex-shrink: 0;
}

.bubble-wrapper {
  position: relative;
}

.bubble {
  padding: 14px 18px;
  border-radius: 18px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message.assistant .bubble {
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-top-left-radius: 4px;
}

.message.user .bubble {
  background: linear-gradient(135deg, #6d28d9, #4c1d95);
  border-top-right-radius: 4px;
}

.message.system .bubble {
  background: transparent;
  color: #6b6b80;
  font-size: 13px;
  padding: 8px 16px;
}

.bubble :deep(.action) {
  color: #a78bfa;
  font-style: italic;
}

/* Streaming cursor */
.streaming .bubble::after {
  content: "\25CA";
  color: #8b5cf6;
  animation: blink-cursor 0.6s infinite;
  font-weight: bold;
}

@keyframes blink-cursor {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

/* Timestamp */
.msg-timestamp {
  font-size: 10px;
  color: #4a4a5a;
  margin-top: 4px;
  padding: 0 4px;
}

.message.user .msg-timestamp {
  text-align: right;
}

/* Reactions */
.msg-reaction {
  margin-top: 2px;
}

.reaction-emoji {
  font-size: 14px;
}

/* Always-visible edit button */
.edit-float-btn {
  position: absolute;
  top: 50%;
  right: -32px;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 1px solid #3a3a4a;
  background: #1a1a24;
  color: #8b5cf6;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: all 0.15s;
}

.edit-float-btn:hover {
  opacity: 1;
  background: #2a2a3a;
  border-color: #8b5cf6;
}

.message.user .edit-float-btn {
  right: auto;
  left: -32px;
}

/* Pin indicator */
.pin-indicator {
  position: absolute;
  top: -6px;
  right: 8px;
  color: #8b5cf6;
  font-size: 10px;
}

/* Action buttons */
.msg-actions {
  display: flex;
  gap: 2px;
  margin-top: 4px;
  padding: 4px 6px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  width: fit-content;
  animation: fadeIn 0.15s ease;
}

.msg-actions.user {
  align-self: flex-end;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.action-btn {
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
  font-size: 12px;
  transition: all 0.15s;
}

.action-btn:hover {
  background: #2a2a3a;
  color: #e4e4eb;
}

.action-btn.active {
  color: #8b5cf6;
}

.action-btn.delete:hover {
  background: #3d1515;
  color: #f87171;
}

/* Edit area */
.edit-area {
  min-width: 300px;
}

.edit-textarea {
  width: 100%;
  background: #1a1a24;
  border: 1px solid #8b5cf6;
  color: #e4e4eb;
  padding: 12px 14px;
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  outline: none;
  line-height: 1.5;
  min-height: 60px;
}

.edit-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  justify-content: flex-end;
}

.edit-btn {
  padding: 6px 14px;
  border-radius: 8px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}

.edit-btn.save {
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
}

.edit-btn.save:hover {
  opacity: 0.9;
}

.edit-btn.cancel {
  background: #2a2a3a;
  color: #c4c4d4;
}

.edit-btn.cancel:hover {
  background: #3a3a4a;
}

/* Save to Lorebook */
.action-btn.save-lb:hover {
  color: #22c55e;
  background: #0a2a15;
}

.save-lb-form {
  margin-top: 8px;
  background: #111118;
  border: 1px solid #2a2a3a;
  border-radius: 12px;
  padding: 12px 14px;
  max-width: 340px;
  animation: fadeIn 0.15s ease;
}

.save-lb-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #c4c4d4;
}

.save-lb-close {
  background: none;
  border: none;
  color: #6b6b80;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.save-lb-close:hover {
  color: #e4e4eb;
}

.save-lb-fields {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.save-lb-input {
  width: 100%;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  color: #e4e4eb;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}

.save-lb-input:focus {
  border-color: #8b5cf6;
}

.save-lb-input::placeholder {
  color: #4a4a5a;
}

.save-lb-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

.save-lb-feedback {
  font-size: 12px;
  color: #22c55e;
}

.save-lb-feedback.error {
  color: #f87171;
}

.save-lb-btn {
  padding: 6px 16px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.15s;
  margin-left: auto;
}

.save-lb-btn:hover {
  opacity: 0.9;
}

.save-lb-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
