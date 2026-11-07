# Geospatial / LiDAR / Imagery Inventory — Cal Academy site, Golden Gate Park

Research track report. **[verified]** = fetched directly; **[search-sourced]** = from search snippets; **[unverified]** = prior knowledge.

## Site reference coordinates
- Centroid WGS84: 37.76986, -122.46609 (55 Music Concourse Dr)
- UTM 10N (EPSG:26910 / 6339): E 547,022  N 4,180,415 (de Young: E 546,793 N 4,180,590)
- EPSG:3857 bboxes for EPT queries: Academy only `[-13633020, -13632686, 4546844, 4547126]`; Academy + Concourse + de Young `[-13633521, -13632407, 4546633, 4547408]`; wider park chunk `[-13634411, -13631628, 4546281, 4547689]`
- San Francisco CS13 (EPSG:7131, native CRS of the 2023 lidar): Academy E~46,582 N~26,204 -> USGS 500 m tile **04650260**; de Young / west half -> **04600260**; south -> 04600255; NE -> 04650265.

## 1. USGS 3DEP LiDAR

### 1a. CA_SanFrancisco_1_B23 (2023, QL0) — BEST DATASET [verified]
- NV5 Geospatial, flown 2023-04-20, Riegl VQ-1560ii, **90.1 pts/m2 first-return**, 40.8 pts/m2 ground; RMSEz 3.2 cm.
- CRS: NAD83(2011) / SF CS13 (EPSG:7131) m; NAVD88 (GEOID18). LAS 1.4. Classes: 1 unclassified, 2 ground, 7/18 noise, 9 water, 17 bridge, 20 ignored ground. **Buildings not classified; roof points are class 1.**
- Deliverables: classified LAZ, 0.25 m bare-earth DEM, 1 m DEM. (0.25 m DSM/intensity not staged; build DSM from points.)
- Project report (62.9 MB PDF): https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/reports/CA_SanFrancisco_LiDAR_ProjectReport.pdf
- License: US Government public domain.

**Access A — Entwine EPT on AWS (no account, streamable)** [verified]
- `https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23/ept.json` — 13.09 B points, EPSG:3857, laszip.
- STAC: https://usgs-lidar-stac.s3-us-west-2.amazonaws.com/ept/CA_SanFrancisco_1_B23.json
- Boundary index: https://raw.githubusercontent.com/hobuinc/usgs-lidar/master/boundaries/resources.geojson

PDAL pipeline (clip bbox, reproject to UTM 10N, drop noise, write COPC):
```json
[
  {"type":"readers.ept",
   "filename":"https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23/ept.json",
   "bounds":"([-13633521,-13632407],[4546633,4547408])",
   "requests":16},
  {"type":"filters.range","limits":"Classification![7:7],Classification![18:18]"},
  {"type":"filters.reprojection","in_srs":"EPSG:3857","out_srs":"EPSG:26910"},
  {"type":"writers.copc","filename":"calacademy_2023_utm10.copc.laz"}
]
```
`pdal pipeline ept_clip.json`. Add `"resolution": 0.5` to readers.ept for a preview. DSM: append `{"type":"writers.gdal","filename":"dsm_025m.tif","resolution":0.25,"output_type":"max","gdaldriver":"GTiff"}`; DTM: filter `Classification[2:2]`, `output_type: idw`. Height above ground: `filters.hag_nn`. Roof only: `filters.crop` with the footprint polygon WKT in EPSG:3857.

**Access B — staged 500 m LAZ tiles (EPSG:7131, LAS 1.4)**
- Link list (652 tiles): https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/LPC/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/0_file_download_links.txt
- VPC: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/LPC/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/CA_SanFrancisco_1_B23.vpc
- Site tiles (~190-197 MB each): `https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/LAZ/USGS_LPC_CA_SanFrancisco_B23_04650260.laz` (Academy), `_04600260.laz` (de Young), `_04600255`, `_04650255`, `_04600265`, `_04650265`, `_04700255/260/265`.
- Per-tile XML: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/LPC/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/metadata/USGS_LPC_CA_SanFrancisco_B23_04650260.xml

**Access C — 0.25 m OPR bare-earth DEM tiles (GeoTIFF)** [verified HEAD 200, 12.98 MB]
- https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/OPR/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/TIFF/USGS_OPR_CA_SanFrancisco_B23_04650260.tif (+ `_04600260`, `_04600255`, `_04650255`, `_04650265`, `_04600265`)
- VRT mosaic: `.../OPR/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/CA_SanFrancisco_1_B23.vrt`
- `gdalwarp -t_srs EPSG:26910 -te 546400 4180000 547500 4180900 -tr 0.25 0.25 /vsicurl/<vrt> site_dtm_025.tif`

**Access D — USGS 1 m DEM (UTM 10N)** [verified]
- https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SanFrancisco_B23/TIFF/USGS_1M_10_x54y418_CA_SanFrancisco_B23.tif (176.6 MB) and `USGS_1M_10_x54y419_CA_SanFrancisco_B23.tif` (111.9 MB); mosaic both.

**Access E — The National Map**: GUI https://apps.nationalmap.gov/downloader/ ; API `https://tnmaccess.nationalmap.gov/api/v1/products?bbox=-122.4720,37.7675,-122.4620,37.7730&datasets=Lidar%20Point%20Cloud%20(LPC)&outputFormat=JSON`

### 1b. ARRA-CA_GoldenGate_2010 (2010, ~2 pts/m2) — early post-construction baseline [verified]
- EPT: https://s3-us-west-2.amazonaws.com/usgs-lidar-public/ARRA-CA_GoldenGate_2010/ept.json (8.78 B pts)
- NOAA Digital Coast COPC (DAV 5007, UTM10N NAVD88): Academy tile `https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/5007/20100512_ca_arra_goldengate_0915.copc.laz`; de Young tile `.../5007/20100529_ca_arra_goldengate_0875.copc.laz`; metadata `.../5007/metadata_ca2010_arra_goldengate.xml`; NOAA EPT `https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/entwine/geoid18/5007/ept.json`
- PDAL: `{"type":"readers.copc","filename":"<url>","bounds":"([546500,547400],[4180150,4180770])"}`

### 1c. USGS_LPC_CA_NoCAL_Wildfires_B5b_2018 [EPT verified]
- https://s3-us-west-2.amazonaws.com/usgs-lidar-public/USGS_LPC_CA_NoCAL_Wildfires_B5b_2018/ept.json (28.7 B pts); covers site; density unverified (QL1/QL2).

### 1d. Not covering the site
2010 SanFranCoast (DAV 1406) coastal strip; 2025 SF Bay-Delta (DAV 14673) baylands; 2004 SF Bay coarse.

### 1e. Planetary Computer derived 3DEP rasters
STAC `https://planetarycomputer.microsoft.com/api/stac/v1`, collections `3dep-lidar-dsm`, `-dtm`, `-hag`, `-intensity`, `-classification`, `-copc`. Coarse (2 m); 2023 ingestion unverified.

## 2. San Francisco open data (DataSF / Socrata) [IDs search-sourced]
Export: `https://data.sfgov.org/api/geospatial/<ID>?method=export&format=GeoJSON` ; SODA bbox: `https://data.sfgov.org/resource/<ID>.geojson?$where=within_box(shape,37.7730,-122.4720,37.7675,-122.4620)&$limit=5000`

| Dataset | ID | Notes |
|---|---|---|
| Building Footprints (lidar heights) | **ynuv-fyni** | 2010 lidar heights (`hgt_mediancm`, `hgt_maxcm`, `gnd_mincm`); Academy included; CC0/PDDL |
| Building Footprints (FGDB) | **asx6-3trm** | same with multipatch |
| Elevation Contours | **rnbg-2qxw** | lidar-derived |
| Urban Tree Canopy | **ni2e-vpbg** | Planning canopy polygons |
| Street Tree List | **tkzw-k3nq** | DPW street trees only; **no Golden Gate Park trees** (RPD) |
| RPD Parks | **3nje-yn2u** | park polygons |
| RPD Facilities | gtr9-ntp6 [unverified] | |
| Parcels | acdm-wktn [unverified] | |
| SF Aerial Photos 1938-2022 | https://sfplanninggis.org/1938/ | viewer only |
| SFGIS enterprise imagery (Pictometry) | https://sfgis-img.sfgov.org/ | licensed, not open |
| Footprint field standards | https://sfdigitalservices.gitbook.io/data-standards-guide/standard-reference-data/basemap/building-footprints | |

## 3. Aerial / ortho imagery
- NAIP (public domain): CA 2022 (60 cm RGBN), 2020, 2018, 2016, 2014 (1 m), 2012, 2010, 2009, 2005. Planetary Computer STAC collection `naip` (notebook https://github.com/microsoft/PlanetaryComputerExamples/blob/main/datasets/naip/naip-example.ipynb); GEE `USDA/NAIP/DOQQ`; EarthExplorer https://earthexplorer.usgs.gov (quad San Francisco North 3712237).
- Google Earth Pro historical imagery (not downloadable): brackets demolition 2005, construction 2005-2008, opening Sept 2008; 1938 Harrison Ryker composite.
- Commercial: Nearmap (~5.5 cm + 3D mesh), Vexcel, EagleView, Hexagon. None open.

## 4. Terrain / roof elevation
- Best DTM: 0.25 m OPR tiles. Best DSM: build from the 2023 EPT at 0.25 m.
- OpenTopography API (free key): `https://portal.opentopography.org/API/usgsdem?datasetName=USGS1m&south=37.7675&north=37.7730&west=-122.4720&east=-122.4620&outputFormat=GTiff&API_Key=KEY`
- **The Living Roof hills are resolvable in the 2023 lidar** (90 pts/m2, 3 cm RMSEz): the two 27 m domes and skylight portholes at ~10 cm. Isolate roof points with the footprint polygon (class 1); use last returns or low-percentile Z per cell to approximate soil surface under vegetation. 2010 data shows the same hills coarsely for a time comparison.

## 5. OpenStreetMap
Candidate Academy way: https://www.openstreetmap.org/way/28695389 [unverified]. Overpass query:
```
[out:json][timeout:60];
(
  way["name"~"California Academy of Sciences"](37.766,-122.475,37.775,-122.458);
  relation["name"~"California Academy of Sciences"](37.766,-122.475,37.775,-122.458);
  way["name"~"de Young"](37.766,-122.475,37.775,-122.458);
  way["building"](37.7670,-122.4730,37.7735,-122.4610);
  way["highway"](37.7670,-122.4730,37.7735,-122.4610);
  way["natural"="water"](37.7670,-122.4730,37.7735,-122.4610);
  node["natural"="tree"](37.7670,-122.4730,37.7735,-122.4610);
  way["leisure"](37.7670,-122.4730,37.7735,-122.4610);
  nwr["name"~"Music Concourse|Spreckels Temple of Music|Bandshell"](37.766,-122.475,37.775,-122.458);
);
out body; >; out skel qt;
```
`curl -G https://overpass-api.de/api/interpreter --data-urlencode "data=<query>" | osmtogeojson > site.geojson` or `wget -O site.osm "https://overpass-api.de/api/map?bbox=-122.4730,37.7670,-122.4610,37.7735"`. SF building heights imported 2016 from DataSF: https://wiki.openstreetmap.org/wiki/San_Francisco_Building_Height_Import . ODbL.

## 6. Satellite
Sentinel-2 L2A (10 m) via AWS Earth Search `https://earth-search.aws.element84.com/v1` collection `sentinel-2-l2a`, tile 10SEG; Landsat via GEE. Sub-meter commercial only; NAIP 60 cm is the only free sub-meter option.

## 7. Street-level
- Google Street View: outdoor on Music Concourse Dr, Bowl Dr, Tea Garden Dr, JFK Dr. Indoor Street View reportedly exists for the Skulls exhibit (https://www.mentalfloss.com/article/62969/explore-room-skulls-google-street-view) — contradicts the imagery track; check Pegman in Maps. Not downloadable.
- Mapillary (CC BY-SA 4.0, API v4, free token): `https://graph.mapillary.com/images?access_token=MLY|APP_ID|TOKEN&fields=id,captured_at,compass_angle,computed_geometry,camera_type,is_pano,thumb_2048_url,thumb_original_url,sfm_cluster,sequence&bbox=-122.4720,37.7675,-122.4620,37.7730&limit=2000` ; `sfm_cluster` gives Mapillary's SfM point cloud for a sequence (seed for splat registration).
- KartaView: `https://api.openstreetcam.org/2.0/photo/?lat=37.76986&lng=-122.46609&radius=300` [unverified]

## 8. Living Roof specifics
2.5 acres, seven hills, ~1.7M plants of nine natives in ~50,000 coir BioTrays, ~15 cm medium; Rana Creek, SWA, Arup, RPBW/Stantec; opened 2008-09-27. Rooftop weather station drives skylights; **no public feed**. No as-built roof survey; derive from 2023 lidar. Landscape Performance case study: https://www.landscapeperformance.org/case-study-briefs/ca-academy-green-roof

## 9. Historic maps & photos
- David Rumsey: "Map of the Golden Gate Park" George W. Blum 1896, 1:9,600 — https://eddie.lunaimaging.com/luna/servlet/detail/RUMSEY~8~1~1576~170034 (Luna export; CC BY-NC-SA). Search davidrumsey.com for "Midwinter", "Golden Gate Park".
- 1894 Midwinter Fair: Osher Map Library https://oshermaps.org/print?id=96470 ; Calisphere bird's-eye https://calisphere.org/item/361ca55ff4fe372edb95352486793f67/ ; OpenSFHistory https://opensfhistory.org/photoset/midwinter-fair-1894 ; FoundSF https://foundsf.org/The_1894_Midwinter_Fair_in_Golden_Gate_Park . The Music Concourse is the fair's sunken Grand Court.
- Sanborn: LOC SF 1913-1950 https://www.loc.gov/item/sanborn00813_030/ ; Stanford 1913 vol. 6 "Golden Gate Park to Presidio" https://purl.stanford.edu/rd688nr3247 (IIIF).
- SFPL: https://digitalsf.org ; https://sfmemory.org ; OpenSFHistory (wnp27.0784, 1926 Steinhart sea-lion pool); Academy archives https://research.calacademy.org/research/library/special/buildings/N1396.htm
- USGS 1915 topo quad (Rumsey); 1938 aerial composite https://sfplanninggis.org/1938/

## Downloadable items
| # | Item | URL | Res/density | Date | Format | Size | License | Verified |
|---|---|---|---|---|---|---|---|---|
| 1 | 3DEP CA_SanFrancisco_1_B23 EPT | https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23/ept.json | 90 pts/m2 | 2023 | EPT/LAZ 3857 | site clip ~50-100M pts | PD | yes |
| 2 | B23 LAZ tile 04650260 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/LAZ/USGS_LPC_CA_SanFrancisco_B23_04650260.laz | same | 2023 | LAZ 1.4 EPSG:7131 | ~197 MB | PD | link list |
| 3 | B23 LAZ tile 04600260 | .../USGS_LPC_CA_SanFrancisco_B23_04600260.laz | same | 2023 | LAZ | ~192 MB | PD | link list |
| 4 | B23 OPR 0.25 m DEM 04650260 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/OPR/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/TIFF/USGS_OPR_CA_SanFrancisco_B23_04650260.tif | 0.25 m | 2023 | GeoTIFF | 13 MB | PD | yes |
| 5 | USGS 1 m DEM x54y418/x54y419 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SanFrancisco_B23/TIFF/USGS_1M_10_x54y418_CA_SanFrancisco_B23.tif | 1 m | 2023 | GeoTIFF | 177 / 112 MB | PD | yes |
| 6 | B23 project report | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/reports/CA_SanFrancisco_LiDAR_ProjectReport.pdf | | 2024 | PDF | 63 MB | PD | yes |
| 7 | ARRA GoldenGate 2010 EPT | https://s3-us-west-2.amazonaws.com/usgs-lidar-public/ARRA-CA_GoldenGate_2010/ept.json | ~2 pts/m2 | 2010 | EPT | | PD | yes |
| 8 | 2010 COPC tile 0915 (Academy) | https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/5007/20100512_ca_arra_goldengate_0915.copc.laz | ~2 pts/m2 | 2010 | COPC UTM10N | tens of MB | PD | yes |
| 9 | 2010 COPC tile 0875 (de Young) | .../5007/20100529_ca_arra_goldengate_0875.copc.laz | | 2010 | COPC | | PD | yes |
| 10 | NoCAL Wildfires 2018 EPT | https://s3-us-west-2.amazonaws.com/usgs-lidar-public/USGS_LPC_CA_NoCAL_Wildfires_B5b_2018/ept.json | QL1/2? | 2018 | EPT | | PD | yes |
| 11 | EPT boundary index | https://raw.githubusercontent.com/hobuinc/usgs-lidar/master/boundaries/resources.geojson | | live | GeoJSON | 9 MB | PD | yes |
| 12 | DataSF Building Footprints | https://data.sfgov.org/api/geospatial/ynuv-fyni?method=export&format=GeoJSON | 50 cm heights | 2010/2017 | GeoJSON | 100+ MB | PDDL | search |
| 13 | DataSF Contours | https://data.sfgov.org/api/geospatial/rnbg-2qxw?method=export&format=GeoJSON | | ~2010 | GeoJSON | large | PDDL | search |
| 14 | DataSF Tree Canopy | https://data.sfgov.org/api/geospatial/ni2e-vpbg?method=export&format=GeoJSON | | | GeoJSON | | PDDL | search |
| 15 | DataSF RPD Parks | https://data.sfgov.org/api/geospatial/3nje-yn2u?method=export&format=GeoJSON | | | GeoJSON | small | PDDL | search |
| 16 | NAIP 2022 CA | Planetary Computer STAC `naip` / GEE / EarthExplorer | 60 cm | 2022 | COG | ~400 MB/DOQQ | PD | notebook |
| 17 | OpenTopography USGS1m | API above | 1 m | | GeoTIFF | 4 MB | PD | search |
| 18 | OSM site extract | Overpass query above | vector | live | GeoJSON | <5 MB | ODbL | blocked |
| 19 | Mapillary bbox | API above | street-level | 2014-now | JSON+JPEG | | CC BY-SA | search |
| 20 | Rumsey 1896 Blum map | https://eddie.lunaimaging.com/luna/servlet/detail/RUMSEY~8~1~1576~170034 | 1:9,600 | 1896 | JPEG/TIFF | 50-200 MB | CC BY-NC-SA | search |
| 21 | LOC Sanborn SF 1913-1950 | https://www.loc.gov/item/sanborn00813_030/ | | 1913-50 | JP2/TIFF | | PD | search |
| 22 | Stanford 1913 Sanborn vol 6 | https://purl.stanford.edu/rd688nr3247 | | 1913 | IIIF | | PD | search |
| 23 | Osher Midwinter Expo view | https://oshermaps.org/print?id=96470 | | 1894 | JPEG | | edu | search |
| 24 | OpenSFHistory Midwinter Fair | https://opensfhistory.org/photoset/midwinter-fair-1894 | | 1894 | JPEG | | WNP | search |
| 25 | SF Planning 1938 aerial | https://sfplanninggis.org/1938/ | ~1 ft | 1938+ | tiles | | City | search |

**Registration workflow:** clip 2023 EPT -> UTM10N COPC; build 0.25 m DSM + OPR DTM; extract roof via footprint polygon; ICP iPhone splats to roof DSM + concourse ground after GPS/compass coarse alignment; NAIP 2022 for context texture; 2010 COPC for a time-lapse; for the "planet", map easting/northing to lon/lat on an exaggerated-radius sphere.
