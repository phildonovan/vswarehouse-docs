# vswarehouse

<div class="hero" markdown>

**Official Python and R clients for the vs-warehouse statistical data API.**

Access {{ series_count }}+ economic, demographic and geospatial time series from {{ sources }} — in two lines of code, returning a data frame ready for analysis.

<div class="badge-row" markdown>

[![PyPI](https://img.shields.io/pypi/v/vswarehouse?label=PyPI&color=blue)](https://pypi.org/project/vswarehouse/)
[![R](https://img.shields.io/badge/R-GitHub-blue)](https://github.com/phildonovan/vswarehouse-r)
[![API](https://img.shields.io/badge/API-api.virtus--solutions.io-blue)](https://api.virtus-solutions.io)

</div>
</div>

---

## Choose your language

=== "Python"

    ```bash
    pip install vswarehouse
    ```

    ```python
    from vswarehouse import Client

    client = Client("vs_your_key")

    # Source-specific helpers
    df = client.statsnz("nz_cpi", start="2020-01-01")
    df = client.oecd("nz_gdp")

    # Or plot it instantly
    df.plot_series()
    ```

=== "R"

    ```r
    remotes::install_github("phildonovan/vswarehouse-r")
    ```

    ```r
    library(vswarehouse)

    vs_key("vs_your_key")

    # Source-specific helpers
    df <- vs_get_statsnz("nz_cpi", start = "2020-01-01")

    # One-line chart
    vs_plot(df)
    ```

---

## What's in the API?

| Category | Examples |
|---|---|
| Macroeconomics | CPI, GDP growth, unemployment, interest rates |
| Labour & Earnings | Employment, wages, gender pay gap |
| Business & Enterprise | Firm counts, births/deaths, industry breakdowns |
| Population | Resident population by age, sex, ethnicity, region |
| Justice & Social | Charges, convictions, household expenditure |
| Fiscal | Government spending, revenue, debt, NZ Super Fund |
| Geospatial | Land parcels, roads, addresses, territorial authorities |

Data is sourced from **Stats NZ**, the **OECD**, **NZ Treasury**, **RBNZ**, and **LINZ**, updated weekly.

---

## Get an API key

Free tier (3 requests/day) requires no credit card. [Get your key →](https://api.virtus-solutions.io/signup)

| Plan | Price | Requests |
|---|---|---|
| Free | $0 | 3/day |
| Starter | $10/month | 10/day |
| Pro | $49/month | Unlimited |

[View pricing →](https://api.virtus-solutions.io/#pricing)
