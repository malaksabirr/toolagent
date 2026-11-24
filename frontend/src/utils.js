export const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);

export function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function formatNumber(v) {
  if (typeof v !== "number") return v;
  const a = Math.abs(v);
  if (a >= 1e9) return `${(v / 1e9).toFixed(1)}G`;
  if (a >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (a >= 1e4) return `${Math.round(v / 1e3)}K`;
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}

/** Sépare le texte de la réponse et le bloc <suggestions> (même pendant le streaming). */
export function splitSuggestions(text) {
  const start = text.indexOf("<suggestions>");
  if (start === -1) {
    const partial = text.match(/<s(u(g(g(e(s(t(i(o(n(s)?)?)?)?)?)?)?)?)?)?$/);
    return { body: partial ? text.slice(0, partial.index).trimEnd() : text, suggestions: [] };
  }
  const body = text.slice(0, start).trimEnd();
  const inner = text.slice(start + 13).split("</suggestions>")[0];
  const suggestions = inner
    .split("\n")
    .map((l) => l.replace(/^\s*[-*•\d.)]+\s*/, "").trim())
    .filter(Boolean)
    .slice(0, 3);
  return { body, suggestions };
}

export function buildReport(conv) {
  const lines = [`# ${conv.title}`, "", `_Rapport généré par ToolAgent le ${new Date().toLocaleString("fr-FR")}_`, ""];
  for (const m of conv.messages) {
    if (m.role === "user") {
      lines.push(`## 🧑 Question`, "", m.content);
      if (m.attachments?.length) lines.push("", `Fichiers : ${m.attachments.map((a) => a.name).join(", ")}`);
      lines.push("");
    } else {
      lines.push(`## ✨ Réponse`, "");
      if (m.steps?.length) lines.push(`**Outils utilisés :** ${m.steps.map((s) => s.label).join(" → ")}`, "");
      for (const b of m.blocks || []) {
        if (b.type === "chart") {
          lines.push(`**${b.title}**`, "", "| Libellé | Valeur |", "|---|---|", ...b.data.map((d) => `| ${d.name} | ${d.value} |`), "");
        } else if (b.type === "table") {
          lines.push(`**${b.title || "Tableau"}**`, "", `| ${b.columns.join(" | ")} |`, `|${b.columns.map(() => "---").join("|")}|`,
            ...b.rows.slice(0, 50).map((r) => `| ${r.join(" | ")} |`), "");
        } else if (b.type === "sources") {
          lines.push("**Sources**", "", ...b.items.map((s) => `- [${s.title}](${s.url})`), "");
        }
      }
      lines.push(splitSuggestions(m.content).body, "");
    }
  }
  return lines.join("\n");
}

export function download(filename, text) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/markdown;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
