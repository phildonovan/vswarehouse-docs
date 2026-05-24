# Python client

The `eolas-data` Python package provides a `Client` class that wraps the eolas REST API and returns **`Dataset` objects** — pandas DataFrames with source metadata and a built-in plot method.

## Installation

```bash
pip install eolas-data
```

Optional extras:

```bash
pip install eolas-data[polars]      # polars output support
pip install eolas-data[plot]        # matplotlib for plot_series()
```

Requires Python 3.10+ and pandas 1.5+.

## Initialisation

```python
from eolas_data import Client

# Pass key directly
client = Client("your_eolas_key")

# Read from EOLAS_API_KEY environment variable
client = Client()

# With in-memory cache (great for notebooks)
client = Client("your_eolas_key", cache=True)
```

## Source-specific helpers

The recommended way to fetch data — the source is encoded in the method name, making code self-documenting and autocomplete-friendly:

```python
df  = client.statsnz("nz_cpi", start="2020-01-01")   # Stats NZ
df  = client.oecd("nz_gdp_growth")                    # OECD
df  = client.rbnz("rbnz_b2_wholesale_rates_monthly")  # RBNZ
df  = client.treasury("treasury_fiscal_spending")     # NZ Treasury
gdf = client.linz("nz_parcels")  # LINZ (~3M rows — auto-bulks in seconds, no limit needed
```

Source-specific helpers call `client.get()` internally and inherit smart routing: large and geospatial datasets auto-route through the cache+sync path, so `client.linz("nz_parcels")` now returns a GeoDataFrame in seconds — not 15 minutes. The first call emits a one-line log explaining what happened; subsequent calls are silent.

For cases where you want to be explicit, use `get_local()` (same path, extra options for `cache_dir` / `format` / `freshness`), or pass `mode="live"` to force the raw Iceberg scan:

```python
# Explicit cache+sync path with extra control
gdf = client.get_local("nz_parcels")
gdf = client.get_local("nz_parcels", cache_dir="/data/eolas", freshness="monthly")

# Force live scan regardless of dataset size
gdf = client.get("nz_parcels", mode="live")
```

See [Bulk downloads](../bulk-downloads.md) for the full routing rules and tier comparison.

Each returns a `Dataset` tagged with the source label.

## Discovery

```python
client.list()              # all series — list of dicts
client.list("Stats NZ")   # filter by source
```

## Dataset

All data-fetching methods return a `Dataset` — a pandas DataFrame subclass with extra metadata:

```python
df = client.statsnz("nz_cpi", start="2020-01-01")

print(df)
# Dataset: nz_cpi [Stats NZ]
# 20 rows
#          date  period   value
# 0  2020-01-01  2020Q1  1010.0
# ...

df.eolas_name    # "nz_cpi"
df.eolas_source  # "Stats NZ"
```

### `.plot_series()`

Quick matplotlib line chart — returns the `Axes` object for further customisation:

```python
ax = df.plot_series()
ax.set_ylabel("Index (base 1000)")   # add to the returned axes
```

Requires `matplotlib`: `pip install matplotlib`.

## Cache

Pass `cache=True` to avoid re-fetching the same series in a notebook session:

```python
client = Client("your_eolas_key", cache=True)

df1 = client.statsnz("nz_cpi")   # hits the API
df2 = client.statsnz("nz_cpi")   # returned from cache
```

## Polars output

```python
df = client.get("nz_cpi", engine="polars")
# returns a polars DataFrame
```

Requires `polars`: `pip install polars`.

## Exceptions

```python
from eolas_data.exceptions import RateLimitError, AuthenticationError, NotFoundError

try:
    df = client.statsnz("nz_cpi")
except RateLimitError:
    print("Upgrade to Pro for unlimited requests")
except AuthenticationError:
    print("Check your API key")
except NotFoundError:
    print("Series does not exist")
```

| Exception | HTTP status | When raised |
|---|---|---|
| `AuthenticationError` | 401, 403 | Invalid or inactive key |
| `RateLimitError` | 429 | Daily limit reached |
| `NotFoundError` | 404 | Series identifier not found |
| `APIError` | other | Unexpected API error |

## Source

[github.com/phildonovan/eolas-data-python](https://github.com/phildonovan/eolas-data-python) · [PyPI](https://pypi.org/project/eolas-data/)
