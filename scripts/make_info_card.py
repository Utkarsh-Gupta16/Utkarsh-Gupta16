#!/usr/bin/env python3
"""
Generate a neofetch-style info card SVG that fades in line by line.
Reads configuration dynamically from profile.json to keep terminal titles consistent.
"""
import json
import os
import sys
import html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "profile.json")
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "info-card.svg")

# Layout
PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
LINE_H = 26
CARD_W = 490

# Colors (Matching the Andrew6rant / GitHub Dark theme)
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
TEXT = "#c9d1d9"
ACCENT = "#39d353"
DIM = "#8b949e"
DOTS = ["#ff5f56", "#ffbd2e", "#27c93f"]

STATIC = bool(os.environ.get("STATIC"))

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {CONFIG_PATH} not found.")
        sys.exit(1)

def build_lines(cfg):
    username = cfg.get("username", "user")
    name = cfg.get("name", username)
    role = cfg.get("role", "Developer")
    location = cfg.get("location", "Earth")
    stack = ", ".join(cfg.get("stack", []))
    highlights = ", ".join(cfg.get("highlights", []))
    
    return [
        (f"{username}@github", ACCENT),
        ("-" * 25, DIM),
        (f"Name      {name}", TEXT),
        (f"Role      {role}", TEXT),
        (f"Location  {location}", TEXT),
        (f"Stack     {stack}", TEXT),
        (f"Focus     {highlights}", TEXT),
    ]

def render(cfg):
    lines = build_lines(cfg)
    username = cfg.get("username", "user")
    
    card_h = TITLEBAR_H + PAD + len(lines) * LINE_H + STATUS_H
    
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{card_h}" '
        f'viewBox="0 0 {CARD_W} {card_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
    )
    
    # Background & Frame
    parts.append('<defs>'
                 f'<linearGradient id="cbg" x1="0" y1="0" x2="0" y2="1">'
                 f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
                 f'</linearGradient></defs>')
    parts.append(f'<rect width="{CARD_W}" height="{card_h}" rx="12" fill="url(#cbg)"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{CARD_W-1}" height="{card_h-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>')
    
    # Titlebar
    parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CARD_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
    for i, dotcol in enumerate(DOTS):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{CARD_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" text-anchor="middle">{html.escape(username)}@github: ~$ ./info.sh</text>')
    
    # Terminal Lines
    if STATIC:
        for i, (text, color) in enumerate(lines):
            y = TITLEBAR_H + PAD + i * LINE_H + 14
            parts.append(f'<text x="{PAD}" y="{y}" fill="{color}" font-size="13">{html.escape(text)}</text>')
    else:
        parts.append("<style>")
        parts.append(".il{opacity:0;animation:fi .4s ease-out forwards}")
        parts.append("@keyframes fi{to{opacity:1}}")
        parts.append("</style>")
        for i, (text, color) in enumerate(lines):
            delay = 0.3 + i * 0.15
            y = TITLEBAR_H + PAD + i * LINE_H + 14
            parts.append(f'<text class="il" style="animation-delay:{delay:.2f}s" x="{PAD}" y="{y}" fill="{color}" font-size="13">{html.escape(text)}</text>')
            
    # Status bar
    status_line_y = card_h - STATUS_H
    status_y = status_line_y + 19
    parts.append(f'<line x1="0" y1="{status_line_y}" x2="{CARD_W}" y2="{status_line_y}" stroke="{FRAME}"/>')
    
    cmd_str = f'{html.escape(username)}@github:~$ cat /etc/os-release'
    parts.append(f'<text x="{PAD}" y="{status_y}" fill="{TITLE_TEXT}" font-size="11">{cmd_str}</text>')
    
    # Blinking cursor in status bar
    cursor_x = PAD + (len(cmd_str) * 7.8) + 4
    parts.append(f'<rect x="{cursor_x:.1f}" y="{status_y-11}" width="7" height="13" fill="{TEXT}">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')

    parts.append("</svg>")
    return "".join(parts)

if __name__ == "__main__":
    cfg = load_config()
    svg = render(cfg)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")