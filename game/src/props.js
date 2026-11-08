// Exhibit props: glTF files dropped into assets/props/ appear at their exhibit positions.
// Sources: Sketchfab (Academy Viz Studio photogrammetry of the Philippine Coral Reef tank; visitor scans of the
// T. rex, megalodon jaws, whale skull, redwood slice ...). Download on the laptop with your Sketchfab account where the
// license allows; see research/cal-academy/12-sketchfab-exhibit-models.md. Files are git-ignored.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { L } from './layout.js';

export const PROPS = [
  // The Academy's blue whale (about 26 m) hangs over Giants of Land and Sea, south-west of the piazza under the roof slab.
  { file: 'blue_whale_skeleton_nhm.glb', name: 'Blue whale skeleton (stand-in: NHM London scan)', pos: [L.whale.x, L.whale.y, L.whale.z], fit: [26, 4, 8], hang: true, replaces: 'whale-procedural' },
  { file: 'orca_skeleton.glb', name: 'Orca O319 skeleton (placeholder)', pos: [55, 6, -5], fit: [7, 1.6, 2.2], hang: true },
  { file: 'philippine_reef_photogrammetry.glb', name: 'Philippine Coral Reef (Viz Studio photogrammetry)', pos: [L.reefTank.x, L.reefTank.bottom, L.reefTank.z], fit: [L.reefTank.w - 1, 7, L.reefTank.d - 1], replaces: 'procedural-coral' },
  { file: 'reef_buddha_wall.glb', name: 'Philippine Reef buddha wall', pos: [L.reefTank.x, L.reefTank.bottom, L.reefTank.z - L.reefTank.d / 2 + 1], fit: [L.reefTank.w - 1, 6, 2] },
  { file: 'trex_full_scale.glb', name: 'Tyrannosaurus rex, entrance hall', pos: [0, 0, 44], fit: [4, 6, 12] },
  { file: 'megalodon_jaws.glb', name: 'Megalodon jaws', pos: [-40, 0, 44], fit: [3, 3, 1.5] },
  { file: 'hubbs_beaked_whale_skull.glb', name: "Hubbs' beaked whale skull", pos: [-30, 0.9, 40], fit: [2.4, 1, 1] },
  { file: 'redwood_cross_section.glb', name: 'Redwood cross-section, Giants of Land and Sea', pos: [40, 0, 38], fit: [4, 4, 0.6] },
  { file: 'seal_sea_lion_skeletons.glb', name: 'Seal and sea lion skeletons', pos: [-60, 2.5, 20], fit: [3, 1.5, 2] },
  { file: 'sea_turtle.glb', name: 'Sea turtle', pos: [-20, 1.5, -20], fit: [1.5, 0.6, 1.8] },
  { file: 'alligator_skull.glb', name: 'Alligator skull, the Swamp rail', pos: [L.swamp.x + L.swamp.r + 1, 1.0, L.swamp.z + 3], fit: [0.7, 0.3, 0.4] },
  { file: 'walrus_skull.glb', name: 'Walrus skull', pos: [70, 1.0, 0], fit: [0.7, 0.5, 0.5] },
  { file: 'grizzly_skull.glb', name: 'Grizzly bear skull, African Hall side gallery', pos: [70, 1.0, 6], fit: [0.5, 0.3, 0.4] },
  { file: 'humongous_tropical_fish.glb', name: 'Large fish mount, aquarium level', pos: [-20, -5.5, 30], fit: [2.5, 1.2, 0.6] },
  { file: 'reptile_fossil.glb', name: 'Reptile fossil slab', pos: [50, 1.0, 30], fit: [1.6, 0.2, 1.2] },
  { file: 'coral_visitor_scan.glb', name: 'Coral (visitor scan)', pos: [L.lagoon.x + 4, L.lagoon.bottom, L.lagoon.z], fit: [1.2, 0.8, 1.2] },
  { file: 'acropora_palmata_01.glb', name: 'Elkhorn coral (Viz Studio)', pos: [L.reefTank.x + 4, L.reefTank.bottom, L.reefTank.z + 2], fit: [2.5, 1.6, 2.5] },
  { file: 'echinophyllia_sp.glb', name: 'Echinophyllia (Viz Studio)', pos: [L.reefTank.x - 4, L.reefTank.bottom, L.reefTank.z - 2], fit: [1.2, 0.5, 1.2] },
];

// Photogrammetry textures arrive at 4-8k; on an iGPU that is the lag. Downscale every map to MAX_TEX on load.
const MAX_TEX = 2048;
function shrinkTextures(root) {
  const seen = new Set();
  root.traverse((o) => {
    if (!o.material) return; const ms = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of ms) for (const k of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap']) {
      const tex = m[k]; if (!tex || seen.has(tex) || !tex.image || !tex.image.width) continue; seen.add(tex);
      const w = tex.image.width, h = tex.image.height; const s = MAX_TEX / Math.max(w, h); if (s >= 1) continue;
      const c = document.createElement('canvas'); c.width = Math.round(w * s); c.height = Math.round(h * s);
      c.getContext('2d').drawImage(tex.image, 0, 0, c.width, c.height); tex.image = c; tex.needsUpdate = true;
    }
  });
}

export async function loadProps(scene, onLoaded) {
  const loader = new GLTFLoader(); const loaded = [];
  for (const p of PROPS) {
    const base = p.file.replace(/\.glb$/, '');
    let url = `./assets/props/${p.file}`; let head = await fetch(url, { method: 'HEAD' }).catch(() => null);
    if (!head || !head.ok) { url = `./assets/props/${base}/scene.gltf`; head = await fetch(url, { method: 'HEAD' }).catch(() => null); }
    if (!head || !head.ok) continue;
    try {
      const gltf = await loader.loadAsync(url); const root = gltf.scene; shrinkTextures(root);
      const box = new THREE.Box3().setFromObject(root); const size = box.getSize(new THREE.Vector3()); const c = box.getCenter(new THREE.Vector3());
      const s = Math.min(p.fit[0] / size.x, p.fit[1] / size.y, p.fit[2] / size.z);
      root.scale.setScalar(s); root.position.set(p.pos[0] - c.x * s, p.hang ? p.pos[1] - c.y * s : p.pos[1] - box.min.y * s, p.pos[2] - c.z * s);
      if (p.hang) { const sz2 = size.clone().multiplyScalar(s); if (sz2.x < sz2.z) root.rotation.y = Math.PI / 2; }
      if (p.replaces) { const old = scene.getObjectByName(p.replaces); if (old) old.visible = false; }
      root.name = 'prop:' + p.file; scene.add(root); p.root = root; p.box = new THREE.Box3().setFromObject(root); loaded.push(p); if (onLoaded) onLoaded(p, root);
    } catch (e) { console.warn('prop failed', p.file, e); }
  }
  return loaded;
}

// Fly-through: a slow camera path that enters a prop's bounding box, passes through it (eye sockets, jaws, the
// hollow of a skull) and exits, then orbits once. Press K to start on the nearest loaded prop, K again to stop.
export function makeFlythrough(camera) {
  let active = null;
  const cp = new THREE.Vector3(), lt = new THREE.Vector3();
  function start(p) {
    if (!p || !p.box) return false;
    const c = p.box.getCenter(new THREE.Vector3()), sz = p.box.getSize(new THREE.Vector3()); const r = Math.max(sz.x, sz.z) * 0.9 + 0.6;
    const pts = [
      c.clone().add(new THREE.Vector3(-r * 1.6, sz.y * 0.4, r * 0.6)),      // approach
      c.clone().add(new THREE.Vector3(-sz.x * 0.35, sz.y * 0.55, sz.z * 0.1)), // enter
      c.clone().add(new THREE.Vector3(0, sz.y * 0.5, 0)),                     // inside
      c.clone().add(new THREE.Vector3(sz.x * 0.35, sz.y * 0.45, -sz.z * 0.1)), // exit
      c.clone().add(new THREE.Vector3(r * 1.3, sz.y * 0.8, -r * 0.8)),      // pull out
      c.clone().add(new THREE.Vector3(0, sz.y * 1.2, r * 1.5)),             // orbit
      c.clone().add(new THREE.Vector3(-r * 1.4, sz.y * 0.6, r * 0.2)),
    ];
    active = { curve: new THREE.CatmullRomCurve3(pts, true, 'centripetal', 0.5), c, t: 0, dur: 28, start: camera.position.clone() };
    return true;
  }
  function update(dt) {
    if (!active) return false;
    active.t += dt / active.dur; if (active.t >= 1) { active = null; return false; }
    active.curve.getPointAt(active.t, cp); camera.position.lerp(cp, 1 - Math.exp(-dt * 3));
    active.curve.getPointAt((active.t + 0.03) % 1, lt); lt.lerp(active.c, 0.6); camera.lookAt(lt);
    return true;
  }
  return { start, update, stop: () => { active = null; }, get active() { return !!active; } };
}
