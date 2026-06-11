"use client";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSearch: () => void;
  loading: boolean;
}

export function SearchBar({ value, onChange, onSearch, loading }: Props) {
  return (
    <div className="flex gap-4">
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        onKeyDown={e => e.key === "Enter" && onSearch()}
        placeholder="e.g. kosher low sodium soup, organic cereal for kids, high protein snack…"
        className="flex-1 rounded-xl px-6 py-5 text-lg outline-none transition-all"
        style={{
          background: "rgba(255,255,255,0.08)",
          border: "1.5px solid rgba(255,255,255,0.15)",
          color: "white",
          caretColor: "#00ED64",
          fontSize: "1.125rem",
        }}
        onFocus={e => {
          e.currentTarget.style.borderColor = "#00ED64";
          e.currentTarget.style.background = "rgba(255,255,255,0.12)";
        }}
        onBlur={e => {
          e.currentTarget.style.borderColor = "rgba(255,255,255,0.15)";
          e.currentTarget.style.background = "rgba(255,255,255,0.08)";
        }}
      />
      <button
        onClick={onSearch}
        disabled={loading || !value.trim()}
        className="px-10 py-5 rounded-xl font-bold text-base transition-all disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap"
        style={{ background: "#00ED64", color: "#001E2B", fontSize: "1rem" }}
        onMouseEnter={e => { if (!loading && value.trim()) e.currentTarget.style.background = "#00c851"; }}
        onMouseLeave={e => { e.currentTarget.style.background = "#00ED64"; }}
      >
        {loading ? "Searching…" : "Search"}
      </button>
    </div>
  );
}
