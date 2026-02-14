import axios from "axios";
import { API, sessionId, characterId, characterMood } from "../store";

export async function fetchMood() {
  if (!sessionId.value || !characterId.value) return;
  try {
    const res = await axios.post(`${API}/chat/mood`, {
      session_id: sessionId.value,
      character_id: characterId.value,
    });
    characterMood.value = res.data;
  } catch (e) {
    console.error("Failed to fetch mood:", e);
  }
}

let messageCountSinceAnalysis = 0;

export function triggerAutoAnalysis() {
  // Fire-and-forget memory extraction
  axios.post(`${API}/chat/extract-memories`, {
    session_id: sessionId.value,
    character_id: characterId.value,
  }).catch(() => {});
  // Fire-and-forget relationship analysis
  axios.post(`${API}/chat/relationship`, {
    session_id: sessionId.value,
    character_id: characterId.value,
  }).catch(() => {});
  // Fire-and-forget lore adaptation
  axios.post(`${API}/chat/adapt-lore`, {
    session_id: sessionId.value,
    character_id: characterId.value,
  }).catch(() => {});
}

export function checkAutoAnalysis() {
  messageCountSinceAnalysis++;
  if (messageCountSinceAnalysis >= 5) {
    messageCountSinceAnalysis = 0;
    triggerAutoAnalysis();
  }
}
