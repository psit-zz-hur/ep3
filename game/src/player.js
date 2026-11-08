// First-person swimmer / walker. Pointer-lock look, WASD, Space up, Shift down. Buoyancy in water, gravity in air.
import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { L, insideFootprint, dryZone, sealedPush } from './layout.js';

export function buildPlayer(camera, dom, site) {
  const controls = new PointerLockControls(camera, dom);
  const keys = {}; window.addEventListener('keydown', (e) => keys[e.code] = true); window.addEventListener('keyup', (e) => keys[e.code] = false);
  const vel = new THREE.Vector3(); const pos = camera.position; const fwd = new THREE.Vector3(), right = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
  const state = { mode: 'air', zone: null, grounded: false, airlock: { t: 0, phase: 'idle' }, skate: false };
  pos.set(29, L.levels.crown + 1.7, 4 + 14); camera.lookAt(0, 12, 3);

  function floorAt(x, y, z) {
    // highest walkable surface at or below y
    const candidates = [];
    if (!insideFootprint(x, z)) candidates.push(site.sample(x, z));
    else {
      if (site.isBuilding(x, z) && y > L.levels.roofSlab - 1) candidates.push(site.sample(x, z)); // on the living roof
      candidates.push(L.levels.main, L.levels.aquarium);
      const mz = L.piazza; if (Math.abs(x - mz.x) < mz.w / 2 + 6 && Math.abs(z - mz.z) < mz.d / 2 + 6 && !(Math.abs(x - mz.x) < mz.w / 2 + 2 && Math.abs(z - mz.z) < mz.d / 2 + 2)) candidates.push(L.levels.mezz + 0.15);
      const rt = L.reefTank; if (Math.abs(x - rt.x) < rt.w / 2 && Math.abs(z - rt.z) < rt.d / 2) { const i = candidates.indexOf(L.levels.main); if (i >= 0) candidates.splice(i, 1); }
      const lg = L.lagoon; if (Math.abs(x - lg.x) < lg.w / 2 && Math.abs(z - lg.z) < lg.d / 2) { const i = candidates.indexOf(L.levels.main); if (i >= 0) candidates.splice(i, 1); candidates.push(lg.bottom); }
      if ((x - L.rainforest.x) ** 2 + (z - L.rainforest.z) ** 2 < L.domeR ** 2) candidates.push(L.amazon.top + 0.2);
    }
    let best = -1e9; for (const c of candidates) if (c <= y + 0.6 && c > best) best = c; return best;
  }

  function update(dt, water) {
    const eye = 1.6; const x = pos.x, y = pos.y, z = pos.z;
    const zone = dryZone(x, y - eye + 0.5, z); state.zone = zone;
    const wet = !zone && water.isWet(x, y - 0.3, z); state.mode = wet ? 'water' : 'air';
    camera.getWorldDirection(fwd); right.crossVectors(fwd, up).normalize();
    const move = new THREE.Vector3();
    if (keys.KeyW) move.add(fwd); if (keys.KeyS) move.sub(fwd); if (keys.KeyD) move.add(right); if (keys.KeyA) move.sub(right);
    if (wet) {
      if (move.lengthSq() > 0) move.normalize();
      if (keys.Space) move.y += 0.8; if (keys.ShiftLeft || keys.ShiftRight) move.y -= 0.8;
      const sp = keys.KeyE ? 6 : 3.2; vel.lerp(move.multiplyScalar(sp), 1 - Math.exp(-dt * 3));
      vel.y += Math.sin(performance.now() * 0.001) * 0.02; // gentle swell
    } else {
      move.y = 0; if (move.lengthSq() > 0) move.normalize();
      const skate = state.skate; const sp = skate ? (keys.KeyE ? 11 : 7.5) : (keys.KeyE ? 6 : 3.0); const resp = skate ? 1.2 : 8; vel.x = THREE.MathUtils.lerp(vel.x, move.x * sp, 1 - Math.exp(-dt * resp)); vel.z = THREE.MathUtils.lerp(vel.z, move.z * sp, 1 - Math.exp(-dt * resp));
      vel.y -= 9.8 * dt; if (keys.Space && state.grounded) vel.y = 4.5;
    }
    pos.addScaledVector(vel, dt);
    // floors
    const f = floorAt(pos.x, pos.y - eye, pos.z); if (f > -1e8 && pos.y - eye < f) { pos.y = f + eye; if (vel.y < 0) vel.y = 0; state.grounded = true; } else state.grounded = Math.abs(pos.y - eye - f) < 0.05;
    // roof slab: can't pass through except via skylight opening or hatches
    const underRoof = insideFootprint(pos.x, pos.z) && pos.y - eye < L.levels.roofSlab && pos.y > L.levels.roofSlab - 0.2;
    const inSky = Math.abs(pos.x - L.skylight.x) < L.skylight.w / 2 && Math.abs(pos.z - L.skylight.z) < L.skylight.d / 2;
    const inHatch = L.hatches.some(h => h.into !== 'piazza' && (pos.x - h.x) ** 2 + (pos.z - h.z) ** 2 < h.r ** 2);
    if (insideFootprint(pos.x, pos.z) && !inSky && !inHatch) {
      const roofTop = site.sample(pos.x, pos.z);
      if (pos.y - eye > L.levels.roofSlab - 0.3 && pos.y - eye < roofTop + 0.3 && !(zone === 'rainforest')) {
        // inside the soil/structure band: push to whichever side is closer
        if (pos.y - eye - (L.levels.roofSlab - 0.3) < roofTop + 0.3 - (pos.y - eye)) { pos.y = L.levels.roofSlab - 0.3 + eye; if (vel.y > 0) vel.y = 0; } else { pos.y = roofTop + 0.3 + eye; if (vel.y < 0) vel.y = 0; }
      }
    }
    // hatches: the rainforest hatch drops you through the dome crown into the dry dome; planetarium porthole drops into the flooded sphere
    // dome shells are solid except at hatch columns and the dome entry portal / airlock
    for (const d of [L.planetarium, L.rainforest]) {
      const dx = pos.x - d.x, dy = pos.y - eye + 0.8 - d.y, dz = pos.z - d.z; const r = Math.sqrt(dx * dx + dy * dy + dz * dz);
      const hatchCol = dx * dx + dz * dz < 2.4 ** 2 && dy > 8; const doorCol = Math.abs(dz) < 1.4 && dy < 1.5 && dy > -2 && ((d === L.rainforest && dx > 0) || (d === L.planetarium && dx < 0));
      if (!hatchCol && !doorCol && Math.abs(r - L.domeR) < 0.9) { const n = new THREE.Vector3(dx, dy, dz).normalize(); const target = r < L.domeR ? L.domeR - 0.95 : L.domeR + 0.95; pos.x = d.x + n.x * target; pos.y = d.y + n.y * target + eye - 0.8; pos.z = d.z + n.z * target; vel.multiplyScalar(0.2); }
    }
    // exterior lift tower: hold E inside the tower to ride up/down; exterior stair is a ramp
    const lt = L.liftTower; if ((pos.x - lt.x) ** 2 + (pos.z - lt.z) ** 2 < lt.r ** 2) {
      state.inLift = true; if (keys.KeyE) { pos.y += dt * 2.2; if (pos.y - eye > lt.y1) pos.y = lt.y1 + eye; vel.y = 0; } else if (keys.KeyQ) { pos.y -= dt * 2.2; if (pos.y - eye < lt.y0) pos.y = lt.y0 + eye; vel.y = 0; } else if (!state.grounded) { vel.y = 0; }
    } else state.inLift = false;
    const ws = L.westStair; if (Math.abs(pos.x - ws.x) < ws.w / 2 + 0.5 && Math.abs(pos.z - ws.z) < ws.d / 2 + 2) { const t = THREE.MathUtils.clamp((pos.z - (ws.z - ws.d / 2)) / ws.d, 0, 1); const sy = ws.y0 + t * (ws.y1 - ws.y0); if (pos.y - eye < sy) { pos.y = sy + eye; vel.y = 0; state.grounded = true; } }
    // sealed rooms + lowest floor
    const push = sealedPush(pos.x, pos.y - eye, pos.z); if (push) { if (push.x) pos.x += push.x; if (push.y) pos.y += push.y; if (push.z) pos.z += push.z; }
    // airlock cycle: entering wet -> chamber drains over 3 s
    if (zone === 'airlock') { state.airlock.t += dt; if (state.airlock.t > 3) state.airlock.phase = 'dry'; else state.airlock.phase = 'draining'; } else { state.airlock.t = 0; state.airlock.phase = 'idle'; }
    // world bounds
    pos.x = THREE.MathUtils.clamp(pos.x, -290, 290); pos.z = THREE.MathUtils.clamp(pos.z, -215, 215); pos.y = Math.min(pos.y, 120);
    return state;
  }
  return { controls, update, state, position: pos };
}
