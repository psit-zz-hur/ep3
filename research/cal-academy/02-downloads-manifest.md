# Downloads manifest — for the laptop session

Priority order. `laptop-bootstrap.sh` fetches everything marked AUTO. Items marked MANUAL need a
browser, an account, or a judgement call on rights. Rights: PD = public domain, ARR = all rights
reserved (reference only; do not redistribute), CC = Creative Commons (check per file).

## A. Geometry ground truth (AUTO)
| # | Item | URL | Format | Size | Rights |
|---|---|---|---|---|---|
| A1 | USGS 3DEP 2023 lidar EPT (stream, clip to bbox) | https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23/ept.json | EPT/LAZ, EPSG:3857 | site clip ~22M pts / 150 MB | PD |
| A2 | 2023 LAZ tile 04650260 (Academy, native EPSG:7131) | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/LAZ/USGS_LPC_CA_SanFrancisco_B23_04650260.laz | LAZ 1.4 | ~197 MB | PD |
| A3 | 2023 LAZ tile 04600260 (de Young) | .../USGS_LPC_CA_SanFrancisco_B23_04600260.laz | LAZ | ~192 MB | PD |
| A4 | 2023 0.25 m bare-earth DEM 04650260 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/OPR/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/TIFF/USGS_OPR_CA_SanFrancisco_B23_04650260.tif | GeoTIFF | 13 MB | PD |
| A5 | 2023 1 m DEM tiles x54y418, x54y419 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SanFrancisco_B23/TIFF/USGS_1M_10_x54y418_CA_SanFrancisco_B23.tif | GeoTIFF | 177 + 112 MB | PD |
| A6 | 2010 lidar COPC tile 0915 (Academy, UTM10N) | https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/5007/20100512_ca_arra_goldengate_0915.copc.laz | COPC | 37 MB | PD |
| A7 | 2010 lidar COPC tile 0875 (de Young) | https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/5007/20100529_ca_arra_goldengate_0875.copc.laz | COPC | ~40 MB | PD |
| A8 | 2023 lidar project report | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/reports/CA_SanFrancisco_LiDAR_ProjectReport.pdf | PDF | 63 MB | PD |
| A9 | OSM site extract | https://overpass-api.de/api/map?bbox=-122.4740,37.7660,-122.4600,37.7740 | OSM XML | <5 MB | ODbL |
| A10 | DataSF building footprints with lidar heights | https://data.sfgov.org/api/geospatial/ynuv-fyni?method=export&format=GeoJSON | GeoJSON | 100+ MB | PDDL |
| A11 | DataSF tree canopy | https://data.sfgov.org/api/geospatial/ni2e-vpbg?method=export&format=GeoJSON | GeoJSON | large | PDDL |
| A12 | DataSF parks | https://data.sfgov.org/api/geospatial/3nje-yn2u?method=export&format=GeoJSON | GeoJSON | small | PDDL |
| A13 | 2018 NoCAL Wildfires lidar EPT (mid-date check) | https://s3-us-west-2.amazonaws.com/usgs-lidar-public/USGS_LPC_CA_NoCAL_Wildfires_B5b_2018/ept.json | EPT | stream | PD |

## B. Drawings (AUTO, reference only, © RPBW)
| # | Item | URL | Format | Size |
|---|---|---|---|---|
| B1 | Fondazione catalogue (17 drawings + models) | https://www.fondazionerenzopiano.org/en/project/california-academy-of-sciences.pdf | PDF | 15 MB |
| B2 | Fondazione booklet (old campus plan, 2 long sections) | https://www.fondazionerenzopiano.org/en/page/california-california-academy-of-sciences/download-book | PDF | 12 MB |
| B3-B19 | 17 sheet PDFs | https://www.fondazionerenzopiano.org/en/project/california-academy-of-sciences/drawing-{235,352,289,613,337,243,240,336,275,328,279,285,311,354,355,303,304}.pdf | PDF | ~150 KB each |
| B20 | ArchDaily gallery (47 large images incl. ground plan, site plan, sections) | https://www.archdaily.com/6810/california-academy-of-sciences-renzo-piano (images: swap `medium_jpg` -> `large_jpg` in `images.adsttc.com/media/images/5010/.../stringio.jpg`) | JPG | ~300 KB each |
| B21 | RPBW long section | https://cdn.sanity.io/images/zi3g9jaq/production/9037e5ae3a056f89e4e311055a5b8f15e203f05c-1400x343.jpg | JPG | small |
| B22 | RPBW roof section detail | https://cdn.sanity.io/images/zi3g9jaq/production/4c998f3c54927ae6e708e8583119c19361fd92db-1320x1023.jpg | JPG | small |

## C. Photos (AUTO where CC; MANUAL where ARR)
| # | Item | URL | Rights |
|---|---|---|---|
| C1 | Commons category: Interior (109), Roof (104), Exterior (37) | https://commons.wikimedia.org/wiki/Category:Main_building_of_the_California_Academy_of_Sciences | CC BY / BY-SA / PD |
| C2 | LOC Highsmith living roof TIFFs | https://www.loc.gov/item/2010630214/ ; https://www.loc.gov/item/2010630212/ | PD (browser; Cloudflare) |
| C3 | Flickr CC search | https://www.flickr.com/search/?text=California%20Academy%20of%20Sciences&license=4%2C5%2C6%2C9%2C10 | CC (manual) |
| C4 | YouTube 4K walkthroughs for frame extraction | https://www.youtube.com/watch?v=gWMpO8nj-4c ; https://www.youtube.com/watch?v=2uDg4jiDLd8 | personal research use only |
| C5 | Construction time-lapse | https://www.youtube.com/watch?v=9VXMdHWJzNQ | © CAS |

## D. Historic maps (AUTO)
| # | Item | URL | Rights |
|---|---|---|---|
| D1 | 1896 Blum Map of Golden Gate Park (8537 x 1907) | https://www.davidrumsey.com/luna/servlet/iiif/RUMSEY~8~1~1576~170034/full/full/0/default.jpg | CC BY-NC-SA |
| D2 | 1948 SF Aerial Photo Survey sheet 131, concourse region | https://www.davidrumsey.com/luna/servlet/iiif/RUMSEY~8~1~313936~90082810/6550,6075,10500,9550/full/0/default.jpg (use tiles; IIIF caps single requests) | CC BY-NC-SA |
| D3 | 1905 Sanborn vol. 6 index | https://www.davidrumsey.com/luna/servlet/iiif/RUMSEY~8~1~214199~5501554/full/full/0/default.jpg | CC BY-NC-SA |
| D4 | HALS CA-49 Golden Gate Park drawing | https://tile.loc.gov/storage-services/master/pnp/habshaer/ca/ca3600/ca3693/sheet/00001a.tif | PD (browser) |
| D5 | SF Planning 1938 aerial viewer | https://sfplanninggis.org/1938/ | viewer only |

## E. 3D models (MANUAL)
| # | Item | URL | Notes |
|---|---|---|---|
| E1 | 3D Warehouse Cal Academy (3,694 polys, 2014) | https://3dwarehouse.sketchup.com/model/1a4c209a43561ba445f5590ac69325a5/California-Academy-of-Sciences | free Trimble account; SKP/DAE |
| E2 | Google Photorealistic 3D Tiles | https://tile.googleapis.com/v1/3dtiles/root.json?key=API_KEY | stream only, no export |
| E3 | Cesium OSM Buildings (ion 96188) | https://cesium.com/platform/cesium-ion/content/cesium-osm-buildings/ | free account |
| E4 | Open City Model SF (LOD1 CityJSON) | https://s3.dualstack.us-east-1.amazonaws.com/opencitymodel/2019-jun/json/California/06075/ | ODbL |
| E5 | NASA WERK 1 m DSM SF 2023 | https://wifire-data.sdsc.edu/dataset/nasa-werk-dem-ca-sanfrancisco-1-b23 | COG |

## F. Museum data (API, no download needed)
See 05-museum-data-and-apis.md: GBIF publisher 66522820-055c-11d8-b84e-b8a03c50a862; iNaturalist radius queries; USGS earthquake GeoJSON; NOAA tides 9414290; NWS points API; eBird hotspot L109439; ProPublica 990 EIN 94-1156258.

## G. Software (laptop)
PDAL + laspy/lazrs, GDAL, CloudCompare, SuperSplat (browser), `npm i @playcanvas/splat-transform`, `npm i @sparkjsdev/spark three`, Brush (Apple Silicon) or Postshot (Windows/NVIDIA), `pip install nerfstudio` (CUDA only), descaniverse (https://github.com/jampekka/descaniverse), SPZ tools (https://github.com/nianticlabs/spz).
