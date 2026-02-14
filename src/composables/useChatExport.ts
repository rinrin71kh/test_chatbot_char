import { msgs, currentCharacter, sessionId } from "../store";

export function useChatExport() {
  function exportAsText() {
    const charName = currentCharacter.value.name || "Character";
    const lines = msgs.value.map((m: any) => {
      const speaker = m.role === "user" ? "You" : m.role === "assistant" ? charName : "System";
      return `[${speaker}]\n${m.content}\n`;
    });
    const text = `Chat with ${charName}\nSession: ${sessionId.value}\n${"=".repeat(40)}\n\n${lines.join("\n")}`;
    downloadFile(`chat_${charName}_${Date.now()}.txt`, text, "text/plain");
  }

  function exportAsJson() {
    const charName = currentCharacter.value.name || "Character";
    const data = {
      character: charName,
      session_id: sessionId.value,
      exported_at: new Date().toISOString(),
      messages: msgs.value.map((m: any) => ({
        role: m.role,
        content: m.content,
        id: m.id || null,
        created_at: m.created_at || null,
      })),
    };
    downloadFile(`chat_${charName}_${Date.now()}.json`, JSON.stringify(data, null, 2), "application/json");
  }

  function downloadFile(filename: string, content: string, type: string) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return { exportAsText, exportAsJson };
}
