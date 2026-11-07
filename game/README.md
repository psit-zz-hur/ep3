# Freeswim Fridays — Cal Academy flooded (design-fiction prototype)

A Three.js prototype of the "Freeswim Fridays" concept: the Renzo Piano building becomes the
aquarium. Divers enter from the Living Roof through the retracted piazza skylight and the
planetarium porthole; fish from the Philippine Coral Reef swim free through the halls.

## Run
Any static server from this folder (ES modules need http):
```
cd game && python3 -m http.server 8080     # then open http://localhost:8080
```
Everything is vendored (three r170 in `vendor/`), so it runs offline on a dome PC.

## Controls
WASD move, mouse look (click to lock), Space up, Shift down, E sprint / ride the Dive Tower up,
Q ride down, F flood or drain, 1/2/3 water presets, D domemaster view, G registration grid,
T / Shift+T tilt ±5°, P save a 4096² domemaster PNG, M flood-zone plan, N lidar grid, H help.

URL params for scripted captures: `?water=9.3&pos=x,y,z&look=x,y,z&dome=1&grid=1&tilt=30&map=1&nohud=1`

## What is real and what is approximate
- Exterior shell: the 2023 USGS 3DEP lidar (90 pts/m², public domain) resampled at 0.5 m, rotated into
  the building frame (`assets/site_meta.json`). Roof hills, both dome crowns (19.3 m), skylight
  portholes and the park trees are measured, not modelled.
- Building box 169 × 110 m, dome radius 13.7 m, piazza skylight 20 × 27.4 m, levels (aquarium −7.6 m,
  main 0, mezzanine 4.6, roof slab 9.6, deck 11.45) come from the lidar and RPBW drawings.
- Interior placement of halls, tanks, café, research wing is approximate (see `src/layout.js`);
  replace with measured positions from the Scaniverse scans.

## Flood-zone plan (M key)
Flooded public: piazza and main-floor circulation, Steinhart aquarium level, African Hall, Morrison
Planetarium (the dome becomes the deepest sphere dive; screen stays on), reef and lagoon tanks (glass
retracted). Dry public with exterior access: Academy Café (west door), The Terrace (east), the
Living Roof deck, Osher Rainforest via a two-door airlock at the piazza. Sealed: penguins, the Swamp
(alligator), Amazon tank (fresh water), California Coast (cold water), research/collections/admin wing,
Project Lab, store, restrooms, theatres, stairs and elevators above L0, life-support and mechanical B2.
Dry route to the roof with the cores sealed: exterior Dive Tower lift beside The Terrace (east) with a
bridge to the deck, and an exterior stair at the café terrace (west).

## Dome output
`src/dome.js` renders a cubemap at the viewer and resamples it to an equidistant 180° fisheye
domemaster (front at the bottom of the frame, IMERSA convention), 2048² live, 4096² on capture (P).
The tilt uniform pitches the lookup so the horizon sits near the audience sweet spot on the 30°
tilted Morrison dome; tune on site with the registration grid (G). See
`research/cal-academy/09-morrison-planetarium-fulldome.md`.
