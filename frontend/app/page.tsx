"use client";

import { useState, useCallback } from "react";
import { runSearch, SearchResponse } from "@/lib/api";
import { SearchBar } from "@/components/SearchBar";
import { Sidebar } from "@/components/Sidebar";
import { ProductGrid } from "@/components/ProductGrid";
import { QueryRouting } from "@/components/QueryRouting";
import { UnderTheHood } from "@/components/UnderTheHood";

const DEMO_QUERIES = [
  { label: "Label filter: kosher + low sodium", query: "kosher low sodium soup" },
  { label: "Semantic: organic cereal", query: "organic whole grain cereal kids" },
  { label: "Hybrid: vegan protein bar", query: "vegan protein bar chocolate" },
  { label: "Claims: gluten free + protein", query: "gluten free pasta high protein" },
  { label: "Semantic: keto snack", query: "keto friendly snack low carb" },
  { label: "Exact: Nutri-Score A dairy", query: "Nutri-Score A dairy product" },
  { label: "Lexical: brand search", query: "Clif bar flavors" },
  { label: "Multi-constraint: high fiber", query: "high fiber breakfast food low sugar" },
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [textWeight, setTextWeight] = useState(1.0);
  const [vectorWeight, setVectorWeight] = useState(1.0);
  const [topK, setTopK] = useState(10);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const doSearch = useCallback(async (q: string, tw = textWeight, vw = vectorWeight, tk = topK) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await runSearch(q, tw, vw, tk);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }, [textWeight, vectorWeight, topK]);

  const handleDemoClick = (q: string) => {
    setQuery(q);
    doSearch(q);
  };

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "#F0F4F5" }}>
      <Sidebar
        textWeight={textWeight}
        vectorWeight={vectorWeight}
        topK={topK}
        onTextWeight={setTextWeight}
        onVectorWeight={setVectorWeight}
        onTopK={setTopK}
        demoQueries={DEMO_QUERIES}
        onDemoClick={handleDemoClick}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header style={{ background: "#001E2B" }} className="px-8 py-4 flex items-center gap-4 shrink-0">
          <div className="flex items-center gap-2">
            <LeafIcon />
            <span className="text-white font-semibold text-base tracking-tight">MongoDB</span>
          </div>
          <div className="h-4 w-px bg-white/20" />
          <span className="text-white/60 text-sm">Structured Search Demo</span>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: "#00ED6420", color: "#00ED64" }}>
              $rankFusion
            </span>
          </div>
        </header>

        {/* Search bar */}
        <div style={{ background: "#001E2B" }} className="px-8 pb-6 pt-2 shrink-0">
          <SearchBar
            value={query}
            onChange={setQuery}
            onSearch={() => doSearch(query)}
            loading={loading}
          />
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          {error && (
            <div className="mb-4 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              {error} — is the API server running? <code className="bg-red-100 px-1 rounded">uvicorn api.main:app --port 8000</code>
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-24">
              <div className="flex flex-col items-center gap-4">
                <div
                  className="w-8 h-8 border-2 rounded-full animate-spin"
                  style={{ borderColor: "#00ED6440", borderTopColor: "#00ED64" }}
                />
                <span className="text-sm" style={{ color: "#89979B" }}>
                  Claude routing → Voyage embedding → $rankFusion…
                </span>
              </div>
            </div>
          )}

          {!loading && result && (
            <div className="space-y-6">
              <QueryRouting constraints={result.constraints} query={result.query} reason={result.reason} />
              <ProductGrid results={result.results} />
              <UnderTheHood searchStage={result.search_stage} pipeline={result.pipeline} results={result.results} />
            </div>
          )}

          {!loading && !result && !error && (
            <div className="flex flex-col items-center justify-center py-24 gap-3 text-center">
              <p className="text-base font-medium" style={{ color: "#001E2B" }}>
                Enter a query or pick a demo from the sidebar
              </p>
              <p className="text-sm" style={{ color: "#89979B" }}>
                Claude extracts structured filters · Voyage AI embeds semantic intent · MongoDB fuses both
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function LeafIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" fill="#00ED64" />
      <path d="M12 5a1 1 0 00-.92.61L6.15 16.95a.75.75 0 001.38.6L9 14h6l1.47 3.55a.75.75 0 001.38-.6L12.92 5.61A1 1 0 0012 5zm0 3.3 2.34 5.7H9.66L12 8.3z" fill="#001E2B"/>
    </svg>
  );
}
