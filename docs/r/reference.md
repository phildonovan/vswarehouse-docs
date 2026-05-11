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
**Note:** If `EOLAS_API_KEY` is set in the environment, you can skip this call entirely.

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
| `limit` | integer \| NULL | `NULL` | Max rows. `NULL` requests the full dataset. Free / Starter plans are capped server-side at 50,000 rows; Pro is unlimited. |
| `as_sf` | logical \| NULL | `NULL` | Return an `sf` object for geospatial datasets. `NULL` auto-converts when geometry is present and the `sf` package is installed. `TRUE` forces conversion (errors if missing). `FALSE` keeps the raw `geometry_wkt` string column. Install with `install.packages("sf")`. |

**Returns:** `eolas_dataset` data frame, or an `sf` object when geometry is present and conversion is enabled.

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

```r
df <- eolas_get_statsnz("nz_cpi", start = "2015-01-01")
attr(df, "eolas_source")   # "Stats NZ"
```

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
