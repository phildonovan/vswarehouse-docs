# Bulk downloads

Download a whole dataset as a single file (Parquet, gzipped CSV, or GeoParquet) — no per-request row caps, no pagination, no client-side stitching.

The endpoint is `/v1/bulk/{namespace}/{table}` on `api.eolas.fyi`. It's cached behind Cloudflare, so monthly snapshots typically arrive in milliseconds after the first download warms the edge.

---

## The easy path — `client.get()` / `eolas_get()` are now smart

`client.get()` and `eolas_get()` are now smart entry points: they automatically route large or geospatial datasets through the cache+sync path, with no code change needed. The 15-minute `client.get("nz_parcels")` call is now a seconds-fast cached GeoParquet read.

**How the routing works:**

- If you pass any slice argument (`start=`, `end=`, `limit=`) the live API is always used — a whole-file cache cannot serve a filtered subset.
- Otherwise the client calls `info(name)` to check the dataset's `bulk_export_class`, `geometry_type`, and `row_count_at_last_refresh`. Datasets that are bulk-eligible AND (geospatial OR >100k rows) are routed through the cache+sync path.
- Licence-restricted datasets (OECD etc., `bulk_export_class="none"`) always go live regardless of size.

When the client first auto-routes a dataset through the cache path it prints a one-time message explaining what happened:

```
INFO  eolas_data: auto-routing 'nz_parcels' through cache+sync (large/geo dataset).
                  Cache lives at ~/.cache/eolas/. Use mode='live' to override.
```

### Python

```python
from eolas_data import Client

client = Client("your_api_key")

# Smart default: nz_parcels auto-routes to cache+sync — first call downloads
# from CDN, subsequent calls in any session return in <1 s.
gdf = client.get("nz_parcels")          # geopandas.GeoDataFrame
df  = client.get("nz_cpi")             # pd.DataFrame (small → stays live)

# Source-specific helpers inherit smart routing automatically:
gdf = client.linz("nz_parcels")        # also auto-routes
```

**Escape hatches when you need explicit control:**

```python
# Force the live Iceberg scan regardless of dataset size
gdf = client.get("nz_parcels", mode="live")

# Force the cache+sync path explicitly (same as get_local)
gdf = client.get("nz_parcels", mode="cached")

# get_local() is the explicit alias for mode="cached" — useful when you want
# to be unambiguous in a script or when cache_dir / format matter:
gdf = client.get_local("nz_parcels")
gdf = client.get_local("nz_parcels", cache_dir="/data/eolas", freshness="monthly")
```

`format` auto-detects from metadata (geo → geoparquet, else parquet). Cached under `~/.cache/eolas/` by default. Exceptions from the bulk endpoint (`BulkLicenceRestricted`, `BulkUpgradeRequired`, `BulkNotYetAvailable`) propagate unchanged.

### R

```r
library(eolas)
eolas_key("your_key")

# Smart default: auto-routes to cache+sync for large/geo datasets
gdf <- eolas_get("nz_parcels")         # sf object
df  <- eolas_get("nz_cpi")             # data.frame (small → stays live)

# Source-specific helpers inherit smart routing:
gdf <- eolas_get_linz("nz_parcels")   # also auto-routes
```

**Escape hatches:**

```r
# Force live
gdf <- eolas_get("nz_parcels", mode = "live")

# Force cache+sync (same as eolas_get_local)
gdf <- eolas_get("nz_parcels", mode = "cached")

# eolas_get_local() is the explicit alias — useful when cache_dir / format matter:
gdf <- eolas_get_local("nz_parcels")
df  <- eolas_get_local("nz_cpi", cache_dir = "/data/eolas", format = "csv_gz")
```

See the [Python reference](python/reference.md) and [R reference](r/reference.md) for the full parameter list.

---

## When to use bulk vs the live API

| You want… | Use |
|---|---|
| A few hundred or thousand recent rows | `/v1/datasets/{name}/data` (filterable, JSON/CSV/Arrow/Parquet) |
| **The full dataset as one file** | **`/v1/bulk/{ns}/{table}`** (this page) |
| The data joined live into your warehouse | Snowflake share (Enterprise) — see [Authentication](authentication.md) |

The live `/data` endpoint is capped (Free: 50,000 rows/request). For multi-million-row geospatial datasets like LINZ parcels, the bulk endpoint is the right tool — it lazy-generates the snapshot file once and serves it from CDN thereafter.

---

## Tiers

The bulk path has **two axes**: licence (set per dataset, not by you) and freshness (set by your plan).

### Licence axis

Each dataset's licence determines whether bulk is permitted at all:

- **CC-BY-licensed datasets** (the vast majority — Stats NZ, LINZ, RBNZ, MBIE, NZ Treasury, councils, etc.): bulk download permitted, subject to attribution.
- **Non-CC-BY datasets** (notably **OECD**, which we serve under terms that prohibit commercial redistribution): bulk returns **403**. Query the data via the live `/data` endpoint instead.

On the [dataset browse page](https://eolas.fyi/datasets), look for the green **"Bulk download"** badge (eligible) vs the slate **"Query-only (licence)"** badge (restricted).

### Freshness axis

| Plan | Freshness |
|---|---|
| **Free** | Latest **monthly** snapshot (generated 1st of each month at 14:00 UTC). |
| **Pro** | The **current** Iceberg snapshot (generated on first request, served from cache thereafter). |
| **Enterprise** | Same as Pro, plus the Snowflake zero-copy share for direct warehouse access. |

If a Free user requests `?freshness=current`, the response is **402** with a link to /pricing. If a Pro user requests `?freshness=monthly` they get the monthly snapshot (sometimes useful for reproducibility).

---

## Formats

| Format | Query | Best for |
|---|---|---|
| **Parquet** (default) | `?format=parquet` | Pandas, DuckDB, Polars, Spark — fastest read, best compression |
| **gzipped CSV** | `?format=csv_gz` | Excel, anything that doesn't speak Parquet |
| **GeoParquet** | `?format=geoparquet` | QGIS, GeoPandas, DuckDB-spatial — only available on datasets with geometry |

GeoParquet output uses **OGC:CRS84** (WGS84 longitude/latitude) and the GeoParquet 1.0.0 metadata spec — every reader that supports the spec will pick it up natively.

---

## Examples

### curl

```bash
# Pro: current snapshot of NZ Treasury fiscal spending as Parquet
curl -H "X-API-Key: vs_..." \
  -o treasury_fiscal_spending.parquet \
  "https://api.eolas.fyi/v1/bulk/treasury/treasury_fiscal_spending?freshness=current&format=parquet"

# Any plan: latest monthly snapshot as gzipped CSV
curl -H "X-API-Key: vs_..." \
  -o treasury_fiscal_spending.csv.gz \
  "https://api.eolas.fyi/v1/bulk/treasury/treasury_fiscal_spending?freshness=monthly&format=csv_gz"

# GeoParquet for a Stats NZ Geo layer
curl -H "X-API-Key: vs_..." \
  -o ta2023.geo.parquet \
  "https://api.eolas.fyi/v1/bulk/statsnz_geo/territorial_authority_2023?freshness=current&format=geoparquet"
```

If you omit `?freshness=`, the API picks the right one for your plan (Free → monthly, Pro → current) and **302-redirects** to the canonical URL. Curl follows by default with `-L`.

### Python (pandas)

```python
import pandas as pd
import requests

headers = {"X-API-Key": "vs_..."}
url = "https://api.eolas.fyi/v1/bulk/treasury/treasury_fiscal_spending?freshness=current"
# pandas can read remote Parquet directly, but we route through requests
# so the API key header is included.
r = requests.get(url, headers=headers, allow_redirects=True)
r.raise_for_status()
df = pd.read_parquet(io.BytesIO(r.content))
print(df.shape, df.columns.tolist())
```

### Python (GeoPandas — for geo datasets)

```python
import io
import geopandas as gpd
import requests

headers = {"X-API-Key": "vs_..."}
url = ("https://api.eolas.fyi/v1/bulk/statsnz_geo/territorial_authority_2023"
       "?freshness=current&format=geoparquet")
r = requests.get(url, headers=headers, allow_redirects=True)
r.raise_for_status()
gdf = gpd.read_parquet(io.BytesIO(r.content))
print(gdf.crs)         # OGC:CRS84 (WGS84 lon/lat)
print(gdf.geometry.iloc[0].geom_type)
```

### DuckDB (read Parquet directly via HTTP)

```sql
-- DuckDB can read remote Parquet without downloading first, but it can't
-- send a custom header. Easiest: download with curl, then query the local file.
INSTALL httpfs; LOAD httpfs;
SELECT count(*) FROM read_parquet('treasury_fiscal_spending.parquet');
```

### Browser

On any [dataset page](https://eolas.fyi/datasets), if you're logged in, click the **Parquet** / **CSV.gz** / **GeoParquet** download buttons in the header. Same gate as the API — Free gets the monthly snapshot, Pro gets the current.

---

## Keeping a downloaded file in sync

After the first download, call `sync_bulk` / `eolas_sync_bulk` / `eolas sync` instead of `download_bulk` on subsequent runs. A HEAD request (~200 bytes) checks the server's `X-Snapshot-Version` header; if the local sidecar records the same snapshot, no data is transferred.

### Python

```python
from eolas_data import Client

client = Client("your_api_key")

r = client.sync_bulk("nz_cpi", path="nz_cpi.parquet")
# r.status is "downloaded" (first run), "updated" (new snapshot), or "unchanged"
# r.bytes_downloaded is 0 when unchanged
print(r.status, r.current_snapshot_id)
```

### R

```r
library(eolas)
eolas_key("your_key")

r <- eolas_sync_bulk("nz_cpi", path = "nz_cpi.parquet")
# r$status: "downloaded" | "updated" | "unchanged"
# r$bytes_downloaded: 0 when unchanged
message(r$status, " — snapshot: ", r$current_snapshot_id)
```

### CLI (one-shot or watch loop)

```bash
# Single check
eolas sync nz_cpi --out ~/data/nz_cpi.parquet

# Foreground loop — polls every hour, exits on Ctrl-C
eolas sync nz_cpi --watch hourly --out ~/data/nz_cpi.parquet
```

The sidecar `<path>.eolas-meta.json` (written automatically) contains the snapshot id, download timestamp, format, and source URL. It is safe to delete — the next call will treat it as a first download. See the [Python reference](python/reference.md) and [R reference](r/reference.md) pages for the full `sync_bulk` API.

---

## What you get in the download

Every bulk file is named `{namespace}__{table}@{snapshot_id}.{ext}`. The snapshot id is the Iceberg snapshot the file was generated from — files are immutable by name, so a new refresh of the source data produces a new URL (CDN cache invalidates itself).

Each bulk download also includes:

1. **A `NOTICE.txt` sidecar** in the eolas-bulk S3 bucket (also retrievable at `{namespace}/{namespace}__{table}@{snapshot_id}.NOTICE.txt`). Contains the source, licence, source URL, snapshot version, "data as of" date, and the attribution clause.
2. **File-level metadata** embedded in the Parquet/GeoParquet (key-value `geo` block for GeoParquet, standard Parquet metadata for the rest).

The `NOTICE` file **must travel with the data** if you redistribute it — that's how the CC-BY attribution obligation is satisfied. See [Terms §5](https://eolas.fyi/terms#bulk).

---

## Caching, freshness, and refresh

- **Monthly snapshots** are pre-generated on the 1st of each month at 14:00 UTC by a server-side cron.
- **Current snapshots** for Pro are lazy-generated on first request and cached at S3 forever (well — for 180 days, per the bucket lifecycle policy).
- **Cloudflare** caches monthly URLs at the edge with `Cache-Control: public, max-age=31536000, immutable`. URLs include the snapshot id, so a new refresh → new URL → automatic CDN invalidation. **No manual cache busting needed.**
- **`X-Snapshot-Version`** response header tells you which Iceberg snapshot you got. Pin it in scripts if you need reproducibility.

---

## Rate limits

| Layer | Limit |
|---|---|
| App-level monthly quota | Free: 10 req/month total (bulk counts). Pro/Enterprise: unlimited. |
| Per-IP at the edge | 5 req per 10 s (Cloudflare zone rule). Bursty downloads get a 10 s 429; spread requests if scripting. |

If you're systematically pulling many datasets, space requests by ~2 s and you'll never trip the per-IP rule.

---

## Redistribution

You may redistribute bulk-downloaded files — including in commercial work and on paid platforms — **provided the `NOTICE.txt` sidecar continues to travel with the data**. Removing or altering it breaches the upstream CC-BY licence (not just our terms).

OECD and other non-CC-BY datasets are excluded from bulk; do not attempt to reconstruct them via repeated `/v1/data` calls — that's a breach of our [acceptable use](https://eolas.fyi/terms) and the upstream licence.

Full terms: [eolas.fyi/terms §5](https://eolas.fyi/terms#bulk).
