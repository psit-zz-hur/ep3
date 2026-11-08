#!/usr/bin/env python3
"""Move today's Scaniverse exports from Downloads into captures/<space>/ and stage SPZs for the game.

    python research/cal-academy/scripts/ingest_captures.py                 # interactive: asks a space name per file
    python research/cal-academy/scripts/ingest_captures.py --map "Scan 12=piazza" --map "Scan 13=steinhart_reef"
    python research/cal-academy/scripts/ingest_captures.py --src "D:/phone" # another source folder

captures/ is git-ignored. The game reads game/assets/splats/<space>.spz (copied here) via assets/splats/manifest.json.
"""
import argparse, pathlib, shutil, sys, re, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
EXTS = {'.spz', '.ply', '.glb', '.usdz', '.las', '.obj', '.fbx'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=str(pathlib.Path.home() / 'Downloads'))
    ap.add_argument('--map', action='append', default=[], help='"<filename stem or prefix>=<space>"')
    ap.add_argument('--since-hours', type=float, default=48)
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    src = pathlib.Path(a.src); cut = time.time() - a.since_hours * 3600
    files = sorted([p for p in src.iterdir() if p.suffix.lower() in EXTS and p.stat().st_mtime > cut], key=lambda p: p.stat().st_mtime)
    if not files: sys.exit(f'no {sorted(EXTS)} files newer than {a.since_hours} h in {src}')
    rules = [m.split('=', 1) for m in a.map]
    caps = ROOT / 'captures'; game_splats = ROOT / 'game' / 'assets' / 'splats'
    for p in files:
        space = next((s for k, s in rules if p.stem.lower().startswith(k.lower())), None)
        if not space:
            space = input(f'{p.name} ({p.stat().st_size // 1_000_000} MB) -> space name (blank = skip): ').strip()
            if not space: continue
        space = re.sub(r'[^a-z0-9_]+', '_', space.lower()).strip('_')
        dest = caps / space / p.name
        print(('would move' if a.dry else 'move'), p, '->', dest)
        if a.dry: continue
        dest.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(p), str(dest))
        if dest.suffix.lower() in ('.spz', '.ply'):
            tgt = game_splats / f'{space}{dest.suffix.lower()}'
            if not tgt.exists() or dest.suffix.lower() == '.spz': shutil.copy2(dest, tgt); print('  staged', tgt)
    print('done. add the new spaces to game/assets/splats/manifest.json if they are not there yet.')

if __name__ == '__main__': main()
