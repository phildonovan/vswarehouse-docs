# RBNZ data via eolas

The [Reserve Bank of New Zealand](https://www.rbnz.govt.nz/statistics) publishes the canonical NZ money-and-banking statistics. eolas serves **33 datasets** from RBNZ, organised by the RBNZ's own letter-numbered table system (`B1`, `B2`, …, `C` series, `M` series).

If you do anything involving mortgages, exchange rates, NZ monetary aggregates, or balance-of-payments — RBNZ is the source.

---

## What's in the catalogue

The 33 datasets cover RBNZ's statistical-release tables. The naming convention is `rbnz_<table_code>_<topic>`, e.g. `rbnz_b1_exchange_rates_daily`.

### Interest rates

| Dataset | Description |
|---|---|
| `rbnz_b1_exchange_rates_daily` | Daily TWI and bilateral exchange rates (NZD vs major currencies). |
| `rbnz_b1_exchange_rates_monthly` | Monthly averages of the same. |
| `rbnz_b2_wholesale_rates_daily` | Wholesale interbank rates — OCR, 90-day bank bill, swap rates. |
| `rbnz_b2_wholesale_rates_monthly` | Monthly averages. |
| `rbnz_b3_retail_rates` | Retail / household rates (term deposits, lending). |
| `rbnz_b20_mortgage_rates` | Mortgage rates by fixed term and lender. |

### Money supply, credit, banking

| Dataset | Description |
|---|---|
| `rbnz_c5_money_supply` | M1 / M2 / M3 monetary aggregates. |
| `rbnz_c6_credit_aggregates` | Lending to households, business, agriculture. |
| `rbnz_c12_registered_banks_balance_sheet` | Aggregate bank balance sheet. |
| `rbnz_c31_new_mortgage_lending` | New mortgage lending by LVR band — useful for housing-market analysis. |

### Macro + external

| Dataset | Description |
|---|---|
| `rbnz_m7_balance_of_payments` | Current account, capital account, NIIP. |
| `rbnz_m8_overseas_trade` | Goods and services exports / imports. |
| `rbnz_m9_labour_market` | Employment, wages, productivity proxies (RBNZ's view; differs slightly from Stats NZ). |

For the full list, browse [eolas.fyi/datasets?source=RBNZ](https://eolas.fyi/datasets?source=RBNZ).

---

## Refresh schedule

Weekly, Wednesday morning NZ time. RBNZ itself publishes most tables monthly or weekly — daily exchange rates the major exception. The weekly refresh catches new monthly releases within 5-12 days of RBNZ publishing them.

---

## License

All RBNZ statistical data is published under **[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)** per the [RBNZ Open Data policy](https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/about-us/copyright-statement.pdf). Commercial use is fine; attribution is required.

Recommended attribution: *"Source: Reserve Bank of New Zealand, via eolas (eolas.fyi). CC-BY 4.0."*

---

## Common patterns

### OCR + 90-day rate

The two interest rates every analyst tracks:

=== "Python"

    ```python
    import pandas as pd
    import matplotlib.pyplot as plt

    rates = client.rbnz("rbnz_b2_wholesale_rates_daily", start="2018-01-01")

    # rates has columns: date, series, value — where series includes "OCR", "90day", etc.
    pivoted = rates.pivot(index="date", columns="series", values="value")
    pivoted[["OCR", "90day"]].plot(figsize=(10, 4), title="OCR vs 90-day bank bill")
    plt.show()
    ```

=== "R"

    ```r
    library(tidyr)
    library(ggplot2)

    rates <- eolas_get_rbnz("rbnz_b2_wholesale_rates_daily", start = "2018-01-01")
    wide  <- pivot_wider(rates, names_from = series, values_from = value)

    ggplot(wide, aes(date)) +
      geom_line(aes(y = OCR,   colour = "OCR")) +
      geom_line(aes(y = `90day`, colour = "90-day")) +
      labs(y = "Rate (%)", colour = NULL)
    ```

### Mortgage rates by term

=== "Python"

    ```python
    mort = client.rbnz("rbnz_b20_mortgage_rates", start="2020-01-01")
    # Columns include date, term, value (rate %)

    fixed_2yr = mort[mort["term"] == "2 years fixed"]
    fixed_2yr.plot(x="date", y="value", title="NZ 2-year fixed mortgage rate")
    ```

### LVR composition of new lending

=== "Python"

    ```python
    lvr = client.rbnz("rbnz_c31_new_mortgage_lending", start="2018-01-01")
    # Shows the >80% LVR share — the RBNZ's macroprudential tool target
    high_lvr = lvr[lvr["lvr_band"] == ">80%"]
    high_lvr.plot(x="date", y="value", title="High-LVR share of new mortgage lending (%)")
    ```

---

## Pipeline use

RBNZ datasets are **full-refresh** on sync — each RBNZ release replaces the full table, so delta fetches are not applicable. Most RBNZ tables are small (exchange-rate series are a few hundred KB; the larger balance-sheet tables top out around 5 MB), so full re-downloads are fast.

When you call `eolas sync` on an RBNZ dataset, it returns "unchanged" in weeks where RBNZ hasn't published a new release — zero bytes transferred. When a new release lands, the full table downloads and replaces the previous file.

=== "Python"

    ```python
    result = client.sync("rbnz_b1_exchange_rates_daily", library_dir="/data/nz-warehouse")
    print(result.status)  # "snapshot_full" (first run) or "unchanged"

    import pyarrow.parquet as pq
    df = pq.ParquetDataset("/data/nz-warehouse/rbnz_b1_exchange_rates_daily").read().to_pandas()
    ```

=== "R"

    ```r
    result <- eolas_sync("rbnz_b1_exchange_rates_daily", library_dir = "/data/nz-warehouse")
    result$status  # "snapshot_full" or "unchanged"
    ```

=== "CLI"

    ```bash
    # Sync all RBNZ tables at once (after syncing them individually first)
    eolas sync --library /data/nz-warehouse --all
    ```

See the [Sync guide](../sync-guide.md) for cron and Airflow recipes.

---

## Source-specific notes

- **Naming**: dataset names follow `rbnz_<rbnz_table_code>_<topic>` so they cross-reference cleanly to RBNZ's own [Statistics page](https://www.rbnz.govt.nz/statistics) — if you read a "B2" release on RBNZ's website, the eolas dataset is `rbnz_b2_*`.
- **Long format**: most tables are emitted as `(date, series, value)` long-format rather than wide. Pivot to wide for charting (Python: `df.pivot()`, R: `tidyr::pivot_wider()`).
- **Cloudflare**: RBNZ's site is Cloudflare-protected. Our pipeline uses residential-proxy fallback to fetch reliably; you don't see this — just clean data. If you're scraping RBNZ directly without proxies you'll see 403s from Fargate-IP-range addresses.
- **Recent retirement**: RBNZ retired 8 legacy tables in May 2026 (404s on the source). We removed those from our schedule rather than report broken pipelines; if you have older code referencing them, the dataset names will 404 from us too.

---

## Where to find more

- **RBNZ datasets on eolas**: [eolas.fyi/datasets?source=RBNZ](https://eolas.fyi/datasets?source=RBNZ)
- **RBNZ's own statistics page**: [www.rbnz.govt.nz/statistics](https://www.rbnz.govt.nz/statistics) — original Excel tables, methodology notes
- **RBNZ OCR decisions**: [www.rbnz.govt.nz/monetary-policy/about-monetary-policy/ocr-decisions](https://www.rbnz.govt.nz/monetary-policy/about-monetary-policy/ocr-decisions)

## Related

- [Stats NZ source guide](statsnz.md) — for the labour, GDP, BOP series Stats NZ publishes (overlaps with RBNZ's M-series)
- [Examples](../examples/index.md) — worked code recipes
