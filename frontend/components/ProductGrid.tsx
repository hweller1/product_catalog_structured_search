import { Product } from "@/lib/api";

const NUTRISCORE_COLORS: Record<string, { bg: string; text: string }> = {
  a: { bg: "#038141", text: "white" },
  b: { bg: "#85BB2F", text: "white" },
  c: { bg: "#FECB02", text: "#001E2B" },
  d: { bg: "#EE8100", text: "white" },
  e: { bg: "#E63312", text: "white" },
};

const DROVE_COLORS: Record<string, { bg: string; text: string }> = {
  Both:   { bg: "#00ED6420", text: "#00ED64" },
  Text:   { bg: "#3B82F620", text: "#3B82F6" },
  Vector: { bg: "#8B5CF620", text: "#8B5CF6" },
  Unknown:{ bg: "#89979B20", text: "#89979B" },
};

function NutriScore({ grade }: { grade: string }) {
  const g = grade?.toLowerCase();
  const color = NUTRISCORE_COLORS[g] || { bg: "#89979B30", text: "#89979B" };
  return (
    <span
      className="text-xs font-bold px-2 py-0.5 rounded"
      style={{ background: color.bg, color: color.text }}
    >
      {g && ["a","b","c","d","e"].includes(g) ? `Nutri-Score ${grade.toUpperCase()}` : "No score"}
    </span>
  );
}

function DroveBadge({ drove }: { drove: string }) {
  const color = DROVE_COLORS[drove] || DROVE_COLORS.Unknown;
  return (
    <span
      className="text-xs font-medium px-2 py-0.5 rounded-full"
      style={{ background: color.bg, color: color.text }}
    >
      {drove === "Both" ? "⚡ Both pipelines" : drove === "Text" ? "🔤 Text pipeline" : drove === "Vector" ? "🔮 Vector pipeline" : drove}
    </span>
  );
}

function ProductCard({ product }: { product: Product }) {
  const cats = product.categories_tags?.slice(-2).map(t => t.replace("en:", "").replace(/-/g, " ")) || [];

  return (
    <div
      className="bg-white rounded-2xl overflow-hidden flex flex-col transition-all duration-200 hover:-translate-y-0.5"
      style={{ boxShadow: "0 1px 3px rgba(0,30,43,0.08), 0 1px 2px rgba(0,30,43,0.06)", border: "1px solid rgba(0,30,43,0.06)" }}
    >
      {/* Image area */}
      <div className="h-40 flex items-center justify-center" style={{ background: "#F0F4F5" }}>
        {product.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={product.image_url} alt={product.product_name} className="h-36 w-auto object-contain" />
        ) : (
          <div className="w-16 h-16 rounded-full flex items-center justify-center text-2xl" style={{ background: "#E8EDEE" }}>
            🛒
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col gap-2 flex-1">
        <div>
          <h3 className="font-semibold text-sm leading-tight line-clamp-2" style={{ color: "#001E2B" }}>
            {product.product_name}
          </h3>
          {product.brands && (
            <p className="text-xs mt-0.5" style={{ color: "#89979B" }}>{product.brands}</p>
          )}
        </div>

        {cats.length > 0 && (
          <p className="text-xs capitalize" style={{ color: "#89979B" }}>
            {cats.join(" · ")}
          </p>
        )}

        <div className="flex flex-wrap gap-1.5 mt-auto pt-2">
          <NutriScore grade={product.nutriscore_grade} />
        </div>

        <div className="flex items-center justify-between pt-1 border-t" style={{ borderColor: "#F0F4F5" }}>
          <DroveBadge drove={product.drove_by} />
          <span className="text-xs font-mono" style={{ color: "#89979B" }}>
            {product.score.toFixed(4)}
          </span>
        </div>

        {/* Nutrition row */}
        {(product.sodium_100g != null || product.proteins_100g != null || product.energy_kcal_100g != null) && (
          <div className="flex gap-3 text-xs" style={{ color: "#89979B" }}>
            {product.energy_kcal_100g != null && <span>{Math.round(product.energy_kcal_100g)} kcal</span>}
            {product.proteins_100g != null && <span>{product.proteins_100g}g protein</span>}
            {product.sodium_100g != null && <span>{Math.round(product.sodium_100g * 1000)}mg sodium</span>}
          </div>
        )}
      </div>
    </div>
  );
}

export function ProductGrid({ results }: { results: Product[] }) {
  if (results.length === 0) {
    return (
      <div className="text-center py-16 text-sm" style={{ color: "#89979B" }}>
        No products found — try broader terms
      </div>
    );
  }

  return (
    <div>
      <p className="text-xs mb-4 font-medium" style={{ color: "#89979B" }}>
        {results.length} results
      </p>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-4">
        {results.map((p, i) => (
          <ProductCard key={i} product={p} />
        ))}
      </div>
    </div>
  );
}
