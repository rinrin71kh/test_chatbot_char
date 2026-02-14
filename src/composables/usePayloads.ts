import { activePersona, chatSettings, pinnedMessageIds, nsfwMode } from "../store";

export function getPersonaPayload() {
  const p = activePersona.value;
  if (!p) return undefined;
  return {
    name: p.name,
    gender: p.gender,
    appearance: p.appearance,
    personality: p.personality,
  };
}

export function getSettingsPayload() {
  const s = chatSettings.value;
  const pinned = [...pinnedMessageIds.value];
  return {
    temperature: s.temperature,
    max_tokens: s.maxTokens,
    response_length: s.responseLength,
    writing_style: s.writingStyle,
    nsfw_level: s.nsfwLevel,
    perspective: s.perspective,
    pinned_message_ids: pinned.length > 0 ? pinned : undefined,
    sfw_mode: !nsfwMode.value,
  };
}
