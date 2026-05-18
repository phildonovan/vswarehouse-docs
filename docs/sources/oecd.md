# OECD data via eolas

The [OECD](https://data-explorer.oecd.org) publishes standardised macroeconomic indicators for its 38 member economies, harmonised so they're directly comparable across countries. eolas serves five NZ indicators from the OECD **Key Economic Indicators (KEI)** dataflow — chosen because they're the headline series most NZ analysts cross-reference internationally.

For deeper OECD coverage (other countries, non-KEI dataflows), see the [external links](#where-to-find-more) at the bottom.

---

## What's in the catalogue

| Dataset | Frequency | Description |
|---|---|---|
| `nz_cpi` | Quarterly | Consumer Price Index, base 100. OECD-harmonised — directly comparable to other OECD CPIs. |
| `nz_gdp_growth` | Quarterly | Real GDP growth, percent change quarter-on-quarter. |
| `nz_unemployment` | Quarterly | Harmonised unemployment rate (15-64), percent of labour force. |
| `nz_interest_short` | Monthly | Short-term interest rate, typically the 3-month inter-bank rate. |
| `nz_interest_long` | Monthly | Long-term interest rate, typically 10-year government bond yield. |

These are all part of the OECD's KEI dataflow (`OECD.SDD.STES,DSD_KEI@DF_KEI`). The same dataflow has equivalents for every OECD member — so any analysis using these five datasets can be replicated for other countries by changing the country code in the underlying SDMX query.

---

## Refresh schedule

Weekly, Wednesday morning NZ time. The OECD itself updates KEI on its own monthly / quarterly cadence; our weekly refresh catches new releases within seven days of publication.

```python
meta = client.info("nz_cpi")
meta["last_refreshed_at"]
meta["source_last_modified_at"]   # OECD's own publish timestamp where available
```

---

## License

OECD data is **not** CC-BY. The [OECD Terms and Conditions](https://www.oecd.org/termsandconditions/) permit non-commercial use and academic / research / journalism use with attribution, but **prohibit commercial redistribution** without a separate licence agreement.

What this means in practice:

- **Free analysis, charts, blog posts**: fine, attribute OECD.
- **Charging customers for OECD data**: not fine without an OECD agreement.
- **eolas's stance**: we serve OECD data on the Free and Pro tiers as a convenience for analytical use. **Enterprise customers** are excluded from automated OECD redistribution — if you're building a paid product on top of OECD data, contact us so we can structure the licence appropriately, or query OECD's own API directly.

Recommended attribution: *"Source: OECD, via eolas (eolas.fyi). © OECD."*

---

## Common patterns

### NZ CPI vs OECD average

The whole point of using OECD data is cross-country comparability. Here, NZ CPI alone:

=== "Python"

    ```python
    import matplotlib.pyplot as plt

    cpi = client.oecd("nz_cpi", start="2010-01-01")
    cpi.plot(x="date", y="value", title="NZ CPI (OECD harmonised)", figsize=(10, 4))
    plt.show()
    ```

=== "R"

    ```r
    library(ggplot2)

    cpi <- eolas_get_oecd("nz_cpi", start = "2010-01-01")
    ggplot(cpi, aes(date, value)) +
      geom_line() +
      labs(title = "NZ CPI (OECD harmonised)", y = "Index, 2015=100")
    ```

For multi-country comparisons (NZ vs Australia vs US), you currently need to query the OECD KEI dataflow directly — that's on the eolas roadmap as a separate `client.oecd_compare()` helper.

### All four interest-rate / GDP / unemployment series at once

=== "Python"

    ```python
    indicators = ["nz_cpi", "nz_gdp_growth", "nz_unemployment", "nz_interest_short"]
    dfs = {name: client.oecd(name, start="2010-01-01") for name in indicators}

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (name, df) in zip(axes.flatten(), dfs.items()):
        df.plot(x="date", y="value", ax=ax, title=name, legend=False)
    plt.tight_layout()
    plt.show()
    ```

=== "R"

    ```r
    library(patchwork)

    indicators <- c("nz_cpi", "nz_gdp_growth", "nz_unemployment", "nz_interest_short")
    plots <- lapply(indicators, function(name) {
      df <- eolas_get_oecd(name, start = "2010-01-01")
      ggplot(df, aes(date, value)) + geom_line() + labs(title = name)
    })
    Reduce(`+`, plots) + plot_layout(ncol = 2)
    ```

---

## Source-specific notes

- **Vintage / revision**: OECD revises its data with new vintages — what was Q1 2024 CPI yesterday may be slightly different tomorrow as Stats NZ submits revised inputs. We pull the latest revision each refresh; if you need a frozen-in-time snapshot, archive your local copy.
- **Country code**: every OECD series is internally keyed by an ISO country code (`NZL` for New Zealand). The five datasets we expose are pre-filtered to NZ; the country code is in the metadata but not in column names.
- **OECD's KEI vs other OECD products**: KEI is the harmonised, comparable, monthly/quarterly indicator set. OECD also publishes annual data (national accounts, social indicators), structural metrics (labour, education), and policy indicators — none of those are currently in eolas. Roadmap if there's demand.
- **No Stats NZ-OECD divergence within reason**: OECD's NZ CPI mostly tracks Stats NZ's published CPI, but small differences appear due to OECD harmonisation rules (e.g. owner-occupied housing treatment). Use OECD when comparing to other countries; use Stats NZ for the NZ-domestic narrative.

---

## Where to find more

- **OECD datasets on eolas**: [eolas.fyi/datasets?source=OECD](https://eolas.fyi/datasets?source=OECD)
- **OECD's own data explorer**: [data-explorer.oecd.org](https://data-explorer.oecd.org)
- **OECD Terms & Conditions**: [oecd.org/termsandconditions](https://www.oecd.org/termsandconditions/)
- **SDMX-JSON spec** (if you want to bypass eolas and query OECD directly): [sdmx.org](https://sdmx.org)

## Related

- [Stats NZ source guide](statsnz.md) — for the NZ-domestic equivalents
- [Examples](../examples/index.md) — worked code recipes
