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


def satin_bow():
    """Big glossy coquette bow with long ribbon tails."""
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    pink, dark, light = fx.rgb("#FF8FB8"), fx.rgb("#E0558C"), fx.rgb("#FFD1E3")
    c = 512
    for sgn in (-1, 1):
        tail = [(c - sgn * 30, 520), (c + sgn * 60, 520), (c + sgn * 250, 900), (c + sgn * 170, 860),
                (c + sgn * 120, 960)]
        d.polygon(tail, fill=fx.rgba(INK))
        inner = [(c + sgn * 0, 540), (c + sgn * 50, 540), (c + sgn * 218, 872), (c + sgn * 168, 840),
                 (c + sgn * 124, 920)]
        d.polygon(inner, fill=fx.rgba(dark))
    for sgn in (-1, 1):
        loop = [(c, 470), (c + sgn * 150, 250), (c + sgn * 360, 220), (c + sgn * 440, 380),
                (c + sgn * 400, 600), (c + sgn * 220, 640), (c, 560)]
        d.polygon(loop, fill=fx.rgba(INK))
        d.line(loop + [loop[0]], fill=fx.rgba(INK), width=36, joint="curve")
        fill = [(c, 482), (c + sgn * 152, 272), (c + sgn * 344, 246), (c + sgn * 414, 384),
                (c + sgn * 380, 580), (c + sgn * 216, 616), (c, 548)]
        d.polygon(fill, fill=fx.rgba(pink))
        d.polygon([(c, 490), (c + sgn * 170, 380), (c + sgn * 190, 560), (c, 540)], fill=fx.rgba(dark))
        d.line([(c + sgn * 190, 300), (c + sgn * 330, 280)], fill=fx.rgba(light), width=26)
    d.rounded_rectangle([c - 70, 420, c + 70, 600], radius=40, fill=fx.rgba(INK))
    d.rounded_rectangle([c - 50, 440, c + 50, 580], radius=30, fill=fx.rgba(pink))
    d.line([(c - 20, 460), (c + 20, 460)], fill=fx.rgba(light), width=16)
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def strawberry():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    body = [(512, 960), (330, 760), (220, 520), (250, 330), (400, 280), (512, 300), (624, 280), (774, 330),
            (804, 520), (694, 760)]
    d.polygon(body, fill=fx.rgba(INK))
    d.line(body + [body[0]], fill=fx.rgba(INK), width=40, joint="curve")
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).polygon(body, fill=255)
    m = m.filter(ImageFilter.MinFilter(15))
    berry = _masked(_vgrad((S, S), ["#FF6B7A", "#F0304E", "#C81E3C"]), m)
    bd = ImageDraw.Draw(berry)
    for y in range(380, 900, 76):
        for i, x in enumerate(range(260, 780, 76)):
            xx = x + (38 if (y // 76) % 2 else 0)
            bd.ellipse([xx - 9, y - 14, xx + 9, y + 14], fill=fx.rgba("#FFE38A"))
    berry.putalpha(Image.fromarray(np.minimum(np.asarray(berry.getchannel("A")), np.asarray(m))))
    lay.alpha_composite(berry)
    d = ImageDraw.Draw(lay)
    d.ellipse([300, 360, 380, 470], fill=(255, 255, 255, 120))
    leaves = [(512, 330), (350, 250), (300, 300), (420, 190), (470, 110), (512, 190), (554, 110),
              (604, 190), (724, 300), (674, 250)]
    d.polygon(leaves, fill=fx.rgba(INK))
    d.line(leaves + [leaves[0]], fill=fx.rgba(INK), width=30, joint="curve")
    lm = Image.new("L", (S, S))
    ImageDraw.Draw(lm).polygon(leaves, fill=255)
    lm = lm.filter(ImageFilter.MinFilter(11))
    lay.alpha_composite(_masked(_vgrad((S, S), ["#8BE07A", "#4FAF4A"]), lm))
    d = ImageDraw.Draw(lay)
    d.line([(512, 190), (530, 70)], fill=fx.rgba(INK), width=40)
    d.line([(512, 190), (530, 78)], fill=fx.rgba("#4FAF4A"), width=20)
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def _ellipse_layer(cx, cy, rx, ry, angle, fill, outline=INK, width=34):
    """A rotated, outlined ellipse on its own full-size layer."""
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    d.ellipse([cx - rx - width / 2, cy - ry - width / 2, cx + rx + width / 2, cy + ry + width / 2],
              fill=fx.rgba(outline))
    d.ellipse([cx - rx + width / 2, cy - ry + width / 2, cx + rx - width / 2, cy + ry - width / 2],
              fill=fx.rgba(fill) if not isinstance(fill, Image.Image) else None)
    if isinstance(fill, Image.Image):
        m = Image.new("L", (S, S))
        ImageDraw.Draw(m).ellipse([cx - rx + width / 2, cy - ry + width / 2, cx + rx - width / 2,
                                   cy + ry - width / 2], fill=255)
        lay.alpha_composite(_masked(fill, m))
    return lay.rotate(angle, center=(cx, cy), resample=Image.BICUBIC)


def daisy():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    c = 512
    for k in range(10):
        petal = Image.new("RGBA", (S, S))
        pd = ImageDraw.Draw(petal)
        pd.ellipse([c - 104, c - 470, c + 104, c - 40], fill=fx.rgba(INK))
        pd.ellipse([c - 86, c - 452, c + 86, c - 56], fill=fx.rgba("#FFFFFF"))
        pd.line([(c, c - 400), (c, c - 140)], fill=fx.rgba("#E3E0EE"), width=12)
        lay.alpha_composite(petal.rotate(k * 36, center=(c, c), resample=Image.BICUBIC))
    d = ImageDraw.Draw(lay)
    d.ellipse([c - 175, c - 175, c + 175, c + 175], fill=fx.rgba(INK))
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).ellipse([c - 158, c - 158, c + 158, c + 158], fill=255)
    lay.alpha_composite(_masked(_vgrad((S, S), ["#FFE36E", "#FFC23A", "#FF9F1C"]), m))
    d = ImageDraw.Draw(lay)
    d.ellipse([c - 100, c - 110, c - 30, c - 50], fill=(255, 255, 255, 150))
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def butterfly():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    c = 512
    grad = _vgrad((S, S), ["#B79BFF", "#8FB8FF", "#FF9BD2", "#FFC2E2"])
    for sgn in (-1, 1):
        lay.alpha_composite(_ellipse_layer(c + sgn * 200, 560, 150, 190, sgn * 25, grad))
        lay.alpha_composite(_ellipse_layer(c + sgn * 220, 320, 210, 250, sgn * -35, grad))
    d = ImageDraw.Draw(lay)
    for sgn in (-1, 1):
        for x, y, r in ((c + sgn * 300, 250, 50), (c + sgn * 210, 400, 28), (c + sgn * 230, 600, 40)):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 190))
    d.rounded_rectangle([c - 36, 250, c + 36, 760], radius=36, fill=fx.rgba(INK))
    d.rounded_rectangle([c - 20, 266, c + 20, 744], radius=20, fill=fx.rgba("#6B4BA8"))
    for sgn in (-1, 1):
        d.line([(c, 262), (c + sgn * 60, 160), (c + sgn * 110, 110)], fill=fx.rgba(INK), width=14, joint="curve")
        d.ellipse([c + sgn * 110 - 20, 90, c + sgn * 110 + 20, 130], fill=fx.rgba(INK))
    for x, y, sz in ((150, 880, 40), (870, 860, 30), (880, 150, 26)):
        sparkle(d, x, y, sz + 8, INK)
        sparkle(d, x, y, sz, "#FFF6B0")
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def angel_heart():
    """Glossy heart with feathered angel wings and a halo."""
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    c = 512
    for sgn in (-1, 1):
        for i, (dx, dy, rx, ry, ang) in enumerate(((300, 430, 170, 70, 25), (290, 520, 150, 60, 5),
                                                    (270, 600, 120, 50, -15))):
            lay.alpha_composite(_ellipse_layer(c + sgn * dx, dy, rx, ry, sgn * ang, "#FFFFFF", width=28))
    pts = fx._heart_pts(c, 560, 260)
    d = ImageDraw.Draw(lay)
    d.polygon(pts, fill=fx.rgba(INK))
    d.line(pts + [pts[0]], fill=fx.rgba(INK), width=40, joint="curve")
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).polygon(fx._heart_pts(c, 560, 240), fill=255)
    lay.alpha_composite(_masked(_vgrad((S, S), ["#FF9AC6", "#FF4F8B", "#D81E5B"]), m))
    d = ImageDraw.Draw(lay)
    d.ellipse([c - 160, 400, c - 80, 470], fill=(255, 255, 255, 170))
    d.ellipse([c - 160, 180, c + 160, 260], outline=fx.rgba(INK), width=40)
    d.ellipse([c - 150, 190, c + 150, 250], outline=fx.rgba("#FFD86B"), width=20)
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def mushroom():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    c = 512
    stem = [(c - 130, 430), (c + 130, 430), (c + 160, 900), (c - 160, 900)]
    d.polygon(stem, fill=fx.rgba(INK))
    d.line(stem + [stem[0]], fill=fx.rgba(INK), width=40, joint="curve")
    d.polygon([(c - 112, 444), (c + 112, 444), (c + 142, 882), (c - 142, 882)], fill=fx.rgba("#FFF4E2"))
    d.chord([c - 430, 110, c + 430, 790], 180, 360, fill=fx.rgba(INK))
    d.rounded_rectangle([c - 400, 430, c + 400, 500], radius=34, fill=fx.rgba(INK))
    d.rounded_rectangle([c - 380, 446, c + 380, 484], radius=18, fill=fx.rgba("#F2D9C4"))
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).chord([c - 410, 130, c + 410, 770], 180, 360, fill=255)
    cap = _masked(_vgrad((S, S), ["#FF6B6B", "#E8384F", "#C2203A"]), m)
    cd = ImageDraw.Draw(cap)
    for x, y, r in ((c - 210, 300, 62), (c + 40, 210, 52), (c + 240, 310, 58), (c - 40, 360, 40),
                    (c + 330, 410, 28), (c - 320, 410, 30)):
        cd.ellipse([x - r, y - r, x + r, y + r], fill=fx.rgba("#FFF4E2"))
    cap.putalpha(Image.fromarray(np.minimum(np.asarray(cap.getchannel("A")), np.asarray(m))))
    lay.alpha_composite(cap)
    d = ImageDraw.Draw(lay)
    for ex in (c - 56, c + 56):
        d.ellipse([ex - 20, 620, ex + 20, 664], fill=fx.rgba(INK))
        d.ellipse([ex - 10, 628, ex, 640], fill=(255, 255, 255, 255))
    d.arc([c - 34, 650, c + 34, 706], 20, 160, fill=fx.rgba(INK), width=10)
    for bx in (c - 100, c + 100):
        d.ellipse([bx - 28, 676, bx + 28, 702], fill=fx.rgba("#FF9DB5", 220))
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)

def rainbow():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    c, cy = 512, 640
    bands = ["#FF6B8B", "#FFA857", "#FFE066", "#7EDC8A", "#6FB8FF", "#B48CFF"]
    r0, bw = 430, 58
    d.pieslice([c - r0 - 18, cy - r0 - 18, c + r0 + 18, cy + r0 + 18], 180, 360, fill=fx.rgba(INK))
    for i, col in enumerate(bands):
        r = r0 - i * bw
        d.pieslice([c - r, cy - r, c + r, cy + r], 180, 360, fill=fx.rgba(col))
    r = r0 - len(bands) * bw
    d.pieslice([c - r + 18, cy - r + 18, c + r - 18, cy + r - 18], 180, 360, fill=(0, 0, 0, 0))
    d.pieslice([c - r - 2, cy - r - 2, c + r + 2, cy + r + 2], 180, 360, outline=fx.rgba(INK), width=18)
    d.rectangle([0, cy, S, S], fill=(0, 0, 0, 0))
    for x, rr in ((c - 300, 120), (c + 300, 120)):
        for dx, dy, k in ((-70, 10, 0.7), (0, -30, 1.0), (70, 10, 0.75)):
            d.ellipse([x + dx - rr * k - 16, cy + dy - rr * k * 0.75 - 16, x + dx + rr * k + 16,
                       cy + dy + rr * k * 0.75 + 16], fill=fx.rgba(INK))
        for dx, dy, k in ((-70, 10, 0.7), (0, -30, 1.0), (70, 10, 0.75)):
            d.ellipse([x + dx - rr * k, cy + dy - rr * k * 0.75, x + dx + rr * k, cy + dy + rr * k * 0.75],
                      fill=fx.rgba("#FFFFFF"))
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def moon_stars():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    c = 470
    d.ellipse([c - 330, c - 330, c + 330, c + 330], fill=fx.rgba(INK))
    m = Image.new("L", (S, S))
    md = ImageDraw.Draw(m)
    md.ellipse([c - 312, c - 312, c + 312, c + 312], fill=255)
    md.ellipse([c - 160, c - 400, c + 400, c + 160], fill=0)
    moon = _masked(_vgrad((S, S), ["#FFF3B0", "#FFD86B", "#FFC14D"]), m)
    lay2 = Image.new("RGBA", (S, S))
    ImageDraw.Draw(lay2).ellipse([c - 168, c - 408, c + 408, c + 168], fill=(255, 255, 255, 255))
    cut = lay2.getchannel("A").point(lambda v: 255 if v > 0 else 0)
    shape = Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), 255 - np.asarray(cut)))
    lay.putalpha(shape)
    lay.alpha_composite(moon)
    edge = Image.new("RGBA", (S, S))
    ImageDraw.Draw(edge).ellipse([c - 168, c - 408, c + 408, c + 168], outline=fx.rgba(INK), width=18)
    outer = Image.new("L", (S, S))
    ImageDraw.Draw(outer).ellipse([c - 322, c - 322, c + 322, c + 322], fill=255)
    edge.putalpha(Image.fromarray(np.minimum(np.asarray(edge.getchannel("A")), np.asarray(outer))))
    lay.alpha_composite(edge)
    d = ImageDraw.Draw(lay)
    d.ellipse([c - 240, c + 20, c - 200, c + 60], fill=fx.rgba("#F2B84B"))
    d.ellipse([c - 160, c + 150, c - 130, c + 180], fill=fx.rgba("#F2B84B"))
    d.arc([c - 250, c - 60, c - 170, c - 10], 20, 160, fill=fx.rgba(INK), width=10)
    d.ellipse([c - 290, c - 20, c - 250, c + 10], fill=fx.rgba("#FF9DB5", 220))
    for x, y, sz in ((760, 260, 70), (830, 520, 46), (680, 720, 56), (240, 880, 30), (870, 820, 30)):
        sparkle(d, x, y, sz + 12, INK)
        sparkle(d, x, y, sz, "#FFF1A8")
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def sunflower():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    c = 512
    for k in range(16):
        petal = Image.new("RGBA", (S, S))
        pd = ImageDraw.Draw(petal)
        pd.ellipse([c - 74, c - 460, c + 74, c - 90], fill=fx.rgba(INK))
        pd.ellipse([c - 58, c - 444, c + 58, c - 104], fill=fx.rgba("#FFC93C" if k % 2 else "#FFB320"))
        lay.alpha_composite(petal.rotate(k * 22.5, center=(c, c), resample=Image.BICUBIC))
    d = ImageDraw.Draw(lay)
    d.ellipse([c - 200, c - 200, c + 200, c + 200], fill=fx.rgba(INK))
    d.ellipse([c - 182, c - 182, c + 182, c + 182], fill=fx.rgba("#7A4A26"))
    for r, n in ((140, 18), (95, 12), (50, 7)):
        for i in range(n):
            a = 2 * math.pi * i / n
            x, y = c + r * math.cos(a), c + r * math.sin(a)
            d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=fx.rgba("#5A3418"))
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def kawaii_cloud():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    puffs = [(300, 560, 170), (512, 460, 230), (730, 560, 170), (420, 640, 150), (610, 640, 150)]
    for x, y, r in puffs:
        d.ellipse([x - r - 20, y - r - 20, x + r + 20, y + r + 20], fill=fx.rgba(INK))
    m = Image.new("L", (S, S))
    md = ImageDraw.Draw(m)
    for x, y, r in puffs:
        md.ellipse([x - r, y - r, x + r, y + r], fill=255)
    lay.alpha_composite(_masked(_vgrad((S, S), ["#FFFFFF", "#EAF4FF", "#CFE6FF"]), m))
    d = ImageDraw.Draw(lay)
    for ex in (440, 584):
        d.ellipse([ex - 22, 540, ex + 22, 590], fill=fx.rgba(INK))
        d.ellipse([ex - 12, 548, ex, 562], fill=(255, 255, 255, 255))
    d.arc([482, 570, 542, 626], 20, 160, fill=fx.rgba(INK), width=12)
    for bx in (380, 644):
        d.ellipse([bx - 32, 590, bx + 32, 620], fill=fx.rgba("#FF9DB5", 220))
    for i, x in enumerate((360, 470, 580, 690)):
        y0 = 800 + (i % 2) * 30
        d.line([(x, y0), (x - 20, y0 + 70)], fill=fx.rgba("#7FB8FF"), width=20)
    sparkle(d, 160, 260, 50, INK)
    sparkle(d, 160, 260, 40, "#FFF1A8")
    sparkle(d, 860, 300, 40, INK)
    sparkle(d, 860, 300, 30, "#FFF1A8")
    img.alpha_composite(_shadow(lay, (14, 16), 0.25))
    img.alpha_composite(lay)
    return _done(img)


def ladybug():
    img, _ = _new()
    lay = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(lay)
    c = 512
    d.ellipse([c - 170, 150, c + 170, 430], fill=fx.rgba(INK))
    for sgn in (-1, 1):
        d.line([(c + sgn * 60, 190), (c + sgn * 150, 90)], fill=fx.rgba(INK), width=18)
        d.ellipse([c + sgn * 150 - 26, 64, c + sgn * 150 + 26, 116], fill=fx.rgba(INK))
    d.ellipse([c - 360, 260, c + 360, 920], fill=fx.rgba(INK))
    m = Image.new("L", (S, S))
    ImageDraw.Draw(m).ellipse([c - 340, 280, c + 340, 900], fill=255)
    shell = _masked(_vgrad((S, S), ["#FF5A5F", "#E8273A", "#B5182B"]), m)
    sd = ImageDraw.Draw(shell)
    sd.line([(c, 280), (c, 900)], fill=fx.rgba(INK), width=20)
    for x, y, r in ((c - 170, 420, 60), (c + 170, 420, 60), (c - 210, 640, 70), (c + 210, 640, 70),
                    (c - 90, 790, 50), (c + 90, 790, 50)):
        sd.ellipse([x - r, y - r, x + r, y + r], fill=fx.rgba(INK))
    shell.putalpha(Image.fromarray(np.minimum(np.asarray(shell.getchannel("A")), np.asarray(m))))
    lay.alpha_composite(shell)
    d = ImageDraw.Draw(lay)
    d.ellipse([c - 250, 340, c - 170, 410], fill=(255, 255, 255, 150))
    for ex in (c - 60, c + 60):
        d.ellipse([ex - 22, 240, ex + 22, 290], fill=fx.rgba("#FFFFFF"))
        d.ellipse([ex - 10, 254, ex + 6, 276], fill=fx.rgba(INK))
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
    "satin_bow": satin_bow,
    "strawberry": strawberry,
    "daisy": daisy,
    "butterfly": butterfly,
    "angel_heart": angel_heart,
    "mushroom": mushroom,
    "rainbow": rainbow,
    "moon_stars": moon_stars,
    "sunflower": sunflower,
    "kawaii_cloud": kawaii_cloud,
    "ladybug": ladybug,
}
