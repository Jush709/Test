"""Garment details drawn onto individual faces: trims, zips, pockets, text."""

import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import fx
from .garment import over

FONT_FILES = {
    "regular": ["/usr/share/fonts/opentype/inter/Inter-Medium.otf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "bold": ["/usr/share/fonts/opentype/inter/Inter-Bold.otf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "black": ["/usr/share/fonts/opentype/inter/Inter-Black.otf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "serif": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"],
}


@lru_cache(maxsize=None)
def font(size, style="bold"):
    for path in FONT_FILES[style]:
        try:
            return ImageFont.truetype(path, int(size))
        except OSError:
            continue
    return ImageFont.load_default(size)


# ---------------------------------------------------------------- primitives

def stitch(d, pts, fill, dash=3, gap=2, width=1):
    """Dashed polyline, like top-stitching."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        if length == 0:
            continue
        t = 0.0
        while t < length:
            t1 = min(t + dash, length)
            d.line([(x0 + (x1 - x0) * t / length, y0 + (y1 - y0) * t / length),
                    (x0 + (x1 - x0) * t1 / length, y0 + (y1 - y0) * t1 / length)], fill=fill, width=width)
            t += dash + gap


def arc_points(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def layer_like(img):
    return Image.new("RGBA", img.size)


def place(face, layer, shadow=(0, 1, 1.2, 0.4)):
    """Composite a detail layer onto a face with an optional soft drop shadow.

    The shadow is clipped to fabric already on the face so it never paints skin.
    """
    if shadow:
        dx, dy, blur, op = shadow
        over(face, fx.clip_to(fx.shadow_of(layer, (dx, dy), blur, op), face))
    over(face, layer)


def polygon_layer(size, pts, fill, outline=None, width=1):
    lay = Image.new("RGBA", size)
    d = ImageDraw.Draw(lay)
    d.polygon(pts, fill=fx.rgba(fill))
    if outline:
        d.line(pts + [pts[0]], fill=fx.rgba(outline), width=width)
    return lay


def textured_polygon(size, pts, texture):
    """Fill a polygon with a texture image of the same size as the face."""
    mask = Image.new("L", size)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    lay = texture.copy()
    lay.putalpha(mask)
    return lay


# ---------------------------------------------------------------- trims

def rib_band(face, y0, y1, color, x0=0, x1=None, period=3):
    """Ribbed knit band (hem, cuff or waistband) across rows y0..y1."""
    x1 = face.width if x1 is None else x1
    band = fx.ribbed((int(x1 - x0), int(y1 - y0)), color, period)
    over(face, band, (x0, y0))
    d = ImageDraw.Draw(face)
    d.line([(x0, y0), (x1, y0)], fill=fx.rgba(fx.tone(color, 0.7), 200))


def seam(face, pts, color, k=0.72):
    d = ImageDraw.Draw(face)
    d.line(pts, fill=fx.rgba(fx.tone(color, k), 220), width=1)


def zipper(face, x, y0, y1, tape, teeth=(190, 192, 198), pull=True, pull_y=None):
    d = ImageDraw.Draw(face)
    d.rectangle([x - 3, y0, x + 2, y1], fill=fx.rgba(fx.tone(tape, 0.8)))
    for y in range(int(y0), int(y1), 2):
        off = -1 if (y // 2) % 2 else 0
        d.rectangle([x - 1 + off, y, x + off, y], fill=fx.rgba(teeth))
    if pull:
        py = y0 + 3 if pull_y is None else pull_y
        lay = layer_like(face)
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([x - 2, py, x + 1, py + 9], radius=1, fill=fx.rgba(teeth),
                             outline=fx.rgba(fx.tone(teeth, 0.6)))
        ld.rectangle([x - 1, py + 6, x, py + 7], fill=fx.rgba(fx.tone(teeth, 0.5)))
        place(face, lay, (1, 1, 0.8, 0.5))


def button(face, cx, cy, r, color, holes=True, rim=None):
    lay = layer_like(face)
    d = ImageDraw.Draw(lay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fx.rgba(color), outline=fx.rgba(rim or fx.tone(color, 0.7)))
    if r >= 2:
        d.point([(cx - r / 2, cy - r / 2)], fill=fx.rgba(fx.tone(color, 1.5)))
    if holes and r >= 2.5:
        hc = fx.rgba(fx.tone(color, 0.55))
        for dx in (-1, 1):
            d.point([(cx + dx * 0.8, cy)], fill=hc)
    place(face, lay, (0, 1, 0.6, 0.45))


def drawstrings(face, xs, y0, length, color, tip=(200, 200, 200), sway=2):
    lay = layer_like(face)
    d = ImageDraw.Draw(lay)
    for i, x in enumerate(xs):
        dx = sway if i % 2 else -sway
        d.ellipse([x - 2, y0 - 2, x + 2, y0 + 2], fill=fx.rgba(fx.tone(color, 0.6)), outline=fx.rgba(tip))
        pts = [(x, y0), (x + dx * 0.5, y0 + length * 0.5), (x + dx, y0 + length)]
        d.line(pts, fill=fx.rgba(color), width=2)
        d.line([(x + dx - 0.5, y0 + length), (x + dx, y0 + length + 5)], fill=fx.rgba(tip), width=2)
    place(face, lay, (1, 1, 0.8, 0.45))


def pocket(face, box, color, stitch_color=None, texture=None, flap=None, button_color=None, radius=1):
    """Patch pocket with top-stitching; optional flap height and button."""
    x0, y0, x1, y1 = box
    size = face.size
    lay = layer_like(face)
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, radius=radius, fill=fx.rgba(color), outline=fx.rgba(fx.tone(color, 0.7)))
    if texture is not None:
        mask = Image.new("L", size)
        ImageDraw.Draw(mask).rounded_rectangle(box, radius=radius, fill=255)
        tex = texture.copy()
        tex.putalpha(mask)
        over(lay, tex)
        ImageDraw.Draw(lay).rounded_rectangle(box, radius=radius, outline=fx.rgba(fx.tone(color, 0.65)))
    sc = fx.rgba(stitch_color or fx.tone(color, 1.35))
    d = ImageDraw.Draw(lay)
    stitch(d, [(x0 + 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2), (x1 - 2, y0 + 2)], sc)
    place(face, lay, (0, 1, 1.0, 0.4))
    if flap:
        fl = layer_like(face)
        fd = ImageDraw.Draw(fl)
        fbox = (x0 - 1, y0 - 1, x1 + 1, y0 + flap)
        fd.rounded_rectangle(fbox, radius=1, fill=fx.rgba(color), outline=fx.rgba(fx.tone(color, 0.65)))
        if texture is not None:
            mask = Image.new("L", size)
            ImageDraw.Draw(mask).rounded_rectangle(fbox, radius=1, fill=255)
            tex = texture.copy()
            tex.putalpha(mask)
            over(fl, tex)
            ImageDraw.Draw(fl).rounded_rectangle(fbox, radius=1, outline=fx.rgba(fx.tone(color, 0.65)))
        fd = ImageDraw.Draw(fl)
        stitch(fd, [(x0 + 1, y0 + flap - 2), (x1 - 1, y0 + flap - 2)], sc)
        place(face, fl, (0, 1, 1.0, 0.55))
        if button_color:
            button(face, (x0 + x1) / 2, y0 + flap - 3, 1.6, button_color, holes=False)


def text(face, s, center, size, color, style="bold", stroke=0, stroke_color=None, shadow=None, anchor="mm",
         spacing=0):
    lay = layer_like(face)
    d = ImageDraw.Draw(lay)
    f = font(size, style)
    if spacing:
        widths = [d.textlength(ch, font=f) for ch in s]
        total = sum(widths) + spacing * (len(s) - 1)
        x = center[0] - total / 2
        for ch, wch in zip(s, widths):
            d.text((x + wch / 2, center[1]), ch, font=f, fill=fx.rgba(color), anchor="mm",
                   stroke_width=stroke, stroke_fill=fx.rgba(stroke_color or color))
            x += wch + spacing
    else:
        d.text(center, s, font=f, fill=fx.rgba(color), anchor=anchor,
               stroke_width=stroke, stroke_fill=fx.rgba(stroke_color or color))
    place(face, lay, shadow)


def arc_text(face, s, cx, cy, radius, size, color, style="black", stroke=0, stroke_color=None, spread=11,
             shadow=(0, 1, 0.8, 0.5)):
    """Letters fanned along an arc above (cx, cy), like a varsity back print."""
    lay = layer_like(face)
    f = font(size, style)
    n = len(s)
    for i, ch in enumerate(s):
        ang = (i - (n - 1) / 2) * spread
        tile = Image.new("RGBA", (size * 3, size * 3))
        ImageDraw.Draw(tile).text((size * 1.5, size * 1.5), ch, font=f, fill=fx.rgba(color), anchor="mm",
                                  stroke_width=stroke, stroke_fill=fx.rgba(stroke_color or color))
        tile = tile.rotate(-ang, resample=Image.BICUBIC)
        x = cx + radius * math.sin(math.radians(ang))
        y = cy - radius * math.cos(math.radians(ang))
        over(lay, tile, (int(x - size * 1.5), int(y - size * 1.5)))
    place(face, lay, shadow)


def paste_graphic(face, graphic, center, width, shadow=None):
    """Scale an RGBA graphic to `width` px and composite it centred on `center`."""
    h = int(graphic.height * width / graphic.width)
    g = graphic.resize((int(width), h), Image.LANCZOS)
    lay = layer_like(face)
    over(lay, g, (int(center[0] - width / 2), int(center[1] - h / 2)))
    place(face, lay, shadow)


# ---------------------------------------------------------------- feminine details

SS = 4  # supersampling for small curvy details


def _big(face):
    return Image.new("RGBA", (face.width * SS, face.height * SS))


def _small(big, face):
    return big.resize(face.size, Image.LANCZOS)


def heart_points(cx, cy, r, n=32):
    return fx._heart_pts(cx, cy, r, n)


def bow(face, cx, cy, w, color, tails=0.7, shadow=(0, 1, 0.8, 0.5)):
    """Ribbon bow with two loops, a knot and V-cut tails, shaded like satin."""
    big = _big(face)
    d = ImageDraw.Draw(big)
    s = SS
    x, y, w = cx * s, cy * s, w * s
    dark, light, edge = fx.tone(color, 0.72), fx.tone(color, 1.25), fx.tone(color, 0.55)
    if tails:
        for sgn in (-1, 1):
            tl = [(x - sgn * w * 0.06, y), (x + sgn * w * 0.10, y), (x + sgn * w * 0.30, y + w * tails),
                  (x + sgn * w * 0.20, y + w * tails * 0.86), (x + sgn * w * 0.10, y + w * tails * 1.02)]
            d.polygon(tl, fill=fx.rgba(dark), outline=fx.rgba(edge))
    for sgn in (-1, 1):
        loop = [(x, y - w * 0.06), (x + sgn * w * 0.18, y - w * 0.30), (x + sgn * w * 0.44, y - w * 0.30),
                (x + sgn * w * 0.52, y - w * 0.08), (x + sgn * w * 0.46, y + w * 0.18),
                (x + sgn * w * 0.22, y + w * 0.22), (x, y + w * 0.06)]
        d.polygon(loop, fill=fx.rgba(color), outline=fx.rgba(edge))
        d.polygon([(x, y - w * 0.04), (x + sgn * w * 0.20, y - w * 0.14), (x + sgn * w * 0.22, y + w * 0.10),
                   (x, y + w * 0.04)], fill=fx.rgba(dark))
        d.line([(x + sgn * w * 0.22, y - w * 0.24), (x + sgn * w * 0.42, y - w * 0.24)], fill=fx.rgba(light),
               width=max(1, int(w * 0.05)))
    d.rounded_rectangle([x - w * 0.10, y - w * 0.12, x + w * 0.10, y + w * 0.12], radius=w * 0.04,
                        fill=fx.rgba(fx.tone(color, 0.9)), outline=fx.rgba(edge))
    place(face, _small(big, face), shadow)


def lace_band(face, y0, y1, color, scallop=8, edge="bottom", x0=0, x1=None, shadow=(0, 1, 0.8, 0.35)):
    """Open-work lace trim over rows y0..y1 with a scalloped edge (skin or fabric shows through)."""
    x1 = face.width if x1 is None else x1
    s = SS
    mask = Image.new("L", (face.width * s, face.height * s))
    md = ImageDraw.Draw(mask)
    r = scallop / 2
    if edge == "bottom":
        md.rectangle([x0 * s, y0 * s, x1 * s, (y1 - r) * s], fill=255)
        cy = y1 - r
    else:
        md.rectangle([x0 * s, (y0 + r) * s, x1 * s, y1 * s], fill=255)
        cy = y0 + r
    x = x0
    while x < x1:
        md.ellipse([x * s, (cy - r) * s, (x + scallop) * s, (cy + r) * s], fill=255)
        x += scallop
    holes = Image.new("L", mask.size)
    hd = ImageDraw.Draw(holes)
    for j, yy in enumerate(range(int(y0) + 1, int(y1) + 1, 2)):
        for xx in range(int(x0) + (j % 2), int(x1), 2):
            hd.ellipse([(xx + 0.2) * s, (yy - 0.6) * s, (xx + 1.0) * s, (yy + 0.2) * s], fill=255)
    m = np.asarray(mask, np.float32) * (1 - np.asarray(holes, np.float32) / 255 * 0.8)
    lay = Image.new("RGBA", mask.size, fx.rgba(color))
    lay.putalpha(Image.fromarray(m.astype(np.uint8)))
    d = ImageDraw.Draw(lay)
    line_y = (y0 if edge == "bottom" else y1) * s
    d.line([(x0 * s, line_y), (x1 * s, line_y)], fill=fx.rgba(fx.tone(color, 0.85)), width=s)
    x = x0
    while x < x1:
        d.ellipse([(x + r - 0.7) * s, (cy - 0.7) * s, (x + r + 0.7) * s, (cy + 0.7) * s],
                  fill=fx.rgba(fx.tone(color, 0.8)))
        x += scallop
    place(face, _small(lay, face), shadow)


def ruffle(face, y0, y1, tex_img, color, wave=6, amp=1.6):
    """Gathered ruffle tier between y0 and y1: fluted folds and a wavy hem."""
    w = face.width
    xs = np.arange(w)
    hem = y1 + amp * np.sin(2 * np.pi * xs / wave)
    yy = np.arange(face.height)[:, None]
    m = ((yy >= y0) & (yy <= hem[None, :])).astype(np.uint8) * 255
    lay = tex_img.copy()
    lay.putalpha(Image.fromarray(m))
    flute = np.clip(128 + 44 * np.cos(2 * np.pi * xs / wave), 0, 255).astype(np.uint8)
    shade = Image.fromarray(np.broadcast_to(flute[None, :], (face.height, w)).copy(), "L")
    lay = fx.apply_shade(lay, shade, 0.8)
    d = ImageDraw.Draw(lay)
    d.line([(0, y0), (w, y0)], fill=fx.rgba(fx.tone(color, 0.6), 200))
    dark = Image.new("RGBA", face.size)
    ImageDraw.Draw(dark).line([(0, y0 + 1), (w, y0 + 1)], fill=fx.rgba(fx.tone(color, 0.75), 160))
    over(lay, fx.clip_to(dark, lay))
    place(face, lay, (0, 1, 1.0, 0.45))


def lacing(face, cx, y0, y1, gap, color, eyelet=(210, 210, 216), step=8, bow_top=True):
    """Corset lacing: criss-crossed ribbon between two rows of eyelets."""
    big = _big(face)
    d = ImageDraw.Draw(big)
    s = SS
    ys = list(np.arange(y0, y1 + 0.1, step))
    lx, rx = cx - gap / 2, cx + gap / 2
    for a, b in zip(ys, ys[1:]):
        d.line([(lx * s, a * s), (rx * s, b * s)], fill=fx.rgba(fx.tone(color, 0.8)), width=int(1.3 * s))
        d.line([(rx * s, a * s), (lx * s, b * s)], fill=fx.rgba(color), width=int(1.3 * s))
    for y in ys:
        for x in (lx, rx):
            d.ellipse([(x - 1.2) * s, (y - 1.2) * s, (x + 1.2) * s, (y + 1.2) * s], fill=fx.rgba(eyelet),
                      outline=fx.rgba(fx.tone(eyelet, 0.55)))
    place(face, _small(big, face), (0, 1, 0.6, 0.5))
    if bow_top:
        bow(face, cx, y0 - 1, 9, color, tails=0.9)


def chain(face, pts, color=(220, 220, 226), link=2.6, width=1.0):
    """A small metal chain along a polyline."""
    big = _big(face)
    d = ImageDraw.Draw(big)
    s = SS
    seg = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / link))
        seg += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    for i, (x, y) in enumerate(seg):
        rx, ry = (link * 0.65, link * 0.38) if i % 2 == 0 else (link * 0.38, link * 0.38)
        d.ellipse([(x - rx) * s, (y - ry) * s, (x + rx) * s, (y + ry) * s], outline=fx.rgba(color),
                  width=int(width * s))
    place(face, _small(big, face), (0, 1, 0.5, 0.45))


def pearls(face, pts, r=1.3, color=(250, 246, 238)):
    big = _big(face)
    d = ImageDraw.Draw(big)
    s = SS
    for x, y in pts:
        d.ellipse([(x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s], fill=fx.rgba(color),
                  outline=fx.rgba(fx.tone(color, 0.75)))
        d.ellipse([(x - r * 0.5) * s, (y - r * 0.6) * s, (x - r * 0.05) * s, (y - r * 0.15) * s],
                  fill=(255, 255, 255, 255))
    place(face, _small(big, face), (0, 1, 0.5, 0.4))


def necklace(face, cx, depth, width, color=(232, 196, 110), pendant="heart", pendant_color=None):
    """Fine chain draped from the neckline with a small pendant."""
    big = _big(face)
    d = ImageDraw.Draw(big)
    s = SS
    pts = arc_points(cx, 0, width / 2, depth, 0, 180, 30)
    d.line([(x * s, y * s) for x, y in pts], fill=fx.rgba(color), width=int(0.7 * s))
    px, py = cx, depth + 2
    pc = pendant_color or color
    if pendant == "heart":
        d.polygon([(x * s, y * s) for x, y in heart_points(px, py, 2.2)], fill=fx.rgba(pc),
                  outline=fx.rgba(fx.tone(pc, 0.7)))
    elif pendant == "pearl":
        d.ellipse([(px - 1.6) * s, (py - 1.6) * s, (px + 1.6) * s, (py + 1.6) * s], fill=fx.rgba(pc))
    place(face, _small(big, face), (0, 1, 0.5, 0.4))


def smocking(face, y0, y1, color, step=3):
    """Shirring: rows of elastic gathers across a panel."""
    d = ImageDraw.Draw(face)
    for y in range(int(y0), int(y1), step):
        pts = [(x, y + 0.6 * math.sin(x / 2.2)) for x in range(0, face.width + 1, 2)]
        d.line(pts, fill=fx.rgba(fx.tone(color, 0.72), 190))
        d.line([(x, yy + 1) for x, yy in pts], fill=fx.rgba(fx.tone(color, 1.25), 120))


def rhinestones(face, pts, r=0.9, color=(236, 240, 250)):
    big = _big(face)
    d = ImageDraw.Draw(big)
    s = SS
    for x, y in pts:
        d.ellipse([(x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s], fill=fx.rgba(color),
                  outline=fx.rgba(fx.tone(color, 0.6)))
        d.point([((x - r * 0.3) * s, (y - r * 0.3) * s)], fill=(255, 255, 255, 255))
    place(face, _small(big, face), (0, 1, 0.4, 0.35))
