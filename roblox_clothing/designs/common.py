"""Shared building blocks for shirt and pants designs."""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .. import details as dt
from .. import fx
from ..garment import Garment, over
from ..shading import shade_garment
from ..template import INNER, OUTER  # noqa: F401  (re-exported for designs)

# Lowest fabric row on arm faces for each sleeve length. Long sleeves stop
# short of the bottom so R15 hands (mapped there) stay skin-coloured.
SLEEVE = {"long": 108, "elbow": 74, "short": 46, "none": 0}


# ---------------------------------------------------------------- texture factories
# A texture factory is tex(size, ox=0) -> RGBA image; `ox` is the x offset in a
# wrap strip so woven patterns line up across seams.

def tex_fabric(color, amount=0.022, streak=0.6, seed=0):
    return lambda size, ox=0: fx.fabric(size, color, amount, seed + ox + size[0] * 7, streak)


def tex_smooth(color, amount=0.012, mottle=0.05, seed=0):
    return lambda size, ox=0: fx.smooth(size, color, amount, seed + ox + size[0], mottle=mottle)


def tex_plaid(sett, scale=1):
    sett = [(c, n * scale) for c, n in sett]
    return lambda size, ox=0: fx.plaid(size, sett, offset=(ox, 0))


def tex_denim(color, seed=0):
    return lambda size, ox=0: fx.denim(size, color, seed + size[0], offset=(ox, 0))


def tex_camo(colors, seed=0, cell=18):
    return lambda size, ox=0: fx.camo(size, colors, seed + size[0], cell)


def tex_mesh(color):
    return lambda size, ox=0: fx.mesh(size, color)


def tex_knit(color, period=32, cable=12):
    return lambda size, ox=0: fx.cable_knit(size, color, period, cable, offset=ox + 10)


def tex_stripes(colors, widths, vertical=False):
    return lambda size, ox=0: fx.stripes(size, colors, widths, vertical, ox if vertical else 0)


# ---------------------------------------------------------------- construction

def fill(part, tex, y0=0, y1=128, caps="U"):
    """Cover a part's side faces between rows y0..y1 (plus the listed caps) with fabric."""
    strip = tex((part.strip_width, 128), 0)
    if y0 > 0 or y1 < 128:
        strip = fx.keep_rows(strip, y0, y1)
    part.over_strip(strip)
    for c in caps:
        part.over(c, tex(part.size(c), 0))


def shirt(tex, sleeves="long", sleeve_tex=None, length=128):
    g = Garment("shirt")
    fill(g.torso, tex, 0, length, caps="U" + ("D" if length >= 128 else ""))
    end = SLEEVE[sleeves] if isinstance(sleeves, str) else int(sleeves)
    for limb in g.limbs:
        if end:
            fill(limb, sleeve_tex or tex, 0, end, caps="U")
    g.sleeve_end = end
    g.length = length
    return g


def pants(tex, top=96, hem=128, leg_tex=None):
    g = Garment("pants")
    fill(g.torso, tex, top, 128, caps="D")
    for limb in g.limbs:
        fill(limb, leg_tex or tex, 0, hem, caps="U" + ("D" if hem >= 128 else ""))
    g.top = top
    g.hem = hem
    return g


def finish(g, strength=0.8, seed=0, **kw):
    """Apply cloth shading using the garment's own sleeve/hem lengths."""
    if g.kind == "shirt":
        kw.setdefault("sleeve_end", g.sleeve_end or 46)
    else:
        kw.setdefault("hem", g.hem)
    shade_garment(g, strength, seed, **kw)


def sides(part):
    return [part.faces[f] for f in part.sides]


def mirror_pts(pts, w=128):
    return [(w - x, y) for x, y in pts]


def mask_from(size, draw_fn):
    m = Image.new("L", size)
    draw_fn(ImageDraw.Draw(m))
    return m


# ---------------------------------------------------------------- trims

def hem_band(g, color, height=10, period=3, bottom=None):
    y1 = bottom if bottom is not None else g.length
    for img in sides(g.torso):
        dt.rib_band(img, y1 - height, y1, color, period=period)


def cuffs(g, color, height=9, period=3):
    e = g.sleeve_end
    for limb in g.limbs:
        for img in sides(limb):
            dt.rib_band(img, e - height, e, color, period=period)


def sleeve_hem(g, color, height=5):
    """Turned-up hem on a short sleeve."""
    e = g.sleeve_end
    for limb in g.limbs:
        for img in sides(limb):
            lay = Image.new("RGBA", img.size)
            d = ImageDraw.Draw(lay)
            d.rectangle([0, e - height, img.width, e - 1], fill=fx.rgba(fx.tone(color, 0.86), 150))
            d.line([(0, e - height), (img.width, e - height)], fill=fx.rgba(fx.tone(color, 0.6), 200))
            dt.stitch(d, [(0, e - 2), (img.width, e - 2)], fx.rgba(fx.tone(color, 0.7), 220))
            over(img, fx.clip_to(lay, img))


def crew_neck(g, trim, width=44, depth=10, back_depth=4, band=3, back=True):
    faces = [("F", depth)] + ([("B", back_depth)] if back else [])
    for face, dep in faces:
        img = g.torso.faces[face]
        cx = img.width / 2
        ring = fx.ribbed(img.size, trim, period=2)
        rmask = mask_from(img.size, lambda d: d.ellipse([cx - width / 2 - band, -dep - band,
                                                          cx + width / 2 + band, dep + band], fill=255))
        ring.putalpha(rmask)
        dt.place(img, ring, (0, 1, 1.0, 0.45))
        fx.cut(img, mask_from(img.size, lambda d: d.ellipse([cx - width / 2, -dep, cx + width / 2, dep], fill=255)))


def v_neck(g, trim, width=34, depth=26, band=3, back_depth=4):
    F = g.torso.faces["F"]
    cx = 64
    outer = [(cx - width / 2 - band, 0), (cx + width / 2 + band, 0), (cx, depth + band * 1.6)]
    inner = [(cx - width / 2, 0), (cx + width / 2, 0), (cx, depth)]
    lay = dt.polygon_layer(F.size, outer, trim)
    dt.place(F, lay, (0, 1, 1.0, 0.45))
    d = ImageDraw.Draw(F)
    d.line([outer[2], (cx, depth)], fill=fx.rgba(fx.tone(trim, 0.7)))
    fx.cut(F, mask_from(F.size, lambda dd: dd.polygon(inner, fill=255)))
    B = g.torso.faces["B"]
    ring = mask_from(B.size, lambda dd: dd.ellipse([cx - 22 - band, -back_depth - band, cx + 22 + band,
                                                    back_depth + band], fill=255))
    lay = Image.new("RGBA", B.size, fx.rgba(trim))
    lay.putalpha(ring)
    dt.place(B, lay)
    fx.cut(B, mask_from(B.size, lambda dd: dd.ellipse([cx - 22, -back_depth, cx + 22, back_depth], fill=255)))


def hood(g, tex, color, lining=None):
    """Hood lying down: a thick collar around the neck in front, draped over the upper back."""
    lining = lining or fx.tone(color, 0.55)
    F, B, U = g.torso.faces["F"], g.torso.faces["B"], g.torso.faces["U"]
    cx = 64
    # front: hood edges frame the neck
    band = tex(F.size, 3)
    outer = [cx - 40, -32, cx + 40, 28]
    inner = [cx - 22, -32, cx + 22, 12]
    band.putalpha(mask_from(F.size, lambda d: d.ellipse(outer, fill=255)))
    fx.cut(band, mask_from(F.size, lambda d: d.ellipse(inner, fill=255)))
    glow = mask_from(F.size, lambda d: d.ellipse([cx - 34, -30, cx + 34, 20], fill=255)).filter(
        ImageFilter.GaussianBlur(4))
    hl = Image.new("RGBA", F.size, (255, 255, 255, 0))
    hl.putalpha(glow.point(lambda v: int(v * 0.16)))
    over(band, fx.clip_to(hl, band))
    d = ImageDraw.Draw(band)
    d.arc(outer, 0, 180, fill=fx.rgba(fx.tone(color, 0.6), 230), width=1)
    d.arc([cx - 31, -30, cx + 31, 20], 25, 155, fill=fx.rgba(fx.tone(color, 0.75), 170), width=1)
    d.arc(inner, 0, 180, fill=fx.rgba(fx.tone(color, 1.3), 220), width=1)
    dt.place(F, band, (0, 2, 2.0, 0.65))
    # a crescent of hood lining shows along the inner edge, then the neck
    neck = mask_from(F.size, lambda dd: dd.ellipse([cx - 20, -40, cx + 20, 8], fill=255))
    lin_layer = Image.new("RGBA", F.size, fx.rgba(lining))
    lin_layer.putalpha(mask_from(F.size, lambda dd: dd.ellipse(inner, fill=255)))
    fx.cut(lin_layer, neck)
    over(F, lin_layer)
    fx.cut(F, neck)
    # back: draped hood
    back = tex(B.size, 5)
    shape = [cx - 40, -44, cx + 40, 48]
    back.putalpha(mask_from(B.size, lambda d: d.ellipse(shape, fill=255)))
    d = ImageDraw.Draw(back)
    d.line([(cx, 0), (cx, 46)], fill=fx.rgba(fx.tone(color, 0.7), 220))
    d.arc([cx - 34, -30, cx + 34, 40], 25, 155, fill=fx.rgba(fx.tone(color, 0.78), 150), width=2)
    d.arc([cx - 30, -40, cx + 30, 26], 30, 150, fill=fx.rgba(fx.tone(color, 0.82), 130), width=1)
    dt.place(B, back, (0, 2, 2.5, 0.55))
    # top: hood bunched behind the head
    top = tex(U.size, 7)
    top.putalpha(mask_from(U.size, lambda d: d.ellipse([10, -34, 118, 56], fill=255)))
    fx.cut(top, mask_from(U.size, lambda d: d.ellipse([28, -10, 100, 52], fill=255)))
    dt.place(U, top, (0, 1, 1.5, 0.45))


def logo_text(face, brand, center, size, color, style="black", spacing=1):
    dt.text(face, brand, center, size, color, style=style, spacing=spacing)


def sheen(img, x0, x1, amount=0.25, blur=4):
    """Soft vertical specular streak (leather, satin, nylon)."""
    w, h = img.size
    m = Image.new("L", img.size)
    ImageDraw.Draw(m).rectangle([x0, -10, x1, h + 10], fill=int(255 * amount))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    hl = Image.new("RGBA", img.size, (255, 255, 255, 0))
    hl.putalpha(m)
    over(img, fx.clip_to(hl, img))


def fade(img, boxes, amount=0.3, blur=8, color=(255, 255, 255)):
    """Lighten elliptical areas, e.g. denim wash or sun fading."""
    m = Image.new("L", img.size)
    d = ImageDraw.Draw(m)
    for b in boxes:
        d.ellipse(b, fill=int(255 * amount))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    lay = Image.new("RGBA", img.size, fx.rgb(color) + (0,))
    lay.putalpha(m)
    over(img, fx.clip_to(lay, img))


def quilt(img, y0, period, depth=0.55, spec=0.3):
    """Puffer baffles: puffy rows with dark stitched seams and a glossy highlight."""
    w, h = img.size
    t = ((np.arange(h) - y0) % period) / period
    f = np.sin(np.pi * t)
    k = (1 - depth) + depth * f ** 0.6 + spec * np.exp(-((t - 0.33) / 0.1) ** 2)
    s = np.clip(128 + (k - 1) * 127, 0, 255).astype(np.uint8)
    shade = Image.fromarray(np.repeat(s[:, None], w, axis=1), "L")
    return fx.apply_shade(img, shade, 1.0)


def sneakers(g, upper=(245, 245, 245), sole=(250, 250, 250), accent=None, height=16, lace=(235, 235, 235)):
    """Low-top sneakers drawn on the bottom of both legs (the foot on R15)."""
    accent = accent or fx.tone(upper, 0.85)
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            w, h = img.size
            y0 = h - height
            lay = Image.new("RGBA", img.size)
            d = ImageDraw.Draw(lay)
            d.rectangle([0, y0, w, h], fill=fx.rgba(upper))
            d.rectangle([0, h - 5, w, h], fill=fx.rgba(sole))
            d.line([(0, h - 5), (w, h - 5)], fill=fx.rgba(fx.tone(sole, 0.75)))
            dt.stitch(d, [(0, h - 3), (w, h - 3)], fx.rgba(fx.tone(sole, 0.7)), dash=2, gap=2)
            d.line([(0, y0), (w, y0)], fill=fx.rgba(fx.tone(upper, 0.7)))
            if f == "F":
                d.rounded_rectangle([18, y0 - 3, w - 18, y0 + 6], radius=3, fill=fx.rgba(fx.tone(upper, 0.93)),
                                    outline=fx.rgba(fx.tone(upper, 0.75)))
                for i in range(3):
                    y = y0 + 1 + i * 2.5
                    d.line([(22, y), (w - 22, y + 1.5)], fill=fx.rgba(fx.tone(lace, 0.8)), width=1)
                    d.line([(22, y + 1.5), (w - 22, y)], fill=fx.rgba(lace), width=1)
                d.arc([6, h - 14, w - 6, h + 4], 180, 360, fill=fx.rgba(fx.tone(upper, 0.8)), width=1)
            elif f in "LR":
                d.polygon([(10, h - 6), (24, y0 + 3), (40, y0 + 3), (54, h - 6)], fill=fx.rgba(accent))
                d.line([(6, y0 + 4), (6, h - 6)], fill=fx.rgba(fx.tone(upper, 0.75)))
            else:
                d.rectangle([24, y0 - 2, 40, y0 + 8], fill=fx.rgba(accent))
            img_shadow = Image.new("RGBA", img.size)
            ImageDraw.Draw(img_shadow).rectangle([0, y0 - 3, w, y0], fill=(0, 0, 0, 70))
            over(img, fx.clip_to(img_shadow.filter(ImageFilter.GaussianBlur(1.2)), img))
            over(img, lay)
        D = limb.faces["D"]
        sd = Image.new("RGBA", D.size, fx.rgba(fx.tone(sole, 0.85)))
        dd = ImageDraw.Draw(sd)
        for y in range(4, D.height - 2, 6):
            dd.line([(6, y), (D.width - 6, y)], fill=fx.rgba(fx.tone(sole, 0.7)), width=2)
        limb.faces["D"] = sd


def dress_shoes(g, color=(26, 22, 22), height=12):
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            w, h = img.size
            y0 = h - height
            lay = Image.new("RGBA", img.size)
            d = ImageDraw.Draw(lay)
            d.rectangle([0, y0, w, h], fill=fx.rgba(color))
            d.rectangle([0, h - 3, w, h], fill=fx.rgba(fx.tone(color, 0.6)))
            if f == "F":
                d.line([(14, y0 + 3), (w - 14, y0 + 3)], fill=fx.rgba(fx.tone(color, 1.35)))
            over(img, lay)
            if f == "F":
                sheen(img, w * 0.3, w * 0.42, 0.08, 2)
        limb.faces["D"] = Image.new("RGBA", limb.size("D"), fx.rgba(fx.tone(color, 0.5)))


def socks(g, color=(250, 250, 250), y0=92, y1=114, stripe=None):
    for limb in g.limbs:
        for img in sides(limb):
            dt.rib_band(img, y0, y1, color, period=2)
            if stripe:
                d = ImageDraw.Draw(img)
                d.rectangle([0, y0 + 3, img.width, y0 + 5], fill=fx.rgba(stripe))
                d.rectangle([0, y0 + 8, img.width, y0 + 9], fill=fx.rgba(stripe))


def tiedye_tex(colors, seed=0):
    # spiral centred on the chest when painting the torso wrap strip (front face spans x 64..192)
    return lambda size, ox=0: fx.tiedye(size, colors, center=(128, 50) if size[0] == 384 else None,
                                        seed=seed + size[0])
