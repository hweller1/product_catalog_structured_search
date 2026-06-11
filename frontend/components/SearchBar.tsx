"use client";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSearch: () => void;
  loading: boolean;
}

export function SearchBar({ value, onChange, onSearch, loading }: Props) {
  return (
    <div className="flex gap-3">
      <div className="flex-1 relative">
        <input
          type="text"
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={e => e.key === "Enter" && onSearch()}
          placeholder="e.g. kosher low sodium soup, organic cereal for kids, high protein snack…"
          className="w-full rounded-xl px-5 py-4 text-base outline-none transition-all"
          style={{
            background: "rgba(255,255,255,0.08)",
            border: "1.5px solid rgba(255,255,255,0.15)",
            color: "white",
            caretColor: "#00ED64",
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
      </div>
      <button
        onClick={onSearch}
        disabled={loading || !value.trim()}
        className="px-6 py-4 rounded-xl font-semibold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        style={{ background: "#00ED64", color: "#001E2B" }}
        onMouseEnter={e => { if (!loading) e.currentTarget.style.background = "#00c851"; }}
        onMouseLeave={e => { e.currentTarget.style.background = "#00ED64"; }}
      >
        {loading ? "Searching…" : "Search"}
      </button>
    </div>
  );
}
