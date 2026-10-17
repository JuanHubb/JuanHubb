#!/usr/bin/env python3
"""Regenerate the Tech Stack icon strips in assets/stack/.

Edit STACK below, then run:  python3 scripts/build_stack.py

Icons come from skillicons.dev; an icon with a file at assets/icons/<id>-<theme>.svg
is read from there instead (for logos skillicons doesn't have, e.g. LangChain).
The strips are baked into the repo because GitHub splits <picture srcset> URLs on
commas, which breaks multi-icon skillicons URLs in dark mode.
"""
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / "assets" / "icons"
OUT = ROOT / "assets" / "stack"

STACK = {
    "languages": ["java", "ts", "js", "python", "dart"],
    "backend": ["spring", "mysql", "postgres", "redis", "supabase"],
    "frontend": ["react", "nextjs", "vite", "tailwind", "threejs", "flutter"],
    "infra": ["aws", "docker", "nginx", "vercel"],
    "ai": ["langchain", "selenium"],
}

SIZE, GAP, HEIGHT = 256, 44, 48  # same geometry as skillicons.dev strips


def icon(name: str, theme: str) -> str:
    local = LOCAL / f"{name}-{theme}.svg"
    if local.exists():
        return local.read_text()
    url = f"https://skillicons.dev/icons?i={name}&theme={theme}"
    req = urllib.request.Request(url, headers={"User-Agent": "build-stack"})
    with urllib.request.urlopen(req) as res:
        svg = res.read().decode()
    if len(svg) < 300:
        raise SystemExit(f"skillicons has no icon named '{name}'")
    return svg


def strip(names: list[str], theme: str) -> str:
    view_w = len(names) * (SIZE + GAP) - GAP
    parts = []
    for i, name in enumerate(names):
        svg = icon(name, theme).strip()
        # Re-position each icon's outer 48x48 wrapper as a 256x256 cell.
        svg = re.sub(r'<svg width="\d+" height="\d+"',
                     f'<svg x="{i * (SIZE + GAP)}" width="{SIZE}" height="{SIZE}"', svg, count=1)
        parts.append(svg)
    width = round(view_w / SIZE * HEIGHT, 2)
    return (f'<svg width="{width}" height="{HEIGHT}" viewBox="0 0 {view_w} {SIZE}" fill="none" '
            'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
            + "\n".join(parts) + "\n</svg>\n")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for row, names in STACK.items():
        for theme in ("dark", "light"):
            (OUT / f"{row}-{theme}.svg").write_text(strip(names, theme))
            print(f"assets/stack/{row}-{theme}.svg  ({', '.join(names)})")
