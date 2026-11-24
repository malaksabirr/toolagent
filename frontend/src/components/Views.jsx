import { ArrowRight, Check, Trash2, Zap } from "lucide-react";
import { ToolIcon } from "./icons.jsx";

export const EXAMPLES = [
  { text: "Recherche les dernières actualités sur l'IA", q: "Recherche les dernières actualités sur l'IA et résume-les avec les sources." },
  { text: "Analyse ce fichier Excel", q: "Analyse ce fichier Excel et donne-moi un résumé avec les graphiques principaux.", file: true },
  { text: "Crée une image d'un paysage marocain", q: "Crée une image d'un paysage marocain : désert, dunes au coucher du soleil et caravane de dromadaires." },
  { text: "Résume ce document PDF", q: "Résume ce document PDF avec les points clés.", file: true },
  { text: "Interroge la base de données sur les clients", q: "Interroge la base de données : quels sont les 5 clients qui ont dépensé le plus, avec leur ville ?" },
  { text: "Explique-moi la différence entre RNN et Transformer", q: "Explique-moi la différence entre RNN et Transformer, avec un tableau comparatif." },
];

export function ExamplesPanel({ store }) {
  const go = (ex) => {
    if (ex.file) { store.setInput(ex.q); store.fileInputRef.current?.click(); } else store.send(ex.q);
  };
  return (
    <aside className="examples">
      <h3><Zap size={20} fill="currentColor" /> Exemples d'utilisations</h3>
      <ul>
        {EXAMPLES.map((ex) => (
          <li key={ex.text}>
            <button onClick={() => go(ex)} disabled={store.streaming}>
              <span>{ex.text}</span><ArrowRight size={16} />
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}

export function ToolsView({ store }) {
  return (
    <div className="page">
      <h2>Mes outils</h2>
      <p className="lead">L'agent choisit seul l'outil adapté à chaque demande. Désactivez ceux dont vous ne voulez pas.</p>
      <div className="tool-grid">
        {store.tools.map((t) => {
          const on = store.enabledTools.includes(t.name);
          return (
            <article key={t.name} className={on ? "tool-card" : "tool-card off"}>
              <div className="tool-card-top">
                <ToolIcon name={t.icon} size={46} />
                <button className={on ? "switch on" : "switch"} role="switch" aria-checked={on} aria-label={`${t.label} : ${on ? "activé" : "désactivé"}`}
                  onClick={() => store.toggleTool(t.name)}><i /></button>
              </div>
              <h4>{t.label}</h4>
              <p>{t.long_description}</p>
              {t.params.length > 0 && <small>Paramètres : {t.params.join(", ")}</small>}
            </article>
          );
        })}
        {store.tools.length === 0 && <p className="empty">Impossible de charger les outils : le backend est-il lancé ?</p>}
      </div>
    </div>
  );
}

export function HistoryView({ store }) {
  const fmt = (t) => new Date(t).toLocaleString("fr-FR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
  return (
    <div className="page">
      <h2>Historique</h2>
      <p className="lead">Vos conversations sont enregistrées dans ce navigateur.</p>
      {store.convs.length === 0 ? <p className="empty">Aucune conversation pour l'instant. Posez votre première question !</p> : (
        <ul className="history">
          {store.convs.map((c) => (
            <li key={c.id} className={c.id === store.activeId ? "current" : ""}>
              <button onClick={() => store.openConv(c.id)}>
                <b>{c.title}</b>
                <small>{c.messages.filter((m) => m.role === "user").length} question(s) · {fmt(c.updatedAt || c.createdAt)}</small>
              </button>
              <button className="icon-btn danger" aria-label="Supprimer" onClick={() => store.deleteConv(c.id)}><Trash2 size={18} /></button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function SettingsView({ store }) {
  const { settings, health } = store;
  return (
    <div className="page narrow">
      <h2>Paramètres</h2>
      <section className="setting">
        <div><b>Thème</b><small>Clair ou sombre</small></div>
        <div className="seg">
          {["light", "dark"].map((t) => (
            <button key={t} className={settings.theme === t ? "on" : ""} onClick={() => store.updateSettings({ theme: t })}>
              {settings.theme === t && <Check size={14} />} {t === "light" ? "Clair" : "Sombre"}
            </button>
          ))}
        </div>
      </section>
      <section className="setting col">
        <div className="row-between"><div><b>Créativité des réponses</b><small>Bas = précis et factuel · Haut = plus créatif</small></div><span className="val">{settings.temperature.toFixed(1)}</span></div>
        <input type="range" min="0" max="1.2" step="0.1" value={settings.temperature}
          onChange={(e) => store.updateSettings({ temperature: Number(e.target.value) })} />
      </section>
      <section className="setting col">
        <b>Modèle (défini dans le fichier .env)</b>
        <dl>
          <dt>Modèle</dt><dd>{health.model || "—"}</dd>
          <dt>Fournisseur</dt><dd>{health.provider || "—"}</dd>
          <dt>Outils</dt><dd>{store.enabledTools.length} actifs sur {store.tools.length}</dd>
          <dt>Backend</dt><dd>{health.status === "ok" ? (health.configured ? "Connecté, clé API détectée" : "Connecté, clé API manquante") : "Injoignable"}</dd>
        </dl>
      </section>
      <section className="setting">
        <div><b>Données locales</b><small>Supprime toutes les conversations enregistrées</small></div>
        <button className="btn-danger" onClick={() => { if (window.confirm("Supprimer toutes les conversations ?")) store.clearAll(); }}>
          <Trash2 size={16} /> Tout effacer
        </button>
      </section>
    </div>
  );
}
