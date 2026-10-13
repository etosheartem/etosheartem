#!/usr/bin/env python3
"""Build the profile illustrations: python3 scripts/gen_header.py.

Standard library only. SVGs are self-contained; content never depends on motion.
The README selects light, dark, and narrow-screen header variants.
"""
from html import escape
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
THEMES = {
    "dark": dict(bg="#111914", panel="#19231c", fg="#f1f3e8", muted="#a4b2a2",
                 line="#344638", accent="#c5f277", orange="#ffc18c", violet="#c4b5fd", ink="#162014"),
    "light": dict(bg="#f3f2e8", panel="#e7e9dc", fg="#202c22", muted="#596752",
                  line="#bdc7b3", accent="#507628", orange="#a65328", violet="#7553a4", ink="#f8f7ef"),
}
SANS = "Arial, Helvetica, 'DejaVu Sans', sans-serif"
MONO = "'DejaVu Sans Mono', Consolas, monospace"


def text(x, y, value, *, size=16, fill="fg", weight=400, mono=False, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{{{fill}}}" font-size="{size}" '
            f'font-weight="{weight}" font-family="{MONO if mono else SANS}" '
            f'{extra}>{escape(value)}</text>')


def svg(width, height, title, description, body, theme):
    c = THEMES[theme]
    for key, value in c.items():
        body = body.replace("{" + key + "}", value)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
  viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">{escape(title)}</title>
  <desc id="description">{escape(description)}</desc>
  <defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="0.8" fill="{c['line']}"/>
  </pattern></defs>
  <style>
    .flow {{ stroke-dasharray: 4 16; animation: flow 18s linear infinite; }}
    @keyframes flow {{ to {{ stroke-dashoffset: -160; }} }}
    @media (prefers-reduced-motion: reduce) {{ .flow {{ animation: none; }} }}
  </style>
  {body}
</svg>
'''


def routing_art():
    return '''
    <circle cx="878" cy="199" r="142" fill="none" stroke="{line}"/>
    <circle cx="878" cy="199" r="110" fill="none" stroke="{line}" stroke-dasharray="2 10"/>
    <path d="M686 108H765L818 161M898 175L951 97H1017M902 229L968 292H1024"
      fill="none" stroke="{line}" stroke-width="2"/>
    <path class="flow" d="M686 108H765L818 161M898 175L951 97H1017M902 229L968 292H1024"
      fill="none" stroke="{accent}" stroke-width="2"/>
    <g transform="translate(878 199)">
      <rect x="-67" y="-67" width="134" height="134" rx="24" fill="{bg}" stroke="{line}" transform="rotate(-21)"/>
      <rect x="-67" y="-67" width="134" height="134" rx="24" fill="{panel}" stroke="{line}" transform="rotate(-10)"/>
      <rect x="-61" y="-61" width="122" height="122" rx="22" fill="{accent}"/>
      <path d="M-31 23L-3-29H9L36 23M-19 1H22M-4 24H9" fill="none"
        stroke="{ink}" stroke-width="9" stroke-linecap="square" stroke-linejoin="miter"/>
    </g>
    <g fill="{bg}" stroke="{line}" stroke-width="1.5">
      <rect x="654" y="77" width="62" height="62" rx="14"/>
      <rect x="985" y="66" width="62" height="62" rx="14"/>
      <rect x="993" y="261" width="62" height="62" rx="14"/>
    </g>
    <g fill="none" stroke="{accent}" stroke-width="2">
      <rect x="670" y="91" width="30" height="12" rx="2"/>
      <rect x="670" y="111" width="30" height="12" rx="2"/>
      <path d="M675 97h3M675 117h3"/>
    </g>
    <g fill="none" stroke="{orange}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M1007 87l-10 10 10 10M1025 87l10 10-10 10M1020 83l-8 28"/>
    </g>
    <g fill="{violet}">
      <path d="M1010 279h28v7h7v24h-7v-7h-7v7h-7v-7h-7v7h-7z"/>
      <path d="M1010 272h7v14h-7zM1031 272h7v14h-7z"/>
    </g>
    <g fill="{bg}"><rect x="1017" y="286" width="5" height="5"/><rect x="1031" y="286" width="5" height="5"/></g>
    <circle cx="760" cy="278" r="5" fill="{orange}"/>
    <path d="M765 57v12m-6-6h12M983 215v12m-6-6h12" stroke="{muted}"/>
    ''' + text(657, 161, "INFRA", size=12, mono=True, fill="muted") + text(992, 148, "TOOLS", size=12, mono=True, fill="muted") + text(1002, 344, "PLAY", size=12, mono=True, fill="muted")


def header(theme, mobile=False):
    if mobile:
        w, h = 640, 620
        body = '''<rect width="640" height="620" rx="24" fill="{bg}"/>
        <rect x="1" y="1" width="638" height="618" rx="23" fill="none" stroke="{line}"/>
        <path d="M30 85H610M30 550H610" stroke="{line}"/>
        <rect x="290" y="150" width="320" height="375" fill="url(#grid)"/>'''
        body += text(32, 53, "ETOSHEARTEM", size=21, mono=True)
        body += text(608, 53, "PERSONAL WORKSHOP", size=13, mono=True, fill="muted", extra='text-anchor="end"')
        body += text(28, 230, "ARTEM", size=139, weight=800, extra='letter-spacing="-9"')
        body += text(34, 280, "SYSTEMS &", size=38, weight=700)
        body += text(34, 325, "SIDE QUESTS", size=38, weight=700)
        body += '<g transform="translate(-200 216) scale(.78)">' + routing_art() + '</g>'
        body += text(34, 417, "Cloud. Code.", size=23, fill="muted")
        body += text(34, 453, "Curiosity.", size=23, fill="muted")
        body += text(32, 591, "DEVOPS / PYTHON / LINUX", size=18, mono=True)
        body += text(608, 591, "↗", size=30, fill="accent", extra='text-anchor="end"')
    else:
        w, h = 1120, 430
        body = '''<rect width="1120" height="430" rx="24" fill="{bg}"/>
        <rect x="1" y="1" width="1118" height="428" rx="23" fill="none" stroke="{line}"/>
        <rect x="610" y="70" width="485" height="280" fill="url(#grid)"/>
        <path d="M36 76H1084M36 363H1084" stroke="{line}"/>'''
        body += text(38, 48, "ETOSHEARTEM", size=16, mono=True)
        body += text(1082, 48, "PERSONAL WORKSHOP / 01", size=13, mono=True, fill="muted", extra='text-anchor="end"')
        body += text(28, 225, "ARTEM", size=172, weight=800, extra='letter-spacing="-11"')
        body += text(38, 279, "SYSTEMS & SIDE QUESTS", size=31, weight=700, extra='letter-spacing="1"')
        body += text(39, 320, "Cloud. Code. Curiosity.", size=21, fill="muted")
        body += routing_art()
        body += text(38, 403, "DEVOPS / PYTHON / LINUX", size=15, mono=True)
        body += text(1082, 403, "BUILD THINGS. FIGURE THEM OUT.", size=13, mono=True, fill="muted", extra='text-anchor="end"')
    return svg(w, h, "Artem — systems & side quests", "Личная мастерская Артёма: инфраструктура, инструменты и игры. DevOps, Python, Linux.", body, theme)


def project(theme, kind, wide=False):
    width = 1120 if wide else 520
    body = f'''<rect width="{width}" height="220" rx="16" fill="{{bg}}"/>
    <rect x="1" y="1" width="{width-2}" height="218" rx="15" fill="none" stroke="{{line}}"/>
    <rect x="{width-260}" y="18" width="240" height="185" fill="url(#grid)"/>'''
    if wide:
        body += '''<path d="M564 111H899" stroke="{line}" stroke-dasharray="2 7"/>
        <circle cx="564" cy="111" r="4" fill="{line}"/>'''
        body += text(580, 100, "REPAIR / REPEAT" if kind == "patch" else "REVISIT / REBUILD", size=13, mono=True, fill="muted")
    if kind == "patch":
        body += text(26, 38, "01 / UTILITY", size=15, mono=True, fill="muted")
        body += text(24, 101, "ag-repatch", size=50 if wide else 36, weight=700, extra='letter-spacing="-1"')
        body += text(26, 142, "Back in working order.", size=22 if wide else 17, fill="muted")
        body += text(26, 192, "PYTHON", size=14, mono=True, fill="accent")
        body += f'<g transform="translate({1005 if wide else 405} 111)">'
        body += '''
          <rect x="-57" y="-62" width="114" height="124" rx="16" fill="{panel}" stroke="{line}" transform="rotate(10)"/>
          <rect x="-57" y="-62" width="114" height="124" rx="16" fill="{bg}" stroke="{line}"/>
          <path d="M-57-29H57" stroke="{line}"/>
          <circle cx="-40" cy="-45" r="3" fill="{orange}"/>
          <circle cx="-28" cy="-45" r="3" fill="{muted}"/>
          <path d="M-25 1a29 29 0 1 1 0 28" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>
          <path d="M-27-10v15h15" fill="none" stroke="{accent}" stroke-width="5" stroke-linejoin="round"/>
          <path d="M-7 15l8 8 14-16" fill="none" stroke="{accent}" stroke-width="4" stroke-linejoin="round"/>
        </g>'''
        title, description = "ag-repatch", "Python-инструмент для восстановления локального патча Antigravity после обновлений."
    else:
        body += text(26, 38, "02 / SIDE QUEST", size=15, mono=True, fill="muted")
        body += text(24, 101, "Ловец душ", size=50 if wide else 36, weight=700, extra='letter-spacing="-1"')
        body += text(26, 142, "A second life for 2007.", size=22 if wide else 17, fill="muted")
        body += text(26, 192, "GODOT / ANDROID", size=14, mono=True, fill="orange")
        body += f'<g transform="translate({1004 if wide else 404} 111) rotate(9)">'
        body += '''
          <rect x="-48" y="-86" width="96" height="172" rx="17" fill="{panel}" stroke="{line}" stroke-width="2"/>
          <path d="M-10-72h20" stroke="{muted}" stroke-width="3" stroke-linecap="round"/>
          <rect x="-35" y="-59" width="70" height="85" rx="5" fill="{bg}" stroke="{line}"/>
          <path d="M-21-31h7v-9h7v9h14v-9h7v9h7v35h-7v-7h-7v7h-7v-7h-7v7h-7v-7h-7z" fill="{orange}"/>
          <rect x="-12" y="-21" width="7" height="7" fill="{bg}"/>
          <rect x="5" y="-21" width="7" height="7" fill="{bg}"/>
          <circle cy="44" r="8" fill="none" stroke="{muted}" stroke-width="2"/>
          <path d="M-29 44h9M20 44h9M-27 64h12M-6 64h12M15 64h12" stroke="{line}" stroke-width="4" stroke-linecap="round"/>
        </g>'''
        body += f'<g transform="translate({600 if wide else 0} 0)"><path d="M476 45v14m-7-7h14M329 169v10m-5-5h10" stroke="{{violet}}" stroke-width="2"/></g>'
        title, description = "Ловец душ", "Фанатский ремейк J2ME-квеста 2007 года для Android на Godot."
    return svg(width, 220, title, description, body, theme)


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            (ASSETS / f"header-{theme}{suffix}.svg").write_text(header(theme, mobile), encoding="utf-8")
        for kind in ("patch", "game"):
            for wide in (False, True):
                suffix = "-wide" if wide else ""
                (ASSETS / f"project-{kind}-{theme}{suffix}.svg").write_text(project(theme, kind, wide), encoding="utf-8")
    print("Generated 12 profile illustrations.")


if __name__ == "__main__":
    main()
