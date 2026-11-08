#!/usr/bin/env python3
"""The status board: one 3840 x 2160 image, images first, a line of text under each. HTML -> PNG with Playwright.

    python research/cal-academy/scripts/build_board.py          # -> boards/CALACADEMY_BOARD_<date>A.html + .png
"""
import datetime, html, json, pathlib, subprocess, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[3]; B = ROOT / 'boards'; IMG = B / 'img'


def img(name, cap, big=False):
    p = IMG / name
    if not p.exists(): return ''
    return f'<figure class="{"big" if big else ""}"><img src="img/{name}"><figcaption>{html.escape(cap)}</figcaption></figure>'


def main():
    tag = datetime.date.today().strftime('%Y_%m_%d') + 'A'
    log = subprocess.run(['git', 'log', '--format=%h %s', '-12'], cwd=ROOT, capture_output=True, text=True).stdout.strip().splitlines()
    commits = [l.split(' ', 1) for l in log]
    props = sorted((ROOT / 'CALACADEMY_3D_ASSETS').glob('*.glb')) if (ROOT / 'CALACADEMY_3D_ASSETS').exists() else []
    lidar = ROOT / 'data' / 'cal-academy' / 'lidar2023'
    laz = sorted(lidar.glob('*.laz')) if lidar.exists() else []
    ept = lidar / 'ept_site_game.ply'
    rh = sorted((ROOT / 'rhino').glob('*.3dm'))
    renders = ROOT / 'research' / 'cal-academy' / 'renders'
    for f in ['cas_lidar_dsm_hillshade.png', 'cas_lidar_oblique.png', 'cas_roof_closeup.png', 'cas_change_2010_2023.png']:
        if (renders / f).exists() and not (IMG / f).exists(): (IMG / f).write_bytes((renders / f).read_bytes())
    cs = ROOT / 'research' / 'cal-academy' / 'contact-sheets'
    for f in ['09_3d_assets.jpg', '08_interior_model.jpg']:
        if (cs / f).exists() and not (IMG / ('cs_' + f)).exists(): (IMG / ('cs_' + f)).write_bytes((cs / f).read_bytes())

    status = [
        ('DONE', 'ep3 repo found + cloned', 'branch claude/vibrant-hypatia-fdw8wx · Documents\\Claude\\ep3'),
        ('DONE', 'game runs · three r187 + Spark 2.4', '35–49 fps on the Intel Arc'),
        ('DONE', 'ADMIN mode · LAYERS · sliders', '` key · orbit, fly through walls, physics off'),
        ('DONE', 'splats.js + BLOB PLANET (flipped)', 'manifest frames game / utm10n / scan'),
        ('DONE', 'splat cut at the footprint', 'lidar_building · lidar_site'),
        ('DONE', 'Sketchfab · 16 props in the halls', 'CC BY ×14 · CC BY-NC-SA ×2 (whale)'),
        ('DONE', 'skatepark skin + supergraphics', 'I cycles tile / concrete / skatepark'),
        ('DONE', 'Rhino A · mesh + massing + splats', 'CALACADEMY_SITE_2026_11_07A.3dm'),
        ('DONE', 'Rhino B · + raw point cloud (EPT)', 'POINTCLOUD layer, 1.5 M pts'),
        ('DONE', 'all 3D assets in one folder', 'CALACADEMY_3D_ASSETS · %d GLB' % len(props)),
        ('DONE', 'lidar DSM mesh → THE VIEW [1]', 'OBJ + PLY + frame JSON, sent'),
        ('DONE', 'dataset census · files 15 + 15b', 'two sessions, pushed'),
        ('RUNNING', 'laptop-bootstrap.sh', 'USGS throttles to 128 KB/s; tile 2 of 6'),
        ('DONE', 'ADMIN panel v3 · Rhino model', 'Viewport / Layers / Properties: selection'),
        ('DONE', 'camera: FOV, axon, circular 360°', 'Camera and Dome rows'),
        ('RUNNING', 'planet of the park quadrant', 'THE TERRITORY proof live · rasters in prep'),
        ('DONE', 'RPBW drawings into Rhino D', '20 raster planes + 19 traced vector layers; sections first'),
        ('DONE', 'park planet rasters a-e for THE TERRITORY', 'exports/territory, 1 m DSM, 5 m DTM, NAIP, water, labels'),
        ('BRYAN', 'Scaniverse scans off the phone', 'SPZ + PLY → Downloads → ingest_captures.py'),
        ('BRYAN', '3D Warehouse massing model', 'login, save as game/assets/cas_3dwarehouse.glb'),
    ]
    sym = {'DONE': '■', 'RUNNING': '◐', 'BRYAN': '□'}
    rows = ''.join(f'<tr class="{s.lower()}"><td class="m">{sym[s]}</td><td>{html.escape(t)}</td><td class="d">{html.escape(d)}</td></tr>' for s, t, d in status)
    assets_rows = ''.join(f'<li>{html.escape(p.stem)} <span>{p.stat().st_size // 1_000_000} MB</span></li>' for p in props)
    top10 = [('Botany 1.9 M · CC0', 'Living Roof: the nine natives'), ('Herpetology 320 k · 221 k images', 'image wall, Rainforest / Swamp'), ('Ichthyology 221 k · 15 k Philippine', 'Philippine reef tank, by depth'), ('Ornithology · 692 window-strike birds', 'the facades themselves'), ('iNaturalist place 54088', 'live park observations on the roof'), ('AntWeb 917 k · CC BY', 'ant swarm, rainforest dome'), ('Invertebrates 285 k', 'reef and tide-pool halls'), ('Galápagos 1905-06', 'the collection that survived 1906'), ('Geology 24 k · CC BY-NC', 'Shake House'), ('Mammalogy 40 k', 'African Hall')]
    top_rows = ''.join(f'<li><b>{html.escape(a)}</b> {html.escape(b)}</li>' for a, b in top10)
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>Cal Academy board</title>
<style>
  html,body{{margin:0;background:#fff;color:#000;font:15px/1.35 ui-monospace,Menlo,Consolas,monospace}}
  .board{{width:3840px;height:2160px;position:relative;overflow:hidden;padding:48px 56px;box-sizing:border-box}}
  h1{{font-size:44px;letter-spacing:.25em;margin:0 0 6px;font-weight:600}}
  .sub{{color:#555;letter-spacing:.12em;margin-bottom:28px}}
  .grid{{display:grid;grid-template-columns:repeat(12,1fr);grid-auto-rows:minmax(0,1fr);gap:22px;height:1930px}}
  figure{{margin:0;min-height:0;height:100%;position:relative;background:#f3f3f3;overflow:hidden;border:1px solid #ddd}}
  figure img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}}
  figcaption{{position:absolute;left:0;right:0;bottom:0;background:#fff;color:#000;padding:6px 10px;font-size:14px;border-top:1px solid #ddd}}
  .c3{{grid-column:span 3}} .c4{{grid-column:span 4}} .c6{{grid-column:span 6}} .c2{{grid-column:span 2}} .r2{{grid-row:span 2}} .r3{{grid-row:span 3}} .r4{{grid-row:span 4}}
  .panel{{min-height:0;border:1px solid #ddd;padding:14px 18px;overflow:hidden;background:#fff}}
  .panel h2{{font-size:16px;letter-spacing:.25em;margin:0 0 10px;font-weight:600}}
  table{{border-collapse:collapse;width:100%}} td{{padding:1px 6px;font-size:13px;vertical-align:top;border-bottom:1px solid #eee}} td.m{{width:22px;font-size:18px}} td.d{{color:#666}}
  tr.running td.m{{color:#2c92ff}} tr.bryan td.m{{color:#ff4400}} tr.bryan td{{color:#ff4400}}
  ul{{margin:0;padding-left:0;list-style:none;columns:2;column-gap:18px}} li{{break-inside:avoid;padding:2px 0;border-bottom:1px solid #eee}} li span{{color:#888;float:right}}
  .top ul{{columns:1}} .top b{{display:inline-block;min-width:330px}}
  .keys{{columns:2;column-gap:24px;color:#333}} .keys div{{padding:2px 0}} .keys b{{display:inline-block;min-width:70px;font-weight:600}}
  .commits li{{font-size:13px;color:#444}} .commits b{{color:#000;margin-right:8px}}
  .foot{{position:absolute;left:56px;right:56px;bottom:30px;color:#666;font-size:13px;display:flex;justify-content:space-between}}
</style></head><body><div class="board">
<h1>FREESWIM FRIDAYS · CAL ACADEMY · STATUS BOARD</h1>
<div class="sub">laptop session, 7 Nov 2026, 18:00–19:40 · repo psit-zz-hur/ep3 · branch claude/vibrant-hypatia-fdw8wx · {len(commits)} commits tonight · Claude (Fable 5.1) for Bryan</div>
<div class="grid">
  <div class="c4 r2">{img('12_blob_planet_flipped.png', 'BLOB PLANET, flipped: the lidar splat of the building through a sphere inversion (centre 60 m up, R 60), roof on top · X warp, Shift+X flip', True)}</div>
  <div class="c4 r2">{img('09_ojos_blob_planet_upside_down.jpg', 'the same at 18:58 before the flip (your screenshot): ring up, roof hanging under')}</div>
  <div class="c4 r2">{img('11_admin_panel_sliders.png', 'ADMIN mode (` key): LAYERS, every part on/off · PROPERTIES as sliders · REGISTRATION of a scan')}</div>
  <div class="c3 r2">{img('18_skatepark_skin.png', 'SKATEPARK skin (I ×2): troweled concrete, canary hatched routes, crosshatched stand-here discs, painted coping')}</div>
  <div class="c3 r2">{img('19_skatepark_plan.png', 'the three laps seen from above the piazza: east lap under the whale, west lap to African Hall, north run past T. rex')}</div>
  <div class="c6 r2">{img('14_whale_in_hall.png', 'NHM London blue whale "Hope" (CC BY-NC-SA) standing in over Giants of Land and Sea; the procedural whale hides')}</div>
  <div class="c6 r2">{img('16_assets_contact_sheet.png', 'CONTACT SHEET: all 16 Sketchfab props + the two lidar splats, live at localhost:8080/contact_sheet.html · files in CALACADEMY_3D_ASSETS/')}</div>
  <div class="c3 r2">{img('20_skin_axon_from_outside.png', 'the skins alone in axonometric from outside the museum: lidar, building and sky layers off · Camera › axon SW')}</div>
  <div class="c3 r2">{img('21_planet_proof_territory.jpg', 'THE TERRITORY’s first planet of the Academy tile (our lidar PLY + frame): sphere, octa, icosa · live at 127.0.0.1:8803/?mode=trial · the quadrant rasters are in preparation')}</div>
  <div class="c3 r2">{img('22_rpbw_drawings_registered.png', 'RPBW drawings registered into Rhino D: roof plan traced over the massing and dome circles; E-W section on the dome spheres; every public sheet is raster-only, so vectors are traces')}</div>
  <div class="c6 r2 panel"><h2>STATUS</h2><div style="columns:2;column-gap:24px;font-size:12px"><table>{rows}</table></div></div>
  <div class="c3 r2 panel"><h2>3D ASSETS · ONE FOLDER</h2><ul>{assets_rows}<li>SPLAT lidar_building / lidar_site (synthetic) <span>PLY</span></li><li>LIDAR_DSM_mesh_0p5m_Yup <span>44 MB PLY</span></li><li>POINTCLOUD lidar2023 site <span>{'ready' if ept.exists() else 'fetching'}</span></li><li>CALACADEMY_SITE A / B <span>3dm</span></li></ul></div>
<div class="foot"><span>game: localhost:8080/?admin=1 · contact sheet: /contact_sheet.html · Rhino: ep3\\rhino\\ · assets: ep3\\CALACADEMY_3D_ASSETS\\ · docs: HANDOFF.md §5b</span><span>■ done · ◐ running · □ needs Bryan's hands</span></div>
</div></body></html>"""
    out = B / f'CALACADEMY_BOARD_{tag}.html'; out.write_text(page, encoding='utf-8')
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True); pg = br.new_page(viewport={'width': 3840, 'height': 2160}, device_scale_factor=1)
        pg.goto(out.resolve().as_uri(), wait_until='load'); pg.wait_for_timeout(1500)
        png = out.with_suffix('.png'); pg.screenshot(path=str(png), full_page=False); br.close()
    print('wrote', out, png)


if __name__ == '__main__':
    main()
