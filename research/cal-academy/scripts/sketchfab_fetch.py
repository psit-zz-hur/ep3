#!/usr/bin/env python3
"""Download the free Sketchfab exhibit models into game/assets/props/ (run on the laptop).

Sketchfab only serves downloads to logged-in accounts, so this uses the official Download API with
your own API token (Sketchfab > Settings > Password & API > API token):

    export SKETCHFAB_TOKEN=...   # never commit it
    python3 research/cal-academy/scripts/sketchfab_fetch.py

Each model is fetched as a glTF zip, unzipped to game/assets/props/<name>/, and the loader in
game/src/props.js reads <name>/scene.gltf (or a .glb if you convert it). Respect each model's license
(CC BY: credit the author in the credits screen). Only models flagged downloadable by their authors
appear here; the Viz Studio reef tank photogrammetry is view-only and stays an embed.
"""
import os, sys, json, zipfile, io, urllib.request, pathlib

MODELS = {
  # target folder name            : (Sketchfab uid, author, note)
  'reef_buddha_wall':               ('33b9a3f789f24ee097a2487a848b2f92', 'California Academy of Sciences Viz Studio', 'Steinhart Philippine Reef buddha wall, photogrammetry'),
  'acropora_palmata_01':            ('90e4a9481fb143769d7107ca3b78f16c', 'California Academy of Sciences Viz Studio', 'Elkhorn coral, raw photogrammetry'),
  'echinophyllia_sp':               ('f530e005c95b476d9fa3f6f974df387d', 'California Academy of Sciences Viz Studio', 'Philippine tank coral photogrammetry test'),
  'hubbs_beaked_whale_skull':       ('1b6becc5e55f48fe813418e2e7be09b2', 'Emm (@edemaistre)', 'iPhone scan at the Academy'),
  'redwood_cross_section':          ('128329651df94258b2305ad7358f6f75', 'Emm (@edemaistre)', 'iPhone scan at the Academy'),
  'sea_turtle':                     ('1a77b2b578cb449a98a4cc9653e5168b', 'Emm (@edemaistre)', 'iPhone scan at the Academy'),
  'alligator_skull':                ('7e389853aa9f4723b824b166491ab150', 'Emm (@edemaistre)', 'iPhone scan at the Academy'),
  'walrus_skull':                   ('810b86b2f0834d86b33bbb2e8bdde76e', 'Emm (@edemaistre)', 'iPhone scan at the Academy'),
  'megalodon_jaws':                 ('0c58b98201174b06b678dc469091e646', 'Emm (@edemaistre)', 'Full-scale megalodon jaws'),
  'seal_sea_lion_skeletons':        ('5624a29e5b9844d8a05be630b4cc9e96', 'Emm (@edemaistre)', 'Seal and sea lion skeletons'),
  'humongous_tropical_fish':        ('c12ba0d543e5407abfaaf60df343efed', 'Emm (@edemaistre)', 'Large fish mount'),
  'grizzly_skull':                  ('0d59abfbb8c34864b96fa9e68b21da4c', 'Emm (@edemaistre)', 'Grizzly bear skull'),
  'reptile_fossil':                 ('fb83029815304e61ae5945e6281d2269', 'Emm (@edemaistre)', 'Reptile fossil slab'),
  'coral_visitor_scan':             ('7da18265ce31434fb3010fcbdb1ee6f6', 'Emm (@edemaistre)', 'Coral'),
  # page could not be read (rate-limited); check on sketchfab.com and add if it says "Download Free":
  # 'trex_full_scale':              ('0390e81bbbc74aa38b4021a0b58c6115', 'Emm (@edemaistre)', 'Day 279: full-scale T. rex skeleton'),
  # View-only (embed, do not download): Viz Studio 'philippine-coral-reef-photogrammetry' 57042a82ee7246b6899832512404dd08,
  # 'steinart-phillipine-reef-big-tank' b491a18288b14100a81265519aabc0a9, 'steinhart-aquarium-philippine-coral-reef' 627a6abdb1834a5b8d9ad1f954da2972,
  # 'dusky-damselfish' 5d4447bbb11b40428c796daa33caa8c7.
}

def main():
    tok = os.environ.get('SKETCHFAB_TOKEN')
    if not tok: sys.exit('set SKETCHFAB_TOKEN (Sketchfab > Settings > Password & API)')
    out = pathlib.Path(__file__).resolve().parents[3] / 'game' / 'assets' / 'props'; out.mkdir(parents=True, exist_ok=True)
    credits = []
    for name, (uid, author, note) in MODELS.items():
        dest = out / name
        if (dest / 'scene.gltf').exists(): print('have', name); continue
        req = urllib.request.Request(f'https://api.sketchfab.com/v3/models/{uid}/download', headers={'Authorization': f'Token {tok}'})
        try: info = json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e: print('skip', name, e); continue
        url = (info.get('gltf') or info.get('glb') or {}).get('url')
        if not url: print('no gltf for', name, list(info)); continue
        data = urllib.request.urlopen(url, timeout=600).read()
        dest.mkdir(exist_ok=True); zipfile.ZipFile(io.BytesIO(data)).extractall(dest)
        meta = json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.sketchfab.com/v3/models/{uid}', headers={'Authorization': f'Token {tok}'}), timeout=60))
        lic = (meta.get('license') or {}).get('label', '?')
        credits.append(f"{meta.get('name')} by {author} ({lic}) https://sketchfab.com/3d-models/{uid} — {note}")
        print('ok', name, lic, len(data) // 1024, 'KB')
    (out / 'CREDITS.md').write_text('# Exhibit model credits\n\n' + '\n'.join('- ' + c for c in credits) + '\n')
    print('wrote', out / 'CREDITS.md')

if __name__ == '__main__': main()
