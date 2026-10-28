"""Pants designs. Each function takes a colourway dict and the brand name and
returns a finished Garment."""

import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .. import details as dt
from .. import fx
from ..garment import Garment, over
from ..template import inner_edge_x
from . import common as c

SHOE_H = 16


def waistband(g, tex, y0=96, h=10, ink=None, loops=(10, 40, 88, 118), back_loops=(12, 64, 116), thread=None):
    ink = ink or (0, 0, 0)
    for f in g.torso.sides:
        img = g.torso.faces[f]
        over(img, tex((img.width, h), 2), (0, y0))
        d = ImageDraw.Draw(img)
        d.line([(0, y0 + h), (img.width, y0 + h)], fill=fx.rgba(ink, 150))
        if thread:
            dt.stitch(d, [(0, y0 + 2), (img.width, y0 + 2)], fx.rgba(thread, 220), 2, 2)
            dt.stitch(d, [(0, y0 + h - 2), (img.width, y0 + h - 2)], fx.rgba(thread, 220), 2, 2)
        xs = loops if f == "F" else back_loops if f == "B" else (32,)
        for x in xs:
            lay = Image.new("RGBA", img.size)
            ImageDraw.Draw(lay).rectangle([x - 1, y0 - 1, x + 2, y0 + h + 1], fill=fx.rgba(ink, 60))
            over(lay, tex((4, h + 3), 5), (x - 1, y0 - 1))
            dt.place(img, lay, (1, 1, 0.6, 0.45))


def drawstring_waist(g, color, y0=94, h=14, string=(245, 245, 245)):
    for img in c.sides(g.torso):
        dt.rib_band(img, y0, y0 + h, color, period=3)
        d = ImageDraw.Draw(img)
        d.line([(0, y0 + 3), (img.width, y0 + 3)], fill=fx.rgba(fx.tone(color, 0.75), 120))
    F = g.torso.faces["F"]
    dt.drawstrings(F, (60, 68), y0 + 7, 15, string, tip=fx.tone(string, 0.8), sway=1)


def side_seams(g, color, k=0.7):
    for limb in g.limbs:
        for f in (c.INNER[limb.name], c.OUTER[limb.name]):
            img = limb.faces[f]
            ImageDraw.Draw(img).line([(32, 0), (32, g.hem)], fill=fx.rgba(fx.tone(color, k), 170))


def rip(img, box, thread=(236, 232, 222), seed=0):
    """Distressed knee rip: a hole with white weft threads across it and frayed edges."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    hole = Image.new("L", img.size)
    hd = ImageDraw.Draw(hole)
    pts = []
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    for i in range(16):
        a = i / 16 * 2 * np.pi
        k = rnd.uniform(0.75, 1.1)
        pts.append((cx + rx * k * np.cos(a), cy + ry * k * np.sin(a)))
    hd.polygon(pts, fill=255)
    fray = hole.filter(ImageFilter.MaxFilter(3))
    lay = Image.new("RGBA", img.size, fx.rgba(thread, 0))
    lay.putalpha(fray.point(lambda v: int(v * 0.8)))
    over(img, fx.clip_to(lay, img))
    fx.cut(img, hole)
    d = ImageDraw.Draw(img)
    for y in range(int(y0) + 1, int(y1), 2):
        d.line([(x0 - 1 + rnd.uniform(0, 2), y), (x1 + 1 - rnd.uniform(0, 2), y + rnd.uniform(-0.6, 0.6))],
               fill=fx.rgba(thread, 235))


def legs_and_shoes(g, p, skirt_end=0):
    """Legwear and shoes for skirts and shorts, chosen by the colourway."""
    white = (252, 252, 252)
    leg = p.get("legwear")
    shoe = p.get("shoes", "mary_janes")
    shoe_h = {"chunky": 20, "sneakers": 16, "platform_boots": 34}.get(shoe, 12)
    if leg == "knee_socks":
        c.socks(g, p.get("socks", white), 76, 114, stripe=p.get("sock_stripe"))
    elif leg == "crew_socks":
        c.socks(g, p.get("socks", white), 98, 112, stripe=p.get("sock_stripe"))
    elif leg == "tights":
        c.tights(g, p.get("tights", (22, 22, 26)), p.get("tights_opacity", 0.6), y0=skirt_end)
    elif leg == "thigh_highs":
        c.thigh_highs(g, p.get("socks", white), top=p.get("sock_top", 56), band=p.get("sock_band"),
                      bow=p.get("sock_bow"))
    elif leg == "leg_warmers":
        c.leg_warmers(g, p.get("warmers", white), 70, 128 - shoe_h + 4)
    elif leg == "lace_socks":
        c.lace_socks(g, p.get("socks", white), 102, 116)
    color = p.get("shoe_color", (24, 22, 26))
    if shoe == "mary_janes":
        c.mary_janes(g, color, bow=p.get("shoe_bow"))
    elif shoe == "loafers":
        c.loafers(g, color)
    elif shoe == "ballet":
        c.ballet_flats(g, color, bow=p.get("shoe_bow"))
    elif shoe == "platform_boots":
        c.platform_boots(g, color)
    elif shoe == "knee_boots":
        c.knee_boots(g, color, top=p.get("boot_top", 66))
    elif shoe == "chunky":
        c.chunky_sneakers(g, **p.get("sneakers", {}))
    elif shoe == "sneakers":
        c.sneakers(g, **p.get("sneakers", {}))


def _belt(g, p, y):
    """Optional belt from the colourway: studded, heart buckle or a draped chain."""
    kind = p.get("belt")
    if not kind:
        return False
    F = g.torso.faces["F"]
    if kind == "studded":
        c.belt(g, y, 7, (20, 20, 22), "square", (210, 210, 216), studs=(214, 214, 220))
    elif kind == "heart":
        c.belt(g, y, 6, p.get("belt_color", (236, 120, 160)), "heart", (226, 226, 232))
    elif kind == "chain":
        c.belt(g, y, 6, p.get("belt_color", (24, 22, 24)), "double", (210, 210, 216))
        dt.chain(F, [(14, y + 7), (36, y + 15), (64, y + 18), (92, y + 15), (114, y + 7)], (220, 220, 226))
    else:
        c.belt(g, y, 6, p.get("belt_color", (60, 40, 30)), "square", (220, 190, 120))
    return True


def jeans(p, brand, baggy=0.8, rips=False, shoes=None, top=96, flared=False):
    denim_c = p["denim"]
    thread = p.get("thread", (214, 150, 70))
    tex = c.tex_denim(denim_c)
    hem = 128 - (SHOE_H if shoes else 0)
    g = c.pants(tex, top=top)
    T = g.torso
    F = T.faces["F"]
    ink = fx.tone(denim_c, 0.5)
    wash = p.get("wash", 0.25)
    for limb in g.limbs:
        c.fade(limb.faces["F"], [(10, 6, 54, 58), (14, 56, 50, 84)], wash, 10)
        c.fade(limb.faces["B"], [(8, 2, 56, 40), (12, 80, 52, 110)], wash * 0.7, 10)
        for f in (c.INNER[limb.name], c.OUTER[limb.name]):
            c.fade(limb.faces[f], [(10, 10, 54, 100)], wash * 0.5, 12)
        # whiskers fanning out from the crotch
        img = limb.faces["F"]
        ix = inner_edge_x(limb.name, "F", 64)
        sgn = -1 if ix else 1
        lay = Image.new("RGBA", img.size)
        ld = ImageDraw.Draw(lay)
        for i in range(4):
            ld.line([(ix + sgn * 3, 4 + i * 4), (ix + sgn * (18 + i * 3), 2 + i * 7)],
                    fill=(255, 255, 255, 90), width=1)
        over(img, fx.clip_to(lay.filter(ImageFilter.GaussianBlur(0.8)), img))
        # back pockets with a stitched arc (or a heart)
        B = limb.faces["B"]
        pk = [(14, 8), (50, 8), (50, 32), (32, 38), (14, 32)]
        lay = dt.textured_polygon(B.size, pk, tex(B.size, 4))
        ld = ImageDraw.Draw(lay)
        ld.line(pk + [pk[0]], fill=fx.rgba(ink))
        dt.stitch(ld, [(16, 10), (16, 31), (32, 36), (48, 31), (48, 10)], fx.rgba(thread), 2, 2)
        if p.get("heart_pockets"):
            heart = dt.heart_points(32, 22, 8, 24)
            dt.stitch(ld, heart + [heart[0]], fx.rgba(p["heart_pockets"]), 2, 1)
        else:
            dt.stitch(ld, [(18, 22), (32, 16), (46, 22)], fx.rgba(thread), 2, 2)
        dt.place(B, lay, (0, 1, 0.8, 0.45))
        dd = ImageDraw.Draw(B)
        dd.line([(0, 0), (64, 0)], fill=fx.rgba(ink))
    side_seams(g, denim_c, 0.55)
    waistband(g, tex, y0=top, ink=ink, thread=thread)
    d = ImageDraw.Draw(F)
    y = top + 10
    dt.stitch(d, [(70, y + 2), (70, 122), (64, 127)], fx.rgba(thread), 2, 2)
    d.line([(64, y), (64, 128)], fill=fx.rgba(ink))
    for side in (0, 1):
        pts = [(26, y), (18, y + 6), (12, 127)]
        pts = c.mirror_pts(pts) if side else pts
        d.line(pts, fill=fx.rgba(ink), width=1)
        dt.stitch(d, [(x + (2 if side else -2), yy) for x, yy in pts], fx.rgba(thread), 2, 2)
    if y + 10 < 128:
        dt.stitch(d, [(92, y + 2), (102, y + 2), (102, min(127, y + 10))], fx.rgba(thread), 2, 1)
    if rips:
        for limb in g.limbs:
            rip(limb.faces["F"], (16, 60, 46, 70), seed=limb.name)
            rip(limb.faces["F"], (24, 26, 36, 30), seed=limb.name + "t")
    for limb in g.limbs:
        for f in limb.sides:
            dt.stitch(ImageDraw.Draw(limb.faces[f]), [(0, hem - 4), (64, hem - 4)], fx.rgba(thread), 2, 2)
    if flared:
        c.flare(g, 80, hem, 1.1)
    c.finish(g, 0.9, baggy=baggy, hem=hem, fit="fitted" if flared or baggy < 0.5 else "relaxed")
    if not _belt(g, p, top + 1):
        dt.button(F, 64, top + 5, 2.4, p.get("button", (176, 116, 60)))
    if shoes:
        c.sneakers(g, **shoes)
    return g


def cargo(p, brand, shoes=None, straps=False):
    base = p["base"]
    tex = c.tex_camo(p["camo"], seed=5) if p.get("camo") else c.tex_denim(base)
    hem = 128 - (SHOE_H if shoes else 0)
    g = c.pants(tex, top=96)
    ink = fx.tone(base, 0.5)
    waistband(g, tex, ink=ink)
    F = g.torso.faces["F"]
    d = ImageDraw.Draw(F)
    d.line([(64, 106), (64, 128)], fill=fx.rgba(ink))
    dt.stitch(d, [(69, 108), (69, 126)], fx.rgba(fx.tone(base, 0.7)), 2, 2)
    for side in (0, 1):
        pts = [(24, 106), (12, 127)]
        d.line(c.mirror_pts(pts) if side else pts, fill=fx.rgba(ink), width=2)
    for limb in g.limbs:
        out = limb.faces[c.OUTER[limb.name]]
        dt.pocket(out, (10, 42, 54, 78), base, stitch_color=fx.tone(base, 0.7), texture=tex(out.size, 6), flap=10,
                  button_color=p.get("snap", (40, 40, 40)))
        dd = ImageDraw.Draw(out)
        dd.line([(32, 50), (32, 78)], fill=fx.rgba(fx.tone(base, 0.6), 160))
        for f in ("F",):
            img = limb.faces[f]
            dd = ImageDraw.Draw(img)
            dd.line([(4, 60), (60, 60)], fill=fx.rgba(ink, 200))
            dt.stitch(dd, [(4, 63), (60, 63)], fx.rgba(fx.tone(base, 0.7)), 2, 2)
        F_ = limb.faces["F"]
        ox = 64 - inner_edge_x(limb.name, "F", 64)
        box = (3, 44, 29, 76) if ox == 0 else (35, 44, 61, 76)
        dt.pocket(F_, box, base, stitch_color=fx.tone(base, 0.7), texture=tex(F_.size, 9), flap=9,
                  button_color=p.get("snap", (40, 40, 40)))
        B = limb.faces["B"]
        dt.pocket(B, (14, 8, 50, 30), base, stitch_color=fx.tone(base, 0.7), texture=tex(B.size, 8), flap=7,
                  button_color=p.get("snap", (40, 40, 40)))
    side_seams(g, base, 0.6)
    cuff = p.get("cuff")
    if cuff:
        for limb in g.limbs:
            for img in c.sides(limb):
                dt.rib_band(img, hem - 10, hem, cuff, period=2)
    c.finish(g, 0.85, baggy=0.9 if cuff else 0.6, hem=hem - (10 if cuff else 0))
    if p.get("belt") and not isinstance(p["belt"], str):
        for f in g.torso.sides:
            img = g.torso.faces[f]
            lay = Image.new("RGBA", img.size)
            ImageDraw.Draw(lay).rectangle([0, 98, img.width, 104], fill=fx.rgba(p["belt"]))
            dt.place(img, lay, (0, 1, 0.6, 0.45))
        lay = Image.new("RGBA", F.size)
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([56, 96, 72, 106], radius=2, fill=fx.rgba((190, 192, 198)),
                             outline=fx.rgba((110, 110, 118)))
        ld.rectangle([60, 99, 68, 103], fill=fx.rgba((120, 120, 128)))
        dt.place(F, lay, (0, 1, 0.6, 0.5))
    elif not _belt(g, p, 98):
        dt.button(F, 64, 101, 2.2, (60, 60, 64))
    if straps:
        out = g.right.faces[c.OUTER["right"]]
        lay = Image.new("RGBA", out.size)
        ld = ImageDraw.Draw(lay)
        ld.rectangle([40, 0, 45, 50], fill=fx.rgba((20, 20, 22)))
        ld.rectangle([38, 30, 47, 37], outline=fx.rgba((190, 192, 198)), width=1)
        dt.place(out, lay, (1, 1, 0.8, 0.55))
        lb = g.left.faces["B"]
        lay = Image.new("RGBA", lb.size)
        ld = ImageDraw.Draw(lay)
        ld.line([(52, 0), (58, 26), (54, 44)], fill=fx.rgba((20, 20, 22)), width=4)
        dt.place(lb, lay, (1, 1, 0.8, 0.5))
    if shoes:
        c.sneakers(g, **shoes)
    return g


def joggers(p, brand, shoes=None):
    base = p["base"]
    tex = c.tex_fabric(base, p.get("grain", 0.022))
    hem = 128 - (SHOE_H if shoes else 0)
    g = c.pants(tex, top=94)
    for limb in g.limbs:
        for img in c.sides(limb):
            dt.rib_band(img, hem - 10, hem, fx.tone(base, 0.94))
        F = limb.faces["F"]
        ix = inner_edge_x(limb.name, "F", 64)
        ox = 64 - ix
        sgn = 1 if ox == 0 else -1
        d = ImageDraw.Draw(F)
        d.line([(ox, 24), (ox + sgn * 14, 0)], fill=fx.rgba(fx.tone(base, 0.6)), width=1)
        dt.stitch(d, [(ox + sgn * 2, 25), (ox + sgn * 16, 0)], fx.rgba(fx.tone(base, 0.8)), 2, 2)
    side_seams(g, base, 0.8)
    if p.get("print"):
        dt.text(g.left.faces["F"], brand, (30, 22), 7, p["print"], style="black", spacing=1)
    c.finish(g, 0.85, baggy=1.0, hem=hem - 10)
    drawstring_waist(g, fx.tone(base, 0.95), string=p.get("string", fx.tone(base, 1.4)))
    if shoes:
        c.sneakers(g, **shoes)
    return g


def wide_trousers(p, brand):
    """High-waisted wide-leg trousers with front pleats, a pressed crease, thin belt and loafers."""
    base = p["base"]
    tex = c.tex_smooth(base, 0.012, 0.05) if not p.get("linen") else c.tex_fabric(base, 0.02, 0.8)
    hem = 116
    g = c.pants(tex, top=94)
    ink = fx.tone(base, 0.55)
    F = g.torso.faces["F"]
    d = ImageDraw.Draw(F)
    d.line([(64, 102), (64, 128)], fill=fx.rgba(ink))
    for side in (0, 1):
        pts = [(28, 102), (16, 127)]
        d.line(c.mirror_pts(pts) if side else pts, fill=fx.rgba(ink), width=1)
    for limb in g.limbs:
        B = limb.faces["B"]
        ImageDraw.Draw(B).line([(16, 14), (48, 14)], fill=fx.rgba(ink), width=2)
        Fl = limb.faces["F"]
        dd = ImageDraw.Draw(Fl)
        for x in (24, 40):
            dd.line([(x, 0), (x + 1, 20)], fill=fx.rgba(ink, 170))
        for f in "FB":
            img = limb.faces[f]
            lay = Image.new("RGBA", img.size)
            ImageDraw.Draw(lay).line([(32, 0), (32, 128)], fill=(255, 255, 255, 70), width=2)
            over(img, fx.clip_to(lay.filter(ImageFilter.GaussianBlur(1)), img))
            ImageDraw.Draw(img).line([(33, 0), (33, 128)], fill=fx.rgba(ink, 90))
    side_seams(g, base, 0.6)
    c.flare(g, 50, hem, 0.7)
    c.finish(g, 0.75, baggy=0.4, hem=hem, folds=0.8)
    c.belt(g, 96, 5, p.get("belt", (60, 38, 28)), "square", p.get("buckle", (222, 194, 120)))
    c.loafers(g, p.get("shoes", (40, 26, 20)))
    return g


def pleated_skirt(p, brand):
    """Pleated mini skirt (plaid or solid) with legwear and shoes chosen by the colourway."""
    tex = c.tex_plaid(p["sett"]) if p.get("sett") else c.tex_fabric(p["base"], 0.01)
    length = p.get("length", 46)
    g = c.pants(tex, top=100, hem=length)
    period = p.get("pleat", 8)

    def pleats(img, y0, y1):
        w, h = img.size
        x = np.arange(w)
        t = (x % period) / period
        val = np.clip(128 + 46 * (t - 0.5) * 2 - 70 * (t > 0.88), 0, 255).astype(np.uint8)
        m = np.broadcast_to(val[None, :], (h, w)).copy()
        m[:y0] = 128
        m[y1:] = 128
        return Image.fromarray(m, "L")

    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            img.paste(fx.apply_shade(img, pleats(img, 0, length), 1.0), (0, 0))
    for f in g.torso.sides:
        img = g.torso.faces[f]
        img.paste(fx.apply_shade(img, pleats(img, 110, 128), 0.7), (0, 0))
    if p.get("hem_stripes"):
        for limb in g.limbs:
            for img in c.sides(limb):
                d = ImageDraw.Draw(img)
                for (y0, y1), col in zip(((length - 9, length - 6), (length - 4, length - 3)), p["hem_stripes"]):
                    d.rectangle([0, y0, img.width, y1], fill=fx.rgba(col))
    c.finish(g, 0.6, hem=length, folds=0.5)
    default_band = fx.tone(p["sett"][0][0], 0.7) if p.get("sett") else fx.tone(p["base"], 0.95)
    band = p.get("band", default_band)
    for img in c.sides(g.torso):
        lay = Image.new("RGBA", img.size)
        ImageDraw.Draw(lay).rectangle([0, 100, img.width, 109], fill=fx.rgba(band))
        dt.place(img, lay, (0, 1, 1.0, 0.5))
    if p.get("button", True):
        dt.button(g.torso.faces["F"], 96, 104, 2.0, p.get("button_color", (230, 210, 140)), holes=False)
    for limb in g.limbs:
        for img in c.sides(limb):
            ImageDraw.Draw(img).line([(0, length - 1), (img.width, length - 1)], fill=fx.rgba((0, 0, 0), 90))
    legs_and_shoes(g, p, length)
    return g


def ruffle_skirt(p, brand):
    """Tiered ruffle mini skirt with a little bow at the waist."""
    base = p["base"]
    tex = c.fabric_tex(p)
    g = c.pants(tex, top=100, hem=24)
    c.finish(g, 0.6, hem=24, folds=0.4)
    for img in c.sides(g.torso):
        dt.rib_band(img, 100, 106, fx.tone(base, 0.95), period=2)
    for limb in g.limbs:
        for img in c.sides(limb):
            dt.ruffle(img, 20, 44, tex(img.size, 3), base, wave=10, amp=1.8)
            if p.get("lace"):
                dt.lace_band(img, 42, 49, p["lace"], scallop=6)
    dt.bow(g.torso.faces["F"], 94, 105, 12, p.get("bow", fx.tone(base, 0.85)), tails=0.9)
    legs_and_shoes(g, p, 46)
    return g


def denim_skirt(p, brand):
    """Denim mini skirt with a frayed hem, worn with tall boots."""
    denim_c = p["denim"]
    thread = p.get("thread", (214, 150, 70))
    tex = c.tex_denim(denim_c)
    length = 42
    g = c.pants(tex, top=98, hem=length)
    ink = fx.tone(denim_c, 0.5)
    for limb in g.limbs:
        c.fade(limb.faces["F"], [(8, 0, 56, 40)], p.get("wash", 0.25), 9)
        B = limb.faces["B"]
        pk = [(16, 4), (48, 4), (48, 22), (32, 27), (16, 22)]
        lay = dt.textured_polygon(B.size, pk, tex(B.size, 4))
        ld = ImageDraw.Draw(lay)
        ld.line(pk + [pk[0]], fill=fx.rgba(ink))
        dt.stitch(ld, [(18, 6), (18, 21), (32, 25), (46, 21), (46, 6)], fx.rgba(thread), 2, 2)
        dt.place(B, lay, (0, 1, 0.8, 0.45))
        for img in c.sides(limb):
            d = ImageDraw.Draw(img)
            dt.stitch(d, [(0, length - 5), (img.width, length - 5)], fx.rgba(thread), 2, 2)
            rnd = random.Random(f"{limb.name}{img.width}")
            for x in range(0, img.width, 2):
                d.line([(x, length - 1), (x + rnd.uniform(-0.5, 0.5), length + rnd.uniform(0.5, 3))],
                       fill=fx.rgba(fx.tone(denim_c, 1.7), 220))
    side_seams(g, denim_c, 0.55)
    waistband(g, tex, y0=98, ink=ink, thread=thread)
    F = g.torso.faces["F"]
    d = ImageDraw.Draw(F)
    d.line([(64, 108), (64, 128)], fill=fx.rgba(ink))
    dt.stitch(d, [(70, 110), (70, 124), (64, 127)], fx.rgba(thread), 2, 2)
    for side in (0, 1):
        pts = [(26, 108), (18, 114), (12, 127)]
        pts = c.mirror_pts(pts) if side else pts
        d.line(pts, fill=fx.rgba(ink), width=1)
        dt.stitch(d, [(x + (2 if side else -2), y) for x, y in pts], fx.rgba(thread), 2, 2)
    c.finish(g, 0.8, hem=length, folds=0.6, fit="fitted")
    if not _belt(g, p, 99):
        dt.button(F, 64, 103, 2.4, p.get("button", (176, 116, 60)))
    legs_and_shoes(g, p, length)
    return g


def flare_leggings(p, brand):
    """Stretchy flare leggings with a crossover waistband and chunky sneakers."""
    base = p["base"]
    tex = c.tex_smooth(base, 0.008, 0.05)
    hem = 114
    g = c.pants(tex, top=92, hem=hem)
    band = c.tex_smooth(fx.tone(base, 1.08), 0.008, 0.05)
    for f in g.torso.sides:
        img = g.torso.faces[f]
        if f == "F":
            for pts in ([(0, 92), (76, 92), (64, 112), (0, 102)], [(128, 92), (52, 92), (64, 112), (128, 102)]):
                lay = dt.textured_polygon(img.size, pts, band(img.size))
                ImageDraw.Draw(lay).line(pts[1:3], fill=fx.rgba(fx.tone(base, 0.6)), width=1)
                dt.place(img, lay, (0, 1, 1.0, 0.45))
        else:
            over(img, band((img.width, 10)), (0, 92))
            ImageDraw.Draw(img).line([(0, 102), (img.width, 102)], fill=fx.rgba(fx.tone(base, 0.6)))
    c.flare(g, 72, hem, 1.2)
    c.finish(g, 0.85, baggy=0.2, hem=hem, fit="fitted")
    for limb in g.limbs:
        c.sheen(limb.faces["F"], 24, 32, 0.12, 3)
        c.sheen(limb.faces[c.OUTER[limb.name]], 30, 36, 0.08, 3)
    c.chunky_sneakers(g, **p.get("sneakers", {}))
    return g


def sundress_skirt(p, brand):
    """The flowy skirt half of a sundress: soft drapes and a frilled hem."""
    base = p["base"]
    tex = c.fabric_tex(p)
    length = p.get("length", 70)
    g = c.pants(tex, top=96, hem=length)
    for img in c.sides(g.torso):
        c.drape(img, 96, 128, 14, 0.4, seed=img.width)
    for limb in g.limbs:
        for img in c.sides(limb):
            c.drape(img, 0, length, 14, 0.45, seed=img.width + 3)
    c.finish(g, 0.6, hem=length, folds=0.35)
    for limb in g.limbs:
        for img in c.sides(limb):
            dt.ruffle(img, length - 6, length, tex(img.size, 9), base, wave=6, amp=1.4)
    legs_and_shoes(g, p, length)
    return g


def scrubs_pants(p, brand):
    base = p["base"]
    tex = c.tex_fabric(base, 0.012)
    hem = 128 - SHOE_H
    g = c.pants(tex, top=96)
    out = g.right.faces[c.OUTER["right"]]
    dt.pocket(out, (12, 46, 52, 74), base, stitch_color=fx.tone(base, 0.7), texture=tex(out.size, 3))
    side_seams(g, base, 0.75)
    c.finish(g, 0.65, baggy=0.4, hem=hem)
    drawstring_waist(g, fx.tone(base, 0.95), 96, 10, string=fx.tone(base, 0.8))
    c.sneakers(g, **p.get("shoes", {}))
    return g


def pajama_pants(p, brand):
    tex = c.tex_plaid(p["sett"]) if p.get("sett") else c.fabric_tex(p)
    g = c.pants(tex, top=96)
    for limb in g.limbs:
        for img in c.sides(limb):
            d = ImageDraw.Draw(img)
            d.line([(0, 120), (img.width, 120)], fill=fx.rgba((0, 0, 0), 90))
    c.finish(g, 0.8, baggy=0.9)
    band = fx.tone(p["sett"][0][0], 0.8) if p.get("sett") else fx.tone(p["base"], 0.9)
    drawstring_waist(g, p.get("band", band), 96, 12, string=(245, 245, 240))
    return g


# ================================================================= more women's bottoms

def gown_skirt(p, brand):
    """Floor-length gown skirt: flowing satin drapes that cover the feet."""
    base = p["base"]
    tex = c.tex_satin(base, 0.3)
    g = c.pants(tex, top=96, hem=128)
    for img in c.sides(g.torso):
        c.drape(img, 96, 128, 16, 0.32, seed=img.width + 1)
    for limb in g.limbs:
        for img in c.sides(limb):
            c.drape(img, 0, 128, 16, 0.4, seed=img.width + 5)
    c.flare(g, 40, 128, 0.6)
    c.finish(g, 0.6, hem=128, folds=0.3)
    for limb in g.limbs:
        for img in c.sides(limb):
            c.sheen(img, 20, 28, 0.1, 4)
            d = ImageDraw.Draw(img)
            d.line([(0, 124), (img.width, 124)], fill=fx.rgba(fx.tone(base, 0.7), 150))
            if p.get("sparkle"):
                c.glitter(img, 0.05, p["sparkle"], seed=img.width + 2)
            if p.get("lace"):
                dt.lace_band(img, 116, 124, p["lace"], scallop=6)
    return g


def pj_pants(p, brand):
    """Satin pajama pants with contrast piping and fluffy slippers."""
    base, piping = p["base"], p["piping"]
    tex = c.tex_satin(base, 0.25)
    g = c.pants(tex, top=96)
    for limb in g.limbs:
        out = limb.faces[c.OUTER[limb.name]]
        ImageDraw.Draw(out).line([(32, 0), (32, 128)], fill=fx.rgba(piping), width=1)
        for img in c.sides(limb):
            ImageDraw.Draw(img).line([(0, 110), (img.width, 110)], fill=fx.rgba(piping), width=1)
    c.finish(g, 0.8, baggy=0.7, hem=114)
    drawstring_waist(g, fx.tone(base, 0.95), 96, 10, string=piping)
    c.slippers(g, p.get("slippers", (252, 252, 252)))
    return g


def overall_shorts(p, brand):
    """Denim shorts half of the overall set: rolled cuffs, crew socks and sneakers."""
    denim_c, thread = p["denim"], p.get("thread", (214, 150, 70))
    tex = c.tex_denim(denim_c)
    length = 40
    g = c.pants(tex, top=96, hem=length)
    for limb in g.limbs:
        c.fade(limb.faces["F"], [(8, 0, 56, 36)], 0.22, 8)
        for img in c.sides(limb):
            over(img, c.tex_denim(fx.tone(denim_c, 1.12))((img.width, 7), 3), (0, length - 7))
            d = ImageDraw.Draw(img)
            d.line([(0, length - 7), (img.width, length - 7)], fill=fx.rgba(fx.tone(denim_c, 0.5)))
            dt.stitch(d, [(0, length - 3), (img.width, length - 3)], fx.rgba(thread), 2, 2)
    side_seams(g, denim_c, 0.55)
    c.finish(g, 0.75, hem=length, folds=0.6)
    legs_and_shoes(g, p, length)
    return g


def biker_shorts(p, brand):
    """Fitted high-waisted biker shorts with crew socks and chunky sneakers."""
    base = p["base"]
    tex = c.tex_smooth(base, 0.008, 0.05)
    length = 50
    g = c.pants(tex, top=92, hem=length)
    for img in c.sides(g.torso):
        over(img, c.tex_smooth(fx.tone(base, 1.06))((img.width, 10)), (0, 92))
        ImageDraw.Draw(img).line([(0, 102), (img.width, 102)], fill=fx.rgba(fx.tone(base, 0.6)))
    for limb in g.limbs:
        for img in c.sides(limb):
            ImageDraw.Draw(img).line([(0, length - 3), (img.width, length - 3)], fill=fx.rgba(fx.tone(base, 0.6)))
    c.finish(g, 0.85, hem=length, fit="fitted")
    for limb in g.limbs:
        c.sheen(limb.faces["F"], 24, 32, 0.14, 3)
    legs_and_shoes(g, p, length)
    return g


def tulle_skirt(p, brand):
    """Layered sheer tulle ballet skirt with a satin ribbon waist and bow."""
    base = p["base"]
    tulle = c.tex_tulle(base, p.get("opacity", 0.5))
    length = 56
    g = Garment("pants")
    g.top, g.hem = 100, length
    if p.get("tights"):
        c.tights(g, p["tights"], p.get("tights_opacity", 0.8))
    c.fill(g.torso, tulle, 100, 128, caps="D")
    for limb in g.limbs:
        c.fill(limb, tulle, 0, length, caps="U")
        c.fill(limb, tulle, 0, length - 10, caps="")
    for limb in g.limbs:
        for img in c.sides(limb):
            xs = np.arange(img.width)
            hem = (length - 1 + 1.5 * np.sin(xs / 3.0)).astype(int)
            a = np.asarray(img.getchannel("A")).copy()
            for x in xs:
                a[hem[x]:length, x] = 0
            img.putalpha(Image.fromarray(a))
    for img in c.sides(g.torso):
        lay = c.tex_satin(p.get("ribbon", base), 0.3)(img.size)
        lay.putalpha(c.mask_from(img.size, lambda d: d.rectangle([0, 100, img.width, 106], fill=255)))
        dt.place(img, lay, (0, 1, 0.8, 0.45))
    dt.bow(g.torso.faces["F"], 64, 103, 14, p.get("ribbon", base), tails=1.2)
    legs_and_shoes(g, p, length)
    return g


def cargo_skirt(p, brand):
    """Y2K cargo mini skirt with flap pockets and a belt."""
    base = p["base"]
    tex = c.tex_denim(base)
    length = 40
    g = c.pants(tex, top=98, hem=length)
    ink = fx.tone(base, 0.5)
    waistband(g, tex, y0=98, ink=ink)
    for limb in g.limbs:
        F = limb.faces["F"]
        ox = 64 - inner_edge_x(limb.name, "F", 64)
        box = (4, 6, 30, 30) if ox == 0 else (34, 6, 60, 30)
        dt.pocket(F, box, base, stitch_color=fx.tone(base, 0.7), texture=tex(F.size, 9), flap=8,
                  button_color=p.get("snap", (40, 40, 40)))
        out = limb.faces[c.OUTER[limb.name]]
        dt.pocket(out, (12, 6, 52, 32), base, stitch_color=fx.tone(base, 0.7), texture=tex(out.size, 6), flap=8,
                  button_color=p.get("snap", (40, 40, 40)))
        for img in c.sides(limb):
            dt.stitch(ImageDraw.Draw(img), [(0, length - 4), (img.width, length - 4)], fx.rgba(fx.tone(base, 0.7)),
                      2, 2)
    side_seams(g, base, 0.6)
    c.finish(g, 0.8, hem=length, folds=0.6, fit="fitted")
    if not _belt(g, p, 99):
        dt.button(g.torso.faces["F"], 64, 103, 2.2, (60, 60, 64))
    legs_and_shoes(g, p, length)
    return g


def mini_skirt(p, brand):
    """Bodycon mini skirt in a statement fabric (leopard, cow print, satin...)."""
    base = p["base"]
    tex = c.fabric_tex(p)
    length = 38
    g = c.pants(tex, top=100, hem=length)
    for img in c.sides(g.torso):
        over(img, c.tex_smooth(p.get("band", fx.tone(base, 0.85)))((img.width, 5)), (0, 100))
    for limb in g.limbs:
        for img in c.sides(limb):
            ImageDraw.Draw(img).line([(0, length - 1), (img.width, length - 1)], fill=fx.rgba((0, 0, 0), 90))
    c.finish(g, 0.8, hem=length, folds=0.5, fit="fitted")
    if p.get("fabric") == "satin":
        for limb in g.limbs:
            c.sheen(limb.faces["F"], 22, 30, 0.12, 3)
    _belt(g, p, 100)
    legs_and_shoes(g, p, length)
    return g
