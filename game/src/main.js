import * as THREE from 'three';
import { L, layerAt } from './layout.js';
import { buildSite } from './site.js';
import { buildInterior } from './building.js';
import { buildWater } from './water.js';
import { buildFish } from './fish.js';
import { buildPlayer } from './player.js';
import { buildDome } from './dome.js';
import { buildMap } from './map.js';
import { buildDiver } from './diver.js';
import { buildPlaques } from './plaques.js';
import { buildDiscovery } from './discovery.js';
import { loadWarehouseModel } from './model.js';
import { loadProps, makeFlythrough, PROPS } from './props.js';
import { buildPoolSkin } from './poolskin.js';
import { buildSplats } from './splats.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { buildLayers } from './layers.js';

const q0 = new URLSearchParams(location.search);
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: true });
const render = { scale: parseFloat(q0.get('scale')) || 1, paused: false, fps: 0 };
renderer.setPixelRatio(render.scale); renderer.setSize(innerWidth, innerHeight); renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.1;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0b0f14);
const camera = new THREE.PerspectiveCamera(75, innerWidth / innerHeight, 0.1, 1500);
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });

// Light: evening Friday in the park, plus underwater key from above
const hemi = new THREE.HemisphereLight(0x9fc4e8, 0x1b2a24, 0.9); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffe2b0, 1.6); sun.position.set(-120, 90, 160); scene.add(sun);
const fill = new THREE.PointLight(0x7fd0ff, 0.6, 120, 1.5); fill.position.set(0, 8, 3); scene.add(fill);
// stars / park dusk sky dome
const sky = new THREE.Mesh(new THREE.SphereGeometry(1200, 24, 12), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, uniforms: {}, vertexShader: 'varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} ', fragmentShader: 'varying vec3 vP; void main(){ float h = normalize(vP).y; vec3 c = mix(vec3(0.10,0.07,0.12), vec3(0.02,0.03,0.07), clamp(h*2.0,0.0,1.0)); c = mix(vec3(0.45,0.22,0.18), c, clamp(h*6.0+0.2,0.0,1.0)); gl_FragColor=vec4(c,1.0);} ' })); sky.name = 'sky'; scene.add(sky);

const hud = document.getElementById('hud'), help = document.getElementById('help'), clickEl = document.getElementById('click');
help.textContent = `O skin on/off · I tile / concrete / skatepark · J Skateboard Saturdays · [ ] skin line · - = fillet radius (6 in) · , . tile size · K fly through the nearest exhibit scan · WASD swim/walk · mouse look · Space up · Shift down · E sprint / ride lift up · Q lift down
F flood / drain · 1 2 3 water presets · C dome view · G registration grid · T tilt ± · P save 4K domemaster
\` ADMIN mode (orbit / zoom with the mouse, WASD + Q E fly through walls, Shift fast, no physics)
M flood-zone map · N lidar grid · V splats (Scaniverse) · X planet warp (Shift+X flips it) · H hide help`;

const site = await buildSite(scene);
const interior = buildInterior(scene);
const water = buildWater(scene);
const fish = await buildFish(scene);
const player = buildPlayer(camera, renderer.domElement, site);
const dome = buildDome(renderer, scene, camera, { faceRes: 1024, outRes: 2048 });
// ADMIN mode: orbit / zoom / pan with the mouse (OrbitControls), WASD + Q/E fly through walls, physics off. Sticky per browser.
const admin = { on: false, speed: 24, keys: {} }; let layers = null;
const orbit = new OrbitControls(camera, renderer.domElement); orbit.enableDamping = true; orbit.dampingFactor = 0.08; orbit.enabled = false; orbit.minDistance = 0.3; orbit.maxDistance = 2000; orbit.zoomSpeed = 1.2;
const _dir = new THREE.Vector3(), _right = new THREE.Vector3(), _mv = new THREE.Vector3();
function setAdmin(on) {
  admin.on = on; orbit.enabled = on;
  if (on) { if (player.controls.isLocked) player.controls.unlock(); clickEl.style.display = 'none'; camera.getWorldDirection(_dir); orbit.target.copy(camera.position).addScaledVector(_dir, 30); orbit.update(); }
  else { clickEl.style.display = ''; }
  try { localStorage.setItem('fs.mode', on ? 'admin' : 'play'); } catch (e) { /* private window */ }
  if (layers) layers.show(on);
}
function adminMove(dt) {
  const k = admin.keys; const sp = admin.speed * (k.ShiftLeft || k.ShiftRight ? 4 : 1) * dt;
  camera.getWorldDirection(_dir); _right.crossVectors(_dir, camera.up).normalize(); _mv.set(0, 0, 0);
  if (k.KeyW) _mv.add(_dir); if (k.KeyS) _mv.sub(_dir); if (k.KeyD) _mv.add(_right); if (k.KeyA) _mv.sub(_right); if (k.KeyE) _mv.y += 1; if (k.KeyQ) _mv.y -= 1;
  if (_mv.lengthSq() > 0) { _mv.normalize().multiplyScalar(sp); camera.position.add(_mv); orbit.target.add(_mv); }
  orbit.update();
}
addEventListener('keyup', (e) => { admin.keys[e.code] = false; });
const pool = buildPoolSkin(scene, camera);
const splats = await buildSplats(renderer, scene, site.meta, { visible: q0.get('splats') !== '0' });
let skate = false;
function setSkate(on) {
  // Skateboard Saturdays: drained, smooth concrete sock to the ceiling, mushroom columns, whale lowered to the floor as a rib-cage arch
  skate = on; player.state.skate = on; pool.state.enabled = true; pool.setMode(on ? 2 : 0); pool.setTileTop(on ? L.levels.roofSlab + 1.0 : L.levels.roofSlab - 0.3);
  water.setTarget(on ? L.levels.aquarium - 0.2 : water.state.target);
  const whale = scene.getObjectByName('whale-procedural'); if (whale) whale.position.y = on ? 1.9 : L.whale.y;
  document.getElementById('title').textContent = on ? 'SKATEBOARD SATURDAYS · CAL ACADEMY · DESIGN FICTION' : 'FREESWIM FRIDAYS · CAL ACADEMY · DESIGN FICTION';
}
const map = buildMap();
const diver = buildDiver(scene, camera);
const plaques = buildPlaques(scene);
const discovery = buildDiscovery(fish);
let prevBreath = 0, prevPos = new THREE.Vector3();
site.setGrid(0.35);

clickEl.addEventListener('click', () => { player.controls.lock(); });
player.controls.addEventListener('lock', () => clickEl.classList.add('hidden'));
player.controls.addEventListener('unlock', () => clickEl.classList.remove('hidden'));
let showHelp = true, gridOn = true;
addEventListener('keydown', (e) => {
  if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON')) return;
  admin.keys[e.code] = true;
  if (e.code === 'Backquote') { setAdmin(!admin.on); return; }
  if (e.code === 'KeyR') { render.paused = !render.paused; hud.textContent = (render.paused ? 'PAUSED · R resumes\n' : '') + hud.textContent; return; }
  if (e.code === 'KeyF') water.toggle();
  if (e.code === 'Digit1') water.setTarget(L.levels.aquarium - 0.2);
  if (e.code === 'Digit2') water.setTarget(2.0);
  if (e.code === 'Digit3') water.setTarget(L.levels.roofSlab - 0.3);
  if (e.code === 'KeyC') dome.state.enabled = !dome.state.enabled;
  if (e.code === 'KeyG') dome.state.gridMix = dome.state.gridMix > 0 ? 0 : 0.85;
  if (e.code === 'KeyT') dome.state.tiltDeg = e.shiftKey ? dome.state.tiltDeg - 5 : dome.state.tiltDeg + 5;
  if (e.code === 'KeyP') dome.capture(4096);
  if (e.code === 'KeyM') map.toggle();
  if (e.code === 'KeyN') { gridOn = !gridOn; site.setGrid(gridOn ? 0.35 : 0); }
  if (e.code === 'KeyK') flyNearest();
  if (e.code === 'KeyO') { pool.state.enabled = !pool.state.enabled; }
  if (e.code === 'KeyI') { pool.setMode((Math.round(pool.mode) + 1) % 3); }
  if (e.code === 'KeyJ') setSkate(!skate);
  if (e.code === 'BracketRight') pool.setTileTop(Math.min(pool.tileTop + 0.5, L.levels.roofSlab + 0.2));
  if (e.code === 'BracketLeft') pool.setTileTop(Math.max(pool.tileTop - 0.5, L.levels.aquarium));
  if (e.code === 'Equal') pool.setFillet(pool.fillet + 0.1524);       // + 6 in
  if (e.code === 'Minus') pool.setFillet(pool.fillet - 0.1524);       // - 6 in
  if (e.code === 'Period') pool.setTileSize(pool.tileSize * 1.25);
  if (e.code === 'Comma') pool.setTileSize(pool.tileSize / 1.25);
  if (e.code === 'KeyH') { showHelp = !showHelp; help.style.display = showHelp ? '' : 'none'; }
  if (e.code === 'KeyV') splats.toggle();
  if (e.code === 'KeyX') { if (e.shiftKey) splats.setFlip(!splats.planet().flip); else splats.toggleWarp(); }
});
// URL params for headless tests: ?water=9&pos=x,y,z&look=x,y,z&dome=1&grid=1&map=1
const q = new URLSearchParams(location.search);
if (q.has('water')) { const v = parseFloat(q.get('water')); water.state.level = v; water.state.target = v; }
if (q.has('pos')) { const [x, y, z] = q.get('pos').split(',').map(Number); camera.position.set(x, y, z); }
if (q.has('look')) { const [x, y, z] = q.get('look').split(',').map(Number); camera.lookAt(x, y, z); }
if (q.get('dome') === '1') dome.state.enabled = true;
if (q.get('grid') === '1') dome.state.gridMix = 0.85;
if (q.get('map') === '1') map.toggle();
if (q.has('tilt')) dome.state.tiltDeg = parseFloat(q.get('tilt'));
if (q.get('model') === '1') loadWarehouseModel(scene);
if (q.get('pool') === '1') pool.state.enabled = true;
if (q.get('skate') === '1') setSkate(true);
{ let m = null; try { m = localStorage.getItem('fs.mode'); } catch (e) {} if (q.get('admin') === '1' || (q.get('admin') == null && m === 'admin')) setAdmin(true); if (q.get('admin') === '0') setAdmin(false); }
if (q.get('planet') != null && q.get('planet') !== '0') { splats.setPlanet((parseInt(q.get('planet'), 10) || 1) - 1); splats.state.warp = true; }
if (q.get('skin') === 'concrete') pool.setMode(1);
if (q.get('skin') === 'skatepark') pool.setMode(2);
if (q.get('pooldebug') === '1') pool.uniforms.uDebug.value = 1;
if (q.has('tiletop')) pool.setTileTop(parseFloat(q.get('tiletop')));
if (q.has('fillet')) pool.setFillet(parseFloat(q.get('fillet')));
if (q.has('tile')) pool.setTileSize(parseFloat(q.get('tile')));
const loadedProps = q.get('props') === '0' ? [] : await loadProps(scene, (p) => console.log('prop', p.name));   // ?props=0 skips the Sketchfab props (fast loads, headless stills)
const fly = makeFlythrough(camera);
function flyNearest() { if (fly.active) { fly.stop(); return; } let best = null, bd = 1e9; for (const p of loadedProps) { const d = p.box.getCenter(new THREE.Vector3()).distanceTo(camera.position); if (d < bd) { bd = d; best = p; } } fly.start(best); }
function goTo(px, py, pz, lx, ly, lz) { camera.position.set(px, py, pz); camera.lookAt(lx, ly, lz); orbit.target.set(lx, ly, lz); }
const VIEWS = [
  ['roof hill (start)', [29, 15.2, 10], [0, 9.6, 3]], ['from the park', [120, 70, 190], [0, 5, 0]], ['piazza', [0, 3, 30], [0, 2, 0]], ['whale hall', [-58, 2.4, 36], [-64, 6.4, 6]],
  ['planetarium', [L.planetarium.x - 24, 4, L.planetarium.z + 2], [L.planetarium.x, 5.6, L.planetarium.z]], ['African Hall', [67, 2, -10], [67, 4, -40]], ['reef tank', [-52, -2, -8], [-52, -4, -28]],
  ['under the floor', [0, -5, 40], [0, -3, 0]], ['plan from above', [0, 120, 4], [0, 0, 3]], ['planet seat', [90, 60, 150], [0, 35, 3]],
];
layers = buildLayers([
  { name: 'Lidar site (2023 DSM)', objects: () => [site.mesh] },
  { name: 'Building interior', objects: () => [interior.group] },
  { name: 'Blue whale (procedural)', objects: () => [scene.getObjectByName('whale-procedural')] },
  { name: 'Pool skin (SDF)', on: pool.state.enabled, set: (v) => { pool.state.enabled = v; } },
  { name: 'Water surface', objects: () => water.meshes },
  { name: 'Fish', objects: () => Object.values(fish.groups || {}).flat() },
  { name: 'Exhibit props (Sketchfab)', objects: () => loadedProps.map((p) => p.root) },
  { name: 'Plaques', objects: () => [scene.getObjectByName('plaques')] },
  { name: 'Sky', objects: () => [sky] },
], splats, {
  footer: '` leaves ADMIN · V / X also toggle splats and the planet warp',
  props: [
    { group: 'RENDER', label: 'PAUSE RENDER (R)', kind: 'toggle', get: () => render.paused, set: (v) => { render.paused = v; } },
    // VIEW: everything the keys do, as controls
    { group: 'VIEW', label: 'dome view (C)', kind: 'toggle', get: () => dome.state.enabled, set: (v) => { dome.state.enabled = v; } },
    { group: 'VIEW', label: 'registration grid (G)', kind: 'toggle', get: () => dome.state.gridMix > 0, set: (v) => { dome.state.gridMix = v ? 0.85 : 0; } },
    { group: 'VIEW', label: 'dome tilt (T)', get: () => dome.state.tiltDeg, set: (v) => { dome.state.tiltDeg = v; }, min: -10, max: 60, step: 1, reset: 30, unit: '°' },
    { group: 'VIEW', label: 'flood-zone map (M)', kind: 'toggle', get: () => map.visible(), set: (v) => { if (map.visible() !== v) map.toggle(); } },
    { group: 'VIEW', label: 'lidar 10 m grid (N)', kind: 'toggle', get: () => gridOn, set: (v) => { gridOn = v; site.setGrid(v ? 0.35 : 0); } },
    { group: 'VIEW', label: 'help text (H)', kind: 'toggle', get: () => showHelp, set: (v) => { showHelp = v; help.style.display = v ? '' : 'none'; } },
    { group: 'VIEW', label: 'save 4K domemaster (P)', kind: 'button', run: () => dome.capture(4096) },
    { group: 'VIEW', label: 'fly through nearest prop (K)', kind: 'button', run: () => flyNearest() },
    { group: 'VIEW', label: 'back to PLAY (`)', kind: 'button', run: () => setAdmin(false) },
    // CAMERA bookmarks
    ...VIEWS.map(([n, p, l]) => ({ group: 'CAMERA', label: n, kind: 'button', run: () => goTo(...p, ...l) })),
    // WATER
    { group: 'WATER', label: 'flood / drain (F)', kind: 'button', run: () => water.toggle() },
    { group: 'WATER', label: '1 · aquarium', kind: 'button', run: () => water.setTarget(L.levels.aquarium - 0.2) },
    { group: 'WATER', label: '2 · main +2 m', kind: 'button', run: () => water.setTarget(2.0) },
    { group: 'WATER', label: '3 · to the roof', kind: 'button', run: () => water.setTarget(L.levels.roofSlab - 0.3) },
    { group: 'WATER', label: 'water level', get: () => water.state.level, set: (v) => { water.state.level = v; water.state.target = v; water.state.flooding = false; }, min: L.levels.aquarium - 0.5, max: L.levels.roofSlab + 2, step: 0.05, reset: L.levels.roofSlab - 0.3, unit: 'm' },
    { group: 'RENDER', label: 'render scale (device px)', get: () => render.scale, set: (v) => { render.scale = v; renderer.setPixelRatio(v); renderer.setSize(innerWidth, innerHeight); }, min: 0.35, max: 2, step: 0.05, reset: 1, fmt: (v) => `${v.toFixed(2)}× · ${Math.round(innerWidth * v)}×${Math.round(innerHeight * v)}` },
    { group: 'RENDER', label: 'pool-skin raymarch steps', get: () => pool.uniforms.uSteps.value, set: (v) => { pool.uniforms.uSteps.value = Math.round(v); }, min: 24, max: 160, step: 4, reset: 96, fmt: (v) => `${Math.round(v)}` },
    { group: 'RENDER', label: 'props (Sketchfab) drawn', kind: 'toggle', get: () => loadedProps.every((p) => p.root.visible), set: (v) => { for (const p of loadedProps) p.root.visible = v; } },
    // POOL SKIN (poolskin.js): the raymarched sock below the tile line
    { group: 'POOL SKIN', label: 'Skateboard Saturdays (J)', kind: 'toggle', get: () => skate, set: (v) => setSkate(v) },
    { group: 'POOL SKIN', label: 'skin on (O)', kind: 'toggle', get: () => pool.state.enabled, set: (v) => { pool.state.enabled = v; } },
    { group: 'POOL SKIN', label: 'skin', get: () => Math.round(pool.mode), set: (v) => pool.setMode(Math.round(v)), min: 0, max: 2, step: 1, reset: 0, fmt: (v) => ['tile', 'concrete', 'skatepark'][Math.round(v)] },
    { group: 'POOL SKIN', label: 'route band width', get: () => pool.band, set: (v) => pool.setBand(v), min: 0.2, max: 3, step: 0.05, reset: 0.8, unit: 'm' },
    { group: 'POOL SKIN', label: 'hatch pitch', get: () => pool.hatch, set: (v) => pool.setHatch(v), min: 0.15, max: 2, step: 0.05, reset: 0.6, unit: 'm' },
    { group: 'POOL SKIN', label: 'fillet radius', get: () => pool.fillet, set: (v) => pool.setFillet(v), min: 0.05, max: 6, step: 0.0254, reset: 0.9144, fmt: (v) => `${(v / 0.3048).toFixed(1)} ft · ${v.toFixed(2)} m` },
    { group: 'POOL SKIN', label: 'tile line (height)', get: () => pool.tileTop, set: (v) => pool.setTileTop(v), min: L.levels.aquarium, max: L.levels.roofSlab + 1.0, step: 0.05, reset: L.levels.roofSlab - 0.3, unit: 'm' },
    { group: 'POOL SKIN', label: 'tile size', get: () => pool.tileSize, set: (v) => pool.setTileSize(v), min: 0.05, max: 2.0, step: 0.01, reset: 0.3, fmt: (v) => `${(v * 100).toFixed(0)} cm` },
    { group: 'POOL SKIN', label: 'column capital', get: () => pool.uniforms.uCapital.value, set: (v) => { pool.uniforms.uCapital.value = v; }, min: 0, max: 4, step: 0.05, reset: 1.6, unit: 'm' },
    // PLANET (splats.js sphere inversion)
    { group: 'BLOB PLANET', label: 'warp on', kind: 'toggle', get: () => splats.state.warp, set: (v) => { splats.state.warp = v; } },
    { group: 'BLOB PLANET', label: 'flipped (roof on top)', kind: 'toggle', get: () => !!splats.planet().flip, set: (v) => splats.setFlip(v) },
    { group: 'BLOB PLANET', label: 'centre height', get: () => splats.uniforms.centre.value.y, set: (v) => { splats.uniforms.centre.value.y = v; splats.planet().centre[1] = v; splats.uniforms.mirrorY.value = v - (splats.uniforms.radius.value ** 2) / (2 * Math.max(Math.abs(v), 1e-3)); splats.touch(); }, min: 5, max: 200, step: 0.5, reset: 60, unit: 'm' },
    { group: 'BLOB PLANET', label: 'radius', get: () => splats.uniforms.radius.value, set: (v) => { splats.uniforms.radius.value = v; splats.planet().radius = v; const cy = splats.uniforms.centre.value.y; splats.uniforms.mirrorY.value = cy - (v * v) / (2 * Math.max(Math.abs(cy), 1e-3)); splats.touch(); }, min: 5, max: 200, step: 0.5, reset: 60, unit: 'm' },
    { group: 'BLOB PLANET', label: 'centre X', get: () => splats.uniforms.centre.value.x, set: (v) => { splats.uniforms.centre.value.x = v; splats.planet().centre[0] = v; splats.touch(); }, min: -120, max: 120, step: 0.5, reset: 0, unit: 'm' },
    { group: 'BLOB PLANET', label: 'centre Z', get: () => splats.uniforms.centre.value.z, set: (v) => { splats.uniforms.centre.value.z = v; splats.planet().centre[2] = v; splats.touch(); }, min: -120, max: 120, step: 0.5, reset: 3, unit: 'm' },
    // ADMIN camera
    { group: 'ADMIN', label: 'fly speed', get: () => admin.speed, set: (v) => { admin.speed = v; }, min: 2, max: 120, step: 1, reset: 24, unit: 'm/s' },
  ],
});
layers.show(admin.on);
if (q.get('nohud') === '1') { hud.style.display = 'none'; help.style.display = 'none'; clickEl.style.display = 'none'; document.getElementById('title').style.display = 'none'; }

const clock = new THREE.Clock(); let acc = 0;
let fpsN = 0, fpsT = 0;
function frame() {
  if (render.paused) { if (admin.on) layers.sync(); requestAnimationFrame(frame); return; }
  const dt = Math.min(clock.getDelta(), 0.05); const t = clock.elapsedTime; fpsN++; fpsT += dt; if (fpsT > 0.5) { render.fps = Math.round(fpsN / fpsT); fpsN = 0; fpsT = 0; }
  camera.position.y -= prevBreath;            // remove last frame's breath offset before physics
  const ps = admin.on ? (fly.active ? fly.update(dt) : adminMove(dt), player.state) : fly.active ? (fly.update(dt), player.state) : player.update(dt, water);
  const env = water.update(dt, t, camera.position, !!ps.zone);
  const moving = prevPos.distanceTo(camera.position) / Math.max(dt, 1e-3) > 0.35; prevPos.copy(camera.position);
  const plaque = plaques.update(camera, moving);
  prevBreath = admin.on ? 0 : diver.update(dt, env.wet, water.state.level, !!plaque || !moving); camera.position.y += prevBreath;
  discovery.update(camera, t, env.wet);
  fish.update(dt, water.state.level, camera.position, t);
  // roof transparency when inside the shell or below the deck
  const insideShell = camera.position.y < L.levels.roofSlab + 0.5 && Math.abs(camera.position.x) < 86 && camera.position.z > -56 && camera.position.z < 57;
  site.setRoofAlpha(insideShell ? 0.12 : 1.0);
  hemi.intensity = env.wet ? 1.1 * env.layer.light + 0.35 : 0.9; sun.intensity = env.wet ? 1.4 * env.layer.light + 0.3 : 1.6; fill.intensity = env.wet ? 1.2 : 0.6; fill.position.set(camera.position.x, camera.position.y + 6, camera.position.z);
  // airlock doors: outer closes when draining, inner opens when dry
  const al = ps.airlock; interior.doors.outer.visible = !(ps.zone === 'airlock' && al.phase === 'idle'); interior.doors.inner.visible = al.phase !== 'dry';
  // dive porthole markers pulse
  interior.markers.forEach((m, i) => m.scale.setScalar(1 + 0.08 * Math.sin(t * 2 + i)));
  pool.update(t, water.state.level, scene.fog, env.wet ? env.layer.light : 1.0);
  splats.update(dt); layers.enforce();
  if (dome.state.enabled) dome.render(); else renderer.render(scene, camera);
  acc += dt; if (acc > 0.1) {
    acc = 0; const p = camera.position; const lay = env.wet ? env.layer.name : (ps.zone ? `DRY · ${ps.zone}${ps.zone === 'airlock' ? ' · ' + al.phase : ''}` : 'AIR · ' + (p.y > L.levels.roofSlab ? 'roof' : 'inside'));
    const near = fish.nearby(p, 12); const nearTxt = Object.entries(near).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([n, c]) => `${c} ${n}`).join(' · ');
    hud.textContent = `${admin.on ? 'ADMIN · orbit / fly · ` back to play · ' + render.fps + ' fps · R pauses\n' : ''}water ${water.state.level.toFixed(1)} m  depth ${env.wet ? (water.state.level - p.y).toFixed(1) : '0.0'} m\n${lay}\nxyz ${p.x.toFixed(0)} ${p.y.toFixed(1)} ${p.z.toFixed(0)}${pool.state.enabled ? `\n${pool.modeName} · line ${pool.tileTop.toFixed(1)} m · fillet ${(pool.fillet / 0.3048).toFixed(1)} ft · tile ${(pool.tileSize * 100).toFixed(0)} cm` : ''}${dome.state.enabled ? `\nDOME 180° · tilt ${dome.state.tiltDeg}° · grid ${dome.state.gridMix ? 'on' : 'off'}` : ''}${splats.count() ? `\nSPLATS ${splats.state.visible ? splats.count() + ' scans' : 'off'}${splats.state.warpMix > 0.01 ? ' · ' + splats.planet().name + ' ' + Math.round(splats.state.warpMix * 100) + '%' : ''}` : ''}${nearTxt ? '\n' + nearTxt : ''}`;
    if (map.visible()) map.draw(p, water.state.level);
    if (admin.on) layers.sync();
  }
  requestAnimationFrame(frame);
}
frame();
window.__fs = { scene, camera, water, dome, player, fish, L, pool, renderer, splats, admin, orbit, setAdmin, layers, render };
