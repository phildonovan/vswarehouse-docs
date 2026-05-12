# MBIE data via eolas

The [Ministry of Business, Innovation and Employment](https://www.mbie.govt.nz) (MBIE) is the policy ministry for the productive economy — business, employment, science, immigration, tourism, energy, building. eolas serves **12 datasets** from MBIE — focused on the operational data streams MBIE publishes most actively: fuel and gas market stats, government procurement (GETS) notices, residential rental bonds, and science funding.

If you're doing energy-market analysis, government-procurement research, or rental-market work — MBIE is the source.

---

## What's in the catalogue

### Energy markets

| Dataset | Description |
|---|---|
| `fuel_prices_weekly` | Weekly retail petrol + diesel prices across all main centres + nationally. The series energy analysts and journalists track. |
| `gas_monthly_stats` | Monthly natural gas production, consumption, and storage. Sourced from MBIE's gas statistics workbook. |

### Government procurement (GETS)

The Government Electronic Tenders Service publishes every public procurement notice. MBIE indexes these:

| Dataset | Description |
|---|---|
| `gets_award_notices` | Procurement contracts awarded — successful tenders, vendor, value. |
| `gets_product_categories` | Standard product/service classification system used in tender categorisation. |
| `gets_region_by_tender` | Regional breakdown of tender activity. |

### Rental market

| Dataset | Description |
|---|---|
| `rental_bonds_quarterly` | Quarterly bond-lodgement stats — proxy for residential rental-market activity, by region. |
| `rental_bonds_by_tla` | Same data sliced by Territorial Authority — useful for council-level housing analysis. |

### Science funding

| Dataset | Description |
|---|---|
| `science_funding` | Government research grants — recipients, amounts, fund stream. |

Plus 4 additional MBIE datasets covering ancillary topics (browse the [live catalogue](https://eolas.fyi/datasets?source=MBIE) for the current list).

---

## Refresh schedule

Weekly, Wednesday morning NZ time. MBIE publishes most series on a monthly or quarterly cadence — the weekly refresh catches new releases promptly.

```python
meta = client.info("fuel_prices_weekly")
meta["last_refreshed_at"]
meta["source_last_modified_at"]
```

---

## License

All MBIE data is published under **[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)**. Commercial use is fine; attribution required.

Recommended attribution: *"Source: MBIE, served via eolas (eolas.fyi). CC-BY 4.0."*

---

## Common patterns

### NZ retail fuel prices over time

=== "Python"

    ```python
    import matplotlib.pyplot as plt

    fuel = client.mbie("fuel_prices_weekly", start="2020-01-01")
    # fuel has columns: date, region, fuel_type, value (cpl)
    nz_avg = fuel[(fuel["region"] == "National") & (fuel["fuel_type"] == "Petrol 91")]
    nz_avg.plot(x="date", y="value", title="NZ Petrol 91 — National avg (cpl)")
    plt.show()
    ```

=== "R"

    ```r
    library(ggplot2)

    fuel <- eolas_get_mbie("fuel_prices_weekly", start = "2020-01-01")
    nz_avg <- fuel[fuel$region == "National" & fuel$fuel_type == "Petrol 91", ]
    ggplot(nz_avg, aes(date, value)) + geom_line() +
      labs(title = "NZ Petrol 91 — National avg (cpl)", y = "Cents per litre")
    ```

### Government procurement by region

=== "Python"

    ```python
    procurement = client.mbie("gets_region_by_tender", start="2022-01-01")
    # Pivot to see top regions by tender count
    pivot = procurement.groupby("region")["count"].sum().sort_values(ascending=False)
    pivot.head(10).plot.barh(title="Top regions by tender activity (2022+)")
    ```

### Rental-market trends by Territorial Authority

=== "Python"

    ```python
    bonds = client.mbie("rental_bonds_by_tla", start="2018-01-01")
    # Filter to one TA (Wellington City = tla_code TBD; verify from data)
    auck = bonds[bonds["tla_name"] == "Auckland"]
    auck.plot(x="date", y="median_rent", title="Auckland median rent (MBIE bonds proxy)")
    ```

---

## Source-specific notes

- **GETS is operational + advisory**: gets_award_notices includes both completed contracts (transparency) and forward-looking spending forecasts. Filter by `notice_type` to separate them.
- **Fuel prices are surveyed**: MBIE doesn't publish actual point-of-sale data — fuel_prices_weekly is a national survey average. For station-level granularity you'd need a private aggregator.
- **Rental bonds proxy ≠ true rent**: rental_bonds_by_tla shows median bond at lodgement, which approximates median rent but lags actual rent-roll movements. For more granular real-time rental data, MBIE collaborates with Tenancy Services — sometimes available via OIA.
- **Cross-source overlap**: MBIE's rental data overlaps with Stats NZ housing stats and council planning data. MBIE's fuel/gas data is the canonical official source — no overlap concern.
- **Science funding lag**: science_funding is published with a 6-12 month delay (after grant cycles close).

---

## Where to find more

- **MBIE datasets on eolas**: [eolas.fyi/datasets?source=MBIE](https://eolas.fyi/datasets?source=MBIE)
- **MBIE's own data hub**: [www.mbie.govt.nz/about/open-government-and-official-information/data](https://www.mbie.govt.nz/about/open-government-and-official-information/data)
- **GETS** (the live procurement portal): [www.gets.govt.nz](https://www.gets.govt.nz)
- **MBIE energy stats**: [www.mbie.govt.nz/building-and-energy/energy-and-natural-resources/energy-statistics-and-modelling](https://www.mbie.govt.nz/building-and-energy/energy-and-natural-resources/energy-statistics-and-modelling)

## Related

- [Stats NZ source guide](statsnz.md) — for the broader BDS / labour-market stats
- [Examples](../examples/index.md) — worked code recipes
