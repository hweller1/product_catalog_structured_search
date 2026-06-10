# MongoDB Structured Search Demo

A Streamlit app demonstrating hybrid search over Open Food Facts data using MongoDB Atlas `$rankFusion`, Voyage AI embeddings, and Claude-generated `$search` queries.

## Prerequisites

- Python >= 3.10
- MongoDB Atlas cluster: M10+ tier running MongoDB 8.0+
- API key for Anthropic — model: `claude-haiku-4-5`
- API key for Voyage AI — model: `voyage-4`

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```
MONGODB_URI=<your Atlas connection string>
ANTHROPIC_API_KEY=<your Anthropic key>
VOYAGE_API_KEY=<your Voyage AI key>
```

### 3. Load data and create indexes

```bash
python scripts/load_data.py
```

This script:
- Downloads the Open Food Facts dataset (~7 GB)
- Embeds 1 000 products using Voyage AI (`voyage-4`)
- Loads the documents into MongoDB Atlas
- Creates both the Atlas Search index and the Vector Search index

**Expected runtime: ~15 minutes.**

## How it works

Every query runs through two parallel pipelines fused by MongoDB's `$rankFusion`:

```
User query: "kosher low sodium soup"
       │
       ├─► Claude (claude-haiku-4-5)
       │       Reads the schema, translates NL → structured $search stage:
       │         • Label: Kosher          ← equals filter on labels_tags
       │         • Sodium ≤ 120mg         ← range filter on sodium_100g
       │         • Keyword: "soup"        ← text search on product_name
       │       This is the TEXT PIPELINE — exact/structured matching.
       │
       └─► Voyage AI (voyage-4)
               Embeds the full query as a 1024-dim vector.
               Runs $vectorSearch for semantic similarity.
               This is the VECTOR PIPELINE — intent matching.

Both pipelines feed into $rankFusion (MongoDB 8.0+), which merges
the ranked results using Reciprocal Rank Fusion (RRF) with configurable weights.
```

After each search the app shows a **Query Routing** panel that makes this visible:
- **Left column**: what Claude extracted and mapped to specific schema fields
- **Right column**: that Voyage AI ran semantic similarity for the full query
- **"Drove by" badge** on each card: whether Text, Vector, or Both pipelines surfaced it

The **Under the Hood** expander shows the raw `$search` JSON Claude generated,
per-pipeline RRF ranks, and the full `$rankFusion` aggregation pipeline.

## Running the App

```bash
streamlit run app.py
```

Open the URL printed in the terminal (default: `http://localhost:8501`).

## Demo Guide

### Demo Queries

Eight pre-built queries showcase different search capabilities:

| # | Query | Feature demonstrated |
|---|-------|----------------------|
| 1 | `kosher low sodium soup` | Label filter + nutrition range via `$search` |
| 2 | `organic whole grain cereal kids` | Semantic intent via Vector Search |
| 3 | `vegan protein bar chocolate` | Hybrid: lexical brand + semantic flavor |
| 4 | `gluten free pasta high protein` | Claims filter + nutrition constraint |
| 5 | `keto friendly snack low carb` | Pure semantic (no `keto` field in schema) |
| 6 | `Nutri-Score A dairy product` | Token exact match on `nutriscore_grade` |
| 7 | `Clif bar flavors` | Brand lexical match via `$search` text pipeline |
| 8 | `high fiber breakfast food low sugar` | Multi-constraint nutrition hybrid |

### Weight Sliders

Two sliders adjust the relative influence of each pipeline inside `$rankFusion`:

- **Text Weight** — controls the `$search` (lexical/structured) pipeline. Higher = stronger influence from keyword, filter, and range matches.
- **Vector Weight** — controls the Vector Search pipeline. Higher = stronger influence from semantic similarity.

Both sliders range from 0 to 2. Setting a weight to 0 disables that pipeline entirely, enabling pure lexical or pure semantic mode.

### Under the Hood Tabs

After running a query, three tabs expose the internals:

- **Generated `$search` Query** — the structured query Claude (`claude-haiku-4-5`) produced from your free-text input.
- **Score Breakdown** — Reciprocal Rank Fusion (RRF) ranks for each result. These are rank-based positions (lower = better match), not similarity percentages.
- **Raw Pipeline** — the complete `$rankFusion` aggregation sent to MongoDB Atlas, including both sub-pipelines and their weights.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Atlas connection failed` | Verify `MONGODB_URI` in `.env`. The cluster must be M10+ tier. |
| `Search index still building` | Wait ~1 minute after `load_data.py` finishes, then reload the app. |
| `Embedding failed` | Verify `VOYAGE_API_KEY` in `.env` and that the key has active quota. |
