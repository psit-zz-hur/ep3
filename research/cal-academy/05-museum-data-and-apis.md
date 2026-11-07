# Open Data & APIs — California Academy of Sciences (for a data-driven 3D/4D building experience)

Research track report. Direct URL verification was blocked for this track (network
allowlist was empty when it ran); endpoints are standard and stable but marked
**[live-tested: no]** where not exercised. Academy coordinates: **37.7699 N, -122.4661 W**
(55 Music Concourse Dr, Golden Gate Park).

## 1. Collections data (research floors / Project Lab / collections wing)

### 1a. GBIF publisher (primary programmatic route)
- Publisher page: https://www.gbif.org/publisher/66522820-055c-11d8-b84e-b8a03c50a862 — ~4 million occurrences across 12 datasets.
- Format/API: GBIF REST JSON (no key for search; free account for bulk downloads). Darwin Core Archive via dataset page "Download" or `https://api.gbif.org/v1/occurrence/download/request`.
- License: per dataset (CC0 or CC BY). GBIF API is free.
- Update frequency: roughly weekly/monthly republishing (version numbers like Botany v157.658, Ichthyology v150.534 in 2026).
- Example calls [live-tested: no]:
  - All CAS datasets: `https://api.gbif.org/v1/dataset/search?publishingOrg=66522820-055c-11d8-b84e-b8a03c50a862&limit=50`
  - Count per dataset: `https://api.gbif.org/v1/occurrence/search?publishingOrg=66522820-055c-11d8-b84e-b8a03c50a862&limit=0&facet=datasetKey&facetLimit=30`
  - Georeferenced only: `...&hasCoordinate=true&hasGeospatialIssue=false`
  - With images: `...&mediaType=StillImage`
  - Per-year histogram for 4D animation: `...&facet=year&facetLimit=200&limit=0`
  - Specimens collected within Golden Gate Park: `...&geometry=POLYGON((-122.511 37.766,-122.454 37.766,-122.454 37.774,-122.511 37.774,-122.511 37.766))`

| Dataset (GBIF title) | GBIF key / DOI | Records (best available) | License |
|---|---|---|---|
| CAS Herpetology (HERP) | key `cece4fc2-1fec-4bb5-a335-7252548e3f0b`, DOI 10.15468/bvoyqy | 215,241 CAS + 53,296 Stanford specimens | CC BY likely |
| CAS Ichthyology (ICH) | key `5d6c10bd-ea31-4363-8b79-58c96d859f5b`, DOI 10.15468/efh2ib | >200,000 lots / ~1.6M specimens | CC BY |
| CAS Botany (BOT) | DOI 10.15468/7gudyo | ~1,053,184 records (iDigBio mirror) | check |
| CAS Entomology (ENT) | DOI 10.15468/3ibpmo | 351,277 records, 1,800 media | CC0 |
| CAS Entomology Type (TYPE) | DOI 10.15468/gak5hc | small (types) | CC0 |
| CAS Invertebrate Zoology (IZ) | DOI 10.15468/tiac99 | 258,246 | check |
| CAS Geology (GEO) microfossils | DOI 10.15468/p5gh1a | 23,878 | check |
| CAS Ornithology (ORN) | key `4f29b6ab-20c0-4479-8795-4915bedcebd1` | 102,794 records, 3,455 species | check |
| CAS Mammalogy (MAM) | DOI 10.15468/dhbozg | not captured | check |
| AntWeb (CAS-hosted) | key `13b70480-bd69-11dd-b15f-b8a03c50a862`, DOI 10.15468/wqmjjt | 917,346 records, 13,169 species, heavily imaged | CC BY |
| Anthropology | not found on GBIF | — | — |

### 1b. iDigBio recordsets (alternative aggregator with media index)
- Entomology: https://portal.idigbio.org/portal/recordsets/26f7cbde-fbcb-4500-80a9-a99daa0ead9d (351,277 specimens, ingested 2026-04-23)
- Invertebrate Zoology: https://portal.idigbio.org/portal/recordsets/51b958bb-9d5f-48d7-9a97-e372c0c747c3 (258,246)
- Lichens: https://portal.idigbio.org/portal/recordsets/1ffce054-8e3e-4209-9ff4-c26fa6c24c2f (3,869 specimens, 7,493 media)
- Legacy CAS set (stale, 2015): https://portal.idigbio.org/portal/recordsets/8dc14464-57b3-423e-8cb0-950ab8f36b6f
- API: `https://search.idigbio.org/v2/search/records?rq={"recordset":"26f7cbde-fbcb-4500-80a9-a99daa0ead9d","geopoint":{"type":"exists"}}&limit=100` — CC0 metadata, JSON.

### 1c. CAS-hosted portals
- Monarch (Symbiota) portal: https://monarch.calacademy.org/collections/misc/collprofiles.php — Entomology, CC0.
- Herpetology catalog: https://researcharchive.calacademy.org/research/herpetology/catalog/index.php
- Ornithology & Mammalogy DBs: https://research.calacademy.org/research/bmammals/aboutomdbs.php
- Informatics overview: https://www.calacademy.org/scientists/informatics
- Eschmeyer's Catalog of Fishes: https://research.calacademy.org/research/ichthyology/catalog/ — 37,799 valid species, updated monthly; no public API.
- Archives: archives.calacademy.org (historical photos, 1906 earthquake material).

### 1d. Researcher datasets (Dryad/Zenodo)
- Atlantic reef fishes distributions & traits (1,628 spp.): https://zenodo.org/records/15636151
- Arabian Peninsula reef-fish genomics (Rocha lab): https://zenodo.org/records/4579399 (~604 GB; impractical)
- mesophotic.org (Hope for Reefs literature + data portal).

## 2. iNaturalist (Academy co-runs it; HQ is in the building)
- API docs: https://api.inaturalist.org/v1/docs (JSON, no key for reads; ~100 req/min). Python: https://pyinaturalist.readthedocs.io
- Golden Gate Park place_id: resolve at runtime via `https://api.inaturalist.org/v1/places/autocomplete?q=Golden%20Gate%20Park`, or use a radius query.
- Example pulls [live-tested: no]:
  - Observations with photos within 500 m: `https://api.inaturalist.org/v1/observations?lat=37.7699&lng=-122.4661&radius=0.5&photos=true&quality_grade=research&geo=true&per_page=200&order_by=observed_on`
  - Species counts in GGP (2 km): `.../observations/species_counts?lat=37.7699&lng=-122.4661&radius=2`
  - Month histogram for 4D: `.../observations/histogram?lat=37.7699&lng=-122.4661&radius=2&date_field=observed&interval=month`
  - Photos: `photos[].url` (swap `square` for `medium`/`large`); filter `photo_license=cc0,cc-by` for reuse.
- City Nature Challenge: SF Bay Area 2025 = 50,094 obs / 3,930 spp (infographic https://www.calacademy.org/sites/default/files/assets/docs/cnc25_results_sf_bay_area_infographic.pdf); 2026 = 63,589 obs. Pull via yearly umbrella project (`/v1/projects?q=City%20Nature%20Challenge%202025%20San%20Francisco`).
- iNat data on GBIF: dataset key `50c9509d-22c7-4a22-a47d-8c48425ef4a7`.

## 3. Living Roof (2.5 acres, 7 hills, ~1.7M plants in 50,000 coconut-fiber trays)
- Plant list (Rana Creek, original 9 natives): Fragaria chiloensis, Armeria maritima, Prunella vulgaris, Sedum spathulifolium (perennials); Eschscholzia californica, Lupinus bicolor, Lasthenia californica, Plantago erecta, Layia platyglossa (annuals). Sources: https://www.gardencentermag.com/news/native-plant-species-top-california-s-living-roof ; ASLA 2009 https://www.asla.org/2009awards/111 . Now >100 native species (ABC7 2018).
- Weather station: ASLA lists a "Rainmaster" station; it drives skylight operation. **No public feed found.** Substitute NWS / PurpleAir (section 9).
- Performance: stormwater retention up to 3.6M gal/yr (~98%); roof surface up to 18 F cooler. Case study + methods: https://www.landscapeperformance.org/case-study-briefs/ca-academy-green-roof ; https://landscapeperformance.org/sites/default/files/2025-02/CA-Academy-Green-Roof-methods.pdf ; SF Planning case study https://default.sfplanning.org/Citywide/livingroof/GR_case_study-CalAcademySciences.pdf ; SWA "20 Years On" https://www.swagroup.com/stories/california-academy-of-sciences-green-roof/
- Solar canopy: ~60,000 PV cells, ~213,000 kWh/yr, 5-10% of building electricity (https://www.calacademy.org/efficient-building-design). No live feed.
- LEED Double Platinum (NC 2008, EBOM 2011). Arup page https://www.arup.com/projects/california-academy-of-sciences/ ; no post-occupancy dataset found.

## 4. Steinhart Aquarium & live feeds
- Webcam hub: https://www.calacademy.org/learn-explore/live-webcams — Penguin cams (3), Philippine Reef Cam, Farallon Islands Cam, Reef Lagoon Cam (https://calacademy.org/learn-explore/animal-webcams/reef-lagoon-cam — offline for maintenance as of Jan 2026). Embeds are YouTube Live; grab iframe `src` at build time; embed only.
- Feeding schedule: penguins 10:30 and 15:00 daily; "Reef 101" daily dive show. Daily calendar pages: https://www.calacademy.org/daily-calendar-view/2026-11-07
- Philippine Coral Reef: 212,000 gal, 25 ft deep, ~2,000 reef fish. Whole aquarium: ~60,000 animals, 800+ species.
- No published species list or water chemistry. Substitute iNat taxa API for species imagery.

## 5. Morrison Planetarium & Visualization Studio
- https://www.calacademy.org/mpvs — 75 ft dome. In-house shows: Fragile Planet (2008), Life (2010), Earthquake (2012), Habitat Earth (2015), Incoming! (2016), Expedition Reef (2018), Big Astronomy (2020), Living Worlds (2021), Spark (2023/24).
- OpenSpace (MIT, free): https://www.openspaceproject.com ; docs https://docs.openspaceproject.com . Morrison is a named partner.
- Digital Universe Atlas (AMNH): https://www.amnh.org/research/hayden-planetarium/digital-universe/download (~20 GB; speck/label text formats, easy to parse into Three.js point clouds; license forbids redistributing modified versions).
- NASA SVS: https://svs.gsfc.nasa.gov (public domain).

## 6. Visitor / operations data
- Annual reports: FY23 https://www.calacademy.org/sites/default/files/assets/docs/fy23_cas-annual-report_231201.pdf ; FY22 https://s3.us-west-2.amazonaws.com/files.calacademy.org/pdf/CalAcademy-Annual-Report-FY22.pdf ; FY20 https://docent.calacademy.org/sites/default/files/assets/docs/fy20_cas-annual-report_210128.pdf ; index https://www.calacademy.org/financials ; FY25 audited statements https://www.calacademy.org/sites/default/files/assets/docs/cas_audited-financial-statements_fy25.pdf
- Attendance: ~750k (2003) -> 1.5M (2013) -> ~1.3M pre-pandemic; paid daytime admissions 403,004 (FY19) -> 324,332 (FY25) per https://www.calacademy.org/press/releases/a-message-to-the-california-academy-of-sciences-community
- IRS 990: EIN 94-1156258. ProPublica API `https://projects.propublica.org/nonprofits/api/v2/organizations/941156258.json`
- Strategic plan FY2027-2031: https://www.calacademy.org/major-initiatives
- NightLife: Thursdays 18:00-22:00, 21+.

## 7. Science programs with datasets
- Hope for Reefs / Twilight Zone: specimens in CAS ICH GBIF dataset; pull `...&datasetKey=5d6c10bd-ea31-4363-8b79-58c96d859f5b&depth=60,150`.
- AntWeb API v3.1: `https://api.antweb.org/v3.1/specimens?genus=Camponotus&limit=100` [unverified]
- bioGraphic https://www.biographic.com ; BigPicture https://www.bigpicturecompetition.org (copyrighted media).

## 8. Seismic
- Building is **not** base-isolated (de Young across the concourse is). Steel grillage roof, column "table-leg" connections, SGH peer review. Sources: https://www.sgh.com/project/california-academy-of-sciences/ ; https://metropolismag.com/programs/part-3-the-engineering/
- Shake House: https://www.calacademy.org/blogs/earthquake/secrets-of-the-shake-house (1989 Loma Prieta M6.9, 1906 M7.9).
- USGS live feed (public domain, no key):
  - `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson` (also all_day, 2.5_week, 4.5_month)
  - Near SF: `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&latitude=37.7699&longitude=-122.4661&maxradiuskm=300&starttime=2025-01-01&minmagnitude=1.5&orderby=time`
  - Historic: `...&starttime=1900-01-01&minmagnitude=6&maxradiuskm=200`

## 9. Environmental sensors nearby
| Source | Endpoint | Notes |
|---|---|---|
| NOAA CO-OPS tides, SF station 9414290 | `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=9414290&product=water_level&datum=MLLW&time_zone=lst_ldt&units=english&format=json` | 6-min data; record since 1854 |
| NWS | `https://api.weather.gov/points/37.7699,-122.4661` (needs User-Agent header) | JSON-LD, public domain |
| PurpleAir (free read key) | `https://api.purpleair.com/v1/sensors?fields=name,pm2.5_10minute,humidity,temperature&location_type=0&nwlng=-122.515&nwlat=37.775&selng=-122.453&selat=37.764` | header X-API-Key |
| OpenAQ v3 (key) | `https://api.openaq.org/v3/locations?coordinates=37.7699,-122.4661&radius=5000` | |
| eBird API 2.0 (key) | `https://api.ebird.org/v2/data/obs/geo/recent?lat=37.7699&lng=-122.4661&dist=2` ; hotspots L109439 (GGP), L499374 Stow Lake, L10148460 Alvord Lake, L1074460 Rhododendron Dell, L1573659 North Lake, L2341719 Big Rec | |
| BirdCast | https://dashboard.birdcast.info (SF County) | no API |

## Not found / not public
Living-roof weather feed, solar generation feed, aquarium water chemistry, Steinhart species list, Arup post-occupancy energy data, NightLife attendance, membership count, Anthropology on GBIF, Hope for Reefs ARMS raw data.

## Visualization ideas (data -> building location)
1. Collections wing as a 4D specimen cloud: GBIF `facet=year` + coordinates, particles rising from collecting localities on a globe beneath the research floors, scrubbed 1853 -> today (1906 fire gap; expedition bursts).
2. Philippine Coral Reef tank <-> Twilight Zone depth column: color the tank model by depth; CAS ICH `depth=60,150` specimens sink to a virtual mesophotic layer below the floor.
3. Living Roof heat/rain map: NWS hourly temp/precip + PurpleAir PM2.5 draped on the 7 hills; 18 F cooling delta as a shader gradient; a stormwater meter filling to 3.6M gal.
4. Roof biodiversity: iNat observations within 300 m placed on the hill where observed; bloom time driven by observation phenology.
5. Morrison dome: Digital Universe speck files as a point cloud on the dome interior; USGS GeoJSON on an Earth model.
6. Shake House seismograph: USGS `all_hour.geojson`; quakes within 300 km shake the model; slider replays 1906 and 1989.
7. Penguin colony clock: penguin YouTube Live on the African Hall balcony; lighting cycles to the 10:30 / 15:00 feedings.
8. Piazza heartbeat: attendance and NightLife Thursdays pulse the piazza; 990 revenue/expense bands on the mezzanine.
9. Golden Gate tide at the Swamp: NOAA 9414290 water level drives the flooded-forest level, with a 170-year replay.
10. Birds over the building: eBird hotspot observations perch on the roof; BirdCast nightly migration streams as particles above the solar canopy.
