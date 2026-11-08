# Water rendering: can we use Noniv/web-ocean?

Source: https://github.com/Noniv/web-ocean (MIT, 2026, Maksymilian Dendura). Live demo: https://ocean-noniv.vercel.app

## What it is
A from-scratch **WebGPU** ocean: Tessendorf FFT with six 256x256 cascades (1103 m down to 0.26 m), JONSWAP spectrum with
Donelan-Banner spreading plus swell, choppy displacement, CDLOD quadtree mesh (17 levels, 6.25 cm near the camera, 160 km reach),
LEAN-mapped anisotropic roughness, analytic sun glitter, per-frame environment cube map, Jacobian-driven whitecaps with aging
foam maps, Hillaire atmosphere with two cloud layers, HDR + MSAA + bloom + AgX. Single 61 KB HTML. Needs Chrome with WebGPU and a
discrete GPU. Open ocean only: no shoreline, no objects in the water, no underwater view.

## Fit for Freeswim Fridays
| Need | Fit | Why |
|---|---|---|
| Surface seen from the roof / piazza, looking down into the flooded building | Partial | Their shading is excellent, but the mesh is a world-scale quadtree with no boundaries or intersecting geometry; we need a 169 x 110 m pool with walls, columns and domes piercing it |
| Underwater view (where most of our game happens) | No | They render no underwater volume, caustics, fog or surface-from-below |
| Rising flood animation | No | Their surface has no level parameter; ours does |
| "Planet" exterior / sky | Yes | The sky and sun glitter would be a strong backdrop for the sphere-wrapped exterior and the roof-deck shore |
| Dome output | Caution | WebGPU only; the Morrison pipeline PC will have an RTX, fine, but it forces our whole renderer to WebGPU or a second canvas |
| Licence | Yes | MIT |

## Recommendation
Do not swap engines. Our game is Three.js WebGL2 (works on the laptop, phones and the dome PC). Borrow three things:
1. **Spectrum and displacement**: port the JONSWAP + choppy displacement to a small GPGPU pass (Three.js `GPUComputationRenderer`
   or a 256x256 render-target FFT) feeding our surface mesh. Even two cascades (64 m, 4 m) make the pool read as water.
2. **Shading**: LEAN slope moments for roughness, the anisotropic glitter term, Fresnel with a tilted reflection direction at
   grazing angles. Their `js/wgsl/ocean.js` is directly translatable to GLSL.
3. **Foam logic**: Jacobian-fold whitecaps along the walls and columns where the surface is disturbed, decaying over time.
Keep our own: bounded surface, underwater fog layers, caustics, surface-from-below, flood level. If we later move to Three.js
`WebGPURenderer` (r186 has native Gaussian splats on it too), their compute shaders can run almost as-is in TSL/WGSL.

## Credit
If any shader math is reused: "Ocean spectrum and shading adapted from web-ocean by Maksymilian Dendura (MIT)".
