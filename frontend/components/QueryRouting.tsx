interface Props {
  constraints: string[];
  query: string;
  reason: string;
}

export function QueryRouting({ constraints, query, reason }: Props) {
  const isFallback = reason !== "ok";

  return (
    <div className="rounded-2xl overflow-hidden" style={{ border: "1px solid rgba(0,30,43,0.1)", background: "white", boxShadow: "0 2px 8px rgba(0,30,43,0.06)" }}>
      <div className="px-6 py-4 flex items-center gap-3" style={{ background: "#001E2B" }}>
        <span className="text-sm font-bold uppercase tracking-widest" style={{ color: "#00ED64" }}>Query Routing</span>
        {isFallback && (
          <span className="text-sm px-3 py-1 rounded-full" style={{ background: "#EE810025", color: "#EE8100" }}>
            fallback — Claude routing unavailable
          </span>
        )}
      </div>

      <div className="grid grid-cols-2" style={{ borderTop: "1px solid #F0F4F5" }}>
        {/* Text pipeline */}
        <div className="p-6" style={{ borderRight: "1px solid #F0F4F5" }}>
          <div className="flex items-center gap-3 mb-4">
            <span className="text-sm font-mono px-2 py-1 rounded font-semibold" style={{ background: "#3B82F610", color: "#3B82F6" }}>$search</span>
            <span className="text-base font-semibold" style={{ color: "#001E2B" }}>Text pipeline</span>
            <span className="text-sm" style={{ color: "#89979B" }}>Claude · BM25</span>
          </div>
          {constraints.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {constraints.map((c, i) => (
                <span key={i} className="text-sm px-3 py-1.5 rounded-full font-medium" style={{ background: "#001E2B0A", color: "#001E2B", border: "1px solid rgba(0,30,43,0.12)" }}>
                  {c}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm" style={{ color: "#89979B" }}>
              {isFallback ? "Keyword match on product name" : "General text search"}
            </p>
          )}
        </div>

        {/* Vector pipeline */}
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-sm font-mono px-2 py-1 rounded font-semibold" style={{ background: "#8B5CF610", color: "#8B5CF6" }}>$vectorSearch</span>
            <span className="text-base font-semibold" style={{ color: "#001E2B" }}>Vector pipeline</span>
            <span className="text-sm" style={{ color: "#89979B" }}>Voyage AI</span>
          </div>
          <span className="text-sm px-3 py-1.5 rounded-full font-medium inline-block" style={{ background: "#8B5CF610", color: "#8B5CF6", border: "1px solid rgba(139,92,246,0.15)" }}>
            &ldquo;{query}&rdquo;
          </span>
          <p className="text-sm mt-3" style={{ color: "#89979B" }}>
            voyage-4 · 1024-dim cosine similarity
          </p>
        </div>
      </div>
    </div>
  );
}
