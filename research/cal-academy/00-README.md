# Cal Academy spatial dossier (7 Nov 2026)

Research for an immersive portfolio piece: "manipulations of Cal Academy spatial data".
Target: a textured mesh and a Gaussian splat of the Renzo Piano building that can be
switched and warped (sphere-inverted "planet", exotic cameras) in a Three.js experience.

## Files
| File | What |
|---|---|
| 01-field-capture-guide.md | What to capture today with Scaniverse / Polycam / Camera, per space, and why |
| 02-downloads-manifest.md | Every downloadable item, with URL, format, size, license, and the laptop command |
| 03-3d-models-and-city-data.md | Existing 3D models (only one: legacy 3D Warehouse), city-scale sources, Google 3D Tiles terms |
| 04-interior-and-exterior-imagery.md | Photos, 360s, webcams, videos, construction photos; splat-suitability ranking per space |
| 05-museum-data-and-apis.md | GBIF/iNaturalist/USGS/NOAA/eBird endpoints and 10 data-to-location visualization ideas |
| 06-splat-and-web-tooling.md | Scaniverse facts, companion apps, merge/registration, Spark warp hooks, pipeline |
| 07-gis-lidar-imagery.md | USGS 3DEP 2023 lidar (90 pts/m2), 2010 lidar, DataSF, NAIP, OSM, historic maps |
| 08-architectural-drawings.md | RPBW/Fondazione CD sheets (17), ArchDaily drawings, books, dimensions |
| 09-morrison-planetarium-fulldome.md | Dome specs, formats, real-time path, contacts |
| 10-freeswim-fridays-design.md | Flood-zone plan, roof access, dive loop |
| 11-steinhart-species-roster.md | 88 reef species + other tanks |
| 12-sketchfab-exhibit-models.md | Exhibit scans, licenses, the blue whale |
| 13-game-precedents.md | 25 games to learn from |
| 14-water-rendering-web-ocean.md | web-ocean assessment |
| 15-cal-academy-public-datasets.md | Census of every public Academy dataset/API/archive, ranked top 10 for a viz demo |
| 15b-cal-academy-building-anchored-datasets.md | Live-tested companion to 15: 50 datasets, the 1,071 specimens collected at the building, Galápagos 1905-06 slice, iNat place IDs, deposits (Zenodo/Dryad/NCBI), IA journals, GitHub orgs, DataSF; building-anchored top 10 + fetch recipes |
| scripts/ | EPT lidar fetch + DSM/roof render scripts used to make renders/ |
| renders/ | Lidar DSM hillshade, oblique point cloud, roof close-up, 1 m roof contours, OSM map |
| laptop-bootstrap.sh | Pulls the public-domain / open data into ./data on the laptop |

## Headline facts
- Site centroid 37.76986, -122.46609; UTM 10N E 547,022 N 4,180,415; EPSG:3857 bbox of the building
  [-13633020, 4546844, -13632686, 4547126].
- Building: 41,000 m2 floor area, 19.3 m max height, 11.3 m canopy; planetarium and rainforest
  domes both 90 ft (27.4 m) diameter; piazza skylight opening 66 x 90 ft; roof 2.5 acres, seven hills.
- Lidar: 2023 USGS CA_SanFrancisco_1_B23, 90 pts/m2, 3 cm RMSEz, public domain, streamable from S3.
  The roof hills, both domes and every skylight porthole resolve at 0.5 m (see renders/).
- No public mesh, photogrammetry or splat of the building exists. The only explicit model is a
  3,694-polygon 2014 SketchUp massing. The owned asset must be built from lidar + our splats.
- Drawings: 17 actual construction-document sheets are free on the Fondazione Renzo Piano site
  (site plan, roof plan with grid, 4 elevations, 3 building sections, 2 interior sections, 6 details).
- Scaniverse raw frames cannot be exported; Polycam Developer Mode or SplatKing give COLMAP-ready poses.
- Web: Spark 2.4 (MIT) exposes per-splat GLSL hooks for the warps; GaussianSplats3D is unmaintained.

## Environment note
This session's cloud environment "ep3 (architecture research)" has an allowlist of the hosts used here.
The View / The Territory code is not in this repository, so formats were chosen to be generic
(PLY/SPZ splats, GLB meshes, COPC/LAZ point clouds, GeoTIFF rasters, GeoJSON vectors).

## Renders added during the visit
- renders/cas_lidar_2010_dsm.png — 2010 NOAA/USGS lidar DSM at 1 m (de Young, concourse, Academy).
- renders/cas_change_2010_2023.png — 2023 minus 2010 surface height; the roof is stable, park trees grew 5-8 m.
- Historic imagery fetched via David Rumsey IIIF (CC BY-NC-SA, kept out of the repo): 1896 Blum park map;
  Aug 1948 aerial survey sheet 131 showing the old Academy campus and de Young. URLs are in 02-downloads-manifest.md.
