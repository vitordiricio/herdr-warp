// Sidebar navigation uses the existing tab boundaries and preserves pane order.
import { sessionName } from "./session-name.js";
export const DETAILS = "warp.sidebar.detailed";
export const CLOSED_DETAILS = "warp.sidebar.details-closed";

export function tabGroups(space, allPanes) {
  return (space.tabs ?? []).map(tab => ({ tab, panes: allPanes.filter(pane => pane.tab === tab.id) }));
}

export function panelLabel(pane, tab, count) {
  if (count === 1 && tab.named) return tab.name;
  if (!pane.terminal) return pane.title || pane.mod || "Panel";
  return sessionName(null, pane) || pane.program?.name || "Terminal";
}

export function focusPanel(pane, allPanes, run) {
  // Detailed navigation reveals the entire composition even if the tab was zoomed.
  const zoomed = allPanes.find(other => other.tab === pane.tab && other.zoomed);
  if (zoomed) run("pane.zoom", { pane: zoomed.pane });
  run("pane.focus", { pane: pane.pane });
}
