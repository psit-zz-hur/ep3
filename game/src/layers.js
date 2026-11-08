// ADMIN panel: LAYERS (every part of the model on/off, each splat scan on/off), PROPERTIES as sliders (pool skin fillet,
// tile line, tile size, water level, the planet), and the registration of the selected scan. White, left, like the
// other Admin panels; shown only in ADMIN mode.
import * as THREE from 'three';

export function buildLayers(spec, splats, opts = {}) {
  const el = document.createElement('div'); el.id = 'layers';
  el.style.cssText = 'position:fixed;left:0;top:0;bottom:0;width:280px;overflow:auto;background:#fff;color:#000;font:12px/1.5 ui-monospace,Menlo,monospace;padding:14px 16px;box-sizing:border-box;display:none;z-index:20;border-right:1px solid #ddd;';
  document.body.appendChild(el);
  const layers = spec.map((s) => ({ ...s, on: s.on !== false }));
  const props = opts.props || [];            // [{ group, label, get, set, min, max, step, unit, fmt, kind: 'range' | 'toggle' }]
  let selected = null; const syncers = []; let dragging = null;

  function objectsOf(l) { try { return (l.objects ? l.objects() : []).map((o) => (o && o.isObject3D ? o : o && o.mesh && o.mesh.isObject3D ? o.mesh : null)).filter(Boolean); } catch (e) { return []; } }
  function apply(l) { if (l.set) l.set(l.on); for (const o of objectsOf(l)) { o.visible = l.on; o.userData.layerOff = !l.on; } }
  function enforce() { for (const l of layers) if (!l.on) for (const o of objectsOf(l)) if (o.visible) o.visible = false; }

  function row(label, on, onChange, indent = 0, selectable = null) {
    const r = document.createElement('label'); r.style.cssText = `display:flex;gap:8px;align-items:center;padding-left:${indent * 14}px;cursor:pointer;`;
    const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = on; cb.style.margin = '0'; cb.addEventListener('change', () => onChange(cb.checked));
    const t = document.createElement('span'); t.textContent = label; t.style.flex = '1';
    if (selectable) { t.style.textDecoration = 'underline dotted'; t.addEventListener('click', (e) => { e.preventDefault(); selected = selectable; render(); }); }
    r.append(cb, t); return r;
  }
  function h(txt, top = 14) { const d = document.createElement('div'); d.textContent = txt; d.style.cssText = `letter-spacing:.2em;margin:${top}px 0 6px;font-weight:600;`; return d; }
  function sub(txt) { const d = document.createElement('div'); d.textContent = txt; d.style.cssText = 'margin:8px 0 2px;color:#444;letter-spacing:.1em;'; return d; }
  function fmtOf(p) { return p.fmt || ((v) => (Math.abs(v) >= 100 ? v.toFixed(0) : v.toFixed(2)) + (p.unit ? ' ' + p.unit : '')); }
  function slider(p) {
    const w = document.createElement('div'); w.style.cssText = 'margin:2px 0 4px;';
    const top = document.createElement('div'); top.style.cssText = 'display:flex;justify-content:space-between;gap:8px;';
    const lab = document.createElement('span'); lab.textContent = p.label; const val = document.createElement('span'); val.style.cssText = 'color:#000;min-width:64px;text-align:right;';
    top.append(lab, val);
    const i = document.createElement('input'); i.type = 'range'; i.min = p.min; i.max = p.max; i.step = p.step || 0.01; i.value = p.get();
    i.style.cssText = 'width:100%;margin:0;accent-color:#000;height:14px;';
    const f = fmtOf(p); val.textContent = f(+i.value);
    i.addEventListener('pointerdown', () => { dragging = i; }); i.addEventListener('pointerup', () => { dragging = null; });
    i.addEventListener('input', () => { const v = parseFloat(i.value); p.set(v); val.textContent = f(p.get()); });
    i.addEventListener('dblclick', () => { if (p.reset != null) { p.set(p.reset); i.value = p.get(); val.textContent = f(p.get()); } });
    syncers.push(() => { if (dragging === i) return; const v = p.get(); if (Math.abs(parseFloat(i.value) - v) > 1e-6) { i.value = v; val.textContent = f(v); } });
    w.append(top, i); return w;
  }
  function toggle(p) {
    const r = row(p.label, !!p.get(), (v) => p.set(v)); const cb = r.querySelector('input');
    syncers.push(() => { const v = !!p.get(); if (cb.checked !== v) cb.checked = v; }); return r;
  }
  function button(p) {
    const b = document.createElement('button'); b.textContent = p.label; b.style.cssText = 'font:inherit;padding:3px 8px;border:1px solid #000;background:#fff;color:#000;cursor:pointer;margin:0 6px 6px 0;';
    b.addEventListener('click', () => { p.run(); setTimeout(() => { for (const s of syncers) s(); }, 50); }); return b;
  }
  function num(label, value, step, onInput) {
    const w = document.createElement('label'); w.style.cssText = 'display:flex;gap:8px;align-items:center;';
    const t = document.createElement('span'); t.textContent = label; t.style.width = '28px';
    const i = document.createElement('input'); i.type = 'number'; i.step = step; i.value = (+value).toFixed(2); i.style.cssText = 'flex:1;font:inherit;padding:1px 4px;border:1px solid #bbb;background:#fff;color:#000;';
    i.addEventListener('input', () => { const v = parseFloat(i.value); if (!Number.isNaN(v)) onInput(v); });
    w.append(t, i); return w;
  }

  function render() {
    el.textContent = ''; syncers.length = 0;
    el.appendChild(h('LAYERS', 0));
    for (const l of layers) el.appendChild(row(l.name, l.on, (v) => { l.on = v; apply(l); }));
    if (splats) {
      const g = splats.state; el.appendChild(row('SPLATS (Scaniverse)', g.visible, () => { splats.toggle(); render(); }));
      for (const e of g.entries) {
        if (!e.mesh) { const d = document.createElement('div'); d.style.cssText = 'padding-left:14px;color:#999;'; d.textContent = `${e.space || e.file} · ${e.missing ? 'file missing' : 'off'}`; el.appendChild(d); continue; }
        el.appendChild(row(e.space || e.file, e.mesh.visible, (v) => { e.mesh.visible = v; }, 1, e));
      }
    }
    // PROPERTIES: sliders by group
    if (props.length) {
      el.appendChild(h('PROPERTIES'));
      let grp = null, btnRow = null;
      for (const p of props) {
        if (p.group !== grp) { grp = p.group; el.appendChild(sub(grp)); btnRow = null; }
        if (p.kind === 'button') { if (!btnRow) { btnRow = document.createElement('div'); btnRow.style.cssText = 'display:flex;flex-wrap:wrap;margin:2px 0;'; el.appendChild(btnRow); } btnRow.appendChild(button(p)); continue; }
        btnRow = null;
        el.appendChild(p.kind === 'toggle' ? toggle(p) : slider(p));
      }
      const hint = document.createElement('div'); hint.style.cssText = 'color:#888;margin-top:4px;'; hint.textContent = 'double-click a slider to reset it'; el.appendChild(hint);
    }
    // registration of the selected scan
    if (splats) {
      el.appendChild(h('REGISTRATION'));
      if (!selected || !selected.mesh) { const d = document.createElement('div'); d.style.color = '#666'; d.textContent = 'click a scan name above to edit its registration'; el.appendChild(d); }
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
  return { el, layers, render, enforce, sync: () => { for (const s of syncers) s(); }, show: (v) => { el.style.display = v ? 'block' : 'none'; if (v) render(); }, get selected() { return selected; } };
}
