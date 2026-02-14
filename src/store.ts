import { ref, computed } from "vue";

export const API = "http://127.0.0.1:8001";

// ---- App state ----
export const currentView = ref<"dashboard" | "chat" | "lorebook">("dashboard");

// ---- Character state ----
export const characters = ref<any[]>([]);
export const characterId = ref("");
export const allTags = ref<string[]>([]);
export const activeTags = ref<string[]>([]);
export const searchQuery = ref("");
export const sidebarCollapsed = ref<Record<string, boolean>>({});

// ---- Session state ----
export const sessionId = ref("");
export const sessionList = ref<any[]>([]);
export const showSessionHistory = ref(false);

// ---- Chat state ----
export const msgs = ref<any[]>([]);
export const loading = ref(false);
export const input = ref("");
export const streamingText = ref("");
export const showScenario = ref(true);

// ---- Persona state ----
export const personas = ref<any[]>([]);
export const activePersonaId = ref("");
export const showPersonaModal = ref(false);
export const personaForm = ref({
  id: "",
  name: "",
  gender: "Male",
  appearance: "",
  personality: "",
  avatar_emoji: "🧑",
});
export const editingPersonaId = ref<string | null>(null);

// ---- Suggestions ----
export const suggestions = ref<string[]>([]);
export const suggestionsLoading = ref(false);

// ---- Message actions state ----
export const editingMessageIndex = ref<number | null>(null);
export const editingMessageContent = ref("");

// ---- Mood state ----
export const characterMood = ref<any>({
  mood: "neutral",
  emoji: "😐",
  intensity: 5,
  description: "Waiting...",
});

// ---- Auto-continue ----
export const autoContinueEnabled = ref(false);
export const autoContinueDelay = ref(8); // seconds

// ---- Chat settings ----
export interface ChatSettings {
  temperature: number;
  maxTokens: number;
  responseLength: "short" | "medium" | "long";
  writingStyle: "dialogue" | "balanced" | "descriptive";
  nsfwLevel: "mild" | "moderate" | "explicit";
  perspective: "first-person" | "third-person";
  typingSpeedMs: number;
}

function loadSettings(): ChatSettings {
  try {
    const stored = localStorage.getItem("chat_settings");
    if (stored) return JSON.parse(stored);
  } catch {}
  return {
    temperature: 0.8,
    maxTokens: 2048,
    responseLength: "medium",
    writingStyle: "balanced",
    nsfwLevel: "explicit",
    perspective: "third-person" as const,
    typingSpeedMs: 0,
  };
}

export const chatSettings = ref<ChatSettings>(loadSettings());
export const showSettingsPanel = ref(false);

// ---- Response variants (swipe) ----
export interface VariantInfo {
  id: number;
  content: string;
  created_at: number;
  is_active: boolean;
}
export const variantsByMsgId = ref<Record<number, VariantInfo[]>>({});
export const variantIndex = ref<Record<number, number>>({});

// ---- Memory ----
export interface MemoryFact {
  id: number;
  session_id: string;
  character_id: string;
  fact: string;
  category: string;
  created_at: number;
}
export const memories = ref<MemoryFact[]>([]);
export const showMemoryPanel = ref(false);

// ---- Relationship ----
export interface RelationshipData {
  affection: number;
  trust: number;
  intimacy: number;
}
export const relationship = ref<RelationshipData>({
  affection: 0,
  trust: 0,
  intimacy: 0,
});

// ---- Pinned messages ----
export const pinnedMessageIds = ref<Set<number>>(new Set());

function loadPinnedMessages(): Set<number> {
  try {
    const stored = localStorage.getItem("pinned_messages");
    if (stored) return new Set(JSON.parse(stored));
  } catch {}
  return new Set();
}

export function initPinnedMessages(charId: string) {
  try {
    const stored = localStorage.getItem(`pinned_messages_${charId}`);
    if (stored) {
      pinnedMessageIds.value = new Set(JSON.parse(stored));
      return;
    }
  } catch {}
  pinnedMessageIds.value = new Set();
}

export function savePinnedMessages(charId: string) {
  localStorage.setItem(
    `pinned_messages_${charId}`,
    JSON.stringify([...pinnedMessageIds.value])
  );
}

// ---- Message search ----
export const searchOpen = ref(false);
export const messageSearchQuery = ref("");

// ---- Lore adaptations ----
export interface LoreAdaptation {
  id: number;
  character_id: string;
  fact: string;
  category: string;
  source: string;
  created_at: number;
}
export const loreAdaptations = ref<LoreAdaptation[]>([]);

// ---- Computed ----
export const currentCharacter = computed(() => {
  return (
    characters.value.find((c: any) => c.id === characterId.value) || {
      name: "Character",
      title: "",
      scenario: "",
      greeting: "",
      gender: "",
      series: "",
      tags: [],
      avatar: "",
    }
  );
});

export const activePersona = computed(() => {
  return personas.value.find((p: any) => p.id === activePersonaId.value) || null;
});

export const charactersBySeries = computed(() => {
  const groups: Record<string, any[]> = {};
  for (const c of characters.value) {
    const series = c.series || "Other";
    if (!groups[series]) groups[series] = [];
    groups[series].push(c);
  }
  return groups;
});

export const filteredCharacters = computed(() => {
  let list = characters.value;
  if (activeTags.value.length > 0) {
    list = list.filter((c: any) =>
      (c.tags || []).some((t: string) => activeTags.value.includes(t))
    );
  }
  const q = searchQuery.value.trim().toLowerCase();
  if (q) {
    list = list.filter((c: any) => {
      const name = (c.name || "").toLowerCase();
      const series = (c.series || "").toLowerCase();
      const title = (c.title || "").toLowerCase();
      const id = (c.id || "").toLowerCase();
      const tags = (c.tags || []).join(" ").toLowerCase();
      return (
        name.includes(q) ||
        series.includes(q) ||
        title.includes(q) ||
        id.includes(q) ||
        tags.includes(q)
      );
    });
  }
  return list;
});

export const EMOJI_OPTIONS = [
  "🧑", "👨", "👩", "🧔", "👱", "💁", "🧝", "🧙", "🦊", "🐺",
  "😈", "👸", "🤴", "🧛", "🧜", "🧞", "🦹", "🗡️", "🌙", "🔥",
];
