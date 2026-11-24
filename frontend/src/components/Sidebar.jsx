import { History, LayoutGrid, MessageCircle, Plus, Settings } from "lucide-react";
import { Mascot, SparkleLogo, ToolIcon } from "./icons.jsx";

const NAV = [
  { id: "chat", label: "Chat", Icon: MessageCircle },
  { id: "tools", label: "Mes outils", Icon: LayoutGrid },
  { id: "history", label: "Historique", Icon: History },
  { id: "settings", label: "Paramètres", Icon: Settings },
];

export default function Sidebar({ store }) {
  const { view, setView, tools, enabledTools, health } = store;
  const online = health.status === "ok";
  const featured = tools.filter((t) => ["web_search", "analyze_dataset", "run_sql", "generate_image", "summarize_document"].includes(t.name));
  const labels = { web_search: "Recherche Web", analyze_dataset: "Analyse de données", run_sql: "Exécution SQL", generate_image: "Génération d'images", summarize_document: "Résumé de documents" };
  return (
    <aside className="sidebar">
      <div className="brand">
        <SparkleLogo size={52} />
        <div>
          <h1>ToolAgent</h1>
          <p>Posez, explorez, automatisez ✨</p>
        </div>
      </div>

      <button className="new-chat" onClick={store.newChat}><Plus size={18} /> Nouvelle conversation</button>

      <nav>
        {NAV.map(({ id, label, Icon }) => (
          <button key={id} className={view === id ? "nav active" : "nav"} onClick={() => setView(id)} aria-current={view === id ? "page" : undefined}>
            <Icon size={22} strokeWidth={1.800} /> <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="divider" />

      <div className="tools-head">
        <span>Outils disponibles</span>
        <span className={online ? "live on" : "live"}><i /> {online ? "En ligne" : "Hors ligne"}</span>
      </div>
      <ul className="tools-list">
        {featured.map((t) => (
          <li key={t.name} className={enabledTools.includes(t.name) ? "" : "off"}>
            <ToolIcon name={t.icon} size={42} />
            <span><b>{labels[t.name] || t.label}</b><small>{t.description}</small></span>
          </li>
        ))}
        {featured.length === 0 && <li className="off"><span><small>Démarrez le backend pour charger les outils.</small></span></li>}
      </ul>

      <div className="mascot-wrap"><Mascot /></div>
    </aside>
  );
}
