#!/usr/bin/env python3
"""Headless stills for the status board (Playwright + the running game server on :8080).

    python research/cal-academy/scripts/board_shots.py            # -> boards/img/*.png
Needs: the game served at http://localhost:8080 (preview server) and Playwright's chromium.
"""
import json, pathlib, sys, time
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT / 'boards' / 'img'; OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://localhost:8080'
ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl', '--no-sandbox']

WAIT_FS = "() => !!(window.__fs && window.__fs.splats && window.__fs.splats.state.ready)"


def shot(page, name, w=1600, h=1000, full=False):
    page.set_viewport_size({'width': w, 'height': h}); time.sleep(0.5)
    page.screenshot(path=str(OUT / name), full_page=full); print('shot', name, file=sys.stderr)


def main():
    only = sys.argv[1:] or ['planet', 'whale', 'panel', 'sheet']
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=ARGS)
        pg = br.new_page(viewport={'width': 1600, 'height': 1000})
        pg.on('console', lambda m: print('[console]', m.type, m.text[:160], file=sys.stderr) if m.type in ('error',) else None)
        if 'planet' in only or 'whale' in only or 'panel' in only:
            pg.goto(f'{BASE}/?admin=1&nohud=0&pos=90,60,150&look=0,35,3', wait_until='load')
            pg.wait_for_function(WAIT_FS, timeout=240000); time.sleep(3)
            pg.evaluate("""() => { const F = window.__fs; F.player.update = () => F.player.state; F.setAdmin(true); }""")
        if 'panel' in only:
            pg.evaluate("""() => { const F = window.__fs; F.camera.position.set(120, 70, 190); F.camera.lookAt(0, 0, 0); F.orbit.target.set(0, 0, 0); }""")
            time.sleep(2); shot(pg, '11_admin_panel_sliders.png', 1600, 1000)
        if 'planet' in only:
            pg.evaluate("""() => { const F = window.__fs; F.layers.el.style.display = 'none'; document.getElementById('help').style.display = 'none';
              F.scene.getObjectByName('lidar-site').visible = false; F.scene.getObjectByName('building').visible = false; F.pool.state.enabled = false;
              F.splats.group.visible = true; F.splats.state.visible = true; for (const e of F.splats.state.entries) if (e.mesh) e.mesh.visible = (e.space === 'lidar_building');
              F.splats.setFlip(true); F.splats.state.warp = true; F.camera.position.set(90, 60, 150); F.camera.lookAt(0, 35, 3); F.orbit.target.set(0, 35, 3); }""")
            time.sleep(4); shot(pg, '12_blob_planet_flipped.png', 1600, 1000)
            pg.evaluate("""() => { const F = window.__fs; F.splats.setFlip(false); }"""); time.sleep(3); shot(pg, '13_blob_planet_unflipped.png', 1600, 1000)
            pg.evaluate("""() => { const F = window.__fs; F.splats.setFlip(true); F.scene.getObjectByName('building').visible = true; F.scene.getObjectByName('lidar-site').visible = true; }""")
        if 'whale' in only:
            pg.evaluate("""async () => { const F = window.__fs; const T = await import('three'); F.splats.state.warp = false; for (const e of F.splats.state.entries) if (e.mesh) e.mesh.visible = false;
              F.water.state.level = -7.8; F.water.state.target = -7.8; F.layers.el.style.display = 'none'; document.getElementById('help').style.display = 'none';
              const w = F.scene.getObjectByName('prop:blue_whale_skeleton_nhm.glb'); const b = new T.Box3().setFromObject(w); const c = b.getCenter(new T.Vector3());
              F.camera.position.set(c.x + 6, c.y - 4, c.z + 30); F.camera.lookAt(c); F.orbit.target.copy(c); }""")
            time.sleep(3); shot(pg, '14_whale_in_hall.png', 1600, 1000)
            pg.evaluate("""() => { const F = window.__fs; F.camera.position.set(-20, 3, 70); F.camera.lookAt(-10, 1, 44); F.orbit.target.set(-10, 1, 44); }""")
            time.sleep(3); shot(pg, '15_entrance_props.png', 1600, 1000)
        if 'sheet' in only:
            pg2 = br.new_page(viewport={'width': 1900, 'height': 1200})
            pg2.goto(f'{BASE}/contact_sheet.html', wait_until='load')
            pg2.wait_for_function("() => window.__sheetDone === true", timeout=600000); time.sleep(1)
            pg2.screenshot(path=str(OUT / '16_assets_contact_sheet.png'), full_page=True); print('shot sheet', file=sys.stderr)
        br.close()


if __name__ == '__main__':
    main()
