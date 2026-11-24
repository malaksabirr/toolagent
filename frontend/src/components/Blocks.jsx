import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, LabelList, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AlertCircle, Database, ExternalLink, FileText, Table2 } from "lucide-react";
import { formatNumber } from "../utils.js";

const PALETTE = ["#5b1a33", "#c98a9f", "#e3cdbd", "#a04a68", "#d9b0be", "#8a6a75"];
const fmtTip = (v) => (typeof v === "number" ? v.toLocaleString("fr-FR") : v);

function ChartCard({ block }) {
  const { kind, title, data } = block;
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  const rows = data.map((d) => ({ ...d, pct: `${Math.round((d.value / total) * 100)}%` }));
  const axis = { fontSize: 11, fill: "var(--muted)" };
  return (
    <div className="chart-card">
      <h4>{title}</h4>
      {kind === "line" && (
        <ResponsiveContainer width="100%" height={190}>
          <LineChart data={rows} margin={{ top: 10, right: 14, left: -8, bottom: 0 }}>
            <CartesianGrid stroke="var(--line)" vertical={false} />
            <XAxis dataKey="name" tick={axis} tickLine={false} axisLine={{ stroke: "var(--line)" }} interval="preserveStartEnd" />
            <YAxis tick={axis} tickLine={false} axisLine={false} tickFormatter={formatNumber} width={46} />
            <Tooltip formatter={fmtTip} contentStyle={{ borderRadius: 12, border: "1px solid var(--line)", background: "var(--surface)", color: "var(--text)" }} />
            <Line type="monotone" dataKey="value" stroke="#7a2a47" strokeWidth={2.500} dot={{ r: 4, fill: "#7a2a47", strokeWidth: 0 }} activeDot={{ r: 6 }} />
          </LineChart>
        </ResponsiveContainer>
      )}
      {kind === "donut" && (
        <div className="donut">
          <ResponsiveContainer width={150} height={170}>
            <PieChart>
              <Pie data={rows} dataKey="value" nameKey="name" innerRadius={42} outerRadius={70} paddingAngle={2} stroke="var(--surface)" strokeWidth={2}>
                {rows.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
              </Pie>
              <Tooltip formatter={fmtTip} contentStyle={{ borderRadius: 12, border: "1px solid var(--line)", background: "var(--surface)", color: "var(--text)" }} />
            </PieChart>
          </ResponsiveContainer>
          <ul className="legend">
            {rows.map((r, i) => (
              <li key={r.name}><i style={{ background: PALETTE[i % PALETTE.length] }} /><span>{r.name}</span><b>{r.pct}</b></li>
            ))}
          </ul>
        </div>
      )}
      {kind === "bar" && (
        <ResponsiveContainer width="100%" height={190}>
          <BarChart data={rows} margin={{ top: 22, right: 8, left: 8, bottom: 0 }}>
            <XAxis dataKey="name" tick={axis} tickLine={false} axisLine={{ stroke: "var(--line)" }} interval={0} />
            <YAxis hide domain={[0, "dataMax"]} />
            <Tooltip formatter={fmtTip} cursor={{ fill: "var(--rose-soft)" }} contentStyle={{ borderRadius: 12, border: "1px solid var(--line)", background: "var(--surface)", color: "var(--text)" }} />
            <Bar dataKey="value" radius={[8, 8, 0, 0]} maxBarSize={56}>
              {rows.map((_, i) => <Cell key={i} fill={["#5b1a33", "#d9a9b7", "#a85a74"][i % 3]} />)}
              <LabelList dataKey="pct" position="top" style={{ fontSize: 12, fontWeight: 700, fill: "var(--text)" }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

function TableBlock({ block }) {
  return (
    <div className="table-card">
      <div className="table-head">
        {block.sql ? <Database size={15} /> : <Table2 size={15} />}
        <b>{block.title || "Tableau"}</b>
        <span>{block.rows.length} ligne{block.rows.length > 1 ? "s" : ""}</span>
      </div>
      {block.sql && <details><summary>Voir la requête SQL</summary><pre>{block.sql}</pre></details>}
      <div className="table-scroll">
        <table>
          <thead><tr>{block.columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
          <tbody>
            {block.rows.map((r, i) => (
              <tr key={i}>{r.map((v, j) => <td key={j} className={typeof v === "number" ? "num" : ""}>{typeof v === "number" ? v.toLocaleString("fr-FR") : String(v ?? "—")}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SourcesBlock({ block }) {
  const host = (u) => { try { return new URL(u).hostname.replace("www.", ""); } catch { return u; } };
  return (
    <div className="sources">
      <div className="sources-title">Sources consultées pour « {block.query} »</div>
      <div className="sources-grid">
        {block.items.map((s, i) => (
          <a key={i} href={s.url} target="_blank" rel="noreferrer" className="source">
            <span className="source-n">{i + 1}</span>
            <span className="source-body"><b>{s.title}</b><small>{host(s.url)}</small></span>
            <ExternalLink size={14} />
          </a>
        ))}
      </div>
    </div>
  );
}

function ImageBlock({ block }) {
  const [state, setState] = useState("loading");
  const [attempt, setAttempt] = useState(0);
  const src = attempt ? `${block.url}${block.url.includes("?") ? "&" : "?"}retry=${attempt}` : block.url;
  return (
    <figure className="image-card">
      {state === "loading" && <div className="img-skeleton"><span /> Création de l'image en cours…</div>}
      {state === "error" ? (
        <div className="img-error"><AlertCircle size={18} /> L'image n'a pas pu être chargée.
          <button onClick={() => { setState("loading"); setAttempt((a) => a + 1); }}>Réessayer</button></div>
      ) : (
        <img src={src} alt={block.prompt} style={{ display: state === "ready" ? "block" : "none" }}
          onLoad={() => setState("ready")} onError={() => setState("error")} />
      )}
      <figcaption>{block.prompt}</figcaption>
    </figure>
  );
}

function DatasetBlock({ block }) {
  return (
    <div className="chips-row">
      <span className="chip-info"><Table2 size={14} /> {block.rows.toLocaleString("fr-FR")} lignes</span>
      {block.columns.map((c) => <span key={c} className="chip-col">{c}</span>)}
    </div>
  );
}

function DocBlock({ block }) {
  return (
    <div className="chips-row">
      <span className="chip-info"><FileText size={14} /> {block.name}</span>
      <span className="chip-col">{block.words.toLocaleString("fr-FR")} mots</span>
      {block.pages ? <span className="chip-col">{block.pages} pages</span> : null}
    </div>
  );
}

export default function Blocks({ blocks }) {
  if (!blocks?.length) return null;
  const charts = blocks.filter((b) => b.type === "chart");
  const others = blocks.filter((b) => b.type !== "chart");
  return (
    <div className="blocks">
      {others.filter((b) => b.type === "dataset" || b.type === "doc").map((b) => (b.type === "doc" ? <DocBlock key={b.id} block={b} /> : <DatasetBlock key={b.id} block={b} />))}
      {charts.length > 0 && <div className={`charts charts-${Math.min(charts.length, 3)}`}>{charts.map((b) => <ChartCard key={b.id} block={b} />)}</div>}
      {others.filter((b) => b.type === "table").map((b) => <TableBlock key={b.id} block={b} />)}
      {others.filter((b) => b.type === "image").map((b) => <ImageBlock key={b.id} block={b} />)}
      {others.filter((b) => b.type === "sources").map((b) => <SourcesBlock key={b.id} block={b} />)}
    </div>
  );
}
