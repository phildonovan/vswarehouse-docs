# eolas-data

<div class="hero" markdown>

**Official Python, R, and command-line clients for the eolas statistical data API.**

Access {{ dataset_count }}+ economic, demographic and geospatial datasets from {{ sources }} — in two lines of code, returning a data frame ready for analysis. Or schedule cron jobs and generate Meltano / Fivetran / Azure Data Factory connector configs from the command line.

<div class="badge-row" markdown>

[![PyPI](https://img.shields.io/pypi/v/eolas-data?label=PyPI&color=blue)](https://pypi.org/project/eolas-data/)
[![R](https://img.shields.io/badge/R-GitHub-blue)](https://github.com/phildonovan/eolas-r)
[![API](https://img.shields.io/badge/API-api.eolas.fyi-blue)](https://api.eolas.fyi)

</div>
</div>

---

## Choose your language

=== "Python"

    ```bash
    pip install eolas-data
    ```

    ```python
    from eolas_data import Client

    client = Client("vs_your_key")

    # Source-specific helpers
    df = client.statsnz("nz_cpi", start="2020-01-01")
    df = client.oecd("nz_gdp")

    # Or plot it instantly
    df.plot_series()
    ```

=== "R"

    ```r
    remotes::install_github("phildonovan/eolas-r")
    ```

    ```r
    library(eolas)

    eolas_key("vs_your_key")

    # Source-specific helpers
    df <- eolas_get_statsnz("nz_cpi", start = "2020-01-01")

    # One-line chart
    eolas_plot(df)
    ```

=== "CLI"

    ```bash
    pip install eolas-data[cli]
    eolas auth set-key                       # one-time
    ```

    ```bash
    # Browse, fetch, schedule, integrate — all from the shell
    eolas datasets list --search cpi
    eolas get nz_cpi --start 2020-01-01 --format csv > cpi.csv
    eolas schedule add nz_cpi --daily --out ~/data/cpi.csv
    eolas integrate meltano --datasets nz_cpi,nz_gdp    # Enterprise
    ```

    Same install on Linux, macOS, and Windows. Pipes cleanly into `jq`, `csvkit`, your spreadsheet, etc.

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

Free tier requires no credit card. [Get your key →](https://api.eolas.fyi/signup)

| Plan | Price | Requests | Row cap per request | Extras |
|---|---|---|---|---|
| Free | $0 | 10/month | 50,000 | — |
| Starter | $10/month | 100/month | 50,000 | — |
| Pro | $49/month | Unlimited | Unlimited | — |
| Enterprise | Contact us | Unlimited | Unlimited | Snowflake share · `eolas integrate` connector scaffolding (Meltano / Fivetran / Azure Data Factory) |

[View pricing →](https://eolas.fyi/#pricing)
