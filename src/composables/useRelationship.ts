import axios from "axios";
import { API, characterId, relationship } from "../store";

export function useRelationship() {
  async function loadRelationship() {
    if (!characterId.value) return;
    try {
      const res = await axios.get(`${API}/relationship/${characterId.value}`);
      if (res.data) {
        relationship.value = {
          affection: res.data.affection ?? 0,
          trust: res.data.trust ?? 0,
          intimacy: res.data.intimacy ?? 0,
        };
      }
    } catch (e) {
      console.error("Failed to load relationship:", e);
    }
  }

  return { loadRelationship };
}
