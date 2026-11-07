// Boids in instanced meshes. Species from assets/species.json. Constrained to the flooded volume.
import * as THREE from 'three';
import { L, insideFootprint, dryZone, sealedPush } from './layout.js';

const HOMES = {
  reef: () => new THREE.Vector3(L.reefTank.x, -3, L.reefTank.z),
  calcoast: () => new THREE.Vector3(L.calCoast.x, -4, L.calCoast.z),
  amazon: () => new THREE.Vector3(L.amazon.x, -4.5, L.amazon.z),
  lagoon: () => new THREE.Vector3(L.lagoon.x, -0.8, L.lagoon.z),
  piazza: () => new THREE.Vector3(L.piazza.x, 3, L.piazza.z),
  hall: () => new THREE.Vector3((L.africanHall.x0 + L.africanHall.x1) / 2, 3, (L.africanHall.z0 + L.africanHall.z1) / 2 + 10),
  deep: () => new THREE.Vector3(-20, -6.5, 20),
};
const LAYER_Y = { sunlit: [-2, 8.5], mid: [-6.5, 8.5], floor: [-7.2, -0.3], twilight: [-7.4, -5.5], any: [-7.2, 8.5] };

function fishGeometry(kind, size, shape) {
  shape = shape || (kind === 'ray' ? 'flat-ray' : kind === 'shark' ? 'shark' : 'fusiform');
  if (shape === 'flat-ray') { const g = new THREE.CircleGeometry(size, 14); g.rotateX(-Math.PI / 2); g.scale(1, 1, 1.3); const t = new THREE.CylinderGeometry(0.02 * size, 0.01 * size, size * 1.2, 5); t.rotateX(Math.PI / 2); t.translate(0, 0, -size * 1.1); return mergeGeos([g, t]); }
  if (shape === 'eel') { const g = new THREE.CylinderGeometry(size * 0.06, size * 0.03, size, 6); g.rotateX(Math.PI / 2); return g; }
  if (shape === 'compressed-oval') { const g = new THREE.SphereGeometry(size * 0.5, 10, 8); g.scale(0.22, 1.0, 1.0); const tail = new THREE.ConeGeometry(size * 0.25, size * 0.3, 4); tail.rotateX(-Math.PI / 2); tail.scale(0.3, 1, 1); tail.translate(0, 0, -size * 0.55); return mergeGeos([g, tail]); }
  if (shape === 'elongate') { const g = new THREE.CylinderGeometry(size * 0.09, size * 0.04, size, 7); g.rotateX(Math.PI / 2); const tail = new THREE.ConeGeometry(size * 0.12, size * 0.25, 4); tail.rotateX(-Math.PI / 2); tail.translate(0, 0, -size * 0.58); return mergeGeos([g, tail]); }
  const g = new THREE.ConeGeometry(size * 0.22, size, 7); g.rotateX(Math.PI / 2); // nose +Z, fusiform
  if (shape === 'shark') { g.scale(1.2, 0.9, 1); const fin = new THREE.ConeGeometry(size * 0.12, size * 0.3, 3); fin.translate(0, size * 0.3, size * 0.05); const tail = new THREE.ConeGeometry(size * 0.2, size * 0.45, 4); tail.rotateX(-Math.PI / 2); tail.scale(0.3, 1.6, 1); tail.translate(0, 0, -size * 0.65); return mergeGeos([g, fin, tail]); }
  const tail = new THREE.ConeGeometry(size * 0.18, size * 0.35, 4); tail.rotateX(-Math.PI / 2); tail.scale(0.3, 1, 1); tail.translate(0, 0, -size * 0.6);
  return mergeGeos([g, tail]);
}
function mergeGeos(gs) {
  // minimal merge (positions+normals only), enough for MeshStandardMaterial
  const ngs = gs.map(g => g.index ? g.toNonIndexed() : g);
  let n = 0; for (const g of ngs) n += g.attributes.position.count;
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3); let o = 0;
  for (const ng of ngs) { const p = ng.attributes.position.array, nn = ng.attributes.normal.array; pos.set(p, o * 3); nor.set(nn, o * 3); o += ng.attributes.position.count; }
  const out = new THREE.BufferGeometry(); out.setAttribute('position', new THREE.BufferAttribute(pos.subarray(0, o * 3), 3)); out.setAttribute('normal', new THREE.BufferAttribute(nor.subarray(0, o * 3), 3)); return out;
}

export async function buildFish(scene) {
  const data = await (await fetch('./assets/species.json')).json();
  const groups = [];
  for (const sp of data.species) {
    const geo = fishGeometry(sp.kind, sp.size, sp.shape);
    const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(sp.color), roughness: 0.6, metalness: 0.15, emissive: new THREE.Color(sp.color), emissiveIntensity: sp.glow ? 0.9 : 0.22, flatShading: true });
    const mesh = new THREE.InstancedMesh(geo, mat, sp.count); mesh.frustumCulled = false; mesh.visible = false; scene.add(mesh);
    const home = HOMES[sp.home](); const [ymin, ymax] = LAYER_Y[sp.layer];
    const pos = [], vel = [];
    for (let i = 0; i < sp.count; i++) {
      pos.push(new THREE.Vector3(home.x + (Math.random() - 0.5) * 10, THREE.MathUtils.clamp(home.y + (Math.random() - 0.5) * 3, ymin, ymax), home.z + (Math.random() - 0.5) * 8));
      vel.push(new THREE.Vector3((Math.random() - 0.5), (Math.random() - 0.5) * 0.3, (Math.random() - 0.5)).normalize().multiplyScalar(sp.speed * 0.6));
    }
    let bounds = null;
    if (sp.home === 'calcoast') bounds = { x0: L.calCoast.x - L.calCoast.w / 2 + 0.5, x1: L.calCoast.x + L.calCoast.w / 2 - 0.5, z0: L.calCoast.z - L.calCoast.d / 2 + 0.5, z1: L.calCoast.z + L.calCoast.d / 2 - 0.5, y0: L.calCoast.bottom + 0.4, y1: L.calCoast.top - 0.3 };
    if (sp.home === 'amazon') bounds = { cx: L.amazon.x, cz: L.amazon.z, r: L.amazon.r - 0.6, y0: L.amazon.bottom + 0.4, y1: L.amazon.top - 0.3 };
    groups.push({ sp, mesh, pos, vel, home, ymin, ymax, phase: Math.random() * 10, bounds });
  }
  const dummy = new THREE.Object3D(); const tmp = new THREE.Vector3(), tmp2 = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);

  function update(dt, waterY, player, t) {
    const released = waterY > -1.0; // tanks' glass "retracts" once the main floor is under water
    for (const g of groups) {
      const { sp, pos, vel, home, ymin, ymax, bounds } = g;
      g.mesh.visible = bounds ? true : waterY > L.levels.aquarium + 0.5;
      const ceil = Math.min(ymax, waterY - 0.4);
      const radius = sp.kind === 'fish' ? 2.2 : 5; const nMax = 10;
      for (let i = 0; i < pos.length; i++) {
        const p = pos[i], v = vel[i];
        // neighbours (same species, sampled)
        let cx = 0, cy = 0, cz = 0, ax = 0, ay = 0, az = 0, sx = 0, sy = 0, sz = 0, cnt = 0;
        for (let k = 0; k < nMax; k++) {
          const j = (i + 1 + k * 7) % pos.length; if (j === i) continue; const q = pos[j]; const d = p.distanceTo(q);
          if (d < radius && d > 1e-4) { cnt++; cx += q.x; cy += q.y; cz += q.z; ax += vel[j].x; ay += vel[j].y; az += vel[j].z; const w = (radius * 0.35 - d); if (w > 0) { sx += (p.x - q.x) / d * w; sy += (p.y - q.y) / d * w; sz += (p.z - q.z) / d * w; } }
        }
        if (cnt) { tmp.set(cx / cnt - p.x, cy / cnt - p.y, cz / cnt - p.z).multiplyScalar(0.6); v.addScaledVector(tmp, dt); tmp.set(ax / cnt, ay / cnt, az / cnt).sub(v).multiplyScalar(0.8); v.addScaledVector(tmp, dt); tmp.set(sx, sy, sz).multiplyScalar(2.5); v.addScaledVector(tmp, dt); }
        // home attraction (weak when released, strong when confined)
        const confined = !released || sp.home === 'deep' && waterY < -2;
        tmp.copy(home).sub(p); const dh = tmp.length(); tmp.normalize().multiplyScalar(confined ? 1.2 : (dh > 55 ? 0.5 : 0.08)); v.addScaledVector(tmp, dt);
        // wander
        tmp.set(Math.sin(t * 0.9 + i * 1.7 + g.phase), Math.sin(t * 0.5 + i * 0.3) * 0.3, Math.cos(t * 0.7 + i * 2.1)).multiplyScalar(0.5); v.addScaledVector(tmp, dt);
        // player avoidance (sharks are curious: circle at 6 m)
        tmp.copy(p).sub(player); const dp = tmp.length();
        if (sp.kind === 'shark') { if (dp < 9) { tmp2.set(-tmp.z, 0, tmp.x).normalize().multiplyScalar(1.5); v.addScaledVector(tmp2, dt); if (dp < 4) v.addScaledVector(tmp.normalize(), dt * 2); } }
        else if (dp < 3.5) v.addScaledVector(tmp.normalize().multiplyScalar(3.5 * (3.5 - dp)), dt);
        if (bounds) { // sealed tank: stay inside its own water
          if (bounds.r !== undefined) { const dx = p.x - bounds.cx, dz = p.z - bounds.cz, rr = Math.hypot(dx, dz); if (rr > bounds.r) { v.x -= dx / rr * dt * 5; v.z -= dz / rr * dt * 5; } }
          else { if (p.x < bounds.x0) v.x += dt * 5; if (p.x > bounds.x1) v.x -= dt * 5; if (p.z < bounds.z0) v.z += dt * 5; if (p.z > bounds.z1) v.z -= dt * 5; }
          if (p.y < bounds.y0) v.y += dt * 5; if (p.y > bounds.y1) v.y -= dt * 5;
          const sMax = sp.speed, sMin = sp.speed * 0.3; const sl = v.length(); if (sl > sMax) v.multiplyScalar(sMax / sl); else if (sl < sMin) v.multiplyScalar(sMin / Math.max(sl, 1e-4));
          p.addScaledVector(v, dt); p.y = THREE.MathUtils.clamp(p.y, bounds.y0 - 0.2, bounds.y1 + 0.2);
          dummy.position.copy(p); tmp.copy(p).add(v); dummy.lookAt(tmp); dummy.rotateY(Math.sin(t * 6 + i) * 0.1); dummy.updateMatrix(); g.mesh.setMatrixAt(i, dummy.matrix); continue;
        }
        // bounds: inside footprint, below water, above floor, out of dry/sealed rooms
        const pad = 1.5; if (p.x < L.bbox.x0 + pad) v.x += dt * 4; if (p.x > L.bbox.x1 - pad) v.x -= dt * 4; if (p.z < L.bbox.z0 + pad) v.z += dt * 4; if (p.z > L.bbox.z1 - pad) v.z -= dt * 4;
        if (p.y > ceil) v.y -= dt * 4 * (p.y - ceil + 0.5); if (p.y < ymin) v.y += dt * 4 * (ymin - p.y + 0.5);
        // roof slab: fish cannot be above it except through the skylight opening
        if (p.y > L.levels.roofSlab - 0.6 && !(Math.abs(p.x - L.skylight.x) < L.skylight.w / 2 && Math.abs(p.z - L.skylight.z) < L.skylight.d / 2)) v.y -= dt * 6;
        if (dryZone(p.x, p.y, p.z)) { tmp.copy(p).sub(L.rainforest); tmp.y = 0; v.addScaledVector(tmp.normalize(), dt * 6); }
        const push = sealedPush(p.x, p.y, p.z); if (push) { if (push.x) v.x += push.x * dt * 6; if (push.y) v.y += push.y * dt * 6; if (push.z) v.z += push.z * dt * 6; }
        if (!confined && sp.home !== 'deep' && p.y < -6.8 && sp.layer !== 'twilight') v.y += dt * 2;
        // speed clamp
        const sMax = sp.speed, sMin = sp.speed * 0.35; const s = v.length(); if (s > sMax) v.multiplyScalar(sMax / s); else if (s < sMin) v.multiplyScalar(sMin / Math.max(s, 1e-4));
        p.addScaledVector(v, dt);
        // instance transform: face velocity, roll for rays
        dummy.position.copy(p); tmp.copy(p).add(v); dummy.lookAt(tmp);
        if (sp.kind === 'ray') dummy.rotateZ(Math.sin(t * 2 + i) * 0.2); else dummy.rotateY(Math.sin(t * 8 + i) * 0.12);
        dummy.updateMatrix(); g.mesh.setMatrixAt(i, dummy.matrix);
      }
      g.mesh.instanceMatrix.needsUpdate = true;
    }
  }
  function nearby(player, r = 12) { const out = {}; for (const g of groups) { let c = 0; for (const p of g.pos) if (p.distanceTo(player) < r) c++; if (c) out[g.sp.name] = c; } return out; }
  return { groups, update, nearby };
}
