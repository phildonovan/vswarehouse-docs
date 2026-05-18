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

## What is eolas?

**eolas** is a unified REST API over New Zealand's fragmented official-data landscape, plus reliable Python and R clients on top of it. The same datasets that normally require separate scrapers / API integrations / Excel downloads from Stats NZ, RBNZ, the OECD, LINZ, MBIE, NZTA, ACC, the regional councils, and 20+ other sources are all available behind one consistent endpoint with one API key.

Built so you don't have to:

- Maintain N source-specific scrapers and watch them break when an agency redesigns its website
- Reconcile dozens of date formats, region codes, and naming conventions
- Wait for batch CSV exports when you want fresh data

If you do data work in NZ — economic, demographic, geospatial, or social — eolas is the layer that gets the data into your pandas / dplyr / SQL pipeline without you babysitting it.

---

## Choose your language

=== "Python"

    ```bash
    pip install eolas-data
    ```

    ```python
    from eolas_data import Client

    client = Client("your_eolas_key")

    # Source-specific helpers
    df = client.statsnz("nz_cpi", start="2020-01-01")
    df = client.oecd("nz_gdp")

    # It's a pandas DataFrame — plot, filter, join as you like
    df.plot(x="date", y="value", title="NZ CPI")
    ```

=== "R"

    ```r
    remotes::install_github("phildonovan/eolas-r")
    ```

    ```r
    library(eolas)

    eolas_key("your_eolas_key")

    # Source-specific helpers
    df <- eolas_get_statsnz("nz_cpi", start = "2020-01-01")

    # It's a tibble — plot with ggplot, dplyr-pipe, anything
    library(ggplot2)
    ggplot(df, aes(date, value)) + geom_line()
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

Data is sourced from **Stats NZ**, the **OECD**, **NZ Treasury**, **RBNZ**, **LINZ**, **MBIE**, **Waka Kotahi (NZTA)**, **MSD**, **NZ Police / MoJ**, **ACC**, **Education Counts**, **WorkSafe NZ**, **Auckland Council**, **Auckland Transport**, **DOC**, **Co-Lab Waikato**, **ECan / Canterbury**, **GeoNet**, **Charities Services**, **Immigration NZ**, **EECA**, **Manaaki Whenua / LRIS**, and 10 regional & district council clusters. Updated weekly.

---

## Get an API key

Free tier requires no credit card. [Get your key →](https://api.eolas.fyi/signup)

| Plan | Price | Requests | Row cap per request | Extras |
|---|---|---|---|---|
| Free | $0 | 10/month | 50,000 | — |
| Pro | $49/month | Unlimited | Unlimited | Email support |
| Enterprise | Contact us | Unlimited | Unlimited | Snowflake share · `eolas integrate` connector scaffolding (Meltano / Fivetran / Azure Data Factory) · SLA |

[View pricing →](https://eolas.fyi/#pricing)
