// A real session name, excluding the terminal/program labels used as fallbacks.
export function sessionName(tab, session) {
  if (tab?.named && tab.name?.trim()) return tab.name;
  const program = session?.program;
  if (program?.shell && !program.agent) return "";
  const raw = (session?.title ?? "").trim();
  if (/^[~/]|^[A-Za-z]:\\/.test(raw)) return "";
  const live = raw.replace(/^[^\p{L}\p{N}]+/u, "").trim();
  const lower = live.toLowerCase();
  if (!live || live === session?.terminal || live === session?.address
      || /^t[0-9a-f]+$/i.test(live) || /^\d+$/.test(live)
      || lower === program?.name?.toLowerCase() || lower === program?.key?.toLowerCase()
      || /^[~/]|^[A-Za-z]:\\/.test(live) || live.includes("@")) return "";
  return live;
}
