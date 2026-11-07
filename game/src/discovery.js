// Species discovery log: when a fish passes within 2.5 m and in front of you, it is logged; the card appears.
import * as THREE from 'three';
export function buildDiscovery(fish) {
  const seen = new Set(); const total = fish.groups.length;
  const card = document.createElement('div'); card.style.cssText = 'position:fixed;right:18px;bottom:48px;width:300px;padding:14px 16px;background:rgba(6,20,30,.82);color:#dff;border:1px solid rgba(120,220,255,.35);font:13px/1.45 ui-monospace,Menlo,monospace;opacity:0;transition:opacity .4s;pointer-events:none'; document.body.appendChild(card);
  const counter = document.createElement('div'); counter.style.cssText = 'position:fixed;right:18px;top:10px;color:#9fe;font:12px ui-monospace,Menlo,monospace;text-shadow:0 1px 2px #000;opacity:.9;pointer-events:none;text-align:right'; document.body.appendChild(counter);
  let hideAt = 0; const fwd = new THREE.Vector3(), to = new THREE.Vector3();
  function update(camera, t, wet) {
    counter.textContent = wet || seen.size ? `species found ${seen.size} / ${total}` : '';
    if (!wet) return; camera.getWorldDirection(fwd);
    for (const g of fish.groups) {
      if (seen.has(g.sp.name)) continue;
      for (const p of g.pos) { to.copy(p).sub(camera.position); const d = to.length(); if (d < 2.8 && to.normalize().dot(fwd) > 0.6) { seen.add(g.sp.name); show(g.sp, t); break; } }
    }
    if (t > hideAt) card.style.opacity = '0';
  }
  function show(sp, t) {
    const hz = sp.hazard ? `<div style="color:#ffb86b;margin-top:6px">${sp.hazard}</div>` : '';
    card.innerHTML = `<div style="color:#9fe;font-size:11px;letter-spacing:.1em">NEW SPECIES · ${seen.size}/${total}</div><div style="font-size:16px;margin-top:4px;color:#fff">${sp.name}</div><div style="font-style:italic;color:#9cc">${sp.sci}</div><div style="margin-top:6px;color:#bde">${sp.family || ''}${sp.size_cm ? ' · to ' + sp.size_cm + ' cm' : ''}${sp.school ? ' · ' + sp.school : ''}</div>${sp.note ? `<div style="margin-top:6px">${sp.note}</div>` : ''}${hz}`;
    card.style.opacity = '1'; hideAt = t + 7;
  }
  return { update, seen };
}
