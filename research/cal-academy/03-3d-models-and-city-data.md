# 3D Sources — Cal Academy building and the Music Concourse site

Research track report. **[verified]** = fetched; **[unverified]** = search snippet only (sketchfab, 3dwarehouse, data.sfgov, overpass, youtube were blocked for this track).

## Headline findings
1. **Exactly one explicit 3D model of the building exists online: the legacy SketchUp 3D Warehouse model** (3D Warehouse Staff account, 3,694 polygons, 27 materials, last modified 2014-03-20, inches). Almost certainly the old Google Earth 3D Buildings layer model. Low-poly massing; free Trimble account to download SKP (usually also DAE). [unverified]
2. **No Sketchfab, TurboSquid, CGTrader, Free3D, Thingiverse, Printables, Cults3D, MyMiniFactory, GrabCAD, BIMobject or RevitCity model of the building.** Sketchfab hits are the Academy's ~700 specimen scans and Viz Studio environment props.
3. **No public photogrammetry, point cloud, or Gaussian splat of the building** found on Polycam, Luma, Scaniverse, Sketchfab or YouTube.
4. **Best legal high-fidelity geometry: USGS 3DEP `CA_SanFrancisco_1_B23` lidar (2023)**; Academy confirmed inside bounds. Mesh the roof DSM, texture from orthoimagery or our splats.
5. **Google Photorealistic 3D Tiles are the best textured mesh but stream-only** (no caching/export under Map Tiles API policies). Fine for live Three.js context via `3d-tiles-renderer`; not as a baked asset.

## 2.1 Explicit models
| Title | URL | Format | Polys | License | Fidelity |
|---|---|---|---|---|---|
| California Academy of Sciences (3D Warehouse) [unverified] | https://3dwarehouse.sketchup.com/model/1a4c209a43561ba445f5590ac69325a5/California-Academy-of-Sciences (classic embed: https://embed-3dwarehouse-classic.sketchup.com/model/1a4c209a43561ba445f5590ac69325a5/California-Academy-of-Sciences) | SKP (+DAE likely) | 3,694 | 3DW General Model License (use in own work, no redistribution) | Low-medium massing with roof hills and domes, 2014 |
| Golden Gate Park Carousel (3D Warehouse) [unverified] | https://3dwarehouse.sketchup.com/model/b6c28f0f5d142e1da452c95d59985708/Golden-Gate-Park-Carousel | SKP | | 3DW | nearby prop; also search 3DW for "de Young", "Spreckels Temple of Music", "Conservatory of Flowers" |

## 2.2 Sketchfab (Academy-related, not the building)
- @calacademy: https://sketchfab.com/calacademy/models — 700+ specimen scans; downloads via Google Form request; CC terms, some "NoAI"; many ~1M tris. Blog: https://sketchfab.com/blogs/community/finding-a-home-for-700-3d-scans-with-the-california-academy-of-sciences
- @vizstudio: https://sketchfab.com/vizstudio/models — 65 planetarium-show environment assets [unverified]
- Visitor collections: https://sketchfab.com/edemaistre/collections/california-academy-of-sciences-d170f803470c4bc19d838be6550f0750 ; https://sketchfab.com/williamj.mitchell/collections/california-academy-of-sciences-30009f3befb34a91a66cf09e44f4ced1 [unverified]
- San Francisco City (free, stylized): https://sketchfab.com/3d-models/san-francisco-city-108841754fd3485886c1dde13301d341 [unverified]

## 2.3 Commercial SF city models (LOD1/LOD2, generic; no living roof)
https://www.cgtrader.com/3d-models/exterior/cityscape/san-francisco-city-and-suburbs ; https://cgtrader.com/3d-models/exterior/cityscape/san-francisco-city-3d-model ; https://www.cgtrader.com/3d-models/exterior/cityscape/san-francisco-3d-skyline-city-map ; https://www.artstation.com/marketplace/p/jrrwd/san-francisco-3d-city-model (Anyscape, LOD2) ; https://www.3dcadbrowser.com/3d-model/san-francisco-city

## 2.4 Student / professional recreations and architect archive (reference only)
- Steinhart Aquarium 3D Breakdown (Behance): https://www.behance.net/gallery/77145291/Steinhart-Aquarium-3d-Breakdown [unverified]
- Fondazione Renzo Piano archive: https://www.fondazionerenzopiano.org/en/project/california-academy-of-sciences/ ; model record https://fondazionerenzopiano.org/en/project/california-academy-of-sciences/model-209.pdf ; project PDF https://www.fondazionerenzopiano.org/media/project_document/5964e4027a12f100177762.pdf (physical study models catalogued; no digital 3D files)
- RPBW: https://www.rpbw.com/project/california-academy-of-sciences
- ArchDaily (plans, sections, roof plan): https://www.archdaily.com/6810/california-academy-of-sciences-renzo-piano
- Landscape Performance green roof methods PDF: https://landscapeperformance.org/sites/default/files/2025-02/CA-Academy-Green-Roof-methods.pdf
- Gemmiti physical green-roof model: https://gemmiti.com/portfolio/renzo-piano-cas-green-roof/
- LEGO Ideas: https://ideas.lego.com/projects/4906ab65-978a-4075-b60c-a53624695693 [unverified]
- RTF case study: https://www.re-thinkingthefuture.com/case-studies/a4635-california-academy-of-sciences-in-golden-gate-park-by-renzo-piano-the-living-roof-architecture/
- No Rhino/Grasshopper, Blender, Revit or YouTube speed-build recreation found.

## 2.5 City-scale streaming sources
| Source | How | Terms | Fidelity |
|---|---|---|---|
| **Google Photorealistic 3D Tiles** | Root `https://tile.googleapis.com/v1/3dtiles/root.json?key=API_KEY` (enable Map Tiles API, billed GCP project). Three.js: `3d-tiles-renderer` (Apache-2.0, https://github.com/NASA-AMMOS/3DTilesRendererJS) with `GoogleCloudAuthPlugin({ apiToken, autoRefreshToken: true })`; `ReorientationPlugin({ lat: 37.7699*DEG2RAD, lon: -122.4661*DEG2RAD })` puts the Academy at the origin (ENU) so splats register. Also Cesium ion asset **2275207** via `CesiumIonAuthPlugin`. [verified from source] | https://developers.google.com/maps/documentation/tile/policies — no offline use, caching, bulk download, export; show attribution. Free tier ~1,000 root-tile requests/month. | Textured mesh, ~0.5-2 m detail; roof hills, portholes, domes visible but blobby |
| **Cesium OSM Buildings** (ion asset 96188) | https://cesium.com/platform/cesium-ion/content/cesium-osm-buildings/ ; `Cesium3DTileset.fromIonAssetId(96188)` | ODbL | LOD1; Academy is an 8 m box |
| **OpenStreetMap** way **28695389** | https://www.openstreetmap.org/way/28695389 (tags: tourism=museum, height=8, wikidata; no building:levels) [unverified] | ODbL | footprint good for masking lidar |
| **Overture Maps buildings** | GeoParquet on S3, clip with GDAL (https://gdal.org/en/stable/tutorials/vector_geoparquet_tut.html) | ODbL / CDLA | LOD1 with lidar/ML heights |
| **Open City Model** (BuildZero) | https://github.com/opencitymodel/opencitymodel ; `https://s3.dualstack.us-east-1.amazonaws.com/opencitymodel/2019-jun/<format>/California/06075/California-06075-NNN.(zip|json)` [verified README] | ODbL | LOD1 CityGML/CityJSON |
| **Mapbox Standard 3D buildings** | https://docs.mapbox.com/map-styles/reference/standard/ ; community tileset `maning.sf-lidar` (https://gist.github.com/rob137/a217ba388884bb9c759a2c217935db6a) | display only | LOD1 / landmarks |
| **Esri SF 3D object scene layer** | https://developers.arcgis.com/javascript/latest/visualization/3d-visualization/cities-in-3d | display only | textured LOD2-ish |
| **Apple Maps Flyover** | SF buildings refreshed 2021 (https://justinobeirne.com/apple-updates-san-francisco-buildings) | no mesh access | reference |
| **Vexcel 3D Cities (SF)** | https://vexceldata.com/?p=9105 | commercial quote | ~7.5 cm aerial photogrammetry textured mesh in 3D Tiles; the only purchasable textured mesh of the real roof |

## 2.6 Open SF data
- DataSF Building Footprints (ynuv-fyni): https://data.sfgov.org/d/ynuv-fyni ; blog https://datasf.org/blog/new-sf-building-footprints-released-with-3d-characteristics ; mirror https://catalog.data.gov/dataset/building-footprints-04ba1 — 177,023 footprints with hgt_meancm/hgt_maxcm/hgt_mediancm; PDDL. The Pictometry multipatch model itself is not public.
- SF Building Masses 2017 LoD1: https://3d.bk.tudelft.nl/opendata/opencities/ ; https://geodata.lib.berkeley.edu/catalog/berkeley-s71t2s (KML/SHP/FGDB)
- USGS 3DEP CA_SanFrancisco_1_B23 (2023): EPT https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23/ept.json [verified: 13.09 B pts, Academy inside]; NOAA InPort https://www.fisheries.noaa.gov/inport/item/73386
- USGS ARRA-CA_SanFranCoast_2010 EPT: https://s3-us-west-2.amazonaws.com/usgs-lidar-public/ARRA-CA_SanFranCoast_2010/ept.json [verified 2.2 B pts; note GIS track says tile index lacks the Academy; check]
- NASA WERK 1 m DEM/DSM SF 2023 (COG): https://wifire-data.sdsc.edu/dataset/nasa-werk-dem-ca-sanfrancisco-1-b23 — fastest ready-made roof heightfield
- AWS registry https://registry.opendata.aws/usgs-lidar/ ; hobu index https://github.com/hobuinc/usgs-lidar
- Microsoft US Building Footprints: https://github.com/microsoft/USBuildingFootprints

## 2.7 Imagery that could feed photogrammetry
- Axiom Images aerials (night orbit of dome, orbit of both museums): https://www.axiomimages.com/tag/California+Academy+of+Sciences (paid)
- Eric Cheng drone stills of the roof (2014): https://echeng.com/p/431 ; https://echeng.com/p/433 (ARR)
- Kite aerial photos of roof (ml_kap): https://www.fluidr.com/photos/ml_kap/sets/72157715419996906 (ARR)
- Google Arts & Culture Hubbs beaked whale 3D: https://artsandculture.google.com/asset/hubbs-beaked-whale-california-academy-of-sciences/jQFAVUOey9cyvQ

## 2.8 Techniques
- **Blosm** (Blender): https://prochitecture.gumroad.com/l/blender-osm ; wiki https://github.com/vvoovv/blosm/wiki/Import-of-Google-3D-Cities ; https://github.com/vvoovv/blosm/wiki/Import-of-3D-Tiles — imports Google 3D Tiles (own key), OSM buildings, terrain, open 3D Tiles datasets. Exporting Google tiles breaches Google policy regardless of tool.
- Tile Importer: https://superhivemarket.com/products/tile-importer
- Maps Models Importer (RenderDoc): https://github.com/eliemichel/MapsModelsImporter — GPL, educational only, against Google TOS.
- Policy: https://developers.google.com/maps/documentation/tile/policies ; FAQ https://cloud.google.com/blog/products/maps-platform/commonly-asked-questions-about-our-recently-launched-photorealistic-3d-tiles
- **Recommended legal pipeline (OSM + lidar -> mesh):** PDAL `readers.ept` on the 2023 EPT with bounds (3857: x -13633400..-13632300, y 4546500..4547500) -> drop noise -> `writers.gdal` 0.25-0.5 m DSM -> Three.js heightfield (PlaneGeometry displacement) or Poisson mesh (Open3D/MeshLab/CloudCompare); mask with OSM way 28695389 or DataSF footprint; texture from NAIP or our splats. QGIS + Qgis2threejs exports terrain + extrusions directly.
- Three.js 3D Tiles streaming: https://github.com/NASA-AMMOS/3DTilesRendererJS (Apache-2.0); Giro3D demo https://giro3d-website-giro3d-44d14610d18b74aaf0dd10d7eb55f19bd6bbddc2d.gitlab.io/next/examples/google-photorealistic-3d-tiles.html

## Downloadable items
| Item | Where | Cost | Format | Fidelity | Verified |
|---|---|---|---|---|---|
| 3D Warehouse Cal Academy (3,694 polys, 2014) | https://3dwarehouse.sketchup.com/model/1a4c209a43561ba445f5590ac69325a5/California-Academy-of-Sciences | free Trimble acct | SKP (+DAE) -> glTF via Blender | low-medium massing | no |
| USGS 3DEP 2023 lidar | EPT above | free PD | EPT/LAZ -> DSM/mesh | high roof form, no colour | yes |
| NASA WERK 1 m DEM/DSM 2023 | https://wifire-data.sdsc.edu/dataset/nasa-werk-dem-ca-sanfrancisco-1-b23 | free | COG | medium-high heightfield | no |
| DataSF footprints w/ heights | https://data.sfgov.org/d/ynuv-fyni | free PDDL | GeoJSON/SHP | footprint | no |
| SF Building Masses 2017 LoD1 | https://geodata.lib.berkeley.edu/catalog/berkeley-s71t2s | free | KML/SHP/FGDB | LOD1 | no |
| Open City Model SF 06075 | S3 path above | free ODbL | CityGML/CityJSON | LOD1 | yes |
| Overture buildings | S3 GeoParquet | free | GeoParquet | LOD1 | no |
| OSM way 28695389 + neighbours | Overpass | free ODbL | GeoJSON | footprints | no |
| Cesium OSM Buildings 96188 | Cesium ion | free acct | 3D Tiles stream | LOD1 | no |
| Google Photorealistic 3D Tiles | tile.googleapis.com / ion 2275207 | GCP key | stream only | high textured | yes (code) |
| Vexcel 3D Cities SF | https://vexceldata.com/?p=9105 | commercial | 3D Tiles mesh | high | no |
| Cal Academy specimen scans | https://sketchfab.com/calacademy | request form | OBJ/glTF | props | no |

## Recommendation
1. Register everything to an ENU frame at 37.7699, -122.4661 (matches splat alignment).
2. Build the owned, bakeable asset from the 2023 lidar (roof hills, domes, concourse grading) masked by the footprint, textured from orthoimagery or our splats.
3. Use the 3D Warehouse model only as a low-poly stand-in for walls/entrance under the roof.
4. Stream Google 3D Tiles live for context (de Young, trees); do not bake.
5. If an offline textured mesh of the real building is required, the only lead is Vexcel 3D Cities (commercial).
