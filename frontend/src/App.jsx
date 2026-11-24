import { Moon, Sun } from "lucide-react";
import Sidebar from "./components/Sidebar.jsx";
import Chat from "./components/Chat.jsx";
import { ExamplesPanel, HistoryView, SettingsView, ToolsView } from "./components/Views.jsx";
import { useStore } from "./store.js";

const TITLES = {
  chat: ["Agent Conversationnel à Outils", "Un assistant intelligent qui utilise des outils pour vous aider"],
  tools: ["Mes outils", "Les capacités de votre agent"],
  history: ["Historique", "Reprenez une conversation"],
  settings: ["Paramètres", "Personnalisez votre expérience"],
};

export default function App() {
  const store = useStore();
  const { health, settings, view } = store;
  const [title, subtitle] = TITLES[view];
  const status = health.status === "loading" ? ["Connexion…", "wait"]
    : health.status !== "ok" ? ["Backend hors ligne", "bad"]
    : !health.configured ? ["Clé API manquante", "warn"] : ["Agent prêt", "ok"];

  return (
    <div className="app">
      <Sidebar store={store} />
      <main className="main">
        <header className="topbar">
          <div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          <div className="top-actions">
            <span className={`status ${status[1]}`}><i /> {status[0]}</span>
            <div className="theme-toggle" role="group" aria-label="Thème">
              <button className={settings.theme === "light" ? "on" : ""} onClick={() => store.updateSettings({ theme: "light" })} aria-label="Thème clair"><Sun size={19} /></button>
              <button className={settings.theme === "dark" ? "on" : ""} onClick={() => store.updateSettings({ theme: "dark" })} aria-label="Thème sombre"><Moon size={19} /></button>
            </div>
          </div>
        </header>
        <div className="content">
          {view === "chat" && <><Chat store={store} /><ExamplesPanel store={store} /></>}
          {view === "tools" && <ToolsView store={store} />}
          {view === "history" && <HistoryView store={store} />}
          {view === "settings" && <SettingsView store={store} />}
        </div>
      </main>
    </div>
  );
}
