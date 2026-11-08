# Proposal from THE DIAGRAM [1] (2026-11-07, by cross-session message, filed verbatim by the Freeswim session)

Status: a proposal for Bryan. Nothing built. Years marked [verify] are THE DIAGRAM's own flags.

THE FIT. Replace "school" with "institution". The Academy, in Golden Gate Park, San Francisco, becomes the centre of the disc and the zero of the distance axis. Bars stay "things the institution keeps doing over years". The red events stay "things that happened at a year and a place".

## 1. What goes where
- BARS (spans, open end if still running), in four groups, one group per lane:
  a. Series: Proceedings, 1854 to now.
  b. Collections by their finding-aid date ranges (each OAC finding aid gives the range).
  c. Buildings: Market Street to 1906; Golden Gate Park halls from 1916 [verify]; Steinhart Aquarium 1923 and Morrison Planetarium 1952 [verify]; the temporary Howard Street site 2004 to 2008; the Piano building from 2008.
  d. People: curators and collectors as career spans, e.g. Alice Eastwood, curator of botany 1892 to 1949 [verify]. Their own lane, never mixed with collections.
- POINTS (red events, at year x log km from the Academy): the 1906 earthquake and fire at 0 km; Loma Prieta 1989 at about 0 km. Digitisation milestones are points too: first GBIF publication, the Internet Archive uploads, Calisphere.
- SPAN EVENTS: expeditions, e.g. Galapagos 1905 to 1906 at about 4,700 km [compute from the gazetteer]. The voyage sits far out on the log axis while the city burns at 0 km, the same year.
- COUNTS, new: specimen records per year (the GBIF census, 1698 to 2026, the 1905-06 jump) as a strip under the bars, one cell per year, in one ink.

## 2. World events: the rule
Keep an event only if the Academy's own record shows it: a break, a jump or a gap in the data, or an act of the Academy itself. Context alone is not enough.
- Keep: 1906 earthquake and fire (the collection lost). Galapagos 1905-06 (the jump in records). Loma Prieta 1989, if a closure or a building decision follows it [verify]. The founding, 1853, as the axis start.
- Test, then decide: the two world wars (keep each only if records per year dip in 1917-18 or 1942-45). The 1915 Panama-Pacific Exposition: keep only if an Academy collection or exhibit is tied to it [verify].
- Drop: Darwin and Origin of Species, 1859. No line in the Academy's data shows it; it belongs in the gloss.

## 3. What the viewer lacks (rough cost order)
- Axis range: fixed to 1930-2029 today. The Academy needs 1853 (or 1698 for the counts) to 2029. Make the start year a setting.
- A link-out on click: Trial hides the title block, so a click shows nothing (found 10/31). One caption card per node: year, name, source, link. The same card fixes the degrees chart.
- The counts strip: a new layer type.
- On the disc: the GBIF records with coordinates as pings by year, binned to a grid (4.2 million points will not draw one by one).
- Image pins: last, and links only (field journals are display-only rights).

```
1853 ......1906.........1989....2008......2029
PROCEEDINGS ==================================>
MARKET ST  =====|
GG PARK          ========================|
PIANO BLDG                                 ====>
EASTWOOD     ==============
[records/yr] .....#####...........::::::::::::::
red, log km:  1906 fire @0 km; Galapagos 05-06 @4,700 km; 1989 @0 km
```

## 4. Stable URLs (each node carries one, plus an access date)
- Strongest: OAC finding aids by ARK (oac.cdlib.org/findaid/ark:/13030/..., e.g. the 1906 collection kt529036n3).
- Strong: Internet Archive items (archive.org/details/<id>, e.g. the Beck journal csfa777220765). Link only.
- Strong: Calisphere items by ARK; prefer an item page to the institution page.
- Strong: GBIF. Cite the Academy's dataset DOI, and for the counts a GBIF download DOI (needs a GBIF account: Bryan's call).
- Probably stable: the Proceedings on the Biodiversity Heritage Library [verify].
- Weaker: archives.calacademy.org item pages and calacademy.org/archives-collection-list. Cite with an access date, keep the matching OAC ARK beside them.
Citation rule kept: no node without a source.

Recommendation: build it as a second institution in the same viewer, not a fork. The work is: axis range, the caption card, the counts strip, in that order. Nothing starts until Bryan says so.
