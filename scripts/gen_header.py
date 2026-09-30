#!/usr/bin/env python3
"""Generate the animated profile SVGs (assets/header.svg, terminal.svg, neofetch.svg).

GitHub READMEs strip CSS/JS, but CSS and SMIL animations inside an SVG served
through <img> still play, so everything here is plain self-contained SVG.
Edit TERMINAL / NEOFETCH below and re-run: python3 scripts/gen_header.py
"""
import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# Tokyo Night palette
BG = "#1a1b26"
BG_DARK = "#16161e"
FG = "#c0caf5"
COMMENT = "#565f89"
BLUE = "#7aa2f7"
CYAN = "#7dcfff"
GREEN = "#9ece6a"
PURPLE = "#bb9af7"
YELLOW = "#e0af68"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

# Each step: a typed command followed by its output lines.
# Output lines are lists of (text, color) segments.
TERMINAL = [
    ("cat about.yaml", [
        [("name", BLUE), (": ", COMMENT), ("Artem", GREEN)],
        [("role", BLUE), (": ", COMMENT), ("Cloud & DevOps Engineer / Python Developer", GREEN)],
        [("focus", BLUE), (":", COMMENT)],
        [("  - ", COMMENT), ("Cloud-Native Infrastructure & Kubernetes", GREEN)],
        [("  - ", COMMENT), ("System Automation & Internal Tooling", GREEN)],
        [("  - ", COMMENT), ("AI Agents & LLM Integrations", GREEN)],
        [("current_stack", BLUE), (": [", COMMENT), ("Kubernetes, Python, Docker, Linux, MikroTik", GREEN), ("]", COMMENT)],
        [("motto", BLUE), (": ", COMMENT), ('"Automate everything, keep it lean and rock-solid."', YELLOW)],
    ]),
    ("ls ~/work", [
        [("devops/    ", BLUE), ("Kubernetes · Docker · Helm — reliable infrastructure", FG)],
        [("python/    ", BLUE), ("CLI tools · async microservices · Telegram bots · AI agents", FG)],
        [("homelab/   ", BLUE), ("Arch · KVM/libvirt · MikroTik RouterOS · WireGuard/AmneziaWG", FG)],
        [("lowlevel/  ", BLUE), ("reverse engineering · binary patching (ag-repatch) · perf", FG)],
    ]),
    ("kubectl get pods -n tooling", [
        [("NAME                 READY   STATUS    AGE", COMMENT)],
        [("telegram-llm-bot     1/1     ", FG), ("Running", GREEN), ("   42d", FG)],
        [("ai-agent-worker      1/1     ", FG), ("Running", GREEN), ("   17d", FG)],
        [("ag-repatch           1/1     ", FG), ("Running", GREEN), ("   9d", FG)],
    ]),
]
PROMPT = [("artem", GREEN), ("@", COMMENT), ("homelab", BLUE), (":", COMMENT), ("~", CYAN), ("$ ", FG)]

ARCH_BLUE = "#1793d1"
ARCH_LOGO = [
    "                  -`",
    "                 .o+`",
    "                `ooo/",
    "               `+oooo:",
    "              `+oooooo:",
    "              -+oooooo+:",
    "            `/:-:++oooo+:",
    "           `/++++/+++++++:",
    "          `/++++++++++++++:",
    "         `/+++ooooooooooooo/`",
    "        ./ooosssso++osssssso+`",
    "       .oossssso-````/ossssss+`",
    "      -osssssso.      :ssssssso.",
    "     :osssssss/        osssso+++.",
    "    /ossssssss/        +ssssooo/-",
    "  `/ossssso+/:-        -:/+osssso+-",
    " `+sso+:-`                 `.-/+oso:",
    "`++:.                           `-/+/",
    ".`                                 `/",
]
# The tech stack, neofetch style
NEOFETCH = [
    ("OS", "Arch Linux x86_64 · Debian"),
    ("Virt", "KVM/QEMU · libvirt · Proxmox VE"),
    ("Network", "MikroTik RouterOS"),
    ("VPN", "WireGuard · AmneziaWG"),
    ("Cloud", "Kubernetes · Docker · Helm"),
    ("CI/CD", "GitHub Actions"),
    ("Langs", "Python · Go · Bash · SQL"),
    ("DB", "PostgreSQL · Redis"),
    ("AI", "LLM Agents · Telegram Bots"),
    ("IDE", "Google Antigravity"),
    ("VCS", "Git"),
]
PALETTE = [
    ["#15161e", "#f7768e", "#9ece6a", "#e0af68", "#7aa2f7", "#bb9af7", "#7dcfff", "#a9b1d6"],
    ["#414868", "#ff899d", "#9fe044", "#faba4a", "#8db0ff", "#c7a9ff", "#a4daff", "#c0caf5"],
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def spans(segments) -> str:
    return "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in segments)


def pct(t: float, total: float) -> str:
    return f"{t / total * 100:.3f}%"


class Term:
    """A looping terminal window: typed commands, lines that pop in, then a fade and restart."""

    font, cw, lh = 16.5, 9.93, 25  # font size, char width, line height
    pad_x, top, width = 26, 68, 860
    char_time, out_gap = 0.075, 0.35

    def __init__(self, label: str):
        self.label = label
        self.items = []  # (kind, row, col, start, data)
        self.rows = 0

    def x(self, col: float) -> float:
        return self.pad_x + col * self.cw

    def cmd(self, row: int, start: float, command: str) -> float:
        """Type a command after the prompt; returns when its output may start."""
        self.items.append(("cmd", row, 0, start, command))
        self.rows = max(self.rows, row + 1)
        return start + len(command) * self.char_time + self.out_gap

    def line(self, row: int, start: float, segments, col: float = 0) -> None:
        self.items.append(("out", row, col, start, segments))
        self.rows = max(self.rows, row + 1)

    def blocks(self, row: int, start: float, colors, col: float = 0, size: int = 3) -> None:
        self.items.append(("blocks", row, col, start, (colors, size)))
        self.rows = max(self.rows, row + 1)

    def render(self, idle_row: int, idle_at: float, hold: float = 4.5) -> str:
        font, cw, lh, top = self.font, self.cw, self.lh, self.top
        total = idle_at + hold + 0.8
        fade_start = idle_at + hold
        prompt_len = sum(len(t) for t, _ in PROMPT)
        css, body = [], []

        def appear(name: str, start: float) -> None:
            css.append(
                f"@keyframes {name}{{0%,{pct(start, total)}{{opacity:0}}"
                f"{pct(start + 0.01, total)},100%{{opacity:1}}}}"
                f".{name}{{opacity:0;animation:{name} {total:.2f}s infinite}}"
            )

        for i, (kind, row, col, start, data) in enumerate(self.items):
            y, x, name = top + row * lh, self.x(col), f"r{i}"
            appear(name, start)
            if kind == "out":
                body.append(f'<text class="{name}" x="{x:.1f}" y="{y}">{spans(data)}</text>')
                continue
            if kind == "blocks":
                colors, size = data
                rects = "".join(
                    f'<rect x="{x + j * size * cw:.1f}" y="{y - font + 1}" width="{size * cw:.1f}" height="{lh - 3}" fill="{c}"/>'
                    for j, c in enumerate(colors)
                )
                body.append(f'<g class="{name}">{rects}</g>')
                continue
            # Prompt line: prompt appears, then the command is revealed char by char
            cx = self.x(prompt_len)
            w = len(data) * cw
            end = start + len(data) * self.char_time
            cover = f"c{i}"
            css.append(
                f"@keyframes {cover}{{0%,{pct(start, total)}{{transform:translateX(0)}}"
                f"{pct(end, total)},100%{{transform:translateX({w:.1f}px)}}}}"
                f".{cover}{{animation:{cover} {total:.2f}s infinite;"
                f"animation-timing-function:steps({len(data)},end)}}"
            )
            # Cursor rides on the cover's left edge while typing, then hides once output starts
            cur = f"k{i}"
            css.append(
                f"@keyframes {cur}{{0%,{pct(start, total)}{{opacity:0}}"
                f"{pct(start + 0.01, total)},{pct(end + self.out_gap - 0.02, total)}{{opacity:1}}"
                f"{pct(end + self.out_gap, total)},100%{{opacity:0}}}}"
                f".{cur}{{opacity:0;animation:{cur} {total:.2f}s infinite}}"
            )
            body.append(
                f'<g class="{name}"><text x="{x:.1f}" y="{y}">{spans(PROMPT)}'
                f'<tspan fill="{FG}">{esc(data)}</tspan></text>'
                f'<g class="{cover}"><rect x="{cx:.1f}" y="{y - font}" width="{w + cw * 2:.1f}" height="{lh}" fill="{BG}"/>'
                f'<rect class="{cur}" x="{cx:.1f}" y="{y - font + 2}" width="{cw:.1f}" height="{font + 3}" fill="{FG}"/></g></g>'
            )

        # Final idle prompt with a blinking cursor
        y = top + idle_row * lh
        appear("fin", idle_at)
        body.append(
            f'<g class="fin"><text x="{self.pad_x}" y="{y}">{spans(PROMPT)}</text>'
            f'<rect class="blink" x="{self.x(prompt_len):.1f}" y="{y - font + 2}" width="{cw:.1f}" height="{font + 3}" fill="{FG}"/></g>'
        )
        css.append("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.blink{animation:blink 1s step-end infinite}")
        css.append(
            f"@keyframes screen{{0%,{pct(fade_start, total)}{{opacity:1}}{pct(total - 0.15, total)},100%{{opacity:0}}}}"
            f".screen{{animation:screen {total:.2f}s infinite}}"
        )
        css.append(f"text{{font-family:{MONO};font-size:{font}px;white-space:pre}}")

        width = self.width
        height = top + idle_row * lh + 26
        dots = "".join(
            f'<circle cx="{22 + i * 20}" cy="20" r="6" fill="{c}"/>'
            for i, c in enumerate(["#f7768e", YELLOW, GREEN])
        )
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(self.label)}">
<style>{"".join(css)}</style>
<defs><linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient></defs>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="{BG}" stroke="url(#edge)" stroke-opacity="0.55" stroke-width="1.5"/>
<path d="M1 13a12 12 0 0 1 12-12h{width - 26}a12 12 0 0 1 12 12v27H1z" fill="{BG_DARK}"/>
{dots}
<text x="{width / 2}" y="25" text-anchor="middle" fill="{COMMENT}" style="font-size:14px">artem@homelab: ~</text>
<g class="screen" xml:space="preserve">{"".join(body)}</g>
</svg>
"""


def terminal_svg() -> str:
    term = Term("Terminal: about Artem — Cloud & DevOps Engineer, Python Developer")
    t, row = 0.6, 0
    for command, outputs in TERMINAL:
        t = term.cmd(row, t, command)
        row += 1
        for segments in outputs:
            term.line(row, t, segments)
            t += 0.12
            row += 1
        t += 0.55
    return term.render(row, t)


def neofetch_svg() -> str:
    term = Term("neofetch: Arch Linux, " + ", ".join(v for _, v in NEOFETCH))
    t = term.cmd(0, 0.6, "neofetch")
    for i, logo_line in enumerate(ARCH_LOGO):
        term.line(1 + i, t + i * 0.03, [(logo_line, ARCH_BLUE if i < 9 else BLUE)])

    info_col = max(len(l) for l in ARCH_LOGO) + 4
    info = [
        [("artem", ARCH_BLUE), ("@", FG), ("homelab", ARCH_BLUE)],
        [("-" * len("artem@homelab"), FG)],
    ] + [[(f"{key}: ", ARCH_BLUE), (value, FG)] for key, value in NEOFETCH]
    t += 0.45
    for i, segments in enumerate(info):
        term.line(1 + i, t + i * 0.1, segments, col=info_col)
    t += len(info) * 0.1 + 0.2
    term.blocks(len(info) + 2, t, PALETTE[0], col=info_col)
    term.blocks(len(info) + 3, t + 0.15, PALETTE[1], col=info_col)
    t += 0.7
    return term.render(len(ARCH_LOGO) + 2, t, hold=7)


def banner_svg() -> str:
    rnd = random.Random(42)
    width, height = 1200, 250

    stars = []
    for _ in range(90):
        x, y = rnd.uniform(0, width), rnd.uniform(0, height - 50)
        r = rnd.choice([0.6, 0.8, 1.0, 1.2, 1.6])
        dur, delay = rnd.uniform(2.2, 5.5), rnd.uniform(0, 5)
        stars.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="tw" '
            f'style="animation-duration:{dur:.2f}s;animation-delay:-{delay:.2f}s"/>'
        )

    sparkles = []
    for x, y, s, d in [(140, 60, 1.0, 0), (1010, 48, 1.2, 1.6), (880, 150, 0.8, 3.1), (300, 170, 0.9, 2.2)]:
        sparkles.append(
            f'<g transform="translate({x} {y}) scale({s})"><path class="sp" style="animation-delay:-{d}s" '
            f'd="M0-9L2-2 9 0 2 2 0 9-2 2-9 0-2-2z" fill="{CYAN}"/></g>'
        )

    def wave(a: float, b: float) -> str:
        return (f"M0 0H{width}V{height - 40 + a:.0f}"
                f"C{width * 0.8:.0f} {height - 10 + b:.0f} {width * 0.62:.0f} {height - 70 - b:.0f} {width * 0.45:.0f} {height - 35:.0f}"
                f"S{width * 0.12:.0f} {height - 5 - a:.0f} 0 {height - 45:.0f}Z")

    waves = ";".join([wave(0, 0), wave(12, -14), wave(0, 0)])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Hi there, I'm Artem">
<style>
.tw{{fill:#fff;animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.95}}}}
.sp{{animation:sp 4.5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes sp{{0%,100%{{opacity:0;transform:scale(.3) rotate(0)}}50%{{opacity:1;transform:scale(1) rotate(90deg)}}}}
.shoot{{animation:shoot 9s linear infinite;opacity:0}}
.shoot.b{{animation-delay:4.7s;animation-duration:11s}}
@keyframes shoot{{0%{{transform:translate(0,0);opacity:0}}2%{{opacity:1}}9%{{transform:translate(-420px,210px);opacity:0}}100%{{transform:translate(-420px,210px);opacity:0}}}}
.title{{font:800 50px {SANS};fill:#fff;animation:rise 1.4s cubic-bezier(.2,.8,.2,1) both}}
.sub{{font:600 17px {MONO};fill:{CYAN};letter-spacing:4px;animation:rise 1.4s .35s cubic-bezier(.2,.8,.2,1) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.hand{{font:48px {SANS};transform-box:fill-box;transform-origin:70% 80%;animation:wave 2.6s ease-in-out 1s infinite}}
@keyframes wave{{0%,60%,100%{{transform:rotate(0)}}10%,30%{{transform:rotate(14deg)}}20%{{transform:rotate(-8deg)}}40%{{transform:rotate(-4deg)}}50%{{transform:rotate(10deg)}}}}
</style>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{BG_DARK}"><animate attributeName="stop-color" values="{BG_DARK};#1f2335;{BG_DARK}" dur="12s" repeatCount="indefinite"/></stop>
<stop offset=".55" stop-color="#24283b"><animate attributeName="stop-color" values="#24283b;#2e3c64;#24283b" dur="12s" repeatCount="indefinite"/></stop>
<stop offset="1" stop-color="#3d59a1"><animate attributeName="stop-color" values="#3d59a1;#6b4fa8;#3d59a1" dur="12s" repeatCount="indefinite"/></stop>
</linearGradient>
<radialGradient id="glow" cx=".5" cy=".45" r=".5"><stop offset="0" stop-color="{BLUE}" stop-opacity=".28"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="wave"><path d="{wave(0, 0)}"><animate attributeName="d" values="{waves}" dur="8s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></path></clipPath>
</defs>
<g clip-path="url(#wave)">
<rect width="{width}" height="{height}" fill="url(#sky)"/>
<ellipse cx="{width / 2}" cy="110" rx="420" ry="120" fill="url(#glow)"/>
{"".join(stars)}
{"".join(sparkles)}
<g class="shoot"><line x1="1000" y1="10" x2="1090" y2="-35" stroke="url(#trail)" stroke-width="2" stroke-linecap="round"/></g>
<g class="shoot b"><line x1="760" y1="0" x2="830" y2="-35" stroke="url(#trail)" stroke-width="1.6" stroke-linecap="round"/></g>
<text class="title" x="342" y="118" textLength="468" lengthAdjust="spacingAndGlyphs">Hi there, I'm Artem</text>
<text class="hand" x="826" y="116">👋</text>
<text class="sub" x="{width / 2}" y="160" text-anchor="middle">CLOUD · DEVOPS · PYTHON · LINUX</text>
</g>
</svg>
"""


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "header.svg").write_text(banner_svg(), encoding="utf-8")
    (ASSETS / "terminal.svg").write_text(terminal_svg(), encoding="utf-8")
    (ASSETS / "neofetch.svg").write_text(neofetch_svg(), encoding="utf-8")
    print("wrote header.svg, terminal.svg and neofetch.svg to", ASSETS)
