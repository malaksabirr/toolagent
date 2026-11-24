import { useEffect, useRef, useState } from "react";
import { AlertCircle, ArrowUp, FileText, Loader2, Paperclip, Square, X } from "lucide-react";
import { AssistantMessage, UserMessage } from "./Message.jsx";
import { SparkleLogo } from "./icons.jsx";
import { formatSize } from "../utils.js";

const STARTERS = [
  { t: "Analyse un fichier CSV", s: "Joins ton fichier : résumé + graphiques automatiques", file: true,
    q: "Analyse ce fichier CSV et donne-moi un résumé avec les graphiques principaux." },
  { t: "Actualités de l'IA", s: "Recherche web avec sources", q: "Recherche les dernières actualités sur l'IA et résume-les avec les sources." },
  { t: "Interroger la base clients", s: "SQL en langage naturel", q: "Interroge la base de données : quelles sont les 5 villes avec le plus de clients ?" },
  { t: "Expliquer un concept", s: "Réponse directe, sans outil", q: "Explique-moi le mécanisme d'attention des transformers comme si j'étais débutant." },
];

export default function Chat({ store }) {
  const { active, input, setInput, pending, uploading, streaming, notice, composerRef, fileInputRef, health } = store;
  const scroller = useRef(null);
  const stick = useRef(true);
  const [drag, setDrag] = useState(false);

  const messages = active?.messages || [];
  const last = messages[messages.length - 1];

  useEffect(() => {
    const el = scroller.current;
    if (el && stick.current) el.scrollTop = el.scrollHeight;
  }, [messages.length, last?.content, last?.steps?.length, last?.blocks?.length]);

  const onScroll = () => {
    const el = scroller.current;
    stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
  };

  useEffect(() => {
    const ta = composerRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  }, [input, composerRef]);

  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); store.send(); }
  };
  const onDrop = (e) => {
    e.preventDefault(); setDrag(false);
    if (e.dataTransfer.files?.length) store.attach(e.dataTransfer.files);
  };
  const startWith = (s) => {
    if (s.file) { store.setInput(s.q); fileInputRef.current?.click(); } else store.send(s.q);
  };

  const canSend = !streaming && !uploading && (input.trim() || pending.length > 0);

  return (
    <section className={`chat ${drag ? "dragging" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)} onDrop={onDrop}>
      <div className="scroller" ref={scroller} onScroll={onScroll}>
        {messages.length === 0 ? (
          <div className="hero">
            <SparkleLogo size={72} />
            <h2>Que puis-je faire pour vous ?</h2>
            <p>Posez n'importe quelle question. Je cherche sur le web, analyse vos fichiers, interroge une base SQL, crée des images et résume vos documents.</p>
            <div className="starters">
              {STARTERS.map((s) => (
                <button key={s.t} onClick={() => startWith(s)}><b>{s.t}</b><span>{s.s}</span></button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((m, i) => m.role === "user"
              ? <UserMessage key={m.id} m={m} />
              : <AssistantMessage key={m.id} m={m} conv={active} isLast={i === messages.length - 1}
                  onSend={store.send} onAskAgain={store.askAgain} busy={streaming} />)}
          </div>
        )}
      </div>

      {drag && <div className="drop-overlay">Déposez votre fichier ici</div>}

      <div className="composer-wrap">
        {notice && <div className="error-box small"><AlertCircle size={16} /><span>{notice}</span><button onClick={() => store.setNotice(null)}><X size={14} /></button></div>}
        {health.status === "ok" && !health.configured && (
          <div className="error-box small"><AlertCircle size={16} /><span>Clé API manquante : renseigne <code>LLM_API_KEY</code> dans <code>.env</code> puis relance le backend.</span></div>
        )}
        {(pending.length > 0 || uploading) && (
          <div className="pending">
            {pending.map((f) => (
              <span key={f.id} className="file-chip"><FileText size={16} /><b>{f.name}</b><small>({formatSize(f.size)})</small>
                <button onClick={() => store.removePending(f.id)} aria-label={`Retirer ${f.name}`}><X size={14} /></button></span>
            ))}
            {uploading && <span className="file-chip"><Loader2 size={16} className="spin" /> Téléversement…</span>}
          </div>
        )}
        <div className="composer">
          <input ref={fileInputRef} type="file" multiple hidden accept=".csv,.tsv,.xlsx,.xls,.json,.pdf,.docx,.txt,.md"
            onChange={(e) => { if (e.target.files?.length) store.attach(e.target.files); e.target.value = ""; }} />
          <button className="icon-btn" onClick={() => fileInputRef.current?.click()} aria-label="Joindre un fichier" title="Joindre un fichier (CSV, Excel, PDF, DOCX, TXT)">
            <Paperclip size={21} />
          </button>
          <textarea ref={composerRef} rows={1} value={input} placeholder="Posez votre question ou demandez une action..."
            onChange={(e) => setInput(e.target.value)} onKeyDown={onKey} />
          {streaming ? (
            <button className="send stop" onClick={store.stop} aria-label="Arrêter"><Square size={18} fill="currentColor" /></button>
          ) : (
            <button className="send" onClick={() => store.send()} disabled={!canSend} aria-label="Envoyer"><ArrowUp size={22} /></button>
          )}
        </div>
        <p className="hint">Entrée pour envoyer · Maj+Entrée pour un retour à la ligne · glissez un fichier pour le joindre</p>
      </div>
    </section>
  );
}
