# Field Capture Guide — California Academy of Sciences (Sat 7 Nov 2026)

Interim version written while research tracks were still running. Verified
specifics from the splat-tooling research track are merged into section 9.
Items marked **(verify)** were not confirmable from this session's network.

## 1. What Scaniverse gives you, and what it does not

- **Splat export:** PLY and SPZ (Niantic's compressed splat format, ~10x smaller
  than PLY, open source at github.com/nianticlabs/spz). Both load in SuperSplat,
  Spark, GaussianSplats3D, PlayCanvas, Blender 4.5+/5.x.
- **Mesh export (LiDAR mode):** OBJ, FBX, GLB, USDZ, STL, PLY, LAS point cloud.
  The GLB carries textures and is the easiest "mesh layer" for the web.
- **Raw data:** Scaniverse has a *Save raw data* option (RGB frames, LiDAR depth,
  device trajectory) that lets you *reprocess inside the app* with different
  settings. The community forum's staff answer has been that raw data is **not
  exportable** out of the app **(verify — may have changed)**. Assume you cannot
  get frames/poses out of Scaniverse for COLMAP/Postshot/Brush.
- **Video:** Scaniverse does **not** save the capture video to Photos. If you want
  reusable source footage, record it separately (section 3).

So: **turn on Save raw data** in Scaniverse settings before you start, and plan a
second pass per space with the native Camera app or Record3D for reprocessable
frames.

## 2. Recommended app stack for today

| Role | App | Why |
|---|---|---|
| Primary splat | Scaniverse (Splat mode, Save raw data ON) | On-device, free, PLY/SPZ out, geo-tagged |
| Primary mesh | Scaniverse (Mesh/LiDAR mode, "Large" area setting) | Textured GLB that becomes the mesh layer |
| Reprocessable frames + poses | Record3D (RGB-D + ARKit poses export) or Polycam (raw photo export) | Lets us retrain with Postshot/Brush/gsplat on the laptop |
| Plain video backup | iOS Camera, 4K30, exposure locked, HDR off | Frame-extract for COLMAP; also b-roll for the portfolio |
| Reference stills | iOS Camera, ProRAW off, HEIC fine | Texture reference, color calibration |

If you only have time for one extra app, make it **Record3D**: it exports the RGB
video, per-frame depth, and ARKit camera poses, which is exactly what we cannot
get out of Scaniverse.

## 3. Camera settings (iPhone 17 Pro)

- Use the **main (1x) camera** for splats. Ultrawide has more distortion and
  worse low-light; only use 0.5x for cramped spots and keep it consistent within
  a scan.
- Video: 4K at 30 fps, HDR video **off**, lock AE/AF (long-press), keep ISO low.
  Avoid 60 fps indoors (shorter shutter = more noise). Apple Log is fine but
  then we grade before SfM; simpler to shoot standard.
- Turn **off** Macro auto-switch and Lens Correction (Settings > Camera).
- Clean the lens. Museum glass puts fingerprints on everything.
- Airplane mode off: we want GPS/compass in metadata for the exterior.

## 4. Movement protocol for each space

1. Walk a slow loop around the subject at chest height, phone in portrait,
   ~1 m/s or slower. Scaniverse's coverage overlay should stay green.
2. Repeat the loop at knee height, then at arm's-reach-above-head height.
3. Add "look-ins": stop at 6-8 points and arc the phone 90 degrees.
4. Close the loop: finish where you started and overlap the first 10 seconds.
5. Keep 60-80 percent overlap between consecutive viewpoints; never swing fast.
6. Keep moving people out of frame when possible; when not, keep them small
   and moving (they become faint ghosts the trainer can prune).
7. Do not change lenses mid-scan. Do not pause for more than a few seconds.
8. For each space, capture **one wide "anchor" scan** that includes a floor
   pattern, a column base, and a wall junction. These are the registration
   anchors we align other data to.

## 5. Priority capture list (ranked for splat quality and portfolio value)

1. **The Piazza** under the glass canopy. Widest, best lit, most "Renzo Piano".
   Do the loop at ground level and again from the mezzanine edge if open.
   Capture the canopy structure looking up.
2. **Osher Rainforest dome, exterior shell** from the Piazza floor (the glass
   sphere with its spiral ramp visible). Then the **interior ramp**: walk the
   spiral slowly in one continuous Scaniverse take; it is a natural loop.
3. **Morrison Planetarium sphere exterior** (the big matte sphere). Its smooth
   surface is hard for photogrammetry but fine for splats; get the base where it
   meets the floor and the walkway around it.
4. **African Hall**: dioramas behind glass are tricky, but the hall itself
   (columns, ceiling, floor) splats well. Capture the penguin tank from a
   distance only.
5. **Living Roof observation deck**: hills, skylights, PV canopy edge, de Young
   tower in the distance. Shoot in the direction away from the sun. Capture
   the skylight domes from close range for the roof-to-interior mapping.
6. **Exterior, east and west facades** along the concourse: glass wall, steel
   columns, canopy overhang. Walk the full length at two distances (3 m, 10 m).
7. **Entrance hall with T. rex** and the Foucault pendulum area.
8. **Swamp and the mezzanine railing** looking down at the alligator pool.
9. **Aquarium tunnel (Amazon flooded forest)**: dark and curved glass; expect a
   noisy splat but a striking one. Record3D helps here (depth).
10. **Exterior from the Music Concourse** including the fountain and de Young
    facade, for the "planet" / sphere-wrap scene context.

Hard or low-yield: the Philippine Coral Reef tank (moving water and fish),
the planetarium interior during a show (dark, dynamic), anything reflected in
glass, hugely crowded spots at midday. Capture these as plain video for mood,
not as splats.

## 6. Shots that help registration later

- Four photos of the Academy site map/wayfinding signs (scale reference).
- A measured feature: pace or tape one column spacing in the Piazza and note
  it in your phone notes; also photograph a floor tile with a shoe for scale.
- Exterior shots from across the concourse with the whole facade in frame (for
  aligning to the GIS footprint and lidar).
- Roof deck panoramas with the horizon visible (orientation).

## 7. File handling on the phone

- Scaniverse: Share > Export > PLY (splat) and SPZ; for mesh scans export GLB
  with textures and LAS. Save to Files > iCloud Drive > CalAcademy/<space>/.
- Record3D: Export "RGBD video + poses" (zip) to the same folder.
- Name everything `YYYYMMDD_<space>_<take>_<app>.<ext>`.
- Expect 200 MB to 1.5 GB per large splat PLY; SPZ is roughly a tenth. Free up
  10-20 GB before you start.
- Scaniverse processes on-device; let big scans finish processing before you
  start the next one or the queue stalls.

## 8. Rules of the house

The Academy's published filming policy covers **commercial** shoots (insurance,
after-hours interiors, specialevents@calacademy.org). Handheld personal
photography is fine; tripods, gimbals, and lights typically are not. Keep it
handheld and unobtrusive, and if staff ask, say it is personal reference
photography. The policy page is linked in the dossier for your records.

## 9. Verified specifics from the tooling research track

- **Confirmed: Scaniverse raw data cannot be exported** through the app. The only route
  is `descaniverse` (github.com/jampekka/descaniverse), which pulls the saved raw data out
  of an unencrypted iOS backup and converts it to Nerfstudio format. So **turn on Save raw
  data** anyway, and do not delete raw data in-app until we have tried that on the laptop.
- **Best pose-bearing companion app:** Polycam LiDAR with **Developer Mode ON** (exports
  keyframe images, 4x4 camera extrinsics, intrinsics, depth, confidence) or **SplatKing**
  (native COLMAP export). Either beats Record3D for our purpose. If you have neither
  installed and no time, the native Camera 4K video pass is the fallback.
- **Scaniverse has no in-app merge and no true pause.** One scan per zone, 25% overlap
  into the neighbouring zone, merge later in SuperSplat / splat-transform.
- **Scaniverse writes SPZ v4.** Export **PLY as the master** alongside SPZ; some tools
  still read only older SPZ versions.
- **Official Niantic guidance** for big interiors: three passes (ceiling, floor, mid);
  perimeter loop then crisscross; pause at doorways with both sides visible; separate
  scans for indoor vs outdoor; a short scan with strong coverage beats a long one with gaps.
- **Tripods and monopods are not allowed** for visitors (staff statement, older thread;
  current wording unverified). Keep everything handheld.
- **Web stack decision:** Spark 2.4 (MIT, Three.js) exposes per-splat GLSL hooks
  (`objectModifier` / `worldModifier`) that let us do the sphere-inversion "planet" and
  other non-Euclidean warps directly on the splat. mkkellogg's GaussianSplats3D is no
  longer maintained and its README points to Spark.
- **Budget:** aim for under ~2M splats per loaded scene for phones; the merged building
  will need Spark's `.rad` LOD streaming.
