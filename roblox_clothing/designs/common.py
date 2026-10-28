"""Shared building blocks for shirt and pants designs."""

import math

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


# ---------------------------------------------------------------- sleeves

def puff(g, y0, y1, gathers=6):
    """Balloon a sleeve section: a soft highlight in the middle, gathered creases at both ends."""
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            w, h = img.size
            m = Image.new("L", img.size, 128)
            d = ImageDraw.Draw(m)
            mid = (y0 + y1) / 2
            d.ellipse([6, mid - (y1 - y0) * 0.36, w - 6, mid + (y1 - y0) * 0.36], fill=172)
            d.rectangle([0, y0, w, y0 + 2], fill=70)
            d.rectangle([0, y1 - 3, w, y1], fill=70)
            m = m.filter(ImageFilter.GaussianBlur(3))
            d = ImageDraw.Draw(m)
            for i in range(gathers):
                x = (i + 0.5) * w / gathers
                d.line([(x, y0), (x + 1, y0 + (y1 - y0) * 0.28)], fill=88, width=1)
                d.line([(x, y1), (x - 1, y1 - (y1 - y0) * 0.24)], fill=88, width=1)
            m = m.filter(ImageFilter.GaussianBlur(0.7))
            img.paste(fx.apply_shade(img, m, 1.0), (0, 0))


def gathered_cuff(g, end, color, band=4, frill=3, tex=None):
    """Elastic band at the sleeve end with a little frill below it."""
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            lay = Image.new("RGBA", img.size)
            d = ImageDraw.Draw(lay)
            d.rectangle([0, end - band, img.width, end - 1], fill=fx.rgba(fx.tone(color, 0.9)))
            for x in range(0, img.width, 3):
                d.line([(x, end - band), (x, end - 1)], fill=fx.rgba(fx.tone(color, 0.78), 160))
            dt.place(img, lay, (0, 1, 0.8, 0.4))
            if frill:
                src = (tex or (lambda size, ox=0: fx.fabric(size, color, 0.01)))(img.size)
                dt.ruffle(img, end, end + frill, src, color, wave=5, amp=1.0)


# ---------------------------------------------------------------- legwear

def tights(g, color=(20, 20, 24), opacity=0.62, y0=0, y1=128):
    """Sheer tights: tinted, a little denser at the edges, with a soft sheen down the front."""
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            w, h = img.size
            x = np.linspace(-1, 1, w)
            a = opacity + (1 - opacity) * 0.45 * np.abs(x) ** 2
            if f == "F":
                a = a - 0.16 * np.exp(-(x / 0.28) ** 2)
            alpha = np.zeros((h, w), np.float32)
            alpha[int(y0):int(y1)] = a[None, :]
            lay = Image.new("RGBA", img.size, fx.rgba(color))
            lay.putalpha(Image.fromarray(np.clip(alpha * 255, 0, 255).astype(np.uint8)))
            over(img, lay)


def thigh_highs(g, color=(250, 250, 250), top=54, bottom=128, band=None, bow=None):
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            over(img, fx.ribbed((img.width, bottom - top), color, period=3, depth=0.12), (0, top))
            d = ImageDraw.Draw(img)
            bc = band or fx.tone(color, 0.92)
            d.rectangle([0, top, img.width, top + 4], fill=fx.rgba(bc))
            d.line([(0, top + 5), (img.width, top + 5)], fill=fx.rgba(fx.tone(color, 0.75), 160))
        if bow:
            dt.bow(limb.faces["F"], 32, top + 3, 11, bow, tails=0.8)


def leg_warmers(g, color, y0=70, y1=118):
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            dt.rib_band(img, y0, y1, color, period=3)
            d = ImageDraw.Draw(img)
            for i, y in enumerate(range(int(y0) + 6, int(y1) - 2, 7)):
                pts = [(x, y + 1.6 * math.sin(x / 7 + i)) for x in range(0, img.width + 1, 3)]
                d.line(pts, fill=fx.rgba(fx.tone(color, 0.62), 210), width=1)
                d.line([(x, yy - 1) for x, yy in pts], fill=fx.rgba(fx.tone(color, 1.3), 150), width=1)


def lace_socks(g, color=(252, 252, 252), y0=100, y1=116):
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            dt.rib_band(img, y0, y1, color, period=2)
            dt.lace_band(img, y0 - 5, y0 + 1, color, scallop=6, edge="top")


# ---------------------------------------------------------------- shoes

def _sole(limb, color):
    D = Image.new("RGBA", limb.size("D"), fx.rgba(fx.tone(color, 0.85)))
    d = ImageDraw.Draw(D)
    for y in range(4, D.height - 2, 6):
        d.line([(6, y), (D.width - 6, y)], fill=fx.rgba(fx.tone(color, 0.65)), width=2)
    limb.faces["D"] = D


def mary_janes(g, color=(24, 22, 26), bow=None, height=12):
    dress_shoes(g, color, height)
    for limb in g.limbs:
        F = limb.faces["F"]
        y0 = 128 - height
        d = ImageDraw.Draw(F)
        d.line([(10, y0 + 2), (54, y0 + 2)], fill=fx.rgba(fx.tone(color, 0.55)), width=2)
        if bow:
            dt.bow(F, 32, y0 + 6, 10, bow, tails=0.4)
        out = limb.faces[OUTER[limb.name]]
        ImageDraw.Draw(out).line([(10, y0 + 2), (54, y0 + 2)], fill=fx.rgba(fx.tone(color, 0.55)), width=2)
        dt.button(out, 50, y0 + 2, 1.4, (214, 214, 220), holes=False)


def loafers(g, color=(40, 26, 20)):
    dress_shoes(g, color, 12)
    for limb in g.limbs:
        d = ImageDraw.Draw(limb.faces["F"])
        d.rectangle([16, 120, 48, 122], fill=fx.rgba(fx.tone(color, 0.6)))
        d.rectangle([28, 120, 36, 122], fill=fx.rgba(fx.tone(color, 0.35)))


def ballet_flats(g, color=(248, 214, 222), bow=None):
    dress_shoes(g, color, 8)
    for limb in g.limbs:
        dt.bow(limb.faces["F"], 32, 122, 9, bow or fx.tone(color, 0.85), tails=0.3)


def chunky_sneakers(g, upper=(248, 248, 248), sole=(244, 244, 244), accent=(226, 226, 232), height=20,
                    lace=(240, 240, 240)):
    """Dad-shoe sneakers: a tall wavy midsole, overlay panels and laces."""
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            w, h = img.size
            y0 = h - height
            lay = Image.new("RGBA", img.size)
            d = ImageDraw.Draw(lay)
            d.rectangle([0, y0, w, h], fill=fx.rgba(upper))
            sy = h - 8
            pts = [(x, sy + 1.2 * math.sin(x / 6)) for x in range(0, w + 1, 2)]
            d.polygon(pts + [(w, h), (0, h)], fill=fx.rgba(sole))
            d.line(pts, fill=fx.rgba(fx.tone(sole, 0.7)), width=1)
            d.line([(0, h - 2), (w, h - 2)], fill=fx.rgba(fx.tone(sole, 0.78)), width=2)
            d.line([(0, y0), (w, y0)], fill=fx.rgba(fx.tone(upper, 0.6)), width=1)
            if f == "F":
                d.rounded_rectangle([16, y0 - 3, w - 16, y0 + 8], radius=3, fill=fx.rgba(fx.tone(upper, 0.95)),
                                    outline=fx.rgba(fx.tone(upper, 0.72)))
                for i in range(3):
                    y = y0 + 1.5 + i * 2.6
                    d.line([(20, y), (w - 20, y + 1.6)], fill=fx.rgba(fx.tone(lace, 0.75)))
                    d.line([(20, y + 1.6), (w - 20, y)], fill=fx.rgba(lace))
                d.polygon([(4, sy), (12, y0 + 10), (w - 12, y0 + 10), (w - 4, sy)], fill=fx.rgba(accent))
            elif f in "LR":
                d.polygon([(4, sy), (16, y0 + 4), (34, y0 + 4), (50, sy)], fill=fx.rgba(accent))
                d.polygon([(30, sy), (44, y0 + 8), (60, y0 + 8), (60, sy)], fill=fx.rgba(fx.tone(accent, 0.92)))
            else:
                d.rectangle([22, y0 - 3, 42, y0 + 9], fill=fx.rgba(accent))
            sh = Image.new("RGBA", img.size)
            ImageDraw.Draw(sh).rectangle([0, y0 - 3, w, y0], fill=(0, 0, 0, 70))
            over(img, fx.clip_to(sh.filter(ImageFilter.GaussianBlur(1.2)), img))
            over(img, lay)
        _sole(limb, sole)


def platform_boots(g, color=(22, 22, 24), height=34, sole_h=9, lace=(40, 40, 44)):
    """Chunky lace-up combat boots with a lug sole."""
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            w, h = img.size
            y0 = h - height
            lay = fx.smooth((w, h), color, 0.01, 0.12)
            m = np.zeros((h, w), np.uint8)
            m[y0:] = 255
            lay.putalpha(Image.fromarray(m))
            d = ImageDraw.Draw(lay)
            d.rectangle([0, h - sole_h, w, h], fill=fx.rgba(fx.tone(color, 0.75)))
            for x in range(0, w, 6):
                d.rectangle([x, h - 3, x + 3, h], fill=fx.rgba(fx.tone(color, 0.45)))
            d.line([(0, h - sole_h), (w, h - sole_h)], fill=fx.rgba(fx.tone(color, 2.0), 90))
            dt.stitch(d, [(0, h - sole_h + 2), (w, h - sole_h + 2)], fx.rgba(fx.tone(color, 1.9), 120), 2, 2)
            d.rectangle([0, y0, w, y0 + 3], fill=fx.rgba(fx.tone(color, 1.25)))
            if f == "F":
                for y in range(y0 + 5, h - sole_h - 4, 4):
                    d.line([(24, y), (40, y + 3)], fill=fx.rgba(lace), width=1)
                    d.line([(40, y), (24, y + 3)], fill=fx.rgba(fx.tone(lace, 1.6)), width=1)
                    for x in (23, 41):
                        d.point([(x, y)], fill=fx.rgba((200, 200, 206)))
            elif f == "B":
                d.rectangle([28, y0 - 4, 36, y0 + 4], fill=fx.rgba(fx.tone(color, 1.2)))
            elif f == INNER[limb.name]:
                d.line([(32, y0 + 4), (32, h - sole_h - 2)], fill=fx.rgba((180, 180, 186)), width=1)
            over(img, lay)
            if f in ("F", OUTER[limb.name]):
                sheen(img, 14, 22, 0.14, 3)
        _sole(limb, fx.tone(color, 0.75))


def knee_boots(g, color=(24, 20, 20), top=66):
    """Tall smooth leather boots with a side zip and a block heel at the back."""
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            w, h = img.size
            lay = fx.smooth((w, h), color, 0.008, 0.10)
            m = np.zeros((h, w), np.uint8)
            m[top:] = 255
            lay.putalpha(Image.fromarray(m))
            d = ImageDraw.Draw(lay)
            d.line([(0, top), (w, top)], fill=fx.rgba(fx.tone(color, 1.8), 140))
            d.rectangle([0, h - 3, w, h], fill=fx.rgba(fx.tone(color, 0.5)))
            if f == "B":
                d.rectangle([20, h - 10, 44, h], fill=fx.rgba(fx.tone(color, 0.6)))
            if f == INNER[limb.name]:
                dt.zipper(lay, 32, top + 2, h - 4, color, teeth=(190, 190, 196), pull_y=top + 3)
            over(img, lay)
            if f in ("F", OUTER[limb.name]):
                sheen(img, 18, 26, 0.2, 3)
                sheen(img, 40, 43, 0.08, 2)
        _sole(limb, fx.tone(color, 0.6))


# ---------------------------------------------------------------- belts

def belt(g, y, h, color, buckle="square", buckle_color=(214, 214, 222), studs=None, x=64, loops=False):
    T = g.torso
    for f in T.sides:
        img = T.faces[f]
        lay = fx.smooth((img.width, img.height), color, 0.01, 0.08)
        m = np.zeros(img.size[::-1], np.uint8)
        m[int(y):int(y + h)] = 255
        lay.putalpha(Image.fromarray(m))
        d = ImageDraw.Draw(lay)
        d.line([(0, y), (img.width, y)], fill=fx.rgba(fx.tone(color, 1.5), 110))
        if studs:
            for sx in range(4, img.width, 7):
                d.ellipse([sx - 1.2, y + h / 2 - 1.2, sx + 1.2, y + h / 2 + 1.2], fill=fx.rgba(studs),
                          outline=fx.rgba(fx.tone(studs, 0.6)))
        dt.place(img, lay, (0, 1, 0.8, 0.5))
    F = T.faces["F"]
    if buckle == "heart":
        big = dt._big(F)
        bd = ImageDraw.Draw(big)
        s = dt.SS
        pts = [(px * s, py * s) for px, py in dt.heart_points(x, y + h / 2, h * 0.95)]
        bd.polygon(pts, outline=fx.rgba(buckle_color), width=int(1.6 * s))
        dt.place(F, dt._small(big, F), (0, 1, 0.5, 0.5))
    elif buckle == "square":
        lay = Image.new("RGBA", F.size)
        ImageDraw.Draw(lay).rounded_rectangle([x - h * 0.8, y - 1, x + h * 0.8, y + h], radius=1,
                                              outline=fx.rgba(buckle_color), width=2)
        dt.place(F, lay, (0, 1, 0.5, 0.5))
    elif buckle == "double":
        for dx in (-5, 5):
            lay = Image.new("RGBA", F.size)
            ImageDraw.Draw(lay).ellipse([x + dx - h * 0.55, y - 0.5, x + dx + h * 0.55, y + h - 0.5],
                                        outline=fx.rgba(buckle_color), width=1)
            dt.place(F, lay, (0, 1, 0.5, 0.5))


# ---------------------------------------------------------------- necklines & cut-outs

def tex_satin(color, sheen=0.35):
    return lambda size, ox=0: fx.satin(size, color, seed=size[0] + ox, sheen=sheen)


def tex_mohair(color):
    return lambda size, ox=0: fx.mohair(size, color, seed=size[0] + ox)


def tex_rib(color, period=2, depth=0.08):
    return lambda size, ox=0: fx.ribbed(size, color, period, depth)


def tex_gingham(color, check=5):
    return lambda size, ox=0: fx.gingham(size, color, check=check, offset=(ox, 0))


def tex_print(base, motif, spacing=(16, 16), ground=None):
    return lambda size, ox=0: fx.print_pattern(size, base, motif, spacing, seed=size[0] + ox, ground=ground)


def sweetheart_mask(size, depth=22, x0=26, x1=102):
    """The area cut away by a sweetheart neckline: two scoops meeting in a point at the centre."""
    cx = (x0 + x1) / 2

    def draw(d):
        d.rectangle([x0, -4, x1, depth * 0.3], fill=255)
        d.ellipse([x0, -depth * 0.7, cx + 2, depth], fill=255)
        d.ellipse([cx - 2, -depth * 0.7, x1, depth], fill=255)
    return mask_from(size, draw)


def clear(img, box):
    """Make a rectangle of a face transparent."""
    fx.cut(img, mask_from(img.size, lambda d: d.rectangle(box, fill=255)))


def keep_only(img, draw_fn):
    """Make everything outside the drawn shape transparent."""
    m = mask_from(img.size, draw_fn)
    fx.cut(img, m.point(lambda v: 255 - v))


def edge_trim(img, cut_mask, color, width=3, alpha=255):
    """Paint a trim band hugging the edge of an area about to be cut away."""
    grown = cut_mask.filter(ImageFilter.MaxFilter(width * 2 + 1))
    band = np.asarray(grown, np.float32) - np.asarray(cut_mask, np.float32)
    band = np.minimum(band, np.asarray(img.getchannel("A"), np.float32))
    lay = Image.new("RGBA", img.size, fx.rgba(color))
    lay.putalpha(Image.fromarray(np.clip(band * alpha / 255, 0, 255).astype(np.uint8)))
    dt.place(img, lay, (0, 1, 0.8, 0.45))


def scallop_edge(img, cut_mask, color, r=2.0, step=4.5):
    """Little scallops along the inside of a cut-out edge (lace or crochet trim)."""
    edge = np.asarray(cut_mask.filter(ImageFilter.MaxFilter(3)), np.int16) - np.asarray(cut_mask, np.int16)
    ys, xs = np.nonzero(edge > 0)
    if not len(xs):
        return
    order = np.argsort(xs)
    lay = Image.new("RGBA", (img.width * 4, img.height * 4))
    d = ImageDraw.Draw(lay)
    last = -99
    for i in order:
        x, y = xs[i], ys[i]
        if x - last < step:
            continue
        last = x
        d.ellipse([(x - r) * 4, (y - r) * 4, (x + r) * 4, (y + r) * 4], fill=fx.rgba(color),
                  outline=fx.rgba(fx.tone(color, 0.8)))
    dt.place(img, lay.resize(img.size, Image.LANCZOS), (0, 1, 0.6, 0.35))


def flare(g, y0=84, y1=128, depth=1.0):
    """Shade legs so they read as flaring out below the knee."""
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            w, h = img.size
            m = Image.new("L", img.size, 128)
            d = ImageDraw.Draw(m)
            for x1, v in ((4, 80), (18, 170), (30, 84), (44, 172), (58, 82)):
                d.line([(32, y0), (x1, y1)], fill=v, width=3)
            m = m.filter(ImageFilter.GaussianBlur(2.2))
            mask = np.zeros((h, w), np.float32)
            mask[int(y0):int(y1)] = np.linspace(0, 1, int(y1) - int(y0))[:, None] ** 0.8
            arr = 128 + (np.asarray(m, np.float32) - 128) * mask * depth
            img.paste(fx.apply_shade(img, Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), 1.0), (0, 0))


def drape(img, y0, y1, period=12, depth=0.5, seed=0):
    """Soft vertical folds for flowy skirts and dresses (stronger towards the hem)."""
    w, h = img.size
    n = fx.smooth_noise((w, h), (period, 200), seed)
    x = np.arange(w)
    wave = np.cos(2 * np.pi * x / period + n[0] * 4)[None, :]
    ramp = np.zeros((h, 1), np.float32)
    ramp[int(y0):int(y1), 0] = np.linspace(0.3, 1, int(y1) - int(y0))
    arr = 128 + wave * ramp * 90 * depth
    img.paste(fx.apply_shade(img, Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), 1.0), (0, 0))


def fabric_tex(p):
    """Texture factory from a colourway: solid knit, gingham, satin or an all-over print."""
    kind = p.get("fabric", "cotton")
    base = p["base"]
    if kind == "gingham":
        return tex_gingham(base, p.get("check", 5))
    if kind == "satin":
        return tex_satin(base)
    if kind == "rib":
        return tex_rib(base, 2, 0.08)
    if kind == "print":
        return tex_print(base, MOTIFS[p["motif"]](*p.get("motif_args", ())), p.get("spacing", (16, 16)))
    return tex_fabric(base, 0.012)


MOTIFS = {
    "flower": fx.motif_flower,
    "cherry": fx.motif_cherry,
    "strawberry": fx.motif_strawberry,
    "heart": fx.motif_heart,
    "bow": fx.motif_bow,
    "star": fx.motif_star,
}
