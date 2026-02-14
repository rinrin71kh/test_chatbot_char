import axios from "axios";
import { API, characterId, msgs, loading } from "../store";

export async function uploadFile(ev: Event) {
  const target = ev.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const form = new FormData();
  form.append("file", file);

  loading.value = true;
  msgs.value.push({
    role: "system",
    content: `Uploading lore: ${file.name}...`,
  });

  try {
    const res = await axios.post(
      `${API}/ingest/file?character_id=${encodeURIComponent(characterId.value)}`,
      form,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    msgs.value.push({
      role: "assistant",
      content: `*Absorbs the new information.*\n\nHmph. ${res.data.chunks} fragments of knowledge acquired. Continue.`,
    });
  } catch (e) {
    msgs.value.push({
      role: "assistant",
      content: "...The lore failed to integrate. Check your file.",
    });
  } finally {
    loading.value = false;
    target.value = "";
  }
}

export async function ingestUrl(url: string) {
  if (!url.trim()) return;

  loading.value = true;
  msgs.value.push({ role: "system", content: `Ingesting: ${url}...` });

  try {
    const res = await axios.post(`${API}/ingest/url`, {
      character_id: characterId.value,
      url,
    });
    msgs.value.push({
      role: "assistant",
      content: `*Processes the external knowledge.*\n\n${res.data.chunks} fragments absorbed. What else?`,
    });
  } catch (e) {
    msgs.value.push({
      role: "assistant",
      content: "...Failed to retrieve that location. Verify your link.",
    });
  } finally {
    loading.value = false;
  }
}
