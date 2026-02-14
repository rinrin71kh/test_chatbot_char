import axios from "axios";
import { nextTick } from "vue";
import {
  API,
  sessionId,
  characterId,
  suggestions,
  suggestionsLoading,
  input,
} from "../store";
import { getPersonaPayload } from "./usePayloads";

export function useSuggestions() {
  async function fetchSuggestions() {
    if (!sessionId.value || !characterId.value) return;
    suggestionsLoading.value = true;
    suggestions.value = [];
    try {
      const res = await axios.post(`${API}/suggestions`, {
        session_id: sessionId.value,
        character_id: characterId.value,
        user_persona: getPersonaPayload(),
      });
      suggestions.value = res.data.suggestions || [];
    } catch (e) {
      console.error("Failed to fetch suggestions:", e);
      suggestions.value = [];
    } finally {
      suggestionsLoading.value = false;
    }
  }

  function useSuggestion(text: string) {
    input.value = text;
    suggestions.value = [];
    // Dynamically import to avoid circular deps
    nextTick(async () => {
      const { useChat } = await import("./useChat");
      const { send } = useChat();
      send();
    });
  }

  return {
    fetchSuggestions,
    useSuggestion,
  };
}
