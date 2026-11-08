#!/usr/bin/env python3
"""Headless stills for the status board (Playwright + the running game server on :8080).

    python research/cal-academy/scripts/board_shots.py            # -> boards/img/*.png (all)
    python research/cal-academy/scripts/board_shots.py planet skate   # a subset
Needs: the game served at http://localhost:8080 (preview server) and Playwright's chromium. Software GL is slow, so the
game canvas is read back with toDataURL (preserveDrawingBuffer) instead of a compositor screenshot.
"""
import base64, pathlib, sys, time
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT / 'boards' / 'img'; OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://localhost:8080'
ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl', '--no-sandbox']
WAIT_FS = "() => !!(window.__fs && window.__fs.splats && window.__fs.splats.state.ready)"
W, H = 1400, 900


def canvas_png(pg, name, frames=3):
    # let a few frames render, then read the canvas back
    for _ in range(frames):
        pg.evaluate("() => new Promise(r => requestAnimationFrame(() => r()))")
    data = pg.evaluate("() => document.getElementById('c').toDataURL('image/png')")
    (OUT / name).write_bytes(base64.b64decode(data.split(',', 1)[1])); print('shot', name, file=sys.stderr)


def setup(pg, extra=''):
    pg.goto(f'{BASE}/?admin=1&props=0&scale=1&pos=90,60,150&look=0,35,3{extra}', wait_until='load')
    pg.wait_for_function(WAIT_FS, timeout=600000)
    pg.evaluate("""() => { const F = window.__fs; F.player.update = () => F.player.state; F.setAdmin(true); F.pool.uniforms.uSteps.value = 64;
      F.layers.el.style.display = 'none'; document.getElementById('help').style.display = 'none'; }""")


def main():
    only = sys.argv[1:] or ['panel', 'planet', 'skate', 'whale', 'sheet']
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=ARGS)
        pg = br.new_page(viewport={'width': W, 'height': H}); pg.set_default_timeout(600000)
        pg.on('console', lambda m: print('[console]', m.text[:160], file=sys.stderr) if m.type == 'error' and '404' not in m.text else None)
        if any(k in only for k in ('panel', 'planet', 'skate')):
            setup(pg)
        if 'panel' in only:
            pg.evaluate("""() => { const F = window.__fs; F.layers.el.style.display = 'block'; F.camera.position.set(120, 70, 190); F.camera.lookAt(0, 0, 0); F.orbit.target.set(0, 0, 0); }""")
            for _ in range(3): pg.evaluate("() => new Promise(r => requestAnimationFrame(() => r()))")
            pg.screenshot(path=str(OUT / '11_admin_panel_sliders.png'), timeout=600000); print('shot panel', file=sys.stderr)
            pg.evaluate("""() => { const F = window.__fs; F.layers.el.style.display = 'none'; document.getElementById('help').style.display = 'none'; }""")
        if 'planet' in only:
            pg.evaluate("""() => { const F = window.__fs; F.scene.getObjectByName('lidar-site').visible = false; F.scene.getObjectByName('building').visible = false; F.pool.state.enabled = false;
              F.splats.group.visible = true; F.splats.state.visible = true; for (const e of F.splats.state.entries) if (e.mesh) e.mesh.visible = (e.space === 'lidar_building');
              F.splats.setFlip(true); F.splats.state.warp = true; F.splats.state.warpMix = 1; F.splats.uniforms.mix.value = 1; F.splats.touch();
              F.camera.position.set(90, 60, 150); F.camera.lookAt(0, 35, 3); F.orbit.target.set(0, 35, 3); }""")
            canvas_png(pg, '12_blob_planet_flipped.png', 4)
            pg.evaluate("() => { window.__fs.splats.setFlip(false); }"); canvas_png(pg, '13_blob_planet_unflipped.png', 3)
            pg.evaluate("""() => { const F = window.__fs; F.splats.setFlip(true); F.splats.state.warp = false; F.splats.state.warpMix = 0; F.splats.uniforms.mix.value = 0; F.splats.touch(); F.scene.getObjectByName('building').visible = true; F.scene.getObjectByName('lidar-site').visible = true; }""")
        if 'skate' in only:
            pg.evaluate("""() => { const F = window.__fs; for (const e of F.splats.state.entries) if (e.mesh) e.mesh.visible = false; F.water.state.level = -7.8; F.water.state.target = -7.8;
              F.pool.state.enabled = true; F.pool.setMode(2); F.pool.setTileTop(10.6); F.camera.position.set(-6, 7.5, 40); F.camera.lookAt(-30, 0, 10); F.orbit.target.set(-30, 0, 10); }""")
            canvas_png(pg, '18_skatepark_skin.png', 3)
            pg.evaluate("""() => { const F = window.__fs; F.camera.position.set(2, 26, 6); F.camera.lookAt(0, 0, 3); F.orbit.target.set(0, 0, 3); }""")
            canvas_png(pg, '19_skatepark_plan.png', 3)
        if 'whale' in only:
            pg2 = br.new_page(viewport={'width': W, 'height': H}); pg2.set_default_timeout(900000)
            pg2.goto(f'{BASE}/?admin=1&scale=1&pos=-60,2,40&look=-64,6,6', wait_until='load'); pg2.wait_for_function(WAIT_FS, timeout=900000)
            pg2.evaluate("""async () => { const F = window.__fs; const T = await import('three'); F.player.update = () => F.player.state; F.setAdmin(true); F.pool.uniforms.uSteps.value = 64;
              F.layers.el.style.display = 'none'; document.getElementById('help').style.display = 'none'; for (const e of F.splats.state.entries) if (e.mesh) e.mesh.visible = false;
              F.water.state.level = -7.8; F.water.state.target = -7.8; const w = F.scene.getObjectByName('prop:blue_whale_skeleton_nhm.glb'); if (w) { const b = new T.Box3().setFromObject(w); const c = b.getCenter(new T.Vector3());
              F.camera.position.set(c.x + 6, c.y - 4, c.z + 30); F.camera.lookAt(c); F.orbit.target.copy(c); } }""")
            canvas_png(pg2, '14_whale_in_hall.png', 4)
            pg2.evaluate("""() => { const F = window.__fs; F.camera.position.set(-20, 3, 70); F.camera.lookAt(-10, 1, 44); F.orbit.target.set(-10, 1, 44); }""")
            canvas_png(pg2, '15_entrance_props.png', 3)
        if 'sheet' in only:
            pg3 = br.new_page(viewport={'width': 1900, 'height': 1200}); pg3.set_default_timeout(1200000)
            pg3.goto(f'{BASE}/contact_sheet.html', wait_until='load')
            pg3.wait_for_function("() => window.__sheetDone === true", timeout=1200000); time.sleep(1)
            pg3.screenshot(path=str(OUT / '16_assets_contact_sheet.png'), full_page=True, timeout=600000); print('shot sheet', file=sys.stderr)
        br.close()


if __name__ == '__main__':
    main()
