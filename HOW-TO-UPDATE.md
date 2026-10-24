# Updating the profile slider

The slider is generated, not hand-written:

```sh
mise run install
mise run build         # writes profile-light.svg and profile-dark.svg
mise run test
```

Edit `content.yml` to change personal or collection content. Layout, artwork,
and animation remain in `build.py`; edit `HOLD` / `MOVE` there to change the
pace. The fonts (Instrument Serif, Work Sans, IBM Plex Mono, all under the SIL
Open Font License) are subset and embedded in the SVG, because GitHub shows
SVGs as images and images can't load web fonts.

To preview the generated files locally, run `mise run preview` and open
`http://localhost:8000/profile-light.svg` or `profile-dark.svg` in a browser.
