# Gaussian Splatting: Capture -> Processing -> Three.js Delivery (state of play, 7 Nov 2026)

Research track report. GitHub repos were fetched directly (strongest citations). Vendor sites
(scaniverse.com, nianticspatial.com, poly.cam, jawset.com, sparkjs.dev, calacademy.org) were
blocked for this track, so their facts are from search summaries, marked **[search-only]**.
**[UNVERIFIED]** marks things nobody could confirm.

## 1. Scaniverse (Niantic Spatial)

| Item | Finding | Source |
|---|---|---|
| Splat mode | Free, unlimited, on-device 3DGS training (~60-90 s processing per secondary guides). | [search-only] https://www.3dgsviewers.com/learn/guide/scaniverse ; https://radiancefields.com/platforms/scaniverse |
| Splat export | **SPZ** and **PLY** (Library > Share > Export Model). USDZ for splats reportedly added July 2026 [search-only]. dev site lists SPZ, PLY, GLB, USDZ. | https://radiancefields.com/scaniverse-adds-usdz-export-to-splats ; https://dev.scaniverse.com/ ; https://community.scaniverse.com/t/which-formats-can-scaniverse-export-to/50 |
| Mesh (LiDAR) export | FBX, OBJ, GLB, USDZ, STL (community) / OBJ, FBX, GLB, USDZ, LAS (App Store). Point clouds PLY, LAS. Confirm in the Share menu. | https://community.scaniverse.com/t/can-i-generate-a-point-cloud/49 |
| Raw video / frames | **Not exportable.** "Save raw data" (2022) keeps RGB frames, LiDAR depth and trajectory inside the app sandbox for in-app reprocessing only. No Files/Photos export. Open feature request: https://community.scaniverse.com/t/export-scan-raw-data/136/1 | https://scaniverse.com/news/save-raw-data-for-future-processing [search-only] |
| Getting raw data out anyway | **descaniverse** (reverse-engineered): enable Save raw data before recording; extract via unencrypted iOS backup (`idevicebackup2` + `ideviceunback`, or the `iOSbackup` Python package) from `/Library/Application Support/scans/`; `to_nerfstudio` converts to Nerfstudio format. Not everything recoverable. | https://github.com/jampekka/descaniverse |
| Processing location | Classic app: on-device. "New Scaniverse" (Plus/Pro business tiers, Feb 2026) adds cloud processing and Scaniverse Web (phone scans and 360 video from Insta360 X4/X5/X6). | [search-only] https://www.nianticspatial.com/docs/scaniverse/360camera/ ; https://thenewstack.io/niantic-spatial-scaniverse-world-models/ |
| Size / duration limits | Not published [UNVERIFIED]. Niantic: break a site into smaller sections; long scans reduce alignment stability. | https://www.nianticspatial.com/docs/scaniverse/techniques/ [search-only] |
| Pause/resume | No true pause control found; guide says pause movement at doorways while recording. [UNVERIFIED] | same |
| Merge scans in-app | **None.** Merge downstream (SuperSplat / splat-transform). | same |
| Geo-location / VPS | Location stored locally, shared only on opt-in. SPZ has `SPZ_NIANTIC_georeference` extension. Public POI upload paused after Lightship migration. | https://github.com/nianticlabs/spz ; https://www.nianticspatial.com/en/faq/scaniverse-lightship-migration [search-only] |
| Sharing | Web viewer links, public or unlisted (Classic). New Scaniverse: private unless exported. | [search-only] |
| iPhone 17 Pro | Not explicitly listed [UNVERIFIED]; 2.0+ supports all iPhones including non-LiDAR, so expected to work. | https://medium.com/scaniverse/scaniverse-2-0-adds-support-for-non-lidar-devices-e5b22b6b3300 |
| Official large-indoor tips | Several overview scans per large room; enclosed space: 3 passes (ceiling, floor, mid); open areas: perimeter loop then crisscross; pause at doorways with features from both sides visible; separate scans for indoor/outdoor; "shorter scan with strong coverage beats longer scan with gaps". | https://www.nianticspatial.com/docs/scaniverse/techniques/ ; https://www.nianticspatial.com/docs/scaniverse/troubleshoot/ [search-only] |

**SPZ format (GitHub, authoritative):** current **v4** (v1-v3 legacy, read-only); zstd, per-attribute streams; ~10x smaller than PLY; **MIT**; C++, TypeScript (WASM), Python bindings; CLI + browser converter (PLY<->SPZ up to ~2 GB); SH degree 0-4; extensions `SPZ_ADOBE_coordinate_system`, `SPZ_ADOBE_safe_orbit_camera`, `SPZ_NIANTIC_georeference`; default coord system RUB. **Caveat:** Scaniverse now writes SPZ v4; older readers fail. three.js r186 SPZLoader and Spark 2.4 handle v4. https://github.com/nianticlabs/spz

## 2. Alternatives to run on the same walk

| App | Splat export | Raw frames + poses? | Notes | Source |
|---|---|---|---|---|
| **Polycam** | Splat PLY (paid) | **Yes.** LiDAR captures: enable **Developer Mode** before capturing, then "Raw Data" zip (same device). Layout (polyform): `keyframes/images`, `corrected_images`, `cameras/*.json` (intrinsics, 4x4 extrinsics, blur_score), `corrected_cameras`, `depth/` 16-bit PNG mm, `confidence/`, `raw.glb`. Nerfstudio has a Polycam importer. | Basic $150/yr or $30/mo; raw export on free tier [UNVERIFIED]. | https://learn.poly.cam/hc/en-us/articles/38276871185044-How-to-Extract-Raw-Data-and-What-Is-Included [search-only]; https://github.com/PolyCam/polyform (MIT) |
| **SplatKing** (radiancefields.com) | via desktop | **Yes: native COLMAP export** (poses, images, sparse points, per-frame depth + confidence) in a "splatpack" folder; v1.0.2 Jun 2026. iOS 17/18+. Pricing [UNVERIFIED]. | | https://radiancefields.com/splatking/guide/output |
| **Record3D** | No | RGB-D video (.r3d), EXR depth + JPG sequence, PLY sequence, OBJ/glTF/FBX/Alembic; LiDAR; per-frame poses in .r3d metadata widely reported [not verified]. | one-time IAPs | https://github.com/marek-simonik/record3d (LGPL-2.1) |
| **Spectacular Rec** | No | Yes: video + IMU (+ARKit); `sai-cli process` -> Nerfstudio/gsplat datasets without COLMAP. SDK non-commercial. | | https://github.com/SpectacularAI/sdk |
| **Voxelio** | SPZ on-device | "Original capture dataset export" [search-only] | new 2026 | https://apps.apple.com/lu/app/id6764829442 |
| **Scantic** | on-device 3DGS | "raw-file export, offline" [search-only] | Aug 2026 | https://digitalproduction.com/2026/08/20/gaussian-splats-on-the-iphone/ |
| **KIRI Engine** | PLY (Pro) + OBJ | not found | Pro $17.99/mo; MIT After Effects splat plugin | https://radiancefields.com/platforms/kiri-engine |
| **Luma 3D Capture** | PLY | No | unmaintained; Genie/Flythroughs shut Jan 2026. Do not rely on it. | https://radiancefields.com/luma-ai-to-sunset-flythroughs-on-january-1-2026 |
| **RealityScan Mobile 1.9** (Epic) | meshes only | images on device; desktop RealityScan 2.x (free < $1M revenue) does alignment -> feeds Postshot/Brush | | https://www.realityscan.com/ai-info |
| **Teleport by Varjo** | PLY (cloud) | No | free 5 scans/mo | https://radiancefields.com/varjo-announces-teleport-2-0 |
| **XGRIDS LCC Scan 2.0** | PLY / LCC2 | [UNVERIFIED] | | https://radiancefields.com/xgrids-releases-lcc-version-2 |

**Recommended reusability stack:** (1) Scaniverse splat mode, SPZ+PLY, Save raw data ON; (2) Scaniverse mesh mode per zone; (3) Polycam LiDAR with Developer Mode ON, or SplatKing, for images + poses + depth; (4) native Camera 4K video, AE/AF locked, as SfM insurance; (5) optional Record3D for hero spaces.

## 3. Capture methodology
Sources: https://www.nianticspatial.com/docs/scaniverse/techniques/ ; https://ar-go.co/blog/gaussian-splatting-production-workflow/ ; https://docs.vulkan.org/samples/latest/samples/complex/render_octomap/Tutorials/capturing-gaussian-splats.html ; https://www.polyvia3d.com/guides/gaussian-splatting-from-photos
- Parallax, not panning. Rotating in place is the most common failure. Always translate.
- Overlap 70-80% between neighboring views, 60-70% between height rings; three heights (knee, chest, overhead).
- Loop closure: start and end each zone at the same anchor; perimeter loop then crisscross / figure-eight.
- Speed ~0.3-0.5 m/s, slower in dim light; pause at doorways.
- Lock exposure/WB/focus; split indoor/outdoor into separate scans.
- Glass, water, mirrors: shoot oblique, accept noise, mask in SuperSplat later.
- Sections + anchors: 20-30% overlap between zones; shared anchor features; one scale reference (door width, floor tile, tape).
- Video vs photos: resolution matters more than fps; shutter >= 1/120 s (raise ISO; noise averages out, blur does not).
- iPhone 17 Pro: 48 MP on all three cameras, Apple Log 2, ProRes RAW, 4K120. For SfM do **not** use Log or ProRes RAW; use 4K60 HEVC Rec.709, exposure locked, no HDR, one lens per scan (main 24 mm). https://fstoppers.com/gear/iphone-17-pro-and-pro-max-bring-200mm-zoom-prores-raw-and-powerful-photo-and-711173 ; https://nofilmschool.com/iphone-17-pro
- GPS/compass: Camera-app stills embed GPS + heading; Postshot 1.1.69 can apply GPS to cameras [search-only]; take geotagged stills at each anchor.

## 4. Processing tools and training times
| Tool | Platform | Inputs | Merge? | Notes | Source |
|---|---|---|---|---|---|
| **Postshot** 1.1.69 | Windows, NVIDIA only | images/video, COLMAP, RealityScan | **Yes (scene merging)** [search-only] | free non-commercial tier; PLY/SPZ export | https://radiancefields.com/platforms/postshot |
| **Brush** | macOS Apple Silicon, Win, Linux, Web; Apache-2.0 | COLMAP, Nerfstudio, masks | No | one Mac report: 30k steps / 4M splats = 2h05 | https://github.com/ArthurBrussee/brush |
| **gsplat / Nerfstudio splatfacto** | CUDA only | COLMAP | No | ~6 GB VRAM; `ns-export gaussian-splat` | https://github.com/nerfstudio-project/nerfstudio |
| **OpenSplat** | Metal (Mac), CUDA, ROCm, CPU; AGPL-3.0 | COLMAP, OpenSfM, ODM | No | outputs ply/splat/spz; M2: 7k steps ~50 min | https://github.com/pierotofy/OpenSplat |
| Inria 3DGS | CUDA | COLMAP | No | baseline | https://github.com/graphdeco-inria/gaussian-splatting |

Training time: RTX 4090 ~21 min per Mip-NeRF360 scene at 30k steps (https://arxiv.org/pdf/2503.10148). Laptop RTX 4070/4080: estimate 30-75 min per zone [UNVERIFIED]. Apple Silicon (Brush/OpenSplat): 1-2+ hours per zone; plan overnight runs for 4-6 zones.

## 5. Merging, registration, georeferencing, scale
- **SuperSplat** (PlayCanvas, MIT, browser, v3 WebGPU): import multiple PLY/SPZ/SOG; per-splat transform, crop, delete; export PLY, compressed PLY, SOG, SPZ, .splat, standalone viewer. https://github.com/playcanvas/supersplat ; https://radiancefields.com/supersplat-adds-multiple-splat-ability
- **splat-transform CLI** (PlayCanvas, MIT): inputs PLY/compressed PLY/SOG/SPZ/SPLAT/KSPLAT/LCC; outputs PLY, compressed PLY, SOG, streamed SOG LOD bundle, SPZ, GLB with KHR_gaussian_splatting, CSV, HTML viewer; **merge multiple inputs with per-input translate/rotate/scale**, box/sphere crop, opacity filter, SH strip, decimate. The scriptable merge step. https://github.com/playcanvas/splat-transform
- **Registration (splat -> point cloud -> ICP):** export splat PLY (centers are a point cloud; drop floaters with an opacity filter), load in **CloudCompare**; coarse-align with point-pair picking including scale; ICP two passes (loose then tight); verify with cloud-to-cloud distance; apply the 4x4 to the splat in SuperSplat / splat-transform. https://arxiv.org/pdf/2409.16296 ; https://www.plainconcepts.com/digital-twins-3d-gaussian-splatting/
- **Scaniverse LiDAR mesh as the metric anchor:** the mesh is already metric (ARKit); register each splat to it so splats inherit real scale; then georeference the assembly to USGS 3DEP lidar or GPS anchors.
- **Scale via known dimension:** measure a door/tile in the splat, apply uniform `--scale` in splat-transform.

## 6. Web delivery (Three.js, 2026) and warp hooks
| Viewer | License | Formats | Custom per-splat shader / warp? | Status | Source |
|---|---|---|---|---|---|
| **Spark 2.4.0** (World Labs) | **MIT**; three >= 0.180 | PLY, compressed PLY, SPZ, SPLAT, KSPLAT, SOG; LOD `.rad` | **YES.** `SplatMesh.objectModifier` / `worldModifier` take dyno blocks embedding raw GLSL rewriting `gsplat.center`, `.scales`, `.quaternion`, `.rgba` per splat; `context.viewToWorld/worldToView` for view-dependent effects; `covObjectModifiers` for covariance-correct warps; `SplatEdit` SDF displacement/recolor; global `opacity`/`recolor` for cross-fades; WebGL2, mobile-friendly; LOD streaming (`build-lod` -> `.rad`/`.radc`). | Active | https://github.com/sparkjsdev/spark (docs: splat-mesh.md, dyno-overview.md, splat-editing.md, lod-getting-started.md; example `examples/splat-shader-effects/`) ; https://www.worldlabs.ai/blog/spark-2.0 |
| **three.js r186 `GaussianSplat`** | MIT | PLY, SPZ v4, SPLAT, KSPLAT, glTF KHR_gaussian_splatting | Partial: NodeMaterial/TSL `vertexNode`, forkable but no public hook; **requires WebGPURenderer**. | new, API churn | https://github.com/mrdoob/three.js/releases/tag/r186 |
| GaussianSplats3D (mkkellogg) | MIT | PLY, SPLAT, KSPLAT | No hook; CPU sort | README: no longer active, recommends Spark | https://github.com/mkkellogg/GaussianSplats3D |
| gsplat.js / antimatter15 | MIT | .splat | hackable, minimal | stale | https://radiancefields.com/platforms/three-js |
| PlayCanvas / SuperSplat Viewer | MIT | PLY, SOG, SPZ | shader chunks overridable; not Three.js | active | https://github.com/playcanvas/supersplat |
| Babylon.js 9 | Apache-2.0 | PLY, .splat, SPZ, SOG | no documented hook | active | https://doc.babylonjs.com/features/featuresDeepDive/importers/gaussianSplatting |
| CesiumJS | Apache-2.0 | 3D Tiles + glTF `KHR_gaussian_splatting` + `KHR_gaussian_splatting_compression_spz_2` | No | Apr 2026 | https://github.com/CesiumGS/cesium |

- `3DTILES_content_gaussian_splats` does not exist; Cesium uses glTF KHR extensions. `KHR_gaussian_splatting` is ratified: https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_gaussian_splatting
- Compression: SPZ ~10x smaller, near-lossless; SOG lossy and tiny (splat-transform produces it); keep the PLY master.
- Budget rule of thumb: <= 1.5-2M splats per loaded scene for mid-range phones; SPZ ~20-40 MB per million splats at SH1-2; use Spark `.rad` LOD if the merged building exceeds ~3M splats.

**Warping recipe (Spark):** an `objectModifier` dyno block whose GLSL does sphere inversion `p' = R^2 * p / dot(p,p)` (origin offset to the "planet" center), scales `gsplat.scales` by the local Jacobian (or `covObjectModifiers` for correct anisotropic covariance), lerped by a uniform; `worldModifier` + `context.worldToView` for camera-dependent non-Euclidean projections. Call `updateGenerator()` after changing modifiers. Templates: `splat-shader-effects`, `interactive-deform`, `splat-dissolve-effects`, `splat-reveal-effects`, `portal` examples.

## 7. Mesh <-> splat switching
- Mesh layer: simplest is the **Scaniverse LiDAR mesh** (textured GLB/OBJ), metric, ARKit frame; register splats to it. From splats: **SuGaR** (textured OBJ, ~30 min/scene) https://github.com/Anttwo/SuGaR ; **2DGS** (TSDF, `--unbounded --mesh_res 1024`) https://github.com/hbb1/2d-gaussian-splatting ; 2D-SuGaR https://github.com/Divyam10/2D-SuGaR ; KIRI "Include Mesh" for no-code.
- Cross-fade in Spark: `splatMesh.opacity` vs mesh material opacity inversely over time, or a `SplatEdit`/dyno SDF dissolve so the mesh reveals the splat spatially. Bake registration into the splat with splat-transform so both share one transform.

## 8. Legal / practical at the Academy
- Official commercial filming page: https://www.calacademy.org/location-filming-and-commercial-photo-shoots (permission after review; inquiry form; lighting/electrical/sound equipment pre-approved; no flash in many exhibits).
- Visitor rules: personal photography allowed except posted zones; **tripods and monopods not allowed** (staff statement in Flickr thread; Tripadvisor); selfie sticks/gimbals typically restricted. Current wording [UNVERIFIED]; assume handheld only. https://www.flickr.com/groups/calacademy/discuss/72157607527889934
- 3D scanning: no policy language found. Handheld phone scanning for a personal portfolio reads as personal photography; if published commercially, file the inquiry form. Terms of use: https://www.calacademy.org/terms-of-use

## Processing & delivery pipeline (recommendation)
1. **Quick path (ship this week):** Scaniverse PLYs -> SuperSplat (clean floaters, crop glass noise) -> align each zone to the Scaniverse LiDAR mesh (CloudCompare ICP on centers -> 4x4) -> splat-transform merge with per-input transforms, strip SH to 1-2, export SPZ (and `.rad` LOD via Spark `build-lod` if > 3M splats) -> Three.js + Spark 2.4: `SplatMesh` + GLB mesh, cross-fade via `opacity`, warps via `objectModifier`/`worldModifier` dyno GLSL.
2. **Quality path (later):** retrain from Polycam/SplatKing COLMAP data in Postshot (Windows/NVIDIA; merges scenes; GPS) or Brush (Mac); optionally SuGaR/2DGS mesh; same merge/delivery.

## Tool table
| Tool | URL | Platform | License | Cost | Role |
|---|---|---|---|---|---|
| Scaniverse | https://scaniverse.com | iOS/Android | proprietary | free (Classic) | capture, on-device splat + LiDAR mesh |
| SPZ lib/CLI | https://github.com/nianticlabs/spz | C++/TS/Py | MIT | free | compression/convert |
| Polycam | https://poly.cam | iOS/Android/web | proprietary | Basic $150/yr | capture, raw data + poses |
| SplatKing | https://radiancefields.com/splatking | iOS | proprietary | [unverified] | capture -> COLMAP |
| Record3D | https://record3d.app | iOS | proprietary; lib LGPL | IAP | RGB-D + poses |
| Spectacular Rec / SDK | https://github.com/SpectacularAI/sdk | iOS + CLI | non-commercial free | | video+IMU -> Nerfstudio |
| Postshot | https://www.jawset.com | Windows/NVIDIA | proprietary | free NC / paid | training, merge, GPS |
| Brush | https://github.com/ArthurBrussee/brush | Mac/Win/Linux/Web | Apache-2.0 | free | training (Apple Silicon) |
| OpenSplat | https://github.com/pierotofy/OpenSplat | Mac Metal/CUDA/ROCm/CPU | AGPL-3.0 | free | training, SPZ out |
| gsplat / Nerfstudio | https://github.com/nerfstudio-project/gsplat | CUDA | Apache-2.0 | free | training |
| SuGaR | https://github.com/Anttwo/SuGaR | CUDA | see repo | free | splat -> textured mesh |
| 2DGS | https://github.com/hbb1/2d-gaussian-splatting | CUDA | see repo | free | splat -> mesh |
| SuperSplat | https://github.com/playcanvas/supersplat | browser (WebGPU) | MIT | free | edit, multi-splat, crop, export |
| splat-transform | https://github.com/playcanvas/splat-transform | Node/browser | MIT | free | merge, transform, SOG/SPZ/LOD/GLB |
| CloudCompare | https://www.cloudcompare.org | desktop | GPL | free | ICP registration, georef |
| Spark | https://github.com/sparkjsdev/spark | Three.js (WebGL2) | MIT | free | web render + custom warps + LOD |
| three.js r186 GaussianSplat | https://github.com/mrdoob/three.js | WebGPURenderer | MIT | free | native splats (TSL) |
| descaniverse | https://github.com/jampekka/descaniverse | Python | see repo | free | pull Scaniverse raw data via iOS backup |
| CesiumJS / ion | https://cesium.com | web | Apache-2.0 / SaaS | free/paid | geospatial HLOD splat tiles |

**Unverified, confirm before relying on:** Scaniverse size/duration limits, pause/resume, iPhone 17 Pro listing, exact export list (LAS vs STL), USDZ splat export; Polycam raw export on free tier; Record3D pose fields; SplatKing pricing; Postshot tier pricing; laptop training-time estimates; Academy current tripod wording; SuperSplat measurement tool.
