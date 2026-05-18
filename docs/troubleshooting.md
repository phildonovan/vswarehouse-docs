# Troubleshooting

Common errors, what they mean, and how to fix them. If something here doesn't match what you're seeing, [open an issue](https://github.com/phildonovan/eolas-data/issues) or email phil@virtus-solutions.io.

---

## HTTP status codes

The API returns standard HTTP codes. Each maps to a Python exception class (and an R error message).

| Code | Python class | When you'll see it | What to do |
|---|---|---|---|
| **401** | `AuthenticationError` | Missing or wrong API key | Check `EOLAS_API_KEY` env var or `Client(api_key=...)`. Keys start with `vs_`; if yours doesn't, regenerate from [your dashboard](https://eolas.fyi/settings). |
| **403** | `AuthenticationError` | API key is valid but your plan doesn't include this endpoint (e.g. `/v1/integrations/*` is Enterprise-only) | Check your plan at [eolas.fyi/dashboard](https://eolas.fyi/dashboard). Upgrade if needed, or use a generic endpoint that's available on your plan. |
| **404** | `NotFoundError` | Dataset name doesn't exist | Double-check the spelling. Run `client.list()` to see all available names, or browse [eolas.fyi/datasets](https://eolas.fyi/datasets). Names are case-sensitive. |
| **413** | `APIError` (status_code=413) | Row cap exceeded for your plan | Free caps at 50,000 rows per request. Either narrow the query (date range, region filter) or upgrade to Pro for uncapped queries. The response includes `X-Plan-Row-Cap` and `X-Plan-Rows-Available` headers. |
| **429** | `RateLimitError` | Monthly request quota reached | Free is 10/month, Pro is unlimited. Wait until next month, upgrade, or contact us if you think the count is wrong. The response includes `X-Plan-Monthly-Limit` and `X-Plan-Requests-Used` headers. |
| **5xx** | `APIError` | Server issue on our end | Retry once or twice — the client doesn't auto-retry. If it persists, check the [status page](https://eolas.fyi/status) and report via GitHub. |

---

## Exception hierarchy (Python)

All exceptions inherit from `eolas_data.exceptions.EolasError`, so you can catch broadly or narrowly:

```python
from eolas_data import Client
from eolas_data.exceptions import (
    EolasError,            # base — catch-all for anything from the client
    AuthenticationError,   # 401 / 403
    RateLimitError,        # 429
    NotFoundError,         # 404
    APIError,              # everything else; has .status_code
)

client = Client()

try:
    df = client.statsnz("nz_cpi", start="2020-01-01")
except AuthenticationError:
    print("API key isn't working — get one at https://eolas.fyi/signup")
except RateLimitError:
    print("Out of free-tier requests this month — upgrade or wait")
except NotFoundError:
    print("That dataset name doesn't exist — try client.list()")
except APIError as e:
    print(f"HTTP {e.status_code}: {e}")
except EolasError as e:
    print(f"Something else went wrong: {e}")
```

In R, all errors come through `stop()` with a message — wrap calls in `tryCatch()` if you need to handle them programmatically.

---

## Common errors

### "No API key found"

You called a function that needs auth without setting a key. Three ways to provide one (in precedence order):

```python
# 1. Explicit argument
client = Client(api_key="vs_...")

# 2. Environment variable (most common)
import os
os.environ["EOLAS_API_KEY"] = "vs_..."   # or set in your shell / .env

# 3. Config file (CLI users)
# Set via: eolas auth set-key
```

```r
# R: explicit
eolas_key("vs_...")

# Or set EOLAS_API_KEY in .Renviron — picked up automatically
```

### "I'm getting fewer rows than I expected"

You're probably hitting the **50,000 row cap** on the Free tier. The response is truncated — no error is raised, but the cap is signalled in the `X-Plan-Row-Cap` and `X-Truncated` HTTP headers.

Options:

1. **Narrow the query**: add `start` / `end` to filter by date, or filter by region / category in your own code.
2. **Upgrade to Pro** ($49/mo) — caps removed entirely.
3. **Use the Snowflake share** (Enterprise) — zero-copy access to the full warehouse, no API in the loop.

```python
# Check whether your result was truncated
df = client.statsnz("nz_addresses")
df.eolas_truncated  # True if you hit the cap
df.eolas_row_cap    # 50000 on Free, None on Pro/Enterprise
```

### "Geometry isn't returning as `sf` / `GeoDataFrame`"

Both clients auto-detect spatial datasets and convert geometry when the optional dependency is installed:

```bash
# Python — install geopandas + shapely
pip install eolas-data[geo]
```

```r
# R — install sf
install.packages("sf")
```

If the package isn't installed, you'll get the raw WKT string in a `geometry_wkt` column instead. Force conversion with `force=True` (Python) or `as_sf = TRUE` (R) to raise a clear ImportError instead of silently falling back.

### "My dataset name doesn't autocomplete"

The Python client ships a `_dataset_names.py` stub for IDE autocomplete, but it's a snapshot from the last release date. If you added a dataset to your warehouse after that, autocomplete won't see it yet. The runtime call still works:

```python
df = client.get("some_new_name")   # works at runtime
df = client.get(DatasetName.some_new_name)   # autocomplete may not see it
```

Check the snapshot date:

```python
from eolas_data._dataset_names import CATALOG_SNAPSHOT_DATE
print(CATALOG_SNAPSHOT_DATE)  # "2026-05-12"
```

We refresh the stub on every release.

### "Schedule isn't running" (CLI)

Check whether the schedule was actually installed:

```bash
eolas schedule list
```

If empty, the `eolas schedule add ...` command registers the schedule with the OS's cron-equivalent. On macOS / Linux it uses `cron`; on Windows it uses Task Scheduler. The schedule won't fire if your machine is asleep at the scheduled time — for always-on scheduling, run it on a server.

### "I'm getting different counts than Stats NZ / RBNZ / [agency]'s own site"

eolas data is sourced directly from the agency's public API or published files, then loaded into our warehouse on a weekly cadence (most pipelines). If the agency has published an update since our last refresh, you'll see the older numbers until our next run.

Each dataset's `last_refreshed_at` and `source_last_modified_at` (if available) are surfaced in the metadata response:

```python
meta = client.info("nz_cpi")
meta["last_refreshed_at"]       # when we last loaded it
meta["source_last_modified_at"] # when the agency last touched the source (where capturable)
```

If `source_last_modified_at` is newer than `last_refreshed_at`, the source has changed and our refresh is pending — usually next Wednesday morning NZ time. If both look fine but your number still doesn't match, double-check that you're querying the same vintage / breakdown / units as the agency's own report.

### "Tests fail in CI but work locally"

Most likely: missing `EOLAS_API_KEY` in CI. We don't bundle keys, and the env-var lookup is the only auth path that works in headless environments (no OS keyring on a server).

{% raw %}
```yaml
# GitHub Actions example
- name: Run tests
  env:
    EOLAS_API_KEY: ${{ secrets.EOLAS_API_KEY }}
  run: pytest
```
{% endraw %}

---

## Debugging tips

### See the raw HTTP request

The Python client uses `requests` under the hood. To inspect:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# requests + urllib3 will log every request / response
df = client.statsnz("nz_cpi")
```

### Check what columns a dataset has before fetching

```python
meta = client.info("nz_meshblock_2023")
print(meta["columns"])     # list of column names + types
print(meta["row_count"])   # so you know whether you'll hit the cap
```

### Verify your key + plan

```python
client = Client()
client.info("nz_cpi")  # any successful call confirms the key works
```

Or from the dashboard at [eolas.fyi/dashboard](https://eolas.fyi/dashboard) — usage counter + plan tier are visible there.

---

## Still stuck?

- [GitHub issues — eolas-data](https://github.com/phildonovan/eolas-data/issues) for Python client bugs
- [GitHub issues — eolas-r](https://github.com/phildonovan/eolas-r/issues) for R client bugs
- **Email**: phil@virtus-solutions.io for billing, plan changes, or anything sensitive
- **Status page**: [eolas.fyi/status](https://eolas.fyi/status) to check if an outage explains what you're seeing
