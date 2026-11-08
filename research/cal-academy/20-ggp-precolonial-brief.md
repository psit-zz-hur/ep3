# Golden Gate Planet, pre-colonial versions (2026-11-07, 21:25)

Bryan, verbatim: "let's make some versions of GGP (golden gate planet) in which everything outside of GGPark is a recreation of a pre-colonial ecosystem, what would have existed there prior to San Francisco existing."

## Versions
- **V1 · the park as an island in its own past**: the park stays as today (the 1 m core, NAIP, trees); everything outside becomes the Outer Lands before 1769/1848: dunes, lakes, creeks, scrub, prairie, beach, no buildings, no streets.
- **V2 · the whole planet before the city**: the park too goes back to sand (it was the "Great Sand Waste" until the 1870s planting), so the planet is dunes end to end with the lakes and the two creeks.
- Both ride the same orrery, sea at real sea level, Ocean Beach as beach.

## What the ground already gives us
- Geometry: the bare-earth DTM (USGS 1 m) IS the dune field under the city; strip buildings and trees and the dunes roll from Ocean Beach to the park. Where grading flattened them (streets), a 1850s smoothing pass or the Coast Survey contours can restore the shape.
- Water: Mountain Lake, Lake Merced (edge), Pine Lake (Laguna Puerca), Laguna Honda, Lobos Creek, the Sunset's seasonal ponds and the sloughs behind the dunes; the park's own lakes are 1870s-1900s constructions (Stow Lake 1893) and leave in V2.

## Sources for the habitat colour layer (the indexical class drape)
- US Coast Survey topographic sheets 1852-1857 (T-sheets) of San Francisco: dunes, lakes, vegetation, trails; public domain; georeferenced rasters via NOAA Shoreline Data Explorer / NOAA Historical Map & Chart Collection; also David Rumsey (CC BY-NC-SA).
- SFEI (San Francisco Estuary Institute) historical ecology: Bay Area habitat polygons; check coverage of the city's west side.
- Nature in the City "Hidden Nature SF" map and Joel Pomerantz's "Seep City" (water history of SF): lakes, creeks, springs, dune lakes; licences to check (reference, not redistribution).
- Presidio Trust / GGNRA historical landscape studies (Lobos Creek, dune restoration targets): the species lists for dune scrub, coastal prairie, coastal scrub, freshwater marsh, willow riparian, beach strand.
- Yelamu (Ramaytush Ohlone) presence: village/camp sites known from the record near Lobos Creek and the Presidio; name the land, no invented sites.

## Habitat classes (for the class raster and its legend)
beach strand · foredune (bare sand) · dune scrub (lupine, coyote brush, mock heather) · coastal prairie · coastal scrub · willow riparian · freshwater marsh · lake · tidal strand / rocky shore (Lands End) · oak-bay woodland (east, outside the 6 km mostly).

## Build plan (THE TERRITORY bakes; this session prepares)
1. Fetch and georeference the 1850s T-sheet(s) covering lon -122.51..-122.44 (NOAA GeoTIFF if available, else Rumsey IIIF + manual control points).
2. Classify the sheet into the habitat classes (colour/texture + hand polygons where the sheet is symbolic), rasterise on grid C (5 m) and the park core grid (1 m): CALACADEMY_PRECOLONIAL_HABITAT_*.tif + legend CSV.
3. Water polygons for the lost lakes and creeks (digitise from the sheet), flat surfaces at their levels.
4. V1 drape: NAIP inside the park mask, habitat palette outside; V2: habitat palette everywhere, park trees removed (DTM instead of DSM in the core).
5. Dots: elk, pelicans, whales offshore instead of fish? Bryan's call.

## Open questions for Bryan
- V1 and V2 both, or V1 first?
- Palette: naturalistic (sand, grey-green scrub, dark willow) or the planet's indexical inks?
- Moving dots: keep the fish, or fauna of the dunes and the shore?

## V3 · the park as an island (21:30)
Bryan: "let's make another version where everything else is ocean, and use that water-generating code from that Reddit post I sent you" = web-ocean (see 14-water-rendering-web-ocean.md: JONSWAP spectrum, FFT displacement, LEAN glitter, MIT). V3: the park core at 1 m stands as an island; everything outside the park outline is sea at real sea level (or at the park's lowest edge, ~5 m, so the island has a shore); the ocean drawn with the web-ocean method if THE TERRITORY's renderer can carry it, else its present sea. Open: shoreline = park boundary or the 5 m contour; waves scaled to the planet; the fish stay.

## THE TERRITORY's answers (21:40)
- One fork, shared code, assets/v0 (today) v1 v2 v3, chosen by ?ggp=v1|v2|v3 (a page reload, not a dial); each version has its own views.json.
- Needs from us: 1 m bare-earth DTM on the park core grid; park-outline masks (uint8) on the core grid and grid b. Both in preparation.
- V1: DSM inside the park, DTM outside; rim DTM; habitat drape outside; lost lakes/creeks as water. V2: DTM + habitat everywhere. V3: park = land mask, the Territory's sea outside; with real NAVD88 heights the park stands 10-100 m above the sea (cliffs, low at Ocean Beach) unless Bryan names a sea level (drowned-city reading: sea at the park's lowest edge).
- web-ocean: partly feasible (three.js r128 / WebGL2): JONSWAP/FFT as a GPU pass making normal + foam maps + LEAN glitter in the sea shader; no vertex displacement (invisible at planet scale). V3 first with the present sea; web-ocean as a follow-up (~a day). Standing law "matte ocean, no glint" holds for the Territory; glitter only on the GGP V3 skin by Bryan's word.

## Bryan's V3 rulings (21:45, verbatim)
- "1. drowned to the park's lowest edge so it settles into the water" -> sea level = lowest DTM value on the park outline.
- "2. web-ocean's glint on V3's sea, yes - let's try it" -> JONSWAP normals + foam + LEAN glitter on V3 only; the Territory stays matte.

## Bryan on the look (21:55, verbatim)
"for the pre-colonial version, I think it would be dunes and native grasses, with elk running around" -> V1/V2 palette: bare sand foredunes + dune grass / coastal prairie as the dominant classes (scrub, willow and lakes as accents); the moving dots become tule elk herds on the prairie (the FLOW/vessel engine with herd paths instead of ferry timetables); the fish stay offshore.

## V3 fauna (22:05, verbatim)
"the ocean version needs whales, that come up to the surface and blow their spouts" -> V3: whales (grey whales on the coast migration; humpbacks; the blue whale is the Academy's own) as the moving layer: a slow track under the surface, a surfacing every few minutes with a spout (a short vertical puff that drifts and fades), a back and a fluke silhouette; one ink, the fish's spirit. Elk on V1/V2, whales on V3.

## Transit layer in V1/V2/V3 + the morph (22:10, verbatim)
"let's have an option where we leave on the transit layer in the precolonial and ocean version. In the precolonial version, when the bus sprite leaves Golden Gate Park, the bus sprite should change into a herd of Tule Elk galloping together along the bus route, following it, arcing gently, naturally, to follow the path. ... In the ocean version, when the bus sprite leaves Golden Gate Park, the bus sprite should change into a giant sea turtle, like in Sky; Children of the Light, that swims gently along the bus route, turning gently. make boids appropriate to these."
- Inside the park outline: the bus sprite on its GTFS schedule. Crossing the park mask outward: V1/V2 -> a herd of tule elk (boids: 8-15 agents, separation / alignment / cohesion + path-following on the route polyline as a leader, limited turn rate so the herd arcs, gallop bursts); V3 -> one giant sea turtle (single agent, slow, max turn rate low, heading eased, flipper beat; Sky: Children of the Light feel). Crossing back in: the bus again. The route is the same GTFS shape in all versions; the timetable keeps the departures.
- Tule elk in pre-colonial SF: yes by the record (Spanish diaries 1769-1776 note elk on the peninsula and around the Bay; the Outside Lands' prairie and dune swales are elk country; hunted out of the city by the 1850s-60s; the Point Reyes herd is the living reference). To be confirmed with citations by the research job (file 22).

## Transit animals, round two (22:20, verbatim)
"in the ocean version, it could be a whale instead of a sea turtle, and at the bus stops, the whale could spout or flip a dorsal fin or breach. let's try that too. when the herd of elk hit a bus stop, they should stop and graze. I'm interested in there being pelicans too, in the ocean one. Perhaps the pelican flock is always flying around, like the fish do in Sagi Planet."
- V3 transit sprite: whale as an alternative to the turtle (try both); at each GTFS stop the whale does a stop-behaviour: spout, dorsal roll, or breach (weighted random), timed to the dwell.
- V1/V2 transit elk: at each stop the herd halts and grazes for the dwell (heads down, slow drift within spread_m), then re-forms and runs on.
- V3 ambient: a pelican flock always in the air over the sea, the fish's role (a boid flock, line-astern glides low over the water, occasional climbs and plunge-dives), one ink.
