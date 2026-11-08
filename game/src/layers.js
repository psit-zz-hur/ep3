// ADMIN panel: LAYERS (every part of the model on/off, each splat scan on/off) and PROPERTIES of the selected scan
// (position, rotation, scale in the game frame; copies the manifest with the result). White, left, like the other
// Admin panels; shown only in ADMIN mode.
import * as THREE from 'three';

export function buildLayers(spec, splats, opts = {}) {
  const el = document.createElement('div'); el.id = 'layers';
  el.style.cssText = 'position:fixed;left:0;top:0;bottom:0;width:260px;overflow:auto;background:#fff;color:#000;font:12px/1.5 ui-monospace,Menlo,monospace;padding:14px 16px;box-sizing:border-box;display:none;z-index:20;border-right:1px solid #ddd;';
  document.body.appendChild(el);
  const layers = spec.map((s) => ({ ...s, on: s.on !== false }));
  let selected = null;

  function objectsOf(l) { try { return (l.objects ? l.objects() : []).filter(Boolean); } catch (e) { return []; } }
  function apply(l) { if (l.set) l.set(l.on); for (const o of objectsOf(l)) { o.visible = l.on; o.userData.layerOff = !l.on; } }
  function enforce() { for (const l of layers) if (!l.on) for (const o of objectsOf(l)) if (o.visible) o.visible = false; }

  function row(label, on, onChange, indent = 0, selectable = null) {
    const r = document.createElement('label'); r.style.cssText = `display:flex;gap:8px;align-items:center;padding-left:${indent * 14}px;cursor:pointer;`;
    const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = on; cb.style.margin = '0'; cb.addEventListener('change', () => onChange(cb.checked));
    const t = document.createElement('span'); t.textContent = label; t.style.flex = '1';
    if (selectable) { t.style.textDecoration = 'underline dotted'; t.addEventListener('click', (e) => { e.preventDefault(); selected = selectable; render(); }); }
    r.append(cb, t); return r;
  }
  function h(txt) { const d = document.createElement('div'); d.textContent = txt; d.style.cssText = 'letter-spacing:.2em;margin:14px 0 6px;font-weight:600;'; return d; }
  function num(label, value, step, onInput) {
    const w = document.createElement('label'); w.style.cssText = 'display:flex;gap:8px;align-items:center;';
    const t = document.createElement('span'); t.textContent = label; t.style.width = '28px';
    const i = document.createElement('input'); i.type = 'number'; i.step = step; i.value = (+value).toFixed(2); i.style.cssText = 'flex:1;font:inherit;padding:1px 4px;border:1px solid #bbb;background:#fff;color:#000;';
    i.addEventListener('input', () => { const v = parseFloat(i.value); if (!Number.isNaN(v)) onInput(v); });
    w.append(t, i); return w;
  }

  function render() {
    el.textContent = '';
    const title = h('LAYERS'); title.style.marginTop = '0'; el.appendChild(title);
    for (const l of layers) el.appendChild(row(l.name, l.on, (v) => { l.on = v; apply(l); }));
    // splats: the group, then one row per scan
    if (splats) {
      const g = splats.state; const gRow = row('SPLATS (Scaniverse)', g.visible, () => { splats.toggle(); render(); }); el.appendChild(gRow);
      for (const e of g.entries) {
        if (!e.mesh) { const d = document.createElement('div'); d.style.cssText = 'padding-left:14px;color:#999;'; d.textContent = `${e.space || e.file} · ${e.missing ? 'file missing' : 'off'}`; el.appendChild(d); continue; }
        el.appendChild(row(e.space || e.file, e.mesh.visible, (v) => { e.mesh.visible = v; }, 1, e));
      }
      el.appendChild(h('PROPERTIES'));
      if (!selected || !selected.mesh) { const d = document.createElement('div'); d.style.color = '#666'; d.textContent = 'click a scan name to edit its registration'; el.appendChild(d); }
      else {
        const m = selected.mesh; const e = new THREE.Euler().setFromQuaternion(m.quaternion, 'YXZ');
        const name = document.createElement('div'); name.textContent = `${selected.space || selected.file} · frame ${selected.frame || 'scan'}`; name.style.marginBottom = '4px'; el.appendChild(name);
        el.appendChild(num('X', m.position.x, 0.5, (v) => { m.position.x = v; }));
        el.appendChild(num('Y', m.position.y, 0.25, (v) => { m.position.y = v; }));
        el.appendChild(num('Z', m.position.z, 0.5, (v) => { m.position.z = v; }));
        el.appendChild(num('RY°', THREE.MathUtils.radToDeg(e.y), 1, (v) => { const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(e.x, THREE.MathUtils.degToRad(v), e.z, 'YXZ')); m.quaternion.copy(q); }));
        el.appendChild(num('S', m.scale.x, 0.01, (v) => { if (v > 0) m.scale.setScalar(v); }));
        const b = document.createElement('button'); b.textContent = 'copy manifest with this registration'; b.style.cssText = 'margin-top:8px;font:inherit;padding:4px 8px;border:1px solid #000;background:#fff;color:#000;cursor:pointer;';
        b.addEventListener('click', async () => { const txt = splats.exportManifest(); try { await navigator.clipboard.writeText(txt); b.textContent = 'copied · paste over assets/splats/manifest.json'; } catch (err) { b.textContent = 'printed to the console (clipboard blocked)'; } });
        el.appendChild(b);
        const note = document.createElement('div'); note.style.cssText = 'color:#666;margin-top:6px;'; note.textContent = 'metres in the game frame: X long axis (east = -X), Y up from the main floor, Z short axis (+Z north).'; el.appendChild(note);
      }
    }
    if (opts.footer) { const f = document.createElement('div'); f.style.cssText = 'color:#666;margin-top:16px;'; f.textContent = opts.footer; el.appendChild(f); }
  }
  render();
  return { el, layers, render, enforce, show: (v) => { el.style.display = v ? 'block' : 'none'; if (v) render(); }, get selected() { return selected; } };
}
