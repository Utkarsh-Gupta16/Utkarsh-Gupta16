#!/usr/bin/env python3
"""
Generate a sleek, self-typing wordmark SVG for the top of the profile.
Uses a clip-path wipe to avoid character-spacing bugs on GitHub.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "profile.json")
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "wordmark.svg")

# Layout
SVG_W = 860
FONT_SIZE = 48
# Approximate width multiplier for heavy monospace fonts
CHAR_W = FONT_SIZE * 0.6 

# Colors
BG = "#0d1117"
INK = "#e6edf3"
CURSOR_CLR = "#39d353"

ANIM_DUR = 1.2 # seconds for the wipe

STATIC = bool(os.environ.get("STATIC"))

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {CONFIG_PATH} not found.")
        sys.exit(1)

def render(cfg):
    # Use wordmark if available, otherwise fallback to name/username
    wordmark = cfg.get("wordmark") or cfg.get("name", "user")
    
    text_w = len(wordmark) * CHAR_W
    text_x = (SVG_W - text_w) / 2
    text_y = 55
    
    cursor_w = 4
    cursor_h = FONT_SIZE * 0.8
    cursor_y = text_y - FONT_SIZE * 0.7
    
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="80" viewBox="0 0 {SVG_W} 80" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
    )
    parts.append(f'<rect width="{SVG_W}" height="80" fill="{BG}"/>')
    
    if STATIC:
        parts.append(f'<text x="{text_x}" y="{text_y}" fill="{INK}" font-size="{FONT_SIZE}" font-weight="700">{wordmark}</text>')
    else:
        # Defs for clip wipe
        parts.append('<defs>')
        parts.append(f'<clipPath id="wm-clip"><rect x="{text_x}" y="0" width="0" height="80">'
                     f'<animate attributeName="width" from="0" to="{text_w}" dur="{ANIM_DUR}s" fill="freeze"/>'
                     f'</rect></clipPath>')
        parts.append('</defs>')
        
        # Text wrapped in clip
        parts.append(f'<g clip-path="url(#wm-clip)">'
                     f'<text x="{text_x}" y="{text_y}" fill="{INK}" font-size="{FONT_SIZE}" font-weight="700">{wordmark}</text>'
                     f'</g>')
        
        # Cursor riding the wipe edge
        parts.append(f'<rect x="{text_x}" y="{cursor_y}" width="{cursor_w}" height="{cursor_h}" fill="{CURSOR_CLR}">'
                     f'<animate attributeName="x" from="{text_x}" to="{text_x + text_w}" dur="{ANIM_DUR}s" fill="freeze"/>'
                     f'<set attributeName="opacity" to="1" begin="0s"/>'
                     f'<set attributeName="opacity" to="0" begin="{ANIM_DUR}s"/>'
                     f'</rect>')
                     
        # Steady blinking cursor after typing finishes
        parts.append(f'<rect x="{text_x + text_w + 4}" y="{cursor_y}" width="{cursor_w}" height="{cursor_h}" fill="{CURSOR_CLR}" opacity="0">'
                     f'<set attributeName="opacity" to="1" begin="{ANIM_DUR}s"/>'
                     f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" begin="{ANIM_DUR}s" repeatCount="indefinite"/>'
                     f'</rect>')

    parts.append("</svg>")
    return "".join(parts)

if __name__ == "__main__":
    cfg = load_config()
    svg = render(cfg)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")