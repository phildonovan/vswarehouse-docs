# Authentication

Every API call needs an API key. This page covers how to get one, where to store it, and how the clients find it at runtime.

---

## Get a key

[**Sign up at eolas.fyi/signup**](https://eolas.fyi/signup) — free tier, no credit card. You get an API key (starts with `vs_`) immediately on confirmation.

Your dashboard at [eolas.fyi/dashboard](https://eolas.fyi/dashboard) shows the key, your current plan, this month's usage, and lets you rotate the key if you need to.

---

## Where to put the key

In precedence order — whichever the client finds first, wins:

| Method | When to use | Setup |
|---|---|---|
| **1. Explicit argument** | Quick scripts, notebooks where the key is a placeholder you'll fill in | `Client(api_key="vs_...")` (Python) / `eolas_key("vs_...")` (R) |
| **2. `EOLAS_API_KEY` environment variable** | Production code, CI, anything you don't want hard-coded | `export EOLAS_API_KEY=vs_...` (or set in `.env` / `.Renviron`) |
| **3. OS keyring (workstation)** | Persistent, encrypted-at-rest — one-shot setup, never paste your key again | `eolas auth save-key` (Python CLI) / `eolas_key_save()` (R) |
| **4. Config file (CLI only)** | Plaintext fallback when OS keyring is unavailable | `eolas auth set-key` and it'll write to `~/.config/eolas/config.json` |

Below, more on each.

---

## Method 1 — Explicit argument

The most direct path. Useful for one-off scripts, exploratory notebooks, or when you want to swap keys per call.

=== "Python"

    ```python
    from eolas_data import Client

    client = Client(api_key="vs_your_key_here")
    df = client.statsnz("nz_cpi")
    ```

=== "R"

    ```r
    library(eolas)

    eolas_key("vs_your_key_here")
    df <- eolas_get_statsnz("nz_cpi")
    ```

**Don't commit the literal key to git.** If your script lives in a repo, prefer Method 2.

---

## Method 2 — Environment variable

The recommended path for anything that runs more than once. Set `EOLAS_API_KEY` once and the clients find it automatically.

### Local shell (macOS / Linux)

```bash
# Set for this terminal session
export EOLAS_API_KEY=vs_your_key_here

# Or make it persistent — add to ~/.zshrc or ~/.bashrc:
echo 'export EOLAS_API_KEY=vs_your_key_here' >> ~/.zshrc
```

### Windows PowerShell

```powershell
$Env:EOLAS_API_KEY = "vs_your_key_here"

# Persistent across sessions:
[Environment]::SetEnvironmentVariable("EOLAS_API_KEY", "vs_your_key_here", "User")
```

### R: use `.Renviron`

R doesn't see shell env vars in all setups (RStudio especially). The reliable home is `~/.Renviron`:

```bash
echo 'EOLAS_API_KEY=vs_your_key_here' >> ~/.Renviron
```

Restart R / RStudio after editing.

### Python: use `.env`

Many Python projects keep a `.env` file alongside the code (in `.gitignore`). Load it with `python-dotenv` before instantiating the client:

```python
from dotenv import load_dotenv
load_dotenv()  # picks up .env from cwd

from eolas_data import Client
client = Client()  # finds EOLAS_API_KEY automatically
```

### Verify it worked

```python
import os
print(os.getenv("EOLAS_API_KEY")[:8] + "…")  # "vs_abcdef…"

client = Client()
client.info("nz_cpi")  # any successful call confirms auth
```

---

## Method 3 — OS keyring (workstation)

The most convenient workstation option: stores the key in the OS-native encrypted credential vault (macOS Keychain, Windows Credential Manager, Linux Secret Service). Set once and every Python and R session finds it automatically — no environment variable, no config file.

The Python CLI and R package share the same keyring slot (`service="eolas"`, `username="api-key"`), so saving from one language makes it available in the other.

=== "Python CLI"

    ```bash
    pip install 'eolas-data[secure]'   # adds the keyring package
    eolas auth save-key                # interactive prompt
    eolas auth save-key vs_mykey       # non-interactive (e.g. from a script)

    eolas auth status                  # shows which source is supplying the key
    eolas auth clear-key               # remove from keyring
    ```

    After `save-key`, `Client()` works without any further setup in new sessions:

    ```python
    from eolas_data import Client
    client = Client()  # finds key from OS keyring automatically
    ```

=== "R"

    ```r
    install.packages("keyring")   # or: pak::pak("keyring")
    # On Linux, you may need: sudo apt install libsecret-1-dev first

    eolas_key_save()        # interactive prompt (masked input)
    eolas_key_save("vs_...") # non-interactive

    eolas_key_status()      # show which source is supplying the key
    eolas_key_clear()       # remove from keyring
    ```

    After `eolas_key_save()`, `eolas_get_*()` works without any further setup:

    ```r
    library(eolas)
    df <- eolas_get("nz_cpi")  # key found from OS keyring automatically
    ```

**Headless / CI environments:** the keyring backend is typically unavailable in Docker containers, GitHub Actions, and cron jobs. The clients fall through to the env var silently — Method 2 is the right choice for those environments.

---

## Method 4 — Config file (CLI)

The CLI has a one-shot setup that writes the key to `~/.eolas/config.json` as plaintext (chmod 600). Use this as a fallback when the OS keyring is unavailable.

```bash
pip install eolas-data[cli]
eolas auth set-key
# Paste your key when prompted; CLI persists it.

eolas auth status   # confirm — masks the key for safety
eolas datasets list # any successful call confirms auth
```

The Python `Client` and R `eolas_*` functions **don't** read this config file — it's CLI-only. Use Method 2 (env var) or Method 3 (OS keyring) if you want one credential shared across Python, R, and the CLI on the same machine.

---

## CI / production environments

Headless environments (Docker containers, GitHub Actions, CI runners, cron jobs) won't have an OS keyring or interactive shell — Method 2 (env var) is the only path.

{% raw %}
=== "GitHub Actions"

    ```yaml
    - name: Run my eolas-using job
      env:
        EOLAS_API_KEY: ${{ secrets.EOLAS_API_KEY }}
      run: python my_script.py
    ```

=== "Docker"

    ```dockerfile
    # Don't bake the key into the image. Pass at runtime:
    # docker run -e EOLAS_API_KEY=vs_... my-image
    ```

=== "Systemd"

    ```ini
    [Service]
    Environment="EOLAS_API_KEY=vs_..."
    ExecStart=/usr/bin/python3 /opt/myapp/main.py
    ```
{% endraw %}

For long-running production apps, rotate the key periodically (see below) and update the secret store. The clients don't cache the key beyond the lifetime of one `Client` instance, so a redeploy with a new key value picks it up cleanly.

---

## Rotating your key

If a key is compromised — or you just want to cycle it on a schedule — rotate it from the dashboard:

1. Visit [eolas.fyi/dashboard](https://eolas.fyi/dashboard)
2. Click **Rotate key**
3. Your old key stops working immediately; the new key is shown once
4. Update `EOLAS_API_KEY` everywhere it's set (local `.env`, CI secrets, server env files)

There's no per-plan limit on rotations. Rotate as often as your security posture warrants.

---

## Multiple keys (dev / prod separation)

Each eolas account has one active API key at a time. To isolate dev from prod, use separate **accounts** (not separate keys on one account):

- Production account on Pro: `vs_prod_...`
- Personal / dev account on Free: `vs_dev_...`

Then your dev environment sets `EOLAS_API_KEY=vs_dev_...` and your prod env sets `EOLAS_API_KEY=vs_prod_...`. Quotas and rate limits are per-account, so dev experiments don't burn through prod's monthly budget.

(Multi-key-per-account is on the roadmap. If you're an Enterprise customer needing this now, get in touch.)

---

## Security best practices

- **Never commit `EOLAS_API_KEY` to a public repo.** Add `.env`, `.Renviron`, and any local config file to `.gitignore`. If you do accidentally commit a key, rotate it before pushing the fix — git history is forever.
- **Use a secret store in CI.** GitHub Actions Secrets, GitLab CI variables, AWS Secrets Manager, etc. — never paste keys into pipeline YAML directly.
- **Limit logging.** The Python / R clients mask the key in their `repr`, but `logging.basicConfig(level=logging.DEBUG)` will log the request headers including `X-API-Key`. Don't run debug-level logging in production.
- **One key per agent.** If you're running eolas from a shared box (a workstation used by multiple people), give each user their own account + key rather than sharing. Usage shows up cleanly per-account in the dashboard.

---

## Troubleshooting auth issues

See the [Troubleshooting page](troubleshooting.md) — sections on **"No API key found"**, **HTTP 401**, and **HTTP 403** cover the common failure modes.
