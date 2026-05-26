# eolas sync — keep your NZ data warehouse fresh in one command

You've done the hard part of your pipeline: data modelled, transforms written, dashboards wired up. The missing piece is the bit that keeps the underlying data current without you babysitting it. That's `eolas sync`.

```bash
# First run: full download (~seconds for small tables, minutes for parcels/addresses)
eolas sync nz_parcels --library /data/nz-warehouse

# Every run after: only fetches what changed — typically a few MB, not gigabytes
eolas sync nz_parcels --library /data/nz-warehouse
# → unchanged (snapshot 5503437…)
```

Run it from cron, Airflow, a GitHub Action, or a shell script. When nothing has changed, nothing is transferred. When LINZ adds 2,000 new title records, you get exactly those 2,000 rows — not a 1.6 GB re-download.

---

## What it does

`get()` is for interactive analysis: call it in a notebook, get a data frame, explore. `sync()` is for pipelines: write a dataset directory to disk once, keep it current with incremental fetches, read it as a single logical table from any tool that understands Parquet.

The key difference:

| | `get()` | `sync()` |
|---|---|---|
| Returns | A DataFrame in memory | A directory of Parquet files on disk |
| Network on repeat call | Full download (unless cached) | Only the delta rows since last sync |
| Best for | Notebooks, one-off analysis | Cron jobs, Airflow DAGs, dbt runs |
| Works with | pandas, polars, Arrow | pandas, polars, DuckDB, Spark, dbt — any Parquet reader |
| State tracking | None | `_eolas-manifest.json` per dataset |

---

## Quickstart

=== "CLI"

    ```bash
    # One-time: install and authenticate
    pip install eolas-data[cli]
    eolas auth set-key

    # Point to your library directory once
    eolas library set /data/nz-warehouse

    # Sync a single dataset
    eolas sync nz_parcels

    # Read the result with any Parquet-aware tool
    duckdb -c "SELECT count(*) FROM read_parquet('/data/nz-warehouse/nz_parcels/*.parquet')"

    # Re-sync: no data transferred if nothing changed
    eolas sync nz_parcels
    # → unchanged (snapshot 5503437…)

    # After a few weeks, roll the delta files into one clean snapshot
    eolas compact --dataset nz_parcels
    ```

=== "Python"

    ```python
    from eolas_data import Client

    client = Client("your_eolas_key")
    LIBRARY = "/data/nz-warehouse"

    # First sync — full download, writes snapshot-2026-05-27.parquet + manifest
    result = client.sync("nz_parcels", library_dir=LIBRARY)
    print(result.status)           # "snapshot_full"
    print(result.bytes_downloaded) # e.g. 1_650_000_000

    # Read as one logical table (PyArrow ParquetDataset under the hood)
    import pyarrow.parquet as pq
    ds = pq.ParquetDataset(f"{LIBRARY}/nz_parcels")
    df = ds.read().to_pandas()

    # Or use source helpers — they read from the library when a manifest exists
    gdf = client.linz("nz_parcels")  # reads local files, no download

    # Next sync — checks server, only fetches delta rows
    result = client.sync("nz_parcels", library_dir=LIBRARY)
    print(result.status)   # "unchanged" or "snapshot_delta"
    print(result.rows_added)  # e.g. 0 or 2847

    # Periodic compaction: merge all delta files into a fresh single snapshot
    client.compact(f"{LIBRARY}/nz_parcels")
    ```

=== "R"

    ```r
    library(eolas)
    eolas_key("your_eolas_key")

    LIBRARY <- "/data/nz-warehouse"

    # First sync — full download
    result <- eolas_sync("nz_parcels", library_dir = LIBRARY)
    result$status           # "snapshot_full"
    result$bytes_downloaded # e.g. 1650000000

    # Read from library using arrow::open_dataset (multi-file, lazy)
    library(arrow)
    ds <- open_dataset(file.path(LIBRARY, "nz_parcels"))
    df <- collect(ds)

    # Or use the source helper — reads local files when a manifest exists
    gdf <- eolas_get_linz("nz_parcels")  # reads from library, no download

    # Next sync — incremental
    result <- eolas_sync("nz_parcels", library_dir = LIBRARY)
    result$status    # "unchanged" or "snapshot_delta"
    result$rows_added  # 0 or e.g. 2847

    # Compact when you've accumulated several delta files
    eolas_compact(file.path(LIBRARY, "nz_parcels"))
    ```

---

## How it works

When you sync a dataset, eolas creates a **directory** on disk, not a single file. Inside that directory are Parquet files and a manifest that tracks which snapshot each file came from.

```
/data/nz-warehouse/nz_parcels/
├── snapshot-2026-05-24.parquet              (initial full ~1.6 GB)
├── delta-2026-05-24-to-2026-05-31.parquet   (week 1 delta ~2 MB)
├── delta-2026-05-31-to-2026-06-07.parquet   (week 2 delta ~3 MB)
└── _eolas-manifest.json                     (tracks lineage + schema)
```

Every Parquet-aware tool treats the whole directory as one logical table natively:

```python
# PyArrow / pandas
import pyarrow.parquet as pq
ds = pq.ParquetDataset("/data/nz-warehouse/nz_parcels")
df = ds.read().to_pandas()

# DuckDB
duckdb.sql("SELECT * FROM read_parquet('/data/nz-warehouse/nz_parcels/*.parquet')")

# Polars
pl.scan_parquet("/data/nz-warehouse/nz_parcels/*.parquet").collect()

# R / arrow
arrow::open_dataset("/data/nz-warehouse/nz_parcels")
```

**The manifest** (`_eolas-manifest.json`) records the snapshot lineage — which snapshot ID each file came from, when it was synced, and the row count. When you call `sync()` again, the client reads the manifest to know its current snapshot, asks the server what the latest snapshot is, and if they differ, fetches only the rows added between the two snapshots.

**Snapshot vs delta:**

- `kind: "snapshot"` — a complete copy of the table at a point in time. Written on first sync, or after a full reset (e.g. if the server's lineage for your old snapshot has expired).
- `kind: "delta"` — only the rows appended since the previous snapshot. Usually orders of magnitude smaller than a full snapshot.

**What about updates and deletes?** SCD2-tracked datasets (LINZ parcels, titles, addresses) handle updates by appending new rows with revised `_eolas_valid_from`/`_eolas_valid_to`/`_eolas_is_current` values. The delta file contains those new rows. Reading `WHERE _eolas_is_current = true` across all files gives you the current state correctly without any client-side merge logic.

**Compaction** rolls all delta files into a new single snapshot file and cleans up the old files. Run it periodically — the client will suggest compaction when you've accumulated more than ~20 deltas, but the explicit call is always available.

---

## When to use sync vs get

| Use case | Use |
|---|---|
| Interactive notebook analysis | `get()` |
| One-off data pull for a report | `get()` |
| Quick look at a small dataset | `get()` |
| Daily cron job that refreshes data | `sync()` |
| Airflow / Prefect / Dagster pipeline | `sync()` |
| dbt source file that stays current | `sync()` |
| Local data warehouse for a team | `sync()` + `sync_all()` |
| Large geospatial dataset you want fast repeated reads of | `sync()` (then read locally) |
| Feeding data into Spark / Databricks | `sync()` |
| Testing code with a fixed snapshot | `download_bulk()` with `freshness="monthly"` |

---

## Cron and Airflow recipes

### Daily cron (Linux/macOS)

```bash
# Sync the whole library nightly at 2 AM
0 2 * * * EOLAS_API_KEY=vs_your_key /usr/local/bin/eolas sync --library /data/nz-warehouse --all

# Or specific datasets
0 2 * * * EOLAS_API_KEY=vs_your_key /usr/local/bin/eolas sync --library /data/nz-warehouse --datasets nz_parcels nz_addresses nz_property_titles

# Weekly compaction on Sunday
0 3 * * 0 EOLAS_API_KEY=vs_your_key /usr/local/bin/eolas compact --library /data/nz-warehouse
```

`eolas sync` exits `0` on success (including "unchanged"), `2` on auth error, `4` if a dataset isn't found, `5` on API error. Use these in conditional logic:

```bash
eolas sync --library /data/nz-warehouse --all && echo "sync OK" | mail -s "eolas sync" you@example.com
```

### Airflow PythonOperator

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def sync_nz_data():
    from eolas_data import Client
    import os

    client = Client(os.environ["EOLAS_API_KEY"])
    library = "/data/nz-warehouse"

    results = client.sync_all(
        library_dir=library,
        datasets=["nz_parcels", "nz_addresses", "nz_property_titles", "nz_road_centrelines"],
    )

    for name, r in results.items():
        print(f"{name}: {r.status} (+{r.rows_added} rows, {r.bytes_downloaded:,} bytes)")

    # Return a summary for XCom / alerting
    return {name: r.status for name, r in results.items()}


def compact_library():
    from eolas_data import Client
    import os

    client = Client(os.environ["EOLAS_API_KEY"])
    client.compact("/data/nz-warehouse")  # library-wide compaction


with DAG(
    dag_id="eolas_sync",
    schedule_interval="0 2 * * *",   # 2 AM daily
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
) as dag:

    sync = PythonOperator(task_id="sync_nz_data", python_callable=sync_nz_data)
    compact = PythonOperator(task_id="compact_library", python_callable=compact_library)

    sync >> compact
```

### dbt source pointing at a synced directory

```yaml
# dbt/profiles.yml — use DuckDB with the synced Parquet directory
eolas_warehouse:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ":memory:"
      extensions: [parquet, httpfs]
```

```yaml
# dbt/models/sources.yml
sources:
  - name: eolas
    schema: main
    tables:
      - name: nz_parcels
        description: LINZ land parcels, synced daily
        external:
          location: "/data/nz-warehouse/nz_parcels/*.parquet"
          format: parquet
```

Pair with a cron that runs `eolas sync` before your `dbt run` and your models always see fresh data.

### Sync all datasets in your library

Once you've synced any dataset, it's registered in `~/.eolas/config.json`. Sync everything you've ever synced in one call:

```bash
eolas sync --library /data/nz-warehouse --all
```

```python
# Python equivalent
results = client.sync_all(library_dir="/data/nz-warehouse")
```

---

## Comparison vs Fivetran / Stitch / DIY

| | Fivetran | Stitch | DIY API integration | eolas sync |
|---|---|---|---|---|
| Price | ~$500+/mo per connector | ~$100–500/mo | Engineering time | $49/mo Pro — covers all datasets |
| NZ data coverage | Generic (no NZ-native connectors) | Generic | You build it | 100+ NZ sources, maintained |
| SCD2 / schema evolution | Handled | Handled | You build it | Handled — eolas does the Iceberg work |
| Incremental | Yes | Yes | You build it | Yes — delta rows only, server-side |
| Setup time | Hours (UI config) | Hours | Days to weeks per source | Minutes (`eolas sync` + cron) |
| Geospatial (GeoParquet) | No | No | You build it | Yes — GeoParquet natively |
| Infra | Cloud warehouse required | Cloud warehouse required | Whatever you build | Any filesystem — local, S3, NFS |

eolas sync is not a general-purpose ETL platform. It's a deliberately narrow tool: NZ official-data sources, Parquet on disk, incremental. If you need to sync Salesforce to Snowflake, use Fivetran. If you need NZ government data in a pipeline, eolas sync is the fastest route by a wide margin.

---

## Datasets that support incremental sync

Most datasets in eolas support incremental sync — only the rows added since your last sync are transferred. The exceptions are datasets where the upstream source replaces the full table on each publish (e.g. Stats NZ SDMX series, OECD indicators, RBNZ tables), where SCD2 lineage can't be preserved through a full replacement, or where the dataset is too small for incrementalism to matter.

**Full-refresh datasets** (the server returns all rows on every sync; your client still skips the download when the snapshot hasn't changed):

- Stats NZ SDMX time-series (`statsnz.*`, `oecd.*`)
- RBNZ tables (`rbnz.*`)
- Charities Services (`charities.*`)
- EECA energy use (`eeca.*`)
- ACC claims (`acc.*`)
- Education Counts (`edcounts.*`)
- NZ Police / MoJ (`police.*`)
- WorkSafe NZ (`worksafe.*`)
- GeoNet seismic events (`geonet.*`)

**Incremental-capable datasets** (delta rows only after the first sync):

- LINZ cadastral and geospatial (`linz.*`) — parcels, titles, addresses, roads, buildings
- Stats NZ geospatial boundaries (`statsnz_geo.*`)
- NZTA / Waka Kotahi (`nzta.*`) — crash analysis, traffic monitoring
- MSD (`msd.*`)
- Auckland Council and Auckland Transport geospatial layers
- Most regional council spatial datasets

When you call `sync()` on a full-refresh dataset, the behaviour is identical from your perspective: if the snapshot hasn't changed since your last sync, zero bytes are transferred. If it has, the new snapshot is downloaded in full and the old file is superseded. The client handles the routing transparently.

---

## Multi-dataset sync

```bash
# CLI — explicit list
eolas sync --library /data/nz-warehouse \
  --datasets nz_parcels nz_addresses nz_property_titles nz_road_centrelines

# CLI — everything you've synced before in this library
eolas sync --library /data/nz-warehouse --all

# Python — explicit list
results = client.sync_all(
    library_dir="/data/nz-warehouse",
    datasets=["nz_parcels", "nz_addresses", "nz_property_titles"],
)
for name, r in results.items():
    print(f"{name}: {r.status}")

# Python — everything in the library
results = client.sync_all(library_dir="/data/nz-warehouse")

# R — explicit list
results <- eolas_sync_all(
  library_dir = "/data/nz-warehouse",
  datasets = c("nz_parcels", "nz_addresses", "nz_property_titles")
)
```

`sync_all()` runs syncs concurrently (up to 4 in parallel by default). Unchanged datasets return immediately with no I/O.

---

## Compaction

As deltas accumulate, the dataset directory grows. Compaction merges all snapshot and delta files into a single new snapshot file, then removes the old ones. The manifest is updated to reflect the new baseline.

```bash
# Single dataset
eolas compact --dataset nz_parcels --library /data/nz-warehouse

# Entire library
eolas compact --library /data/nz-warehouse
```

```python
# Single dataset directory
client.compact("/data/nz-warehouse/nz_parcels")

# Library-wide (compact every dataset that has deltas)
client.compact("/data/nz-warehouse")
```

Run compaction when `SyncResult.files_count` exceeds ~20, or on a weekly schedule after the nightly sync. It's safe to run at any time — it reads the existing files, writes the new snapshot atomically, and only removes old files after the new snapshot is confirmed.

---

## Library shared between Python and R

The `_eolas-manifest.json` format is shared between the Python and R clients. A directory synced from Python can be read from R, and vice versa. Both clients write the same manifest schema.

```r
# Sync from Python CLI, read in R
library(arrow)
ds <- open_dataset("/data/nz-warehouse/nz_parcels")  # reads all parquet files
sf_layer <- sfarrow::st_read_parquet("/data/nz-warehouse/nz_parcels")
```

The `library_dir` itself is also shared via `~/.eolas/config.json` — set it once from either client and both use it:

```bash
eolas library set /data/nz-warehouse
```

```r
eolas_library_set("/data/nz-warehouse")
```

---

## See also

- [Bulk downloads](bulk-downloads.md) — for one-off whole-dataset downloads without building a local library
- [Python API reference — sync methods](python/reference.md#clientsyncname-library_dir)
- [R API reference — sync methods](r/reference.md#eolas_syncname-library_dir)
- [CLI reference — sync and compact](cli/index.md#eolas-sync-library-dir-name)
- [CLI reference — compact](cli/index.md#eolas-compact)
- [Authentication](authentication.md) — how to set and store your API key
