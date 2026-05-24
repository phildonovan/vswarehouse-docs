# R client

The `eolas-data` R package provides a family of functions that wrap the eolas REST API and return **`eolas_dataset` data frames** ready for analysis with base R, dplyr, or ggplot2.

## Installation

```r
remotes::install_github("phildonovan/eolas-r")
```

Requires R 4.1+ and `httr2` 1.0+.

## Authentication

```r
library(eolas)

# Set for the session
eolas_key("your_eolas_key")
```

Or add to `.Renviron` for permanent, session-free access:

```
EOLAS_API_KEY=your_eolas_key
```

## Source-specific helpers

The recommended way to fetch data — the source is encoded in the function name, making code self-documenting and autocomplete-friendly in RStudio:

```r
df  <- eolas_get_statsnz("nz_cpi", start = "2020-01-01")   # Stats NZ
df  <- eolas_get_oecd("nz_gdp_growth")                      # OECD
df  <- eolas_get_rbnz("rbnz_b2_wholesale_rates_monthly")    # RBNZ
df  <- eolas_get_treasury("treasury_fiscal_spending")       # NZ Treasury
gdf <- eolas_get_linz("nz_parcels")   # LINZ (~3M rows — auto-bulks in seconds, no limit needed)
```

Source-specific helpers call `eolas_get()` internally and inherit smart routing: large and geospatial datasets auto-route through the cache+sync path, so `eolas_get_linz("nz_parcels")` returns an `sf` object in seconds — not 15 minutes. The first call emits a one-line message explaining what happened; subsequent calls are silent.

For cases where you want to be explicit, use `eolas_get_local()` (same path, extra options for `cache_dir` / `format` / `freshness`), or pass `mode = "live"` to force the raw Iceberg scan:

```r
# Explicit cache+sync path with extra control
gdf <- eolas_get_local("nz_parcels")
df  <- eolas_get_local("nz_cpi", cache_dir = "/data/eolas", format = "csv_gz")

# Force live scan regardless of dataset size
gdf <- eolas_get("nz_parcels", mode = "live")
```

See [Bulk downloads](../bulk-downloads.md) for the full routing rules and tier comparison.

Each returns a `eolas_dataset` tagged with the source label.

## Discovery

```r
eolas_list()            # all series — tibble (or data.frame)
eolas_list_statsnz()    # Stats NZ only
eolas_list_oecd()       # OECD only
eolas_list_rbnz()       # RBNZ only
eolas_list_treasury()   # NZ Treasury only
eolas_list_linz()       # LINZ only

# Generic filter
eolas_list("Stats NZ")
```

## eolas_dataset

All data-fetching functions return a `eolas_dataset` — a data frame with name and source metadata:

```r
df <- eolas_get_statsnz("nz_cpi", start = "2020-01-01")
df
# eolas_dataset: nz_cpi [Stats NZ]
# 20 rows
#         date period  value
# 1 2020-01-01 2020Q1 1010.0
# ...

attr(df, "eolas_name")    # "nz_cpi"
attr(df, "eolas_source")  # "Stats NZ"
```

`eolas_dataset` is fully compatible with dplyr, ggplot2, and any function that accepts a data frame.

## `eolas_plot()`

One-line ggplot2 chart — returns a `ggplot` object you can customise further with `+`:

```r
eolas_get_statsnz("nz_cpi", start = "2010-01-01") |>
  eolas_plot() +
  ggplot2::labs(y = "Index (base 1000)")
```

Requires `ggplot2`: `install.packages("ggplot2")`.

## `eolas_integration()` (Enterprise plan)

Generate ready-to-run connector configs for popular data-pipeline tools:

```r
# Inspect the generated files without writing anything
result <- eolas_integration("meltano", c("nz_cpi", "nz_gdp_growth"))
names(result$files)            # "meltano.yml", "README.md", ".env.example"
cat(result$files$meltano.yml)

# Or write straight to a directory ready for `meltano install`
eolas_integration(
  "meltano",
  c("nz_cpi", "nz_gdp_growth"),
  output_dir = "./my-pipeline"
)
```

Platforms: `"meltano"`, `"fivetran"`, `"azure-data-factory"`.

This is an Enterprise-plan feature. Non-Enterprise keys see the server's upgrade message surfaced verbatim, with the pricing URL. The gating lives server-side so it's bypass-proof. See <https://eolas.fyi/#pricing>.

## Error handling

```r
tryCatch(
  eolas_get_statsnz("nz_cpi"),
  error = function(e) message("Error: ", conditionMessage(e))
)
```

| Condition | When raised |
|---|---|
| `"Authentication error: ..."` | Invalid or inactive key |
| `"Rate limit reached. ..."` | Daily limit reached |
| `"Not found: ..."` | Series identifier not found |
| `"API error (HTTP ...): ..."` | Unexpected API error |

## Source

[github.com/phildonovan/eolas-r](https://github.com/phildonovan/eolas-r)
