import { Product } from "@/lib/api";

const NUTRISCORE_COLORS: Record<string, { bg: string; text: string }> = {
  a: { bg: "#038141", text: "white" },
  b: { bg: "#85BB2F", text: "white" },
  c: { bg: "#FECB02", text: "#001E2B" },
  d: { bg: "#EE8100", text: "white" },
  e: { bg: "#E63312", text: "white" },
};

const DROVE_COLORS: Record<string, { bg: string; text: string }> = {
  Both:    { bg: "#00ED6415", text: "#00a847" },
  Text:    { bg: "#3B82F615", text: "#2563EB" },
  Vector:  { bg: "#8B5CF615", text: "#7C3AED" },
  Unknown: { bg: "#89979B20", text: "#89979B" },
};

function NutriScore({ grade }: { grade: string }) {
  const g = grade?.toLowerCase();
  const color = NUTRISCORE_COLORS[g] || { bg: "#89979B20", text: "#89979B" };
  const valid = ["a","b","c","d","e"].includes(g);
  return (
    <span className="text-sm font-bold px-3 py-1 rounded-md" style={{ background: color.bg, color: color.text }}>
      {valid ? `Nutri-Score ${grade.toUpperCase()}` : "No score"}
    </span>
  );
}

function DroveBadge({ drove }: { drove: string }) {
  const color = DROVE_COLORS[drove] || DROVE_COLORS.Unknown;
  const label = drove === "Both" ? "⚡ Both" : drove === "Text" ? "🔤 Text" : drove === "Vector" ? "🔮 Vector" : drove;
  return (
    <span className="text-sm font-semibold px-3 py-1 rounded-full" style={{ background: color.bg, color: color.text }}>
      {label}
    </span>
  );
}

function ProductCard({ product }: { product: Product }) {
  const cats = product.categories_tags?.slice(-2).map(t => t.replace("en:", "").replace(/-/g, " ")) ?? [];

  return (
    <div
      className="bg-white rounded-2xl overflow-hidden flex flex-col transition-all duration-150 hover:-translate-y-1 hover:shadow-lg"
      style={{ boxShadow: "0 1px 4px rgba(0,30,43,0.08)", border: "1px solid rgba(0,30,43,0.07)" }}
    >
      {/* Image */}
      <div className="h-48 flex items-center justify-center" style={{ background: "#F5F8F9" }}>
        {product.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={product.image_url} alt={product.product_name} className="h-40 w-auto object-contain p-2" />
        ) : (
          <div className="w-20 h-20 rounded-full flex items-center justify-center text-4xl" style={{ background: "#E8EDEE" }}>🛒</div>
        )}
      </div>

      {/* Body */}
      <div className="p-5 flex flex-col gap-3 flex-1">
        <div>
          <h3 className="font-semibold text-base leading-snug line-clamp-2" style={{ color: "#001E2B" }}>
            {product.product_name}
          </h3>
          {product.brands && (
            <p className="text-sm mt-1" style={{ color: "#89979B" }}>{product.brands}</p>
          )}
          {cats.length > 0 && (
            <p className="text-sm mt-0.5 capitalize" style={{ color: "#89979B" }}>{cats.join(" · ")}</p>
          )}
        </div>

        <NutriScore grade={product.nutriscore_grade} />

        {(product.energy_kcal_100g != null || product.proteins_100g != null || product.sodium_100g != null) && (
          <div className="flex flex-wrap gap-3 text-sm" style={{ color: "#89979B" }}>
            {product.energy_kcal_100g != null && <span>{Math.round(product.energy_kcal_100g)} kcal</span>}
            {product.proteins_100g != null && <span>{product.proteins_100g}g protein</span>}
            {product.sodium_100g != null && <span>{Math.round(product.sodium_100g * 1000)}mg Na</span>}
          </div>
        )}

        <div className="mt-auto pt-3 flex items-center justify-between border-t" style={{ borderColor: "#F0F4F5" }}>
          <DroveBadge drove={product.drove_by} />
          <span className="text-sm font-mono" style={{ color: "#89979B" }}>{product.score.toFixed(4)}</span>
        </div>
      </div>
    </div>
  );
}

export function ProductGrid({ results }: { results: Product[] }) {
  if (results.length === 0) {
    return <div className="text-center py-16 text-base" style={{ color: "#89979B" }}>No products found — try broader terms</div>;
  }

  return (
    <div>
      <p className="text-sm font-medium mb-5" style={{ color: "#89979B" }}>{results.length} results</p>
      <div className="grid grid-cols-2 gap-5 lg:grid-cols-3 xl:grid-cols-4">
        {results.map((p, i) => <ProductCard key={i} product={p} />)}
      </div>
    </div>
  );
}
