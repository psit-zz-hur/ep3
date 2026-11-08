#!/usr/bin/env python3
"""One image: what is running, done, or waiting on Bryan, with the latest picture per stream. Images instead of prose.
    python -X utf8 research/cal-academy/scripts/status_card.py  -> boards/CALACADEMY_STATUS_CARD_<time>.png
"""
import datetime, pathlib, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[3]; B = ROOT / 'boards'; IMG = B / 'img'
ROWS = [  # (state, label, image)  state: done | running | bryan
    ('done', 'Collecting Disc mockup (THE DIAGRAM)', B / 'CALACADEMY_DIAGRAM_MOCKUP_2026_11_07B.png'),
    ('done', 'Golden Gate Planet v0 (THE TERRITORY)', ROOT / 'exports' / 'CALACADEMY_PLANET_SHEET_2026_11_07B.jpg'),
    ('done', 'RPBW drawings in Rhino D / E', IMG / '22_rpbw_drawings_registered.png'),
    ('done', 'Sketchfab props + assets folder', IMG / '16_assets_contact_sheet.png'),
    ('running', 'FFT water for the flood', IMG / '24_ocean_surface.png'),
    ('running', 'whole-park core 1 m + rim + buses (GTFS)', None),
    ('running', 'pre-colonial habitat + elk herds', IMG / '23_precolonial_habitat.png'),
    ('running', 'Outside Lands + Carville research', IMG / '26_outside_lands_carville_contact.png'),
    ('running', 'whale tracks, sprites, transit overrides', IMG / '27_sprites_proof.png'),
    ('running', 'planet v1 v2 v3 bakes (THE TERRITORY)', None),
    ('bryan', 'Scaniverse: which two scans are the savannah', None),
    ('bryan', 'Rhino: run skp_register_v3.py (one line)', None),
    ('bryan', 'disc mockup: your marks', None),
]
INK = {'done': (0, 0, 0), 'running': (44, 146, 255), 'bryan': (255, 68, 0)}


def main():
    W, H = 1600, 90 + 96 * len(ROWS) + 40
    im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype('arial.ttf', 26); fs = ImageFont.truetype('arial.ttf', 20); fb = ImageFont.truetype('arialbd.ttf', 30)
    except Exception: f = fs = fb = ImageFont.load_default()
    now = datetime.datetime.now().strftime('%H:%M')
    d.text((40, 28), f'STATUS · {now}', font=fb, fill='black'); d.line((40, 72, W - 40, 72), fill='black', width=2)
    y = 90
    for state, label, img in ROWS:
        c = INK[state]
        if state == 'done': d.rectangle((40, y + 34, 62, y + 56), fill=c)
        elif state == 'running': d.rectangle((40, y + 34, 62, y + 56), outline=c, width=3); d.rectangle((40, y + 34, 51, y + 56), fill=c)
        else: d.rectangle((40, y + 34, 62, y + 56), outline=c, width=3)
        d.text((84, y + 30), label, font=f, fill=c if state == 'bryan' else 'black')
        if img and pathlib.Path(img).exists():
            try:
                t = Image.open(img).convert('RGB'); t.thumbnail((300, 84)); im.paste(t, (W - 40 - t.width, y + 4))
            except Exception: pass
        d.line((40, y + 92, W - 40, y + 92), fill=(227, 229, 233), width=1); y += 96
    d.text((40, y + 8), '■ done   ◧ running   □ needs you', font=fs, fill=(85, 85, 85))
    out = B / f"CALACADEMY_STATUS_CARD_{datetime.datetime.now().strftime('%Y_%m_%d_%H%M')}.png"; im.save(out); print(out)


if __name__ == '__main__':
    main()
