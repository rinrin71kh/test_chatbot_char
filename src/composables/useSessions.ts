import axios from "axios";
import {
  API,
  sessionId,
  sessionList,
  showSessionHistory,
  characterId,
  msgs,
  currentCharacter,
} from "../store";

export function useSessions() {
  function getStoredSession(charId: string) {
    try {
      return localStorage.getItem(`session_${charId}`) || "";
    } catch {
      return "";
    }
  }

  function storeSession(charId: string, sessId: string) {
    try {
      localStorage.setItem(`session_${charId}`, sessId);
      localStorage.setItem("last_character", charId);
    } catch {}
  }

  async function loadSessionList(charId: string) {
    try {
      const res = await axios.get(`${API}/sessions`, {
        params: { character_id: charId },
      });
      sessionList.value = res.data || [];
    } catch (e) {
      console.error("Failed to load sessions:", e);
      sessionList.value = [];
    }
  }

  async function loadChatHistoryRaw(sessId: string, charId: string) {
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

  async function switchSession(sessId: string) {
    sessionId.value = sessId;
    storeSession(characterId.value, sessId);

    const history = await loadChatHistoryRaw(sessId, characterId.value);
    if (history.length > 0) {
      msgs.value = history;
    } else {
      const char = currentCharacter.value;
      msgs.value = [];
      if (char.greeting) {
        msgs.value.push({ role: "assistant", content: char.greeting });
      }
    }
    showSessionHistory.value = false;
  }

  function clearChat() {
    const newSess = crypto.randomUUID();
    sessionId.value = newSess;
    storeSession(characterId.value, newSess);

    const char = currentCharacter.value;
    msgs.value = [];
    if (char.greeting) {
      msgs.value.push({ role: "assistant", content: char.greeting });
    }
  }

  function formatSessionDate(timestamp: number) {
    if (!timestamp) return "Unknown";
    const d = new Date(timestamp * 1000);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    if (diff < 60000) return "Just now";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
    return d.toLocaleDateString();
  }

  return {
    getStoredSession,
    storeSession,
    loadSessionList,
    loadChatHistoryRaw,
    switchSession,
    clearChat,
    formatSessionDate,
  };
}
