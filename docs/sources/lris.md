# Manaaki Whenua / LRIS data via eolas

[Manaaki Whenua – Landcare Research](https://www.landcareresearch.co.nz) is New Zealand's primary CRI for terrestrial ecosystem science. It runs the [Land Resource Information Systems (LRIS) portal](https://lris.scinfo.org.nz), which hosts the canonical national datasets on land cover, land use, soils, and protected areas. eolas serves **20 datasets** from LRIS — the foundational layers behind every "what's on the ground" analysis in NZ.

If you're doing environmental research, agricultural / forestry / horticultural analytics, climate-policy modelling, or ecological-impact studies — LRIS is the source.

---

## What's in the catalogue

### Land Cover Database (LCDB)

The LCDB is the canonical national land-cover classification — what type of vegetation, surface, or use covers each ~10m² of NZ. It's been re-derived from satellite imagery at successive vintages, so you can compare class transitions over time. Six versions are in eolas:

| Dataset | Description |
|---|---|
| `lcdb_v6_mainland` | LCDB v6 polygon land-cover for mainland NZ (latest). |
| `lcdb_v6_chatham` | LCDB v6 for the Chatham Islands. |
| `lcdb_v6_version_trace_mainland` | Full change history of every polygon across all LCDB versions (mainland). |
| `lcdb_v6_version_trace_chatham` | Same trace table for Chatham. |
| `lcdb_v5_mainland`, `lcdb_v5_chatham`, `lcdb_v5_version_trace_*` | LCDB v5. |
| `lcdb_v41_mainland`, `lcdb_v41_chatham`, `lcdb_v41_version_trace_mainland` | LCDB v4.1. |
| `lcdb_v40_mainland`, `lcdb_v40_change` | LCDB v4.0 + change table. |
| `lcdb_v33_mainland`, `lcdb_v33_change` | LCDB v3.3. |
| `lcdb_v30_mainland`, `lcdb_v30_change` | LCDB v3.0. |

For a single point-in-time analysis, use the latest (`lcdb_v6_mainland`). For change-over-time analysis, the version-trace tables give you a polygon-by-polygon transition record without having to join multiple versions manually.

### Land use + protected areas

| Dataset | Description |
|---|---|
| `nzlum_v03` | NZ Land Use Map v0.3 — polygon land-use classification (~170k features). Distinct from LCDB: classifies *use* (dairy, exotic forestry, urban) rather than *cover* (grassland, native bush, built). |
| `pan_nz_2025_draft` | Protected Areas Network of NZ 2025 (~60k features). All formally-protected land — DOC + QEII covenants + iwi-protected + ngā whenua rāhui. The comprehensive protection layer. |
| `pbc_h3_r9` | Pastoral beef + sheep farming intensity modelled on the H3 geospatial indexing system at resolution 9. |

---

## Refresh schedule

Weekly, Wednesday morning NZ time.

LRIS datasets are research outputs — they refresh on the LRIS portal's publication cadence (sometimes annually, sometimes longer between major versions). Our weekly refresh catches any changes promptly.

```python
meta = client.info("lcdb_v6_mainland")
meta["last_refreshed_at"]
meta["source_last_modified_at"]
```

---

## License

LRIS data is published under **[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)** in most cases — but always check the per-dataset metadata. A few research outputs have stricter or attribution-only licences.

Recommended attribution: *"Source: Manaaki Whenua – Landcare Research / LRIS Portal, served via eolas (eolas.fyi). CC-BY 4.0."*

If you cite LCDB in academic work, Manaaki Whenua publishes a recommended citation per version on the LRIS dataset page.

---

## Common patterns

### Land-cover composition of a region

=== "Python"

    ```python
    import geopandas as gpd

    lcdb = client.lris("lcdb_v6_mainland", as_sf=True)
    # Filter to one region (clip against LINZ regional council boundaries)
    rc = client.linz("nz_regional_councils", as_sf=True)
    canterbury = rc[rc["regc2023_v1_00_name"] == "Canterbury"]
    cant_cover = gpd.clip(lcdb, canterbury)

    # Area by cover class
    cant_cover["area_ha"] = cant_cover.to_crs("EPSG:2193").area / 10_000
    composition = cant_cover.groupby("class_name")["area_ha"].sum().sort_values(ascending=False)
    print(composition.head(15))
    ```

=== "R"

    ```r
    library(sf)
    library(dplyr)

    lcdb <- eolas_get_lris("lcdb_v6_mainland", as_sf = TRUE)
    rc   <- eolas_get_linz("nz_regional_councils", as_sf = TRUE)
    cant <- rc[rc$regc2023_v1_00_name == "Canterbury", ]
    cant_cover <- st_intersection(lcdb, cant)

    cant_cover$area_ha <- as.numeric(st_area(st_transform(cant_cover, 2193))) / 10000
    composition <- cant_cover |>
      st_drop_geometry() |>
      group_by(class_name) |>
      summarise(area_ha = sum(area_ha)) |>
      arrange(desc(area_ha))
    print(head(composition, 15))
    ```

### Land-cover change 2008 vs 2018 (v3.3 → v5)

```python
# Use the version-trace table — already has class_2008 + class_2018 on each polygon
trace = client.lris("lcdb_v5_version_trace_mainland")
# Polygons that flipped from "Indigenous Forest" to "Exotic Grassland" (i.e. cleared)
cleared = trace[(trace["class_2008"] == "Indigenous Forest") & (trace["class_2018"] == "Exotic Grassland")]
print(f"Indigenous forest cleared to grassland 2008-2018: {cleared['area_ha'].sum():.0f} ha")
```

### What's protected near me?

```python
import geopandas as gpd
from shapely.geometry import Point

pan = client.lris("pan_nz_2025_draft", as_sf=True)
# 50km buffer around a point (in NZTM)
pt = gpd.GeoSeries([Point(174.7762, -41.2865)], crs="EPSG:4326").to_crs("EPSG:2193")
buffer = pt.buffer(50_000).iloc[0]
nearby = pan[pan.to_crs("EPSG:2193").intersects(buffer)]
print(f"Protected areas within 50km of Wellington: {len(nearby)} polygons, {nearby['area_ha'].sum():.0f} ha")
```

### Pastoral intensity heatmap

```python
import matplotlib.pyplot as plt

pbc = client.lris("pbc_h3_r9", as_sf=True)
# pbc has H3 hex polygons + a modelled intensity score
pbc.plot(column="intensity", cmap="RdYlGn_r", figsize=(10, 12), legend=True)
plt.title("Pastoral beef + sheep intensity (H3 R9)")
```

---

## Source-specific notes

- **LCDB versions are vintaged, not "updated"**: each LCDB version was independently re-derived from satellite imagery at a specific epoch (v3.0 ≈ 2001/02, v3.3 ≈ 2001/02 reprocessed, v4.0 ≈ 2008, v4.1 ≈ 2008 reprocessed, v5 ≈ 2012/13, v6 ≈ 2018). Use the version-trace tables for proper change analysis — don't just join two raw versions on geometry, the polygon boundaries themselves shift.
- **LCDB classes (33 total)**: see the [LCDB documentation](https://lris.scinfo.org.nz/layer/104400-lcdb-v50-deprecated-land-cover-database-version-50-mainland-new-zealand) — top-level categories are Artificial, Bare/Lightly-vegetated, Water, Cropland, Grassland, Scrub, Forest. Each splits into specific classes (e.g. "Indigenous Forest", "Exotic Forest", "Manuka and/or Kanuka").
- **Cover vs use**: LCDB tells you *what's growing/present*; NZLUM tells you *what it's used for*. Forestry land in LCDB might be "Exotic Forest" cover; in NZLUM it'd be "Forestry — exotic — production". Use the right one for the question you're answering.
- **PAN includes private protection**: the Protected Areas Network is broader than just DOC's `doc_public_conservation_land`. It includes QEII covenants on private land, ngā whenua rāhui on Māori land, and other formal protections. For "what's protected somewhere" use PAN; for "what does DOC manage" use the DOC layer.
- **Geometry**: all LRIS datasets expose `geometry_wkt`. The polygon datasets (LCDB, NZLUM, PAN) can be large — `lcdb_v6_mainland` is ~430k polygons. Free tier 50,000-row cap will truncate; either upgrade or filter with a region clip first.
- **CRS**: LRIS publishes in NZTM2000 (EPSG:2193). The eolas pipeline reprojects to WGS84 (EPSG:4326) for the wire format. For area / distance calculations, reproject back to NZTM (`.to_crs("EPSG:2193")`).

---

## Where to find more

- **LRIS datasets on eolas**: [eolas.fyi/datasets?source=Manaaki+Whenua](https://eolas.fyi/datasets?source=Manaaki%20Whenua%20%2F%20LRIS)
- **LRIS Portal** (the underlying portal): [lris.scinfo.org.nz](https://lris.scinfo.org.nz)
- **Manaaki Whenua – Landcare Research**: [www.landcareresearch.co.nz](https://www.landcareresearch.co.nz)
- **LCDB documentation + classes**: [www.landcareresearch.co.nz/tools-and-resources/mapping/lcdb-v50/](https://www.landcareresearch.co.nz/tools-and-resources/mapping/lcdb-v50/)

## Related

- [LINZ source guide](linz.md) — for the cadastral parcels you'd often intersect LCDB against
- [DOC source guide](doc.md) — for the public-conservation-land subset of `pan_nz_2025_draft`
- [Examples](../examples/index.md) — boundary mapping recipes
