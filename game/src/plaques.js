// Exhibit plaques: billboards in the world with real exhibit text; a reading overlay when you hover in front of one.
import * as THREE from 'three';
import { L } from './layout.js';

export const PLAQUES = [
  { id: 'reef', title: 'Philippine Coral Reef', pos: [L.reefTank.x, 1.4, L.reefTank.z + L.reefTank.d / 2 + 1.2], face: [0, 0, 1], body: 'One of the deepest living coral reef displays in the world: 212,000 gallons, 25 feet deep, about 2,000 fish and living corals from the Philippines, the heart of the Coral Triangle. Tonight the glass is retracted. The reef is the museum.' },
  { id: 'lagoon', title: 'Reef Lagoon', pos: [L.lagoon.x, 1.2, L.lagoon.z + L.lagoon.d / 2 + 1.2], face: [0, 0, 1], body: 'A shallow lagoon of rays and small reef sharks, seen from the piazza. Rays rest on the sand; blacktips patrol the edge. Keep your fins still and they will come to you.' },
  { id: 'planetarium', title: 'Morrison Planetarium', pos: [L.planetarium.x - L.domeR - 1.5, 1.6, L.planetarium.z + 3], face: [-1, 0, 0], body: 'A 75-foot, 30-degree tilted dome, six 4K laser projectors, 290 seats. On Freeswim Fridays the sphere floods to the crown and the show runs for an audience that drifts. Enter through the porthole on the west hill.' },
  { id: 'rainforest', title: 'Osher Rainforest', pos: [L.airlock.x1 + 1.2, 1.6, L.airlock.z1 + 1.0], face: [1, 0, 0], body: 'A four-storey glass sphere, 90 feet across, kept at 85 F and 75 percent humidity. It stays dry tonight. Cycle through the airlock: outer door, drain, inner door. Surface slowly.' },
  { id: 'whale', title: 'Blue Whale', pos: [L.whale.x + 2, 1.6, L.whale.z + 6], face: [0, 0, 1], body: 'Balaenoptera musculus, about 87 feet, the largest animal that has ever lived. It has hung here since the building opened in 2008; Giants of Land and Sea was built underneath it in 2018. Tonight you can swim its length and look it in the eye.' },
  { id: 'african', title: 'African Hall', pos: [L.africanHall.x0 - 1.5, 1.6, (L.africanHall.z0 + L.africanHall.z1) / 2], face: [-1, 0, 0], body: 'The 1934 hall rebuilt to its original volume: dioramas of the savanna under a barrel vault. The penguins at the far end are sealed behind their own glass; they keep their cold water.' },
  { id: 'piazza', title: 'The Piazza', pos: [L.piazza.x + 6, 1.6, L.piazza.z - L.piazza.d / 2 - 1], face: [0, 0, -1], body: 'The open heart of the building under a 66 by 90 foot skylight. The skylight is open; the roof above is the shore. Look up: that is the way out.' },
  { id: 'swamp', title: 'The Swamp', pos: [L.swamp.x + L.swamp.r + 1.2, 1.4, L.swamp.z], face: [1, 0, 0], body: 'Claude, the albino alligator, stays in his own water. The enclosure is sealed for his sake and yours. Watch from above as he watches you.' },
  { id: 'calcoast', title: 'California Coast', pos: [L.calCoast.x, 1.2, L.calCoast.z + L.calCoast.d / 2 + 1.2], face: [0, 0, 1], body: 'A cold-water tank, 55 F, kept sealed. You are warm-water tonight. Swim along the glass and watch rockfish, anemones and a kelp forest from the wrong side of the window.' },
];

export function buildPlaques(scene) {
  const group = new THREE.Group(); scene.add(group);
  const texs = [];
  for (const p of PLAQUES) {
    const c = document.createElement('canvas'); c.width = 512; c.height = 320; const g = c.getContext('2d');
    g.fillStyle = '#f2efe6'; g.fillRect(0, 0, 512, 320); g.fillStyle = '#1b1b1b'; g.font = 'bold 30px Helvetica, Arial, sans-serif'; g.fillText(p.title.toUpperCase(), 24, 50);
    g.fillStyle = '#d4a017'; g.fillRect(24, 62, 120, 4); g.fillStyle = '#333'; g.font = '19px Helvetica, Arial, sans-serif';
    const words = p.body.split(' '); let line = '', y = 100; for (const w of words) { const t = line + w + ' '; if (g.measureText(t).width > 464) { g.fillText(line, 24, y); line = w + ' '; y += 26; } else line = t; } g.fillText(line, 24, y);
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; texs.push(tex);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.0), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.6 })); m.position.set(...p.pos);
    const f = new THREE.Vector3(...p.face); m.lookAt(m.position.clone().add(f)); group.add(m);
    const post = new THREE.Mesh(new THREE.BoxGeometry(0.08, p.pos[1], 0.08), new THREE.MeshStandardMaterial({ color: 0x444 })); post.position.set(p.pos[0], p.pos[1] / 2, p.pos[2]); group.add(post);
    p.mesh = m; p.normal = f;
  }
  const ov = document.createElement('div'); ov.style.cssText = 'position:fixed;left:50%;top:50%;transform:translate(-50%,-50%) scale(.98);width:min(560px,80vw);padding:22px 26px;background:rgba(242,239,230,.92);color:#222;font:16px/1.5 Helvetica,Arial,sans-serif;border-left:6px solid #d4a017;opacity:0;transition:opacity .5s, transform .5s;pointer-events:none;box-shadow:0 20px 60px rgba(0,0,0,.5)'; document.body.appendChild(ov);
  const fwd = new THREE.Vector3(), to = new THREE.Vector3();
  function update(camera, moving) {
    camera.getWorldDirection(fwd); let best = null, bestD = 99;
    for (const p of PLAQUES) { to.copy(p.mesh.position).sub(camera.position); const d = to.length(); if (d < 3.2 && d < bestD && to.normalize().dot(fwd) > 0.8 && fwd.dot(p.normal) < -0.3) { best = p; bestD = d; } }
    if (best && !moving) { ov.innerHTML = `<div style="font-weight:700;letter-spacing:.08em;font-size:13px;color:#8a6a00">EXHIBIT · ${best.title.toUpperCase()}</div><div style="margin-top:8px">${best.body}</div>`; ov.style.opacity = '1'; ov.style.transform = 'translate(-50%,-50%) scale(1)'; }
    else { ov.style.opacity = '0'; ov.style.transform = 'translate(-50%,-50%) scale(.98)'; }
    return best;
  }
  return { update, group };
}
