import { nextTick, watch } from "vue";
import { msgs, streamingText } from "../store";

let chatContainerEl: HTMLElement | null = null;

export function setChatContainer(el: HTMLElement | null) {
  chatContainerEl = el;
}

export function scrollToBottom() {
  nextTick(() => {
    if (chatContainerEl) {
      chatContainerEl.scrollTop = chatContainerEl.scrollHeight;
    }
  });
}

export async function streamFromEndpoint(
  url: string,
  body: any,
  assistantMsg: any
) {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;

        try {
          const data = JSON.parse(jsonStr);
          if (data.error) {
            assistantMsg.content =
              "*Expression darkens.*\n\n...Something interfered. Try again.";
            break;
          }
          if (data.token) {
            streamingText.value += data.token;
            assistantMsg.content = streamingText.value;
            scrollToBottom();
          }
          if (data.done && data.full_reply) {
            assistantMsg.content = data.full_reply;
          }
          if (data.variant_id) {
            assistantMsg._variantId = data.variant_id;
          }
        } catch {}
      }
    }
  } catch (e) {
    if (!assistantMsg.content) {
      assistantMsg.content =
        "*Expression darkens.*\n\n...Something interfered with our connection. Try again.";
    }
  }
}

// Watch msgs for scrolling
watch(msgs, scrollToBottom, { deep: true });
