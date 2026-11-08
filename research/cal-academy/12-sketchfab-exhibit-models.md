# Sketchfab models of Academy exhibits and specimens

Checked 8 Nov 2026 from the public model pages (sketchfab.com; the API host is not reachable from this session).
"FREE DOWNLOAD" = the page title says "Download Free 3D model" (author enabled downloads, usually CC BY). Downloads still
require a logged-in Sketchfab account: run `research/cal-academy/scripts/sketchfab_fetch.py` on the laptop with your API token.
Credit every author; view-only models can be embedded with the Sketchfab viewer but not pulled into the game.

## Academy Viz Studio (@vizstudio) — https://sketchfab.com/vizstudio
Photogrammetry of the real Philippine Coral Reef tank (the big tank, the "buddha wall", corals), Caribbean corals, a dusky damselfish
animated by Ken Ackerman, "Ken's schooling fish", and planetarium previs geometry. The reef-tank scans are the ground truth for the
reef in the game; they are view-only, so use them as reference and embed them in the portfolio page.

## Visitor collection by Emm (@edemaistre) — https://sketchfab.com/edemaistre/collections/california-academy-of-sciences-d170f803470c4bc19d838be6550f0750
iPhone scans (Scenario app) of public-floor exhibits: full-scale T. rex, megalodon jaws, Hubbs' beaked whale skull, walrus and grizzly
and alligator skulls, redwood cross-section, seal and sea lion skeletons, sea turtle, reptile fossil, a large fish mount, coral.

## Status per model
| Model | Author | Download | URL |
|---|---|---|---|
| Philippine coral reef photogrammetry | Viz Studio | view only | https://sketchfab.com/3d-models/philippine-coral-reef-photogrammetry-57042a82ee7246b6899832512404dd08 |
| Steinart Phillipine Reef Big Tank | Viz Studio | view only | https://sketchfab.com/3d-models/steinart-phillipine-reef-big-tank-b491a18288b14100a81265519aabc0a9 |
| Steinhart Aquarium, Philippine Coral Reef | Viz Studio | view only | https://sketchfab.com/3d-models/steinhart-aquarium-philippine-coral-reef-627a6abdb1834a5b8d9ad1f954da2972 |
| Steinhart Philippine Reef Buddha Wall | Viz Studio | FREE DOWNLOAD | https://sketchfab.com/3d-models/steinhart-philippine-reef-buddha-wall-33b9a3f789f24ee097a2487a848b2f92 |
| kens-schooling-fish-v01-03dbdbd13cbe45ec91feb5dc2e1b0363 | ? | unknown (page rate-limited) | https://sketchfab.com/3d-models/kens-schooling-fish-v01-03dbdbd13cbe45ec91feb5dc2e1b0363 |
| Dusky damselfish | Viz Studio | view only | https://sketchfab.com/3d-models/dusky-damselfish-5d4447bbb11b40428c796daa33caa8c7 |
| Acropora palmata 01 | Viz Studio | FREE DOWNLOAD | https://sketchfab.com/3d-models/acropora-palmata-01-90e4a9481fb143769d7107ca3b78f16c |
| Echinophyllia sp. | Viz Studio | FREE DOWNLOAD | https://sketchfab.com/3d-models/echinophyllia-sp-f530e005c95b476d9fa3f6f974df387d |
| day-279-full-scale-tyrannosaurus-rex-skeleton-0390e81bbbc74a | ? | unknown (page rate-limited) | https://sketchfab.com/3d-models/day-279-full-scale-tyrannosaurus-rex-skeleton-0390e81bbbc74aa38b4021a0b58c6115 |
| Full-scale Megalodon jaws | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/full-scale-megalodon-jaws-0c58b98201174b06b678dc469091e646 |
| Hubbs' beaked whale skull | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/hubbs-beaked-whale-skull-1b6becc5e55f48fe813418e2e7be09b2 |
| Redwood cross section | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/redwood-cross-section-128329651df94258b2305ad7358f6f75 |
| Seal & seal lion skeletons | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/seal-seal-lion-skeletons-5624a29e5b9844d8a05be630b4cc9e96 |
| Sea turtle | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/sea-turtle-1a77b2b578cb449a98a4cc9653e5168b |
| Alligator skull 🐊 | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/alligator-skull-7e389853aa9f4723b824b166491ab150 |
| Humongous tropical fish, Cal. Academy of Science | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/humongous-tropical-fish-cal-academy-of-science-c12ba0d543e5407abfaaf60df343efed |
| Grizzly bear skull | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/grizzly-bear-skull-0d59abfbb8c34864b96fa9e68b21da4c |
| Day 310: Walrus skull | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/day-310-walrus-skull-810b86b2f0834d86b33bbb2e8bdde76e |
| Reptile fossil (California Academy of Sciences) | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/reptile-fossil-california-academy-of-sciences-fb83029815304e61ae5945e6281d2269 |
| Coral | Emm (@edemaistre) | FREE DOWNLOAD | https://sketchfab.com/3d-models/coral-7da18265ce31434fb3010fcbdb1ee6f6 |

## Official Academy collection (@calacademy) — https://sketchfab.com/calacademy/models
769+ specimen scans (skulls, mollusks, basketry, fish, herps). Downloads are off; each page has a request form that feeds
https://www.calacademy.org/3d-model-download-request . Terms (https://www.calacademy.org/3d-model-licensing-terms): cite the Darwin Core
triplet (CAS:HERP:12345) and the media DOI/ARK, non-commercial without written approval, no redistribution. Good for a "Skulls" room.

## In the game
- `game/src/props.js` places each downloaded model at its exhibit position (T. rex in the entrance hall, megalodon jaws and whale
  skull nearby, redwood slice in Giants of Land and Sea, skulls in African Hall, corals in the reef and lagoon).
- **K** starts a fly-through of the nearest scan: the camera enters the bounding box, passes through the hollow of the skull or the
  jaws, pulls out and orbits once. Works with any loaded prop.
- Credits are written to `game/assets/props/CREDITS.md` by the fetch script.
