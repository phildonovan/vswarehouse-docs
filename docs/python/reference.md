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

### `client.get(name, start=None, end=None, format="json", engine="pandas", limit=None, as_geo=None)`

Fetch dataset rows as a DataFrame. For everyday use prefer the source-specific methods above.

```python
df = client.get("nz_cpi", start="2020-01-01", end="2024-12-31")
df = client.get("nz_cpi", engine="polars")        # returns polars DataFrame
df = client.get("nz_addresses", limit=1000)       # first 1000 rows only
df = client.get("nz_cpi")                         # full dataset (Pro tier)

# Geospatial: returns a geopandas.GeoDataFrame when geopandas is installed
gdf = client.get("nz_addresses", limit=10)
gdf.plot()                                        # ready for mapping
gdf.to_crs("EPSG:2193")                           # reproject to NZTM
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Dataset identifier |
| `start` | `str \| None` | `None` | ISO date lower bound, e.g. `"2020-01-01"` |
| `end` | `str \| None` | `None` | ISO date upper bound |
| `format` | `str` | `"json"` | `"json"` or `"csv"`. You don't need to set this for speed — the client transparently negotiates Apache Arrow over the wire for the DataFrame path (see *Performance*). |
| `engine` | `str` | `"pandas"` | `"pandas"` or `"polars"` |
| `limit` | `int \| None` | `None` | Max rows to return. `None` requests the full dataset. Free plan is capped server-side at 50,000 rows; Pro is unlimited. |
| `as_geo` | `bool \| None` | `None` | Return a `geopandas.GeoDataFrame` for geospatial datasets. `None` auto-converts when geometry is present and `geopandas` is importable. `True` forces conversion (errors if missing). `False` keeps the raw `geometry_wkt` string column. Install with `pip install eolas-data[geo]`. |

**Returns:** `Dataset` (pandas) or `polars.DataFrame` when `engine="polars"`  
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

### `client.download_bulk(name, *, freshness="auto", format="parquet", path=None)`

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

### `client.sync_bulk(name, *, path, format="parquet", freshness="auto")`

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

## `Dataset`

A `pandas.DataFrame` subclass returned by all data-fetching methods.

**Extra attributes**

| Attribute | Type | Description |
|---|---|---|
| `eolas_name` | `str` | Series identifier, e.g. `"nz_cpi"` |
| `eolas_source` | `str` | Source label, e.g. `"Stats NZ"` |

**Methods**

### `Dataset.plot_series(ax=None, **kwargs)`

Quick matplotlib line chart.

```python
ax = df.plot_series()
ax.set_ylabel("Index")   # customise further
```

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `ax` | `matplotlib.Axes \| None` | `None` | Existing axes to plot into. Creates a new figure if `None`. |
| `**kwargs` | | | Passed to `ax.plot()`. |

**Returns:** `matplotlib.Axes`  
**Requires:** `matplotlib` — `pip install matplotlib` or `pip install eolas-data[plot]`

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
