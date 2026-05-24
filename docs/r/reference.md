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

### `eolas_get(name, start = NULL, end = NULL, limit = NULL, as_sf = NULL)`

Generic workhorse. For everyday use prefer the source-specific helpers below.

```r
df  <- eolas_get("nz_cpi", start = "2020-01-01", end = "2024-12-31")
df  <- eolas_get("nz_addresses", limit = 1000)   # first 1000 rows
df  <- eolas_get("nz_cpi")                       # full dataset (Pro tier)

# Geospatial: returns an sf object when the sf package is installed
gdf <- eolas_get("nz_addresses", limit = 10)
plot(gdf["full_address"])                     # ready for mapping
sf::st_transform(gdf, 2193)                   # reproject to NZTM
```

**Arguments**

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | character | — | Dataset identifier |
| `start` | character \| NULL | `NULL` | ISO date lower bound, e.g. `"2020-01-01"` |
| `end` | character \| NULL | `NULL` | ISO date upper bound |
| `limit` | integer \| NULL | `NULL` | Max rows. `NULL` requests the full dataset. Free plan is capped server-side at 50,000 rows; Pro is unlimited. |
| `as_sf` | logical \| NULL | `NULL` | Return an `sf` object for geospatial datasets. `NULL` auto-converts when geometry is present and the `sf` package is installed. `TRUE` forces conversion (errors if missing). `FALSE` keeps the raw `geometry_wkt` string column. Install with `install.packages("sf")`. |

**Returns:** `eolas_dataset` data frame, or an `sf` object when geometry is present and conversion is enabled.

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
| `eolas_get_statsnz(name, start, end, limit, as_sf)` | Stats NZ |
| `eolas_get_oecd(name, start, end, limit, as_sf)` | OECD |
| `eolas_get_rbnz(name, start, end, limit, as_sf)` | RBNZ |
| `eolas_get_treasury(name, start, end, limit, as_sf)` | NZ Treasury |
| `eolas_get_linz(name, start, end, limit, as_sf)` | LINZ |
| `eolas_get_statsnz_geo(name, start, end, limit, as_sf)` | Stats NZ Geospatial |
| `eolas_get_mbie(name, start, end, limit, as_sf)` | MBIE |
| `eolas_get_nzta(name, start, end, limit, as_sf)` | Waka Kotahi (NZTA) |
| `eolas_get_msd(name, start, end, limit, as_sf)` | MSD |
| `eolas_get_police(name, start, end, limit, as_sf)` | NZ Police / MoJ |
| `eolas_get_immigration(name, start, end, limit, as_sf)` | Immigration NZ |
| `eolas_get_lris(name, start, end, limit, as_sf)` | Manaaki Whenua / LRIS |
| `eolas_get_geonet(name, start, end, limit, as_sf)` | GeoNet |
| `eolas_get_doc(name, start, end, limit, as_sf)` | DOC (Department of Conservation) |
| `eolas_get_akl_council(name, start, end, limit, as_sf)` | Auckland Council |
| `eolas_get_akl_transport(name, start, end, limit, as_sf)` | Auckland Transport |
| `eolas_get_bay_of_plenty(name, start, end, limit, as_sf)` | Bay of Plenty Councils |
| `eolas_get_charities(name, start, end, limit, as_sf)` | Charities Services |
| `eolas_get_colab_waikato(name, start, end, limit, as_sf)` | Co-Lab Waikato |
| `eolas_get_ecan_canterbury(name, start, end, limit, as_sf)` | ECan / Canterbury |
| `eolas_get_eeca(name, start, end, limit, as_sf)` | EECA (energy use, EV chargers, regional heat demand) |
| `eolas_get_hawkes_bay(name, start, end, limit, as_sf)` | Hawke's Bay Councils |
| `eolas_get_manawatu_whanganui(name, start, end, limit, as_sf)` | Manawatū-Whanganui Councils |
| `eolas_get_napier_whanganui(name, start, end, limit, as_sf)` | Napier + Whanganui |
| `eolas_get_northland(name, start, end, limit, as_sf)` | Northland Councils |
| `eolas_get_otago(name, start, end, limit, as_sf)` | Otago Councils |
| `eolas_get_pharmac(name, start, end, limit, as_sf)` | PHARMAC |
| `eolas_get_southland(name, start, end, limit, as_sf)` | Southland Councils |
| `eolas_get_taranaki(name, start, end, limit, as_sf)` | Taranaki Councils |
| `eolas_get_top_of_south(name, start, end, limit, as_sf)` | Gisborne / Top of South Councils |
| `eolas_get_wellington(name, start, end, limit, as_sf)` | Wellington Region Councils |
| `eolas_get_west_coast(name, start, end, limit, as_sf)` | West Coast (Te Tai o Poutini) |

```r
df <- eolas_get_statsnz("nz_cpi", start = "2015-01-01")
attr(df, "eolas_source")   # "Stats NZ"
```

---

### `eolas_download_bulk(name, freshness = "auto", format = "parquet", path = NULL, ...)`

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

### `eolas_sync_bulk(name, path, format = "parquet", freshness = "auto", ...)`

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

## Plotting

### `eolas_plot(x)`

Quick ggplot2 line chart for a `eolas_dataset`. Returns a `ggplot` object — add further layers with `+`.

```r
eolas_get_statsnz("nz_cpi", start = "2010-01-01") |>
  eolas_plot() +
  ggplot2::labs(y = "Index (base 1000)")
```

**Arguments**

| Name | Type | Description |
|---|---|---|
| `x` | eolas_dataset | A data frame returned by any `eolas_get_*()` function |

**Returns:** `ggplot` object.  
**Requires:** `ggplot2` — `install.packages("ggplot2")`.

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

**With eolas_plot (quick):**

```r
df <- eolas_get_statsnz("nz_cpi", start = "2010-01-01")
eolas_plot(df)
```

**In R Markdown:**

````markdown
```{r setup, include=FALSE}
library(eolas)
eolas_key(Sys.getenv("EOLAS_API_KEY"))
```

```{r cpi-chart, fig.cap="NZ Consumer Price Index"}
eolas_get_statsnz("nz_cpi", start = "2015-01-01") |> eolas_plot()
```
````
