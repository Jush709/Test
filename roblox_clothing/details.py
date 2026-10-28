"""Garment details drawn onto individual faces: trims, zips, pockets, text."""

import math
from functools import lru_cache

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
