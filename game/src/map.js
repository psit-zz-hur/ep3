// Flood-zone plan overlay (press M). Draws the layout zones on a 2D canvas.
import { L } from './layout.js';
const COL = { flood: 'rgba(40,150,210,.55)', dry: 'rgba(90,200,120,.55)', sealed: 'rgba(120,120,130,.6)', airlock: 'rgba(255,210,70,.7)', route: 'rgba(255,170,60,.5)' };
export function buildMap() {
  const c = document.createElement('canvas'); c.width = 900; c.height = 560; c.style.cssText = 'position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);width:min(90vw,900px);background:rgba(0,0,0,.85);border:1px solid #345;display:none;pointer-events:none';
  document.body.appendChild(c); const g = c.getContext('2d');
  const S = 3.4, ox = 450, oz = 290; // px per m, origin (building centre); +Z (north, concourse) drawn DOWN? draw north up: screen y = oz - z*S
  const X = (x) => ox - x * S, Y = (z) => oz - z * S;   // east (-x) to the right, north (+z) up
  function draw(player, waterLevel) {
    g.clearRect(0, 0, c.width, c.height); g.font = '11px ui-monospace, monospace';
    // footprint
    g.strokeStyle = '#9ab'; g.lineWidth = 1.5; g.strokeRect(X(L.bbox.x1), Y(L.bbox.z1), (L.bbox.x1 - L.bbox.x0) * S, (L.bbox.z1 - L.bbox.z0) * S);
    for (const z of L.zones) {
      g.fillStyle = COL[z.kind]; g.strokeStyle = 'rgba(255,255,255,.35)';
      if (z.circle) { g.beginPath(); g.arc(X(z.circle.x), Y(z.circle.z), z.circle.r * S, 0, Math.PI * 2); g.fill(); g.stroke(); }
      else if (z.level === 'roof') { continue; }
      else { g.fillRect(X(z.x1), Y(z.z1), (z.x1 - z.x0) * S, (z.z1 - z.z0) * S); g.strokeRect(X(z.x1), Y(z.z1), (z.x1 - z.x0) * S, (z.z1 - z.z0) * S); }
    }
    // labels
    g.fillStyle = '#eef'; let i = 0;
    for (const z of L.zones) { const cx = z.circle ? z.circle.x : (z.x0 + z.x1) / 2, cz = z.circle ? z.circle.z : (z.z0 + z.z1) / 2; if (z.level === 'roof') continue; g.fillText(z.name, X(cx) - 30, Y(cz) + 4); i++; }
    // hatches, doors
    g.fillStyle = '#ffd34d'; for (const h of L.hatches) { g.beginPath(); g.arc(X(h.x), Y(h.z), 5, 0, Math.PI * 2); g.fill(); }
    g.fillStyle = '#5f5'; for (const d of [L.cafe.door, L.terrace.door]) g.fillRect(X(d.x) - 3, Y(d.z) - 3, 6, 6);
    // player
    g.fillStyle = '#fff'; g.beginPath(); g.arc(X(player.x), Y(player.z), 4, 0, Math.PI * 2); g.fill();
    // legend
    const leg = [['flood', 'FLOODED (public, exhibits waterproofed)'], ['dry', 'DRY PUBLIC (café, Terrace, rainforest)'], ['airlock', 'AIRLOCK'], ['sealed', 'SEALED (animals, cold tank, research, admin, LSS)'], ['route', 'DRY ROUTE TO ROOF (exterior lift + stair)']];
    leg.forEach(([k, t], j) => { g.fillStyle = COL[k]; g.fillRect(12, 12 + j * 16, 14, 11); g.fillStyle = '#dde'; g.fillText(t, 32, 22 + j * 16); });
    g.fillStyle = '#9cf'; g.fillText(`water level ${waterLevel.toFixed(1)} m  ·  N up  ·  east right`, 12, c.height - 12);
  }
  return { canvas: c, draw, toggle: () => { c.style.display = c.style.display === 'none' ? 'block' : 'none'; }, visible: () => c.style.display !== 'none' };
}
