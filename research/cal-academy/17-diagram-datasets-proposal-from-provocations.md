# Proposal from PROVOCATIONS [1] (2026-11-07, by cross-session message, filed verbatim by the Freeswim session)

Status: a thinking reply for Bryan; no files changed by PROVOCATIONS. Companion to `16-diagram-proposal-from-the-diagram.md`.

PROVOCATIONS proposal: which Academy datasets belong in THE DIAGRAM viewer, and the smallest changes that would carry them.

First, the lens I used. The Diagram's grammar is fixed and strong: x = year, y = log distance from one centre (the school; here the Academy at 37.76986, -122.46609, Golden Gate Park as the zero), events = dots at year x distance, long-running things = bars (the degrees lane), and the DISC = the same data as an azimuthal map from the centre with a year ring, a sweeping hand, and pings sized by sqrt(count) at a place. It draws ink, not pictures. So the datasets that earn a place are the ones that carry (year, place) pairs or (start, end) spans. Everything else is off-grammar however spectacular it is in the game.

## 1. Ranked candidates
1) The Academy's own collection as year x distance dots (census 15b D1-D9, the 12 GBIF datasets). 2.18 million georeferenced specimens with a collecting year, binned to (year, log-distance band, bearing) counts. The pre-1906 band is nearly empty (the fire), the Galapagos cluster sits at about 5,000 km in 1905-06, then the climb through Madagascar, the Philippines, Costa Rica. Licence CC0 (3.26 M rows), CC BY (AntWeb), CC BY-NC (GEO, EGG: 24 k rows, mark them).
2) The 12 datasets as bars (the degrees lane): a bar per dataset from first to last collecting year, thickness = records per year. "DEGREES OFFERED" becomes "SPECIMENS SO FAR" in the numeral panel. Cited to the GBIF dataset page and DOI.
3) Galapagos 1905-06 (D32) as the first span bar plus its dot cluster: a span (Jun 1905 - Nov 1906) and 4,568 georeferenced records at one bearing and one distance, sub-layered by collector (Slevin, King, Williams, Ochsner, Beck). The journals (D33) enter only as a link-out field, never as page images.
4) The building's own 1,071 specimens (D14): counts per year 2008-2022 at distance 0, by zone (Front Entrance 189, Rooftop 177, Business Entrance 97, West Garden 83, East Garden 70, Living Roof 47, Piazza 17): 692 window-strike birds and 277 insects. On the chart a short strip on the 0 KM ground line; on the DISC pings at the centre.
5) iNaturalist at the centre and the park (D20 Academy 10,348 obs, D21 Living Roof 3,885, D22 Grounds 5,282, D23 Golden Gate Park 130,213) plus City Nature Challenge SF Bay Area by year (D24, 2016-2026): counts per year 2008-2026 in the 0-3 km and 0-100 km bands. Counts only, no photos.
6) The Philippine expeditions 2011-2015 (D5, D6, D4 country=PH, 77,824 georeferenced) as a second span bar with its cluster at about 11,000 km. The 60-150 m Twilight Zone depth is a third axis the viewer does not have; leave depth to the game.
7) Farallon Islands seabird series 1968 to now (file 15 §2, Point Blue via NOAA ERDDAP): counts per year at one fixed distance, 43 km west. Candidate only; unverified endpoint.

## 2. What the viewer can show today, and the smallest tweak for each
- 1 and 6: a `count` field on an event node and dot radius by sqrt(count) on the CHART (the disc has it); an importer that writes aggregated nodes from the GBIF Darwin Core archives (per dataset zip from ipt.calacademy.org, no key) binned to year x 1/4-degree cell, then to log band x bearing. The public file is a few hundred kB of bins; each bin node cites the GBIF occurrence-search URL that returns exactly its rows.
- 2: a bar whose thickness varies by year; or 12 plain bars with a per-year histogram strip under the lane.
- 3: a `url` field per node, shown in Properties of the selection and in the ledger text as a hairline link.
- 4: a "ground strip" that stacks counts per year on the ground line.
- 5: the same ground strip, plus bands at 1-3 km and 10-100 km.
- Axis: year0 and span as two properties of the Viewport, set to 1850 / 200 for this build; the 1698-1849 records in a "before" gutter.
- The 1906 break: a vertical rule on the paper and a radial tick on the disc, in the RDS red of the inks. No blast, no hollowing.
- Numerals: YEAR stays; the second numeral becomes the running count of specimens collected so far.

## 3. What I would leave out, and why
AntCat and Eschmeyer's Catalog of Fishes (no place); Sketchfab, MorphoSource, image walls, Corsi photos (pictures, NC terms); webcams, calendar, sensors, energy (no time depth or no feed); DataSF footprints, contours, trees (scaffold); OpenAlex, Zenodo, NCBI, Dryad, Figshare (unstable counts, off-story); Monarch inventory (no place or year per row, 503); iDigBio (duplicate route); Anthropology (all rights reserved); archive texts, BHL, Internet Archive journals (link-outs only).

## 4. Numbers to distrust or to label before citing
- "With images": 15b says 551,615 across the publisher; file 15 says 2,128,295. Cite per dataset, never the publisher total.
- Botany year span "1528-2026": a data-entry error; start the axis at 1850, gutter earlier records.
- GRSciColl "46,000,000 specimens" vs GBIF 4.2 M: different units. Cite GBIF.
- iDigBio institutioncode=cas 3,253,581: not de-duplicated. Do not cite.
- OpenAlex 10,222 vs 5,577: do not cite a total. Zenodo "8,229 records": only 260 are datasets.
- The 1905-06 spike reading: "GBIF year facet, 7 Nov 2026", not "the Academy says".
- Catalog of Fishes 37,799: not re-verified. AntWeb API 503/403: cite DOI 10.15468/wqmjjt.
- Licence limits: IA journals and film display-only; webcams stream-only; Sketchfab NC by request; MorphoSource CC BY-NC; GEO and EGG CC BY-NC; iNaturalist photos per observer (counts only); specimen images copyright claimed while records are CC0. Every node carries a "queried on" date.

## 5. The one view
THE COLLECTING DISC. Centre: the Academy. Ring: 12 o'clock = 1850, one turn = 200 years, the 12 datasets as the ring's bars. Paper: year 1850-2026 across, log km from the building up, the 1906 rule in red. Dots: every collecting locality on earth as a ping sized by specimens collected there so far; at the centre, the building's own 1,071. The hand sweeps 1853 to 2026 and the second numeral counts specimens so far. Almost nothing survives before 1906 except one cluster 5,000 km away; from 1906 the Academy rebuilds itself from the whole Pacific inward, until the last fifteen years, when the nearest band fills faster than any expedition ever did. One more: the same disc with all layers off except Galapagos 1905-06 and the building slice: the specimens that escaped the fire and the birds that hit its glass.

Effort, if Bryan says yes later: the GBIF archive pull and binning is one script and an evening (check Botany's zip size, stop under 2 GB without his word). The viewer changes are four small properties plus the variable-thickness bar.
