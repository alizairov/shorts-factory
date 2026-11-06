# Shorts Factory

Code-animated YouTube Shorts (satisfying · educational · comparison).
Everything — visuals and music — is generated from code in `src/` (Python + pycairo + numpy + ffmpeg).

- `src/common.py` — palette, drawing helpers, encoder, synth music
- `src/*.py` — one script per video (`python3 x.py stills N...` to preview, `python3 x.py full` to render)
- `videos/weekN/` — rendered 1080x1920 MP4s and `weekN.json` (titles, descriptions, tags)
