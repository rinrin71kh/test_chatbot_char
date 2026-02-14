export function formatMessage(content: string) {
  return content.replace(
    /\*([^*]+)\*/g,
    '<span class="action">*$1*</span>'
  );
}

export function formatTimestamp(created_at: number) {
  if (!created_at) return "";
  const now = Date.now() / 1000;
  const diff = now - created_at;
  if (diff < 60) return "Just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  const d = new Date(created_at * 1000);
  const hours = d.getHours().toString().padStart(2, "0");
  const mins = d.getMinutes().toString().padStart(2, "0");
  return `${d.getMonth() + 1}/${d.getDate()} ${hours}:${mins}`;
}
