"use client";

interface Props {
  textWeight: number;
  vectorWeight: number;
  topK: number;
  onTextWeight: (v: number) => void;
  onVectorWeight: (v: number) => void;
  onTopK: (v: number) => void;
  demoQueries: { label: string; query: string }[];
  onDemoClick: (query: string) => void;
}

function Slider({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium" style={{ color: "rgba(255,255,255,0.6)" }}>{label}</span>
        <span className="text-sm font-mono font-bold" style={{ color: "#00ED64" }}>{value.toFixed(1)}</span>
      </div>
      <input
        type="range" min={0} max={2} step={0.1}
        value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className="w-full h-2 rounded-full appearance-none cursor-pointer"
        style={{ accentColor: "#00ED64" }}
      />
    </div>
  );
}

export function Sidebar({ textWeight, vectorWeight, topK, onTextWeight, onVectorWeight, onTopK, demoQueries, onDemoClick }: Props) {
  return (
    <aside className="w-72 shrink-0 flex flex-col overflow-y-auto" style={{ background: "#001E2B", borderRight: "1px solid rgba(255,255,255,0.08)" }}>
      <div className="p-6 space-y-8">

        {/* Pipeline weights */}
        <div>
          <p className="text-xs font-bold uppercase tracking-widest mb-5" style={{ color: "#00ED64" }}>
            Pipeline Weights
          </p>
          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-mono px-2 py-1 rounded font-semibold" style={{ background: "#023430", color: "#00ED64" }}>$search</span>
                <span className="text-sm" style={{ color: "rgba(255,255,255,0.5)" }}>Claude · BM25</span>
              </div>
              <Slider label="Text Weight" value={textWeight} onChange={onTextWeight} />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-mono px-2 py-1 rounded font-semibold" style={{ background: "#023430", color: "#00ED64" }}>$vectorSearch</span>
                <span className="text-sm" style={{ color: "rgba(255,255,255,0.5)" }}>Voyage AI</span>
              </div>
              <Slider label="Vector Weight" value={vectorWeight} onChange={onVectorWeight} />
            </div>
          </div>
        </div>

        {/* Result count */}
        <div>
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-medium" style={{ color: "rgba(255,255,255,0.6)" }}>Results</span>
            <span className="text-sm font-mono font-bold text-white">{topK}</span>
          </div>
          <input
            type="range" min={5} max={20} step={5}
            value={topK}
            onChange={e => onTopK(parseInt(e.target.value))}
            className="w-full h-2 rounded-full appearance-none cursor-pointer"
            style={{ accentColor: "#00ED64" }}
          />
        </div>

        {/* Demo queries */}
        <div>
          <p className="text-xs font-bold uppercase tracking-widest mb-4" style={{ color: "#00ED64" }}>
            Demo Queries
          </p>
          <div className="space-y-2">
            {demoQueries.map(({ label, query }) => (
              <button
                key={query}
                onClick={() => onDemoClick(query)}
                className="w-full text-left text-sm px-4 py-3 rounded-lg transition-all font-medium"
                style={{ color: "rgba(255,255,255,0.65)", background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)" }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = "rgba(0,237,100,0.1)";
                  e.currentTarget.style.color = "#00ED64";
                  e.currentTarget.style.borderColor = "rgba(0,237,100,0.25)";
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                  e.currentTarget.style.color = "rgba(255,255,255,0.65)";
                  e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)";
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-auto p-5 border-t" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
        <p className="text-sm" style={{ color: "rgba(255,255,255,0.35)" }}>MongoDB 8.0+ · M10+ cluster</p>
      </div>
    </aside>
  );
}
