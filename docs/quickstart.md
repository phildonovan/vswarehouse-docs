# Getting started

## 1. Get an API key

Sign up at [api.eolas.fyi](https://api.eolas.fyi/signup). Your key will start with `vs_`.

## 2. Install the client

=== "Python"

    ```bash
    pip install eolas-data
    ```

=== "R"

    ```r
    remotes::install_github("phildonovan/eolas-r")
    ```

=== "CLI"

    ```bash
    pip install eolas-data[cli]
    ```

    Installs `eolas` on PATH. Same install on Linux, macOS, and Windows. See the [CLI reference](cli/index.md) for the full command list.

## 3. Set your key

=== "Python"

    Pass it directly:

    ```python
    from eolas_data import Client
    client = Client("vs_your_key")
    ```

    Or set the environment variable and omit the argument:

    ```bash
    export EOLAS_API_KEY=vs_your_key
    ```

    ```python
    client = Client()  # reads EOLAS_API_KEY automatically
    ```

=== "R"

    Call `eolas_key()` once per session:

    ```r
    library(eolas)
    eolas_key("vs_your_key")
    ```

    Or add it to your `.Renviron` for permanent access:

    ```
    EOLAS_API_KEY=vs_your_key
    ```

=== "CLI"

    One-time interactive setup (writes `~/.eolas/config.json` with mode 0600):

    ```bash
    eolas auth set-key
    # Prompts: API key: vs_your_key
    ```

    Or use the env var — overrides the config file:

    ```bash
    export EOLAS_API_KEY=vs_your_key
    ```

    Check status any time:

    ```bash
    eolas auth status
    # key:    vs_yourk…
    # source: ~/.eolas/config.json
    ```

## 4. Fetch your first series

Use source-specific helpers so your code is self-documenting:

=== "Python"

    ```python
    # Stats NZ
    df = client.statsnz("nz_cpi", start="2020-01-01")

    # OECD
    df = client.oecd("nz_gdp")

    # NZ Treasury
    df = client.treasury("treasury_fiscal_spending")

    # Manaaki Whenua / LRIS (land cover — returns a GeoDataFrame when geopandas is installed)
    gdf = client.lris("lcdb_v6_mainland")

    # GeoNet (recent NZ earthquakes — rolling ~100 events, MMI>=3)
    quakes = client.geonet("geonet_quakes_recent")

    # DOC (Department of Conservation — returns a GeoDataFrame when geopandas is installed)
    huts = client.doc("doc_huts")   # 1,429 DOC huts across NZ

    # PHARMAC (NZ pharmaceutical schedule — 840k rows of subsidy history back to 2006)
    schedule = client.pharmac("pharmac_schedule")          # current month's funded medicines
    history  = client.pharmac("pharmac_schedule_history")  # 2006-present archive, ~512k rows

    # EECA (energy use, EV chargers, regional heat demand)
    chargers = client.eeca("eeca_ev_chargers_public")      # 2,050 public EV chargers (point geometry)
    energy   = client.eeca("eeca_energy_end_use")          # NZ energy by sector x fuel x end-use x year
    ev_ta    = client.eeca("eeca_ev_metrics_district")     # EV penetration by territorial authority

    print(df)
    # Dataset: nz_cpi [Stats NZ]
    # 20 rows
    #          date  period   value
    # 0  2020-01-01  2020Q1  1010.0
    # ...
    ```

=== "R"

    ```r
    # Stats NZ
    df <- eolas_get_statsnz("nz_cpi", start = "2020-01-01")

    # OECD
    df <- eolas_get_oecd("nz_gdp")

    # NZ Treasury
    df <- eolas_get_treasury("treasury_fiscal_spending")

    # Manaaki Whenua / LRIS (land cover — returns an sf object when the sf package is installed)
    gdf <- eolas_get_lris("lcdb_v6_mainland")

    # GeoNet (recent NZ earthquakes — rolling ~100 events, MMI>=3)
    quakes <- eolas_get_geonet("geonet_quakes_recent")

    # DOC (Department of Conservation — returns an sf object when the sf package is installed)
    huts <- eolas_get_doc("doc_huts")   # 1,429 DOC huts across NZ

    # PHARMAC (NZ pharmaceutical schedule — 840k rows of subsidy history back to 2006)
    schedule <- eolas_get_pharmac("pharmac_schedule")          # current month's funded medicines
    history  <- eolas_get_pharmac("pharmac_schedule_history")  # 2006-present archive, ~512k rows

    # EECA (energy use, EV chargers, regional heat demand)
    chargers <- eolas_get_eeca("eeca_ev_chargers_public")      # 2,050 public EV chargers (Point geometry)
    energy   <- eolas_get_eeca("eeca_energy_end_use")          # NZ energy by sector x fuel x end-use x year
    ev_ta    <- eolas_get_eeca("eeca_ev_metrics_district")     # EV penetration by territorial authority

    df
    # eolas_dataset: nz_cpi [Stats NZ]
    # 20 rows
    #         date period  value
    # 1 2020-01-01 2020Q1 1010.0
    # ...
    ```

=== "CLI"

    ```bash
    # CSV to stdout — pipe into anything
    eolas get nz_cpi --start 2020-01-01 --format csv > cpi.csv

    # JSON streamed to jq
    eolas get nz_cpi --format json | jq '.[].value'

    # Parquet straight to a file
    eolas get sa2_2023 --format parquet --out sa2.parquet
    ```

    Output auto-detects piping: rich tables in an interactive terminal, NDJSON / CSV when stdout is redirected. Pass `--json` to force NDJSON.

## 5. Access regional council data

Each of New Zealand's regional and city/district council groups has a dedicated source helper, making it easy to discover and fetch geospatial planning, hazard, and environmental layers by region.

=== "Python"

    ```python
    # Auckland
    gdf = client.akl_council("akc_significant_ecological_areas_overlay")
    gdf = client.akl_transport("akt_cycle_facility_network")

    # Bay of Plenty
    gdf = client.bay_of_plenty("boprc_historic_flood_extents")

    # Canterbury
    gdf = client.ecan_canterbury("ecan_liquefaction_susceptibility_final")

    # Wellington
    gdf = client.wellington("wcc_flood_hazard_operative")

    # Otago
    gdf = client.otago("orc_otago_land_use_2024")

    # Discover all datasets in a region
    client.list("Auckland Council")          # returns list of dicts
    client.list("Wellington Region Councils")
    ```

=== "R"

    ```r
    # Auckland
    gdf <- eolas_get_akl_council("akc_significant_ecological_areas_overlay")
    gdf <- eolas_get_akl_transport("akt_cycle_facility_network")

    # Bay of Plenty
    gdf <- eolas_get_bay_of_plenty("boprc_historic_flood_extents")

    # Canterbury
    gdf <- eolas_get_ecan_canterbury("ecan_liquefaction_susceptibility_final")

    # Wellington
    gdf <- eolas_get_wellington("wcc_flood_hazard_operative")

    # Otago
    gdf <- eolas_get_otago("orc_otago_land_use_2024")

    # Discover all datasets in a region
    eolas_list_akl_council()
    eolas_list_wellington()
    ```

Available regional helpers: `akl_council`, `akl_transport`, `bay_of_plenty`, `charities`, `colab_waikato`, `ecan_canterbury`, `hawkes_bay`, `manawatu_whanganui`, `napier_whanganui`, `northland`, `otago`, `southland`, `taranaki`, `top_of_south`, `wellington`, `west_coast`. See the [Python reference](python/reference.md) or [R reference](r/reference.md) for the full list.

---

## 6. Plot it

=== "Python"

    ```python
    df = client.statsnz("nz_cpi", start="2010-01-01")
    df.plot(x="date", y="value", title="NZ CPI")   # pandas .plot — returns Axes
    ```

=== "R"

    ```r
    library(ggplot2)
    df <- eolas_get_statsnz("nz_cpi", start = "2010-01-01")
    ggplot(df, aes(date, value)) + geom_line() + labs(title = "NZ CPI")
    ```

## 7. Browse available series

=== "Python"

    ```python
    client.list()              # all series
    client.list("Stats NZ")   # Stats NZ only
    ```

=== "R"

    ```r
    eolas_list()            # all series
    eolas_list_statsnz()    # Stats NZ only
    eolas_list_oecd()       # OECD only
    eolas_list_treasury()   # NZ Treasury only
    ```

=== "CLI"

    ```bash
    eolas datasets list                           # rich table in TTY, NDJSON when piped
    eolas datasets list --source "Stats NZ"
    eolas datasets list --search cpi --json | jq '.[].name'
    eolas datasets info nz_cpi
    eolas datasets preview nz_cpi --limit 5
    ```

You can also browse interactively at [eolas.fyi/datasets](https://eolas.fyi/datasets).

---

!!! tip "Rate limits"
    Free keys allow **10 requests per month** at up to 50,000 rows per request. [Pro](https://eolas.fyi/#pricing) ($49/month) is unlimited requests and unlimited rows. Enterprise adds Snowflake share + connector scaffolding + SLA.
