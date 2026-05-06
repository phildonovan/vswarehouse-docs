"""mkdocs-macros hook: fetch live counts from the vs-warehouse API at build time.

Variables exposed to markdown templates:
    {{ series_count }}  rounded-down series count, e.g. "270" when live is 278
    {{ sources }}       human-readable source list, e.g. "Stats NZ, OECD, RBNZ, ..."
    {{ source_count }}  number of distinct sources

Falls back to safe defaults if the API is unreachable so docs builds never break.
"""
import requests

API = "https://api.virtus-solutions.io/v1/series"
FALLBACK = {"series_count": 270, "sources": "Stats NZ, OECD, RBNZ, NZ Treasury, LINZ", "source_count": 10}


def _fetch():
    r = requests.get(API, timeout=10)
    r.raise_for_status()
    data = r.json()
    sources = sorted({s["source"] for s in data})
    return {
        "series_count": (len(data) // 10) * 10,
        "sources": ", ".join(sources),
        "source_count": len(sources),
    }


def define_env(env):
    try:
        values = _fetch()
    except Exception as e:
        print(f"[macros] API fetch failed ({e}), using fallback")
        values = FALLBACK
    for k, v in values.items():
        env.variables[k] = v
