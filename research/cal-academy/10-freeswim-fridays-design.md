# Freeswim Fridays — design notes, flood-zone plan, access

Design fiction: after close on Fridays the Renzo Piano building floods to the roof slab, the aquarium
glass retracts, and visitors dive in from the Living Roof. Prototype: `game/` (Three.js, offline).

## Seed tank: Philippine Coral Reef
Warm tropical water, 25 ft deep, 212,000 gallons, ~2,000 fish, living corals, blacktip reef sharks and rays.
Academy divers already swim in it daily ("Reef 101"), so humans in the water with these animals is an
existing, safe practice. Open-topped at main-floor level with viewing windows on the aquarium level: it
already reads as "descend into it".

## Flood-zone plan (public space only; all exhibits assumed waterproofed)
| Zone | Status | Why / how |
|---|---|---|
| Piazza + main-floor circulation, Giants of Land and Sea, Color of Life | FLOOD | the open heart; the retracted 66x90 ft skylight is the main dive entry |
| Steinhart aquarium level (galleries, Water Planet, Twilight Zone gallery) | FLOOD | tank glass retracts for the reef and lagoon only |
| Philippine Coral Reef, Reef Lagoon | FLOOD, glass retracted | warm-water, diver-safe residents |
| Morrison Planetarium | FLOOD | the 27 m sphere becomes the deepest dive; projectors in sealed housings, the show runs underwater; entry via the west-hill porthole |
| African Hall (dioramas) | FLOOD | waterproofed dioramas; a drowned temple |
| Osher Rainforest | DRY | glass sphere kept at 85 F / 75% RH; two-door **airlock** at the piazza entry; also reachable dry from the east-hill hatch |
| Academy Café | DRY | exterior door on the west facade |
| The Terrace restaurant | DRY | outside the shell on the east end; its own doors |
| Living Roof deck | DRY | the "shore"; public |
| Penguins (African Hall south end) | SEALED | cold water, their own enclosure |
| The Swamp (Claude the alligator) | SEALED | animal and diver safety |
| Amazon Flooded Forest (under the rainforest) | SEALED | fresh water; arapaima, venomous freshwater rays; viewed through its glass from the flood |
| California Coast | SEALED | 55 F cold water; viewed through glass from the flood |
| Research / collections / admin wing, Project Lab, Naturalist Center, library | SEALED | non-public, paper and specimens |
| Store, restrooms, Forum / Hohfeld theatres, Shake House | SEALED | electronics, merchandise, motion platform |
| Stairs and elevators above L0, B2 life-support and mechanical, loading dock | SEALED | the aquarium's life support must stay dry and running |

Interior doors to seal: every door on the south-side research corridor at L0 and L-1; stair and elevator
doors at L0 and the roof; the penguin and swamp service doors; the Amazon and California Coast
life-support access; the store, restroom and theatre doors; the Project Lab glass wall (keep it as a window).

## Getting visitors to the roof with the cores sealed
Internal elevators are sealed and the stairs are under water, so the dry route must be exterior:
1. **Dive Tower**: an exterior lift beside The Terrace (east end), grade to the deck (11.45 m), with a short
   bridge onto the living roof. The Terrace is already a dry zone with its own doors, so it becomes the
   check-in and gear-up room.
2. **Café stair**: an exterior stair from the café's west terrace up the facade to the deck, as the second
   egress the fire code would demand.
3. Alternative to building anything: make one existing stair core watertight (two sealed doors at L0 and
   L-1) and use it as a dry trunk; realistic, but it removes the pleasure of arriving on the roof from outside.
Both exterior routes are in the prototype (M map shows them in orange; E/Q rides the lift).

## Dive loop
Terrace, gear up; Dive Tower to the roof; walk the hills to the skylight; drop into the piazza (sunlit reef
layer); the reef tank and lagoon; halls at mid-water; the planetarium porthole for the deep sphere; the
Twilight Zone on the lowest level; surface in the rainforest airlock to breathe real air among trees;
back to the roof via the east-hill hatch.

## Core experience beats (in the prototype)
- Gravity-free exhibit reading: hover in front of a plaque; the card fades in only when you are still.
  Breath cycle raises and sinks you, exhale bubbles rise past the text, fish cross the mask.
- Species discovery: a fish within 2.8 m and in view is logged with its card; goal is the full roster.
- Sealed tanks viewed from the water: a human in a larger tank watching garibaldi behind glass.
- The planetarium show seen while drifting under its dome.

## Water column (depth in the building = depth in the ocean)
| Layer | Building level | Fog / light |
|---|---|---|
| Sunlit reef | above -2 m (main floor, piazza, under the skylight) | teal, far |
| Mid-water halls | -2 to -6.5 m | blue, medium |
| Twilight Zone | below -6.5 m (aquarium level, planetarium bottom) | indigo, short, lanternfish glow |

## Fulldome
See 09-morrison-planetarium-fulldome.md. The game's D key renders an IMERSA-style domemaster with the PDB
V14 registration grid overlay (G) and a tilt uniform for the 30-degree dome.
