import { computed } from "vue";
import { msgs, messageSearchQuery } from "../store";

export function useMessageSearch() {
  const searchResults = computed(() => {
    const q = messageSearchQuery.value.trim().toLowerCase();
    if (!q) return [];
    const results: { index: number; msg: any }[] = [];
    for (let i = 0; i < msgs.value.length; i++) {
      const m = msgs.value[i];
      if (m.content && m.content.toLowerCase().includes(q)) {
        results.push({ index: i, msg: m });
      }
    }
    return results;
  });

  function scrollToMessage(index: number) {
    const els = document.querySelectorAll(".message");
    if (els[index]) {
      els[index].scrollIntoView({ behavior: "smooth", block: "center" });
      els[index].classList.add("search-highlight");
      setTimeout(() => els[index].classList.remove("search-highlight"), 2000);
    }
  }

  return { searchResults, scrollToMessage };
}
