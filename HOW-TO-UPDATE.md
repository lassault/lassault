# Updating the profile slider

The slider is generated, not hand-written:

```sh
pip install fonttools brotli
python3 build.py        # writes profile-light.svg and profile-dark.svg
```

Edit the `SLIDES` and `MATERIALS` lists in `build.py` to change the content,
and `HOLD` / `MOVE` to change the pace. The fonts (Instrument Serif, Work Sans,
IBM Plex Mono, all under the SIL Open Font License) are subset and embedded in
the SVG, because GitHub shows SVGs as images and images can't load web fonts.

The old `profile.svg` and `media/` folder are no longer used and can be deleted.
