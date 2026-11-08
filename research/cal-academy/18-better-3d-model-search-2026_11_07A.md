# Better 3D model of the California Academy of Sciences: search result (2026-11-07A)

Bottom line: no better ready-made model of the building turned up. Searches (WebSearch plus WebFetch) found no building model on Sketchfab, TurboSquid, CGTrader, Free3D, Fab, BlenderKit, GrabCAD, Revit City, BIMobject, Archive3D or Thingiverse/Printables/MyMiniFactory. No photogrammetry, splat or point-cloud release of the building was found either. Bryan's 3D Warehouse staff model (3,694 polygons) appears to be the only public 3D model of the building. The practical route to "correct roof hills and domes" is to build it, using free public-domain lidar for the hill geometry. A warning on method: WebSearch is a snippet engine. Sketchfab and 3D Warehouse search pages render client-side, so WebFetch got no result lists from them (marked below). The negative findings come from many queries plus indirect checks, not from a full catalogue crawl. Bryan should run a ten-minute manual search in a logged-in browser on Sketchfab (filters: Architecture, Downloadable), 3D Warehouse, CGTrader and TurboSquid to close that gap.

## Ranked top 5

1. **USGS 3DEP / 2010 GoldenGate lidar, to build the roofs from (best route to correct hills)**
   - Sources: USGS 3DEP public-domain point clouds, 2023 San Francisco project (EPT on AWS, or LAZ); 2010 ARRA-CA GoldenGate survey via OpenTopography (about 3.3 pts/m2 average, denser around SF) [snippet only, unverified for the park]. NASA WERK 2023 1 m DEM (COG) also covers SF [snippet only].
   - Detail: point cloud only. At roughly 1 to 3+ pts/m2 it should resolve the seven hills (a few metres of relief over about 170 x 110 m) and the two dome rises. It will not resolve glass, rafters or interior.
   - Licence: public domain. Download mechanics: free, no login for AWS/EPT; OpenTopography needs a free account [unverified].
   - Judgment: free, measured and accurate. Gives true roof heights, which the staff model lacks. Needs a Rhino/CloudCompare meshing step.
   - URLs: https://www.geoweeknews.com/articles/usgs-3dep-lidar-data-now-available-to-the-public/ ; https://www.fisheries.noaa.gov/inport/item/73386 ; https://wifire-data.sdsc.edu/dataset/nasa-werk-dem-ca-sanfrancisco-1-b23 ; https://rapidlasso.de/?p=3728

2. **Existing 3D Warehouse staff model (the baseline Bryan has, id 1a4c209a43561ba445f5590ac69325a5)**
   - Fetched: https://embed-3dwarehouse-classic.sketchup.com/model/1a4c209a43561ba445f5590ac69325a5/California-Academy-of-Sciences
   - Author: 3D Warehouse Staff; last modified 2014-03-20; 3,694 polygons, 27 materials, 3 layers, inches; 8K downloads, 38K views; no interior.
   - Judgment: confirmed low detail. Keep it only as a footprint and massing guide. Use it as a scale check against the lidar.

3. **Hand-build from published drawings plus the lidar surface (RPBW / Fondazione Renzo Piano / Stantec / Webcor)**
   - Pages checked: https://www.rpbw.com/project/california-academy-of-sciences ; https://www.rpbw.com/publications/renzo-piano-san-francisco-california-academy-of-sciences-monograph ; https://www.fondazionerenzopiano.org/media/project_document/5964e4027a12f100177762.pdf (surfaced in search only, not read) ; https://www.stantec.com/en/projects/united-states-projects/c/california-academy-of-sciences ; https://webcor.com/project/california-academy-of-sciences (all surfaced in search; none shows a 3D or BIM download) [unverified].
   - Judgment: the only way to get correct domes (27.4 m) and interior. Works as sheets, sections and plans. A written request to RPBW, Stantec or the Academy's press office for any BIM/Rhino massing is cheap to try, but expect no reply (NDA-type material).

4. **Google Photorealistic 3D Tiles (view-only reference, not an asset)**
   - Policy page fetched: https://developers.google.com/maps/documentation/tile/policies
   - Terms: no pre-fetch, store or cache beyond HTTP cache headers; no export, extraction or scraping; no offline use; building 3D models from the tiles is named as prohibited; your own 3D objects may be overlaid only if not extracted, traced or derived from the tiles.
   - Judgment: gives an excellent look at the roof, but display through the API only. Do not trace from it. Use it only as eyeball reference.

5. **DataSF building footprints with 3D characteristics (height only)**
   - Found via: https://datasf.org/blog/new-sf-building-footprints-released-with-3d-characteristics (redirects to https://www.sf.gov/departments--city-administrator--datasf ; not read further). Footprints are collapsed from a 2010 Pictometry 3D model; heights come from lidar ground and roof surface statistics [snippet only].
   - Judgment: gives a footprint and summary heights only (an extruded block). No roof hills. Not a 3D model.

## Other candidates checked

| Candidate | URL | Finding |
|---|---|---|
| 3DCADBrowser "San Francisco City, CA, USA 3D Model (2024)" | https://www.3dcadbrowser.com/3d-model/san-francisco-city-ca-usa-2024 | Fetched. 57.3M polygons, AI photogrammetry, 4096 textures x 251 tiles; OBJ/FBX/MAX/BLEND/C4D; paid account. Extent: lat 37.7662-37.8112, lon -122.4294 to -122.3725. The Academy is near lon -122.466, so it is outside this box (my inference from known coordinates). Not useful. |
| RenderHub "San Francisco, California USA 50km" (3dstudio) | https://www.renderhub.com/3dstudio/san-francisco-california-usa-50km | Fetched. 12M polygons, GIS-based, $149, 3dm/3ds/c4d/fbx/obj/stl, "low poly", 2.2 GB. City-scale; the Academy would be a small low-detail block. Not worth the price for this purpose. |
| CGTrader "San Francisco streets and buildings" | https://www.cgtrader.com/3d-models/exterior/landmark/san-francisco-streets-and-buildings | Fetch returned empty. Unverified, city-scale anyway. |
| SOM San Francisco Digital Context Model | https://www.architectmagazine.com/?p=149598 | Fetched. Built by SOM SF for itself and used by Planning for zoning visuals; no public download stated. Not available. |
| Academy's own Sketchfab | https://sketchfab.com/calacademy/models | Fetch gave HTTP 500; search snippets show about 769 models, all specimens and artifacts; downloads by request form. No building. [snippet only] |
| Academy Viz Studio Sketchfab | https://sketchfab.com/vizstudio/models | Fetched 25 of 65: rocks, trees, coral, point clouds, LSST telescope. No building in the visible part; 40 not seen. |
| Sketchfab collection by williamj.mitchell | https://sketchfab.com/williamj.mitchell/collections/california-academy-of-sciences-30009f3befb34a91a66cf09e44f4ced1 | Fetched. 31 models, animals and hominin fossils (dioramas). No building. |
| Sketchfab collection by edemaistre | https://sketchfab.com/edemaistre/collections/california-academy-of-sciences-d170f803470c4bc19d838be6550f0750 | Fetched. 21 specimen scans (skulls, fish). No building. |
| OpenStreetMap main building way | https://www.openstreetmap.org/way/28695389 | Search snippet only: height 8, roof:material grass; no building:part roof detail. Height only. |
| Archibase 3D-Archive blog entry | https://archibase.co/blog/view/3997.html | Fetched. A 2012 video post, not a model. |
| LEGO Ideas build | https://ideas.lego.com/projects/4906ab65-978a-4075-b60c-a53624695693 | A 373-brick physical design, not a file. |

## Dead ends (no building model found)

- Sketchfab search page (https://sketchfab.com/search?q=california+academy+of+sciences+building&type=models) and 3D Warehouse search page (https://3dwarehouse.sketchup.com/search/?q=california%20academy%20of%20sciences): both render client-side; WebFetch returned no results. Not checked by eye.
- TurboSquid, Free3D, Fab, BlenderKit, GrabCAD, Revit City, BIMobject, Archive3D, Thingiverse, Printables, MyMiniFactory: web searches returned no listing for the building [search only; sites not crawled directly].
- MorphoSource: not searched (unlikely, specimens only).
- Photogrammetry, Gaussian splat, Polycam, Luma, Scaniverse: one search, nothing found [search only; Polycam/Luma public galleries are not indexed well, so a manual look is worthwhile].
- Apple Maps: no accessible 3D data; not used.
- Cesium ion / OSM Buildings: only OSM height 8 m with grass roof; no detail.
- RPBW, Fondazione, Arup, Stantec, Webcor, ArchDaily, Architizer, Arch2o, Archello pages: images and text only; none offers a model or point cloud.
- Citywide DataSF / Planning 3D model download: no public CityGML/OBJ/3D Tiles of the city found. Only footprints with heights.

## Recommendation

1. Treat the lidar as the source of truth for the hills: pull the 2023 USGS 3DEP SF tiles for the Academy bounding box (37.769 N, -122.466 W), mesh the roof surface, and cut it into the footprint.
2. Use the 3D Warehouse model for footprint, ground plane and scale check, and the two published domes (27.4 m) for the dome volumes.
3. Add glazing and the piazza from published plans and sections (RPBW monograph, Architectural Record pages).
4. In parallel, spend ten minutes on manual searches (list above) and send one request to the Academy press office and RPBW for any BIM massing.

Nothing was downloaded or committed.

## Addendum (Freeswim session, 20:25, checked in Bryan's logged-in Chrome)
- **Sketchfab "California Academy of Sciences" by echeng (Eric Cheng)**: https://sketchfab.com/3d-models/california-academy-of-sciences-9d5a2e52172942829ccfe82cc1db9ce5 -- drone photogrammetry of the whole building and roof, 1,000,000 triangles, 475.4k vertices, "Aerial images captured with DJI Inspire 1 and Zenmuse X5 camera with DJI 15mm lens", processed with Pix4D (pix4d avatar on the page). 545 views, 5 likes. **View-only: no Download button.** This is the best 3D model of the building seen tonight (real roof hills, domes, skylights, textured). Route: ask the author for the model or for download permission (Eric Cheng, echeng.com, well known in the drone/underwater photo world); a Sketchfab comment or his site's contact form. Bryan's call.
- Sketchfab "Oceans Edge" (264 views) and "California Academy of Sciences Redwoods" (201 views) appear in the same search; not inspected.
- 3D Warehouse search page needs the cookie banner dismissed before results render in text; not re-checked beyond the 2014 staff model.
