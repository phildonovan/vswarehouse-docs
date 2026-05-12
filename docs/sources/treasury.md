# NZ Treasury data via eolas

[The Treasury](https://www.treasury.govt.nz) is New Zealand's principal economic and financial advisor to the government. eolas serves **5 datasets** from Treasury — small in count but heavy in policy relevance: the fiscal headline numbers + GDP estimates + the New Zealand Superannuation Fund.

If you're tracking government spending, debt, fiscal sustainability, or NZSF performance — Treasury is the source.

---

## What's in the catalogue

| Dataset | Description |
|---|---|
| `treasury_fiscal_spending` | Government operating + capital spending. Sourced from Treasury's monthly Crown Financial Statements. |
| `treasury_fiscal_revenue` | Crown revenue — tax, levies, sales of goods and services. |
| `treasury_fiscal_debt` | Crown gross + net debt, by maturity. The metric monetary policy and credit-rating agencies watch. |
| `treasury_gdp` | Treasury's own GDP estimates and forecasts — used for fiscal planning. Differs slightly from Stats NZ's published GDP for methodological reasons. |
| `treasury_nzs_fund` | New Zealand Superannuation Fund total assets + monthly performance. |

---

## Refresh schedule

Monthly. Treasury publishes the Crown Financial Statements on its own schedule (typically 30 days after month-end); our refresh runs weekly to catch the release within 5-12 days.

```python
meta = client.info("treasury_fiscal_spending")
meta["last_refreshed_at"]
meta["source_last_modified_at"]
```

---

## License

All NZ Treasury data is published under **[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)** per the [Treasury Open Data policy](https://www.treasury.govt.nz/publications/legal/copyright). Commercial use is fine; attribution required.

Recommended attribution: *"Source: The Treasury, served via eolas (eolas.fyi). CC-BY 4.0."*

---

## Common patterns

### Track Crown net debt trajectory

=== "Python"

    ```python
    import matplotlib.pyplot as plt

    debt = client.treasury("treasury_fiscal_debt", start="2010-01-01")
    # debt has columns: date, series (e.g. "net_debt", "gross_debt"), value
    net = debt[debt["series"] == "net_debt"]
    net.plot(x="date", y="value", title="Crown net debt (NZD millions)")
    plt.show()
    ```

=== "R"

    ```r
    library(ggplot2)

    debt <- eolas_get_treasury("treasury_fiscal_debt", start = "2010-01-01")
    net  <- debt[debt$series == "net_debt", ]
    ggplot(net, aes(date, value)) + geom_line() +
      labs(title = "Crown net debt (NZD millions)")
    ```

### NZSF performance vs benchmark

=== "Python"

    ```python
    nzsf = client.treasury("treasury_nzs_fund", start="2005-01-01")
    nzsf.plot(x="date", y="value", title="NZSF total assets (NZD millions)")
    ```

### Spending vs revenue (fiscal balance)

=== "Python"

    ```python
    spending = client.treasury("treasury_fiscal_spending", start="2010-01-01")
    revenue  = client.treasury("treasury_fiscal_revenue",  start="2010-01-01")

    import pandas as pd
    df = spending.merge(revenue, on="date", suffixes=("_spending", "_revenue"))
    df["balance"] = df["value_revenue"] - df["value_spending"]
    df.plot(x="date", y="balance", title="Crown fiscal balance (NZD millions)")
    ```

---

## Source-specific notes

- **Treasury GDP vs Stats NZ GDP**: Treasury publishes its own GDP estimate for use in fiscal planning. It's not Stats NZ's official GDP — small methodological differences mostly around forecast horizon and revisions cycle. For the canonical economic-statistics GDP, use `nz_gdp_growth` from OECD or Stats NZ's BDS series. For fiscal-context GDP (where Treasury is the source of truth), use `treasury_gdp`.
- **Monthly vs annual**: most Treasury fiscal data is monthly (Crown Financial Statements) but `treasury_nzs_fund` is annual (fund's annual report). Check the date frequency in the response.
- **Forecasts vs actuals**: Treasury also publishes forecasts (BEFU / HYEFU / Pre-Election Economic and Fiscal Update). The eolas datasets are *actuals* only. For forecasts, see Treasury's own [publications page](https://www.treasury.govt.nz/publications).
- **Half-year cycle**: NZ government runs on a 1 July financial year. "FY2024" in Treasury data means July 2023 – June 2024.

---

## Where to find more

- **NZ Treasury datasets on eolas**: [eolas.fyi/datasets?source=NZ+Treasury](https://eolas.fyi/datasets?source=NZ%20Treasury)
- **Treasury's own data portal**: [www.treasury.govt.nz/information-and-services/nz-economy](https://www.treasury.govt.nz/information-and-services/nz-economy)
- **Crown Financial Statements**: [www.treasury.govt.nz/publications/financial-statements-government](https://www.treasury.govt.nz/publications/financial-statements-government)
- **NZSF**: [www.nzsuperfund.nz](https://www.nzsuperfund.nz)

## Related

- [Stats NZ source guide](statsnz.md) — for the official GDP series and macro indicators
- [RBNZ source guide](rbnz.md) — for monetary-policy adjacent data (OCR, mortgages, money supply)
- [Examples](../examples/index.md)
