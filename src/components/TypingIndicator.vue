<script setup>
import { currentCharacter } from "../store";
import { useCharacters } from "../composables/useCharacters";

const { getAvatarUrl } = useCharacters();
</script>

<template>
  <div class="message assistant">
    <div class="message-content">
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
      <div class="typing-wrapper">
        <div class="typing-name">{{ currentCharacter.name }} is typing</div>
        <div class="bubble typing">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message {
  display: flex;
}

.message-content {
  display: flex;
  gap: 12px;
  max-width: 75%;
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

.typing-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.typing-name {
  font-size: 11px;
  color: #6b6b80;
  padding-left: 4px;
  animation: fadeInOut 2s infinite;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.typing {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
  background: #1a1a24;
  border: 1px solid #2a2a3a;
  border-radius: 18px;
  border-top-left-radius: 4px;
}

.typing span {
  width: 8px;
  height: 8px;
  background: #6b6b80;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing span:nth-child(1) {
  animation-delay: 0s;
}
.typing span:nth-child(2) {
  animation-delay: 0.2s;
}
.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px);
  }
}
</style>
