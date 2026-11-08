# Planet of the park quadrant: data layers brief (2026-11-07, 20:55)

Status: candidate third snack ("the planet is looking cool. we might add that as a third snack, seeing how things go"). Nothing built from this yet. THE TERRITORY [1] owns the planet (PLANDEV/skins/calacademy-planet/); this is the wish list and the source map.

## Bryan, verbatim
"could be interesting to add some data layers, transportation, some kind of indexical color layers on the mesh, the houses, the neighborhoods - animated buslines, add the orrery of course, extroverted and introverted views, we'd need good 3d geometry of the whole 'planet', with textures properly registered..."

## Layer by layer: what it is, where the data is, what it costs
| layer | source (all open) | shape for the planet | note |
|---|---|---|---|
| Geometry of the whole planet | 2023 USGS 3DEP via the S3 EPT (the octree gives coarser levels for free: depth-limited nodes = a decimated cloud, so a 2 m DSM of the 6 x 6 km region is a few hundred MB, not 3 billion points); core stays at 1 m | region DSM (roofs and trees) replaces the bare-earth DTM rim | one script, an hour of download; `lidar_ept_site.py` already walks the hierarchy |
| Textures properly registered | NAIP 2022 (60 cm, public domain) on the same grids; the lidar's own RGB where NAIP lags | drape at 1 m core / 2 m region, no manual registration (both are UTM rasters) | done for the current bake; 60 cm NAIP exists if the core goes finer |
| Houses | DataSF Building Footprints with lidar heights (ynuv-fyni, PDDL) + the DSM | extruded footprints or the DSM itself; indexical colour by height, year built (SF Assessor parcels), use | 150 k footprints citywide; clip to the 6 km |
| Neighborhoods | DataSF Analysis Neighborhoods (41 polygons) and Planning Districts | tinted zones on the mesh, labels | small |
| Indexical colour layers on the mesh | DataSF zoning / land use, Assessor use codes, tree canopy (the DSM minus DTM = canopy height), SF Urban Forest street trees (200 k points), elevation bands, slope | one colour ramp per layer, switched by the DATA dial | the canopy layer is free from what we have |
| Transportation | SFMTA GTFS static (routes, stops, shapes, timetables) and GTFS-realtime (vehicle positions); Muni lines through the park: 5, 7, 28, 29, 33, 44, N Judah on the edge; also the park shuttle, bike lanes (DataSF), JFK Promenade car-free | lines on the mesh; animated buses from the timetable (no live feed needed for a loop: play one weekday's schedule as moving dots) | the GTFS schedule is the animation; realtime is a later live mode |
| Animated bus lines | GTFS shapes + stop_times -> position per second per trip | dots along the shapes on the planet clock (the Territory already has a clock) | one parser; the clock exists |
| The orrery | already in the Territory: sun, moon, SF clock; add the planets if "orrery" means the solar system | | ask THE TERRITORY what the orrery currently shows |
| Extroverted and introverted views | already in the Territory: sphere outside / sphere in / octa / icosa in (the 4-view sheet) | | exists |
| Water bodies | OSM lake polygons (fetched, 42) as flat surfaces at each lake's own level | | small layer, THE TERRITORY offered it |

## Open questions for Bryan
1. Which indexical colour first: canopy height, building height, year built, zoning, neighborhood?
2. Bus lines: schedule loop (one weekday compressed to the planet's day) or live positions?
3. Does "orrery" mean the sun/moon clock that exists, or a solar-system ring around the planet?
4. Core extent: keep the quadrant at 1 m, or grow the fine core to the whole park (4.5 x 0.8 km)?

## Sources (verified tonight unless marked)
- EPT: https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23/ept.json (public domain)
- NAIP 2022 via Planetary Computer STAC collection `naip` (public domain)
- DataSF footprints ynuv-fyni; Analysis Neighborhoods; zoning; street trees (PDDL / ODC) [search-only tonight except footprints]
- SFMTA GTFS: https://www.sfmta.com/reports/gtfs-transit-data (static zip) and 511.org GTFS-realtime (free key) [search-only]
- OSM water + labels: fetched, ODbL

## THE TERRITORY's feasibility read (21:05)
- Exists: six geometries in/out; orrery + clock (SF, PST); DATA dial; line layers (routes.json "lanes"); moving dots (vessel engine, FLOW); indexical colour overlays (layers_ext.js: class / value / mask / photo); registered drapes.
- Re-bake only: bus routes as lanes; neighbourhoods, zoning, canopy (DSM - DTM), footprints as colour.
- Small-to-medium new code: GTFS loader -> vessel engine (animated buses).
- New code: 3D houses; on the core colour the footprints instead (the DSM already has the roofs); extrude only on the rim if at all.
- Rim: a 5 m DSM (highest return per 5 m cell from coarser EPT levels, same grid as b) replaces the DTM; 2 m would be resampled away (rim mesh ~9-10 m/vertex). Close-ups: widen the 1 m core or re-bake the near ring at 4-5 m.
- NAIP 60 cm core: modest gain, only with a wider core.
- Cheapest first colour layers: canopy height or neighbourhoods. Most alive: bus lines (needs the loader).

## Bryan's rulings (21:10, verbatim)
- "'orrery' means the clock that exists - the sun and moon and galaxy image. it's all built already. that's all i meant"
- "scheduled or live buses - i think scheduled, just like the scheduled ferries in our Sagi Planet"
- "fine core grows from the quadrant to the whole park - yes. highest res."
- First colour layer: not yet chosen; canopy + neighbourhoods prepared as the cheap pair.
