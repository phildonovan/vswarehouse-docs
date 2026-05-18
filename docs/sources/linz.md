# LINZ data via eolas

[Land Information New Zealand](https://www.linz.govt.nz) (LINZ) is the agency responsible for cadastral, geodetic, hydrographic, and topographic data. eolas serves **106 datasets** from LINZ — covering property parcels, addresses, road centrelines, suburbs, place names, and the geodetic mark networks (including Antarctic + offshore islands).

If you're doing property-data, cadastral, or NZ-wide spatial-reference work, LINZ is the primary source.

---

## What's in the catalogue

### Cadastral

| Dataset | Description |
|---|---|
| `nz_parcels` | All NZ land parcels (~3 million features). The cadastral foundation layer. |
| `nz_primary_parcels` | Primary parcels (one per title); ~2 million. Faster than `nz_parcels` for most use cases. |
| `nz_non_primary_parcels` | Easements, roads, secondary parcels. |
| `nz_property_titles` | Title records keyed to parcels. |
| `nz_landonline_parcels` | Landonline working copy — useful for in-flight subdivisions before they propagate to nz_parcels. |

### Addresses + place names

| Dataset | Description |
|---|---|
| `nz_addresses` | Street addresses (~3 million). LINZ's authoritative address layer. |
| `nz_street_address` | Address points only (no extra metadata). |
| `nz_suburb_locality` | Suburb / locality polygons. |
| `nz_suburbs_and_localities` | The combined LINZ table — what most users want for "suburb of X". |
| `nz_suburb_suburb_locality_territorial_authority` | Suburb-to-TA crosswalk. |
| `nz_place_names` | NZGB authoritative place names — official and historical, with iwi/hapū attribution. |

### Buildings + topography

| Dataset | Description |
|---|---|
| `nz_building_outlines` | Building footprints (~2 million). |
| `nz_road_centrelines` | Road network as line geometry. |
| `nz_river_centrelines` | River network. |
| `nz_coastlines` | NZ coastline polygons. |

### Geodetic + survey

| Dataset | Description |
|---|---|
| `nz_trig_points` | Trigonometric survey marks. |
| `antarctic_geodetic_marks` | Antarctic survey network — NZ's responsibility under the Antarctic Treaty. |
| `antarctic_geodetic_vertical_marks` | Vertical control marks (heights). |
| `canterbury_eq_geodetic_marks_2010_11`, `_2016` | Marks affected by the 2010-2011 and 2016 Canterbury earthquakes (movement records). |

For the full list, browse [eolas.fyi/datasets?source=LINZ](https://eolas.fyi/datasets?source=LINZ).

---

## Refresh schedule

Weekly, Wednesday morning NZ time. The cadastral layers (parcels, titles) update frequently as Landonline transactions complete; the topographic and geodetic layers are more stable.

```python
meta = client.info("nz_parcels")
meta["last_refreshed_at"]
meta["source_last_modified_at"]   # LINZ's Koordinates publish timestamp
```

---

## License

All LINZ data is published under **[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)**. You can use it commercially, derive from it, and redistribute — with attribution.

Recommended attribution: *"Source: LINZ, served via eolas (eolas.fyi). CC-BY 4.0."*

LINZ also has specific guidance on derivative works (e.g. for property analytics products) at [www.linz.govt.nz/licensing](https://www.linz.govt.nz/licensing). Worth a look if you're building a commercial product on LINZ data.

---

## Common patterns

### Plot all NZ road centrelines

=== "Python"

    ```python
    # ~2 million features — needs Pro tier to avoid the 50k row cap, or filter first
    roads = client.linz("nz_road_centrelines", as_sf=True)
    roads.plot(figsize=(10, 12), linewidth=0.1, color="grey")
    ```

=== "R"

    ```r
    library(sf)
    library(ggplot2)

    roads <- eolas_get_linz("nz_road_centrelines", as_sf = TRUE)
    ggplot(roads) + geom_sf(linewidth = 0.05) + theme_void()
    ```

### Look up addresses near a point

LINZ doesn't ship spatial-index filters in the eolas API yet — you'd download a region first, then filter in memory:

=== "Python"

    ```python
    import geopandas as gpd
    from shapely.geometry import Point

    # Fetch addresses in a bounding box (currently no API-side filter; pull region + filter local)
    addresses = client.linz("nz_addresses", as_sf=True)

    # Filter to within 500m of a point
    pt = gpd.GeoSeries([Point(174.7762, -41.2865)], crs="EPSG:4326")  # Wellington
    pt_nztm = pt.to_crs("EPSG:2193")
    addr_nztm = addresses.to_crs("EPSG:2193")

    nearby = addr_nztm[addr_nztm.geometry.distance(pt_nztm.geometry[0]) < 500]
    ```

A native spatial-filter API is on the eolas roadmap — for now, large region pulls + local filtering work.

### Property research: parcels + titles + addresses

=== "Python"

    ```python
    parcels   = client.linz("nz_primary_parcels", as_sf=True)
    titles    = client.linz("nz_property_titles")
    addresses = client.linz("nz_addresses", as_sf=True)

    # Join titles to parcels via title_no
    parcels_titled = parcels.merge(titles, on="title_no", how="left")

    # Then spatial-join the addresses
    parcels_full = parcels_titled.sjoin(addresses, how="left", predicate="contains")
    ```

This is the workflow behind property-search tools (PropertyGuru-style sites) — you're materialising what most NZ property platforms build on top of.

---

## Source-specific notes

- **SCD2 for cadastral**: parcels, titles, and addresses use SCD2 replication — each refresh adds a new version of any changed rows and marks the old one as expired. The `_eolas_is_current`, `_eolas_valid_from`, and `_eolas_valid_to` columns let you reconstruct the state at any past timestamp. Most users want `WHERE _eolas_is_current = true` to get the current cadastral state.
- **Size**: `nz_parcels` (~3M) and `nz_addresses` (~3M) exceed the Free tier's 50,000-row cap. Either upgrade to Pro, filter via geometry (spatial filter on the roadmap), or [download the snapshot](https://eolas.fyi/datasets/nz_parcels/download).
- **Koordinates / WFS origin**: most LINZ layers come from the [data.linz.govt.nz](https://data.linz.govt.nz) Koordinates portal via WFS. Some layers (Landonline cadastral working data) come from the LINZ Exports API and are loaded via a different code path.
- **Earthquake-displaced marks**: the `canterbury_eq_*` datasets capture geodetic marks that moved during the 2010-2011 + 2016 Canterbury quakes — important for surveyors reconciling pre- and post-quake datums.
- **Antarctic + Ross Dependency**: NZ has Antarctic geodetic responsibility under the Antarctic Treaty; the `antarctic_geodetic_*` datasets are NZ-government data, not third-party.

---

## Where to find more

- **LINZ datasets on eolas**: [eolas.fyi/datasets?source=LINZ](https://eolas.fyi/datasets?source=LINZ)
- **LINZ Data Service** (the underlying portal): [data.linz.govt.nz](https://data.linz.govt.nz)
- **NZGB Gazetteer** (the place-names authority): [gazetteer.linz.govt.nz](https://gazetteer.linz.govt.nz)
- **LINZ licensing**: [www.linz.govt.nz/licensing](https://www.linz.govt.nz/licensing)

## Related

- [Stats NZ geospatial boundaries](statsnz.md#geospatial-boundaries-census) — for census boundaries (meshblocks, SAs, TAs) that complement LINZ's cadastral layers
- [Examples](../examples/index.md#load-a-boundary-and-map-it) — worked geo recipes
