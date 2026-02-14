import axios from "axios";
import {
  API,
  msgs,
  loading,
  input,
  streamingText,
  sessionId,
  characterId,
  suggestions,
  autoContinueEnabled,
  autoContinueDelay,
  sessionList,
} from "../store";
import { setChatContainer, scrollToBottom, streamFromEndpoint } from "./useStreaming";
import { getPersonaPayload, getSettingsPayload } from "./usePayloads";
import { formatMessage, formatTimestamp } from "./useFormatting";
import { fetchMood, checkAutoAnalysis } from "./useMood";
import { uploadFile, ingestUrl } from "./useIngestion";
import {
  startEditMessage,
  cancelEditMessage,
  saveEditAndRegenerate,
  regenerateResponse,
  regenerateAtIndex,
  deleteMessage,
  copyMessage,
} from "./useMessageActions";

let autoContinueTimer: ReturnType<typeof setTimeout> | null = null;

async function reloadSessionList() {
  try {
    const res = await axios.get(`${API}/sessions`, {
      params: { character_id: characterId.value },
    });
    sessionList.value = res.data || [];
  } catch {}
}

export function useChat() {
  async function loadChatHistory(sessId: string, charId: string) {
    try {
      const res = await axios.get(`${API}/chat/history`, {
        params: { session_id: sessId, character_id: charId },
      });
      return res.data.messages || [];
    } catch (e) {
      console.error("Failed to load chat history:", e);
      return [];
    }
  }

  async function streamChat(message: string, mode: string) {
    loading.value = true;
    streamingText.value = "";
    suggestions.value = [];

    const assistantMsg = { role: "assistant", content: "", id: null };
    msgs.value.push(assistantMsg);

    const settings = getSettingsPayload();
    const body: any = {
      session_id: sessionId.value,
      character_id: characterId.value,
      message: message,
      mode: mode,
      ...settings,
    };
    const personaPayload = getPersonaPayload();
    if (personaPayload) body.user_persona = personaPayload;

    await streamFromEndpoint(`${API}/chat/stream`, body, assistantMsg);

    streamingText.value = "";
    loading.value = false;
    reloadSessionList();
    // Reload history to get IDs
    const updated = await loadChatHistory(sessionId.value, characterId.value);
    if (updated.length > 0) msgs.value = updated;
    // Fetch mood + auto-analysis
    fetchMood();
    checkAutoAnalysis();
    // Auto-continue
    scheduleAutoContinue();
  }

  async function send() {
    const text = input.value.trim();
    if (!text || loading.value) return;

    suggestions.value = [];
    msgs.value.push({ role: "user", content: text });
    input.value = "";
    await streamChat(text, "interact");
  }

  async function continueStory() {
    if (loading.value) return;
    msgs.value.push({ role: "user", content: "[Continue the story]" });
    await streamChat("[Continue the story]", "continue");
  }

  function onInputChange() {
    if (input.value.trim()) {
      suggestions.value = [];
    }
  }

  // ---- Auto-continue ----
  function scheduleAutoContinue() {
    clearAutoContinue();
    if (!autoContinueEnabled.value) return;
    autoContinueTimer = setTimeout(() => {
      continueStory();
    }, autoContinueDelay.value * 1000);
  }

  function clearAutoContinue() {
    if (autoContinueTimer) {
      clearTimeout(autoContinueTimer);
      autoContinueTimer = null;
    }
  }

  function toggleAutoContinue() {
    autoContinueEnabled.value = !autoContinueEnabled.value;
    if (!autoContinueEnabled.value) {
      clearAutoContinue();
    }
  }

  return {
    // Streaming / scroll
    setChatContainer,
    scrollToBottom,
    // Chat core
    loadChatHistory,
    streamChat,
    send,
    continueStory,
    onInputChange,
    // Message actions (re-exported)
    startEditMessage,
    cancelEditMessage,
    saveEditAndRegenerate,
    regenerateResponse,
    regenerateAtIndex,
    deleteMessage,
    copyMessage,
    // Mood (re-exported)
    fetchMood,
    // Auto-continue
    toggleAutoContinue,
    // Ingestion (re-exported)
    uploadFile,
    ingestUrl,
    // Formatting (re-exported)
    formatMessage,
    formatTimestamp,
  };
}
