# Immigration NZ data via eolas

[Immigration New Zealand](https://www.immigration.govt.nz) (INZ, part of MBIE) administers visa decisions and operates the [Migration Data Explorer](https://www.immigration.govt.nz/about-us/research-and-statistics) — the canonical public dataset for who's getting which visas, by which category, over time. eolas serves **16 datasets** from Immigration NZ — 13 from INZ's GitHub-published `.rda` files (the same data behind the Migration Data Explorer Shiny app) and 3 from MBIE's monthly RSE (Recognised Seasonal Employer) statistics workbook.

If you're doing migration analysis, labour-market forecasting that depends on visa flows, or RSE-scheme research — this is the source.

---

## What's in the catalogue

### Residence

| Dataset | Description |
|---|---|
| `immigration_residence_decisions` | Residence visa decisions (approved / declined / withdrawn) over time. |
| `immigration_residence_occupations` | Residence approvals by stated occupation. |
| `immigration_residence_apps_accepted` | Applications accepted (started processing). |
| `immigration_residence_apps_on_hand` | Applications in the queue at each month-end. |
| `immigration_returning_residence_decisions` | RRV (Returning Resident Visa) decisions. |

### Visitor

| Dataset | Description |
|---|---|
| `immigration_visitor_decisions` | Visitor visa decisions by source country + visa subtype. |

### Work

| Dataset | Description |
|---|---|
| `immigration_work_decisions` | Work visa decisions (essential skills, accredited employer, etc.). |
| `immigration_work_occupations` | Work approvals by stated occupation. |

### Student

| Dataset | Description |
|---|---|
| `immigration_student_decisions` | Student visa decisions. |
| `immigration_student_first_time` | First-time student visas (excludes renewals). |

### Arrivals / departures

| Dataset | Description |
|---|---|
| `immigration_arrivals_by_visa` | Border arrival counts segmented by visa type. |
| `immigration_departures_by_visa` | Departures by visa type. |
| `immigration_limited_purpose_decisions` | LPV (Limited Purpose Visa) decisions — niche but useful for specific-event tracking. |

### RSE (seasonal worker scheme)

The Recognised Seasonal Employer scheme brings workers from Pacific Island nations for horticulture/viticulture seasonal work. eolas serves three RSE statistics streams from MBIE's monthly published workbook:

| Dataset | Description |
|---|---|
| `immigration_rse_onshore_by_region_sex` | Current RSE workers on-shore, by region × nationality × gender (snapshot). |
| `immigration_rse_onshore_by_year_sex` | Same breakdown but as a time series back to 2011/12 (~4,500 rows). |
| `immigration_rse_atr_processing_times` | Monthly P50 and P90 processing times for Agreement to Recruit applications. **SCD2 stream** — each refresh appends a new month rather than overwriting, so this dataset accumulates a real time series. |

---

## Refresh schedule

Weekly, Wednesday morning NZ time. The RDA `.rda` files on the [joh024/migration_data_explorer_public](https://github.com/joh024/migration_data_explorer_public) GitHub repo update monthly (after INZ's monthly data drop); our weekly refresh catches new releases promptly. The RSE workbook also refreshes monthly.

```python
meta = client.info("immigration_residence_decisions")
meta["last_refreshed_at"]
meta["source_last_modified_at"]
```

---

## License

All Immigration NZ data is published under **[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)**. Commercial use is fine; attribution required.

Recommended attribution: *"Source: Immigration NZ, served via eolas (eolas.fyi). CC-BY 4.0."*

---

## Common patterns

### Residence-visa flow over time

=== "Python"

    ```python
    import matplotlib.pyplot as plt

    res = client.immigration("immigration_residence_decisions", start="2018-01-01")
    # res has columns: Date, Count, plus several classifier factors

    # Total residence approvals over time
    by_date = res[res["Decision"] == "Approved"].groupby("Date")["Count"].sum().reset_index()
    by_date.plot(x="Date", y="Count", title="NZ residence approvals (monthly)")
    plt.show()
    ```

=== "R"

    ```r
    library(dplyr)
    library(ggplot2)

    res <- eolas_get_immigration("immigration_residence_decisions", start = "2018-01-01")
    by_date <- res |>
      filter(Decision == "Approved") |>
      group_by(Date) |>
      summarise(Count = sum(Count))

    ggplot(by_date, aes(Date, Count)) + geom_line() +
      labs(title = "NZ residence approvals (monthly)")
    ```

### Top source countries for visitor visas

=== "Python"

    ```python
    visitor = client.immigration("immigration_visitor_decisions", start="2022-01-01")
    top = (visitor[visitor["Decision"] == "Approved"]
              .groupby("Country")["Count"].sum()
              .sort_values(ascending=False).head(10))
    top.plot.barh(title="Top 10 source countries — visitor visa approvals (2022+)")
    ```

### RSE workforce composition

=== "Python"

    ```python
    rse = client.immigration("immigration_rse_onshore_by_region_sex")
    # 156 rows: Region × Nationality × Sex × Count + Suppressed flag

    # Total by nationality
    by_nat = rse[~rse["Suppressed"]].groupby("Nationality")["Count"].sum().sort_values(ascending=False)
    by_nat.plot.barh(title="RSE workers on-shore by source nationality")
    ```

### ATR processing-time trend

This is the SCD2 stream — accumulates over time so each refresh adds new month-end data points:

=== "Python"

    ```python
    atr = client.immigration("immigration_rse_atr_processing_times")
    # Columns: YearMonth, Description, Applications, P50, P90

    atr.plot(x="YearMonth", y=["P50", "P90"], title="ATR processing time (business days)")
    ```

---

## Source-specific notes

- **Two upstreams, one namespace**: 13 of the 16 datasets come from MBIE/INZ's GitHub-published `.rda` files (the Migration Data Explorer source). 3 come from MBIE's monthly RSE Excel workbook on immigration.govt.nz. Different file formats; eolas normalises both to the same schema convention.
- **Privacy suppression**: cells with counts of 5 or fewer are suppressed to protect individual privacy. The eolas response has `count_suppressed=true` and `count=null` for those rows; raw "<=5" strings have been replaced. See [data conventions §6](https://github.com/phildonovan/eolas/blob/main/docs/data-conventions.md#6-null-handling-and-privacy-suppression) for the full rule.
- **Rounded counts**: per MBIE policy, counts are rounded to base-3. Totals will not equal exact sums of cells.
- **RSE workbook has 3 sheets**: Sheet 1 (current snapshot) → `immigration_rse_onshore_by_region_sex`; Sheet 2 (year × sex time series) → `immigration_rse_onshore_by_year_sex`; Sheet 3 (ATR percentiles) → `immigration_rse_atr_processing_times`. The ATR stream uses SCD2 because the source workbook only ever contains the current month's percentiles — appending lets us build a longitudinal record.
- **Not currently in eolas**: sector data reports (health/tourism/primary industries — Cloudflare-protected parent page), Migrant Employment ZIP (large multi-CSV quarterly), refugee resettlement (PDF-only), Migration Trends 2016/17 historical XLSX (one-off snapshot). On the backlog if there's demand.

---

## Where to find more

- **Immigration NZ datasets on eolas**: [eolas.fyi/datasets?source=Immigration+NZ](https://eolas.fyi/datasets?source=Immigration%20NZ)
- **Migration Data Explorer**: [www.immigration.govt.nz/about-us/research-and-statistics/migration-data-explorer](https://www.immigration.govt.nz/about-us/research-and-statistics/migration-data-explorer)
- **GitHub source**: [github.com/joh024/migration_data_explorer_public](https://github.com/joh024/migration_data_explorer_public)
- **RSE scheme stats**: [www.immigration.govt.nz/about-us/research-and-statistics/statistics](https://www.immigration.govt.nz/about-us/research-and-statistics/statistics)
- **INZ Statistics**: [www.immigration.govt.nz/about-us/research-and-statistics](https://www.immigration.govt.nz/about-us/research-and-statistics)

## Related

- [Stats NZ source guide](statsnz.md) — for population estimates that contextualise migration flows
- [MBIE source guide](mbie.md) — RSE workbook is actually MBIE-published; visa decisions are INZ
- [Examples](../examples/index.md)
