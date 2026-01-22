<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const API = "http://127.0.0.1:8001";

const sessionId = ref(crypto.randomUUID());
const characters = ref([]);
const characterId = ref("ingrid");

const input = ref("");
const loading = ref(false);
const msgs = ref([
  { role: "assistant", content: "…State your business." }
]);

async function loadCharacters() {
  const res = await axios.get(`${API}/characters`);
  characters.value = res.data;
  if (!characters.value.find(c => c.id === characterId.value) && characters.value.length) {
    characterId.value = characters.value[0].id;
  }
}

async function send() {
  const text = input.value.trim();
  if (!text || loading.value) return;

  msgs.value.push({ role: "user", content: text });
  input.value = "";
  loading.value = true;

  try {
    const res = await axios.post(`${API}/chat`, {
      session_id: sessionId.value,
      character_id: characterId.value,
      message: text,
      temperature: 0.7,
    });
    msgs.value.push({ role: "assistant", content: res.data.reply });
  } catch (e) {
    msgs.value.push({ role: "assistant", content: "…Tch. Your connection is broken." });
  } finally {
    loading.value = false;
  }
}

async function uploadFile(ev) {
  const file = ev.target.files?.[0];
  if (!file) return;

  const form = new FormData();
  form.append("file", file);

  msgs.value.push({ role: "assistant", content: `Uploading lore: ${file.name}` });

  await axios.post(`${API}/ingest/file?character_id=${encodeURIComponent(characterId.value)}`, form, {
    headers: { "Content-Type": "multipart/form-data" }
  });

  msgs.value.push({ role: "assistant", content: "Lore ingested. Now speak." });
  ev.target.value = "";
}

const urlToIngest = ref("");
async function ingestUrl() {
  const url = urlToIngest.value.trim();
  if (!url) return;
  msgs.value.push({ role: "assistant", content: `Ingesting URL: ${url}` });

  await axios.post(`${API}/ingest/url`, {
    character_id: characterId.value,
    url
  });

  msgs.value.push({ role: "assistant", content: "Done. Don’t make me repeat myself." });
  urlToIngest.value = "";
}

onMounted(loadCharacters);
</script>

<template>
  <div class="wrap">
    <header class="top">
      <div class="row">
        <strong>Local Character Chat</strong>
        <span class="muted">Session: {{ sessionId.slice(0, 8) }}</span>
      </div>

      <div class="row">
        <label class="muted">Character</label>
        <select v-model="characterId">
          <option v-for="c in characters" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>

        <input type="file" accept=".txt" @change="uploadFile" />
      </div>

      <div class="row">
        <input v-model="urlToIngest" placeholder="Paste URL to ingest (wiki, page, etc.)" />
        <button @click="ingestUrl">Ingest URL</button>
      </div>
    </header>

    <main class="chat">
      <div v-for="(m, i) in msgs" :key="i" class="msg" :class="m.role">
        <div class="bubble">{{ m.content }}</div>
      </div>
    </main>

    <footer class="bottom">
      <input
        v-model="input"
        @keydown.enter="send"
        placeholder="Type..."
      />
      <button @click="send" :disabled="loading">{{ loading ? "..." : "Send" }}</button>
    </footer>
  </div>
</template>

<style>
.wrap { height: 100vh; display: flex; flex-direction: column; background: #0b0b0f; color: #e9e9ef; }
.top { padding: 12px; border-bottom: 1px solid #222; display: flex; flex-direction: column; gap: 10px; }
.row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.muted { color: #a6a6b3; font-size: 12px; }
select, input, button { background: #13131a; border: 1px solid #2a2a36; color: #e9e9ef; padding: 8px 10px; border-radius: 10px; }
button { cursor: pointer; }
.chat { flex: 1; overflow: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.msg { display: flex; }
.msg.user { justify-content: flex-end; }
.bubble { max-width: 70%; padding: 10px 12px; border-radius: 14px; background: #171723; border: 1px solid #2a2a36; white-space: pre-wrap; }
.msg.user .bubble { background: #1f1f2e; }
.bottom { padding: 12px; border-top: 1px solid #222; display: flex; gap: 10px; }
.bottom input { flex: 1; }
</style>
