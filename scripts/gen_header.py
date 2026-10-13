#!/usr/bin/env python3
"""Render the profile's Kubernetes pod typography with the standard library.

Run from any directory: python3 scripts/gen_header.py
The topology is an illustration, not cluster telemetry. A 12-second loop removes
one letter's pod and reconciles it. Reduced-motion mode preserves the full name.
"""
from html import escape
from math import cos, sin, pi
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
THEMES = {
    "dark": dict(bg="#090c13", panel="#101725", fg="#f0f5ff", muted="#8fa3c2",
                 line="#253550", grid="#121d30", blue="#568eff", pod="#3d7cff",
                 edge="#95baff", cyan="#87e5ef", orange="#ffc280"),
    "light": dict(bg="#f6f8ff", panel="#edf2ff", fg="#122441", muted="#536783",
                  line="#b7c7e3", grid="#e0e8f6", blue="#245ad7", pod="#326ce5",
                  edge="#1b4eb8", cyan="#00697a", orange="#a84813"),
}
LETTERS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
}
SANS = "Arial, Helvetica, 'DejaVu Sans', sans-serif"
MONO = "'DejaVu Sans Mono', Consolas, monospace"


def text(x, y, value, size=16, color="fg", *, weight=400, mono=True, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{{{color}}}" font-family="{MONO if mono else SANS}" '
            f'font-size="{size}" font-weight="{weight}" {extra}>{escape(value)}</text>')


def wheel(x, y, scale=1):
    points = " ".join(f"{66*cos(-pi/2+i*2*pi/7):.2f},{66*sin(-pi/2+i*2*pi/7):.2f}" for i in range(7))
    result = f'<g transform="translate({x} {y}) scale({scale})">'
    result += '<circle r="83" fill="none" stroke="{line}" stroke-dasharray="1 7"/>'
    result += '<circle class="orbit" r="76" fill="none" stroke="{blue}" stroke-width="2" stroke-dasharray="25 452"/>'
    result += f'<polygon points="{points}" fill="#326ce5"/>'
    result += '<g fill="none" stroke="#ffffff" stroke-linecap="round" stroke-width="6">'
    result += '<circle r="29"/>'
    for i in range(7):
        a = -pi/2 + i*2*pi/7
        result += f'<path d="M{12*cos(a):.2f} {12*sin(a):.2f}L{47*cos(a):.2f} {47*sin(a):.2f}"/>'
    result += '</g><circle r="9" fill="#ffffff"/></g>'
    return result


def node(letter, x, y, compact=False):
    width, height, cell, step, padx, pady = (104, 160, 12, 16, 14, 32) if compact else (190, 270, 24, 30, 23, 42)
    result = f'<g><title>Worker {letter.lower()}: pods form the letter {letter}</title>'
    result += f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{{panel}}" stroke="{{line}}"/>'
    result += f'<path d="M{x} {y+10}v-10h10M{x+width-10} {y+height}h10v-10" stroke="{{blue}}" stroke-width="2" fill="none"/>'
    result += text(x+10, y+20 if compact else y+25, f"worker-{letter.lower()}", 10 if compact else 13, "muted")
    for row, pattern in enumerate(LETTERS[letter]):
        for col, on in enumerate(pattern):
            px, py = x+padx+col*step, y+pady+row*step
            result += f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="1" fill="none" stroke="{{grid}}"/>'
            if on == "0":
                continue
            changing = letter == "T" and row == 4 and col == 2
            cls = ' class="recreated-pod"' if changing else ''
            result += f'<g{cls}><rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="1" fill="{{pod}}"/>'
            result += f'<path d="M{px+3} {py+cell-3}h{cell-6}" stroke="{{edge}}" stroke-width="1"/></g>'
            if changing:
                result += f'<rect class="missing-pod" x="{px-2}" y="{py-2}" width="{cell+4}" height="{cell+4}" fill="none" stroke="{{orange}}" stroke-dasharray="3 3"/>'
    result += '</g>'
    return result


def state(x, y, compact=False):
    size = 15 if compact else 16
    result = text(x, y, "desired: ARTEM", size, "muted")
    dx = x if compact else x+400
    dy = y+30 if compact else y
    for cls, value, color in [
        ("phase-steady", "observed = desired", "cyan"),
        ("phase-drift", "pod lost / drift detected", "orange"),
        ("phase-reconcile", "reconciling / creating pod", "blue"),
    ]:
        result += text(dx, dy, value, size, color, extra=f'class="{cls}"')
    return result


def header(theme, mobile=False):
    w, h = (640, 724) if mobile else (1120, 668)
    body = f'<rect width="{w}" height="{h}" fill="{{bg}}"/>'
    body += f'<rect x="1" y="1" width="{w-2}" height="{h-2}" fill="url(#grid)" stroke="{{line}}"/>'
    body += f'<path d="M24 59H{w-24}" stroke="{{line}}"/>'
    body += text(28, 37, "ARTEM / CLOUD & DEVOPS", 13 if mobile else 15)
    body += text(w-28, 37, "ctx: etosheartem", 12 if mobile else 14, "muted", extra='text-anchor="end"')
    if mobile:
        body += text(26, 135, "KUBERNETES", 67, weight=800, mono=False, extra='letter-spacing="-3"')
        body += text(30, 173, "LINUX / HELM / AUTOMATION", 17, "muted")
        body += wheel(320, 280, .9)
        body += text(320, 382, "deployment / identity", 15, "muted", extra='text-anchor="middle"')
        body += '<path d="M320 355V403M82 403H558" fill="none" stroke="{line}"/>'
        for i, letter in enumerate(LETTERS):
            x = 30+i*119
            body += f'<path d="M{x+52} 403V426" stroke="{{blue}}" fill="none"/>'
            body += node(letter, x, 426, True)
        body += '<path d="M30 619H610" stroke="{line}"/>'
        body += state(30, 652, True)
        body += text(610, 682, "↺", 28, "blue", extra='text-anchor="end"')
    else:
        body += text(29, 160, "KUBERNETES", 100, weight=800, mono=False, extra='letter-spacing="-5"')
        body += text(36, 202, "LINUX / HELM / AUTOMATION", 20, "muted")
        body += wheel(974, 155)
        body += '<path d="M974 239V266M127 266H983" stroke="{line}" fill="none"/>'
        body += '<rect x="376" y="250" width="367" height="30" fill="{bg}"/>'
        body += text(560, 271, "deployment / identity", 17, "muted", extra='text-anchor="middle"')
        for i, letter in enumerate(LETTERS):
            x = 32+i*214
            body += f'<path d="M{x+95} 266V304" stroke="{{line}}" fill="none"/>'
            body += f'<path class="traffic" d="M{x+95} 266V304" stroke="{{blue}}" stroke-width="2" fill="none"/>'
            body += node(letter, x, 304)
        body += '<path d="M32 608H1088" stroke="{line}"/>'
        body += state(36, 642)
        body += text(1082, 642, "↺ reconcile()", 15, "blue", extra='text-anchor="end"')
    colors = THEMES[theme]
    for key, value in colors.items():
        body = body.replace("{"+key+"}", value)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"
  role="img" aria-labelledby="title desc">
  <title id="title">Artem / Kubernetes — a name built from pods</title>
  <desc id="desc">Артём, Cloud и DevOps. Схема Kubernetes: поды на пяти узлах складываются в ARTEM.
  Один под исчезает и восстанавливается в анимации reconciliation. Это иллюстрация профиля.</desc>
  <defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="{colors['grid']}" stroke-width=".5"/>
  </pattern></defs>
  <style>
    .orbit {{ animation: orbit 12s linear infinite; }}
    .traffic {{ stroke-dasharray: 4 34; animation: traffic 3s linear infinite; }}
    .recreated-pod {{ animation: pod 12s linear infinite; }}
    .missing-pod {{ opacity: 0; animation: missing 12s linear infinite; }}
    .phase-steady {{ animation: steady 12s step-end infinite; }}
    .phase-drift {{ opacity: 0; animation: drift 12s step-end infinite; }}
    .phase-reconcile {{ opacity: 0; animation: reconcile 12s step-end infinite; }}
    @keyframes orbit {{ to {{ stroke-dashoffset: -477; }} }}
    @keyframes traffic {{ to {{ stroke-dashoffset: -38; }} }}
    @keyframes pod {{ 0%,27% {{ opacity:1; }} 30%,55% {{ opacity:0; }} 65%,100% {{ opacity:1; }} }}
    @keyframes missing {{ 0%,27% {{ opacity:0; }} 30%,55% {{ opacity:1; }} 65%,100% {{ opacity:0; }} }}
    @keyframes steady {{ 0% {{ opacity:1; }} 28% {{ opacity:0; }} 66% {{ opacity:1; }} }}
    @keyframes drift {{ 0% {{ opacity:0; }} 28% {{ opacity:1; }} 45% {{ opacity:0; }} }}
    @keyframes reconcile {{ 0% {{ opacity:0; }} 45% {{ opacity:1; }} 66% {{ opacity:0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      * {{ animation:none !important; }}
      .recreated-pod, .phase-steady {{ opacity:1; }}
      .missing-pod, .phase-drift, .phase-reconcile {{ opacity:0; }}
    }}
  </style>
  {body}
</svg>
'''


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            (ASSETS / f"cluster-{theme}{suffix}.svg").write_text(header(theme, mobile), encoding="utf-8")
    print("Generated four Kubernetes profile illustrations.")


if __name__ == "__main__":
    main()
