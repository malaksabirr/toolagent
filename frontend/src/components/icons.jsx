import {
  BarChart3, Calculator, Clock, Cloud, Database, FileText, Globe, Image as ImageIcon, Search, Wrench,
} from "lucide-react";

export function SparkleLogo({ size = 56 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
      <defs>
        <linearGradient id="sg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f6d5dd" />
          <stop offset="1" stopColor="#c98a9f" />
        </linearGradient>
      </defs>
      <path d="M32 4c2.4 16 12 26 28 28-16 2-25.600 12-28 28-2.400-16-12-26-28-28C20 30 29.600 20 32 4z" fill="url(#sg)" />
      <path d="M52 6c.8 4 3 6.400 7 7-4 .8-6.200 3-7 7-.8-4-3-6.200-7-7 4-.6 6.200-3 7-7z" fill="#e7b7c4" opacity=".8" />
    </svg>
  );
}

export function Mascot() {
  return (
    <svg viewBox="0 0 220 190" className="mascot" aria-hidden="true">
      <path d="M0 150c40-30 80-34 120-18s70 14 100-8v66H0z" fill="#7a2a47" opacity=".55" />
      <circle cx="30" cy="48" r="3" fill="#f0c9d3" /><circle cx="190" cy="40" r="2.500" fill="#f0c9d3" />
      <path d="M26 20c1 6 4 9 10 10-6 1-9 4-10 10-1-6-4-9-10-10 6-1 9-4 10-10z" fill="#f0c9d3" />
      <path d="M180 62c.8 4 3 6 7 7-4 .8-6 3-7 7-.8-4-3-6-7-7 4-1 6-3 7-7z" fill="#f0c9d3" />
      <line x1="104" y1="22" x2="104" y2="38" stroke="#e8d5da" strokeWidth="3" strokeLinecap="round" />
      <circle cx="104" cy="20" r="4.500" fill="#e8d5da" />
      <rect x="52" y="36" width="104" height="88" rx="38" fill="#f4eaec" />
      <rect x="40" y="68" width="14" height="30" rx="7" fill="#e3ccd2" /><rect x="154" y="68" width="14" height="30" rx="7" fill="#e3ccd2" />
      <rect x="64" y="52" width="80" height="56" rx="24" fill="#2e1520" />
      <path d="M82 76q8-9 16 0M110 76q8-9 16 0" stroke="#f4eaec" strokeWidth="5" strokeLinecap="round" fill="none" />
      <path d="M94 90q10 9 20 0" stroke="#e8a3b6" strokeWidth="4.500" strokeLinecap="round" fill="none" />
      <rect x="62" y="128" width="84" height="26" rx="13" fill="#f4eaec" />
      <path d="M96 138l52-8 26 40-82 6z" fill="#3a2a33" />
      <circle cx="132" cy="156" r="5" fill="#8d7a84" />
      <path d="M70 154l72-10 4 22-76 8z" fill="#2a1a22" opacity=".9" />
    </svg>
  );
}

const MAP = {
  search: { Icon: Search, bg: "linear-gradient(135deg,#4f8bf5,#3f63e0)", fg: "#fff" },
  globe: { Icon: Globe, bg: "linear-gradient(135deg,#5b9cf5,#4a73e8)", fg: "#fff" },
  chart: { Icon: BarChart3, bg: "linear-gradient(135deg,#b28bf0,#8a62d8)", fg: "#fff" },
  database: { Icon: Database, bg: "linear-gradient(135deg,#f3e2a0,#e6cf7d)", fg: "#4a3a10" },
  image: { Icon: ImageIcon, bg: "linear-gradient(135deg,#7ad3a0,#4cb883)", fg: "#fff" },
  file: { Icon: FileText, bg: "linear-gradient(135deg,#6f9bf2,#4f78e4)", fg: "#fff" },
  calculator: { Icon: Calculator, bg: "linear-gradient(135deg,#f0a7b9,#d9748f)", fg: "#fff" },
  clock: { Icon: Clock, bg: "linear-gradient(135deg,#f2b78a,#e08f5a)", fg: "#fff" },
  cloud: { Icon: Cloud, bg: "linear-gradient(135deg,#78cde0,#4fa9c8)", fg: "#fff" },
  tool: { Icon: Wrench, bg: "linear-gradient(135deg,#bda0aa,#8d6f7b)", fg: "#fff" },
};

export function ToolIcon({ name, size = 44 }) {
  const { Icon, bg, fg } = MAP[name] || MAP.tool;
  return (
    <span className="tool-tile" style={{ width: size, height: size, background: bg, color: fg, borderRadius: size * 0.3 }}>
      <Icon size={size * 0.5} strokeWidth={2.200} />
    </span>
  );
}
