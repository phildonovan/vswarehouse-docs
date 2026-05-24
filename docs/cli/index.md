# Command-line interface

The `eolas` command ships with the Python package as an optional install
extra. Same install on Linux, macOS, and Windows.

```bash
pip install eolas-data[cli]
eolas auth set-key
eolas --help
```

The CLI is a thin layer over the Python client — same auth, same retry
logic, same error mapping. Use it from a terminal, a cron job, a shell
script, or an AI agent.

## Quick examples

```bash
# Browse
eolas datasets list --source "Stats NZ"
eolas datasets list --search cpi --json | jq '.[].name'

# Fetch (row-level, live API)
eolas get nz_cpi --start 2020-01-01 --format csv > cpi.csv
eolas get nz_cpi --format json | jq '.[].value'

# Bulk download (whole dataset as a single file)
eolas download nz_cpi                                    # → nz_cpi.parquet in cwd
eolas download nz_cpi --format csv --out cpi.csv.gz     # gzipped CSV
eolas download territorial_authority_2023 --format geoparquet

# Schedule (cron on POSIX, Task Scheduler on Windows)
eolas schedule add nz_cpi --daily --out ~/data/cpi.csv
eolas schedule list

# Generate connector configs (Enterprise plan)
eolas integrate meltano --datasets nz_cpi,nz_gdp_growth --output ./my-pipeline/
```

---

## Authentication

`eolas` resolves your API key in this order:

1. `--api-key VALUE` flag on the command
2. `EOLAS_API_KEY` environment variable
3. OS keyring (`pip install 'eolas-data[secure]'` required; service `"eolas"`, username `"api-key"`)
4. `~/.eolas/config.json` (written by `eolas auth set-key`, mode 0600)

For workstations, the OS keyring is the most convenient: one-shot setup, encrypted at rest, no environment variable to manage. For CI and Docker, use the env var — the keyring backend is not available in headless environments.

```bash
# OS keyring (recommended for workstations)
pip install 'eolas-data[secure]'
eolas auth save-key              # interactive prompt
eolas auth save-key vs_mykey     # non-interactive (e.g. from a script)
eolas auth clear-key             # remove from keyring

# Config file (plaintext fallback)
eolas auth set-key               # prompt for the key, write config
eolas auth clear                 # delete the config file

# Always available
eolas auth status                # show which source is in use (env / keyring / config)
```

---

## Output: human or machine

The CLI auto-detects whether stdout is a terminal:

| Context | Default output |
|---|---|
| Interactive terminal | Rich coloured tables |
| Piped (`\| jq`, `> file.csv`, etc.) | NDJSON or CSV — whatever's most pipeable |

Force machine output explicitly with `--json` on any command that supports it.

```bash
# Same command, different output
eolas datasets list                       # → coloured table
eolas datasets list --json                # → newline-delimited JSON
eolas datasets list | head                # → newline-delimited JSON (auto-detected)
```

---

## Commands

### `eolas get <name>`

Fetch a dataset and write it to stdout or a file.

```bash
eolas get nz_cpi                                       # CSV to stdout
eolas get nz_cpi --format json                         # JSON to stdout
eolas get nz_cpi --start 2020-01-01 --end 2024-12-31   # filtered
eolas get nz_meshblock_2023 --format parquet --out sa2.parquet  # Parquet (must specify --out)
eolas get nz_cpi --limit 100                           # cap rows
```

Formats: `csv` (default), `json`, `parquet`.
Parquet requires `--out FILE` (binary output isn't safe to stream to stdout).

### `eolas download <name>`

Download a complete dataset as a single file. Wraps the `/v1/bulk/{namespace}/{table}` endpoint — no row caps, no pagination.

See [Bulk downloads](../bulk-downloads.md) for tiers, caching, licence rules, and redistribution guidance.

```bash
eolas download nz_cpi                                    # Parquet, written to ./nz_cpi.parquet
eolas download nz_cpi --format csv                       # gzipped CSV → ./nz_cpi.csv.gz
eolas download nz_cpi --format parquet --out ~/data/cpi.parquet
eolas download territorial_authority_2023 --format geoparquet
eolas download nz_cpi --freshness monthly                # pin to latest monthly snapshot
eolas download nz_cpi --freshness current                # Pro plan — current Iceberg snapshot
```

**Options**

| Flag | Values | Default | Description |
|---|---|---|---|
| `--format`, `-f` | `parquet`, `csv`, `geoparquet` | `parquet` | Output format. `csv` writes a `.csv.gz` file. GeoParquet requires a geospatial dataset. |
| `--freshness` | `auto`, `monthly`, `current` | `auto` | `auto` — server picks based on plan (Free→monthly, Pro→current). |
| `--out`, `-o` | PATH | `<name>.<ext>` in cwd | Destination file path. |
| `--api-key` | KEY | resolved from env / config | Override API key. |

**Exit codes**

| Code | Meaning |
|---|---|
| `0` | Success — file written |
| `2` | Auth error (invalid key, 402 upgrade required, 403 licence restricted) |
| `5` | API error (503 snapshot not yet available, 5xx) |
| `4` | Dataset not found |

On success (interactive mode) the command prints the filename and file size. When stdout is piped, it emits a single JSON line: `{"path": "...", "bytes": ..., "format": "...", "freshness": "..."}`.

---

### `eolas sync <name>`

Incrementally sync a bulk dataset — only re-downloads when the server's snapshot changes.

On each run, a lightweight HEAD request checks the `X-Snapshot-Version` header. If the local file is already current (snapshot id matches the sidecar), no data is transferred. The file is replaced **atomically** when an update is available. A sidecar file `<out>.eolas-meta.json` records the snapshot id for the next check.

```bash
# Single-shot sync (no --watch)
eolas sync nz_cpi                                     # → ./nz_cpi.parquet
eolas sync nz_cpi --format csv --out ~/data/cpi.csv.gz

# Watch mode: poll every hour, print one line per iteration, exit with Ctrl-C
eolas sync nz_cpi --watch 1h
eolas sync nz_cpi --watch hourly --out ~/data/cpi.parquet
eolas sync nz_cpi --watch 30m    --freshness current
```

**Options**

| Flag | Values | Default | Description |
|---|---|---|---|
| `--format`, `-f` | `parquet`, `csv`, `geoparquet` | `parquet` | Output format. |
| `--freshness` | `auto`, `monthly`, `current` | `auto` | Freshness level. |
| `--out`, `-o` | PATH | `<name>.<ext>` in cwd | Destination file path. |
| `--watch` | duration | (off) | Foreground poll loop. Duration examples: `60` / `30s` / `5m` / `1h` / `1d` / `hourly` / `daily` / `weekly`. |
| `--api-key` | KEY | resolved from env / config | Override API key. |

**Watch-mode output** (one line per iteration):

```
[14:00:00 NZST] unchanged (snapshot 5503437…)
[15:00:00 NZST] updated to snapshot 7041234… (1.2 MB)
```

**Exit codes:** Same as `eolas download` (`0` success, `2` auth/plan, `5` API error, `4` not found, `64` bad usage).

---

### `eolas datasets ...`

```bash
eolas datasets list                                    # everything
eolas datasets list --source "Stats NZ"                # filter by source
eolas datasets list --search cpi                       # substring on name/title
eolas datasets info nz_cpi                             # full metadata
eolas datasets preview nz_cpi --limit 5                # first N rows
```

### `eolas auth ...`

```bash
# OS keyring — one-shot workstation setup (pip install 'eolas-data[secure]')
eolas auth save-key              # interactive prompt; saves to OS keyring
eolas auth save-key vs_mykey     # non-interactive (e.g. from a setup script)
eolas auth clear-key             # remove key from OS keyring

# Config file — plaintext fallback (no extra install needed)
eolas auth set-key               # interactive prompt; writes ~/.eolas/config.json
eolas auth clear                 # remove config file

# Status — works regardless of which source is active
eolas auth status                # masked key + which source is supplying it
```

`eolas auth status` checks all sources in precedence order and reports the first one it finds — useful for debugging auth issues in any environment.

### `eolas schedule ...`

Recurring fetches via the OS-native scheduler. **cron** on Linux/macOS,
**Task Scheduler** on Windows — same commands, same behaviour.

```bash
# Daily at 06:00 local time (the default)
eolas schedule add nz_cpi --daily --out ~/data/cpi.csv

# Other shortcuts
eolas schedule add nz_cpi --hourly  --out ~/data/cpi.csv
eolas schedule add nz_cpi --weekly  --out ~/data/cpi.csv
eolas schedule add nz_cpi --monthly --out ~/data/cpi.csv

# Custom cron expression (POSIX only)
eolas schedule add rbnz_b1_exchange_rates_monthly --cron "0 */6 * * *" --out ~/data/fx.csv

# Preview without installing
eolas schedule add nz_cpi --daily --out ~/data/cpi.csv --dry-run

eolas schedule list
eolas schedule remove nz_cpi
```

`--out FILE` is required — cron jobs run with no terminal, so stdout has
to go somewhere on disk.

On POSIX, managed entries are tagged with `# eolas-schedule: <name>`
sentinels, so `eolas schedule list/remove` only ever touch lines that
belong to eolas. Your other cron jobs aren't affected. On Windows the
equivalent is the `eolas-<name>` task name prefix.

### `eolas integrate <platform>` (Enterprise plan)

Generate ready-to-deploy connector configs for popular data-pipeline tools.

```bash
eolas integrate meltano             --datasets nz_cpi,nz_gdp_growth --output ./tap-eolas/
eolas integrate fivetran            --datasets nz_cpi
eolas integrate azure-data-factory  --datasets nz_cpi,nz_gdp_growth
```

| Platform | What you get | Status |
|---|---|---|
| Meltano | `meltano.yml` (uses `tap-rest-api-msdk`) + README + `.env.example` — `meltano install && meltano run tap-eolas target-jsonl` and you're loading | **Verified end-to-end** — see recipe below |
| Fivetran | Connector Builder YAML for paste-into-dashboard import + setup README | **Experimental** — output is structure-verified but hasn't been tested end-to-end against a real Fivetran account |
| Azure Data Factory | Linked-service + per-dataset REST datasets + copy pipeline JSON — usable via `az datafactory` CLI or ADF Studio paste | **Experimental** — output is structure-verified but hasn't been tested end-to-end against a real Azure subscription |

Output directory defaults to `./eolas-<platform>/`. Existing files are
preserved unless you pass `--force`.

This is an Enterprise-plan feature. Non-Enterprise keys see a clear
upgrade pointer with the [pricing URL](https://eolas.fyi/#pricing). The
gating lives server-side so the capability is bypass-proof.

#### Meltano verification recipe

Roughly five minutes, end-to-end:

```bash
eolas integrate meltano --datasets nz_cpi --output /tmp/eolas-meltano-test
cd /tmp/eolas-meltano-test
export EOLAS_API_KEY=your_enterprise_key
meltano install
meltano run tap-eolas target-jsonl
ls output/             # → nz_cpi.jsonl with the CPI series in it
```

If records land in `output/nz_cpi.jsonl`, the generated `meltano.yml` is provably
correct — Meltano installed the tap, fetched data through the eolas API, and
wrote it to disk. This is the path used to mark Meltano "verified".

#### Experimental status

"Experimental" doesn't mean *broken*; it means the output passes a thorough
set of structural checks (parses as valid YAML / JSON, declares all the
fields the platform's documented spec requires, internal references between
resources resolve correctly) but **the generated config has not actually
been imported into the target platform and run end-to-end**.

If you import the experimental output into Fivetran or ADF and it fails with
a specific error, [open an issue on eolas-data](https://github.com/phildonovan/eolas-data/issues)
with the error message. Usually it's a renamed field or a stricter type than
the generator assumed; fixes ship within hours.

### Other commands

```bash
eolas health    # ping the API; useful smoke check in CI
eolas version   # print installed eolas-data version
```

---

## Exit codes

For shell scripts and AI agents that branch on outcome:

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Generic error |
| `2` | Authentication (invalid key, Enterprise plan required, etc.) |
| `3` | Rate limit hit |
| `4` | Dataset / resource not found |
| `5` | Other API error (5xx, etc.) |
| `64` | Bad command-line usage (mirrors `sysexits.h`) |

```bash
if eolas health; then
  eolas get nz_cpi --format csv > cpi.csv
fi

case $? in
  2)  echo "auth problem — run eolas auth set-key" ;;
  3)  echo "rate limited — wait and retry" ;;
  4)  echo "dataset not found" ;;
esac
```

---

## Tips

- **Piping**: every command that produces records auto-switches to NDJSON
  when stdout is piped. Combine with `jq`, `csvkit`, `mlr`, or anything else.
- **CI usage**: set `EOLAS_API_KEY` as a CI secret; the env var takes
  precedence over any on-disk config.
- **Agent usage**: `--help` is structured enough that an LLM can discover
  the commands without reading external docs. Stable exit codes mean
  agents can branch on outcome programmatically.
- **Custom output dir for integrations**: pass `--output DIR`. If `DIR`
  doesn't exist it's created.

---

## Source

The CLI lives in [eolas-data](https://github.com/phildonovan/eolas-data) —
`eolas_data/cli.py` and `eolas_data/schedule.py`. PRs welcome.
