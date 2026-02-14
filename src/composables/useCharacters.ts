import axios from "axios";
import {
  API,
  characters,
  characterId,
  allTags,
  activeTags,
  sidebarCollapsed,
  currentView,
  sessionId,
  sessionList,
  msgs,
  showSessionHistory,
} from "../store";

export function useCharacters() {
  async function loadCharacters() {
    try {
      const res = await axios.get(`${API}/characters`);
      characters.value = res.data;
    } catch (e) {
      console.error("Failed to load characters:", e);
    }
  }

  async function loadTags() {
    try {
      const res = await axios.get(`${API}/tags`);
      allTags.value = res.data;
    } catch (e) {
      console.error("Failed to load tags:", e);
    }
  }

  function toggleTag(tag: string) {
    const idx = activeTags.value.indexOf(tag);
    if (idx >= 0) {
      activeTags.value.splice(idx, 1);
    } else {
      activeTags.value.push(tag);
    }
  }

  function clearTagFilter() {
    activeTags.value = [];
  }

  async function openCharacterChat(charId: string) {
    characterId.value = charId;

    // Inline session logic to avoid circular deps
    let sessId = "";
    try {
      sessId = localStorage.getItem(`session_${charId}`) || "";
    } catch {}
    if (!sessId) {
      sessId = crypto.randomUUID();
    }
    try {
      localStorage.setItem(`session_${charId}`, sessId);
      localStorage.setItem("last_character", charId);
    } catch {}
    sessionId.value = sessId;

    // Load history
    try {
      const res = await axios.get(`${API}/chat/history`, {
        params: { session_id: sessId, character_id: charId },
      });
      const history = res.data.messages || [];
      if (history.length > 0) {
        msgs.value = history;
      } else {
        const char = characters.value.find((c: any) => c.id === charId);
        msgs.value = [];
        if (char && char.greeting) {
          msgs.value.push({ role: "assistant", content: char.greeting });
        }
      }
    } catch {
      const char = characters.value.find((c: any) => c.id === charId);
      msgs.value = [];
      if (char && char.greeting) {
        msgs.value.push({ role: "assistant", content: char.greeting });
      }
    }

    // Load session list
    try {
      const res = await axios.get(`${API}/sessions`, {
        params: { character_id: charId },
      });
      sessionList.value = res.data || [];
    } catch {}

    currentView.value = "chat";
  }

  function selectCharacter(id: string) {
    openCharacterChat(id);
  }

  function goToDashboard() {
    currentView.value = "dashboard";
  }

  function toggleSeries(series: string) {
    sidebarCollapsed.value[series] = !sidebarCollapsed.value[series];
  }

  function isSeriesCollapsed(series: string) {
    return !!sidebarCollapsed.value[series];
  }

  function genderBadge(gender: string) {
    if (!gender || gender === "Unknown") return "";
    return gender;
  }

  function scenarioLabel(charId: string) {
    const parts = charId.split("_");
    if (parts.length > 1) {
      const last = parts[parts.length - 1];
      return last.charAt(0).toUpperCase() + last.slice(1);
    }
    return "";
  }

  function getAvatarUrl(avatarField: string) {
    if (!avatarField) return null;
    if (avatarField.startsWith("/assets/")) return `${API}${avatarField}`;
    return null;
  }

  function getLastCharacter() {
    try {
      return localStorage.getItem("last_character") || "";
    } catch {
      return "";
    }
  }

  return {
    loadCharacters,
    loadTags,
    toggleTag,
    clearTagFilter,
    openCharacterChat,
    selectCharacter,
    goToDashboard,
    toggleSeries,
    isSeriesCollapsed,
    genderBadge,
    scenarioLabel,
    getAvatarUrl,
    getLastCharacter,
  };
}
