import { ref, computed } from "vue";
import { API } from "../store";

// ---- Types ----
export interface LorebookChapter {
  path: string;
  name: string;
  filename: string;
  size: number;
  images: string[];
}

export interface LorebookSeries {
  id: string;
  name: string;
  cover: string;
  chapter_count: number;
  chapters: LorebookChapter[];
}

export interface LorebookCharacter {
  id: string;
  name: string;
  series: string;
  avatar: string;
  tags: string[];
  gender: string;
  background: string;
  lore_file_count: number;
  scenario_count: number;
  folder_path: string;
}

export interface CharacterLore {
  id: string;
  profile: any;
  scenarios: { name: string; title: string; greeting: string; context: string }[];
  lore_texts: { filename: string; content: string }[];
}

// ---- State ----
const series = ref<LorebookSeries[]>([]);
const characters = ref<LorebookCharacter[]>([]);
const loading = ref(false);
const error = ref("");

// Sub-view state
const activeTab = ref<"all" | "series" | "characters">("all");
const searchQuery = ref("");
const selectedSeries = ref<LorebookSeries | null>(null);
const selectedCharacter = ref<LorebookCharacter | null>(null);
const characterLore = ref<CharacterLore | null>(null);

// Reader state
const readerContent = ref("");
const readerTitle = ref("");
const readerChapterIndex = ref(0);
const readerImages = ref<string[]>([]);
const showReader = ref(false);

// ---- Computed ----
const filteredSeries = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return series.value;
  return series.value.filter(
    (s) =>
      s.name.toLowerCase().includes(q) ||
      s.id.toLowerCase().includes(q) ||
      s.chapters.some((ch) => ch.name.toLowerCase().includes(q))
  );
});

const filteredCharacters = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return characters.value;
  return characters.value.filter(
    (c) =>
      c.name.toLowerCase().includes(q) ||
      c.series.toLowerCase().includes(q) ||
      c.tags.some((t) => t.toLowerCase().includes(q))
  );
});

const allItems = computed(() => {
  const items: { type: "series" | "character"; data: any }[] = [];
  for (const s of filteredSeries.value) {
    items.push({ type: "series", data: s });
  }
  for (const c of filteredCharacters.value) {
    items.push({ type: "character", data: c });
  }
  return items;
});

const displayItems = computed(() => {
  if (activeTab.value === "series") return allItems.value.filter((i) => i.type === "series");
  if (activeTab.value === "characters") return allItems.value.filter((i) => i.type === "character");
  return allItems.value;
});

// ---- Actions ----
async function loadSeries() {
  try {
    const r = await fetch(`${API}/lorebook/series`);
    const data = await r.json();
    series.value = data.series || [];
  } catch (e) {
    console.error("Failed to load lorebook series:", e);
  }
}

async function loadCharacters() {
  try {
    const r = await fetch(`${API}/lorebook/characters`);
    const data = await r.json();
    characters.value = data.characters || [];
  } catch (e) {
    console.error("Failed to load lorebook characters:", e);
  }
}

async function loadAll() {
  loading.value = true;
  error.value = "";
  try {
    await Promise.all([loadSeries(), loadCharacters()]);
  } catch (e: any) {
    error.value = e.message || "Failed to load lorebook data";
  } finally {
    loading.value = false;
  }
}

function openSeries(s: LorebookSeries) {
  selectedSeries.value = s;
  selectedCharacter.value = null;
  characterLore.value = null;
  showReader.value = false;
}

async function openCharacterLore(c: LorebookCharacter) {
  selectedCharacter.value = c;
  selectedSeries.value = null;
  showReader.value = false;
  loading.value = true;
  try {
    const r = await fetch(`${API}/lorebook/character/${c.id}/lore`);
    const data = await r.json();
    characterLore.value = data;
  } catch (e) {
    console.error("Failed to load character lore:", e);
    characterLore.value = null;
  } finally {
    loading.value = false;
  }
}

async function readChapter(chapter: LorebookChapter, index: number) {
  loading.value = true;
  try {
    const r = await fetch(`${API}/lorebook/chapter?path=${encodeURIComponent(chapter.path)}`);
    const data = await r.json();
    readerContent.value = data.content || "";
    readerTitle.value = chapter.name;
    readerChapterIndex.value = index;
    readerImages.value = (data.images || []).map((img: string) =>
      img.startsWith("/") ? `${API}${img}` : img
    );
    showReader.value = true;
  } catch (e) {
    console.error("Failed to load chapter:", e);
  } finally {
    loading.value = false;
  }
}

function readLoreText(text: { filename: string; content: string }) {
  readerContent.value = text.content;
  readerTitle.value = text.filename.replace(".txt", "").replace(/_/g, " ");
  readerChapterIndex.value = 0;
  showReader.value = true;
}

function readScenario(scenario: { name: string; title: string; greeting: string; context: string }) {
  let content = "";
  if (scenario.context) content += scenario.context + "\n\n---\n\n";
  if (scenario.greeting) content += scenario.greeting;
  readerContent.value = content;
  readerTitle.value = scenario.title || scenario.name;
  readerChapterIndex.value = 0;
  showReader.value = true;
}

function closeReader() {
  showReader.value = false;
}

function goBack() {
  if (showReader.value) {
    showReader.value = false;
    return;
  }
  if (selectedSeries.value || selectedCharacter.value) {
    selectedSeries.value = null;
    selectedCharacter.value = null;
    characterLore.value = null;
    return;
  }
}

function navigateChapter(delta: number) {
  if (!selectedSeries.value) return;
  const chapters = selectedSeries.value.chapters;
  const newIndex = readerChapterIndex.value + delta;
  if (newIndex >= 0 && newIndex < chapters.length) {
    readChapter(chapters[newIndex], newIndex);
  }
}

function getAvatarUrl(avatar: string): string {
  if (!avatar) return "";
  if (avatar.startsWith("http") || avatar.startsWith("/")) return avatar.startsWith("/") ? `${API}${avatar}` : avatar;
  return "";
}

export function useLorebook() {
  return {
    // State
    series,
    characters,
    loading,
    error,
    activeTab,
    searchQuery,
    selectedSeries,
    selectedCharacter,
    characterLore,
    readerContent,
    readerTitle,
    readerChapterIndex,
    readerImages,
    showReader,
    // Computed
    filteredSeries,
    filteredCharacters,
    displayItems,
    // Actions
    loadAll,
    openSeries,
    openCharacterLore,
    readChapter,
    readLoreText,
    readScenario,
    closeReader,
    goBack,
    navigateChapter,
    getAvatarUrl,
  };
}
