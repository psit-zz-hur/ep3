// Parametric interior: floors, column grid, piazza, domes, tanks, halls, dry rooms, airlock.
import * as THREE from 'three';
import { L } from './layout.js';

const M = {
  concrete: new THREE.MeshStandardMaterial({ color: 0x9a9b94, roughness: 0.9 }),
  floor: new THREE.MeshStandardMaterial({ color: 0x8c8f88, roughness: 0.95 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x3a3d3f, roughness: 0.9 }),
  steel: new THREE.MeshStandardMaterial({ color: 0xc9ccd0, roughness: 0.4, metalness: 0.7 }),
  glass: new THREE.MeshPhysicalMaterial({ color: 0xbfe6ff, roughness: 0.05, metalness: 0, transmission: 0, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false }),
  domeShell: new THREE.MeshStandardMaterial({ color: 0xdcdcd8, roughness: 0.8, side: THREE.DoubleSide }),
  domeScreen: new THREE.MeshBasicMaterial({ color: 0x0b1b33, side: THREE.BackSide }),
  coral: new THREE.MeshStandardMaterial({ color: 0xd9825a, roughness: 0.8, flatShading: true }),
  coral2: new THREE.MeshStandardMaterial({ color: 0xb04fa0, roughness: 0.8, flatShading: true }),
  coral3: new THREE.MeshStandardMaterial({ color: 0xe8d36a, roughness: 0.8, flatShading: true }),
  foliage: new THREE.MeshStandardMaterial({ color: 0x3f8a3c, roughness: 0.9, flatShading: true }),
  warm: new THREE.MeshStandardMaterial({ color: 0xc9a46a, roughness: 0.8 }),
  sealed: new THREE.MeshStandardMaterial({ color: 0x4a4e52, roughness: 0.9 }),
  marker: new THREE.MeshBasicMaterial({ color: 0xffd34d }),
  markerWet: new THREE.MeshBasicMaterial({ color: 0x55e0ff }),
};

function box(w, h, d, mat, x, y, z, group) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.position.set(x, y, z); group.add(m); return m; }

export function buildInterior(scene) {
  const g = new THREE.Group(); g.name = 'building'; scene.add(g);
  const B = L.bbox, W = B.x1 - B.x0, D = B.z1 - B.z0, cx = (B.x0 + B.x1) / 2, cz = (B.z0 + B.z1) / 2;
  const Lv = L.levels;

  // Floors (slabs) with openings via multiple boxes: aquarium level, main floor with piazza/tank/dome openings, roof slab with skylight opening.
  box(W, 0.4, D, M.dark, cx, Lv.aquarium - 0.2, cz, g);                 // aquarium level floor
  // main floor slab, leaving the two domes' cores and tanks open is approximated by boxes around them
  const mainY = -0.2;
  // split the main floor into strips that avoid dome circles & reef tanks: we just place slab and cut visually with tank boxes (gameplay uses layout).
  box(W, 0.4, D, M.floor, cx, mainY, cz, g);
  // openings in the main floor: piazza (to lower level stairs) is NOT open in reality; reef tank top is open water. Model: tank volumes as glass.
  // Mezzanine ring around piazza
  const mz = L.piazza;
  box(mz.w + 16, 0.3, 4, M.floor, mz.x, Lv.mezz, mz.z + mz.d / 2 + 2, g);
  box(mz.w + 16, 0.3, 4, M.floor, mz.x, Lv.mezz, mz.z - mz.d / 2 - 2, g);
  box(4, 0.3, mz.d + 8, M.floor, mz.x + mz.w / 2 + 2, Lv.mezz, mz.z, g);
  box(4, 0.3, mz.d + 8, M.floor, mz.x - mz.w / 2 - 2, Lv.mezz, mz.z, g);
  // Roof slab with skylight opening: four boxes around the opening
  const sk = L.skylight, rs = Lv.roofSlab;
  box((B.x1 - (sk.x + sk.w / 2)), 0.5, D, M.concrete, (B.x1 + sk.x + sk.w / 2) / 2, rs, cz, g);
  box(((sk.x - sk.w / 2) - B.x0), 0.5, D, M.concrete, (B.x0 + sk.x - sk.w / 2) / 2, rs, cz, g);
  box(sk.w, 0.5, (B.z1 - (sk.z + sk.d / 2)), M.concrete, sk.x, rs, (B.z1 + sk.z + sk.d / 2) / 2, g);
  box(sk.w, 0.5, ((sk.z - sk.d / 2) - B.z0), M.concrete, sk.x, rs, (B.z0 + sk.z - sk.d / 2) / 2, g);
  // skylight frame (retracted glass): thin steel ring
  const frame = new THREE.Mesh(new THREE.TorusGeometry(1, 0.15, 6, 4), M.steel); frame.scale.set(sk.w / 2, sk.d / 2, 1); frame.rotation.x = Math.PI / 2; frame.rotation.z = Math.PI / 4; frame.position.set(sk.x, rs + 0.3, sk.z); g.add(frame);

  // Column grid between main floor and roof slab
  const colGeo = new THREE.CylinderGeometry(0.35, 0.35, rs, 10);
  const cols = []; const gs = L.columnGrid;
  for (let x = B.x0 + gs / 2; x < B.x1; x += gs) for (let z = B.z0 + gs / 2; z < B.z1; z += gs) {
    const inDome = (x - L.planetarium.x) ** 2 + (z - L.planetarium.z) ** 2 < (L.domeR + 1) ** 2 || (x - L.rainforest.x) ** 2 + (z - L.rainforest.z) ** 2 < (L.domeR + 1) ** 2;
    const inPiazza = Math.abs(x - mz.x) < mz.w / 2 && Math.abs(z - mz.z) < mz.d / 2;
    if (inDome || inPiazza) continue; cols.push([x, z]);
  }
  const colMesh = new THREE.InstancedMesh(colGeo, M.concrete, cols.length); const mtx = new THREE.Matrix4();
  cols.forEach(([x, z], i) => { mtx.makeTranslation(x, rs / 2, z); colMesh.setMatrixAt(i, mtx); }); g.add(colMesh);
  // lower-level columns
  const colMesh2 = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.4, 0.4, -Lv.aquarium, 10), M.dark, cols.length);
  cols.forEach(([x, z], i) => { mtx.makeTranslation(x, Lv.aquarium / 2, z); colMesh2.setMatrixAt(i, mtx); }); g.add(colMesh2);

  // Glass facade
  const fac = new THREE.Mesh(new THREE.BoxGeometry(W, rs, D), M.glass); fac.position.set(cx, rs / 2, cz); g.add(fac);
  // facade mullions
  const mul = new THREE.InstancedMesh(new THREE.BoxGeometry(0.15, rs, 0.15), M.steel, Math.ceil(W / 3.6) * 2 + Math.ceil(D / 3.6) * 2);
  let mi = 0; for (let x = B.x0; x <= B.x1; x += 3.6) { mtx.makeTranslation(x, rs / 2, B.z0); mul.setMatrixAt(mi++, mtx); mtx.makeTranslation(x, rs / 2, B.z1); mul.setMatrixAt(mi++, mtx); }
  for (let z = B.z0; z <= B.z1; z += 3.6) { mtx.makeTranslation(B.x0, rs / 2, z); mul.setMatrixAt(mi++, mtx); mtx.makeTranslation(B.x1, rs / 2, z); mul.setMatrixAt(mi++, mtx); }
  mul.count = mi; g.add(mul);

  // Planetarium: opaque sphere shell, interior is the dome screen (flooded in the fiction)
  const pl = new THREE.Mesh(new THREE.SphereGeometry(L.domeR, 48, 32), M.domeShell); pl.position.set(L.planetarium.x, L.planetarium.y, L.planetarium.z); g.add(pl);
  const plScreen = new THREE.Mesh(new THREE.SphereGeometry(L.domeR - 0.5, 48, 32), M.domeScreen); plScreen.position.copy(pl.position); g.add(plScreen);
  // planetarium entry portal at main floor (west side of the piazza)
  box(3, 3, 2.5, M.dark, L.planetarium.x - L.domeR + 0.5, 1.5, L.planetarium.z, g);

  // Rainforest: glass sphere, canopy inside, spiral ramp
  const rf = new THREE.Mesh(new THREE.SphereGeometry(L.domeR, 48, 32), M.glass); rf.position.set(L.rainforest.x, L.rainforest.y, L.rainforest.z); g.add(rf);
  const rfRibs = new THREE.Mesh(new THREE.SphereGeometry(L.domeR + 0.05, 24, 12), new THREE.MeshBasicMaterial({ color: 0x9fb4c0, wireframe: true, transparent: true, opacity: 0.35 })); rfRibs.position.copy(rf.position); g.add(rfRibs);
  for (let i = 0; i < 48; i++) {
    const t = i / 48, ang = t * Math.PI * 4, r = 11 - t * 2, y = -0.5 + t * 9;
    box(2.4, 0.2, 2.4, M.warm, L.rainforest.x + Math.cos(ang) * r, y, L.rainforest.z + Math.sin(ang) * r, g).rotation.y = -ang;
  }
  for (let i = 0; i < 60; i++) {
    const ang = Math.random() * Math.PI * 2, r = 3.5 + Math.random() * 5, h = 2 + Math.random() * 7;
    const tree = new THREE.Mesh(new THREE.ConeGeometry(0.8 + Math.random() * 1.6, h, 6), M.foliage); tree.position.set(L.rainforest.x + Math.cos(ang) * r, h / 2, L.rainforest.z + Math.sin(ang) * r); g.add(tree);
  }
  // Amazon tank below the dome (sealed): dark water disc
  const amGlass = new THREE.MeshPhysicalMaterial({ color: 0xa8c89a, roughness: 0.02, transparent: true, opacity: 0.25, side: THREE.DoubleSide, depthWrite: false });
  const am = new THREE.Mesh(new THREE.CylinderGeometry(L.amazon.r, L.amazon.r, L.amazon.top - L.amazon.bottom, 40, 1, false), amGlass); am.position.set(L.amazon.x, (L.amazon.top + L.amazon.bottom) / 2, L.amazon.z); g.add(am);
  const amFloor = new THREE.Mesh(new THREE.CylinderGeometry(L.amazon.r, L.amazon.r, 0.2, 40), new THREE.MeshStandardMaterial({ color: 0x3a2e1c, roughness: 1 })); amFloor.position.set(L.amazon.x, L.amazon.bottom + 0.1, L.amazon.z); g.add(amFloor);
  for (let i = 0; i < 14; i++) { const ang = Math.random() * Math.PI * 2, r = 2 + Math.random() * 8; const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.35, L.amazon.top - L.amazon.bottom, 6), new THREE.MeshStandardMaterial({ color: 0x4a3524, roughness: 1 })); trunk.position.set(L.amazon.x + Math.cos(ang) * r, (L.amazon.top + L.amazon.bottom) / 2, L.amazon.z + Math.sin(ang) * r); g.add(trunk); }

  // Airlock chamber: two doors (outer towards piazza at x1, inner towards dome at x0)
  const al = L.airlock; const alW = al.x1 - al.x0, alD = al.z1 - al.z0, alH = al.y1 - al.y0;
  const alWall = new THREE.Mesh(new THREE.BoxGeometry(alW, alH, alD), new THREE.MeshStandardMaterial({ color: 0xe6c24a, roughness: 0.6, transparent: true, opacity: 0.35, side: THREE.DoubleSide })); alWall.position.set((al.x0 + al.x1) / 2, al.y0 + alH / 2, (al.z0 + al.z1) / 2); g.add(alWall);
  const doorMat = new THREE.MeshStandardMaterial({ color: 0xffcc33, roughness: 0.5, metalness: 0.3, side: THREE.DoubleSide });
  const doorOuter = new THREE.Mesh(new THREE.BoxGeometry(0.2, 2.6, 2.2), doorMat); doorOuter.position.set(al.x1, al.y0 + 1.3, (al.z0 + al.z1) / 2); g.add(doorOuter);
  const doorInner = new THREE.Mesh(new THREE.BoxGeometry(0.2, 2.6, 2.2), doorMat); doorInner.position.set(al.x0, al.y0 + 1.3, (al.z0 + al.z1) / 2); g.add(doorInner);

  // Tanks: Philippine Coral Reef (glass walls retracted => coral heads + rock), Reef Lagoon, California Coast (sealed), Swamp (sealed)
  const tankPit = (t) => { const h = t.top - t.bottom; box(t.w, h, t.d, M.dark, t.x, t.bottom + h / 2 - 0.02, t.z, g).material = M.dark; };
  const reef = L.reefTank; // walls of the pit (floor is at bottom)
  box(reef.w + 0.6, 0.3, reef.d + 0.6, M.dark, reef.x, reef.bottom - 0.15, reef.z, g);
  for (let i = 0; i < 70; i++) {
    const mat = [M.coral, M.coral2, M.coral3][i % 3]; const s = 0.4 + Math.random() * 1.4;
    const c = new THREE.Mesh(i % 2 ? new THREE.IcosahedronGeometry(s, 0) : new THREE.ConeGeometry(s * 0.7, s * 1.6, 5), mat);
    c.position.set(reef.x + (Math.random() - 0.5) * (reef.w - 2), reef.bottom + s * 0.5 + Math.random() * 2.5, reef.z + (Math.random() - 0.5) * (reef.d - 2)); g.add(c);
  }
  // reef tank viewing wall remnants (glass retracted): low steel sills at main floor
  box(reef.w + 1, 0.6, 0.4, M.steel, reef.x, 0.3, reef.z + reef.d / 2 + 0.2, g); box(reef.w + 1, 0.6, 0.4, M.steel, reef.x, 0.3, reef.z - reef.d / 2 - 0.2, g);
  const lag = L.lagoon; box(lag.w, 0.2, lag.d, new THREE.MeshStandardMaterial({ color: 0xd8c7a0, roughness: 1 }), lag.x, lag.bottom, lag.z, g);
  for (let i = 0; i < 25; i++) { const s = 0.3 + Math.random() * 0.6; const c = new THREE.Mesh(new THREE.IcosahedronGeometry(s, 0), M.coral); c.position.set(lag.x + (Math.random() - 0.5) * (lag.w - 2), lag.bottom + s * 0.5, lag.z + (Math.random() - 0.5) * (lag.d - 2)); g.add(c); }
  const cc = L.calCoast; const ccH = cc.top - cc.bottom;
  const tankGlass = new THREE.MeshPhysicalMaterial({ color: 0x9fd9e8, roughness: 0.02, metalness: 0, transparent: true, opacity: 0.22, side: THREE.DoubleSide, depthWrite: false });
  box(cc.w, ccH, cc.d, tankGlass, cc.x, (cc.top + cc.bottom) / 2, cc.z, g);
  box(cc.w, 0.3, cc.d, new THREE.MeshStandardMaterial({ color: 0x2b3d33, roughness: 1 }), cc.x, cc.bottom + 0.15, cc.z, g);
  box(cc.w + 0.4, ccH + 0.4, 0.3, new THREE.MeshStandardMaterial({ color: 0x1d2a33, roughness: 0.9 }), cc.x, (cc.top + cc.bottom) / 2, cc.z - cc.d / 2 - 0.15, g); // back wall
  for (let i = 0; i < 24; i++) { const h = 2 + Math.random() * 4; const kelp = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.12, h, 5), new THREE.MeshStandardMaterial({ color: 0x5a6b23, roughness: 0.9 })); kelp.position.set(cc.x + (Math.random() - 0.5) * (cc.w - 1), cc.bottom + h / 2, cc.z + (Math.random() - 0.5) * (cc.d - 1)); kelp.rotation.z = (Math.random() - 0.5) * 0.3; g.add(kelp); }
  for (let i = 0; i < 12; i++) { const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(0.4 + Math.random() * 0.8, 0), new THREE.MeshStandardMaterial({ color: 0x6b6358, roughness: 1, flatShading: true })); rock.position.set(cc.x + (Math.random() - 0.5) * (cc.w - 1), cc.bottom + 0.5, cc.z + (Math.random() - 0.5) * (cc.d - 1)); g.add(rock); }
  const sw = L.swamp; const swm = new THREE.Mesh(new THREE.CylinderGeometry(sw.r, sw.r, 0.3, 32), M.sealed); swm.position.set(sw.x, 0.15, sw.z); g.add(swm);

  // African Hall: barrel vault, dioramas as recessed boxes on the long walls
  const ah = L.africanHall; const ahW = ah.x1 - ah.x0, ahD = ah.z1 - ah.z0;
  const vault = new THREE.Mesh(new THREE.CylinderGeometry(ahW / 2, ahW / 2, ahD, 24, 1, true, 0, Math.PI), new THREE.MeshStandardMaterial({ color: 0xcfc8b2, roughness: 0.9, side: THREE.DoubleSide }));
  vault.rotation.z = Math.PI / 2; vault.rotation.y = Math.PI / 2; vault.position.set((ah.x0 + ah.x1) / 2, ah.vaultTop - ahW / 2, (ah.z0 + ah.z1) / 2); vault.scale.y = 1; g.add(vault);
  for (let z = ah.z0 + 6; z < ah.z1 - 4; z += 8) { box(3, 4, 6, M.warm, ah.x0 + 1.5, 2.2, z, g); box(3, 4, 6, M.warm, ah.x1 - 1.5, 2.2, z, g); }
  // Penguins (sealed): glass block at the south end
  const pg = L.penguins; box(pg.x1 - pg.x0, 6, pg.z1 - pg.z0, M.sealed, (pg.x0 + pg.x1) / 2, 3, (pg.z0 + pg.z1) / 2, g);
  // Research wing (sealed, south side)
  const rw = L.researchWing; box(rw.x1 - rw.x0, rs, rw.z1 - rw.z0, M.sealed, (rw.x0 + rw.x1) / 2, rs / 2, (rw.z0 + rw.z1) / 2, g);
  // Café (dry) and Terrace (dry, outside the shell)
  const cf = L.cafe; const cfm = box(cf.x1 - cf.x0, rs - 0.6, cf.z1 - cf.z0, new THREE.MeshStandardMaterial({ color: 0xe9dcc2, roughness: 0.9, transparent: true, opacity: 0.55 }), (cf.x0 + cf.x1) / 2, (rs - 0.6) / 2, (cf.z0 + cf.z1) / 2, g);
  for (let i = 0; i < 14; i++) box(1.2, 0.75, 1.2, M.warm, cf.x0 + 4 + (i % 5) * 5, 0.4, cf.z0 + 5 + Math.floor(i / 5) * 8, g);
  const te = L.terrace; box(te.x1 - te.x0, 0.3, te.z1 - te.z0, M.warm, (te.x0 + te.x1) / 2, 0.15, (te.z0 + te.z1) / 2, g);
  box(te.x1 - te.x0 + 2, 0.3, te.z1 - te.z0 + 2, M.steel, (te.x0 + te.x1) / 2, 5.5, (te.z0 + te.z1) / 2, g);
  for (const [x, z] of [[te.x0 + 1, te.z0 + 1], [te.x1 - 1, te.z0 + 1], [te.x0 + 1, te.z1 - 1], [te.x1 - 1, te.z1 - 1]]) box(0.3, 5.2, 0.3, M.steel, x, 2.75, z, g);
  // Doors from outside: café west door, terrace east door
  const door = (p, y) => { const m = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2.6, 0.2), doorMat); m.position.set(p.x, y + 1.3, p.z); m.rotation.y = Math.PI / 2; g.add(m); };
  door(cf.door, 0); door(te.door, 0);

  // Exterior dry routes to the roof: lift tower by The Terrace, stair by the café terrace
  const lt = L.liftTower; const tower = new THREE.Mesh(new THREE.CylinderGeometry(lt.r, lt.r, lt.y1 - lt.y0 + 3, 24, 1, true), new THREE.MeshStandardMaterial({ color: 0xffd34d, roughness: 0.5, transparent: true, opacity: 0.35, side: THREE.DoubleSide })); tower.position.set(lt.x, (lt.y0 + lt.y1 + 3) / 2, lt.z); g.add(tower);
  const cab = new THREE.Mesh(new THREE.CylinderGeometry(lt.r - 0.4, lt.r - 0.4, 0.3, 24), M.steel); cab.position.set(lt.x, 0.15, lt.z); g.add(cab);
  const bridge = box(8, 0.3, 3, M.steel, lt.x + 4 + 2, lt.y1 + 0.1, lt.z, g); // bridge from the tower top to the roof edge
  const ws = L.westStair; for (let i = 0; i < 16; i++) box(ws.w, 0.25, ws.d / 16, M.steel, ws.x, (i + 0.5) * (ws.y1 / 16), ws.z - ws.d / 2 + (i + 0.5) * ws.d / 16, g);
  box(3, 0.3, 4, M.steel, ws.x - 2, ws.y1 + 0.1, ws.z + ws.d / 2, g);
  // T. rex in the entrance hall (north side), the pendulum: simple landmarks
  box(2, 6, 10, M.concrete, 0, 3, 44, g);
  const pend = new THREE.Mesh(new THREE.SphereGeometry(0.5, 16, 12), M.steel); pend.position.set(-45, 1.5, 44); g.add(pend);

  // Hatch markers on the roof hills and the skylight
  const markers = [];
  for (const h of L.hatches) {
    const m = new THREE.Mesh(new THREE.TorusGeometry(h.r, 0.18, 8, 32), h.wet ? M.markerWet : M.marker); m.rotation.x = Math.PI / 2; m.position.set(h.x, h.y + 0.2, h.z); g.add(m); markers.push(m);
  }
  return { group: g, markers, doors: { outer: doorOuter, inner: doorInner }, liftCab: cab };
}
