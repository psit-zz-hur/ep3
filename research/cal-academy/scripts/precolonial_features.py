#!/usr/bin/env python3
"""Texture features from the 1852 T-sheet (T00382) at sheet/6 resolution (~5.07 m): ink density (grass-tuft / stipple / scrub symbols), red contour density,
paper (blank) flag. Cached as npz next to the sheet; rerunnable.  Outputs: data/cal-academy/precolonial/t00382_features_f6.npz"""
import numpy as np, cv2, pathlib
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / 'data' / 'cal-academy' / 'precolonial' / 'noaa_tsheets' / 'T00382-00-1852.jpg'
OUTF = ROOT / 'data' / 'cal-academy' / 'precolonial' / 't00382_features_f6.npz'
F = 6
def main():
    im = np.asarray(Image.open(SRC).convert('RGB')); H, W, _ = im.shape
    h, w = H // F, W // F
    ink = np.zeros((h, w), np.float32); red = np.zeros_like(ink); dark = np.zeros_like(ink); paper = np.zeros_like(ink)
    S = 1200
    for y in range(0, H, S):
        y0, y1 = max(0, y - 60), min(H, y + S + 60)
        c = im[y0:y1].astype(np.float32); L = c.mean(2); R, G, B = c[..., 0], c[..., 1], c[..., 2]
        bg = cv2.GaussianBlur(L, (0, 0), 25)
        ink_m = ((L < bg * 0.55) & ((R - G) < 40)).astype(np.float32)
        red_m = (((R - G) > 45) & (L < bg * 0.9)).astype(np.float32)
        dark_m = (L < bg * 0.40).astype(np.float32)
        a, b = y - y0, y - y0 + min(S, H - y)
        for name, m, dst in (('ink', ink_m, ink), ('red', red_m, red), ('dark', dark_m, dark)):
            blk = m[a:b][: (b - a) // F * F, : w * F].reshape((b - a) // F, F, w, F).mean((1, 3))
            dst[y // F: y // F + blk.shape[0]] = blk
        pm = ((np.abs(R - G) < 200) & (L > 150)).astype(np.float32)   # paper-ish brightness
        blk = pm[a:b][: (b - a) // F * F, : w * F].reshape((b - a) // F, F, w, F).mean((1, 3)); paper[y // F: y // F + blk.shape[0]] = blk
        print('strip', y, end='\r')
    np.savez_compressed(OUTF, ink=ink, red=red, dark=dark, paper=paper, F=F)
    print('saved', OUTF, ink.shape, ink.mean(), red.mean())
if __name__ == '__main__': main()
