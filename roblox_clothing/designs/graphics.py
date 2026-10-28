"""Original 512x512 graphics, sold as classic T-shirts and printed on shirts.

Everything is drawn at 2x and downsampled for smooth edges. Backgrounds are
transparent so the graphic sits on whatever the avatar wears underneath.
"""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .. import fx
from ..details import font

S = 1024  # working resolution
OUT = 512
INK = (34, 24, 48)


def _new():
    img = Image.new("RGBA", (S, S))
    return img, ImageDraw.Draw(img)


def _done(img):
    return img.resize((OUT, OUT), Image.LANCZOS)


def _vgrad(size, stops):
    """Vertical gradient through evenly spaced colour stops."""
    w, h = size
    t = np.linspace(0, 1, h)[:, None]
    cols = np.array([fx.rgb(c) for c in stops], np.float32) / 255
    seg = np.clip(t * (len(stops) - 1), 0, len(stops) - 1 - 1e-6)
    i = seg.astype(int)
    f = (seg - i)[..., None]
    arr = cols[i] * (1 - f) + cols[i + 1] * f
    return fx.to_image(np.broadcast_to(arr, (h, w, 3)).copy())


def _masked(fill_img, mask):
    out = fill_img.copy()
    out.putalpha(mask)
    return out


def _glow(layer, radius, opacity, color=None):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * opacity))
    g = Image.new("RGBA", layer.size, fx.rgba(color or (255, 255, 255), 0))
    if color is None:
        g = layer.copy()
    g.putalpha(a)
    return g


def _shadow(layer, offset=(14, 16), opacity=0.35):
    a = layer.getchannel("A").point(lambda v: int(v * opacity))
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(a)
    out = Image.new("RGBA", layer.size)
    out.paste(sh, offset)
    return out


def sparkle(d, cx, cy, r, color):
    k = r * 0.22
    d.polygon([(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k), (cx, cy + r), (cx - k, cy + k),
               (cx - r, cy), (cx - k, cy - k)], fill=fx.rgba(color))


# ---------------------------------------------------------------- graphics

def retro_sunset():
    img, _ = _new()
    cx, cy, r = 512, 470, 330
    sun_mask = Image.new("L", (S, S))
    md = ImageDraw.Draw(sun_mask)
    md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    for i in range(6):
        y = cy + 30 + i * 50
        md.rectangle([0, y, S, y + 8 + i * 6], fill=0)
    sun = _masked(_vgrad((S, S), ["#FFF07A", "#FFC145", "#FF7A59", "#FF2E88"]), sun_mask)
    img.alpha_composite(_glow(sun, 40, 0.55))
    img.alpha_composite(sun)
    grid = Image.new("RGBA", (S, S))
    gd = ImageDraw.Draw(grid)
    top, bot = cy + r - 4, 960
    col = fx.rgba("#B95CFF")
    gd.line([(90, top), (934, top)], fill=col, width=10)
    for i in range(1, 6):
        t = (i / 5) ** 1.7
        y = top + (bot - top) * t
        gd.line([(90 - 60 * t, y), (934 + 60 * t, y)], fill=col, width=8)
    for i in range(-6, 7):
        gd.line([(512 + i * 30, top), (512 + i * 120, bot)], fill=col, width=8)
    mask = Image.new("L", (S, S))
    ImageDraw.Draw(mask).polygon([(90, top - 6), (934, top - 6), (994, bot + 4), (30, bot + 4)], fill=255)
    grid.putalpha(Image.fromarray(np.minimum(np.asarray(grid.getchannel("A")), np.asarray(mask))))
    img.alpha_composite(_glow(grid, 10, 0.8))
    img.alpha_composite(grid)
    return _done(img)


HEART = [
    "..XXX...XXX..",
    ".XXXXX.XXXXX.",
    "XXXXXXXXXXXXX",
    "XXXXXXXXXXXXX",
    "XXXXXXXXXXXXX",
    ".XXXXXXXXXXX.",
    "..XXXXXXXXX..",
    "...XXXXXXX...",
    "....XXXXX....",
    ".....XXX.....",
    "......X......",
]


def pixel_heart():
    img, d = _new()
    rows = len(HEART)
    cols = len(HEART[0])
    px = 58
    ox = (S - (cols + 2) * px) // 2 + px
    oy = (S - (rows + 2) * px) // 2 + px
    filled = {(x, y) for y, row in enumerate(HEART) for x, ch in enumerate(row) if ch == "X"}
    outline = set()
    for x, y in filled:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in filled:
                outline.add((x + dx, y + dy))

    def cell(x, y, color):
        d.rectangle([ox + x * px, oy + y * px, ox + (x + 1) * px - 1, oy + (y + 1) * px - 1], fill=fx.rgba(color))

    for x, y in outline:
        cell(x, y, INK)
    for x, y in filled:
        dark = (x + y) > 13 or y >= 8
        cell(x, y, "#C81E4A" if dark else "#FF3D6E")
    for x, y in ((2, 1), (3, 1), (1, 2), (2, 2), (1, 3)):
        cell(x, y, "#FFFFFF" if (x, y) in ((2, 1), (1, 2)) else "#FF9DB5")
    sh = _shadow(img, (18, 18), 0.25)
    sh.alpha_composite(img)
    return _done(sh)


def _gradient_text(lines, size, stops, stroke=20, gap=0.95):
    img, d = _new()
    f = font(size, "black")
    total = size * gap * len(lines)
    y0 = (S - total) / 2 + size * gap / 2
    mask = Image.new("L", (S, S))
    md = ImageDraw.Draw(mask)
    outline = Image.new("RGBA", (S, S))
    od = ImageDraw.Draw(outline)
    for i, line in enumerate(lines):
        y = y0 + i * size * gap
        od.text((S / 2, y), line, font=f, anchor="mm", fill=fx.rgba(INK), stroke_width=stroke,
                stroke_fill=fx.rgba(INK))
        md.text((S / 2, y), line, font=f, anchor="mm", fill=255)
    fill = _masked(_vgrad((S, S), stops), mask)
    img.alpha_composite(_shadow(outline, (12, 16), 0.3))
    img.alpha_composite(outline)
    img.alpha_composite(fill)
    gloss = Image.new("L", (S, S))
    gd = ImageDraw.Draw(gloss)
    for i in range(len(lines)):
        y = y0 + i * size * gap
        gd.rectangle([0, y - size * 0.36, S, y - size * 0.24], fill=110)
    gloss = Image.fromarray(np.minimum(np.asarray(gloss), np.asarray(mask)))
    wl = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    wl.putalpha(gloss)
    img.alpha_composite(wl)
    return img, d


def good_vibes():
    img, d = _gradient_text(["GOOD", "VIBES"], 250, ["#FF5FA2", "#FF9A3C", "#FFE45E"])
    for x, y, r in ((150, 210, 52), (880, 260, 40), (860, 800, 58), (180, 820, 36), (512, 105, 30)):
        sparkle(d, x, y, r + 10, INK)
        sparkle(d, x, y, r, "#FFF6B0")
    return _done(img)


def cherries():
    img, d = _new()
    stem = Image.new("RGBA", (S, S))
    sd = ImageDraw.Draw(stem)
    joint = (590, 210)
    for a, b in (((390, 560), (470, 330)), ((660, 600), (640, 360))):
        line = [(a[0] * (1 - t) ** 2 + 2 * b[0] * (1 - t) * t + joint[0] * t * t,
                 a[1] * (1 - t) ** 2 + 2 * b[1] * (1 - t) * t + joint[1] * t * t) for t in np.linspace(0, 1, 40)]
        sd.line(line, fill=fx.rgba(INK), width=44, joint="curve")
        sd.line(line, fill=fx.rgba("#4E9A3F"), width=22, joint="curve")
    leaf = Image.new("RGBA", (S, S))
    ld = ImageDraw.Draw(leaf)
    ld.ellipse([590, 150, 860, 270], fill=fx.rgba(INK))
    ld.ellipse([604, 162, 846, 258], fill=fx.rgba("#6CC24A"))
    ld.line([(606, 210), (840, 210)], fill=fx.rgba("#3F8A33"), width=8)
    leaf = leaf.rotate(18, center=joint, resample=Image.BICUBIC)
    img.alpha_composite(stem)
    img.alpha_composite(leaf)
    for cx, cy, r in ((380, 660, 170), (668, 700, 160)):
        ball = Image.new("RGBA", (S, S))
        bd = ImageDraw.Draw(ball)
        bd.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=fx.rgba(INK))
        m = Image.new("L", (S, S))
        ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        yy, xx = np.mgrid[0:S, 0:S]
        dist = np.hypot(xx - (cx - r * 0.35), yy - (cy - r * 0.35)) / (r * 1.6)
        col = np.clip(dist, 0, 1)[..., None]
        arr = (np.array(fx.rgb("#FF4D5E")) * (1 - col) + np.array(fx.rgb("#9E0B2E")) * col) / 255
        ball.alpha_composite(_masked(fx.to_image(arr), m))
        bd = ImageDraw.Draw(ball)
        bd.ellipse([cx - r * 0.6, cy - r * 0.62, cx - r * 0.2, cy - r * 0.3], fill=(255, 255, 255, 200))
        img.alpha_composite(_shadow(ball, (14, 16), 0.25))
        img.alpha_composite(ball)
    return _done(img)


def mountain_badge():
    img, d = _new()
    c, R = 512, 430
    d.ellipse([c - R - 14, c - R - 14, c + R + 14, c + R + 14], fill=fx.rgba(INK))
    d.ellipse([c - R, c - R, c + R, c + R], fill=fx.rgba("#F6EBDD"))
    r = R - 86
    inner = Image.new("L", (S, S))
    ImageDraw.Draw(inner).ellipse([c - r, c - r, c + r, c + r], fill=255)
    scene = _vgrad((S, S), ["#FF8C6B", "#FFB38A", "#FFE1B8"])
    sd = ImageDraw.Draw(scene)
    sd.ellipse([c - 110, 380, c + 110, 600], fill=fx.rgba("#FFF4D2"))
    sd.polygon([(c - r, 760), (330, 520), (450, 640), (620, 470), (c + r, 700), (c + r, S), (c - r, S)],
               fill=fx.rgba("#7A6FA8"))
    sd.polygon([(c - r, 860), (260, 640), (420, 770), (560, 560), (760, 780), (c + r, 690), (c + r, S),
                (c - r, S)], fill=fx.rgba("#3C3F73"))
    sd.polygon([(560, 560), (512, 616), (540, 610), (566, 630), (604, 606)], fill=fx.rgba("#F6EBDD"))
    sd.polygon([(260, 640), (226, 676), (252, 672), (288, 664)], fill=fx.rgba("#F6EBDD"))
    for i, x in enumerate(range(200, 860, 70)):
        h = 90 + (i * 37) % 60
        sd.polygon([(x, 900), (x + 30, 900 - h), (x + 60, 900)], fill=fx.rgba("#22254A"))
    img.alpha_composite(_masked(scene, inner))
    d = ImageDraw.Draw(img)
    d.ellipse([c - r, c - r, c + r, c + r], outline=fx.rgba(INK), width=12)
    f = font(74, "black")
    text = "EXPLORE MORE"
    n = len(text)
    for i, ch in enumerate(text):
        ang = math.radians(-90 + (i - (n - 1) / 2) * 12.5)
        x, y = c + (R - 44) * math.cos(ang), c + (R - 44) * math.sin(ang)
        tile = Image.new("RGBA", (160, 160))
        ImageDraw.Draw(tile).text((80, 80), ch, font=f, fill=fx.rgba(INK), anchor="mm")
        tile = tile.rotate(-math.degrees(ang) - 90, resample=Image.BICUBIC)
        img.alpha_composite(tile, (int(x - 80), int(y - 80)))
    d = ImageDraw.Draw(img)
    for x in (c - 120, c, c + 120):
        sparkle(d, x, c + R - 44, 22, INK)
    return _done(img)


def lightning_bolt():
    img, _ = _new()
    pts = [(610, 60), (250, 560), (470, 560), (380, 964), (790, 410), (560, 410), (700, 60)]
    bolt = Image.new("RGBA", (S, S))
    bd = ImageDraw.Draw(bolt)
    bd.polygon(pts, fill=fx.rgba(INK))
    bd.line(pts + [pts[0]], fill=fx.rgba(INK), width=40, joint="curve")
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    m = m.filter(ImageFilter.MinFilter(17))
    fill = _masked(_vgrad((S, S), ["#FFF27A", "#FFC928", "#FF8A00"]), m)
    glow = Image.new("RGBA", (S, S), fx.rgba("#FFD23F", 0))
    glow.putalpha(m.filter(ImageFilter.GaussianBlur(60)).point(lambda v: int(v * 0.8)))
    img.alpha_composite(glow)
    img.alpha_composite(bolt)
    img.alpha_composite(fill)
    hl = Image.new("L", (S, S))
    ImageDraw.Draw(hl).polygon([(620, 110), (330, 520), (390, 520), (660, 110)], fill=150)
    wl = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    wl.putalpha(Image.fromarray(np.minimum(np.asarray(hl), np.asarray(m))))
    img.alpha_composite(wl)
    return _done(img)


def boba():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    straw = Image.new("RGBA", (S, S))
    sd = ImageDraw.Draw(straw)
    sd.rounded_rectangle([560, 60, 650, 560], radius=20, fill=fx.rgba(INK))
    sd.rounded_rectangle([576, 76, 634, 560], radius=14, fill=fx.rgba("#FF7EB6"))
    sd.rectangle([590, 76, 602, 560], fill=fx.rgba("#FFB3D4"))
    straw = straw.rotate(-12, center=(605, 400), resample=Image.BICUBIC)
    lay.alpha_composite(straw)
    cup = [(270, 360), (754, 360), (680, 930), (344, 930)]
    d = ImageDraw.Draw(lay)
    d.polygon(cup, fill=fx.rgba(INK))
    d.line(cup + [cup[0]], fill=fx.rgba(INK), width=36, joint="curve")
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).polygon(cup, fill=255)
    m = m.filter(ImageFilter.MinFilter(13))
    tea = _masked(_vgrad((S, S), ["#F7DDBF", "#E9BC8E", "#D49A68"]), m)
    td = ImageDraw.Draw(tea)
    for row, y in enumerate((860, 800, 742)):
        for i in range(6 - row):
            x = 400 + row * 26 + i * 52
            td.ellipse([x - 26, y - 26, x + 26, y + 26], fill=fx.rgba("#3B2416"))
            td.ellipse([x - 14, y - 16, x - 4, y - 6], fill=(255, 255, 255, 120))
    tea.putalpha(Image.fromarray(np.minimum(np.asarray(tea.getchannel("A")), np.asarray(m))))
    lay.alpha_composite(tea)
    d = ImageDraw.Draw(lay)
    d.chord([250, 250, 774, 470], 180, 360, fill=fx.rgba(INK))
    d.chord([270, 270, 754, 450], 180, 360, fill=(255, 255, 255, 235))
    d.rounded_rectangle([238, 340, 786, 392], radius=24, fill=fx.rgba(INK))
    d.rounded_rectangle([254, 352, 770, 380], radius=14, fill=fx.rgba("#FFFFFF"))
    for ex in (430, 594):
        d.ellipse([ex - 30, 540, ex + 30, 604], fill=fx.rgba(INK))
        d.ellipse([ex - 16, 552, ex - 2, 568], fill=(255, 255, 255, 255))
    for bx in (370, 654):
        d.ellipse([bx - 36, 610, bx + 36, 646], fill=fx.rgba("#FF8FB1", 200))
    d.arc([470, 596, 514, 640], 0, 180, fill=fx.rgba(INK), width=10)
    d.arc([510, 596, 554, 640], 0, 180, fill=fx.rgba(INK), width=10)
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def ringed_planet():
    img, d = _new()
    c, r = 512, 250
    ring = Image.new("RGBA", (S, S))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([c - 450, c - 120, c + 450, c + 120], outline=fx.rgba(INK), width=74)
    rd.ellipse([c - 440, c - 110, c + 440, c + 110], outline=fx.rgba("#FFD36E"), width=54)
    rd.ellipse([c - 412, c - 88, c + 412, c + 88], outline=fx.rgba("#FFB347"), width=10)
    ring = ring.rotate(16, center=(c, c), resample=Image.BICUBIC)
    front = Image.new("L", (S, S))
    ImageDraw.Draw(front).rectangle([0, c, S, S], fill=255)
    front = front.rotate(16, center=(c, c), resample=Image.BICUBIC)
    ring_front = ring.copy()
    ring_front.putalpha(Image.fromarray(np.minimum(np.asarray(ring.getchannel("A")), np.asarray(front))))
    img.alpha_composite(ring)
    pl = Image.new("RGBA", (S, S))
    pd = ImageDraw.Draw(pl)
    pd.ellipse([c - r - 14, c - r - 14, c + r + 14, c + r + 14], fill=fx.rgba(INK))
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).ellipse([c - r, c - r, c + r, c + r], fill=255)
    bands = _vgrad((S, S), ["#9D7BFF", "#7B5CFF", "#C86BFA", "#FF6EC7", "#FF9DCB"])
    bd = ImageDraw.Draw(bands)
    for y, h in ((360, 24), (430, 14), (560, 30), (640, 12)):
        bd.rectangle([0, y, S, y + h], fill=(255, 255, 255, 60))
    pl.alpha_composite(_masked(bands, m))
    pd = ImageDraw.Draw(pl)
    pd.ellipse([c - 150, c - 190, c - 60, c - 120], fill=(255, 255, 255, 150))
    sh = Image.new("L", (S, S))
    ImageDraw.Draw(sh).ellipse([c - r + 90, c - r + 70, c + r + 170, c + r + 150], fill=255)
    sh = Image.fromarray(np.minimum(255 - np.asarray(sh), np.asarray(m)) // 3)
    dark = Image.new("RGBA", (S, S), (30, 10, 60, 0))
    dark.putalpha(sh.filter(ImageFilter.GaussianBlur(30)))
    pl.alpha_composite(dark)
    img.alpha_composite(pl)
    img.alpha_composite(ring_front)
    d = ImageDraw.Draw(img)
    for x, y, s in ((150, 160, 40), (860, 170, 30), (880, 820, 46), (160, 840, 28), (760, 90, 18)):
        sparkle(d, x, y, s + 8, INK)
        sparkle(d, x, y, s, "#FFF6B0")
    return _done(img)


def chrome_star():
    img, _ = _new()
    c = 512

    def star(r, k):
        pts = []
        for i in range(8):
            a = math.radians(-90 + i * 45)
            rr = r if i % 2 == 0 else r * k
            pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
        return pts

    outer = star(470, 0.3)
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    d.polygon(outer, fill=fx.rgba(INK))
    d.line(outer + [outer[0]], fill=fx.rgba(INK), width=34, joint="curve")
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).polygon(star(440, 0.28), fill=255)
    chrome = _vgrad((S, S), ["#FFFFFF", "#C9D2E0", "#7D879A", "#E9EEF6", "#FFFFFF", "#A7B1C4"])
    lay.alpha_composite(_masked(chrome, m))
    hl = Image.new("L", (S, S))
    ImageDraw.Draw(hl).polygon([(c, 90), (c + 40, c - 40), (c, c)], fill=170)
    wl = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    wl.putalpha(hl)
    lay.alpha_composite(wl)
    d = ImageDraw.Draw(lay)
    for x, y, s in ((210, 200, 60), (820, 790, 70), (830, 230, 36)):
        sparkle(d, x, y, s + 10, INK)
        sparkle(d, x, y, s, "#E6ECF5")
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


GRAPHICS = {
    "retro_sunset": retro_sunset,
    "pixel_heart": pixel_heart,
    "good_vibes": good_vibes,
    "cherries": cherries,
    "mountain_badge": mountain_badge,
    "lightning_bolt": lightning_bolt,
    "boba": boba,
    "ringed_planet": ringed_planet,
    "chrome_star": chrome_star,
}
