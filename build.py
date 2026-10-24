#!/usr/bin/env python3
"""Builds profile-light.svg and profile-dark.svg for the GitHub profile README.

A sliding walk through The Lassa Collection: each slide is a framed work and
its wall label. Fonts are subset and embedded, because GitHub shows SVGs as
images and images cannot load web fonts.

    pip install fonttools brotli
    python3 build.py
"""
import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
W, H = 800, 300
HOLD = 4.8      # seconds each slide stays still
MOVE = 1.0      # seconds of sliding between slides

THEMES = {
    "light": dict(bg="#FFFFFF", stone="#F1F0EC", ink="#1A1A1A", text2="#3D3D39", muted="#5A5A55",
                  line="#E2E2DE", mat="#FFFFFF", shadow="rgba(0,0,0,0.45)", wall="#FFFFFF"),
    "dark": dict(bg="#161616", stone="#232321", ink="#F1F0EC", text2="#D3D1CA", muted="#A8A8A2",
                 line="#3A3A37", mat="#EDEBE4", shadow="rgba(0,0,0,0.8)", wall="#161616"),
}

PING = """<svg class="ping" viewBox="-2 -2 166 106" xmlns="http://www.w3.org/2000/svg">
<polygon points="118,0 121,0 140,20 160,40 120,80 80,80 118,42 76,42" fill="#FFFFFF"/>
<polygon points="78,0 118,0 76,42 118,42 80,80 0,80" fill="#063970"/>
<path d="M118 42 L140 20 L160 40 L120 80 L80 80" fill="none" stroke="#111111" stroke-width="2" stroke-linejoin="round"/>
<polygon points="121,0 159,0 140,19" fill="#FCB60C"/>
<circle cx="123" cy="21" r="5" fill="#111111"/>
<path d="M41 80 V91 M81 80 V91" stroke="#111111" stroke-width="2"/>
<path d="M41 91 H55 A5 4.5 0 0 1 55 100 H41 Z M81 91 H95 A5 4.5 0 0 1 95 100 H81 Z" fill="#FCB60C" stroke="#111111" stroke-width="1.5"/>
</svg>"""

ART = {
    "shift": '<div class="art" style="background:#063970"><div class="shift"><i></i><i></i><i></i></div></div>',
    "modules": '<div class="art" style="background:#F1EBDD"><div class="modules">'
               + "".join('<i class="odd"></i>' if i == 7 else "<i></i>" for i in range(12)) + "</div></div>",
    "stars": '<div class="art" style="background:#0E1430">'
             + "".join(f'<i class="star" style="left:{(i*61+i*i*7+13)%96}%;top:{(i*29+i*i*11+5)%88}%"></i>' for i in range(24))
             + '<b class="ship"></b></div>',
}

SLIDES = [
    dict(kind="entrance"),
    dict(kind="work", art="shift", eyebrow="Room 1 · The day job", no="Cat. 01",
         title="Shift Left", year="2022 – today", medium="GitLab CI/CD, Docker, security scanners",
         text="Security checks moved to the start of the release process, where problems are cheap. "
              "Note how each bar has moved left.",
         note="Occasionally blocks a Friday deploy. This is considered a feature.",
         credit="Commissioned by Veridas, DevOps engineer since March 2022."),
    dict(kind="work", art="modules", eyebrow="Room 1 · The day job", no="Cat. 02",
         title="Everything as Code", year="2022 – today", medium="Terraform, AWS, a little GCP, pull requests",
         text="Infrastructure that only changes through pull requests: lint, validate, deploy. "
              "Reusable modules, checked by testing.",
         note="Manual changes in the cloud console are treated as vandalism.",
         credit="Commissioned by Veridas."),
    dict(kind="work", art="stars", eyebrow="Room 2 · The night shift", no="Cat. 06",
         title="SpaceWar", year="2019", medium="Java",
         text="A space shooter. What hangs here is a portrait; the original is playable online.",
         note="Highest score, held by the artist: 2,147,483,647. Unverified.",
         credit="Also on display: TLMgram, livEvent, 100tipy, OSniffy."),
    dict(kind="materials"),
    dict(kind="exit"),
]

MATERIALS = ["AWS", "GCP", "Terraform", "GitLab CI/CD", "GitHub Actions",
             "Docker", "Linux", "Rust", "Python", "Java"]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slide_html(s: dict, n: int, total: int) -> str:
    counter = f'<span>{n} / {total}</span>'
    if s["kind"] == "entrance":
        return f"""<div class="slide">
  <div class="frame entrance-frame">{PING}</div>
  <div class="label">
    <p class="top"><span>The Lassa Collection</span>{counter}</p>
    <h1 class="serif">Fermin Lassa</h1>
    <p class="sub serif"><em>Selected Works, 2019 – today</em></p>
    <p class="text">An exhibition of systems built, broken and repaired by a DevOps engineer in Spain.
    Most of the works still run. Some of them should not.</p>
  </div>
</div>"""
    if s["kind"] == "materials":
        items = "".join(f"<li>{esc(m)}</li>" for m in MATERIALS)
        return f"""<div class="slide">
  <div class="frame placard-frame"><div class="placard"><p class="eyebrow">Wall text</p>
    <p class="serif placard-title"><em>Materials used in this collection</em></p></div></div>
  <div class="label">
    <p class="top"><span>Medium</span>{counter}</p>
    <ul class="materials">{items}</ul>
    <p class="note"><b>Conservation note.</b> Coffee, four a day, is load-bearing.</p>
  </div>
</div>"""
    if s["kind"] == "exit":
        return f"""<div class="slide">
  <div class="frame exit-frame">
    <div class="door-wrap">
      <span class="sign">STAFF ONLY</span>
      <div class="door-frame"><div class="cameo"><div class="head"><i class="hair"></i><i class="face"></i>
        <i class="band"></i><i class="lens l"></i><i class="lens r"></i></div></div>
        <div class="door"><i class="knob"></i></div></div>
    </div>
  </div>
  <div class="label">
    <p class="top"><span>Exit · Gift shop</span>{counter}</p>
    <h2 class="serif">Plan your visit</h2>
    <p class="text">The full collection is open at <b>fermin.lassa.es</b>.<br/>
    Monday – Friday, 9:00 – 17:00 (Madrid time). Admission free.</p>
    <p class="note"><b>Note.</b> There is no Room 3. Please do not try the door.</p>
  </div>
</div>"""
    return f"""<div class="slide">
  <div class="frame">{ART[s["art"]]}</div>
  <div class="label">
    <p class="top"><span>{esc(s["eyebrow"])}</span>{counter}</p>
    <h2 class="work-title"><em class="serif">{esc(s["title"])}</em>, {esc(s["year"])}</h2>
    <p class="muted">{esc(s["medium"])}</p>
    <p class="text">{esc(s["text"])}</p>
    <p class="note"><b>Conservation note.</b> {esc(s["note"])}</p>
    <p class="credit">{esc(s["no"])} · {esc(s["credit"])}</p>
  </div>
</div>"""


def keyframes(count: int) -> tuple[str, float]:
    # Slides 0..count-1, plus a copy of slide 0 at the end for a seamless loop.
    seg = HOLD + MOVE
    total = seg * count
    steps = []
    for i in range(count):
        start, hold_end = i * seg, i * seg + HOLD
        steps.append(f"{start / total * 100:.3f}%, {hold_end / total * 100:.3f}% {{ transform: translateX(-{i * W}px); }}")
    steps.append(f"100% {{ transform: translateX(-{count * W}px); }}")
    return "@keyframes walk { " + " ".join(steps) + " }", total


def font_face(family: str, file: str, style: str, weight: int, text: str) -> str:
    font = TTFont(HERE / "fonts" / file)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face {{ font-family: '{family}'; font-style: {style}; font-weight: {weight}; "
            f"src: url(data:font/woff2;base64,{data}) format('woff2'); }}")


def build(theme: str) -> str:
    t = THEMES[theme]
    slides = [slide_html(s, i + 1, len(SLIDES)) for i, s in enumerate(SLIDES)]
    slides.append(slides[0])  # seamless loop
    body = "\n".join(slides)
    frames, total = keyframes(len(SLIDES))
    charset = "".join(chr(c) for c in range(0x20, 0x7F)) + "’‘“”–—·→éíáóúñ×"
    fonts = "\n".join([
        font_face("Instrument Serif", "instrument-serif-latin-400-normal.woff2", "normal", 400, charset),
        font_face("Instrument Serif", "instrument-serif-latin-400-italic.woff2", "italic", 400, charset),
        font_face("Work Sans", "work-sans-latin-400-normal.woff2", "normal", 400, charset),
        font_face("Work Sans", "work-sans-latin-600-normal.woff2", "normal", 600, charset),
        font_face("IBM Plex Mono", "ibm-plex-mono-latin-500-normal.woff2", "normal", 500, charset),
    ])
    css = f"""
{fonts}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
.root {{ width: {W}px; height: {H}px; overflow: hidden; background: {t['wall']}; color: {t['ink']};
  font-family: 'Work Sans', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; line-height: 1.5; }}
.slides {{ display: flex; width: {W * (len(SLIDES) + 1)}px; height: {H}px; animation: walk {total:.1f}s infinite; }}
{frames}
.slide {{ width: {W}px; height: {H}px; flex-shrink: 0; display: flex; }}
.serif {{ font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; }}
.frame {{ width: 340px; height: {H}px; flex-shrink: 0; background: {t['stone']}; display: flex; align-items: center; justify-content: center; }}
.art {{ position: relative; width: 268px; height: 201px; border: 10px solid {t['mat']}; border-radius: 14px; box-shadow: 0 16px 26px -16px {t['shadow']}; overflow: hidden; }}
.art i, .art b {{ position: absolute; display: block; }}
.shift {{ position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; gap: 13px; padding: 0 14%; }}
.shift i {{ position: static !important; height: 18px; width: 70%; background: #FCB60C; }}
.shift i:nth-child(1) {{ margin-left: 30%; }} .shift i:nth-child(2) {{ margin-left: 15%; opacity: .8; }} .shift i:nth-child(3) {{ opacity: .6; }}
.modules {{ position: absolute; inset: 16% 14%; display: grid; grid-template-columns: repeat(4, 1fr); gap: 7px; }}
.modules i {{ position: static !important; border: 2px solid #063970; background: #DDE4EE; }}
.modules i.odd {{ background: #FCB60C; border-color: #1A1A1A; }}
.star {{ width: 2px; height: 2px; background: #F2F2F2; }}
.ship {{ left: 46%; top: 62%; width: 16px; height: 19px; background: #FCB60C; clip-path: polygon(50% 0, 100% 100%, 0 100%); }}
.label {{ flex: 1; padding: 30px 40px 26px 40px; display: flex; flex-direction: column; justify-content: flex-end; gap: 6px; }}
.top {{ display: flex; justify-content: space-between; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: {t['muted']}; margin-bottom: auto; }}
h1 {{ font-size: 60px; line-height: .95; letter-spacing: -0.02em; }}
h2 {{ font-weight: 400; }}
h2.serif {{ font-size: 40px; line-height: 1; }}
.sub {{ font-size: 28px; line-height: 1.05; color: {t['muted']}; }}
.work-title {{ font-size: 15px; font-weight: 600; }}
.work-title em {{ font-size: 28px; font-style: italic; font-weight: 400; }}
.muted {{ color: {t['muted']}; margin-top: -4px; }}
.text {{ color: {t['text2']}; margin-top: 6px; }}
.note {{ margin-top: 6px; padding-top: 8px; border-top: 1px solid {t['line']}; color: {t['text2']}; font-size: 12px; }}
.credit {{ font-size: 11px; color: {t['muted']}; }}
.entrance-frame .ping {{ width: 220px; height: auto; }}
.placard-frame {{ padding: 30px; }}
.placard {{ width: 100%; height: 100%; border: 1.5px solid {t['ink']}; border-radius: 14px; padding: 22px; display: flex; flex-direction: column; justify-content: space-between; }}
.eyebrow {{ font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: {t['muted']}; }}
.placard-title {{ font-size: 34px; line-height: 1.05; }}
.materials {{ list-style: none; display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px 16px; font-family: 'IBM Plex Mono', ui-monospace, monospace; font-size: 13px; font-weight: 500; }}
.materials li {{ padding: 6px 0; border-bottom: 1px solid {t['line']}; }}
.exit-frame {{ align-items: flex-end; }}
.door-wrap {{ display: flex; flex-direction: column; align-items: center; gap: 8px; }}
.sign {{ padding: 3px 9px; background: {t['ink']}; color: {t['wall']}; font-size: 10px; letter-spacing: .16em; }}
.door-frame {{ position: relative; width: 112px; height: 190px; background: #10202F; border: 3px solid {t['ink']}; border-bottom: 0; border-radius: 14px 14px 0 0; overflow: hidden; }}
.door {{ position: absolute; inset: 0; background: #D9D3C5; }}
.door::before, .door::after {{ content: ""; position: absolute; left: 12px; right: 12px; border: 1.5px solid #B3AC9B; }}
.door::before {{ top: 14px; height: 60px; }} .door::after {{ bottom: 14px; height: 80px; }}
.knob {{ position: absolute; right: 10px; top: 96px; width: 9px; height: 9px; border-radius: 50%; background: #1A1A1A; }}
.cameo {{ position: absolute; left: 100%; top: 50px; width: 44px; height: 62px; overflow: hidden; }}
.head {{ position: absolute; left: 0; top: 0; width: 48px; height: 62px; transform: translateX(-100%); animation: peek {total:.1f}s ease-in-out infinite; }}
.head i {{ position: absolute; display: block; }}
.hair {{ left: 0; top: 0; width: 48px; height: 27px; background: #D2602A; clip-path: polygon(0 70%, 10% 15%, 22% 55%, 32% 0, 46% 45%, 58% 5%, 68% 50%, 80% 0, 90% 55%, 100% 30%, 100% 100%, 0 100%); }}
.face {{ left: 6px; top: 13px; width: 34px; height: 38px; border-radius: 48%; background: #E8B98F; border: 2px solid #1A1A1A; }}
.band {{ left: 2px; top: 25px; width: 42px; height: 4px; background: #1A1A1A; }}
.lens {{ top: 20px; width: 12px; height: 12px; border-radius: 50%; background: #CFE3EA; border: 2px solid #1A1A1A; }}
.lens.l {{ left: 10px; }} .lens.r {{ left: 22px; }}
{peek_keyframes(total)}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>The Lassa Collection — Fermin Lassa, DevOps engineer. Selected works, 2019 – today.</title>
<foreignObject width="{W}" height="{H}">
<div xmlns="http://www.w3.org/1999/xhtml" class="root">
<style>{css}</style>
<div class="slides">
{body}
</div>
</div>
</foreignObject>
</svg>
"""


def peek_keyframes(total: float) -> str:
    # The artist only peeks while the exit slide is showing.
    seg = HOLD + MOVE
    start = (len(SLIDES) - 1) * seg
    p = lambda s: f"{(start + s) / total * 100:.3f}%"
    return ("@keyframes peek { "
            f"0%, {p(0.9)} {{ transform: translateX(-100%); }} "
            f"{p(1.5)}, {p(2.6)} {{ transform: translateX(-30%); }} "
            f"{p(2.9)} {{ transform: translateX(-42%); }} "
            f"{p(3.2)} {{ transform: translateX(-30%); }} "
            f"{p(3.8)}, 100% {{ transform: translateX(-100%); }} }}")


if __name__ == "__main__":
    for name in THEMES:
        out = HERE / f"profile-{name}.svg"
        out.write_text(build(name), encoding="utf-8")
        print(out.name, f"{out.stat().st_size / 1024:.0f} KB")
