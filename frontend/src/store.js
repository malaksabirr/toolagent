import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { getHealth, getTools, streamChat, uploadFile } from "./api.js";
import { splitSuggestions, uid } from "./utils.js";

const LS_CONVS = "toolagent.convs.v1";
const LS_SETTINGS = "toolagent.settings.v1";

function load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

const DEFAULT_SETTINGS = { theme: "light", temperature: 0.3, disabledTools: [] };

export function useStore() {
  const [convs, setConvs] = useState(() => load(LS_CONVS, []));
  const [activeId, setActiveId] = useState(null);
  const [settings, setSettings] = useState(() => ({ ...DEFAULT_SETTINGS, ...load(LS_SETTINGS, {}) }));
  const [health, setHealth] = useState({ status: "loading" });
  const [tools, setTools] = useState([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [notice, setNotice] = useState(null);
  const [view, setView] = useState("chat");
  const abortRef = useRef(null);
  const composerRef = useRef(null);
  const fileInputRef = useRef(null);

  // ── persistance ───────────────────────────────────────────────
  useEffect(() => {
    const t = setTimeout(() => {
      try { localStorage.setItem(LS_CONVS, JSON.stringify(convs.slice(0, 50))); } catch { /* quota */ }
    }, 600);
    return () => clearTimeout(t);
  }, [convs]);

  useEffect(() => {
    localStorage.setItem(LS_SETTINGS, JSON.stringify(settings));
    document.documentElement.dataset.theme = settings.theme;
  }, [settings]);

  // ── santé du backend + outils ─────────────────────────────────
  useEffect(() => {
    let alive = true;
    const ping = () => getHealth().then((h) => alive && setHealth(h)).catch(() => alive && setHealth({ status: "down" }));
    ping();
    const t = setInterval(ping, 15000);
    getTools().then((t2) => alive && setTools(t2)).catch(() => {});
    return () => { alive = false; clearInterval(t); };
  }, []);
  useEffect(() => {
    if (health.status === "ok" && tools.length === 0) getTools().then(setTools).catch(() => {});
  }, [health.status, tools.length]);

  const active = useMemo(() => convs.find((c) => c.id === activeId) || null, [convs, activeId]);
  const enabledTools = useMemo(
    () => tools.map((t) => t.name).filter((n) => !settings.disabledTools.includes(n)),
    [tools, settings.disabledTools],
  );

  const patchMessage = useCallback((convId, msgId, fn) => {
    setConvs((prev) => prev.map((c) => (c.id !== convId ? c : {
      ...c, updatedAt: Date.now(),
      messages: c.messages.map((m) => (m.id === msgId ? fn(m) : m)),
    })));
  }, []);

  // ── actions ───────────────────────────────────────────────────
  const newChat = useCallback(() => {
    setActiveId(null); setView("chat"); setInput(""); setPending([]);
    setTimeout(() => composerRef.current?.focus(), 50);
  }, []);

  const openConv = useCallback((id) => { setActiveId(id); setView("chat"); }, []);
  const deleteConv = useCallback((id) => {
    setConvs((p) => p.filter((c) => c.id !== id));
    setActiveId((a) => (a === id ? null : a));
  }, []);
  const clearAll = useCallback(() => { setConvs([]); setActiveId(null); }, []);
  const updateSettings = useCallback((patch) => setSettings((s) => ({ ...s, ...patch })), []);
  const toggleTool = useCallback((name) => setSettings((s) => ({
    ...s, disabledTools: s.disabledTools.includes(name) ? s.disabledTools.filter((n) => n !== name) : [...s.disabledTools, name],
  })), []);

  const attach = useCallback(async (fileList) => {
    setUploading(true); setNotice(null);
    try {
      for (const f of Array.from(fileList)) {
        const meta = await uploadFile(f);
        setPending((p) => [...p, meta]);
      }
    } catch (e) {
      setNotice(e.message || "Échec du téléversement");
    } finally {
      setUploading(false);
    }
  }, []);
  const removePending = useCallback((id) => setPending((p) => p.filter((f) => f.id !== id)), []);

  const stop = useCallback(() => abortRef.current?.abort(), []);

  const send = useCallback(async (textArg) => {
    const raw = (typeof textArg === "string" ? textArg : input).trim();
    if (streaming || uploading || (!raw && pending.length === 0)) return;
    const text = raw || "Analyse ce fichier et donne-moi un résumé avec les points principaux.";
    setNotice(null);

    const convId = active ? active.id : uid();
    const base = active || { id: convId, title: text.slice(0, 48), messages: [], files: [], createdAt: Date.now() };
    const attachments = pending;
    const userMsg = { id: uid(), role: "user", content: text, attachments };
    const asst = { id: uid(), role: "assistant", content: "", steps: [], blocks: [], status: "streaming" };
    const files = [...base.files, ...attachments];

    const history = [...base.messages, userMsg]
      .filter((m) => m.role === "user" || m.status === "done" || m.status === "stopped")
      .map((m) => ({ role: m.role, content: m.role === "assistant" ? splitSuggestions(m.content).body : m.content }))
      .filter((m) => m.content);
    if (attachments.length) {
      history[history.length - 1].content += `\n\n[Fichiers joints : ${attachments.map((a) => `${a.name} (id=${a.id})`).join(", ")}]`;
    }

    setConvs((prev) => {
      const next = { ...base, files, updatedAt: Date.now(), messages: [...base.messages, userMsg, asst] };
      return active ? prev.map((c) => (c.id === convId ? next : c)) : [next, ...prev];
    });
    setActiveId(convId); setView("chat"); setInput(""); setPending([]); setStreaming(true);

    const ctrl = new AbortController();
    abortRef.current = ctrl;
    let buf = "";
    let timer = null;
    const flush = () => {
      if (timer) { clearTimeout(timer); timer = null; }
      if (!buf) return;
      const t = buf; buf = "";
      patchMessage(convId, asst.id, (m) => ({ ...m, content: m.content + t }));
    };

    const onEvent = (ev) => {
      if (ev.type === "token") {
        buf += ev.text;
        if (!timer) timer = setTimeout(flush, 40);
        return;
      }
      flush();
      if (ev.type === "tool_start") {
        patchMessage(convId, asst.id, (m) => ({ ...m, steps: [...m.steps, { id: ev.id, name: ev.name, label: ev.label, icon: ev.icon, args: ev.args, status: "running" }] }));
      } else if (ev.type === "tool_result") {
        patchMessage(convId, asst.id, (m) => ({ ...m, steps: m.steps.map((s) => (s.id === ev.id ? { ...s, status: ev.ok ? "done" : "error", summary: ev.summary, ms: ev.ms } : s)) }));
      } else if (ev.type === "block") {
        patchMessage(convId, asst.id, (m) => ({ ...m, blocks: [...m.blocks, { id: uid(), ...ev.block }] }));
      } else if (ev.type === "error") {
        patchMessage(convId, asst.id, (m) => ({ ...m, error: ev.message }));
      }
    };

    try {
      await streamChat({ messages: history, files, enabled_tools: enabledTools, temperature: settings.temperature }, onEvent, ctrl.signal);
      flush();
      patchMessage(convId, asst.id, (m) => ({ ...m, status: m.error && !m.content ? "error" : "done" }));
    } catch (e) {
      flush();
      if (e.name === "AbortError") {
        patchMessage(convId, asst.id, (m) => ({ ...m, status: "stopped" }));
      } else {
        patchMessage(convId, asst.id, (m) => ({
          ...m, status: "error",
          error: "Impossible de joindre le backend. Vérifie qu'il tourne sur le port 8000 (voir README).",
        }));
      }
    } finally {
      setStreaming(false);
      abortRef.current = null;
      setTimeout(() => composerRef.current?.focus(), 50);
    }
  }, [active, input, pending, streaming, uploading, enabledTools, settings.temperature, patchMessage]);

  const askAgain = useCallback(() => {
    const lastUser = [...(active?.messages || [])].reverse().find((m) => m.role === "user");
    if (lastUser) setInput(lastUser.content);
    setTimeout(() => composerRef.current?.focus(), 30);
  }, [active]);

  return {
    convs, active, activeId, settings, health, tools, enabledTools, input, setInput, pending, uploading, streaming,
    notice, setNotice, view, setView, composerRef, fileInputRef,
    send, stop, attach, removePending, newChat, openConv, deleteConv, clearAll, updateSettings, toggleTool, askAgain,
  };
}
