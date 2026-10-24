#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent.parent
FONT_DATA = re.compile(r"data:font/woff2;base64,[^)]+")


def normalized(svg: str) -> str:
    return FONT_DATA.sub("data:font/woff2;base64,<embedded-font>", svg)


for name in ("profile-light.svg", "profile-dark.svg"):
    current = (HERE / name).read_text(encoding="utf-8")
    committed = subprocess.check_output(
        ["git", "show", f"HEAD:{name}"], cwd=HERE, text=True
    )
    if normalized(current) != normalized(committed):
        raise SystemExit(f"{name} differs from the committed generated structure")
