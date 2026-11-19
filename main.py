#!/usr/bin/env python3
"""news-image-20261119 — "Sum up 19 November's world news in one image".

A one-page newspaper front page for Thursday 19 November 2026, drawn
pixel by pixel with pure Python stdlib. No network, no clock, no random:
two runs produce byte-identical PNG output.

Lead story: Grand Theft Auto VI begins its global rollout (midnight by
midnight, New Zealand first, after a 13-year wait). Supporting stories:
Hakeem Jeffries wins the House Speaker nomination; the US and Iran trade
fire in the Gulf; Voyager 1 reaches one light-day from Earth; the EU
proposes a EUR 45bn loan for Ukraine; Cyclone Akvan nears India's east
coast; Nvidia's acting CEO promises earlier pay rises. Ticker: the
Trump-Xi-Putin trilateral in Shenzhen, Fed minutes, Pew on world faiths.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Canvas: 1024 x 1024, PNG under 1 MiB.
"""

import os
import struct
import zlib
from binascii import crc32

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)   # newsprint cream
INK = (22, 22, 22)        # near-black ink
GREY = (110, 104, 90)
RULE = (60, 56, 48)
SUNSET_TOP = (232, 106, 44)   # orange dusk
SUNSET_MID = (226, 122, 122)  # pink band
SUNSET_LOW = (245, 178, 110)  # pale horizon
SEA = (31, 122, 107)          # teal sea
SKYLINE = (38, 28, 52)        # dusk purple silhouettes
SUN = (255, 214, 90)
ACCENT_RED = (179, 38, 30)
ACCENT_BLUE = (29, 78, 158)
ACCENT_TEAL = (31, 122, 107)
WHITE = (255, 255, 255)
PANEL_BG = (255, 253, 246)

# ------------------------------------------------------------------- font
# Hand-drawn 5x7 bitmap font, uppercase + digits + punctuation only.
# Each glyph: 7 rows of 5 bits. Unknown chars render as blank.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '"': ["01010", "01010", "01010", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "—": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "•": ["00000", "00000", "01100", "01100", "01100", "00000", "00000"],
    "*": ["00000", "00100", "10101", "01110", "10101", "00100", "00000"],
}
CHAR_W = 6  # 5 glyph columns + 1 spacing column


def text_width(s, scale):
    return len(s) * CHAR_W * scale - scale


def draw_text(px, x, y, s, scale, color):
    """Draw uppercase text; returns width in pixels."""
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(px, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += CHAR_W * scale
    return cx - x - scale


def draw_text_centered(px, x, y, w, s, scale, color):
    tw = text_width(s, scale)
    draw_text(px, x + (w - tw) // 2, y, s, scale, color)


def wrap_text(s, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    words = s.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ----------------------------------------------------------------- canvas
def new_canvas():
    buf = bytearray(W * H * 3)
    for i in range(0, len(buf), 3):
        buf[i] = PAPER[0]
        buf[i + 1] = PAPER[1]
        buf[i + 2] = PAPER[2]
    return buf


def set_px(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = color[0]
        px[i + 1] = color[1]
        px[i + 2] = color[2]


def fill_rect(px, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i] = color[0]
            px[i + 1] = color[1]
            px[i + 2] = color[2]


def hline(px, x, y, w, color, thick=1):
    fill_rect(px, x, y, w, thick, color)


def vline(px, x, y, h, color, thick=1):
    fill_rect(px, x, y, thick, h, color)


def draw_rect(px, x, y, w, h, color, thick=1):
    hline(px, x, y, w, color, thick)
    hline(px, x, y + h - thick, w, color, thick)
    vline(px, x, y, h, color, thick)
    vline(px, x + w - thick, y, h, color, thick)


def line(px, x0, y0, x1, y1, color, thick=1):
    """Bresenham line with square brush."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        fill_rect(px, x0 - thick // 2, y0 - thick // 2, thick, thick, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else 0
        fill_rect(px, cx - dx, yy, dx * 2 + 1, 1, color)


def circle_outline(px, cx, cy, r, color, thick=2):
    for a in range(360):
        import math
        x = cx + int(r * math.cos(math.radians(a)))
        y = cy + int(r * math.sin(math.radians(a)))
        fill_rect(px, x - thick // 2, y - thick // 2, thick, thick, color)


# -------------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(px, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += px[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- hero art
def draw_hero(px, x, y, w, h):
    """Vice City at dusk: sunset sky, sun, skyline, palms, teal sea."""
    # Sky: three horizontal bands, orange -> pink -> pale.
    fill_rect(px, x, y, w, h // 3, SUNSET_TOP)
    fill_rect(px, x, y + h // 3, w, h // 3, SUNSET_MID)
    fill_rect(px, x, y + 2 * h // 3, w, h - 2 * h // 3, SUNSET_LOW)
    # Sun with horizontal slats (retro sunset).
    sun_cx, sun_cy, sun_r = x + w // 2, y + h // 2 - 6, 52
    fill_circle(px, sun_cx, sun_cy, sun_r, SUN)
    for i in range(4):
        gap_y = sun_cy + 8 + i * 9
        fill_rect(px, sun_cx - sun_r, gap_y, sun_r * 2, 4, SUNSET_MID)
    # Skyline silhouettes: a row of towers of fixed heights.
    base = y + h - 58
    towers = [(0, 96, 120), (70, 60, 150), (130, 84, 96), (210, 110, 128),
              (300, 70, 108), (360, 92, 140), (440, 64, 100), (500, 118, 132),
              (600, 76, 110), (670, 100, 138), (760, 62, 104), (820, 92, 126),
              (900, 70, 96)]
    for tx, tw, th in towers:
        fill_rect(px, x + tx, base - th, tw, th + 58, SKYLINE)
    # Lit windows: fixed grid of tiny warm squares on the towers.
    for tx, tw, th in towers:
        for wy in range(base - th + 10, base - 6, 18):
            for wx in range(x + tx + 10, x + tx + tw - 8, 20):
                if (wx * 7 + wy * 13) % 5 < 2:
                    fill_rect(px, wx, wy, 6, 8, SUN)
    # Palm trees: trunk + five fronds, left and right.
    for palm_x, palm_h in ((x + 52, 96), (x + w - 52, 110)):
        line(px, palm_x, base + 58, palm_x + 6, base + 58 - palm_h, SKYLINE, 5)
        top_x, top_y = palm_x + 6, base + 58 - palm_h
        for dx, dy in ((-34, -16), (-26, -30), (0, -36), (26, -30), (36, -14),
                       (-18, -6), (20, -6)):
            line(px, top_x, top_y, top_x + dx, top_y + dy, SKYLINE, 4)
    # Sea strip at the bottom with a sun reflection.
    fill_rect(px, x, base + 34, w, h - (base + 34 - y), SEA)
    for i in range(6):
        rw = 90 - i * 10
        fill_rect(px, sun_cx - rw // 2, base + 40 + i * 7, rw, 3, SUN)
    draw_rect(px, x, y, w, h, INK, 3)


# -------------------------------------------------------------- icons
def icon_capitol(px, x, y, s, color):
    """US Capitol dome + columns."""
    # Dome.
    for r in range(s // 2, 0, -1):
        fill_rect(px, x + s // 2 - r, y + s // 2 - r, r * 2, 2, color)
    fill_rect(px, x, y + s // 2, s, 3, color)
    vline(px, x + s // 2, y - 6, 8, color, 3)
    fill_circle(px, x + s // 2, y - 8, 3, color)
    # Columns.
    for cx in range(4):
        vline(px, x + 4 + cx * (s - 8) // 3, y + s // 2 + 4, s // 2 - 2,
              color, 3)
    hline(px, x, y + s - 2, s, color, 3)


def icon_fire(px, x, y, s, color):
    """Two crossing missile trails + burst."""
    line(px, x + 4, y + s - 4, x + s - 8, y + 6, color, 3)
    line(px, x + s - 4, y + s - 4, x + 8, y + 6, color, 3)
    # Arrowheads.
    fill_rect(px, x + s - 12, y + 2, 10, 4, color)
    fill_rect(px, x + 2, y + 2, 10, 4, color)
    # Burst star at the crossing.
    cx, cy = x + s // 2, y + s // 2
    for dx, dy in ((0, -8), (0, 8), (-8, 0), (8, 0), (-6, -6), (6, -6),
                   (-6, 6), (6, 6)):
        line(px, cx, cy, cx + dx, cy + dy, ACCENT_RED, 3)


def icon_voyager(px, x, y, s, color):
    """Deep-space probe: dish, body, antenna, stars."""
    for sx, sy in ((x + 2, y + 2), (x + s - 6, y + 6), (x + 8, y + s - 4),
                   (x + s - 2, y + s - 8)):
        fill_rect(px, sx, sy, 3, 3, color)
    cx, cy = x + s // 2, y + s // 2
    circle_outline(px, cx, cy, s // 3, color, 3)
    line(px, cx, cy, cx + s // 3, cy - s // 3, color, 3)
    fill_rect(px, cx - 4, cy - 4, 9, 9, color)
    line(px, cx + 4, cy - 4, cx + s // 2, cy - s // 2, color, 2)
    fill_rect(px, cx + s // 2 - 2, cy - s // 2 - 2, 4, 4, ACCENT_RED)


def icon_eu(px, x, y, s, color):
    """Circle of stars + euro sign."""
    import math
    cx, cy = x + s // 2, y + s // 2
    for k in range(12):
        a = math.radians(k * 30 - 90)
        sx = cx + int((s // 2 - 4) * math.cos(a))
        sy = cy + int((s // 2 - 4) * math.sin(a))
        fill_rect(px, sx - 2, sy - 2, 5, 5, ACCENT_BLUE)
    # Euro: a C with two bars.
    fill_rect(px, cx - 9, cy - 8, 16, 4, color)
    fill_rect(px, cx - 9, cy - 8, 4, 16, color)
    fill_rect(px, cx - 9, cy + 4, 16, 4, color)
    hline(px, cx - 12, cy - 3, 22, color, 3)
    hline(px, cx - 12, cy + 1, 22, color, 3)


def icon_cyclone(px, x, y, s, color):
    """Spiral storm: concentric broken arcs."""
    cx, cy = x + s // 2, y + s // 2
    for r in (6, 12, 18, 24):
        circle_outline(px, cx, cy, r, color if r % 12 else ACCENT_TEAL, 3)
    fill_circle(px, cx, cy, 4, ACCENT_RED)
    line(px, cx, cy - s // 2, cx + 8, cy - s // 2 + 10, color, 3)


def icon_chip(px, x, y, s, color):
    """Microchip with pins."""
    fill_rect(px, x + 6, y + 6, s - 12, s - 12, color)
    fill_rect(px, x + 14, y + 14, s - 28, s - 28, PAPER)
    draw_text(px, x + 18, y + 18, "NV", 2, color)
    for i in range(4):
        off = 12 + i * (s - 24) // 3
        hline(px, x, y + off, 8, color, 3)
        hline(px, x + s - 8, y + off, 8, color, 3)
        vline(px, x + off, y, 8, color, 3)
        vline(px, x + off, y + s - 8, 8, color, 3)


# -------------------------------------------------------------- panels
def draw_panel(px, x, y, w, h, kicker, headline, body, icon_fn, accent):
    fill_rect(px, x, y, w, h, PANEL_BG)
    draw_rect(px, x, y, w, h, INK, 2)
    # Kicker bar.
    fill_rect(px, x + 2, y + 2, w - 4, 22, accent)
    draw_text(px, x + 10, y + 7, kicker, 2, WHITE)
    # Icon, top-right of the kicker row.
    icon_fn(px, x + w - 62, y + 30, 46, INK)
    # Headline, wrapped, scale 3.
    lines = wrap_text(headline, w - 78, 3)
    ty = y + 32
    for ln in lines:
        draw_text(px, x + 10, ty, ln, 3, INK)
        ty += 24
    # Rule, then body text scale 2.
    hline(px, x + 10, ty + 2, w - 20, RULE, 2)
    ty += 12
    for ln in wrap_text(body, w - 20, 2):
        draw_text(px, x + 10, ty, ln, 2, INK)
        ty += 17


# ----------------------------------------------------------------- page
def build():
    px = new_canvas()
    mx = 24  # margin
    cw = W - 2 * mx  # content width = 976

    # Masthead: black band, paper name + tagline.
    fill_rect(px, mx, 24, cw, 74, INK)
    draw_text_centered(px, mx, 34, cw, "THE WORLD", 11, WHITE)
    draw_text_centered(px, mx, 84, cw, "ONE IMAGE - THE WHOLE DAY",
                       2, GREY)
    # Dateline.
    draw_text_centered(px, mx, 108, cw,
                       "THURSDAY 19 NOVEMBER 2026", 3, INK)
    hline(px, mx, 132, cw, INK, 3)
    hline(px, mx, 137, cw, INK, 1)

    # Lead headline + subhead.
    draw_text_centered(px, mx, 150, cw, "GTA VI ARRIVES", 8, INK)
    draw_text_centered(px, mx, 208, cw,
                       "AFTER 13 YEARS, VICE CITY OPENS - MIDNIGHT BY MIDNIGHT",
                       2, INK)

    # Hero art + caption.
    draw_hero(px, mx, 232, cw, 208)
    draw_text_centered(px, mx, 448, cw,
                       "16M COPIES PRE-SOLD - $1.5BN - METACRITIC 99 - PS5 + XBOX",
                       2, INK)

    # Story grid: 3 columns x 2 rows.
    gw, gh, gap = 312, 196, 20
    gy = 476
    stories = [
        ("WASHINGTON", "JEFFRIES WINS SPEAKER NOMINATION",
         "251 DEMOCRATS BACK HIM IN A SECRET BALLOT. FIRST BLACK SPEAKER "
         "NOMINEE; FORMAL VOTE 3 JAN.",
         icon_capitol, ACCENT_BLUE),
        ("MIDDLE EAST", "US AND IRAN TRADE FIRE",
         "US HIT A MISSILE SITE ON QESHM ISLAND; IRAN STRUCK BASES IN "
         "BAHRAIN AND KUWAIT.",
         icon_fire, ACCENT_RED),
        ("SPACE", "VOYAGER 1 HITS ONE LIGHT-DAY",
         "AFTER NEARLY 50 YEARS IN FLIGHT, THE PROBE IS A FULL LIGHT-DAY "
         "FROM EARTH.",
         icon_voyager, ACCENT_TEAL),
        ("EUROPE", "EU PLANS 45BN EURO LOAN FOR KYIV",
         "TO BE REPAID AFTER RUSSIA PAYS REPARATIONS, THE COMMISSION "
         "PROPOSES.",
         icon_eu, ACCENT_BLUE),
        ("INDIA", "CYCLONE AKVAN NEARS EAST COAST",
         "LANDFALL EXPECTED BETWEEN MACHILIPATNAM AND PURI; RAILWAYS ON "
         "ALERT.",
         icon_cyclone, ACCENT_TEAL),
        ("TECH", "NVIDIA AFTER HUANG",
         "ACTING CEO KRESS PROMISES EARLIER PAY RISES; H-SERIES CHIP "
         "SHIPMENTS TO CHINA STOP.",
         icon_chip, ACCENT_RED),
    ]
    for i, (kicker, head, body, icon_fn, accent) in enumerate(stories):
        col, row = i % 3, i // 3
        draw_panel(px, mx + col * (gw + gap), gy + row * (gh + gap),
                   gw, gh, kicker, head, body, icon_fn, accent)

    # Ticker strip.
    ty = gy + 2 * gh + gap + 8
    fill_rect(px, mx, ty, cw, 30, INK)
    draw_text(px, mx + 10, ty + 8,
              "APEC: TRUMP, XI AND PUTIN MEET IN SHENZHEN  •  FED: MORE "
              "HIKES LIKELY  •  PEW: ISLAM LARGEST FAITH BY 2035",
              2, WHITE)

    # Footer.
    draw_text_centered(px, mx, ty + 40, cw,
                       "SOURCES: AP - REUTERS - CNN - BBC - THE HINDU - "
                       "PEW RESEARCH", 2, GREY)
    return px


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    px = build()
    size = write_png(px, path)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
