# Laptop handoff — Cal Academy / Freeswim Fridays

Branch: `claude/vibrant-hypatia-fdw8wx` on `psit-zz-hur/ep3`. Everything below is committed.

## 1. First five minutes
```bash
git clone https://github.com/psit-zz-hur/ep3.git && cd ep3 && git checkout claude/vibrant-hypatia-fdw8wx
cd game && python3 -m http.server 8080        # open http://localhost:8080
```
In the game: click to lock the mouse, F floods, O skin, I tile/concrete, J Skateboard Saturdays, D dome view, G grid,
M flood plan, K fly-through, H help. Start on the west roof hill; the skylight ring below is the dive entry.

## 2. Pull the data (public domain and open; ~1.5 GB)
```bash
bash research/cal-academy/laptop-bootstrap.sh            # lidar 2023 + 2010, DEMs, RPBW drawing PDFs, ArchDaily, Rumsey maps
export SKETCHFAB_TOKEN=...                                 # Sketchfab > Settings > Password & API
python3 research/cal-academy/scripts/sketchfab_fetch.py   # 16 exhibit scans incl. the NHM blue whale -> game/assets/props/
```
Manual, browser + login: 3D Warehouse massing model (save as `game/assets/cas_3dwarehouse.glb`, run with `?model=1`).

## 3. Today's Scaniverse captures
Export each scan as PLY (master) and SPZ; also GLB for LiDAR mesh scans. Put them in `captures/<space>/` (git-ignored).
Pipeline (see research/cal-academy/06-splat-and-web-tooling.md):
1. SuperSplat in the browser: clean floaters, crop glass noise, export compressed PLY.
2. Register to the lidar: CloudCompare, align each splat's point centres to `calacademy_2023_utm10.copc.laz`
   (or to the game frame via `game/assets/site_meta.json`: rotation 137.5 deg, centre 547023 E / 4180411 N UTM10N,
   ground 77.05 m). Save the 4x4.
3. `npx @playcanvas/splat-transform` to apply transforms and merge; export SPZ.
4. Load in the game with Spark (`npm i @sparkjsdev/spark three`) as a `SplatMesh`; this is the step not yet written.
   Target: a `splats.js` module next to `poolskin.js`, toggled with a key, with the sphere-inversion warp as a dyno modifier.
If Scaniverse "Save raw data" was on: `descaniverse` can pull frames + poses from an unencrypted iOS backup for Postshot/Brush.

## 4. What exists
| Path | What |
|---|---|
| research/cal-academy/00-README.md | index of the dossier (files 01-14) |
| research/cal-academy/02-downloads-manifest.md | every download with URL, format, size, license |
| research/cal-academy/09-morrison-planetarium-fulldome.md | dome specs, formats, how to get a demo on the dome |
| research/cal-academy/10-freeswim-fridays-design.md | flood-zone plan, roof access, dive loop |
| research/cal-academy/11-steinhart-species-roster.md | 88 reef species + other tanks, sources, hazards |
| research/cal-academy/12-sketchfab-exhibit-models.md | exhibit scans, licenses, the whale |
| research/cal-academy/13-game-precedents.md | 25 games with one lesson each |
| research/cal-academy/14-water-rendering-web-ocean.md | what to borrow from web-ocean (MIT) |
| research/cal-academy/contact-sheets/ | lidar, interiors, 3D assets, precedents, sock renders |
| game/ | the prototype; README.md documents every module and key |

## 5. In flight at handoff time
A research agent is compiling a census of every public dataset the Academy hosts (collections portals, GBIF/iDigBio,
research deposits, iNaturalist, planetarium assets, archives, live feeds, GitHub). It lands as
`research/cal-academy/15-cal-academy-public-datasets.md` with a ranked top-10 for a visualization demo. If this file is
missing when you read this, the agent had not finished; re-run the brief in `research/cal-academy/00-README.md`.

## 5b. Laptop state (7 Nov 2026, evening; this clone lives at Documents\Claude\ep3, git-ignored by the workspace repo)
- three r170 -> r187 and Spark 2.4 are vendored (`game/vendor/`); importmap has `@sparkjsdev/spark`. Runs on the laptop's
  Intel Arc at 35-45 fps at 1024x768 (not the 60 fps hoped for; it is an iGPU).
- `game/src/splats.js` is written: Spark `SplatMesh` per scan from `game/assets/splats/manifest.json`, frames `game` /
  `utm10n` (site_meta transform) / `scan` (guess + in-game nudge), sphere-inversion planet warp as a dyno
  `objectModifier` (centre, radius, mix uniforms; three presets). Keys: V splats, X warp, Shift+X next planet;
  `?splats=0`, `?planet=1..3`; `__fs.splats.nudge()` / `.exportManifest()` for registration by hand.
- Tested with a synthetic splat of the lidar DSM (`scripts/lidar_to_splat_ply.py`, 189k gaussians, git-ignored):
  loads, registers at identity on top of the lidar mesh, warps into the little planet. Scaniverse scans not yet exported.
- `scripts/ingest_captures.py` moves phone exports from Downloads into `captures/<space>/` and stages SPZs for the game.
- `laptop-bootstrap.sh` run: see `data/cal-academy/` (PDAL clip skipped, PDAL not installed). rockyweb throttles the LAZ tiles
  to ~128 KB/s and truncated the first; the raw cloud for the site came from the S3 EPT instead (`scripts/lidar_ept_site.py`,
  877 nodes -> `data/cal-academy/lidar2023/ept_site_game.ply`, 1.5 M pts in the game frame).
- Sketchfab: all 16 props fetched with Bryan's token (CC BY x14, the NHM whale CC BY-NC-SA); they load in the halls; textures
  are capped at 2k on load (`props.js`); `?props=0` skips them. `CALACADEMY_3D_ASSETS/` (git-ignored) holds every asset as one
  file (GLB per prop via gltf-pipeline, splat PLYs, lidar mesh PLY, raw point cloud PLY, the Rhino files); `game/contact_sheet.html`
  renders them all on one page.
- ADMIN mode (` key): OrbitControls + WASD/QE fly, physics off; white LAYERS panel (`src/layers.js`) with every part on/off, each
  splat on/off, PROPERTIES as sliders (render scale, raymarch steps, pause render (R), dome view/grid/tilt, flood map, camera
  bookmarks, water, pool skin incl. fillet radius, the blob planet) and the registration of the selected scan. Dome view moved to C.
- Pool skin mode 2 SKATEPARK (I cycles): troweled concrete with canary hatched routes (three laps) and stand-here discs; J uses it.
- BLOB PLANET: one preset, mirrored so the roof sits on top (Shift+X flips). The other two presets are gone at Bryan's request.
- Rhino: `scripts/export_rhino_3dm.py` -> `rhino/CALACADEMY_SITE_2026_11_07A.3dm` (mesh + massing + splats) and `..._B.3dm`
  (+ POINTCLOUD layer from the EPT cloud). Frame: game frame Z-up, (x, y, z) = (X, -Z, Y), metres, origin = main floor centre.
- Lidar DSM mesh exported (`scripts/export_lidar_mesh.py` -> `exports/`) and handed to THE VIEW [1] session by message.
- Dataset census: `15-cal-academy-public-datasets.md` (cloud agent) and `15b-cal-academy-building-anchored-datasets.md`
  (laptop session, live-tested). First picks for the demo: Ornithology window-strike birds on the facades; Philippine fishes by depth.
- Status board: `scripts/build_board.py` -> `boards/CALACADEMY_BOARD_<date>A.png` (3840 x 2160) from `boards/img/` (stills by
  `scripts/board_shots.py`, headless).

## 6. Open work, in order
1. ~~Splat loader (Spark)~~ done; registration of the real scans to the lidar frame once they are exported.
2. Scaniverse scans: export from the phone (SPZ + PLY) -> `scripts/ingest_captures.py` -> register in the panel.
3. Skate physics against the SDF (port `map()` from poolskin.js to JS for the player collider; transitions, airs).
3. BIM-grade mezzanine, bridges and rainforest ramp from the Fondazione sections (drawing-336/328/279 PDFs).
4. Fixed-step 4096x4096 domemaster frame capture for the 7thSense Delta; email planet@calacademy.org with a test frame.
5. Water: port JONSWAP displacement + LEAN glitter from web-ocean into `water.js`.
6. Replace approximate interior positions with measured ones from the scans.

## 7. Known rough edges
- Swiftshader screenshots are slow; on the laptop GPU the game should run at 60 fps at 1080p.
- `poolskin.js` SDF has ~40 primitives; keep raymarch steps at 160, or lower `faceRes` in dome mode.
- Commons/Wikipedia APIs rate-limit scripted fetches; pace them.
- The environment "ep3 (architecture research)" holds the allowlist of hosts used; irrelevant on the laptop.
