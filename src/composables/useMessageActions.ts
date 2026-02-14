import axios from "axios";
import {
  API,
  msgs,
  loading,
  streamingText,
  sessionId,
  characterId,
  suggestions,
  editingMessageIndex,
  editingMessageContent,
} from "../store";
import { streamFromEndpoint } from "./useStreaming";
import { getPersonaPayload, getSettingsPayload } from "./usePayloads";

async function reloadHistory() {
  try {
    const res = await axios.get(`${API}/chat/history`, {
      params: { session_id: sessionId.value, character_id: characterId.value },
    });
    const updated = res.data.messages || [];
    if (updated.length > 0) msgs.value = updated;
  } catch {}
}

// ---- Edit message ----
export function startEditMessage(index: number) {
  const msg = msgs.value[index];
  if (!msg || msg.role !== "user") return;
  editingMessageIndex.value = index;
  editingMessageContent.value = msg.content;
}

export function cancelEditMessage() {
  editingMessageIndex.value = null;
  editingMessageContent.value = "";
}

export async function saveEditAndRegenerate() {
  if (editingMessageIndex.value === null) return;
  const idx = editingMessageIndex.value;
  const msg = msgs.value[idx];
  if (!msg || !msg.id) {
    cancelEditMessage();
    return;
  }

  const newContent = editingMessageContent.value.trim();
  if (!newContent) return;

  loading.value = true;
  streamingText.value = "";
  suggestions.value = [];

  // Truncate local msgs after the edited message
  msgs.value = msgs.value.slice(0, idx);
  msgs.value.push({ role: "user", content: newContent, id: msg.id });

  editingMessageIndex.value = null;
  editingMessageContent.value = "";

  // Add placeholder for new response
  const assistantMsg = { role: "assistant", content: "", id: null };
  msgs.value.push(assistantMsg);

  const settings = getSettingsPayload();
  const body: any = {
    session_id: sessionId.value,
    character_id: characterId.value,
    message_id: msg.id,
    new_content: newContent,
    mode: "interact",
    ...settings,
  };
  const personaPayload = getPersonaPayload();
  if (personaPayload) body.user_persona = personaPayload;

  await streamFromEndpoint(
    `${API}/chat/edit-and-regenerate`,
    body,
    assistantMsg
  );

  streamingText.value = "";
  loading.value = false;
  await reloadHistory();
}

// ---- Regenerate last response ----
export async function regenerateResponse() {
  if (loading.value) return;

  // Remove the last assistant message from local state
  const lastIdx = msgs.value.length - 1;
  if (lastIdx >= 0 && msgs.value[lastIdx].role === "assistant") {
    msgs.value.pop();
  }

  loading.value = true;
  streamingText.value = "";
  suggestions.value = [];

  const assistantMsg = { role: "assistant", content: "", id: null };
  msgs.value.push(assistantMsg);

  const settings = getSettingsPayload();
  const body: any = {
    session_id: sessionId.value,
    character_id: characterId.value,
    mode: "interact",
    ...settings,
  };
  const personaPayload = getPersonaPayload();
  if (personaPayload) body.user_persona = personaPayload;

  await streamFromEndpoint(`${API}/chat/regenerate`, body, assistantMsg);

  streamingText.value = "";
  loading.value = false;
  await reloadHistory();
}

// ---- Regenerate at specific index (non-last assistant message) ----
export async function regenerateAtIndex(index: number) {
  if (loading.value) return;
  const msg = msgs.value[index];
  if (!msg || msg.role !== "assistant" || !msg.id) return;

  // Find the preceding user message
  let userMsgId: number | null = null;
  for (let i = index - 1; i >= 0; i--) {
    if (msgs.value[i].role === "user" && msgs.value[i].id) {
      userMsgId = msgs.value[i].id;
      break;
    }
  }
  if (!userMsgId) return;

  loading.value = true;
  streamingText.value = "";
  suggestions.value = [];

  // Truncate local messages after the user message (remove this assistant msg and everything after)
  const userIdx = msgs.value.findIndex((m: any) => m.id === userMsgId);
  if (userIdx < 0) {
    loading.value = false;
    return;
  }
  msgs.value = msgs.value.slice(0, userIdx + 1);

  // Truncate on backend
  try {
    await axios.post(`${API}/chat/truncate-after`, {
      session_id: sessionId.value,
      character_id: characterId.value,
      after_message_id: userMsgId,
    });
  } catch (e) {
    console.error("Failed to truncate:", e);
  }

  // Add placeholder for new response
  const assistantMsg = { role: "assistant", content: "", id: null };
  msgs.value.push(assistantMsg);

  const settings = getSettingsPayload();
  const body: any = {
    session_id: sessionId.value,
    character_id: characterId.value,
    mode: "interact",
    ...settings,
  };
  const personaPayload = getPersonaPayload();
  if (personaPayload) body.user_persona = personaPayload;

  await streamFromEndpoint(`${API}/chat/regenerate`, body, assistantMsg);

  streamingText.value = "";
  loading.value = false;
  await reloadHistory();
}

// ---- Delete message ----
export async function deleteMessage(index: number) {
  const msg = msgs.value[index];
  if (!msg || !msg.id) return;

  try {
    await axios.delete(`${API}/chat/message/${msg.id}`);
    msgs.value.splice(index, 1);
  } catch (e) {
    console.error("Failed to delete message:", e);
  }
}

// ---- Copy message ----
export async function copyMessage(index: number) {
  const msg = msgs.value[index];
  if (!msg) return;
  try {
    await navigator.clipboard.writeText(msg.content);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = msg.content;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }
}
