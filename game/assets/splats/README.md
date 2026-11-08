# Splats (Scaniverse captures) for the game

Drop the cleaned scans here as `<space>.spz` (or `.ply`); they are git-ignored. `manifest.json` is committed and holds
the registration of each scan into the game frame. `src/splats.js` loads whatever the manifest lists and exists.

## From the phone to here
1. Scaniverse > Library > the scan > Share > **Export Model** > `SPZ` (small) and `PLY` (master). LiDAR mesh scans: also `GLB`.
2. Get them to the laptop (AirDrop is not an option on Windows): share sheet > Save to Files > Google Drive (personal),
   or a USB cable with the Apple Devices app, or LocalSend. Land them in `Downloads`.
3. `python research/cal-academy/scripts/ingest_captures.py` moves `Downloads/*.spz|*.ply|*.glb` into `captures/<space>/`
   (asks for the space name per file, or takes `--map "IMG_1234=piazza"`), and copies the SPZ here as `<space>.spz`.
4. Reload the game. `V` shows the splats, `X` the planet warp. Unregistered scans sit at their `guess` position.

## Registering a scan (three ways)
- **In the game:** `__fs.splats.nudge(0, {dx: 1, ry: 15})` in the console moves scan 0 (metres, degrees, `s` scales);
  `__fs.splats.exportManifest()` prints the manifest with the result baked in (frame `game`). Paste it over this file.
- **CloudCompare:** align the scan's PLY (centres) to `data/cal-academy/lidar2023/calacademy_2023_utm10.copc.laz`,
  copy the 4x4 from the console into `matrix` (16 numbers, row-major) with `frame: "utm10n"`.
- **splat-transform (merge / convert):** `npx @playcanvas/splat-transform in.ply -t x,y,z -r rx,ry,rz -s k out.spz`.

Entry fields: `space`, `file`, `frame`, one of `matrix` | `position`+`quaternion`|`rotationDeg`+`scale` | `guess`,
`yDown: true` for a SuperSplat-exported PLY, `enabled`, `captured`, `app`, free notes.
