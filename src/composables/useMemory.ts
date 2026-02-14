import axios from "axios";
import { API, sessionId, characterId, memories } from "../store";

export function useMemory() {
  async function loadMemories() {
    if (!characterId.value) return;
    try {
      const res = await axios.get(`${API}/memories`, {
        params: { character_id: characterId.value },
      });
      memories.value = res.data.memories || [];
    } catch (e) {
      console.error("Failed to load memories:", e);
    }
  }

  async function deleteMemory(id: number) {
    try {
      await axios.delete(`${API}/memories/${id}`);
      memories.value = memories.value.filter((m) => m.id !== id);
    } catch (e) {
      console.error("Failed to delete memory:", e);
    }
  }

  async function extractMemoriesNow() {
    if (!sessionId.value || !characterId.value) return;
    try {
      await axios.post(`${API}/chat/extract-memories`, {
        session_id: sessionId.value,
        character_id: characterId.value,
      });
      await loadMemories();
    } catch (e) {
      console.error("Failed to extract memories:", e);
    }
  }

  return {
    loadMemories,
    deleteMemory,
    extractMemoriesNow,
  };
}
