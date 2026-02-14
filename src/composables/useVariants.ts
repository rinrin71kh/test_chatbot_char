import axios from "axios";
import {
  API,
  msgs,
  loading,
  streamingText,
  sessionId,
  characterId,
  variantsByMsgId,
  variantIndex,
} from "../store";
import { streamFromEndpoint } from "./useStreaming";
import { getPersonaPayload, getSettingsPayload } from "./usePayloads";

export function useVariants() {
  async function loadVariants(userMsgId: number) {
    try {
      const res = await axios.get(`${API}/chat/variants/${userMsgId}`);
      const variants = res.data.variants || [];
      variantsByMsgId.value[userMsgId] = variants;
      // Find active index
      const activeIdx = variants.findIndex((v: any) => v.is_active);
      variantIndex.value[userMsgId] = activeIdx >= 0 ? activeIdx : variants.length - 1;
    } catch {}
  }

  async function generateVariant(assistantMsgId: number, userMsgId: number) {
    if (loading.value) return;

    loading.value = true;
    streamingText.value = "";

    // Find the assistant message in msgs and update it in place
    const assistantMsg = msgs.value.find((m: any) => m.id === assistantMsgId);
    if (!assistantMsg) {
      loading.value = false;
      return;
    }

    // Save old content before overwriting
    const oldContent = assistantMsg.content;
    assistantMsg.content = "";

    const settings = getSettingsPayload();
    const body: any = {
      session_id: sessionId.value,
      character_id: characterId.value,
      assistant_msg_id: assistantMsgId,
      mode: "interact",
      ...settings,
    };
    const personaPayload = getPersonaPayload();
    if (personaPayload) body.user_persona = personaPayload;

    await streamFromEndpoint(
      `${API}/chat/regenerate-variant`,
      body,
      assistantMsg
    );

    streamingText.value = "";
    loading.value = false;

    // Reload variants list
    await loadVariants(userMsgId);
  }

  async function switchVariant(variantId: number, assistantMsgId: number, userMsgId: number) {
    try {
      const res = await axios.put(`${API}/chat/variants/${variantId}/activate`, {
        assistant_msg_id: assistantMsgId,
      });
      if (res.data.ok) {
        // Update the assistant message content locally
        const assistantMsg = msgs.value.find((m: any) => m.id === assistantMsgId);
        if (assistantMsg) {
          assistantMsg.content = res.data.content;
        }
        // Update variant index
        const variants = variantsByMsgId.value[userMsgId] || [];
        const idx = variants.findIndex((v: any) => v.id === variantId);
        if (idx >= 0) {
          variantIndex.value[userMsgId] = idx;
          // Update active flags
          variants.forEach((v: any, i: number) => {
            v.is_active = i === idx;
          });
        }
      }
    } catch (e) {
      console.error("Failed to switch variant:", e);
    }
  }

  function getVariantCount(userMsgId: number): number {
    return (variantsByMsgId.value[userMsgId] || []).length;
  }

  function getCurrentVariantIndex(userMsgId: number): number {
    return variantIndex.value[userMsgId] ?? 0;
  }

  return {
    loadVariants,
    generateVariant,
    switchVariant,
    getVariantCount,
    getCurrentVariantIndex,
  };
}
