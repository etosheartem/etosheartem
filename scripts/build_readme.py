#!/usr/bin/env python3
"""Build Night Shift, a native, dark-only GitHub README incident game.

Run: python3 scripts/build_readme.py
Content: app/incidents.json. No dependencies, scripts in the README, backend,
issue creation, or external image services. Named <details> form exclusive
panels. <picture> prevents GitHub from turning summary images into links.
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
COLORS = dict(bg="#090e18", panel="#111b2b", line="#28374e", fg="#edf3ff",
              muted="#95a8c6", blue="#8abfff", amber="#f8c77c", red="#ff858f", green="#85e6bd")
SANS = "Arial, Helvetica, 'DejaVu Sans', sans-serif"
MONO = "'DejaVu Sans Mono', Consolas, monospace"


def txt(x, y, content, size=16, color="fg", *, mono=False, weight=400, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{MONO if mono else SANS}" '
            f'font-size="{size}" font-weight="{weight}" fill="{{{color}}}" {extra}>{escape(content)}</text>')


def svg(width, height, title, body):
    for key, value in COLORS.items():
        body = body.replace("{"+key+"}", value)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
  viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
  <title id="title">{escape(title)}</title>
  <style>
    .signal {{ animation: signal 4s ease-in-out infinite; }}
    @keyframes signal {{ 0%,100% {{ opacity:.4; }} 50% {{ opacity:1; }} }}
    @media (prefers-reduced-motion: reduce) {{ .signal {{ animation:none; }} }}
  </style>
  {body}
</svg>
'''


def masthead(mobile=False):
    width, height = (640, 324) if mobile else (1120, 282)
    b = f'<rect width="{width}" height="{height}" rx="12" fill="{{bg}}"/>'
    b += f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="11" fill="none" stroke="{{line}}"/>'
    b += '<circle class="signal" cx="31" cy="34" r="5" fill="{amber}"/>'
    b += txt(47, 40, "03:17 / ON CALL", 15, "amber", mono=True)
    b += txt(width-28, 40, "KUBERNETES LAB", 14, "muted", mono=True, extra='text-anchor="end"')
    b += txt(26, 125, "NIGHT SHIFT", 66 if mobile else 78, weight=800, extra='letter-spacing="-3"')
    if mobile:
        b += txt(30, 178, "Прод падает.", 31)
        b += txt(30, 219, "Твоя смена.", 31)
        b += '<path d="M30 252H610" stroke="{line}"/>'
        b += txt(30, 290, "3 ИНЦИДЕНТА / 9 РЕШЕНИЙ", 19, "blue", mono=True)
        b += txt(610, 290, "↓", 30, "blue", extra='text-anchor="end"')
    else:
        b += txt(30, 168, "Прод падает. Твоя смена.", 27)
        b += '<path d="M30 215H1090" stroke="{line}"/>'
        b += txt(30, 253, "DIAGNOSE → DECIDE → RESTORE", 16, "blue", mono=True)
        b += txt(1090, 253, "3 ИНЦИДЕНТА / 9 РЕШЕНИЙ", 15, "muted", mono=True, extra='text-anchor="end"')
        b += '<rect x="740" y="71" width="350" height="115" rx="6" fill="{panel}" stroke="{line}"/>'
        for i, (label, status, color) in enumerate([
            ("ROUTING", "503", "red"), ("MEMORY", "OOM", "amber"), ("SCHEDULER", "PENDING", "blue")
        ]):
            y=98+i*32
            b += f'<circle cx="762" cy="{y-5}" r="3" fill="{{{color}}}"/>'
            b += txt(776, y, label, 14, "muted", mono=True)
            b += txt(1067, y, status, 14, color, mono=True, extra='text-anchor="end"')
    return svg(width, height, "Night Shift — интерактивная смена дежурного Kubernetes", b)


def case_button(case, mobile=False):
    width, height = (560, 154) if mobile else (1120, 102)
    b = f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="7" fill="{{panel}}" stroke="{{line}}"/>'
    b += f'<path d="M1 15V{height-15}" stroke="{{amber}}" stroke-width="3"/>'
    b += txt(25, 85 if mobile else 60, case["number"], 27, "amber", mono=True)
    if mobile:
        b += txt(84, 65, case["mobile_title"][0], 36, weight=700)
        b += txt(84, 108, case["mobile_title"][1], 36, weight=700)
    else:
        b += txt(89, 45, case["title"], 30, weight=700)
        b += txt(90, 77, case["tag"], 14, "muted", mono=True)
        b += txt(1080, 61, "+", 35, "blue", mono=True, extra='text-anchor="end"')
    return svg(width, height, f'Открыть инцидент {case["number"]}: {case["title"]}', b)


def result_banner(success):
    color = "green" if success else "red"
    label = "INCIDENT RESOLVED" if success else "STILL BROKEN"
    b = '<rect x="1" y="1" width="598" height="76" rx="6" fill="{panel}" stroke="{line}"/>'
    b += f'<circle cx="37" cy="39" r="17" fill="none" stroke="{{{color}}}" stroke-width="2"/>'
    if success:
        b += '<path d="M29 39l6 6 11-13" fill="none" stroke="{green}" stroke-width="3"/>'
    else:
        b += '<path d="M31 33l12 12M43 33L31 45" stroke="{red}" stroke-width="3"/>'
    b += txt(75, 49, label, 30, color, mono=True)
    return svg(600, 78, "Инцидент закрыт" if success else "Проблема осталась — попробуй другое решение", b)


def picture(name, alt, *, responsive=False, width="100%", align=False):
    parts = ["<picture>"]
    if responsive:
        parts.append(f'<source media="(max-width: 600px)" srcset="assets/{name}-mobile.svg">')
    middle = ' align="middle"' if align else ''
    parts.append(f'<img src="assets/{name}.svg" width="{width}"{middle} alt="{escape(alt, quote=True)}">')
    parts.append("</picture>")
    return "".join(parts)


def pre(content):
    # Separate raw HTML blocks: GitHub otherwise reparses subsequent lines as
    # Markdown and destroys indentation in YAML evidence.
    return '\n\n<pre><code>'+escape(content)+'</code></pre>\n\n'


def panel(summary, body, group):
    return f'<details name="{group}">\n<summary>{summary}</summary>\n\n{body}\n\n</details>'


def incident(case):
    uid=case["id"]
    body=[f'<p>{escape(case["brief"])}</p>', '<p><strong>1 / Исследуй</strong> — нажимай на команды, чтобы увидеть вывод.</p>']
    for i, probe in enumerate(case["probes"], 1):
        summary=f'<kbd>{i}</kbd> <strong>{escape(probe["label"])}</strong>'
        contents=pre('$ '+probe["command"])+pre(probe["output"])+f'<p>{escape(probe["note"])}</p>'
        body.append(panel(summary, contents, f'{uid}-probes'))
    body.append('<p><strong>2 / Прими решение</strong> — выбери действие и посмотри, что изменится.</p>')
    for i, choice in enumerate(case["choices"]):
        summary=f'<kbd>{chr(65+i)}</kbd> <strong>{escape(choice["label"])}</strong>'
        contents=picture("resolved" if choice["success"] else "still-broken", "Инцидент закрыт" if choice["success"] else "Проблема осталась", width="360")
        contents += pre(choice["output"])
        contents += f'<p>{escape(choice["explanation"])}</p>'
        if choice["success"]:
            contents += f'<p><strong>{escape(case["lesson"])}</strong></p>'
            contents += f'<p><a href="{case["source"]}">Разобрать механизм в документации Kubernetes ↗</a></p>'
        else:
            contents += '<p><em>Попробуй другое действие или вернись к диагностике.</em></p>'
        body.append(panel(summary, contents, f'{uid}-decisions'))
    summary=picture('case-'+case["number"],case["title"],responsive=True,width="90%",align=True)
    return panel(summary,"\n\n".join(body),'night-shift-incidents')


def main():
    cases=json.loads((ROOT/'app/incidents.json').read_text(encoding='utf-8'))
    assert len(cases)==3 and len({c['id'] for c in cases})==3
    for case in cases:
        assert len(case['probes'])==3 and len(case['choices'])==3
        assert sum(choice['success'] for choice in case['choices'])==1
    ASSETS.mkdir(exist_ok=True)
    for mobile in (False,True):
        suffix='-mobile' if mobile else ''
        (ASSETS/f'night-shift{suffix}.svg').write_text(masthead(mobile),encoding='utf-8')
        for case in cases:
            (ASSETS/f'case-{case["number"]}{suffix}.svg').write_text(case_button(case,mobile),encoding='utf-8')
    for success in (False,True):
        name='resolved' if success else 'still-broken'
        (ASSETS/f'{name}.svg').write_text(result_banner(success),encoding='utf-8')
    readme='''<!-- Generated by scripts/build_readme.py. Edit app/incidents.json for the game. -->
'''+picture('night-shift','Night Shift — интерактивный Kubernetes incident lab',responsive=True)+'''

**Прими смену.** Выбери учебный инцидент → открой вывод команд → найди рабочее исправление.

<table width="100%"><tr><td>

'''+"\n\n".join(incident(case) for case in cases)+'''

</td></tr></table>

<sub>Выбор другого инцидента переключает панель. Можно исследовать и пробовать решения в любом порядке.</sub>

---

**Kubernetes · Linux · Python · Go**

<details>
<summary>Кто собрал этот стенд</summary>

Cloud & DevOps Engineer. Занимаюсь Kubernetes, инфраструктурой и автоматизацией. В работе — Helm, Docker, GitHub Actions, Python и Go. В домашней лаборатории — Arch, KVM/QEMU, MikroTik и WireGuard. Ещё интересуюсь AI-агентами и реверс-инжинирингом.

</details>

[ag-repatch](https://github.com/etosheartem/ag-repatch) — восстановление патча Antigravity · [Ловец душ](https://github.com/etosheartem/lovec-dush) — ремейк J2ME-квеста

**[Telegram ↗](https://t.me/etosheartem)**
'''
    (ROOT/'README.md').write_text(readme,encoding='utf-8')
    print('Built Night Shift: 3 incidents, 9 probes, 9 choices, 10 dark SVGs.')


if __name__=='__main__':
    main()
