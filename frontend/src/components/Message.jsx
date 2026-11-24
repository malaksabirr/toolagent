import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AlertCircle, Check, ChevronDown, Copy, Download, FileText, Loader2, RefreshCw, BarChart3, User } from "lucide-react";
import Blocks from "./Blocks.jsx";
import { SparkleLogo, ToolIcon } from "./icons.jsx";
import { buildReport, download, formatSize, splitSuggestions } from "../utils.js";

const mdComponents = {
  a: ({ node, ...p }) => <a {...p} target="_blank" rel="noreferrer" />,
  table: ({ node, ...p }) => <div className="md-table"><table {...p} /></div>,
  pre: ({ node, children, ...p }) => <CodeBlock {...p}>{children}</CodeBlock>,
};

function CodeBlock({ children }) {
  const [copied, setCopied] = useState(false);
  const code = children?.props?.children;
  const lang = /language-(\w+)/.exec(children?.props?.className || "")?.[1];
  return (
    <div className="code">
      <div className="code-bar">
        <span>{lang || "code"}</span>
        <button onClick={() => { navigator.clipboard?.writeText(String(code)); setCopied(true); setTimeout(() => setCopied(false), 1400); }}>
          {copied ? <><Check size={13} /> Copié</> : <><Copy size={13} /> Copier</>}
        </button>
      </div>
      <pre>{children}</pre>
    </div>
  );
}

function argPreview(args) {
  const v = Object.values(args || {}).find((x) => typeof x === "string");
  return v ? (v.length > 70 ? `${v.slice(0, 70)}…` : v) : "";
}

function Steps({ steps, streaming }) {
  const [open, setOpen] = useState(true);
  if (!steps?.length) return null;
  const running = steps.some((s) => s.status === "running");
  return (
    <div className="steps">
      <button className="steps-head" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        {running ? <Loader2 size={15} className="spin" /> : <Check size={15} />}
        <span>{running ? "L'agent utilise ses outils…" : `${steps.length} outil${steps.length > 1 ? "s" : ""} utilisé${steps.length > 1 ? "s" : ""}`}</span>
        <ChevronDown size={15} className={open ? "chev open" : "chev"} />
      </button>
      {(open || (streaming && running)) && (
        <ul>
          {steps.map((s) => (
            <li key={s.id} className={`step ${s.status}`}>
              <ToolIcon name={s.icon} size={28} />
              <span className="step-main"><b>{s.label}</b><small>{argPreview(s.args) || "—"}</small></span>
              <span className="step-state">
                {s.status === "running" && <Loader2 size={15} className="spin" />}
                {s.status === "done" && <><em>{s.summary}</em><Check size={15} /></>}
                {s.status === "error" && <><em>{s.summary}</em><AlertCircle size={15} /></>}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function UserMessage({ m }) {
  return (
    <div className="row user">
      <div className="bubble user-bubble">
        <p>{m.content}</p>
        {m.attachments?.length > 0 && (
          <div className="attach-row">
            {m.attachments.map((a) => (
              <span key={a.id} className="file-chip"><FileText size={17} /><b>{a.name}</b><small>({formatSize(a.size)})</small></span>
            ))}
          </div>
        )}
      </div>
      <span className="avatar user-avatar"><User size={22} /></span>
    </div>
  );
}

export function AssistantMessage({ m, isLast, conv, onSend, onAskAgain, busy }) {
  const { body, suggestions } = splitSuggestions(m.content);
  const streaming = m.status === "streaming";
  const thinking = streaming && !body && !m.steps.length;
  const showActions = isLast && !streaming;
  return (
    <div className="row assistant">
      <span className="avatar bot-avatar"><SparkleLogo size={30} /></span>
      <div className="stack">
        <div className="bubble bot-bubble">
          <Steps steps={m.steps} streaming={streaming} />
          <Blocks blocks={m.blocks} />
          {thinking && <div className="typing"><i /><i /><i /></div>}
          {body && (
            <div className={`md ${streaming ? "streaming" : ""}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>{body}</ReactMarkdown>
            </div>
          )}
          {m.status === "stopped" && <div className="note">Génération interrompue.</div>}
          {m.error && <div className="error-box"><AlertCircle size={17} /><span>{m.error}</span></div>}
        </div>
        {showActions && suggestions.length > 0 && (
          <div className="suggestions">
            {suggestions.map((s) => <button key={s} onClick={() => onSend(s)} disabled={busy}>{s}</button>)}
          </div>
        )}
        {showActions && (
          <div className="actions">
            <button onClick={() => download(`${conv.title.replace(/[^\w]+/g, "_").slice(0, 40) || "rapport"}.md`, buildReport(conv))}>
              <Download size={17} /> Télécharger le rapport
            </button>
            <button onClick={() => onSend("Donne-moi plus de détails et une analyse plus approfondie de ta dernière réponse.")} disabled={busy}>
              <BarChart3 size={17} /> Voir plus de détails
            </button>
            <button onClick={onAskAgain}><RefreshCw size={17} /> Reposer une question</button>
          </div>
        )}
      </div>
    </div>
  );
}
