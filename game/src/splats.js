// Gaussian splats of the real interiors (Scaniverse captures) rendered with Spark, registered to the lidar frame,
// with a sphere-inversion "planet" warp as a dyno object modifier.
//
//   assets/splats/manifest.json lists the scans (see assets/splats/README.md). Each entry has a `frame`:
//     "game"   : the matrix is already in game units (X = long axis, Y up from the main floor, Z = short axis, +Z north)
//     "utm10n" : the matrix takes the scan into UTM 10N metres / NAVD88 (CloudCompare against the lidar); we apply
//                site_meta.json (rotation 137.5 deg about the centre, ground 77.05 m) to land it in the game frame
//     "scan"   : no registration yet; the scan is placed at `guess` (game x,y,z) and can be nudged in the game
//   Keys (main.js): V splats on/off, X planet warp on/off, Shift+X cycles the planet presets.
//   Alignment: window.__fs.splats.nudge(i, {dx,dy,dz,ry,s}) moves scan i; .exportManifest() prints the manifest with the
//   nudged matrices baked in (frame "game"), ready to paste back into assets/splats/manifest.json.
import * as THREE from 'three';
import { SparkRenderer, SplatMesh, dyno } from '@sparkjsdev/spark';
import { L } from './layout.js';

// ---- lidar / site frame -------------------------------------------------------------------------------------
// From site_meta.json: the DSM was rotated by rotation_deg_applied about centre_utm10n; image x right = game +X,
// image y down = game +Z; heights are NAVD88 metres with ground_m at game Y = 0.
export function utmToGame(meta) {
  const th = THREE.MathUtils.degToRad(meta.rotation_deg_applied), c = Math.cos(th), s = Math.sin(th);
  const [E0, N0] = meta.centre_utm10n, g0 = meta.ground_m;
  // X = c*dE - s*dN ; Yup = s*dE + c*dN ; game Z = -Yup ; game Y = z - ground
  // as a Matrix4 acting on (E, N, Z, 1) -> (X, Y, Zgame, 1)
  const m = new THREE.Matrix4();
  m.set(
    c, -s, 0, -(c * E0 - s * N0),
    0, 0, 1, -g0,
    -s, -c, 0, (s * E0 + c * N0),
    0, 0, 0, 1);
  return m;
}

function matrixFromEntry(e) {
  const m = new THREE.Matrix4();
  if (Array.isArray(e.matrix) && e.matrix.length === 16) m.set(...e.matrix);           // row-major, CloudCompare style
  else {
    const p = new THREE.Vector3(...(e.position || e.guess || [0, 0, 0]));
    const q = new THREE.Quaternion(); if (e.quaternion) q.set(...e.quaternion); else if (e.rotationDeg) q.setFromEuler(new THREE.Euler(...e.rotationDeg.map(THREE.MathUtils.degToRad)));
    const s = e.scale == null ? 1 : e.scale;
    m.compose(p, q, new THREE.Vector3(s, s, s));
  }
  return m;
}

// ---- the planet warp: sphere inversion p' = c + R^2 (p - c) / |p - c|^2 -----------------------------------
// Inversion is conformal: locally a similarity with scale R^2/r^2 and a reflection across the plane normal to the
// radial direction. A Gaussian is centrally symmetric, so the reflection is the 180 deg rotation about the radial
// axis (quaternion (n, 0)). `mix` lerps the whole thing on, so the warp can breathe.
// One planet (Bryan, 11/07: 'I love this blob planet. you can get rid of the other ones, just flip this'): inversion centre
// 60 m above the piazza, R = 60, then mirrored about the ground-sphere's centre height so the roof sits on top of the blob
// (unmirrored, the roof hangs underneath, farther from the centre than the facade ring).
const PLANETS = [
  { name: 'BLOB PLANET · above the roof', centre: [0, 60, 3], radius: 60, flip: true },
];

function makePlanetModifier(u) {
  return dyno.dynoBlock({ gsplat: dyno.Gsplat }, { gsplat: dyno.Gsplat }, ({ gsplat }) => {
    const d = new dyno.Dyno({
      inTypes: { gsplat: dyno.Gsplat, centre: 'vec3', radius: 'float', mixAmt: 'float', flipY: 'float', mirrorY: 'float' },
      outTypes: { gsplat: dyno.Gsplat },
      globals: () => [dyno.unindent(/* glsl */ `
        vec4 qmul(vec4 a, vec4 b) { return vec4(a.w*b.xyz + b.w*a.xyz + cross(a.xyz, b.xyz), a.w*b.w - dot(a.xyz, b.xyz)); }
      `)],
      statements: ({ inputs, outputs }) => dyno.unindentLines(/* glsl */ `
        ${outputs.gsplat} = ${inputs.gsplat};
        vec3 c = ${inputs.centre}; float R = ${inputs.radius}; float m = ${inputs.mixAmt};
        if (m > 0.0001) {
          vec3 p = ${inputs.gsplat}.center - c;
          float r2 = max(dot(p, p), 1e-4);
          float k = R * R / r2;                       // local similarity scale
          vec3 n = p * inversesqrt(r2);               // radial unit
          vec3 pInv = c + p * k;
          float kk = mix(1.0, k, m);
          // flip: mirror the inverted world about y = mirrorY (the ground-sphere's centre height) so the planet stays put but turns right side up
          vec3 pFlip = vec3(pInv.x, 2.0 * ${inputs.mirrorY} - pInv.y, pInv.z);
          pInv = mix(pInv, pFlip, ${inputs.flipY});
          ${outputs.gsplat}.center = mix(${inputs.gsplat}.center, pInv, m);
          ${outputs.gsplat}.scales = ${inputs.gsplat}.scales * kk;
          // reflect the ellipsoid across the plane normal to n == rotate 180 deg about n; slerp by m via the axis-angle
          float ang = m * 3.14159265;
          vec4 qn = vec4(n * sin(ang * 0.5), cos(ang * 0.5));
          vec4 q1 = qmul(qn, ${inputs.gsplat}.quaternion);
          // the y-mirror of a centrally symmetric ellipsoid == rotation 180 deg about Y
          float angF = m * ${inputs.flipY} * 3.14159265;
          vec4 qf = vec4(0.0, sin(angF * 0.5), 0.0, cos(angF * 0.5));
          ${outputs.gsplat}.quaternion = qmul(qf, q1);
        }
      `),
    });
    gsplat = d.apply({ gsplat, centre: u.centre, radius: u.radius, mixAmt: u.mix, flipY: u.flip, mirrorY: u.mirrorY }).gsplat;
    return { gsplat };
  });
}

// ---- module ------------------------------------------------------------------------------------------------
export async function buildSplats(renderer, scene, meta, opts = {}) {
  const state = { visible: opts.visible !== false, warp: false, warpMix: 0, planet: 0, entries: [], meshes: [], ready: false, error: null };
  const group = new THREE.Group(); group.name = 'splats'; scene.add(group);
  let spark = null;
  const u = { centre: dyno.dynoVec3(new THREE.Vector3(...PLANETS[0].centre)), radius: dyno.dynoFloat(PLANETS[0].radius), mix: dyno.dynoFloat(0), flip: dyno.dynoFloat(PLANETS[0].flip ? 1 : 0), mirrorY: dyno.dynoFloat(0) };
  const mirrorFor = (p) => p.centre[1] - (p.radius * p.radius) / (2 * Math.max(Math.abs(p.centre[1]), 1e-3));   // ground plane y=0 -> sphere centre height
  u.mirrorY.value = mirrorFor(PLANETS[0]);
  const modifier = makePlanetModifier(u);
  const toGame = utmToGame(meta);

  let manifest = null;
  try { const r = await fetch('./assets/splats/manifest.json'); if (r.ok) manifest = await r.json(); } catch (e) { /* no manifest yet */ }
  const entries = (manifest && manifest.scans) || [];
  state.entries = entries;
  if (!entries.length) { state.ready = true; return api(); }

  spark = new SparkRenderer({ renderer, maxStdDev: 2.6 }); scene.add(spark);
  for (const e of entries) {
    if (e.enabled === false) continue;
    const url = `./assets/splats/${e.file}`;
    const head = await fetch(url, { method: 'HEAD' }).catch(() => null);
    if (!head || !head.ok) { console.warn('splat missing', url); e.missing = true; continue; }
    try {
      const mesh = new SplatMesh({ url, objectModifier: modifier, onLoad: () => { e.loaded = true; console.log('splat', e.space || e.file, 'loaded'); } });
      let m = matrixFromEntry(e);
      if (e.frame === 'utm10n') m = toGame.clone().multiply(m);
      // Scaniverse / ARKit scans are Y up, metres. A `yDown: true` entry (SuperSplat-exported PLY) gets flipped first.
      if (e.yDown) m.multiply(new THREE.Matrix4().makeRotationX(Math.PI));
      mesh.matrixAutoUpdate = false; mesh.matrix.copy(m); mesh.matrix.decompose(mesh.position, mesh.quaternion, mesh.scale); mesh.matrixAutoUpdate = true;
      mesh.name = 'splat:' + (e.space || e.file); e.mesh = mesh; group.add(mesh); state.meshes.push(mesh);
    } catch (err) { console.warn('splat failed', e.file, err); e.error = String(err); }
  }
  group.visible = state.visible; state.ready = true;
  return api();

  function setPlanet(i) {
    state.planet = ((i % PLANETS.length) + PLANETS.length) % PLANETS.length; const p = PLANETS[state.planet];
    u.centre.value.set(...p.centre); u.radius.value = p.radius; u.flip.value = p.flip ? 1 : 0; u.mirrorY.value = mirrorFor(p);
    for (const m of state.meshes) m.updateVersion();
    return p;
  }
  function update(dt) {
    const target = state.warp ? 1 : 0;
    if (Math.abs(state.warpMix - target) > 1e-3) { state.warpMix = THREE.MathUtils.damp(state.warpMix, target, 2.5, dt); u.mix.value = state.warpMix; for (const m of state.meshes) m.updateVersion(); }
    else if (u.mix.value !== target) { state.warpMix = target; u.mix.value = target; for (const m of state.meshes) m.updateVersion(); }
  }
  function nudge(i, { dx = 0, dy = 0, dz = 0, ry = 0, s = 1 } = {}) {
    const e = entries[i]; if (!e || !e.mesh) return null; const m = e.mesh;
    m.position.x += dx; m.position.y += dy; m.position.z += dz; m.rotateY(THREE.MathUtils.degToRad(ry)); m.scale.multiplyScalar(s); m.updateMatrix();
    return m.matrix.toArray();
  }
  function exportManifest() {
    const out = { ...manifest, scans: entries.map((e) => { if (!e.mesh) return e; e.mesh.updateMatrix(); const r = { ...e, frame: 'game', matrix: Array.from(e.mesh.matrix.clone().transpose().elements).map((v) => +v.toFixed(5)) }; delete r.mesh; delete r.guess; delete r.position; delete r.quaternion; delete r.rotationDeg; delete r.scale; delete r.loaded; delete r.missing; delete r.error; return r; }) };
    const txt = JSON.stringify(out, null, 1); console.log(txt); return txt;
  }
  function api() {
    return {
      state, group, PLANETS, planet: () => PLANETS[state.planet], setPlanet, update, nudge, exportManifest, utmToGame: toGame, uniforms: u,
      touch: () => { for (const m of state.meshes) m.updateVersion(); },
      setFlip: (on) => { u.flip.value = on ? 1 : 0; PLANETS[state.planet].flip = !!on; for (const m of state.meshes) m.updateVersion(); },
      toggle: () => { state.visible = !state.visible; group.visible = state.visible; return state.visible; },
      toggleWarp: () => { state.warp = !state.warp; return state.warp; },
      count: () => state.meshes.length,
    };
  }
}
