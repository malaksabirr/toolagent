export async function getHealth() {
  const r = await fetch("/api/health");
  if (!r.ok) throw new Error("backend");
  return r.json();
}

export async function getTools() {
  const r = await fetch("/api/tools");
  if (!r.ok) throw new Error("backend");
  return r.json();
}

export async function uploadFile(file) {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch("/api/upload", { method: "POST", body: fd });
  if (!r.ok) {
    let detail = "Échec du téléversement";
    try { detail = (await r.json()).detail || detail; } catch { /* ignore */ }
    throw new Error(detail);
  }
  return r.json();
}

/** Lit le flux SSE de /api/chat et appelle onEvent pour chaque évènement. */
export async function streamChat(payload, onEvent, signal) {
  const r = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
  if (!r.ok || !r.body) throw new Error(`Erreur serveur (${r.status})`);
  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buf.indexOf("\n\n")) !== -1) {
      const chunk = buf.slice(0, idx).trim();
      buf = buf.slice(idx + 2);
      if (chunk.startsWith("data:")) {
        try { onEvent(JSON.parse(chunk.slice(5).trim())); } catch { /* ignore */ }
      }
    }
  }
}
