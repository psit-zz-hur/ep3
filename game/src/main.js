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

const q0 = new URLSearchParams(location.search);
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(innerWidth, innerHeight); renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.1;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0b0f14);
const camera = new THREE.PerspectiveCamera(75, innerWidth / innerHeight, 0.1, 1500);
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });

// Light: evening Friday in the park, plus underwater key from above
const hemi = new THREE.HemisphereLight(0x9fc4e8, 0x1b2a24, 0.9); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffe2b0, 1.6); sun.position.set(-120, 90, 160); scene.add(sun);
const fill = new THREE.PointLight(0x7fd0ff, 0.6, 120, 1.5); fill.position.set(0, 8, 3); scene.add(fill);
// stars / park dusk sky dome
const sky = new THREE.Mesh(new THREE.SphereGeometry(1200, 24, 12), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, uniforms: {}, vertexShader: 'varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} ', fragmentShader: 'varying vec3 vP; void main(){ float h = normalize(vP).y; vec3 c = mix(vec3(0.10,0.07,0.12), vec3(0.02,0.03,0.07), clamp(h*2.0,0.0,1.0)); c = mix(vec3(0.45,0.22,0.18), c, clamp(h*6.0+0.2,0.0,1.0)); gl_FragColor=vec4(c,1.0);} ' })); scene.add(sky);

const hud = document.getElementById('hud'), help = document.getElementById('help'), clickEl = document.getElementById('click');
help.textContent = `O skin on/off · I tile/concrete · J Skateboard Saturdays · [ ] skin line · - = fillet radius (6 in) · , . tile size · K fly through the nearest exhibit scan · WASD swim/walk · mouse look · Space up · Shift down · E sprint / ride lift up · Q lift down
F flood / drain · 1 2 3 water presets · D dome view · G registration grid · T tilt ± · P save 4K domemaster
M flood-zone map · N lidar grid · V splats (Scaniverse) · X planet warp · Shift+X next planet · H hide help`;

const site = await buildSite(scene);
const interior = buildInterior(scene);
const water = buildWater(scene);
const fish = await buildFish(scene);
const player = buildPlayer(camera, renderer.domElement, site);
const dome = buildDome(renderer, scene, camera, { faceRes: 1024, outRes: 2048 });
const pool = buildPoolSkin(scene, camera);
const splats = await buildSplats(renderer, scene, site.meta, { visible: q0.get('splats') !== '0' });
let skate = false;
function setSkate(on) {
  // Skateboard Saturdays: drained, smooth concrete sock to the ceiling, mushroom columns, whale lowered to the floor as a rib-cage arch
  skate = on; player.state.skate = on; pool.state.enabled = true; pool.setMode(on ? 1 : 0); pool.setTileTop(on ? L.levels.roofSlab + 1.0 : L.levels.roofSlab - 0.3);
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
  if (e.code === 'KeyF') water.toggle();
  if (e.code === 'Digit1') water.setTarget(L.levels.aquarium - 0.2);
  if (e.code === 'Digit2') water.setTarget(2.0);
  if (e.code === 'Digit3') water.setTarget(L.levels.roofSlab - 0.3);
  if (e.code === 'KeyD') dome.state.enabled = !dome.state.enabled;
  if (e.code === 'KeyG') dome.state.gridMix = dome.state.gridMix > 0 ? 0 : 0.85;
  if (e.code === 'KeyT') dome.state.tiltDeg = e.shiftKey ? dome.state.tiltDeg - 5 : dome.state.tiltDeg + 5;
  if (e.code === 'KeyP') dome.capture(4096);
  if (e.code === 'KeyM') map.toggle();
  if (e.code === 'KeyN') { gridOn = !gridOn; site.setGrid(gridOn ? 0.35 : 0); }
  if (e.code === 'KeyK') { if (fly.active) fly.stop(); else { let best = null, bd = 1e9; for (const p of loadedProps) { const d = p.box.getCenter(new THREE.Vector3()).distanceTo(camera.position); if (d < bd) { bd = d; best = p; } } fly.start(best); } }
  if (e.code === 'KeyO') { pool.state.enabled = !pool.state.enabled; }
  if (e.code === 'KeyI') { pool.setMode(pool.mode > 0.5 ? 0 : 1); }
  if (e.code === 'KeyJ') setSkate(!skate);
  if (e.code === 'BracketRight') pool.setTileTop(Math.min(pool.tileTop + 0.5, L.levels.roofSlab + 0.2));
  if (e.code === 'BracketLeft') pool.setTileTop(Math.max(pool.tileTop - 0.5, L.levels.aquarium));
  if (e.code === 'Equal') pool.setFillet(pool.fillet + 0.1524);       // + 6 in
  if (e.code === 'Minus') pool.setFillet(pool.fillet - 0.1524);       // - 6 in
  if (e.code === 'Period') pool.setTileSize(pool.tileSize * 1.25);
  if (e.code === 'Comma') pool.setTileSize(pool.tileSize / 1.25);
  if (e.code === 'KeyH') { showHelp = !showHelp; help.style.display = showHelp ? '' : 'none'; }
  if (e.code === 'KeyV') splats.toggle();
  if (e.code === 'KeyX') { if (e.shiftKey) { splats.setPlanet(splats.state.planet + 1); splats.state.warp = true; } else splats.toggleWarp(); }
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
if (q.get('planet') != null && q.get('planet') !== '0') { splats.setPlanet((parseInt(q.get('planet'), 10) || 1) - 1); splats.state.warp = true; }
if (q.get('skin') === 'concrete') pool.setMode(1);
if (q.get('pooldebug') === '1') pool.uniforms.uDebug.value = 1;
if (q.has('tiletop')) pool.setTileTop(parseFloat(q.get('tiletop')));
if (q.has('fillet')) pool.setFillet(parseFloat(q.get('fillet')));
if (q.has('tile')) pool.setTileSize(parseFloat(q.get('tile')));
const loadedProps = await loadProps(scene, (p) => console.log('prop', p.name));
const fly = makeFlythrough(camera);
if (q.get('nohud') === '1') { hud.style.display = 'none'; help.style.display = 'none'; clickEl.style.display = 'none'; document.getElementById('title').style.display = 'none'; }

const clock = new THREE.Clock(); let acc = 0;
function frame() {
  const dt = Math.min(clock.getDelta(), 0.05); const t = clock.elapsedTime;
  camera.position.y -= prevBreath;            // remove last frame's breath offset before physics
  const ps = fly.active ? (fly.update(dt), player.state) : player.update(dt, water);
  const env = water.update(dt, t, camera.position, !!ps.zone);
  const moving = prevPos.distanceTo(camera.position) / Math.max(dt, 1e-3) > 0.35; prevPos.copy(camera.position);
  const plaque = plaques.update(camera, moving);
  prevBreath = diver.update(dt, env.wet, water.state.level, !!plaque || !moving); camera.position.y += prevBreath;
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
  splats.update(dt);
  if (dome.state.enabled) dome.render(); else renderer.render(scene, camera);
  acc += dt; if (acc > 0.1) {
    acc = 0; const p = camera.position; const lay = env.wet ? env.layer.name : (ps.zone ? `DRY · ${ps.zone}${ps.zone === 'airlock' ? ' · ' + al.phase : ''}` : 'AIR · ' + (p.y > L.levels.roofSlab ? 'roof' : 'inside'));
    const near = fish.nearby(p, 12); const nearTxt = Object.entries(near).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([n, c]) => `${c} ${n}`).join(' · ');
    hud.textContent = `water ${water.state.level.toFixed(1)} m  depth ${env.wet ? (water.state.level - p.y).toFixed(1) : '0.0'} m\n${lay}\nxyz ${p.x.toFixed(0)} ${p.y.toFixed(1)} ${p.z.toFixed(0)}${pool.state.enabled ? `\n${pool.mode > 0.5 ? 'CONCRETE SOCK' : 'TILE SOCK'} · line ${pool.tileTop.toFixed(1)} m · fillet ${(pool.fillet / 0.3048).toFixed(1)} ft · tile ${(pool.tileSize * 100).toFixed(0)} cm` : ''}${dome.state.enabled ? `\nDOME 180° · tilt ${dome.state.tiltDeg}° · grid ${dome.state.gridMix ? 'on' : 'off'}` : ''}${splats.count() ? `\nSPLATS ${splats.state.visible ? splats.count() + ' scans' : 'off'}${splats.state.warpMix > 0.01 ? ' · ' + splats.planet().name + ' ' + Math.round(splats.state.warpMix * 100) + '%' : ''}` : ''}${nearTxt ? '\n' + nearTxt : ''}`;
    if (map.visible()) map.draw(p, water.state.level);
  }
  requestAnimationFrame(frame);
}
frame();
window.__fs = { scene, camera, water, dome, player, fish, L, pool, renderer, splats };
