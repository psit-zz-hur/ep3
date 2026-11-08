#!/usr/bin/env python3
"""One image: what is running, done, or waiting on Bryan, with the latest picture per stream.
    python -X utf8 research/cal-academy/scripts/status_card.py  -> boards/CALACADEMY_STATUS_CARD_<time>.png
"""
import datetime, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[3]; B = ROOT / 'boards'; IMG = B / 'img'; EX = ROOT / 'exports'
ROWS = [  # (state, label, image)
    ('running', 'DIAGRAM · Cal Academy real build (hours)', B / 'CALACADEMY_DIAGRAM_MOCKUP_2026_11_07A.png'),
    ('running', 'PLANET · V1 park today + pre-colonial outside', IMG / '23_precolonial_habitat.png'),
    ('running', 'PLANET · V2 all pre-colonial, elk', IMG / '26_outside_lands_carville_contact.png'),
    ('done', 'PLANET · V3 island, sea at 7.4 m', EX / 'CALACADEMY_PLANET_V3_SHEET_2026_11_07C.jpg'),
    ('done', 'PLANET · V0 today', EX / 'CALACADEMY_PLANET_SHEET_2026_11_07B.jpg'),
    ('running', 'whole-park 1 m core, rim, buses, masks', None),
    ('done', 'sprites v3 (PDM whales)', IMG / '27_sprites_proof.png'),
    ('done', 'FFT water in the game flood', IMG / '24_ocean_surface.png'),
    ('done', 'RPBW drawings in Rhino D / E', IMG / '22_rpbw_drawings_registered.png'),
    ('bryan', 'Scaniverse: name the two savannah scans', None),
    ('bryan', 'Rhino: run skp_register_v3 + drawings_pictures_v1', None),
]
INK = {'done': (0, 0, 0), 'running': (44, 146, 255), 'bryan': (255, 68, 0)}


def main():
    W, H = 1600, 90 + 110 * len(ROWS) + 40
    im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype('arial.ttf', 28); fs = ImageFont.truetype('arial.ttf', 20); fb = ImageFont.truetype('arialbd.ttf', 30)
    except Exception: f = fs = fb = ImageFont.load_default()
    d.text((40, 28), 'SITREP · ' + datetime.datetime.now().strftime('%H:%M'), font=fb, fill='black'); d.line((40, 72, W - 40, 72), fill='black', width=2)
    y = 90
    for state, label, img in ROWS:
        c = INK[state]
        if state == 'done': d.rectangle((40, y + 40, 64, y + 64), fill=c)
        elif state == 'running': d.rectangle((40, y + 40, 64, y + 64), outline=c, width=3); d.rectangle((40, y + 40, 52, y + 64), fill=c)
        else: d.rectangle((40, y + 40, 64, y + 64), outline=c, width=3)
        d.text((86, y + 36), label, font=f, fill=c if state == 'bryan' else 'black')
        if img and pathlib.Path(img).exists():
            try: t = Image.open(img).convert('RGB'); t.thumbnail((360, 100)); im.paste(t, (W - 40 - t.width, y + 4))
            except Exception: pass
        d.line((40, y + 106, W - 40, y + 106), fill=(227, 229, 233), width=1); y += 110
    d.text((40, y + 8), '■ done   ◧ running   □ needs you', font=fs, fill=(85, 85, 85))
    out = B / f"CALACADEMY_STATUS_CARD_{datetime.datetime.now().strftime('%Y_%m_%d_%H%M')}.png"; im.save(out); print(out)


if __name__ == '__main__':
    main()
