# Stats NZ data via eolas

[Statistics New Zealand](https://www.stats.govt.nz) is the national statistical agency. eolas serves **415 datasets** from Stats NZ — the largest single source in the catalogue — covering everything from quarterly CPI prints to 2023-vintage census meshblock boundaries.

This page is the orientation guide. For specific datasets, browse [eolas.fyi/datasets?source=Stats+NZ](https://eolas.fyi/datasets?source=Stats%20NZ).

---

## What's in the catalogue

Stats NZ datasets fall into seven broad categories. Counts are approximate; check the [live API](https://api.eolas.fyi/v1/datasets) for current totals.

### Macroeconomic indicators

CPI, GDP, unemployment, balance-of-payments. Quarterly series for most. See also the [OECD source guide](oecd.md) — OECD provides the same headline indicators with international comparability.

```python
df = client.statsnz("nz_cpi", start="2020-01-01")
df = client.statsnz("nz_gdp_growth")
```

### Business demography (BDS)

Enterprise counts, business births and deaths, industry breakdowns, geographic units by region and size. ~30 datasets prefixed `bds_`.

```python
df = client.statsnz("bds_enterprises_industry_size")
df = client.statsnz("bds_geographic_units_births_deaths")
```

### Population estimates and projections

National + sub-national estimated resident population, projections to 2048, by age / sex / ethnicity / Māori-descent. Prefixed `popes_` (estimates) and `poppr_` (projections).

```python
df = client.statsnz("popes_erp_components")
df = client.statsnz("poppr_eth_national_2023")
```

### Productivity and earnings

Labour productivity, multifactor productivity, LEED (linked employer-employee data), wages by industry / occupation / region.

```python
df = client.statsnz("prd_labour_productivity_growth")
df = client.statsnz("leed_q_measures_industry")
```

### Justice and social

Charges, convictions, youth justice, household expenditure, household income. Prefixed `jus_`, `hes_` (household expenditure), `inc_` (income).

```python
df = client.statsnz("jus_charges_by_offence_fiscal")
df = client.statsnz("hes_expenditure_category")
```

### Iwi statistics (2018 census)

Iwi affiliation, iwi grouping counts for the Māori-descent population. 20+ datasets prefixed `iwi18_`. Note: 2023 census iwi frame not yet published; 2018 is current.

```python
df = client.statsnz("nz_population_estimates")
```

### Geospatial boundaries + census

About **~230 of the 415 Stats NZ datasets are geospatial** — census boundaries at every vintage Stats NZ has published, plus the census + population data already tabulated against those boundaries. All ship with `geometry_wkt` and load as `sf` / `GeoDataFrame` when the geo extras are installed.

The set splits into three layers:

**Boundary geometries.** Pure polygons keyed to a vintage. Used to put data on a map.

| Geography | 2023 vintage | 2018 vintage | 2013 vintage |
|---|---|---|---|
| Meshblock (~50k blocks) | `nz_meshblock_2023` | `nz_meshblock_2018` | `nz_meshblock_2013` |
| SA1 (~30k blocks) | `nz_statistical_area_1_2023` | `nz_statistical_area_1_2018` | — |
| SA2 (~2k blocks) | `nz_statistical_area_2_2023` | `nz_statistical_area_2_2018` | `nz_statistical_area_2_2013` |
| SA3 | `nz_statistical_area_3_2023` | — | — |
| Territorial authority | `nz_territorial_authority_2023` | `nz_territorial_authority_2018` | `nz_territorial_authority_2013` |
| Regional council | `nz_regional_council_2023` | `nz_regional_council_2018` | — |
| Urban / rural | `nz_urban_rural_2023` | `nz_urban_rural_2018` | — |
| Urban area | `nz_urban_area_2023` | `nz_urban_area_2018` | — |
| Ward | `nz_ward_2025` | `nz_ward_2020` | — |
| Community board | `nz_community_board_2025` | `nz_community_board_2020` | — |
| Constituency / iwi / electoral | available per-vintage — search the catalogue | | |

**Census tables, vintaged against boundaries.** The 2023 + 2018 + 2013 censuses each have ~15-20 datasets where the underlying census records have already been aggregated to a boundary geography. Use these for "show me a map of X by SA2" without doing the boundary join yourself.

```python
# 2023 census usually-resident population, by SA2, ready to map
pop = client.statsnz("census_2023_pop_change_sa2", as_sf=True)
pop.plot(column="usually_resident_2023", legend=True, cmap="viridis")
```

Common 2018 datasets: `census_2018_dwelling_sa1`, `census_2018_household_sa1`, `census_2018_individual_sa1_p1`/`p2`/`p3a`/`p3b` (individual variables split across four parts due to row width), `census_2018_pop_age_sa2`, `census_2018_rc_urban_accessibility`, `census_2018_electoral_mb_2020`.

2023 has 18 equivalent tables; 2013 has 3 (the older census results are mostly available via SDMX time-series in the existing tables above).

**Population estimates against boundaries (post-census).** Stats NZ publishes Estimated Resident Population (ERP) updates between censuses. The `popes_*` and `poppr_*` tables come pre-tabulated against modern boundaries:

```python
# Sub-national population estimates by SA2 (current frame)
sa2_pop = client.statsnz("popes_sub_rc_sa2")
# Projected population by SA2 to 2048 (2023 base)
proj = client.statsnz("poppr_sub_sa23_2023")
```

Boundary vintages matter — see the [vintaged columns convention](https://github.com/phildonovan/eolas/blob/main/docs/data-conventions.md#13-vintaged-concepts-carry-the-year-in-the-column-name) for joining historical census data to current geographies. Don't assume a meshblock or SA code from the 2013 vintage maps cleanly to 2018 or 2023 — Stats NZ redraws boundaries each census, so use the matched vintage on both sides of a join.

---

## Refresh schedule

Most Stats NZ pipelines run **weekly, Wednesday morning NZ time**. Stats NZ itself publishes on its own schedule — CPI is quarterly, business demography annual, population estimates quarterly. Our refresh fires once a week regardless; if the upstream hasn't changed, the data is identical to last week.

You can check the freshness of any specific dataset via the metadata endpoint:

```python
meta = client.info("nz_cpi")
meta["last_refreshed_at"]        # our last pull
meta["source_last_modified_at"]  # when Stats NZ last touched the file (where capturable)
```

---

## License

All Stats NZ data is published under **[Creative Commons Attribution 4.0 (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/)**. You can use it commercially, derive from it, and redistribute — with attribution. eolas serves the data unchanged; attribution requirements transfer to you when you redistribute.

Recommended attribution: *"Source: Stats NZ, served via eolas (eolas.fyi). CC-BY 4.0."*

---

## Common patterns

### CPI over time

=== "Python"

    ```python
    import matplotlib.pyplot as plt

    cpi = client.statsnz("nz_cpi", start="2010-01-01")
    cpi.plot(x="date", y="value", title="NZ CPI", figsize=(10, 4))
    plt.show()
    ```

=== "R"

    ```r
    library(ggplot2)

    cpi <- eolas_get_statsnz("nz_cpi", start = "2010-01-01")
    ggplot(cpi, aes(date, value)) +
      geom_line() +
      labs(title = "NZ CPI", y = "Index")
    ```

### Census boundary + value join

The classic geo-demographic pattern: load boundaries, join your own data:

=== "Python"

    ```python
    # 2023 SA2 boundaries (about 2,000 polygons, fits in Free tier)
    sa2 = client.statsnz_geo("nz_statistical_area_2_2023", as_sf=True)

    # Your own analysis data (with sa2_code_2023 column)
    import pandas as pd
    survey = pd.read_csv("my_survey.csv")

    merged = sa2.merge(survey, on="sa2_code_2023")
    merged.plot(column="my_metric", legend=True, cmap="viridis")
    ```

=== "R"

    ```r
    library(sf)
    library(ggplot2)

    sa2 <- eolas_get_statsnz_geo("nz_statistical_area_2_2023", as_sf = TRUE)
    survey <- read.csv("my_survey.csv")

    merged <- merge(sa2, survey, by = "sa2_code_2023")
    ggplot(merged) + geom_sf(aes(fill = my_metric))
    ```

### Discovering Stats NZ datasets

```bash
# CLI
eolas datasets list --source "Stats NZ" --search population

# Python
[d for d in client.list("Stats NZ") if "population" in d["name"]]

# R
sn <- eolas_list_statsnz()
sn[grepl("population", sn$name), ]
```

---

## Pipeline use

Stats NZ datasets are **full-refresh** on sync — the upstream SDMX source replaces the whole table on each publish, so eolas can't emit incremental rows. When you call `eolas sync` on a Stats NZ dataset, it checks whether the server snapshot has changed; if not, no bytes are transferred. If the snapshot is new, the full table is re-downloaded and replaces the previous file.

In practice, CPI and GDP tables are 1–5 MB — a weekly re-download is negligible. The geospatial boundary tables (meshblocks, SA2s) can be larger, but they change infrequently; most weeks the sync call returns "unchanged".

=== "Python"

    ```python
    from eolas_data import Client

    client = Client("your_eolas_key")

    # Sync once; subsequent calls are no-ops until Stats NZ publishes a new revision
    result = client.sync("nz_cpi", library_dir="/data/nz-warehouse")
    print(result.status)  # "snapshot_full" (first time) or "unchanged"

    # Read from library — zero network traffic after first sync
    import pyarrow.parquet as pq
    df = pq.ParquetDataset("/data/nz-warehouse/nz_cpi").read().to_pandas()
    ```

=== "R"

    ```r
    library(eolas)

    result <- eolas_sync("nz_cpi", library_dir = "/data/nz-warehouse")
    result$status  # "snapshot_full" or "unchanged"

    library(arrow)
    df <- collect(open_dataset("/data/nz-warehouse/nz_cpi"))
    ```

=== "CLI"

    ```bash
    eolas sync nz_cpi --library /data/nz-warehouse
    # → snapshot_full (2.1 MB)  — first run
    # → unchanged (snapshot 7041234…)  — next run, nothing published
    ```

See the [Sync guide](../sync-guide.md) for cron, Airflow, and dbt integration recipes.

---

## Source-specific notes

- **SDMX origin**: most Stats NZ time-series come from their SDMX API. Multi-dimensional series (e.g. CPI by quarter × group) are flattened into a long-format `(date, period, value, ...)` table. The `period` column carries the original SDMX period code (e.g. `2024Q1`).
- **Vintage-suffixed columns**: any geospatial column drawn from the 2023 census frame carries `_2023` (e.g. `meshblock_id_2023`, `sa2_code_2023`). 2018-frame columns carry `_2018`. Don't assume codes match across vintages — boundaries are redrawn every 5 years.
- **Suppressed counts**: for privacy, Stats NZ rounds many small-count cells to base-3 and suppresses cells below threshold (typically `<6`). These appear as `null` with a companion `_suppressed=true` flag in the response.
- **Provisional vs final**: some boundary tables exist in both forms (e.g. `nz_ward_2025_v2_provisional` and `nz_ward_2025`). The provisional version is usually the working draft Stats NZ released for public consultation; the un-suffixed version is the final.

---

## Where to find more

- **All Stats NZ datasets on eolas**: [eolas.fyi/datasets?source=Stats+NZ](https://eolas.fyi/datasets?source=Stats%20NZ)
- **Stats NZ's own data portal**: [www.stats.govt.nz](https://www.stats.govt.nz) — SDMX API, downloads, methodology
- **Stats NZ Geospatial (Datafinder)**: [datafinder.stats.govt.nz](https://datafinder.stats.govt.nz) — the WFS/Koordinates source for our boundary tables
- **Open data licence summary**: [data.govt.nz/about/open-data-nzgoal](https://data.govt.nz/about/open-data-nzgoal)

## Related

- [OECD source guide](oecd.md) — international-comparable indicators
- [Examples](../examples/index.md) — worked code recipes
- [Authentication](../authentication.md) — how to set your API key
