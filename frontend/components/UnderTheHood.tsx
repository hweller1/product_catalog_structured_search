"use client";

import { useState } from "react";
import { Product } from "@/lib/api";

interface Props {
  searchStage: Record<string, unknown>;
  pipeline: Record<string, unknown>[];
  results: Product[];
}

export function UnderTheHood({ searchStage, pipeline, results }: Props) {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<"search" | "scores" | "pipeline">("search");

  return (
    <div className="rounded-2xl overflow-hidden" style={{ border: "1px solid rgba(0,30,43,0.08)", background: "white" }}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full px-5 py-3 flex items-center justify-between text-left transition-colors"
        style={{ borderBottom: open ? "1px solid #F0F4F5" : undefined }}
      >
        <span className="text-sm font-semibold" style={{ color: "#001E2B" }}>Under the Hood</span>
        <span className="text-xs" style={{ color: "#89979B" }}>{open ? "▲ hide" : "▼ show"}</span>
      </button>

      {open && (
        <div>
          {/* Tabs */}
          <div className="flex border-b px-5" style={{ borderColor: "#F0F4F5" }}>
            {(["search", "scores", "pipeline"] as const).map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className="text-xs font-medium px-3 py-2 border-b-2 transition-colors"
                style={{
                  borderColor: tab === t ? "#00ED64" : "transparent",
                  color: tab === t ? "#001E2B" : "#89979B",
                }}
              >
                {t === "search" ? "Generated $search" : t === "scores" ? "Score Breakdown" : "Raw Pipeline"}
              </button>
            ))}
          </div>

          <div className="p-5">
            {tab === "search" && (
              <pre className="text-xs overflow-auto rounded-xl p-4 leading-relaxed" style={{ background: "#001E2B", color: "#00ED64", maxHeight: 320 }}>
                {JSON.stringify(searchStage, null, 2)}
              </pre>
            )}

            {tab === "scores" && (
              <div className="overflow-auto rounded-xl" style={{ border: "1px solid #F0F4F5" }}>
                <table className="w-full text-xs">
                  <thead>
                    <tr style={{ background: "#F0F4F5" }}>
                      <th className="text-left px-4 py-2 font-medium" style={{ color: "#89979B" }}>Product</th>
                      <th className="text-right px-4 py-2 font-medium" style={{ color: "#89979B" }}>RRF Score</th>
                      <th className="text-right px-4 py-2 font-medium" style={{ color: "#3B82F6" }}>Text Rank</th>
                      <th className="text-right px-4 py-2 font-medium" style={{ color: "#8B5CF6" }}>Vector Rank</th>
                      <th className="text-right px-4 py-2 font-medium" style={{ color: "#89979B" }}>Drove By</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((r, i) => (
                      <tr key={i} style={{ borderTop: "1px solid #F0F4F5" }}>
                        <td className="px-4 py-2 font-medium truncate max-w-48" style={{ color: "#001E2B" }}>{r.product_name}</td>
                        <td className="text-right px-4 py-2 font-mono" style={{ color: "#001E2B" }}>{r.score}</td>
                        <td className="text-right px-4 py-2 font-mono" style={{ color: "#3B82F6" }}>{r.text_rank}</td>
                        <td className="text-right px-4 py-2 font-mono" style={{ color: "#8B5CF6" }}>{r.vector_rank}</td>
                        <td className="text-right px-4 py-2" style={{ color: "#89979B" }}>{r.drove_by}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="px-4 py-2 text-xs" style={{ color: "#89979B", borderTop: "1px solid #F0F4F5" }}>
                  RRF scores are rank-based — lower rank = stronger match in that pipeline
                </p>
              </div>
            )}

            {tab === "pipeline" && (
              <pre className="text-xs overflow-auto rounded-xl p-4 leading-relaxed" style={{ background: "#001E2B", color: "#00ED64", maxHeight: 400 }}>
                {JSON.stringify(pipeline, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
