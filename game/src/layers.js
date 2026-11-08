// ADMIN panel, on the Rhino model: a LAYERS list (On tick + name per part of the scene, splat scans as child rows), a
// short VIEWPORT list (Camera, Dome, Render), and "Properties: <selection>" showing only the selected row's controls.
// Nothing is drawn over the viewport in ADMIN; the status line lives at the foot of the panel. Tokens and type follow
// the PROVOCATIONS kit (12 px Arial/Helvetica, selected row #c3dcff, border #c8cbd1, hairline #e3e5e9, accent #2c92ff,
// header rows #f2e8dc); width 300 px and three fixed sections are this tool's own choices (rapid prototyping, no folds).
import * as THREE from 'three';

const CSS = `
#layers{position:fixed;left:0;top:0;bottom:0;width:300px;background:#fff;color:#000;font:12px/1.4 Arial,Helvetica,sans-serif;display:none;z-index:20;border-right:1px solid #c8cbd1;box-sizing:border-box;flex-direction:column}
#layers .ph{position:sticky;top:0;background:#f2e8dc;border-top:1px solid #d9d4cb;border-bottom:1px solid #d9d4cb;padding:4px 8px;letter-spacing:.04em}
#layers .ph span{color:#555;margin-left:6px}
#layers .scroll{flex:1;overflow:auto}
#layers .row{display:flex;align-items:center;gap:6px;height:22px;padding:0 8px;cursor:pointer;border-bottom:1px solid #eef0f3}
#layers .row:hover{background:#f4f5f7}
#layers .row.sel{background:#c3dcff}
#layers .row input{margin:0;accent-color:#2c92ff;flex:none}
#layers .row .n{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#layers .row.root .n{font-weight:700;letter-spacing:.04em}
#layers .row.child{padding-left:28px}
#layers .row .dim{color:#555}
#layers .props{border-top:1px solid #c8cbd1;max-height:55%;overflow:auto;display:flex;flex-direction:column}
#layers .props .body{padding:4px 8px 8px}
#layers .pr{display:grid;grid-template-columns:1fr 92px;align-items:center;min-height:24px;padding:0 0 0 4px;border-bottom:1px solid #e3e5e9;gap:8px}
#layers .pr .v{text-align:right;color:#000;white-space:nowrap}
#layers .track{padding:2px 4px 6px;border-bottom:1px solid #e3e5e9}
#layers .track input{width:100%;margin:0;accent-color:#2c92ff;height:12px}
#layers .tg{display:flex;align-items:center;gap:7px;min-height:24px;padding:0 4px;border-bottom:1px solid #e3e5e9}
#layers .tg input{margin:0;accent-color:#2c92ff}
#layers .btns{display:flex;flex-wrap:wrap;gap:6px;padding:6px 4px}
#layers button{font:inherit;padding:2px 8px;border:1px solid #c8cbd1;background:#fff;color:#000;cursor:pointer;border-radius:2px}
#layers button:hover{border-color:#2c92ff;color:#2c92ff}
#layers .num{display:grid;grid-template-columns:1fr 92px;align-items:center;min-height:24px;padding:0 0 0 4px;border-bottom:1px solid #e3e5e9;gap:8px}
#layers .num input{font:inherit;padding:1px 4px;border:1px solid #c8cbd1;background:#fff;color:#000;width:100%;box-sizing:border-box}
#layers .note{color:#555;padding:4px 4px 2px}
#layers .status{border-top:1px solid #c8cbd1;background:#eaebef;padding:6px 8px;color:#555;white-space:pre-line;min-height:30px}
`;

export function buildLayers(spec, splats, opts = {}) {
  if (!document.getElementById('layers-css')) { const st = document.createElement('style'); st.id = 'layers-css'; st.textContent = CSS; document.head.appendChild(st); }
  const el = document.createElement('div'); el.id = 'layers';
  const scroll = document.createElement('div'); scroll.className = 'scroll'; const propsEl = document.createElement('div'); propsEl.className = 'props'; const statusEl = document.createElement('div'); statusEl.className = 'status';
  el.append(scroll, propsEl, statusEl); document.body.appendChild(el);
  const viewport = (spec.viewport || []).map((r) => ({ ...r, kind: 'viewport' }));
  const layers = (spec.layers || []).map((r) => ({ ...r, on: r.on !== false }));
  let selected = viewport[0] || layers[0]; const syncers = []; let dragging = null;

  function objectsOf(l) { try { return (l.objects ? l.objects() : []).map((o) => (o && o.isObject3D ? o : o && o.mesh && o.mesh.isObject3D ? o.mesh : null)).filter(Boolean); } catch (e) { return []; } }
  function apply(l) { if (l.set) l.set(l.on); for (const o of objectsOf(l)) { o.visible = l.on; o.userData.layerOff = !l.on; } }
  function enforce() { for (const l of layers) if (!l.on) for (const o of objectsOf(l)) if (o.visible) o.visible = false; }
  function fmtOf(p) { return p.fmt || ((v) => (Math.abs(v) >= 100 ? v.toFixed(0) : v.toFixed(2)) + (p.unit ? ' ' + p.unit : '')); }
  function ph(txt, sub) { const d = document.createElement('div'); d.className = 'ph'; d.textContent = txt; if (sub) { const s = document.createElement('span'); s.textContent = sub; d.appendChild(s); } return d; }

  function row(r, child = false, root = false) {
    const d = document.createElement('div'); d.className = 'row' + (child ? ' child' : '') + (root ? ' root' : '') + (r === selected ? ' sel' : '');
    if (r.kind !== 'viewport') {
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = r.on; cb.title = 'On';
      cb.addEventListener('click', (e) => e.stopPropagation()); cb.addEventListener('change', () => { r.on = cb.checked; apply(r); });
      d.appendChild(cb); syncers.push(() => { if (r.get && cb.checked !== !!r.get()) cb.checked = !!r.get(); });
    }
    const n = document.createElement('span'); n.className = 'n' + (r.dim ? ' dim' : ''); n.textContent = r.name; d.appendChild(n);
    d.addEventListener('click', () => { selected = r; renderLists(); renderProps(); });
    return d;
  }
  function slider(p) {
    const frag = document.createDocumentFragment();
    const pr = document.createElement('div'); pr.className = 'pr'; const lab = document.createElement('span'); lab.textContent = p.label; const val = document.createElement('span'); val.className = 'v'; pr.append(lab, val);
    const tr = document.createElement('div'); tr.className = 'track'; const i = document.createElement('input'); i.type = 'range'; i.min = p.min; i.max = p.max; i.step = p.step || 0.01; i.value = p.get(); i.title = 'double-click resets'; tr.appendChild(i);
    const f = fmtOf(p); val.textContent = f(+i.value);
    i.addEventListener('pointerdown', () => { dragging = i; }); i.addEventListener('pointerup', () => { dragging = null; });
    i.addEventListener('input', () => { const v = parseFloat(i.value); p.set(v); val.textContent = f(p.get()); });
    i.addEventListener('dblclick', () => { if (p.reset != null) { p.set(p.reset); i.value = p.get(); val.textContent = f(p.get()); } });
    syncers.push(() => { if (dragging === i) return; const v = p.get(); if (Math.abs(parseFloat(i.value) - v) > 1e-6) { i.value = v; val.textContent = f(v); } });
    frag.append(pr, tr); return frag;
  }
  function toggle(p) {
    const r = document.createElement('label'); r.className = 'tg'; const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = !!p.get(); cb.addEventListener('change', () => p.set(cb.checked));
    const t = document.createElement('span'); t.textContent = p.label; r.append(cb, t); syncers.push(() => { const v = !!p.get(); if (cb.checked !== v) cb.checked = v; }); return r;
  }
  function button(p) { const b = document.createElement('button'); b.textContent = p.label; b.addEventListener('click', () => { p.run(); setTimeout(sync, 50); }); return b; }
  function num(label, value, step, onInput) {
    const w = document.createElement('label'); w.className = 'num'; const t = document.createElement('span'); t.textContent = label;
    const i = document.createElement('input'); i.type = 'number'; i.step = step; i.value = (+value).toFixed(2); i.addEventListener('input', () => { const v = parseFloat(i.value); if (!Number.isNaN(v)) onInput(v); }); w.append(t, i); return w;
  }
  function controls(container, props) {
    let btnRow = null;
    for (const p of props || []) {
      if (p.kind === 'button') { if (!btnRow) { btnRow = document.createElement('div'); btnRow.className = 'btns'; container.appendChild(btnRow); } btnRow.appendChild(button(p)); continue; }
      btnRow = null;
      if (p.kind === 'note') { const d = document.createElement('div'); d.className = 'note'; d.textContent = p.label; container.appendChild(d); continue; }
      container.appendChild(p.kind === 'toggle' ? toggle(p) : slider(p));
    }
  }
  function registration(e) {
    const m = e.mesh; const eu = new THREE.Euler().setFromQuaternion(m.quaternion, 'YXZ'); const frag = document.createDocumentFragment();
    frag.appendChild(num('X (m)', m.position.x, 0.5, (v) => { m.position.x = v; })); frag.appendChild(num('Y (m)', m.position.y, 0.25, (v) => { m.position.y = v; })); frag.appendChild(num('Z (m)', m.position.z, 0.5, (v) => { m.position.z = v; }));
    frag.appendChild(num('rotation Y (°)', THREE.MathUtils.radToDeg(eu.y), 1, (v) => { m.quaternion.setFromEuler(new THREE.Euler(eu.x, THREE.MathUtils.degToRad(v), eu.z, 'YXZ')); }));
    frag.appendChild(num('scale', m.scale.x, 0.01, (v) => { if (v > 0) m.scale.setScalar(v); }));
    const br = document.createElement('div'); br.className = 'btns'; const b = document.createElement('button'); b.textContent = 'copy manifest with this registration';
    b.addEventListener('click', async () => { const txt = splats.exportManifest(); try { await navigator.clipboard.writeText(txt); b.textContent = 'copied · paste over assets/splats/manifest.json'; } catch (err) { b.textContent = 'printed to the console'; } });
    br.appendChild(b); frag.appendChild(br); const note = document.createElement('div'); note.className = 'note'; note.textContent = `frame ${e.frame || 'scan'} · game frame: X long axis (east = -X), Y up from the main floor, Z short axis (+Z north)`; frag.appendChild(note);
    return frag;
  }

  function renderLists() {
    scroll.textContent = ''; syncers.length = 0;
    if (viewport.length) { scroll.appendChild(ph('Viewport')); for (const r of viewport) scroll.appendChild(row(r)); }
    scroll.appendChild(ph('Layers'));
    for (const l of layers) {
      scroll.appendChild(row(l, false, !!l.children));
      if (l.children) for (const c of l.children()) scroll.appendChild(row(c, true));
    }
    if (opts.footer) { const f = document.createElement('div'); f.className = 'note'; f.textContent = opts.footer; scroll.appendChild(f); }
  }
  function renderProps() {
    propsEl.textContent = ''; propsEl.appendChild(ph('Properties:', selected ? selected.name : 'Viewport'));
    const body = document.createElement('div'); body.className = 'body'; propsEl.appendChild(body);
    if (!selected) return;
    if (selected.scan && selected.scan.mesh) body.appendChild(registration(selected.scan));
    controls(body, typeof selected.props === 'function' ? selected.props() : selected.props);
    if (!selected.props && !selected.scan) { const d = document.createElement('div'); d.className = 'note'; d.textContent = 'no properties on this layer yet'; body.appendChild(d); }
  }
  function sync() { for (const s of syncers) s(); }
  function render() { renderLists(); renderProps(); }
  render();
  return { el, layers, viewport, render, enforce, sync, status: (txt) => { statusEl.textContent = txt; }, select: (name) => { const r = [...viewport, ...layers].find((x) => x.name === name); if (r) { selected = r; render(); } },
    show: (v) => { el.style.display = v ? 'flex' : 'none'; if (v) render(); }, get selected() { return selected; } };
}
