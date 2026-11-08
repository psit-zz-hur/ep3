# Building-anchored dataset census, live-tested (7 Nov 2026)

**Companion to `15-cal-academy-public-datasets.md`** (the cloud agent's broader sweep, compiled 8 Nov from a sandbox that could not
reach several hosts). This file was written from an unrestricted network on 7 Nov and fills the gaps that file lists as blocked or missing:
Zenodo, Dryad, NCBI, OpenAlex, iDigBio, the Internet Archive Galápagos journals, DataSF, the `github.com/calacademy` organisation
(18 public repos; file 15 says none exists), the iNaturalist place IDs for the Academy / Living Roof / Grounds, and two
GBIF *slices*: the **1,071 specimens collected at the building** and the **Galápagos 1905-06 expedition** (14,311 records).
Its top 10 ranks by "anchored in the building" for the game; file 15's top 10 ranks for global spectacle. Pick across both.
Where the two disagree on a count, the difference is the date (7 vs 8 Nov) or `hasGeospatialIssue=false` (used here).

Census for the Freeswim Fridays visualization demo. It extends `05-museum-data-and-apis.md`
(which listed endpoints but had no network access) with **live-tested counts and licences**.
Everything marked ✔ was queried from this session on 2026-11-07; counts are as of that day and drift weekly.

**Verified flag:** ✔ = endpoint called live, numbers are from the response · ◐ = page or finding aid read,
no machine endpoint exercised · ✘ = not verified (stated from search results or memory, treat as a lead).

**Corrections to file 05** (its table was written offline): Botany is 1,909,776 records, not ~1.05 M;
Herpetology is 320,148, not 215,241; Ichthyology is 220,947 lots-records; Ornithology is CC0, not "check";
Mammalogy 40,006 (was "not captured"); Geology is CC BY-NC (not CC0); the GBIF publisher has **12** datasets
and **4,202,371** occurrences, of which **2,184,463 have usable coordinates** and **551,615 carry images**.
The Academy's iNaturalist place 62549 has a corrupt bounding box (longitude -482); use **54088**.

Academy coordinates: 37.76986 N, -122.46609 W. Building box used below:
`POLYGON((-122.4678 37.7684, -122.4644 37.7684, -122.4644 37.7709, -122.4678 37.7709, -122.4678 37.7684))`
(this is the iNaturalist "Academy" place box; it contains the building, piazza, gardens, Music Concourse edge).

---

## 1. Collections: the GBIF / IPT publisher (Academy-hosted, CC0 mostly)

All twelve datasets are published by the Academy through its own IPT at `http://ipt.calacademy.org:8080`
(installation key `a43950ae-eb88-4ef4-bfff-43bcf12885ad`) and mirrored by GBIF. Publisher key
`66522820-055c-11d8-b84e-b8a03c50a862` (https://www.gbif.org/publisher/66522820-055c-11d8-b84e-b8a03c50a862).
Each has an unauthenticated Darwin Core Archive (ZIP) at `http://ipt.calacademy.org:8080/archive.do?r=<id>`
(HEAD tested for all twelve: 200, `application/zip`, last-modified 2 Nov 2026 except Geology). EML at `eml.do?r=<id>`.
GBIF REST search needs no key (https://api.gbif.org/v1/occurrence/search; **URL-encode spaces in `geometry=`**).

| # | Dataset (GBIF key) | Records · with coords · with images | Licence | IPT id → DwC-A | Placement in the building | Ver. |
|---|---|---|---|---|---|---|
| D1 | **CAS Botany (BOT)** `f934f8e2-32ca-46a7-b2f8-b032a4740454`, DOI 10.15468/7gudyo. https://www.gbif.org/dataset/f934f8e2-32ca-46a7-b2f8-b032a4740454 | 1,909,776 · 281,632 · 1,832,325 | CC0 | `botany` | Living Roof (plants), herbarium/collections wing; California subset for the roof hills | ✔ |
| D2 | **AntWeb** `13b70480-bd69-11dd-b15f-b8a03c50a862`, DOI 10.15468/wqmjjt. https://www.gbif.org/dataset/13b70480-bd69-11dd-b15f-b8a03c50a862 | 917,346 · 873,765 · 66,365 | CC BY 4.0 | `antweb` | Rainforest dome / Living Roof ant swarm; macro ant portraits | ✔ |
| D3 | **CAS Entomology (ENT)** `14f3151a-e95d-493c-a40d-d9938ef62954`, DOI 10.15468/3ibpmo. https://www.gbif.org/dataset/14f3151a-e95d-493c-a40d-d9938ef62954 | 352,537 · 154,119 · 610 | CC0 | `ent` | Roof and Living Roof (277 records collected at the site, see D14) | ✔ |
| D4 | **CAS Herpetology (HERP)** `cece4fc2-1fec-4bb5-a335-7252548e3f0b`, DOI 10.15468/bvoyqy. https://www.gbif.org/dataset/cece4fc2-1fec-4bb5-a335-7252548e3f0b | 320,148 · 312,344 · **221,515** | CC0 | `herp` | Rainforest/Swamp and Africa/Madagascar wall; image wall | ✔ |
| D5 | **CAS Invertebrate Zoology (IZ)** `44bcde48-ac71-46f2-bf73-24fc3c008b6c`, DOI 10.15468/tiac99. https://www.gbif.org/dataset/44bcde48-ac71-46f2-bf73-24fc3c008b6c | 285,564 · 250,354 · 0 | CC0 | `invz` | Philippine Coral Reef (22,855 Philippine records), tide-pool/aquarium halls | ✔ |
| D6 | **CAS Ichthyology (ICH)** `5d6c10bd-ea31-4363-8b79-58c96d859f5b`, DOI 10.15468/efh2ib. https://www.gbif.org/dataset/5d6c10bd-ea31-4363-8b79-58c96d859f5b | 220,947 · 184,282 · 3,499 | CC0 | `ich` | Philippine Coral Reef tank (15,009 Philippine), Twilight Zone depth column (4,192 georeferenced at 60-150 m) | ✔ |
| D7 | **CAS Ornithology (ORN)** `4f29b6ab-20c0-4479-8795-4915bedcebd1`, DOI 10.15468/ozz2u5. https://www.gbif.org/dataset/4f29b6ab-20c0-4479-8795-4915bedcebd1 | 102,794 · 69,288 · 0 | CC0 | `orn` | **Building facades and gardens (692 window-strike birds, D14)**, Galápagos 1905-06 birds (7,502) | ✔ |
| D8 | **CAS Mammalogy (MAM)** `6ce7290f-47f6-4046-8356-371f5b6749df`, DOI 10.15468/dhbozg. https://www.gbif.org/dataset/6ce7290f-47f6-4046-8356-371f5b6749df | 40,006 · 32,574 · 0 | CC0 | `mam` | African Hall / collections wing | ✔ |
| D9 | **CAS Entomology Type (TYPE)** `6ec3c7f5-6233-48f6-b36a-06b867edbadd`, DOI 10.15468/gak5hc. https://www.gbif.org/dataset/6ec3c7f5-6233-48f6-b36a-06b867edbadd | 17,942 · 3,190 · 3,981 | CC0 | `type` | Type-specimen drawer in the collections wing (images on monarch.calacademy.org) | ✔ |
| D10 | **CAS Geology (GEO)** `5e848873-567f-42dd-8a29-88056b9b33a4`, DOI 10.15468/p5gh1a. https://www.gbif.org/dataset/5e848873-567f-42dd-8a29-88056b9b33a4 | 23,880 · 22,109 · 0 (fossils: 24,136 across the publisher) | **CC BY-NC 4.0** | `geo` | Earthquake/geology exhibits, Shake House | ✔ |
| D11 | **CAS Ornithology Egg & Nest (EGG)** `d3bc4c7d-325c-49ea-aa71-d915b2ee3204`, DOI 10.15468/tbh8hg. https://www.gbif.org/dataset/d3bc4c7d-325c-49ea-aa71-d915b2ee3204 | 11,190 · 565 · 0 | **CC BY-NC 4.0** | `casegg` | Collections wing (egg cabinet); only 5 % georeferenced | ✔ |
| D12 | **CAS Geology Microfossil Collection** `3807f67c-a065-43eb-bc1b-e2176c09c03f`, DOI 10.15468/sjngf7. https://www.gbif.org/dataset/3807f67c-a065-43eb-bc1b-e2176c09c03f | 241 · 241 · 0 | **CC BY-NC 4.0** | `cas_geology_microfossil_collection` | Negligible; skip | ✔ |

Whole-publisher facts (✔): 4,202,371 occurrences; licence mix CC0 3,260,904 / CC BY 917,346 / CC BY-NC 24,121.
Georeferenced occurrences by country: US 747,455 · MX 170,215 · MG 155,690 · CR 117,743 · PH 77,824 · AU 69,454 · CN 58,939 · ZA 47,613.
California alone: 463,198. Specimen images sit on Academy servers (`ibss-images.calacademy.org/static/<dept>/originals/…`,
`researcharchive.calacademy.org/image_db/herp/…`, `monarch.calacademy.org/mnt/target-images/…`) and on `antweb.org/images/…`
(checked from sample media records). Media-level licences can differ from the dataset licence (TYPE sample had `license: null`; AntWeb is CC BY 4.0).

Spatial/temporal extent: global, with strong Pacific, Madagascar, Galápagos and Californian holdings; collecting years 1698-2026
(GBIF `year` facet returns 197 distinct years among georeferenced records, 313 among all). The pre-1906 collection was largely lost in the
earthquake and fire, so the year histogram has a **spike at 1905-06 (6,920 / 6,481 georeferenced records vs ~3,000 a year before)**: the Galápagos
expedition's material was away at sea and survived (observation from the facet, not a published claim).

## 2. Other aggregator and Academy-hosted collection portals

| # | Dataset | Owner · URL | What / size | Format · API | Licence | Placement | Ver. |
|---|---|---|---|---|---|---|---|
| D13 | **iDigBio CAS records** | iDigBio · https://search.idigbio.org/v2/summary/count/records?rq={"institutioncode":"cas"} · portal recordsets listed in 05 §1b (e.g. https://portal.idigbio.org/portal/recordsets/26f7cbde-fbcb-4500-80a9-a99daa0ead9d) | `institutioncode=cas` returns **3,253,581** records (may include other "CAS" institutions, ✘ not de-duplicated); Entomology recordset has **200,432** with geopoints | JSON search API, no key | CC0 metadata (per recordset) | Same as D1-D9; mainly a backup route and a media index | ✔ count, ✘ attribution of every "cas" row |
| D14 | **Specimens collected at the Academy building** (a *slice* of D3/D7/D8/D1/D2…, not a separate dataset) | GBIF query over the building box (recipe 1) | **1,071 specimens**, all with coordinates: ORN 692, ENT 277, MAM 24, IZ 19, BOT 19, AntWeb 18, EGG 13, HERP 5, ICH 4. Birds 705, insects 257. Locality strings name the zone: *Front Entrance* (189), *Business Entrance* (97), *West Garden* (83), *East Garden* (70), *Rooftop* (177), *Living Roof* (47), *Piazza* (17), North/South/East/West side. Collecting years 2008-2022 dominate (ENT 2019, 2022; ORN 2008-09, 2019); one 1905 and a handful of 1930s-60s older records. ORN remarks are salvage-skin measurements (window-strike birds) | DwC JSON; no key | CC0 (ORN, ENT, MAM, IZ, BOT, HERP, ICH), CC BY (AntWeb), CC BY-NC (EGG) | **The building itself**: pin each record to the façade or garden named in `locality`. No images (media 0) | ✔ |
| D15 | **Monarch (Symbiota) portal**, Entomology | CAS · https://monarch.calacademy.org/collections/misc/collprofiles.php | Entomology + type images (`/mnt/target-images/…`) | Symbiota HTML/DwC export | CC0 | Collections wing | ✘ returned HTTP 503 during testing; images reachable via GBIF media URLs |
| D16 | **Eschmeyer's Catalog of Fishes** | CAS Ichthyology · https://www.calacademy.org/scientists/projects/catalog-of-fishes · https://researcharchive.calacademy.org/research/ichthyology/catalog/fishcatmain.asp | ~37.8 k valid species (per 05), updated monthly | HTML search, **no API, no bulk download advertised**; the informatics page lists no download links | © Academy (terms on page) | Aquarium names plates | ◐ (pages return 200; claim of 37,799 from 05) |
| D17 | **Diatoms names database; California Wildflowers database** | CAS · http://researcharchive.calacademy.org/research/diatoms/names/index.asp · http://researcharchive.calacademy.org/research/botany/wildflow/ | Listed on https://www.calacademy.org/scientists/informatics | HTML only | not stated | Roof wildflowers (Wildflowers photos) | ◐ page read, ✘ content not inspected |
| D18 | **AntCat (World Catalog of Ants)** | CAS · repo https://github.com/calacademy-research/antcat (pushed 2026-11-08) · feeds antweb.org | Taxonomic catalogue behind AntWeb | Rails app; DB dumps ✘ | not stated | Ant swarm labels | ◐ |
| D19 | **AntWeb API v3.1** | CAS-hosted · https://api.antweb.org/v3.1/specimens?genus=Camponotus&limit=2 | Specimens + images | JSON | CC BY | Ant swarm | ✘ **503 / 403** when tested (www.antweb.org/api/v3.1 → 403). Use D2 via GBIF instead |

## 3. iNaturalist (the Academy co-runs it and is in the building)

API https://api.inaturalist.org/v1 (no key for reads, ~100 req/min; User-Agent header). Photo licences are per observer;
filter `photo_license=cc0,cc-by,cc-by-sa` to reuse. GBIF mirror (research grade): dataset `50c9509d-22c7-4a22-a47d-8c48425ef4a7`.
Bulk: `https://inaturalist-open-data.s3.amazonaws.com/{observations,photos,taxa}.csv.gz` = 13.7 GB / 21.1 GB / 40 MB (HEAD, 27 Oct 2026): too big for a script, use the API.

| # | Place / project | ID · URL | Contents (✔ 2026-11-07) | Extent | Placement | Ver. |
|---|---|---|---|---|---|---|
| D20 | **Academy** place | 54088 · https://www.inaturalist.org/observations?place_id=54088 | **10,348 obs, 1,477 species**; research grade 3,407, of which 655 have an open-licensed photo; 101 bird species; 1,946 identifiers; by year: 2019 1,351 → 2022 707 → 2025 965 → 2026 1,415 (partial) | box 37.7685-37.7709 N, -122.4678…-122.4644 | Whole footprint; **Piazza and gardens** | ✔ |
| D21 | **Academy Living Roof** place | 55189 · https://www.inaturalist.org/observations?place_id=55189 | **3,885 obs, 969 species**. Top research-grade species: Brewer's Blackbird 50, common yarrow 38, Red-tailed Hawk 30, Wild Turkey 29, California poppy 27, beach strawberry 17 (two of the roof's original nine natives) | box 37.7691-37.7706 N, -122.4671…-122.4651 | **The roof**, hill by hill (lat/lng per observation) | ✔ |
| D22 | **Academy Grounds** place | 114015 · https://www.inaturalist.org/places/114015 | **5,282 obs, 692 species** | box 37.7685-37.7708 N, -122.4674…-122.4645 | Gardens and entrances | ✔ |
| D23 | **Golden Gate Park** place | 165701 · https://www.inaturalist.org/places/165701 (also 150793 Oak Woodlands: 7,232 obs; 75752 Eastern GGP) | **130,213 obs, 5,018 species** | whole park | The park seen through the windows; "outside" layer | ✔ |
| D24 | **City Nature Challenge, SF Bay Area** (2023 `146321`, 2024 `181463`, 2025 `226032`, **2026 `263576`**) | https://www.inaturalist.org/projects/263576 | 2026: **65,727 obs, 3,910 species, 234 users listed**; daily counts 17,232 (24 Apr) / 20,768 (25 Apr) / 15,558 (26 Apr); 3,828 research-grade open-photo obs. Academy infographic for 2025 in 05 | Bay Area, late April each year | **Piazza heartbeat** time-lapse; Academy is the lead organiser | ✔ |
| D25 | **California Academy of Sciences Bioblitzes** (umbrella) | 30186 · https://www.inaturalist.org/projects/california-academy-of-sciences-bioblitzes | 71,253 obs, 3,552 species across child projects | various Bay Area parks | Event wall in the Naturalist Center | ✔ |
| D26 | **Academy Galápagos trip** | 33500 · https://www.inaturalist.org/projects/california-academy-of-sciences-galapagos-trip | 1,882 obs, 412 species (7 users) | Galápagos | Pairs with D32 (1905-06) in the "then / now" globe | ✔ |

## 4. Research deposits by Academy authors

| # | Repository | Query and URL | Size (✔) | Format | Licence | Placement | Ver. |
|---|---|---|---|---|---|---|---|
| D27 | **Zenodo** | `https://zenodo.org/api/records?q=creators.affiliation:"California Academy of Sciences"&type=dataset&sort=mostrecent` · https://zenodo.org/search?q=creators.affiliation%3A%22California%20Academy%20of%20Sciences%22 | **8,229** records with an Academy affiliation (the newest hits are taxonomic figures and supplements; share of data sets not counted beyond the 260), **260 are datasets**; examples: widow-spider atlas voucher images & metadata (10.5281/zenodo.22661424), Phenobase v1 (10.5281/zenodo.22051238), Atlantic reef-fish traits (https://zenodo.org/records/15636151, from 05) | JSON API, files per record | per record (mostly CC BY / CC0) | Library / Project Lab wall; spider atlas ↔ roof | ✔ |
| D28 | **Dryad** | `https://datadryad.org/api/v2/search?q="California Academy of Sciences"` · https://datadryad.org/search?q=California%20Academy%20of%20Sciences | 7 hits for the exact phrase, 35 for the loose phrase; includes *The avifauna of the Galapagos Islands* (doi:10.5061/dryad.156) and a *Bembidion* subgenus data set (doi:10.5061/dryad.b5mkkwhgc) | JSON API, CC0 files | CC0 | Galápagos bird data pairs with D7 | ✔ (affiliation filter by ROR returned 0; text query works) |
| D29 | **NCBI BioProject / BioSample** | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=bioproject&term="California Academy of Sciences"[Organization]` | **51** BioProjects by organisation (73 free text); BioSample free text 4,846. Newest: PRJNA1552669 (*Madracis* coral cryptic diversity), PRJNA1550192 (sunflower star *Pycnopodia* + *Pisaster* genomes), PRJNA1529784/1530629/1543628 (*Castilleja foliolosa* genome) | E-utilities JSON/XML; sequences need SRA tools | public domain (INSDC) | Genomics wall in the research lab; sunflower star ↔ tide pool | ✔ counts; nuccore search rate-limited (429), ✘ |
| D30 | **Figshare** | `POST https://api.figshare.com/v2/articles/search {"search_for":"\"California Academy of Sciences\""}` | Hits exist (PLOS supplements, Zootaxa-type revisions of Malagasy ants and Opiliones); total not counted | JSON | per item | Low priority | ✔ reachable, ✘ no count |
| D31 | **OpenAlex** (publication metadata) | https://api.openalex.org/institutions/I2803094215 · ROR https://ror.org/02wb73912 | Institution record: 10,222 works; filter by ROR returned 5,577 works (counts differ by query, ✘ reason unknown); 1,613 tagged 2026 | JSON, no key | CC0 | Library "citation constellation"; `publications_finder` repo uses it | ✔ |
| D32 | **Galápagos GBIF slice, 1905-06 expedition** (slice of D4/D7/D1…) | GBIF query `country=EC&eventDate=1905-01-01,1906-12-31` (recipe 3) | **14,311 records, 4,568 georeferenced** (ORN 7,502; HERP 3,898; BOT 1,923; ENT 395; EGG 257; IZ 145; MAM 113). Collectors in the first 300: J.R. Slevin 135, E.S. King 99, F.X. Williams 26, W.H. Ochsner 22. `island`, `islandGroup` populated (e.g. Santa Cruz Id.) | JSON | CC0 / CC BY-NC | Planetarium dome as globe, or **African Hall → "away at sea in 1906"** | ✔ |

## 5. Library, archives and audiovisual

| # | Dataset | Owner · URL | Contents | Format · API | Licence/rights | Placement | Ver. |
|---|---|---|---|---|---|---|---|
| D33 | **Galápagos 1905-06 expedition journals on Internet Archive** | CAS Archives via BHL/IA · e.g. https://archive.org/details/csfa777220765 (Rollo Beck journal), https://archive.org/details/csfa795808124 (Gifford), https://archive.org/details/csfa788564365June (Hunter), https://archive.org/details/csfa788562626Pack4 (Stewart), https://archive.org/details/csfa788564467Part1 (Slevin), https://archive.org/details/csfa788564485 (Ochsner) | 23 `csfa*` items match the 1905/06 query; a plain "Galapagos 1905 Academy" search returns 30 items incl. the 14-part *Expedition of the California Academy of Sciences to the Galapagos Islands* papers (e.g. https://archive.org/details/ants_03351). Sample item `csfa788562626Pack4` has 27 files | IA `advancedsearch.php` + `metadata/<id>` JSON; PDF, DjVu, OCR text, JP2 | `licenseurl` = BHL permissions; `rights` = California Academy of Sciences. Academy blog footer: © all rights reserved. **Treat as view/embed, ask before redistributing** | Library mezzanine; paired with D32 on the globe | ✔ metadata, ◐ rights |
| D34 | **Academy film and video archive (`csfa_000xxx`)** | CAS · https://archive.org/details/calacademy · collection `californiarevealed`, `calacademyvideo` (stream-only) | Collection `calacademy`: **2,704** items; 180 identifiers matching `csfa*` (e.g. *Farallon Islands*, *Science in Action: Whales*, oral histories) | IA JSON; stream-only video | not stated; stream-only | Lobby screen; Farallon cam companion | ✔ counts, ✘ rights |
| D35 | **BHL: Academy Library contributions** | https://www.biodiversitylibrary.org/ (Beck field notes post: https://calacademy.org/blogs/from-the-stacks/rollo-h-beck-field-notes-now-accessible-online) ; IA query `collection:biodiversity AND contributor:"California Academy of Sciences Library"` | **591** IA items; 271 files in Commons category *BHL California Academy of Sciences collection* (https://commons.wikimedia.org/wiki/Category:Biodiversity_Heritage_Library_California_Academy_of_Sciences_collection) | BHL API (key ✘), IA, Commons API | mostly public domain pre-1929; check each | Library | ✔ counts |
| D36 | **Galápagos finding aids** (Beck papers 30+ boxes; Gifford 244 photographs; Hunter, Ochsner, Slevin, Williams, Stewart papers) | https://research.calacademy.org/research/library/special/galapagos.htm ; Beck https://researcharchive.calacademy.org/research/library/special/findaids/Beck.html | Physical holdings; finding aids only. Many notebooks are still held by the research departments | HTML | permission needed for reproduction | Library mezzanine | ◐ (not digitised) |
| D37 | **San Francisco Earthquake of 1906 collection (S.1159)** | https://oac.cdlib.org/findaid/ark:/13030/kt529036n3 | 2.0 cu ft: photographs, correspondence, ephemera, reports; finding aid is the only online item. A blog says the Rixford series was digitised (✘ not located online) | HTML/EAD | unrestricted access; reproduction per Academy policy | Shake House / the old building | ◐ finding aid read; ✘ images not found online |
| D38 | **Wikimedia Commons: Academy categories** | https://commons.wikimedia.org/wiki/Category:California_Academy_of_Sciences (76 files, 14 subcategories) and …Main_building_of_the_California_Academy_of_Sciences (1 file); Wikidata Q965731 (museum), Q134486471 (main building) | Photos and scans | MediaWiki API | per file (CC BY-SA / PD) | Reference photos | ✔ counts |

## 6. GitHub organisations (code, and some data hooks)

| # | Dataset | URL | Contents | Licence | Placement | Ver. |
|---|---|---|---|---|---|---|
| D39 | **github.com/calacademy** (18 public repos) | https://github.com/calacademy | Exhibit software for the floor: `bluewhale` (Giants on-floor touchscreen, pushed 2026-11-05; live at https://s3.us-west-2.amazonaws.com/bluewhale.calacademy.org/index.html), `fade-to-1906-offline` (Giants "Fade to 1906" interactive), `3-systems-static-{carbon,fog,upwelling}`, `a-layered-life-offline`, `race-shifting-idea-offline`, `balancing-the-sun-offline`, `skullwall`, `nightjar`, `wifi`, `RockyReef`, `sketchfab-embed-demo` | none declared on most repos (treat as all rights reserved) | The Giants of Land and Sea hall; study the interactions, do not copy | ✔ |
| D40 | **github.com/calacademy-research** (67 public repos; IBSS) | https://github.com/calacademy-research | Data-adjacent code: `antweb`, `antcat`, `expedition-clustering` (spatiotemporal DBSCAN groups Botany specimens into inferred expeditions), `galapagos_island_mapper` (GBIF Ecuador ~2.3 M records → island assignment and species × island tables; maintainer J. Dumbacher), `cas_bot_georeference`, `explorer-core` (Django API), `collections-explorer-prototype` (Next.js + Convex), `web-asset-importer`, `publications_finder` (OpenAlex), `COMB`, `label_reconciliations`, `LabelLlama_CAS` | mixed (MIT / GPL / Apache-2.0 / none) | Research floors; `expedition-clustering` gives the "expedition" rings in the specimen cloud (data not published, ✘ output files) | ✔ |

## 7. City and park datasets that touch the site

| # | Dataset | Owner · URL | Contents | Format · API | Licence | Placement | Ver. |
|---|---|---|---|---|---|---|---|
| D41 | **Building Footprints (with lidar heights)** | DataSF · https://data.sfgov.org/resource/ynuv-fyni.json · id `ynuv-fyni` | Includes the Academy polygons: a query with `within_circle(shape,37.76986,-122.46609,120)` returned footprint `201006.0000017` (median height 12.08 m, peak 96.43 m ASL) and a small adjoining one (4.06 m). Data as of 2023-09-11 | Socrata JSON/GeoJSON, SoQL | ODC PDDL | Footprint scaffold, roofline check against 07 lidar | ✔ |
| D42 | **Elevation Contours** | DataSF · `6d73-6c4f` · https://data.sfgov.org/resource/6d73-6c4f.json | City contour lines | Socrata | ODC PDDL | Terrain under the park | ✔ (schema), ✘ resolution near the site |
| D43 | **Recreation and Parks Properties; Park Sections** | DataSF · `gtr9-ntp6` https://data.sfgov.org/resource/gtr9-ntp6.json ; `8du2-b837` https://data.sfgov.org/resource/8du2-b837.json | Park polygons incl. neighbours (the Academy parcel itself is **not** listed: `$q=Academy` returned 0 rows in both) | Socrata | ODC PDDL | Park boundary layer | ✔ |
| D44 | **Street Tree Inventory; Urban Tree Canopy** | DataSF · `tkzw-k3nq` (144,606 rows) · `ni2e-vpbg` | Street trees (GGP park trees are Rec & Park, not in this inventory ✘) | Socrata | ODC PDDL | Context trees on Music Concourse edge | ✔ count, ✘ coverage of the park |
| D45 | **USGS 3DEP 2023 lidar, 2010 lidar, NAIP, OSM** | see `07-gis-lidar-imagery.md` | Roof hills and domes at 0.5 m | COPC/EPT | public domain | Roof shell | cross-ref |

DataSF search for "Academy of Sciences" returned **no dataset** that names the Academy. Nothing in the Golden Gate Park open data
describes the Academy building itself beyond D41.

## 8. Live feeds, webcams and shows

| # | Dataset | URL | Contents | Format | Rights | Placement | Ver. |
|---|---|---|---|---|---|---|---|
| D46 | **Academy webcams** | https://www.calacademy.org/learn-explore/live-webcams | Live Penguin Cams (3) https://www.calacademy.org/learn-explore/animal-webcams/live-penguin-cams ; Philippine Coral Reef Cam https://www.calacademy.org/learn-explore/animal-webcams/philippine-coral-reef-cam (YouTube) ; Farallon Islands Cam https://www.calacademy.org/webcams/farallones ; Reef Lagoon cam: offline for maintenance | embeds only; no data API | © Academy | African Hall penguins, Philippine Coral Reef tank, Farallon window | ◐ (pages return 200; embed host for penguin and Farallon not stated) |
| D47 | **Daily calendar pages** | https://www.calacademy.org/daily-calendar-view/2026-11-07 | Feeding times, shows, NightLife | HTML, scrape-only | © Academy | Schedule clock (penguin 10:30 / 15:00 from 05) | ◐ |
| D48 | **Academy models on Sketchfab** | https://sketchfab.com/calacademy/models (see `12-sketchfab-exhibit-models.md`) | 700+ 3D specimen scans (counts per file 12) | glTF via Sketchfab API (token ✘) | mostly CC; check per model | Specimens in the exhibits | cross-ref, ✘ here |
| D49 | **Morrison Planetarium / Visualization Studio** | https://www.calacademy.org/mpvs ; OpenSpace partner page https://www.openspaceproject.com/about/partners.html | In-house fulldome shows. **No open dataset, scene or asset release found**: search returned only background pages. Real-time dome content comes from OpenSpace (MIT) and the AMNH Digital Universe (05 §5) | n/a | © Academy | Dome | ✘ negative result |
| D50 | **Steinhart Aquarium species** | none public. Secondary roster in `11-steinhart-species-roster.md`; iNaturalist guide 970 and the JZBG 2023 paper "The Iconic Philippine Coral Reef at Steinhart Aquarium" (cited in file 11, not re-read here) | 157 chordates, 106 cnidarians … (via guide) | n/a | ✘ | Philippine Coral Reef | ✘ (see file 11) |

**Not found / not public** (re-checked): aquarium water chemistry feed, Living Roof weather or solar telemetry, a Morrison data release,
digitised 1906 earthquake photographs, Anthropology on GBIF, an Academy-run public API for the "Collections Explorer" (the `explorer-core` repo is the Django back-end but no public base URL was found).
Anthropology and Invertebrate Zoology & Geology portals: IZ+GEO are on the IPT/GBIF (D5, D10-D12); Anthropology has no online dataset.

---

## Top 10 for the in-game demo

Scoring 0-2 on five criteria: **A**nchor (coordinates or a natural place in the building) · **V**isually rich · **L**icence open ·
**F**etch in one script · **S**tory the Academy tells. Max 10.

| Rank | Demo layer | Datasets | A | V | L | F | S | Σ |
|---|---|---|---|---|---|---|---|---|
| 1 | The building's own specimens: birds and insects pinned to the zone named on the label | D14 (D7, D3) | 2 | 1 | 2 | 2 | 2 | 9 |
| 2 | Living Roof biodiversity, bloom and visitors by hill | D21, D22, D20 | 2 | 2 | 1 | 2 | 2 | 9 |
| 3 | The Galápagos 1905-06 expedition as a "survivor" globe | D32, D33 | 1 | 2 | 1 | 2 | 2 | 8 |
| 4 | Philippine reef: where the tank's relatives were collected, plus the 60-150 m Twilight Zone column | D5, D6, D4 | 2 | 1 | 2 | 2 | 1 | 8 |
| 5 | Four centuries of collecting: specimen accumulation by year, with the 1906 loss | D1-D9 `year` facet | 1 | 2 | 2 | 2 | 1 | 8 |
| 6 | City Nature Challenge time-lapse over the Piazza | D24 | 2 | 1 | 1 | 2 | 2 | 8 |
| 7 | CC0 specimen image wall (herp, fish, plants) placed by country | D4, D6, D1 | 1 | 2 | 2 | 2 | 1 | 8 |
| 8 | AntWeb ants swarming the roof | D2 | 1 | 2 | 1 | 2 | 1 | 7 |
| 9 | Golden Gate Park as the outside layer | D23 | 2 | 1 | 1 | 2 | 1 | 7 |
| 10 | Expedition journals as pages in the Library | D33, D35 | 1 | 2 | 0 | 1 | 2 | 6 |

Runners-up: DataSF footprints + lidar heights (D41, scaffold not a story), Egg & Nest (D11, CC BY-NC, 5 % georeferenced),
Zenodo spider atlas (D27, images but small).

1. **Specimens collected at the building (D14).** *Visual:* 1,071 small markers (705 birds, 257 insects) pinned to the Front Entrance, West and East Gardens, Piazza and Rooftop, with window-strike hot spots glowing and year driving a slow rain of points (a 2008-2022 bulge). *Fetch:* one GBIF `occurrence/search` over the building polygon, four pages of 300, CC0, no key (recipe 1).
2. **Living Roof biodiversity (D21/D22/D20).** *Visual:* iNaturalist observations as photo cards on the seven hills, sized by species count (969 on the roof), blooming with `observed_on` month (poppy, yarrow, beach strawberry on the original-nine list). *Fetch:* `observations?place_id=55189&photos=true&quality_grade=research` plus `species_counts`, JSON, filter `photo_license` for reuse (recipe 2).
3. **Galápagos 1905-06 (D32/D33).** *Visual:* 4,568 georeferenced specimens as dots on a small Galápagos island map (sphere-inversion "planet" fits), coloured by collector (Slevin, King, Williams, Ochsner), with the Beck journal pages as a texture. *Fetch:* one GBIF query `country=EC&eventDate=1905-01-01,1906-12-31&hasCoordinate=true`, 300 per page, CC0 and CC BY-NC (recipe 3).
4. **Philippine reef sources and Twilight Zone (D5/D6/D4).** *Visual:* 77,824 Philippine records as a point cloud around the reef tank, plus 4,192 fish lots lowered into a depth column at 60-150 m under the floor. *Fetch:* GBIF `country=PH&hasCoordinate=true` (paged) and `datasetKey=5d6c10bd…&depth=60,150`.
5. **Accumulation timeline (all datasets).** *Visual:* a drum of years from 1698 to 2026 filling a particle cloud on the research floors, with the 1905 spike and the 1906 break as the story beat. *Fetch:* one call, `…/occurrence/search?publishingOrg=<CAS>&limit=0&facet=year&facetLimit=400` (313 buckets), then optional per-year coordinate pulls.
6. **City Nature Challenge time-lapse (D24).** *Visual:* a daily pulse (17-21 k observations a day in April 2026) of colour-coded points flooding the Piazza and fading to the Bay Area outline. *Fetch:* `observations/histogram?project_id=263576&date_field=observed&interval=day`, then a capped observation pull; the 2023-2025 project IDs are listed.
7. **Specimen image wall (D4/D6/D1).** *Visual:* 221,515 CC0 herp photographs, 3,499 fish images and 1.8 M plant sheets as frames in the Rainforest dome, grouped by country. *Fetch:* GBIF `mediaType=StillImage` returns the image URL, licence and coordinates in the same JSON; images are hot-linkable from `researcharchive.calacademy.org` / `ibss-images.calacademy.org`.
8. **AntWeb swarm (D2).** *Visual:* 66,365 macro head/profile/dorsal photographs on ants that crawl across the roof model; one sample record is an Argentine ant caught at 37.76928, -122.46628 (on the building). *Fetch:* GBIF dataset `13b70480…` with `mediaType=StillImage` (the AntWeb API itself returned 503/403).
9. **Golden Gate Park outer layer (D23).** *Visual:* 130,213 observations as a ground texture around the model, fading in by season, with species cards (Red-tailed Hawk, Wild Turkey and others from the roof list) appearing at the windows. *Fetch:* `observations/species_counts?place_id=165701` and `histogram`; use the 150793 Oak Woodlands place for a smaller pull.
10. **Journals in the Library (D33/D35).** *Visual:* the six expedition journals as turnable pages (OCR text overlay), placed with the Beck and Gifford photographs. *Fetch:* IA `advancedsearch` for `csfa*` then `archive.org/download/<id>/<id>.pdf`; **rights are not open**, so display only and ask the Academy library (library@calacademy.org per the finding aid) before shipping any page images.

---

## Fetch recipes (top three)

Spaces in `geometry=` must be URL-encoded; `curl -G --data-urlencode` does it. On Windows open JSON with `encoding="utf-8"`.
GBIF caps offset+limit at 100,000 for the search API; the building and Galápagos slices are far below it.

**1. Specimens collected at the building (1,071 records, CC0 mostly)**
```bash
P=66522820-055c-11d8-b84e-b8a03c50a862
for off in 0 300 600 900; do
  curl -s -G "https://api.gbif.org/v1/occurrence/search" \
    --data-urlencode "publishingOrg=$P" --data-urlencode "limit=300" --data-urlencode "offset=$off" \
    --data-urlencode "geometry=POLYGON((-122.4678 37.7684,-122.4644 37.7684,-122.4644 37.7709,-122.4678 37.7709,-122.4678 37.7684))" \
    -o building_$off.json
done
# fields to keep: scientificName, class, eventDate, year, locality, decimalLatitude, decimalLongitude, datasetKey, license
```
Python (one call, merges the pages):
```python
import json, urllib.request as u, urllib.parse as p
q = {"publishingOrg":"66522820-055c-11d8-b84e-b8a03c50a862","limit":300,
     "geometry":"POLYGON((-122.4678 37.7684,-122.4644 37.7684,-122.4644 37.7709,-122.4678 37.7709,-122.4678 37.7684))"}
rows = []
for off in range(0, 1200, 300):
    q["offset"] = off
    d = json.load(u.urlopen("https://api.gbif.org/v1/occurrence/search?"+p.urlencode(q)))
    rows += d["results"]
    if d["endOfRecords"]: break
print(len(rows))   # 1071 on 2026-11-07
```

**2. Living Roof observations with photos (iNaturalist place 55189)**
```bash
curl -s -G "https://api.inaturalist.org/v1/observations" \
  --data-urlencode "place_id=55189" --data-urlencode "photos=true" --data-urlencode "quality_grade=research" \
  --data-urlencode "photo_license=cc0,cc-by,cc-by-sa" --data-urlencode "per_page=200" \
  --data-urlencode "order_by=id" --data-urlencode "order=asc" -o roof_obs.json
# next page: add --data-urlencode "id_above=<last id>"; species list:
curl -s "https://api.inaturalist.org/v1/observations/species_counts?place_id=55189&per_page=200" -o roof_species.json
# photo: results[].photos[0].url, swap "square" for "medium" or "large"; location: results[].location "lat,lng"
```

**3. Galápagos 1905-06 expedition specimens**
```bash
P=66522820-055c-11d8-b84e-b8a03c50a862
curl -s -G "https://api.gbif.org/v1/occurrence/search" \
  --data-urlencode "publishingOrg=$P" --data-urlencode "country=EC" \
  --data-urlencode "eventDate=1905-01-01,1906-12-31" \
  --data-urlencode "hasCoordinate=true" --data-urlencode "hasGeospatialIssue=false" \
  --data-urlencode "limit=300" --data-urlencode "offset=0" -o galapagos_0.json
# 4,568 georeferenced; page with offset 0..4500. Fields: scientificName, decimalLatitude, decimalLongitude,
# eventDate, recordedBy, island, islandGroup, datasetKey
# Whole archives, no key: curl -o orn.zip "http://ipt.calacademy.org:8080/archive.do?r=orn"
```

---

## Open questions for the build
- **Rights to ship:** CC0 (most GBIF rows), CC BY (AntWeb), CC BY-NC (EGG, GEO) and per-photo iNat licences must be tracked per row; keep `license` and `rightsHolder` in the exported JSON. Archive journals (D33) and webcam streams (D46) are display-only.
- **Server health:** `antweb.org` API and `monarch.calacademy.org` were down or blocked on 7 Nov; the GBIF route avoids both.
- **Freshness:** counts above will have moved by the time of the build; re-run the facet calls and store them with a timestamp.
- **Unverified leads:** Rixford 1906 earthquake digitisation (D37), AntWeb API (D19), a public "Collections Explorer" endpoint (D40), the Steinhart species table behind D50.
