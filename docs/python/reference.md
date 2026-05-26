# Python API reference

## `Client`

```python
class Client(api_key=None, base_url="https://api.eolas.fyi", cache=False)
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `api_key` | `str \| None` | `None` | Your `vs_...` key. Falls back to `EOLAS_API_KEY` env var. |
| `base_url` | `str` | `"https://api.eolas.fyi"` | Override for testing. |
| `cache` | `bool` | `False` | Cache responses in memory for the lifetime of the client. |

---

### Source-specific methods

All source methods accept the same parameters as `client.get()` and return a `Dataset` tagged with the source label.

| Method | Source |
|---|---|
| `client.statsnz(name, **kwargs)` | Stats NZ |
| `client.oecd(name, **kwargs)` | OECD |
| `client.rbnz(name, **kwargs)` | RBNZ |
| `client.treasury(name, **kwargs)` | NZ Treasury |
| `client.linz(name, **kwargs)` | LINZ |
| `client.statsnz_geo(name, **kwargs)` | Stats NZ Geospatial |
| `client.mbie(name, **kwargs)` | MBIE |
| `client.nzta(name, **kwargs)` | Waka Kotahi (NZTA) |
| `client.msd(name, **kwargs)` | MSD |
| `client.police(name, **kwargs)` | NZ Police / MoJ |
| `client.immigration(name, **kwargs)` | Immigration NZ |
| `client.lris(name, **kwargs)` | Manaaki Whenua / LRIS |
| `client.geonet(name, **kwargs)` | GeoNet |
| `client.doc(name, **kwargs)` | DOC (Department of Conservation) |
| `client.akl_council(name, **kwargs)` | Auckland Council |
| `client.akl_transport(name, **kwargs)` | Auckland Transport |
| `client.bay_of_plenty(name, **kwargs)` | Bay of Plenty Councils |
| `client.charities(name, **kwargs)` | Charities Services |
| `client.colab_waikato(name, **kwargs)` | Co-Lab Waikato |
| `client.ecan_canterbury(name, **kwargs)` | ECan / Canterbury |
| `client.eeca(name, **kwargs)` | EECA (energy use, EV chargers, regional heat demand) |
| `client.hawkes_bay(name, **kwargs)` | Hawke's Bay Councils |
| `client.manawatu_whanganui(name, **kwargs)` | Manawatū-Whanganui Councils |
| `client.napier_whanganui(name, **kwargs)` | Napier + Whanganui |
| `client.northland(name, **kwargs)` | Northland Councils |
| `client.otago(name, **kwargs)` | Otago Councils |
| `client.pharmac(name, **kwargs)` | PHARMAC |
| `client.southland(name, **kwargs)` | Southland Councils |
| `client.taranaki(name, **kwargs)` | Taranaki Councils |
| `client.top_of_south(name, **kwargs)` | Gisborne / Top of South Councils |
| `client.wellington(name, **kwargs)` | Wellington Region Councils |
| `client.west_coast(name, **kwargs)` | West Coast (Te Tai o Poutini) |

```python
df = client.statsnz("nz_cpi", start="2020-01-01")
df.eolas_source  # "Stats NZ"
```

---

### `client.list(source=None)`

Return metadata for all available series.

```python
all_series = client.list()
nz_series  = client.list("Stats NZ")
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `source` | `str \| None` | `None` | Filter by source label, e.g. `"Stats NZ"`, `"OECD"`. |

**Returns:** `list[dict]`

---

### `client.info(name)`

Return metadata for a single series.

```python
meta = client.info("nz_cpi")
# {"name": "nz_cpi", "title": "NZ Consumer Price Index", "source": "Stats NZ", ...}
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `name` | `str` | Series identifier, e.g. `"nz_cpi"` |

**Returns:** `dict`  
**Raises:** `NotFoundError` if the series does not exist.

---

### `client.get(name, start=None, end=None, format="json", engine="pandas", limit=None, as_geo=None, as_arrow=False, *, mode="auto")`

Fetch dataset rows as a DataFrame. For everyday use prefer the source-specific methods above — they call `get()` internally and inherit smart routing.

`get()` is now a **smart entry point**: in `mode="auto"` (the default) it inspects the dataset's metadata and automatically routes large or geospatial datasets through the cache+sync path, returning a `GeoDataFrame` in seconds instead of minutes. See [Bulk downloads](../bulk-downloads.md) for the full routing rules.

```python
# Smart default: nz_parcels auto-routes to cache+sync (~seconds after first call)
gdf = client.get("nz_parcels")

# Small dataset: stays on the live path (no metadata overhead for sliced queries)
df = client.get("nz_cpi", start="2020-01-01", end="2024-12-31")
df = client.get("nz_cpi", engine="polars")        # returns polars DataFrame
df = client.get("nz_addresses", limit=1000)       # limit= forces live

# Force live even for large datasets
gdf = client.get("nz_parcels", mode="live")

# Force cache+sync explicitly (same as get_local)
gdf = client.get("nz_parcels", mode="cached")
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Dataset identifier |
| `start` | `str \| None` | `None` | ISO date lower bound, e.g. `"2020-01-01"`. Forces live path in `mode="auto"`. |
| `end` | `str \| None` | `None` | ISO date upper bound. Forces live path in `mode="auto"`. |
| `format` | `str` | `"json"` | `"json"` or `"csv"`. You don't need to set this for speed — the client transparently negotiates Apache Arrow over the wire for the DataFrame path (see *Performance*). |
| `engine` | `str` | `"pandas"` | `"pandas"` or `"polars"` |
| `limit` | `int \| None` | `None` | Max rows to return. `None` requests the full dataset. Free plan is capped server-side at 50,000 rows; Pro is unlimited. Forces live path in `mode="auto"`. |
| `as_geo` | `bool \| None` | `None` | Return a `geopandas.GeoDataFrame` for geospatial datasets. `None` auto-converts when geometry is present and `geopandas` is importable. `True` forces conversion (errors if missing). `False` keeps the raw `geometry_wkt` string column. Install with `pip install eolas-data[geo]`. Mutually exclusive with `as_arrow=True`. |
| `as_arrow` | `bool` | `False` | Return a `pyarrow.Table` instead of a DataFrame or GeoDataFrame. Skips all shapely allocation — geometry stays as Arrow buffers. Works on all datasets, all routing modes, and all source helpers. Mutually exclusive with `as_geo=True`. |
| `mode` | `str` | `"auto"` | `"auto"` — smart-routes via metadata (see above). `"live"` — hit the live API directly; useful for freshest data, OECD-restricted sources, or sliced queries (e.g. with `limit=`/`start=`/`end=`). The server returns **413** if the dataset is large (>100 k rows) or has geometry and no filter is set — use `mode="cached"` for whole-dataset pulls. `"cached"` — always use cache+sync (equivalent to `get_local()`). |

**Returns:** `Dataset` (pandas), `polars.DataFrame` when `engine="polars"`, `geopandas.GeoDataFrame` when routed through the cache path, or `pyarrow.Table` when `as_arrow=True`  
**Raises:** `NotFoundError`, `AuthenticationError`, `RateLimitError`

#### Performance: Arrow & Parquet

The API serves datasets in four formats via `?format=` — `json` (default), `csv`, `arrow` (Apache Arrow IPC stream), and `parquet`. Arrow and Parquet are columnar and typed, so they're dramatically faster for anything beyond a few hundred rows. Measured end-to-end on a 100,000-row × 71-column dataset:

| Format | Wire size | Total (download + parse) |
|---|---|---|
| JSON | 165 MB | 39.5 s |
| **Arrow** | 66 MB | **7.7 s** (5× faster; ~80× faster parse) |
| **Parquet** | 6.3 MB | **4.3 s** (9× faster; 26× smaller) |

The Python client uses Arrow automatically — `client.get("nz_cpi")` returns the same `DataFrame`, just much faster on large pulls, with a transparent JSON fallback. Hitting the REST API directly:

```bash
curl -H "X-API-Key: $EOLAS_API_KEY" \
  "https://api.eolas.fyi/v1/datasets/nzta_cas_crashes/data?format=parquet&limit=100000" \
  -o crashes.parquet
```

---

### `client.sync(name, library_dir)`

Incrementally sync a dataset into a local library directory. On the first call, downloads the full snapshot. On subsequent calls, fetches only the rows appended since the last sync and adds them as a delta file. Returns immediately (no download) when the server snapshot is unchanged.

The dataset is stored as a directory of Parquet files plus `_eolas-manifest.json`. Any Parquet-aware tool (`pandas`, `DuckDB`, `polars`, `Spark`, `dbt`) can read the whole directory as one logical table.

See the [Sync guide](../sync-guide.md) for the full conceptual walkthrough, cron and Airflow recipes, and a comparison vs Fivetran/Stitch.

```python
from eolas_data import Client

client = Client("your_eolas_key")
LIBRARY = "/data/nz-warehouse"

# First sync — full download
result = client.sync("nz_parcels", library_dir=LIBRARY)
print(result.status)           # "snapshot_full"
print(result.bytes_downloaded) # e.g. 1_650_000_000

# Re-sync — only delta rows
result = client.sync("nz_parcels", library_dir=LIBRARY)
print(result.status)   # "unchanged" or "snapshot_delta"
print(result.rows_added)  # 0 or e.g. 2847
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `name` | `str` | Dataset identifier, e.g. `"nz_parcels"` |
| `library_dir` | `str \| Path` | Root directory of your local dataset library. The dataset is written to `<library_dir>/<name>/`. |

**Returns:** `SyncResult` (see below)

---

### `client.sync_all(library_dir, datasets=None)`

Sync multiple datasets concurrently. When `datasets` is not provided, syncs every dataset already registered in the library (by manifest). Up to 4 datasets are synced in parallel.

```python
# Explicit list
results = client.sync_all(
    library_dir="/data/nz-warehouse",
    datasets=["nz_parcels", "nz_addresses", "nz_property_titles"],
)
for name, r in results.items():
    print(f"{name}: {r.status} (+{r.rows_added} rows)")

# Everything in the library
results = client.sync_all(library_dir="/data/nz-warehouse")
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `library_dir` | `str \| Path` | — | Root library directory |
| `datasets` | `list[str] \| None` | `None` | Datasets to sync. `None` syncs all datasets with existing manifests in the library. |

**Returns:** `dict[str, SyncResult]`

---

### `client.compact(path)`

Merge all snapshot and delta files in a dataset directory into a single new snapshot file, then remove the old files. The manifest is updated atomically. Safe to run at any time — old files are only removed after the new snapshot is confirmed.

Pass a single dataset directory or the library root (compacts all datasets with deltas).

```python
# Single dataset
client.compact("/data/nz-warehouse/nz_parcels")

# Entire library
client.compact("/data/nz-warehouse")
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `path` | `str \| Path` | Path to a dataset directory OR the library root. |

**Returns:** `CompactResult`

| Field | Type | Description |
|---|---|---|
| `files_removed` | `int` | Number of old snapshot/delta files deleted |
| `bytes_saved` | `int` | Approximate disk space recovered |
| `new_snapshot_file` | `str` | Filename of the new consolidated snapshot |

---

### `SyncResult`

Returned by `client.sync()`. Also available as `eolas_data.SyncResult`.

| Field | Type | Description |
|---|---|---|
| `status` | `str` | `"unchanged"` — no data transferred. `"snapshot_full"` — full dataset downloaded (first sync, or full reset after lineage gap). `"snapshot_delta"` — delta rows appended. |
| `bytes_downloaded` | `int` | Bytes written to disk (`0` when `status="unchanged"`) |
| `rows_added` | `int` | Rows written in this sync (`0` when unchanged) |
| `files_added` | `int` | New Parquet files created (`0` when unchanged) |
| `current_snapshot_id` | `str` | The snapshot ID now recorded in the manifest |
| `dataset` | `str` | Dataset name |

---

### `client.get()` — library-aware smart routing

When `library_dir` is configured (via `eolas library set` or the `EOLAS_LIBRARY` env var) and a manifest exists for the requested dataset, `client.get()` and the source-specific helpers (`client.linz()`, etc.) automatically read from the local library files using PyArrow's `ParquetDataset` — zero network traffic, no cadence re-check if the manifest is within the dataset's refresh window.

```python
# After syncing nz_parcels into /data/nz-warehouse:
client = Client("your_key")  # EOLAS_LIBRARY=/data/nz-warehouse or eolas library set

gdf = client.linz("nz_parcels")   # reads from /data/nz-warehouse/nz_parcels/ — no download
df  = client.get("nz_cpi")        # small dataset, still goes live (no manifest)
```

Set the library directory once:

```bash
eolas library set /data/nz-warehouse
```

Or per-process via env var: `EOLAS_LIBRARY=/data/nz-warehouse python my_pipeline.py`.

---

### `client.download_bulk(name, *, freshness="auto", format="parquet", path=None, progress=None)`

Download a complete dataset as a single binary file via the `/v1/bulk/{namespace}/{table}` endpoint. Monthly snapshots are served from Cloudflare's edge cache; Pro current snapshots are lazy-generated on first request.

See [Bulk downloads](../bulk-downloads.md) for the full narrative, tier comparison, and worked examples.

```python
import io, pandas as pd

# Return raw bytes
raw = client.download_bulk("nz_cpi")
df  = pd.read_parquet(io.BytesIO(raw))

# Write to a file, get the path back
path = client.download_bulk("nz_cpi", path="nz_cpi.parquet")

# Gzipped CSV
client.download_bulk("nz_cpi", format="csv_gz", path="nz_cpi.csv.gz")

# GeoParquet for a geospatial dataset
import geopandas as gpd
raw = client.download_bulk("territorial_authority_2023", format="geoparquet")
gdf = gpd.read_parquet(io.BytesIO(raw))

# Force monthly freshness (reproducibility across plan levels)
client.download_bulk("nz_cpi", freshness="monthly", path="nz_cpi.parquet")
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Dataset identifier, e.g. `"nz_cpi"` |
| `freshness` | `str` | `"auto"` | `"auto"` — server picks based on plan (Free→monthly, Pro→current). `"monthly"` or `"current"` to override. |
| `format` | `str` | `"parquet"` | `"parquet"`, `"csv_gz"`, or `"geoparquet"`. GeoParquet only available on geospatial datasets. |
| `path` | `str \| Path \| None` | `None` | Write to this path and return the resolved `Path`. `None` returns raw bytes. Parent directories are created automatically. |
| `progress` | `bool \| None` | `None` | Control the download progress bar. `None` auto-detects: shown when `sys.stdout.isatty()` is `True` (terminal or VSCode notebook), hidden otherwise. `True` forces the bar on; `False` forces it off. Also suppressed by `EOLAS_NO_PROGRESS=1` env var. When `path=None` (bytes mode) progress is always disabled. |

**Returns:** `pathlib.Path` when `path` is set; `bytes` when `path` is `None`.

**Raises:**

| Exception | When |
|---|---|
| `BulkUpgradeRequired` | HTTP 402 — `freshness="current"` requires Pro plan |
| `BulkLicenceRestricted` | HTTP 403 (licence body) — dataset excluded from bulk (e.g. OECD). Use `client.get()` instead. |
| `BulkNotYetAvailable` | HTTP 503 — monthly snapshot not yet generated |
| `NotFoundError` | Dataset not found |
| `AuthenticationError` | Invalid or missing API key |

```python
from eolas_data.exceptions import BulkUpgradeRequired, BulkLicenceRestricted

try:
    client.download_bulk("nz_cpi", freshness="current")
except BulkUpgradeRequired:
    print("Upgrade to Pro for current snapshots: https://eolas.fyi/pricing")
```

---

### `client.sync_bulk(name, *, path, format="parquet", freshness="auto", progress=None)`

Incrementally sync a bulk dataset file — only re-downloads when the snapshot changes.

Issues a lightweight HEAD request to read the server's `X-Snapshot-Version` header. If the local sidecar records the same snapshot id and the file exists, returns immediately with `status="unchanged"` and zero data I/O. Otherwise downloads the new snapshot and replaces the file **atomically** (`os.replace()`).

A sidecar file `<path>.eolas-meta.json` is written next to the data file on every download or update, recording the snapshot id, timestamp, and source URL.

```python
from eolas_data import Client, SyncResult

client = Client("your_api_key")

# First call: full download
r = client.sync_bulk("nz_cpi", path="nz_cpi.parquet")
print(r.status)            # "downloaded"
print(r.bytes_downloaded)  # e.g. 2_100_000

# Subsequent calls: no-op when snapshot unchanged
r = client.sync_bulk("nz_cpi", path="nz_cpi.parquet")
print(r.status)            # "unchanged"
print(r.bytes_downloaded)  # 0

# After a new ETL run: file replaced in place
r = client.sync_bulk("nz_cpi", path="nz_cpi.parquet")
print(r.status)            # "updated"
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Dataset identifier, e.g. `"nz_cpi"` |
| `path` | `str \| Path` | — | **Required.** Where to write the data file. Sidecar lives at `f"{path}.eolas-meta.json"`. |
| `format` | `str` | `"parquet"` | `"parquet"`, `"csv_gz"`, or `"geoparquet"`. |
| `freshness` | `str` | `"auto"` | `"auto"`, `"monthly"`, or `"current"`. |
| `progress` | `bool \| None` | `None` | Control the download progress bar. `None` auto-detects via `sys.stdout.isatty()`. `True` forces the bar on; `False` forces it off. `EOLAS_NO_PROGRESS=1` env var globally suppresses. When `status="unchanged"` no bar is shown regardless (no data transferred). |

**Returns:** `SyncResult` — a dataclass with fields:

| Field | Type | Description |
|---|---|---|
| `status` | `str` | `"downloaded"`, `"updated"`, or `"unchanged"` |
| `previous_snapshot_id` | `str \| None` | Snapshot id from the sidecar before sync, or `None` if no sidecar existed |
| `current_snapshot_id` | `str` | Snapshot id from the server |
| `path` | `pathlib.Path` | Resolved path to the data file |
| `bytes_downloaded` | `int` | Bytes written (`0` when unchanged) |

**Raises:** Same as `download_bulk` (`BulkUpgradeRequired`, `BulkLicenceRestricted`, `BulkNotYetAvailable`, `NotFoundError`, `AuthenticationError`). No sidecar is written on error.

---

### `client.get_local(name, *, cache_dir="~/.cache/eolas", format=None, freshness="auto", as_geo=None, as_arrow=False)`

Explicit alias for `client.get(name, mode="cached")`. Forces the cache+sync path regardless of dataset size or metadata.

`client.get(name)` in `mode="auto"` (the default) now auto-routes large and geospatial datasets to this same path automatically — so for most use cases you no longer need to call `get_local()` explicitly. Keep using it when:

- You want to be unambiguous in production scripts.
- You need to control `cache_dir`, `format`, or `freshness` (those parameters are only available here, not on `get()`).

On the first call it fetches the bulk file from CDN and writes it to `~/.cache/eolas/`. On subsequent calls a lightweight HEAD request checks whether the file is still current; if so the local copy is read directly with zero data transfer.

```python
from eolas_data import Client

client = Client("your_api_key")

# Geospatial dataset — first call downloads from CDN; subsequent calls read locally
gdf = client.get_local("nz_parcels")     # geopandas.GeoDataFrame (if geopandas installed)

# Non-geo dataset
df = client.get_local("nz_cpi")          # pd.DataFrame

# Custom cache directory
df = client.get_local("nz_cpi", cache_dir="/data/eolas-cache")

# Force a specific format
df = client.get_local("nz_cpi", format="csv_gz")

# Keep raw WKB column instead of converting to GeoDataFrame
df = client.get_local("nz_parcels", as_geo=False)
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Dataset identifier, e.g. `"nz_parcels"` |
| `cache_dir` | `str \| Path \| None` | `None` | Local directory for cached files. `None` (default) resolves via the library precedence chain (env → config → `~/.cache/eolas/`). An explicit value wins outright. See [Authentication → Library](../authentication.md#library-where-your-data-files-live). |
| `format` | `str \| None` | `None` | `"parquet"`, `"csv_gz"`, or `"geoparquet"`. `None` auto-detects from dataset metadata (geo → geoparquet, else parquet). |
| `freshness` | `str` | `"auto"` | `"auto"`, `"monthly"`, or `"current"`. Passed verbatim to `sync_bulk`. |
| `as_geo` | `bool \| None` | `None` | When `True` and the file is GeoParquet and `geopandas` is installed, returns a `GeoDataFrame`. When `False` (or geopandas is missing), returns a plain `DataFrame` with the raw WKT column. `None` auto-converts when geometry is present and geopandas is importable (unless `as_arrow=True`). Mutually exclusive with `as_arrow=True`. |
| `as_arrow` | `bool` | `False` | Return a `pyarrow.Table` instead of a DataFrame or GeoDataFrame. Skips all shapely allocation. Mutually exclusive with `as_geo=True`. |

**Returns:** `pd.DataFrame`, `geopandas.GeoDataFrame`, or `pyarrow.Table` when `as_arrow=True`

**Raises:**

| Exception | When |
|---|---|
| `BulkUpgradeRequired` | HTTP 402 — `freshness="current"` requires Pro plan |
| `BulkLicenceRestricted` | HTTP 403 (licence body) — dataset excluded from bulk (e.g. OECD). Use `client.get()` instead. |
| `BulkNotYetAvailable` | HTTP 503 — monthly snapshot not yet generated |
| `NotFoundError` | Dataset not found |
| `AuthenticationError` | Invalid or missing API key |

---

## `Dataset`

A `pandas.DataFrame` subclass returned by all data-fetching methods.

**Extra attributes**

| Attribute | Type | Description |
|---|---|---|
| `eolas_name` | `str` | Series identifier, e.g. `"nz_cpi"` |
| `eolas_source` | `str` | Source label, e.g. `"Stats NZ"` |

**Plotting**

`Dataset` subclasses `DataFrame`, so any matplotlib, seaborn, or plotly workflow works directly. `plot_series()` was removed in v1.3.0 — use pandas `.plot()` instead:

```python
df.plot(x="date", y="value")
```

---

## CLI auth commands

Manages the API key from the terminal. Requires `pip install 'eolas-data[cli]'`. For the OS-keyring commands, also install the `secure` extra:

```bash
pip install 'eolas-data[secure]'
```

### `eolas auth save-key [KEY]`

Save the API key to the OS keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service). Requires `pip install 'eolas-data[secure]'`.

```bash
eolas auth save-key                # interactive masked prompt
eolas auth save-key vs_mykey       # non-interactive (e.g. piped from a script)
```

Stored under `service="eolas"`, `username="api-key"` — the same slot the R client uses, so a key saved from Python is immediately visible in R.

### `eolas auth clear-key`

Remove the API key from the OS keyring. Does not affect `EOLAS_API_KEY` or the config file.

```bash
eolas auth clear-key
```

### `eolas auth status`

Show the resolved API key (masked to first 8 characters) and which source supplied it. Checks all sources in precedence order: env var → OS keyring → config file.

```bash
eolas auth status
# key:    vs_abcde1…
# source: OS keyring (service='eolas')
```

### `eolas auth set-key`

Save the API key to `~/.eolas/config.json` (chmod 600) as a plaintext fallback. No extra install required.

```bash
eolas auth set-key
```

### `eolas auth clear`

Remove `~/.eolas/config.json`. Does not affect the env var or keyring.

---

## CLI library commands

Manage the directory where `get_local()` and smart-routed `get()` cache bulk data files. Requires `pip install 'eolas-data[cli]'`.

### `eolas library set [PATH]`

Write `library_dir` to `~/.eolas/config.json`. Future calls to `get_local()` use this directory unless overridden by `EOLAS_LIBRARY` or an explicit `cache_dir=` argument.

```bash
eolas library set ~/eolas-library        # user-wide persistent location
eolas library set /data/eolas           # custom absolute path
eolas library set                        # interactive prompt if no arg given
```

The config file is shared with the R `eolas` client, so a path set here is immediately honoured in R.

### `eolas library status`

Show the resolved library directory and which source is supplying it (env var, config file, or `~/.cache/eolas/` fallback).

```bash
eolas library status
# library: /home/you/eolas-library
# source:  /home/you/.eolas/config.json
```

### `eolas library clear`

Remove `library_dir` from `~/.eolas/config.json`. After clearing, `get_local()` reverts to `~/.cache/eolas/` (or `EOLAS_LIBRARY` if set).

```bash
eolas library clear
```

---

## Exceptions

All exceptions inherit from `eolas_data.exceptions.EolasError`.

```python
from eolas_data.exceptions import (
    EolasError,              # base
    AuthenticationError,     # 401 / 403
    RateLimitError,          # 429
    NotFoundError,           # 404
    APIError,                # other HTTP errors — has .status_code attribute
    # Bulk-download-specific (subclass APIError)
    BulkUpgradeRequired,     # 402 — current freshness requires Pro
    BulkLicenceRestricted,   # 403 (licence body) — dataset excluded from bulk
    BulkNotYetAvailable,     # 503 — monthly snapshot not yet generated
)
```
