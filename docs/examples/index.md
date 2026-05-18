# Examples

Real-world recipes for the most common eolas use cases. Every snippet works on the published v1.0.0 clients.

---

## Plot a time series (NZ CPI)

The canonical "I just want a chart" recipe.

=== "Python"

    ```python
    from eolas_data import Client

    client = Client()  # picks up EOLAS_API_KEY env var
    df = client.statsnz("nz_cpi", start="2010-01-01")

    df.plot(x="date", y="value", title="NZ Consumer Price Index",
            ylabel="Index", figsize=(10, 4))
    ```

=== "R"

    ```r
    library(eolas)
    library(ggplot2)

    df <- eolas_get_statsnz("nz_cpi", start = "2010-01-01")

    ggplot(df, aes(date, value)) +
      geom_line() +
      labs(title = "NZ Consumer Price Index", y = "Index") +
      theme_minimal()
    ```

---

## Compare two series side-by-side

Useful for inflation-vs-unemployment, mortgage-rates-vs-house-prices, etc.

=== "Python"

    ```python
    import matplotlib.pyplot as plt

    cpi  = client.statsnz("nz_cpi",          start="2015-01-01")
    unem = client.oecd("nz_unemployment",    start="2015-01-01")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    cpi.plot(x="date", y="value", ax=ax1, title="NZ CPI", legend=False)
    unem.plot(x="date", y="value", ax=ax2, title="NZ Unemployment Rate", legend=False)
    plt.tight_layout()
    plt.show()
    ```

=== "R"

    ```r
    library(patchwork)

    cpi  <- eolas_get_statsnz("nz_cpi",        start = "2015-01-01")
    unem <- eolas_get_oecd("nz_unemployment",  start = "2015-01-01")

    p1 <- ggplot(cpi,  aes(date, value)) + geom_line() + labs(title = "NZ CPI")
    p2 <- ggplot(unem, aes(date, value)) + geom_line() + labs(title = "Unemployment %")

    p1 / p2   # stacked with patchwork
    ```

---

## Discover what's available

If you don't know the exact dataset name, browse first.

=== "Python"

    ```python
    # Everything
    all_datasets = client.list()
    print(f"{len(all_datasets)} datasets available")

    # Filter by source
    nz  = client.list("Stats NZ")
    rbnz = client.list("RBNZ")

    # Search by name fragment
    cpi_like = [d for d in all_datasets if "cpi" in d["name"]]
    for d in cpi_like:
        print(f"{d['name']:40} {d['source']}")
    ```

=== "R"

    ```r
    # Source-specific helpers
    nz   <- eolas_list_statsnz()
    rbnz <- eolas_list_rbnz()

    # Everything
    all_datasets <- eolas_list()

    # Filter by name fragment (base R)
    cpi_like <- all_datasets[grepl("cpi", all_datasets$name), ]
    cpi_like[, c("name", "source")]
    ```

=== "CLI"

    ```bash
    eolas datasets list --search cpi
    eolas datasets list --source "Stats NZ" | head -20
    ```

---

## Load a boundary and map it

Spatial datasets auto-return as `GeoDataFrame` (Python) or `sf` (R) when the optional dep is installed.

=== "Python"

    ```bash
    pip install eolas-data[geo]   # adds geopandas + shapely
    ```

    ```python
    # 2023 meshblock boundaries — small enough to fit on Free tier with date filter
    mb = client.statsnz_geo("nz_meshblock_2023", as_sf=True)

    # Quick map
    mb.plot(figsize=(10, 10), edgecolor="white", linewidth=0.1)

    # Or filter to Wellington and join your own data
    wellington = mb[mb["regc_code_2023"] == "09"]   # 09 = Wellington Region
    wellington.plot()
    ```

=== "R"

    ```r
    install.packages("sf")   # one-time

    mb <- eolas_get_statsnz_geo("nz_meshblock_2023", as_sf = TRUE)

    library(ggplot2)
    ggplot(mb) + geom_sf(linewidth = 0.05) + theme_void()

    # Filter to a region
    wellington <- mb[mb$regc_code_2023 == "09", ]
    ggplot(wellington) + geom_sf() + theme_void()
    ```

> **Heads up**: Meshblock 2023 has ~57k features. Free tier row cap is 50,000 — this dataset will truncate. Filter via the API (`start` / `end` only work on time series; for spatial you need a region/bbox filter — not yet in v1.0). For full coverage, use Pro tier or [download the snapshot](https://eolas.fyi/datasets/nz_meshblock_2023/download).

---

## Schedule a weekly download via CLI

Set-and-forget for analysts who want fresh data without writing a cron job.

```bash
# One-time setup
pip install eolas-data[cli]
eolas auth set-key

# Schedule a weekly fetch — registers with cron on macOS/Linux, Task Scheduler on Windows
eolas schedule add nz_cpi \
    --weekly \
    --out ~/data/nz_cpi.csv \
    --format csv

# List active schedules
eolas schedule list

# Remove one
eolas schedule remove nz_cpi
```

The schedule fires from your local machine — for always-on scheduling, run it on a server. To filter the export:

```bash
eolas schedule add nz_cpi \
    --weekly \
    --start 2020-01-01 \
    --out ~/data/nz_cpi_recent.csv
```

---

## Export to CSV

=== "Python"

    ```python
    df = client.statsnz("nz_cpi", start="2020-01-01")
    df.to_csv("nz_cpi.csv", index=False)
    ```

=== "R"

    ```r
    df <- eolas_get_statsnz("nz_cpi", start = "2020-01-01")
    write.csv(df, "nz_cpi.csv", row.names = FALSE)
    ```

=== "CLI"

    ```bash
    eolas get nz_cpi --start 2020-01-01 --format csv > nz_cpi.csv
    ```

---

## Notebook-friendly caching

Re-running cells shouldn't re-hit the API. Both clients support per-client caching.

=== "Python"

    ```python
    client = Client(cache=True)

    df = client.statsnz("nz_cpi")    # fetched
    df = client.statsnz("nz_cpi")    # from cache (no HTTP call)
    ```

=== "R Markdown / Quarto"

    ````markdown
    ```{r load-data, cache=TRUE}
    library(eolas)
    df <- eolas_get_statsnz("nz_cpi", start = "2015-01-01")
    ```
    ````

---

## In R Markdown / Quarto

````markdown
---
title: "NZ Economic Overview"
---

```{r setup, include=FALSE}
library(eolas)
library(ggplot2)
# EOLAS_API_KEY is picked up from .Renviron — no need to call eolas_key()
```

```{r cpi, fig.cap="NZ Consumer Price Index since 2010"}
eolas_get_statsnz("nz_cpi", start = "2010-01-01") |>
  ggplot(aes(date, value)) +
    geom_line() +
    labs(y = "Index (base 1000)") +
    theme_minimal()
```

```{r unemployment, fig.cap="NZ Unemployment Rate"}
eolas_get_oecd("nz_unemployment", start = "2010-01-01") |>
  ggplot(aes(date, value)) +
    geom_line() +
    labs(y = "Rate (%)") +
    theme_minimal()
```
````

---

## Production patterns

### Catch and handle errors gracefully

```python
from eolas_data.exceptions import RateLimitError, NotFoundError

try:
    df = client.statsnz("nz_cpi", start="2010-01-01")
except RateLimitError:
    print("Quota hit — backing off until next month")
    raise
except NotFoundError:
    print(f"Dataset name was wrong; available similar: {[d['name'] for d in client.list() if 'cpi' in d['name']]}")
    raise
```

### Detect row-cap truncation

When you query a large dataset on the Free tier, the response is silently capped at 50,000 rows. Check for it:

```python
df = client.statsnz("nz_addresses")     # ~3M rows — will be capped

if df.eolas_truncated:
    print(f"Got {len(df)} rows of {df.eolas_total_rows} — upgrade for full data")
```

### Chunk a large query by date

Stay under the row cap by paging through time:

```python
import pandas as pd
from datetime import date, timedelta

chunks = []
start = date(2010, 1, 1)
end   = date(2024, 12, 31)
step  = timedelta(days=365)

cur = start
while cur < end:
    nxt = min(cur + step, end)
    df = client.statsnz("nz_cpi", start=cur.isoformat(), end=nxt.isoformat())
    chunks.append(df)
    cur = nxt

full = pd.concat(chunks, ignore_index=True)
```

For very large queries, the Snowflake share (Enterprise tier) is a better fit — zero-copy, no API in the loop.

---

## See also

- [Authentication](../authentication.md) — for the API-key setup that all these examples assume
- [Troubleshooting](../troubleshooting.md) — when an example doesn't work
- [Python reference](../python/reference.md) / [R reference](../r/reference.md) — full method-by-method API surface
