export interface Product {
  product_name: string;
  brands: string;
  nutriscore_grade: string;
  nova_group: number | null;
  categories_tags: string[];
  labels_tags: string[];
  sodium_100g: number | null;
  proteins_100g: number | null;
  sugars_100g: number | null;
  energy_kcal_100g: number | null;
  image_url: string | null;
  score: number;
  drove_by: "Text" | "Vector" | "Both" | "Unknown";
  text_rank: string | number;
  vector_rank: string | number;
}

export interface SearchResponse {
  results: Product[];
  search_stage: Record<string, unknown>;
  pipeline: Record<string, unknown>[];
  reason: string;
  constraints: string[];
  query: string;
}

export async function runSearch(
  query: string,
  textWeight: number,
  vectorWeight: number,
  topK: number
): Promise<SearchResponse> {
  const res = await fetch("http://localhost:8000/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      text_weight: textWeight,
      vector_weight: vectorWeight,
      top_k: topK,
    }),
  });
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}
