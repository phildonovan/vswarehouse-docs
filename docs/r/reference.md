# R API reference

## Authentication

### `eolas_key(key)`

Store an API key for the duration of the R session.

```r
eolas_key("vs_your_key")
```

**Arguments**

| Name | Type | Description |
|---|---|---|
| `key` | character | A `vs_...` API key |

**Returns:** The key, invisibly.  
**Note:** If `EOLAS_API_KEY` is set in the environment, or the key has been saved via `eolas_key_save()`, you can skip this call entirely.

---

### `eolas_key_save(key = NULL)`

Save the API key to the OS keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service). Once saved, all `eolas_get_*()` calls find the key automatically in every future R session.

The keyring slot (`service = "eolas"`, `username = "api-key"`) is shared with the Python `eolas-data` client, so a key saved from R is immediately visible in Python and vice versa.

Requires the `keyring` package. On Linux, `libsecret-1-dev` system headers must be installed before `install.packages("keyring")`.

```r
install.packages("keyring")   # one-off install

eolas_key_save()              # interactive masked prompt
eolas_key_save("vs_...")      # non-interactive

# After saving, no explicit key call needed:
library(eolas)
df <- eolas_get("nz_cpi")    # key read from OS keyring automatically
```

**Arguments**

| Name | Type | Default | Description |
|---|---|---|---|
| `key` | character \| NULL | `NULL` | The API key to save. `NULL` triggers an interactive prompt. |

**Returns:** Invisibly `NULL`.

---

### `eolas_key_clear()`

Remove the eolas API key from the OS keyring. Does not affect the `EOLAS_API_KEY` environment variable or any in-session key set by `eolas_key()`.

```r
eolas_key_clear()
```

**Returns:** Invisibly `NULL`.

---

### `eolas_key_status()`

Show which source is supplying the eolas API key (in-session, env var, OS keyring, or none) and print the key masked to the first eight characters.

```r
eolas_key_status()
# key:    vs_abcdef…
# source: OS keyring (service = "eolas")
```

**Returns:** Character string describing the source, invisibly (`"session"`, `"env"`, `"keyring"`, or `"none"`). Called primarily for its printed output.

---

## Discovery

### `eolas_list(source = NULL)`

Return metadata for all available series.

```r
eolas_list()              # all series
eolas_list("Stats NZ")   # Stats NZ only
```

**Arguments**

| Name | Type | Default | Description |
|---|---|---|---|
| `source` | character \| NULL | `NULL` | Filter by source label, e.g. `"Stats NZ"`, `"OECD"`. |

**Returns:** tibble (if `tibble` is installed) or `data.frame` with columns `name`, `title`, `source`, `namespace`, `description`.

---

### Source-specific list helpers

Convenience wrappers over `eolas_list(source = ...)`.

| Function | Equivalent |
|---|---|
| `eolas_list_statsnz()` | `eolas_list("Stats NZ")` |
| `eolas_list_oecd()` | `eolas_list("OECD")` |
| `eolas_list_rbnz()` | `eolas_list("RBNZ")` |
| `eolas_list_treasury()` | `eolas_list("NZ Treasury")` |
| `eolas_list_linz()` | `eolas_list("LINZ")` |
| `eolas_list_statsnz_geo()` | `eolas_list("Stats NZ Geospatial")` |
| `eolas_list_mbie()` | `eolas_list("MBIE")` |
| `eolas_list_nzta()` | `eolas_list("Waka Kotahi")` |
| `eolas_list_msd()` | `eolas_list("MSD")` |
| `eolas_list_police()` | `eolas_list("NZ Police / MoJ")` |
| `eolas_list_immigration()` | `eolas_list("Immigration NZ")` |
| `eolas_list_lris()` | `eolas_list("Manaaki Whenua / LRIS")` |
| `eolas_list_geonet()` | `eolas_list("GeoNet")` |
| `eolas_list_doc()` | `eolas_list("DOC")` |
| `eolas_list_akl_council()` | `eolas_list("Auckland Council")` |
| `eolas_list_akl_transport()` | `eolas_list("Auckland Transport")` |
| `eolas_list_bay_of_plenty()` | `eolas_list("Bay of Plenty Councils")` |
| `eolas_list_charities()` | `eolas_list("Charities Services")` |
| `eolas_list_colab_waikato()` | `eolas_list("Co-Lab Waikato")` |
| `eolas_list_ecan_canterbury()` | `eolas_list("ECan / Canterbury")` |
| `eolas_list_eeca()` | `eolas_list("EECA")` |
| `eolas_list_hawkes_bay()` | `eolas_list("Hawke's Bay Councils")` |
| `eolas_list_manawatu_whanganui()` | `eolas_list("Manawatū-Whanganui Councils")` |
| `eolas_list_napier_whanganui()` | `eolas_list("Napier + Whanganui")` |
| `eolas_list_northland()` | `eolas_list("Northland Councils")` |
| `eolas_list_otago()` | `eolas_list("Otago Councils")` |
| `eolas_list_pharmac()` | `eolas_list("PHARMAC")` |
| `eolas_list_southland()` | `eolas_list("Southland Councils")` |
| `eolas_list_taranaki()` | `eolas_list("Taranaki Councils")` |
| `eolas_list_top_of_south()` | `eolas_list("Gisborne / Top of South Councils")` |
| `eolas_list_wellington()` | `eolas_list("Wellington Region Councils")` |
| `eolas_list_west_coast()` | `eolas_list("West Coast (Te Tai o Poutini)")` |

---

### `eolas_info(name)`

Return metadata for a single series.

```r
meta <- eolas_info("nz_cpi")
meta$title   # "NZ Consumer Price Index"
meta$source  # "Stats NZ"
```

**Arguments**

| Name | Type | Description |
|---|---|---|
| `name` | character | Series identifier, e.g. `"nz_cpi"` |

**Returns:** Named `list`.  
**Errors:** Stops with `"Not found: ..."` if the series does not exist.

---

## Fetching data

### `eolas_get(name, start = NULL, end = NULL, limit = NULL, as_sf = NULL, as_arrow = FALSE, mode = "auto")`

Generic workhorse. For everyday use prefer the source-specific helpers below — they call `eolas_get()` internally and inherit smart routing.

`eolas_get()` is now a **smart entry point**: in `mode = "auto"` (the default) it inspects the dataset's metadata and automatically routes large or geospatial datasets through the cache+sync path. See [Bulk downloads](../bulk-downloads.md) for the full routing rules.

```r
# Smart default: nz_parcels auto-routes to cache+sync (~seconds after first call)
gdf <- eolas_get("nz_parcels")

# Small dataset stays on the live path; slice args always force live:
df  <- eolas_get("nz_cpi", start = "2020-01-01", end = "2024-12-31")
df  <- eolas_get("nz_addresses", limit = 1000)

# Force live even for large datasets
gdf <- eolas_get("nz_parcels", mode = "live")

# Force cache+sync explicitly (same as eolas_get_local)
gdf <- eolas_get("nz_parcels", mode = "cached")
```

**Arguments**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | character | — | Dataset identifier |
| `start` | character \| NULL | `NULL` | ISO date lower bound, e.g. `"2020-01-01"`. Forces live path in `mode = "auto"`. |
| `end` | character \| NULL | `NULL` | ISO date upper bound. Forces live path in `mode = "auto"`. |
| `limit` | integer \| NULL | `NULL` | Max rows. `NULL` requests the full dataset. Free plan is capped server-side at 50,000 rows; Pro is unlimited. Forces live path in `mode = "auto"`. |
| `as_sf` | logical \| NULL | `NULL` | Return an `sf` object for geospatial datasets. `NULL` auto-converts when geometry is present and the `sf` package is installed. `TRUE` forces conversion (errors if missing). `FALSE` keeps the raw `geometry_wkt` string column. Install with `install.packages("sf")`. Mutually exclusive with `as_arrow = TRUE`. |
| `as_arrow` | logical | `FALSE` | Return an `arrow::Table` instead of a data frame or `sf` object. Skips all geometry materialisation — geometry stays as character WKT. Works on all datasets, all routing modes, and all `eolas_get_*()` source helpers. Mutually exclusive with `as_sf = TRUE`. |
| `mode` | character | `"auto"` | `"auto"` — smart-routes via metadata (see above). `"live"` — hit the live API directly; useful for freshest data, OECD-restricted sources, or sliced queries (e.g. with `limit`/`start`/`end`). The server returns **413** if the dataset is large (>100 k rows) or has geometry and no filter is set — use `"cached"` for whole-dataset pulls. `"cached"` — always use cache+sync (equivalent to `eolas_get_local()`). |

**Returns:** `eolas_dataset` data frame, `sf` object when geometry is present and conversion is enabled, `arrow::Table` when `as_arrow = TRUE`, or the return value of `eolas_get_local()` when routed through the cache path.

#### Performance: Arrow & Parquet

The API serves datasets in four formats via `?format=` — `json` (default), `csv`, `arrow` (Apache Arrow IPC stream), and `parquet`. Arrow and Parquet are columnar and typed, so they're dramatically faster for anything beyond a few hundred rows. Measured end-to-end on a 100,000-row × 71-column dataset:

| Format | Wire size | Total (download + parse) |
|---|---|---|
| JSON | 165 MB | 39.5 s |
| **Arrow** | 66 MB | **7.7 s** (5× faster; ~80× faster parse) |
| **Parquet** | 6.3 MB | **4.3 s** (9× faster; 26× smaller) |

`eolas_get()` uses Arrow **automatically** when the `arrow` package is installed — `eolas_get("nz_cpi")` returns the same data frame, just much faster on large pulls, with a transparent JSON fallback. `arrow` is a *suggested* dependency, so install it once to switch the transport on (without it you get a one-time hint and JSON transport):

```r
install.packages("arrow")   # one-off; no code change needed
```

Hitting the REST API directly for a Parquet file:

```bash
curl -H "X-API-Key: $EOLAS_API_KEY" \
  "https://api.eolas.fyi/v1/datasets/nzta_cas_crashes/data?format=parquet&limit=100000" \
  -o crashes.parquet
```

---

### Source-specific get helpers

Each is a named wrapper over `eolas_get()` that tags the result with the source label.

| Function | Source |
|---|---|
| `eolas_get_statsnz(name, start, end, limit, as_sf, as_arrow)` | Stats NZ |
| `eolas_get_oecd(name, start, end, limit, as_sf, as_arrow)` | OECD |
| `eolas_get_rbnz(name, start, end, limit, as_sf, as_arrow)` | RBNZ |
| `eolas_get_treasury(name, start, end, limit, as_sf, as_arrow)` | NZ Treasury |
| `eolas_get_linz(name, start, end, limit, as_sf, as_arrow)` | LINZ |
| `eolas_get_statsnz_geo(name, start, end, limit, as_sf, as_arrow)` | Stats NZ Geospatial |
| `eolas_get_mbie(name, start, end, limit, as_sf, as_arrow)` | MBIE |
| `eolas_get_nzta(name, start, end, limit, as_sf, as_arrow)` | Waka Kotahi (NZTA) |
| `eolas_get_msd(name, start, end, limit, as_sf, as_arrow)` | MSD |
| `eolas_get_police(name, start, end, limit, as_sf, as_arrow)` | NZ Police / MoJ |
| `eolas_get_immigration(name, start, end, limit, as_sf, as_arrow)` | Immigration NZ |
| `eolas_get_lris(name, start, end, limit, as_sf, as_arrow)` | Manaaki Whenua / LRIS |
| `eolas_get_geonet(name, start, end, limit, as_sf, as_arrow)` | GeoNet |
| `eolas_get_doc(name, start, end, limit, as_sf, as_arrow)` | DOC (Department of Conservation) |
| `eolas_get_akl_council(name, start, end, limit, as_sf, as_arrow)` | Auckland Council |
| `eolas_get_akl_transport(name, start, end, limit, as_sf, as_arrow)` | Auckland Transport |
| `eolas_get_bay_of_plenty(name, start, end, limit, as_sf, as_arrow)` | Bay of Plenty Councils |
| `eolas_get_charities(name, start, end, limit, as_sf, as_arrow)` | Charities Services |
| `eolas_get_colab_waikato(name, start, end, limit, as_sf, as_arrow)` | Co-Lab Waikato |
| `eolas_get_ecan_canterbury(name, start, end, limit, as_sf, as_arrow)` | ECan / Canterbury |
| `eolas_get_eeca(name, start, end, limit, as_sf, as_arrow)` | EECA (energy use, EV chargers, regional heat demand) |
| `eolas_get_hawkes_bay(name, start, end, limit, as_sf, as_arrow)` | Hawke's Bay Councils |
| `eolas_get_manawatu_whanganui(name, start, end, limit, as_sf, as_arrow)` | Manawatū-Whanganui Councils |
| `eolas_get_napier_whanganui(name, start, end, limit, as_sf, as_arrow)` | Napier + Whanganui |
| `eolas_get_northland(name, start, end, limit, as_sf, as_arrow)` | Northland Councils |
| `eolas_get_otago(name, start, end, limit, as_sf, as_arrow)` | Otago Councils |
| `eolas_get_pharmac(name, start, end, limit, as_sf, as_arrow)` | PHARMAC |
| `eolas_get_southland(name, start, end, limit, as_sf, as_arrow)` | Southland Councils |
| `eolas_get_taranaki(name, start, end, limit, as_sf, as_arrow)` | Taranaki Councils |
| `eolas_get_top_of_south(name, start, end, limit, as_sf, as_arrow)` | Gisborne / Top of South Councils |
| `eolas_get_wellington(name, start, end, limit, as_sf, as_arrow)` | Wellington Region Councils |
| `eolas_get_west_coast(name, start, end, limit, as_sf, as_arrow)` | West Coast (Te Tai o Poutini) |

```r
df <- eolas_get_statsnz("nz_cpi", start = "2015-01-01")
attr(df, "eolas_source")   # "Stats NZ"
```

---

### `eolas_sync(name, library_dir)`

Incrementally sync a dataset into a local library directory. On the first call, downloads the full snapshot. On subsequent calls, fetches only the rows appended since the last sync and adds them as a delta file. Returns immediately (no download) when the server snapshot is unchanged.

The dataset is stored as a directory of Parquet files plus `_eolas-manifest.json`. Any Parquet-aware tool (`arrow::open_dataset`, DuckDB, polars, dbt) can read the whole directory as one logical table.

See the [Sync guide](../sync-guide.md) for the full conceptual walkthrough, cron and Airflow recipes, and comparison vs Fivetran/Stitch.

```r
library(eolas)
eolas_key("your_eolas_key")

LIBRARY <- "/data/nz-warehouse"

# First sync — full download
result <- eolas_sync("nz_parcels", library_dir = LIBRARY)
result$status           # "snapshot_full"
result$bytes_downloaded # e.g. 1650000000

# Re-sync — only delta rows
result <- eolas_sync("nz_parcels", library_dir = LIBRARY)
result$status     # "unchanged" or "snapshot_delta"
result$rows_added # 0 or e.g. 2847
```

**Arguments**

| Name | Type | Description |
|---|---|---|
| `name` | character | Dataset identifier, e.g. `"nz_parcels"` |
| `library_dir` | character | Root directory of your local dataset library. The dataset is written to `<library_dir>/<name>/`. |

**Returns:** Named list with the fields of `SyncResult` (see below).

---

### `eolas_sync_all(library_dir, datasets = NULL)`

Sync multiple datasets. When `datasets` is `NULL`, syncs every dataset already registered in the library (by manifest). Datasets are synced concurrently.

```r
# Explicit list
results <- eolas_sync_all(
  library_dir = "/data/nz-warehouse",
  datasets = c("nz_parcels", "nz_addresses", "nz_property_titles")
)
lapply(results, function(r) cat(r$status, "+", r$rows_added, "rows\n"))

# Everything in the library
results <- eolas_sync_all(library_dir = "/data/nz-warehouse")
```

**Arguments**

| Name | Type | Default | Description |
|---|---|---|---|
| `library_dir` | character | — | Root library directory |
| `datasets` | character \| NULL | `NULL` | Dataset names to sync. `NULL` syncs all datasets with existing manifests. |

**Returns:** Named list of sync result lists, one per dataset.

---

### `eolas_compact(path)`

Merge all snapshot and delta files in a dataset directory into a single new snapshot file, then remove the old files. The manifest is updated atomically. Safe to run at any time.

Pass a single dataset directory or the library root (compacts all datasets with deltas).

```r
# Single dataset
eolas_compact("/data/nz-warehouse/nz_parcels")

# Entire library
eolas_compact("/data/nz-warehouse")
```

**Arguments**

| Name | Type | Description |
|---|---|---|
| `path` | character | Path to a dataset directory OR the library root. |

**Returns:** Named list with `files_removed`, `bytes_saved`, `new_snapshot_file`.

---

### `SyncResult` fields (R)

All sync functions return a named list with these fields:

| Name | Type | Description |
|---|---|---|
| `status` | character | `"unchanged"` — no data transferred. `"snapshot_full"` — full dataset downloaded. `"snapshot_delta"` — delta rows appended. |
| `bytes_downloaded` | integer | Bytes written to disk (`0L` when unchanged) |
| `rows_added` | integer | Rows written in this sync (`0L` when unchanged) |
| `files_added` | integer | New Parquet files created (`0L` when unchanged) |
| `current_snapshot_id` | character | Snapshot ID now recorded in the manifest |
| `dataset` | character | Dataset name |

---

### `eolas_get()` — library-aware smart routing

When `library_dir` is configured (via `eolas_library_set()` or the `EOLAS_LIBRARY` env var) and a manifest exists for the requested dataset, `eolas_get()` and the source-specific helpers (`eolas_get_linz()`, etc.) automatically read from the local library files using `arrow::open_dataset()` — zero network traffic.

```r
# After syncing nz_parcels into /data/nz-warehouse:
eolas_library_set("/data/nz-warehouse")

gdf <- eolas_get_linz("nz_parcels")   # reads from /data/nz-warehouse/nz_parcels/ — no download
df  <- eolas_get("nz_cpi")            # small dataset, still goes live (no manifest)
```

The `_eolas-manifest.json` format is shared with the Python client — a library synced from Python can be read in R and vice versa.

---

### `eolas_download_bulk(name, freshness = "auto", format = "parquet", path = NULL, progress = NULL, ...)`

Download a complete dataset as a single binary file via the `/v1/bulk/{namespace}/{table}` endpoint. Monthly snapshots are served from Cloudflare's edge cache; Pro current snapshots are lazy-generated on first request.

See [Bulk downloads](../bulk-downloads.md) for the full narrative, tier comparison, and worked examples.

```r
# Return a raw vector
raw <- eolas_download_bulk("nz_cpi")
df  <- arrow::read_parquet(raw)

# Write to a file, get the path back invisibly
path <- eolas_download_bulk("nz_cpi", path = "nz_cpi.parquet")
df   <- arrow::read_parquet(path)

# Gzipped CSV (read.csv / readr compatible)
eolas_download_bulk("nz_cpi", format = "csv_gz", path = "nz_cpi.csv.gz")
df <- read.csv(gzfile("nz_cpi.csv.gz"))

# GeoParquet for a geospatial dataset
eolas_download_bulk("territorial_authority_2023",
                    format = "geoparquet",
                    path   = "ta2023.geo.parquet")

# Force monthly freshness (reproducibility across plan levels)
eolas_download_bulk("nz_cpi", freshness = "monthly", path = "nz_cpi.parquet")
```

**Arguments**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | character | — | Dataset identifier, e.g. `"nz_cpi"` |
| `freshness` | character | `"auto"` | `"auto"` — server picks based on plan (Free→monthly, Pro→current). `"monthly"` or `"current"` to override. |
| `format` | character | `"parquet"` | `"parquet"`, `"csv_gz"`, or `"geoparquet"`. GeoParquet only available on geospatial datasets. |
| `path` | character \| NULL | `NULL` | Write to this path and return it invisibly. `NULL` returns the raw bytes as a `raw` vector. Parent directories are created automatically. |
| `progress` | logical \| NULL | `NULL` | Control the download progress bar. `NULL` auto-detects: shown when `interactive()` is `TRUE`, hidden in batch/CI. `TRUE` forces the bar on; `FALSE` forces it off. Also suppressed by `EOLAS_NO_PROGRESS=1` env var. When `path = NULL` (bytes mode) progress is always disabled. |

**Returns:** Invisibly the normalised path when `path` is set; a `raw` vector when `path = NULL`.

**Errors (via `stop()`):**

| Condition | When |
|---|---|
| `"Bulk upgrade required:"` | HTTP 402 — `freshness = "current"` requires Pro plan |
| `"Bulk licence restricted:"` | HTTP 403 (licence body) — dataset excluded from bulk (e.g. OECD). Use `eolas_get()` instead. |
| `"Bulk not yet available:"` | HTTP 503 — monthly snapshot not yet generated |
| `"Not found:"` | Dataset not found |
| `"Authentication error:"` | Invalid or missing API key |

---

### `eolas_sync_bulk(name, path, format = "parquet", freshness = "auto", progress = NULL, ...)`

Incrementally sync a bulk dataset file — only re-downloads when the snapshot changes.

Issues a lightweight HEAD request to read the server's `X-Snapshot-Version` header. If the local sidecar records the same snapshot id and the file exists, returns immediately with `status = "unchanged"` and zero data I/O. Otherwise downloads the new snapshot and replaces the file **atomically** (temp file + `file.rename()`).

A sidecar file `paste0(path, ".eolas-meta.json")` is written next to the data file on every download or update.

```r
eolas_key("your_key")

# First call: full download
r <- eolas_sync_bulk("nz_cpi", path = "nz_cpi.parquet")
r$status            # "downloaded"
r$bytes_downloaded  # e.g. 2100000

# Subsequent calls: no-op when snapshot unchanged
r <- eolas_sync_bulk("nz_cpi", path = "nz_cpi.parquet")
r$status            # "unchanged"
r$bytes_downloaded  # 0

# Poll in a script
repeat {
  r <- eolas_sync_bulk("nz_cpi", path = "nz_cpi.parquet")
  if (r$status != "unchanged") message("Updated to ", r$current_snapshot_id)
  Sys.sleep(3600)
}
```

**Arguments**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | character | — | Dataset identifier, e.g. `"nz_cpi"` |
| `path` | character | — | **Required.** File path for the data. Sidecar written at `paste0(path, ".eolas-meta.json")`. |
| `format` | character | `"parquet"` | `"parquet"`, `"csv_gz"`, or `"geoparquet"`. |
| `freshness` | character | `"auto"` | `"auto"`, `"monthly"`, or `"current"`. |
| `progress` | logical \| NULL | `NULL` | Control the download progress bar. `NULL` auto-detects via `interactive()`. `TRUE` forces on; `FALSE` forces off. `EOLAS_NO_PROGRESS=1` env var suppresses globally. When `status = "unchanged"` no bar is shown regardless. |

**Returns:** Named list with the same fields as Python's `SyncResult`:

| Name | Type | Description |
|---|---|---|
| `status` | character | `"downloaded"`, `"updated"`, or `"unchanged"` |
| `previous_snapshot_id` | character \| NA | Snapshot id from the sidecar, or `NA` if none |
| `current_snapshot_id` | character | Snapshot id from the server |
| `path` | character | Normalised path to the data file |
| `bytes_downloaded` | integer | Bytes written (`0L` when unchanged) |

**Errors (via `stop()`):** Same conditions as `eolas_download_bulk`. No sidecar is written on error.

---

### `eolas_get_local(name, cache_dir = NULL, format = NULL, freshness = "auto", as_sf = NULL, as_arrow = FALSE)`

Explicit alias for `eolas_get(name, mode = "cached")`. Forces the cache+sync path regardless of dataset size or metadata.

`eolas_get(name)` in `mode = "auto"` (the default) now auto-routes large and geospatial datasets to this same path automatically — so for most use cases you no longer need to call `eolas_get_local()` explicitly. Keep using it when:

- You want to be unambiguous in production scripts.
- You need to control `cache_dir`, `format`, or `freshness` (those parameters are only available here, not on `eolas_get()`).

On the first call it fetches the bulk file from CDN and writes it to `~/.cache/eolas/`. On subsequent calls a lightweight HEAD request checks whether the file is still current; if so the cached copy is read directly with zero data transfer.

```r
library(eolas)
eolas_key("your_key")

# Geospatial dataset — first call downloads from CDN; subsequent calls read locally
gdf <- eolas_get_local("nz_parcels")      # sf object (if sf installed)

# Non-geo dataset
df  <- eolas_get_local("nz_cpi")          # data.frame

# Custom cache directory
df  <- eolas_get_local("nz_cpi", cache_dir = "/data/eolas-cache")

# Keep plain data.frame instead of converting to sf
df  <- eolas_get_local("nz_parcels", as_sf = FALSE)

# Force a specific format
df  <- eolas_get_local("nz_cpi", format = "csv_gz")
```

**Arguments**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | character | — | Dataset identifier, e.g. `"nz_parcels"` |
| `cache_dir` | character \| NULL | `NULL` | Local directory for cached files. `NULL` (default) resolves via the library precedence chain (`EOLAS_LIBRARY` env → `library_dir` in `~/.eolas/config.json` → `~/.cache/eolas/`). An explicit value always wins. See [Authentication → Library](../authentication.md#library-where-your-data-files-live). |
| `format` | character \| NULL | `NULL` | `"parquet"`, `"csv_gz"`, or `"geoparquet"`. `NULL` auto-detects from dataset metadata (geo → geoparquet, else parquet). |
| `freshness` | character | `"auto"` | `"auto"`, `"monthly"`, or `"current"`. Passed verbatim to `eolas_sync_bulk()`. |
| `as_sf` | logical \| NULL | `NULL` | When `TRUE` and the file is GeoParquet, attempts to return an `sf` object via `sfarrow::st_read_parquet()` or `sf::st_read()`. When `FALSE`, returns a plain `data.frame`. `NULL` auto-converts when geometry is present and `sf` is installed (unless `as_arrow = TRUE`). Mutually exclusive with `as_arrow = TRUE`. |
| `as_arrow` | logical | `FALSE` | Return an `arrow::Table` instead of a data frame or `sf` object. Skips all geometry materialisation. Mutually exclusive with `as_sf = TRUE`. |

**Returns:** `data.frame`, `sf` object, or `arrow::Table` when `as_arrow = TRUE`.

**Errors (via `stop()`):**

| Condition | When |
|---|---|
| `"Bulk upgrade required:"` | HTTP 402 — `freshness = "current"` requires Pro plan |
| `"Bulk licence restricted:"` | HTTP 403 (licence body) — dataset excluded from bulk (e.g. OECD). Use `eolas_get()` instead. |
| `"Bulk not yet available:"` | HTTP 503 — monthly snapshot not yet generated |

---

## Library management

These helpers manage the directory where `eolas_get_local()` and smart-routed `eolas_get()` cache bulk data files. They read and write the same `~/.eolas/config.json` that the Python `eolas-data` CLI uses, so a path set from R is immediately honoured in Python and vice versa. See [Authentication → Library](../authentication.md#library-where-your-data-files-live) for the full precedence chain.

### `eolas_library_set(path)`

Write `library_dir` to `~/.eolas/config.json`.

```r
eolas_library_set("~/eolas-library")    # user-wide persistent location
eolas_library_set("/data/eolas")        # custom absolute path
```

**Arguments:** `path` — character, the directory to use. Supports `~`-prefixed paths.  
**Returns:** The resolved (absolute) path, invisibly.

---

### `eolas_library_status()`

Show the resolved library directory and which source is supplying it.

```r
eolas_library_status()
# library: /home/you/eolas-library
# source:  /home/you/.eolas/config.json
```

**Returns:** Named list with `source`, `path`, `env_var`, `config_file`, `config_value`, invisibly. Called primarily for its printed output.

---

### `eolas_library_clear()`

Remove `library_dir` from `~/.eolas/config.json`. After clearing, `eolas_get_local()` reverts to `~/.cache/eolas/` (or `EOLAS_LIBRARY` if set).

```r
eolas_library_clear()
```

**Returns:** Invisibly `NULL`.

---

## Plotting

`eolas_dataset` is a plain data frame. `eolas_plot()` was removed in v1.3.0 — it silently mis-rendered datasets that have a dimension column (multiple series per date). Use ggplot2 directly instead:

```r
library(ggplot2)

df <- eolas_get_statsnz("nz_cpi", start = "2010-01-01")

ggplot(df, aes(date, value)) +
  geom_line() +
  labs(y = "Index (base 1000)")
```

---

## Common patterns

**With dplyr:**

```r
library(dplyr)
library(eolas)

eolas_key("vs_your_key")

eolas_get_statsnz("nz_cpi", start = "2015-01-01") |>
  filter(value > 1050) |>
  arrange(date)
```

**With ggplot2 (manual):**

```r
library(ggplot2)

df <- eolas_get_statsnz("nz_cpi", start = "2010-01-01")

ggplot(df, aes(date, value)) +
  geom_line(colour = "#3b82f6") +
  labs(title = "NZ Consumer Price Index", x = NULL, y = "Index") +
  theme_minimal()
```

**In R Markdown:**

````markdown
```{r setup, include=FALSE}
library(eolas)
eolas_key(Sys.getenv("EOLAS_API_KEY"))
```

```{r cpi-chart, fig.cap="NZ Consumer Price Index"}
library(ggplot2)
df <- eolas_get_statsnz("nz_cpi", start = "2015-01-01")
ggplot(df, aes(date, value)) + geom_line()
```
````
