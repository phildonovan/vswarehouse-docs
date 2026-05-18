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

## Exceptions

All exceptions inherit from `eolas_data.exceptions.EolasError`.

```python
from eolas_data.exceptions import (
    EolasError,            # base
    AuthenticationError,   # 401 / 403
    RateLimitError,        # 429
    NotFoundError,         # 404
    APIError,              # other HTTP errors — has .status_code attribute
)
```
