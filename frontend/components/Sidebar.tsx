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
        <span className="text-xs font-medium" style={{ color: "#89979B" }}>{label}</span>
        <span className="text-xs font-mono font-semibold" style={{ color: "#00ED64" }}>{value.toFixed(1)}</span>
      </div>
      <input
        type="range"
        min={0} max={2} step={0.1}
        value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
        style={{ accentColor: "#00ED64" }}
      />
    </div>
  );
}

export function Sidebar({ textWeight, vectorWeight, topK, onTextWeight, onVectorWeight, onTopK, demoQueries, onDemoClick }: Props) {
  return (
    <aside className="w-60 shrink-0 flex flex-col overflow-y-auto" style={{ background: "#001E2B", borderRight: "1px solid rgba(255,255,255,0.08)" }}>
      <div className="p-5 space-y-6">
        {/* Controls */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: "#89979B" }}>
            Pipeline Weights
          </p>
          <div className="space-y-5">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs px-1.5 py-0.5 rounded font-mono" style={{ background: "#023430", color: "#00ED64" }}>$search</span>
                <span className="text-xs text-white/60">Claude · BM25</span>
              </div>
              <Slider label="Text Weight" value={textWeight} onChange={onTextWeight} />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs px-1.5 py-0.5 rounded font-mono" style={{ background: "#023430", color: "#00ED64" }}>$vectorSearch</span>
                <span className="text-xs text-white/60">Voyage AI</span>
              </div>
              <Slider label="Vector Weight" value={vectorWeight} onChange={onVectorWeight} />
            </div>
          </div>
        </div>

        {/* Result count */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-medium" style={{ color: "#89979B" }}>Results</span>
            <span className="text-xs font-mono font-semibold text-white">{topK}</span>
          </div>
          <input
            type="range"
            min={5} max={20} step={5}
            value={topK}
            onChange={e => onTopK(parseInt(e.target.value))}
            className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
            style={{ accentColor: "#00ED64" }}
          />
        </div>

        {/* Demo queries */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: "#89979B" }}>
            Demo Queries
          </p>
          <div className="space-y-1.5">
            {demoQueries.map(({ label, query }) => (
              <button
                key={query}
                onClick={() => onDemoClick(query)}
                className="w-full text-left text-xs px-3 py-2 rounded-lg transition-all"
                style={{ color: "rgba(255,255,255,0.7)", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = "rgba(0,237,100,0.08)";
                  e.currentTarget.style.color = "#00ED64";
                  e.currentTarget.style.borderColor = "rgba(0,237,100,0.2)";
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = "rgba(255,255,255,0.04)";
                  e.currentTarget.style.color = "rgba(255,255,255,0.7)";
                  e.currentTarget.style.borderColor = "rgba(255,255,255,0.06)";
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-auto p-4 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
        <p className="text-xs" style={{ color: "#89979B" }}>
          MongoDB 8.0+ · M10+ cluster
        </p>
      </div>
    </aside>
  );
}
