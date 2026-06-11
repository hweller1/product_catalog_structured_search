interface Props {
  constraints: string[];
  query: string;
  reason: string;
}

export function QueryRouting({ constraints, query, reason }: Props) {
  const isFallback = reason !== "ok";

  return (
    <div
      className="rounded-2xl overflow-hidden"
      style={{ border: "1px solid rgba(0,30,43,0.08)", background: "white", boxShadow: "0 1px 3px rgba(0,30,43,0.06)" }}
    >
      <div className="px-5 py-3 flex items-center gap-2" style={{ background: "#001E2B", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: "#00ED64" }}>Query Routing</span>
        {isFallback && (
          <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "#EE810020", color: "#EE8100" }}>
            fallback — Claude routing unavailable
          </span>
        )}
      </div>

      <div className="grid grid-cols-2" style={{ borderTop: "1px solid #F0F4F5" }}>
        {/* Text pipeline */}
        <div className="p-5" style={{ borderRight: "1px solid #F0F4F5" }}>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-mono px-1.5 py-0.5 rounded" style={{ background: "#3B82F610", color: "#3B82F6" }}>$search</span>
            <span className="text-xs font-semibold" style={{ color: "#001E2B" }}>Text pipeline</span>
            <span className="text-xs" style={{ color: "#89979B" }}>Claude · BM25</span>
          </div>
          {constraints.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {constraints.map((c, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-full font-medium" style={{ background: "#001E2B08", color: "#001E2B", border: "1px solid rgba(0,30,43,0.1)" }}>
                  {c}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs" style={{ color: "#89979B" }}>
              {isFallback ? "Keyword match on product name" : "General text search"}
            </p>
          )}
        </div>

        {/* Vector pipeline */}
        <div className="p-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-mono px-1.5 py-0.5 rounded" style={{ background: "#8B5CF610", color: "#8B5CF6" }}>$vectorSearch</span>
            <span className="text-xs font-semibold" style={{ color: "#001E2B" }}>Vector pipeline</span>
            <span className="text-xs" style={{ color: "#89979B" }}>Voyage AI</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-xs px-2.5 py-1 rounded-full font-medium" style={{ background: "#8B5CF610", color: "#8B5CF6", border: "1px solid rgba(139,92,246,0.15)" }}>
              "{query}"
            </span>
          </div>
          <p className="text-xs mt-2" style={{ color: "#89979B" }}>
            voyage-4 · 1024-dim cosine similarity
          </p>
        </div>
      </div>
    </div>
  );
}
