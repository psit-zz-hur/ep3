# Pre-colonial Golden Gate Park: sources census, georeferencing, habitat METHOD (2026-11-07A)

Brief: `20-ggp-precolonial-brief.md`. Grid C = EPSG:32610, E 544023..550023, N 4177411..4183411, 1200 x 1200 at 5 m.
Scripts: `research/cal-academy/scripts/precolonial_georef.py`, `precolonial_features.py`, `precolonial_habitat.py`, `precolonial_water.py`, `precolonial_elk.py`, `precolonial_proof.py`.
Outputs: `exports/territory/precolonial/` (git-ignored). Downloads: `data/cal-academy/precolonial/`.

## 0. Two findings first

1. **Grid C does not contain Ocean Beach.** Its west edge E 544023 is lon -122.5003. Ocean Beach at the park is lon -122.511 (E 543067), Lands End is E 543031. Grid C only holds the Golden Gate strait in its NW corner, so class 1 (beach) and class 9 (rocky shore) can barely appear in it. I built the habitat raster on an **extended grid CW** (grid C plus 1500 m west and 1000 m south: E 542523..550023, N 4172411..4183411, 1500 x 2200, same 5 m lattice) and wrote grid C as an exact clip. Use CW for the planet.
2. **The NOAA T-sheets are not GeoTIFFs.** The Historical Map & Chart Collection serves plain JPG scans (8-9 k px wide, 300 dpi, ~0.85 m/px at 1:10 000). The catalog footprints are wrong boxes. I georeferenced one sheet myself (section 2). The 1852 sheet is the best single source: it draws vegetation symbols, lakes, dune sand and contours.

## 1. Sources census

### (a) US Coast Survey T-sheets, 1852-1857 (lon -122.51..-122.44, lat 37.74..37.80)
NOAA Office of Coast Survey, Historical Map & Chart Collection. Search endpoint used: `https://historicalcharts.noaa.gov/includes/imageDBDT.php` (type T-Sheet, state CA); download `https://historicalcharts.noaa.gov/includes/downloadsingle.php?filename=<ID>&fileExt=.jpg`. Public domain (US government). Landing: https://historicalcharts.noaa.gov/

| Sheet | Year | Title | Scale | Coverage | Status |
|---|---|---|---|---|---|
| **T00382** | 1852 (A.D. Bache Supt, A.M. Harrison) | Part of the Coast of California from Point Lobos Southward | 1:10 000 | Point Lobos (N 4182.3k) south to ~lat 37.69, Ocean Beach to ~lon -122.470 (E ~546 600). Whole western park, Sand Hills, Lake Merced. | **downloaded, georeferenced, used** |
| T00382A | 1873 (tracing of the Military Map; "sand limit survey" May 1873) | Nearby Bay Area of California, San Francisco Peninsula (Military) | n/a | Fort Point to Lake Merced, east to Laguna Honda; blue line = drifting-sand limit, Frear stone monuments | downloaded, **not** georeferenced (useful next: sand-limit line, 1873 so already post-park) |
| T00663 | 1857 | Survey of Lighthouses and Defensive Works of Harbor of San Francisco | 1:10 000 | Golden Gate, Presidio, Point Lobos to Fort Point, Lime Point | downloaded, **not** georeferenced (next for the Presidio / Lobos Creek / north of grid) |
| T00687 | 1857 (plane table sheet XXXI, A.F. Rodgers) | City of San Francisco and Its Vicinity | 1:10 000 | Presidio east, park east of ~lon -122.467, city, Mission Bay | downloaded, **not** georeferenced (next for the park's east strip) |
| T01619 / T01631 | 1882 | City of San Francisco / Point Lobos Southward and Eastward | 1:10 000 | post-park, built-up | listed only; not 1850s, not downloaded |
| T02128 | 1892 | Revisory Survey of Golden Gate Entrance | | | listed only |

Files: `data/cal-academy/precolonial/noaa_tsheets/T00382-00-1852.jpg`, `T00382a-00-1873.jpg`, `T00663-00-1857.jpg`, `T00687-00-1857.jpg` (sizes 23.6, 27.3, 21.6, 32.1 MB).
NOAA Shoreline Data Explorer / NGS Shoreline Data Rescue (`https://shoreline.noaa.gov/data/`, InPort items for CA37B08 "City of San Francisco and its Vicinity 1857") serve vector shorelines, not scans; the NSDE pages returned 403 to me. [unverified: whether a georeferenced T-sheet raster exists there.]
Judgment: T00382 is the one 1850s sheet that carries the west-side ecology. Use T00663 and T00687 to extend.

### (b) SFEI historical ecology
- **Historical Ecology GIS Data Compilation v2.3** https://www.sfei.org/data/historical-ecology-gis-data-compilation ; zip https://www.sfei.org/sites/default/files/data/HE_Compilation_v2.3.zip (51 MB file geodatabase, downloaded and opened). Licence GNU GPL v3 (stated on the page). Layers: 38 902 habitat polygons, 87 305 channel lines, 22 project boundaries. **West side of San Francisco: no coverage.** One bayside project ("Historical Baylands", 1998) intersects my west-side bbox at its eastern edge; zero channel features. Judgment: nothing usable for the Outer Lands.
- **Hidden Nature SF** (SFEI, 2019-2021, v1.0) https://sfei.org/node/7503 ; https://sites.google.com/sfei.org/hidden-nature-sf/learn ; web map https://map.hidden-nature.org/home . Phase 1 "mapped the northern portion of the San Francisco peninsula" (page text); later phases south. It does cover interdune ponds and dunes by description. **No GIS download and no licence statement found** (page gives a citation: "San Francisco Estuary Institute. 2021. Hidden Nature SF, version 1.0."). [unverified: whether the map layers cover the park/Sunset; the map is a JS app I could not query.] Judgment: ask SFEI for the polygons; do not scrape the map.

### (c) Lost lakes and creeks maps
- **Seep City** (Joel Pomerantz, Thinkwalks) https://seepcity.joelpomerantz.com/ ; method/licence page https://seepcity.joelpomerantz.com/learn.html . Printed poster/shower curtain. Licence on its page: **CC BY-NC-SA 4.0**; "a full digital copy of the map is available only by arrangement" (search summary of the page). Shows lakes with no fixed shoreline that shrank into the dunes. Not downloaded. Judgment: reference only; ask Joel for a digital copy if we want the lake outlines.
- **Hidden Nature SF**: see (b).
- **Oakland Museum of California "Guide to San Francisco Bay Area Creeks"** (OMCA, William Lettis & Associates, SFEI) https://explore.museumca.org/creeks/GIS/index.html (Cloudflare challenge blocked me [unverified page content]). Its data is mirrored as the CNRA ArcGIS layer https://gis.cnra.ca.gov/arcgis/rest/services/Ocean/CSMW_San_Francisco_Bay_Historical_Creeks/MapServer/0 , which I queried (16 features in lon -122.52..-122.43, lat 37.73..37.80, polylines; layer licence not stated [unverified]). It is mostly bayside creeks (Arroyo Dolores, Islais Creek, Hayes Creek) plus a few unnamed stubs near Lake Merced / the Sunset; **no Lobos Creek**. Written into the water GeoJSON.

### (d) Presidio Trust / GGNRA dune and Lobos Creek documents
- Presidio Trust, Lobos Creek Valley: https://presidio.gov/explore/attractions/lobos-creek-valley-trail ; Golden Gate National Parks Conservancy, Lobos Creek: https://www.parksconservancy.org/projects/lobos-creek . Text: "just 200 years ago Lobos Creek Valley was part of a vast system of sand dunes covering one-third of San Francisco"; first major Presidio restoration after 1994; San Francisco lessingia.
- NPS 2001 Presidio Vegetation Management Plan, https://www.nps.gov/goga/learn/management/upload/-1455-Presidio-vegetation-management-plan_2001.pdf (404 on my fetch [unverified, find the current link]); 1995 "Restoration Plan for Lobos Creek" (cited by NPSpecies, not fetched).
- FoundSF "Native Flora of San Francisco" (Holloran 1998; Howell 1934) https://foundsf.org/Native_Flora_of_San_Francisco : Presidio >260 native species, native plant communities on 145 acres. **Species named by Howell for dune/strand/scrub:** Chorizanthe cuspidata (SF spineflower), Cryptantha leiocarpa, Lessingia germanorum (SF lessingia), Baccharis pilularis (coyote brush), Ericameria ericoides (mock heather), Phacelia distans, Croton californicus, Camissonia cheiranthifolia; **swale at Lake Merced:** willows, California sweet gale, Cirsium (thistles). A UC eScholarship study (https://escholarship.org/content/qt71r6m3rx/qt71r6m3rx.pdf, not fetched, snippet only) names northern foredune, central dune scrub and central coast arroyo willow riparian for the historical dunes. [unverified: no single plant-community list per class from a Trust/GGNRA document; the class names in the legend follow Holland/CNPS usage.]
Judgment: enough to name classes 2, 3, 6 and give species for labels; not a quantitative cover map.

### (e) Ramaytush Ohlone / Yelamu, Outer Lands (named sites from the literature only)
- NPS Golden Gate, "Home of the Yelamu" https://www.nps.gov/places/000/8-home-of-the-yelamu.htm : Yelamu territory included today's Crissy Field; winter villages **Tubsinte, Sitlintac, Petlenuc**; summer/fall villages **Chutchui, Amuctac**.
- NPS "Ohlones and Coast Miwoks" https://home.nps.gov/goga/learn/historyculture/ohlones-and-coast-miwoks.htm : "In San Francisco, the villages were located at today's Fort Mason, Crissy Field, and Sutro Baths."
- Also Wikipedia Yelamu / List of Ohlone villages (https://en.wikipedia.org/wiki/Yelamu), Presidio El Polin Spring (search summary only [unverified]).
- **No named site in the Outer Sunset or the park interior turned up.** The only Outer Lands site named is Sutro Baths (Lands End). Ramaytush is the language group. Nothing invented; the habitat layer carries no village points.

### (f) Georeferenced historical-habitat GIS for SF
- SFEI compilation (above): none west. OMCA creeks (above): east-biased.
- David Rumsey: https://www.davidrumsey.com/ (CC BY-NC-SA). Search showed a georeferenced Rumsey layer of an 1859 Coast Survey sheet titled "Entrance to San Francisco Bay California" (Stanford/Berkeley records, bbox -122.72..-122.15, 37.66..37.94, e.g. https://geodata.lib.berkeley.edu/catalog/stanford-xz007mk8152) ; "City of San Francisco and its vicinity" 1859 appears in Rumsey (https://davidrumsey.com/luna/servlet/detail/RUMSEY~8~1~239938~5512085) but **I found no georeferenced copy of that exact sheet**. It is the same survey as NOAA T00687 anyway. Berkeley Library catalog pages are behind an Anubis challenge [unverified].
- Wackenreuder: 1861/1863 "City and County of San Francisco" (Berkeley record https://geodata.lib.berkeley.edu/catalog/stanford-vx863mc2329) , no georeferenced raster confirmed. A 1869 Coast Survey "Golden Gate, Ocean Beach, Laguna de la Merced" photocopy is in UC Riverside's collection (https://public.ucrlib.aspace.cdlib.org/repositories/5/archival_objects/181499), not a GIS.
- SF Planning historic creek layer: not found on DataSF [unverified].
Judgment: no ready habitat GIS exists for the west side. The T-sheets are the primary source.

## 2. Georeferencing (T00382, 1852)

Method: control points in the sheet's JPG pixels, 6-parameter affine to EPSG:32610.
1. 1947 pencil datum note "NA 1927 Datum 10-20-47 C.P.R." with green crosshair at 122 deg 31' W, 37 deg 45' N, px (1250, 5510). NAD27, converted with pyproj.
2. Same kind of note at 122 deg 30', 37 deg 42', px (2405, 12200).
3. "Round Top" summit ring = Strawberry Hill, px (5846, 3500), tied to OSM Strawberry Hill nodes.
4. Summit ring of Grand View Hill, px (6083, 5127), tied to OSM Grand View Hill.
Result: pixel 0.846 m, sheet rotated 5.8 deg (the sheet is drawn to magnetic north, not true), **fit RMS 3.6 m, leave-one-out 10.5 / 10.6 m (hills) and 44-46 m (the two datum crossings predicted from the other three)**. So absolute accuracy is about 10-45 m. Independent checks: today's Stow Lake / Strawberry Hill contour and Lake Merced overlay sit on the sheet's hill and lake; the modern Ocean Beach shoreline lies about 40-50 m west of the sheet's beach edge (the beach has grown seaward, expected). The CRS is NAD83; nothing was warped to correct 1850s survey error.
Outputs (uint8 RGB, 0 = no sheet; the sheet paper margin and title block are inside the footprint):
- `CALACADEMY_TSHEET_1850s_5m_UTM10N_2026_11_07A.tif` (grid C, 1200 x 1200; sheet covers about 1.0 M of 1.44 M cells, west part only)
- `CALACADEMY_TSHEET_1850s_5m_CW_UTM10N_2026_11_07A.tif` (grid CW)
- `CALACADEMY_TSHEET_1850s_PARKBBOX_1m_UTM10N_2026_11_07A.tif` (lon -122.5120..-122.4520, lat 37.7635..37.7750 = E 542982..548260, N 4179687..4180993, 5278 x 1306 at 1 m, cubic; the scan is 0.85 m so 1 m is supported; the east ~1.6 km of this box is off the sheet)
- `CALACADEMY_TSHEET_T00382_GEOREF_2026_11_07A.json` (affine, GCPs, errors)
No CC BY-NC-SA material is used: NOAA public domain only.

## 3. METHOD: habitat classes (`CALACADEMY_PRECOLONIAL_HABITAT_5m_UTM10N_2026_11_07A.tif`, grid C; `..._5m_CW_...` extended; `..._CONF_5m_CW_...` confidence raster 3/2/1)

Input features (precolonial_features.py): on the full-res scan, ink (black pen, not red contour) and dark-ink density per sheet/6 cell (~5 m), red contour density. T-sheet conventions as I read them from the 1852 sheet: the field of small tufted arcs with dashes = grass-covered ground; ground with no symbol and "Sand Hills" lettering and small 'd' marks = bare drifting sand; fine stipple along the beach = strand sand; compact dark clumps = scrub/trees; blank areas with neither symbol nor contour = water. [My reading of the symbols; no legend sheet was in hand: the symbol key for the 1850s Coast Survey is not on this sheet. Verify against the Coast Survey topographic conventions.]

| Code | Class | From | Confidence |
|---|---|---|---|
| 1 | beach strand | DTM < 3 m within 300 m of the shoreline (brief rule), shoreline = DEM no-data sea of today | medium (shoreline is 2023, beach edge on the sheet is ~45 m east) |
| 2 | foredune / bare sand dune | sheet cells with 25 m-smoothed ink density < 0.007 (no symbols) inside the survey; outside the sheet, smoothed carry-over of the sheet's mix | medium on the sheet, low outside (conf 1) |
| 3 | dune scrub | intermediate ink density (sparse tufts), the ecotone between bare sand and grass; low-confidence | low |
| 4 | coastal prairie / dune grass | smoothed ink density > 0.018 (tuft field) | medium |
| 5 | coastal scrub | dark clumps off water and off the beach; hills (> 110 m or slope > 18 deg) outside the sheet | low-medium |
| 6 | willow riparian | dark clumps < 12 m elevation within 600 m of sheet lakes (creek hollows behind Lake Merced) | low |
| 7 | freshwater marsh | stippled ponds/wet hollows (dark clumps, low, 600 m+ from lakes, < 900 m inland) + 60 m fringe of lakes on flat ground | low |
| 8 | lake | symbol-free enclosed areas on the sheet (Lake Merced north and south arms, 1852 extent); OSM modern outline for Mountain Lake, Laguna Honda, Pine Lake (confidence 2). **The park's constructed lakes are not included.** | high on sheet / medium outlines |
| 9 | rocky shore | DTM slope > 30 deg within 150 m of the sea north of N 4181300 (Lands End / Sutro) | medium |
| 10 | oak-bay woodland | **none**: no source in hand places it in this window (an 1856 account in a SPUR slide cites "clusters of chaparral and liveoak" on the dunes near Eddy and Franklin, far east) | n/a |
| 0 | unknown / open sea | DEM no-data = sea | |

Per Bryan's steer (dunes and native grasses): the sheet itself makes bare sand (2) and grass (4) dominant. Grid C land: class 2 = 30.1 %, class 4 = 47.3 %, class 5 = 19.0 %, class 3 = 2.7 %, class 1 = 0.7 %, class 8 = 0.1 %, class 9 = 0.1 %, classes 6/7/10 = 0 (willow and marsh sit around Lake Merced, outside grid C). Grid CW: 2 = 536 k, 4 = 1344 k, 5 = 508 k cells; willow 2.8 k, marsh 12.6 k, lake 38 k.
Honest limits: (i) the sheet ends at ~E 546 600 and at Point Lobos; the **park's east strip, the Richmond and the Presidio are extrapolated (conf 1)** by smoothed carry-over and the hill rule until T00663/T00687 are georeferenced; the east hills (Sutro, Twin Peaks, Mount Davidson) show as class 5 from elevation alone; (ii) willow/marsh are weak (compact dark clumps and rules, not read as species); (iii) the DTM is modern bare earth, the dunes under the city are graded, so DTM rules use only the coarse beach and cliff tests; (iv) 1852 is before the 1870s planting but after 1840s grazing and sand shifts; (v) the lake mask misses small ponds drawn with stipple. Legend CSV: `CALACADEMY_PRECOLONIAL_HABITAT_LEGEND_2026_11_07A.csv` (naturalistic palette from Bryan: sand #d9c8a0, prairie #c9b87a, dune scrub #8f9a7a, coastal scrub #6f7f5a, willow #4a5f3a, marsh #6a8f6a, lake #5b8fb5, beach #e8dcc0, rocky #7a7066, oak-bay #4f5f3f; unknown/sea #b9c4c9 is mine).

## 4. Water GeoJSON
`CALACADEMY_PRECOLONIAL_WATER_2026_11_07A.geojson` (WGS84; source, confidence and licence per feature): 4 Lake Merced polygons (1852 extent from T00382), Mountain Lake, Laguna Honda, Pine Lake (OSM outlines), 3 modern Lake Merced reference rings, 15 OMCA/SFEI creek lines (13 unnamed, Arroyo Dolores, Islais Creek), Lobos Creek from OSM (5 ways, modern alignment). **Not done:** Sunset sloughs and the sheet's drawn creek lines were not digitised (the sheet shows drainage hollows that I did not trace).

## 5. Elk herds (for THE TERRITORY, schema `ggp-elk-herds/1`)
`CALACADEMY_ELK_HERDS_v1_2026_11_07A.json` (6 herds, 59 animals, outside the park outline +40 m) and `..._v2_...json` (7 herds, 71 animals, may cross the park). Loops 1.0-1.9 km, points every 15-19.9 m, closed, speed 1.0-1.8 m/s, phase 0-1. Validated by script: every point on class 2, 3 or 4 (0 violations), none in the V1 park outline. Illustrative paths, not documented elk movements. `habitat` tags are `foredune`, `dune_scrub`, `coastal_prairie`.

## 6. Next
Georeference T00663 (Presidio, 1857) and T00687 (park east, 1857) the same way, then redo the extrapolated strips; ask SFEI (Hidden Nature) and Joel Pomerantz for their polygons; digitise the sheet's creek lines; confirm the sheet's symbol key.
