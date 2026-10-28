"""Pants designs. Each function takes a colourway dict and the brand name and
returns a finished Garment."""

import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .. import details as dt
from .. import fx
from ..garment import over
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


def jeans(p, brand, baggy=0.8, rips=False, shoes=None):
    denim_c = p["denim"]
    thread = p.get("thread", (214, 150, 70))
    tex = c.tex_denim(denim_c)
    hem = 128 - (SHOE_H if shoes else 0)
    g = c.pants(tex, top=96)
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
        # back pockets with a stitched arc
        B = limb.faces["B"]
        pk = [(14, 8), (50, 8), (50, 32), (32, 38), (14, 32)]
        lay = dt.textured_polygon(B.size, pk, tex(B.size, 4))
        ld = ImageDraw.Draw(lay)
        ld.line(pk + [pk[0]], fill=fx.rgba(ink))
        dt.stitch(ld, [(16, 10), (16, 31), (32, 36), (48, 31), (48, 10)], fx.rgba(thread), 2, 2)
        dt.stitch(ld, [(18, 22), (32, 16), (46, 22)], fx.rgba(thread), 2, 2)
        dt.place(B, lay, (0, 1, 0.8, 0.45))
        dd = ImageDraw.Draw(B)
        dd.line([(0, 0), (64, 0)], fill=fx.rgba(ink))
    side_seams(g, denim_c, 0.55)
    waistband(g, tex, ink=ink, thread=thread)
    d = ImageDraw.Draw(F)
    dt.stitch(d, [(70, 108), (70, 122), (64, 127)], fx.rgba(thread), 2, 2)
    d.line([(64, 106), (64, 128)], fill=fx.rgba(ink))
    for side in (0, 1):
        pts = [(26, 106), (18, 112), (12, 127)]
        pts = c.mirror_pts(pts) if side else pts
        d.line(pts, fill=fx.rgba(ink), width=1)
        dt.stitch(d, [(x + (2 if side else -2), y) for x, y in pts], fx.rgba(thread), 2, 2)
    dt.stitch(d, [(92, 108), (102, 108), (102, 116)], fx.rgba(thread), 2, 1)
    if rips:
        for limb in g.limbs:
            rip(limb.faces["F"], (16, 60, 46, 70), seed=limb.name)
            rip(limb.faces["F"], (24, 26, 36, 30), seed=limb.name + "t")
    for limb in g.limbs:
        for f in limb.sides:
            dt.stitch(ImageDraw.Draw(limb.faces[f]), [(0, hem - 4), (64, hem - 4)], fx.rgba(thread), 2, 2)
    c.finish(g, 0.85, baggy=baggy, hem=hem)
    dt.button(F, 64, 101, 2.4, p.get("button", (176, 116, 60)))
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
    if p.get("belt"):
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
    else:
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


def track_pants(p, brand, shoes=None):
    base, stripe = p["base"], p["stripe"]
    tex = c.tex_smooth(base, 0.01, 0.04)
    hem = 128 - (SHOE_H if shoes else 0)
    g = c.pants(tex, top=94)
    # two stripes wrapping the corner where the front meets the outer side, from hip to ankle
    def stripes_at(part, seams, y0, y1):
        lay = Image.new("RGBA", (part.strip_width, 128))
        d = ImageDraw.Draw(lay)
        for s in seams:
            for x in (s - 6, s + 1):
                d.rectangle([x, y0, x + 3, y1 - 1], fill=fx.rgba(stripe))
        part.over_strip(lay)

    stripes_at(g.torso, (g.torso.offset("F"), g.torso.offset("L")), 104, 128)
    stripes_at(g.right, (g.right.offset("F"),), 0, hem)
    stripes_at(g.left, (g.left.offset("L"),), 0, hem)
    c.finish(g, 0.75, baggy=0.5, hem=hem)
    for limb in g.limbs:
        out = limb.faces[c.OUTER[limb.name]]
        c.sheen(out, 6, 14, 0.12, 3)
        dt.zipper(out, 32, hem - 22, hem - 1, base, pull_y=hem - 20)
    drawstring_waist(g, fx.tone(base, 0.9), 94, 10, string=stripe)
    if shoes:
        c.sneakers(g, **shoes)
    return g


def suit_trousers(p, brand):
    base = p["base"]
    tex = c.tex_smooth(base, 0.012, 0.04)
    hem = 116
    g = c.pants(tex, top=96)
    ink = fx.tone(base, 0.5)
    F = g.torso.faces["F"]
    d = ImageDraw.Draw(F)
    d.line([(64, 104), (64, 128)], fill=fx.rgba(ink))
    for side in (0, 1):
        pts = [(26, 104), (16, 127)]
        d.line(c.mirror_pts(pts) if side else pts, fill=fx.rgba(ink), width=1)
    for limb in g.limbs:
        B = limb.faces["B"]
        dd = ImageDraw.Draw(B)
        dd.line([(16, 14), (48, 14)], fill=fx.rgba(ink), width=2)
        for f in "FB":
            img = limb.faces[f]
            lay = Image.new("RGBA", img.size)
            ImageDraw.Draw(lay).line([(32, 0), (32, 128)], fill=(255, 255, 255, 60), width=2)
            over(img, fx.clip_to(lay.filter(ImageFilter.GaussianBlur(1)), img))
            ImageDraw.Draw(img).line([(33, 0), (33, 128)], fill=fx.rgba(ink, 90))
    side_seams(g, base, 0.6)
    c.finish(g, 0.7, baggy=0.3, hem=hem, folds=0.8)
    belt = p.get("belt", (28, 22, 20))
    for f in g.torso.sides:
        img = g.torso.faces[f]
        lay = Image.new("RGBA", img.size)
        ld = ImageDraw.Draw(lay)
        ld.rectangle([0, 96, img.width, 103], fill=fx.rgba(belt))
        ld.line([(0, 97), (img.width, 97)], fill=fx.rgba(fx.tone(belt, 1.5), 120))
        dt.place(img, lay, (0, 1, 0.6, 0.5))
    lay = Image.new("RGBA", F.size)
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([58, 95, 70, 104], radius=1, outline=fx.rgba(p.get("buckle", (210, 190, 130))), width=2)
    dt.place(F, lay, (0, 1, 0.6, 0.5))
    c.dress_shoes(g, p.get("shoes", (24, 20, 20)), 128 - hem)
    return g


def pleated_skirt(p, brand):
    tex = c.tex_plaid(p["sett"])
    length = 46
    g = c.pants(tex, top=100, hem=length)
    period = 8

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
    c.finish(g, 0.6, hem=length, folds=0.5)
    band = p.get("band", fx.tone(p["sett"][0][0], 0.7))
    for img in c.sides(g.torso):
        lay = Image.new("RGBA", img.size)
        ImageDraw.Draw(lay).rectangle([0, 100, img.width, 109], fill=fx.rgba(band))
        dt.place(img, lay, (0, 1, 1.0, 0.5))
    dt.button(g.torso.faces["F"], 96, 104, 2.0, p.get("button", (230, 210, 140)), holes=False)
    for limb in g.limbs:
        for img in c.sides(limb):
            ImageDraw.Draw(img).line([(0, length - 1), (img.width, length - 1)], fill=fx.rgba((0, 0, 0), 90))
    c.socks(g, p.get("socks", (250, 250, 250)), 76, 114, stripe=p.get("sock_stripe"))
    shoe = p.get("shoes", (24, 22, 26))
    c.dress_shoes(g, shoe, 14)
    for limb in g.limbs:
        d = ImageDraw.Draw(limb.faces["F"])
        d.line([(16, 116), (48, 116)], fill=fx.rgba(fx.tone(shoe, 0.4)), width=2)
        dt.button(limb.faces["F"], 46, 116, 1.4, (200, 200, 205), holes=False)
    return g


def basketball_shorts(p, brand):
    base, panel = p["base"], p["panel"]
    tex = c.tex_mesh(base)
    length = 58
    g = c.pants(tex, top=94, hem=length)
    for limb in g.limbs:
        out = limb.faces[c.OUTER[limb.name]]
        lay = c.tex_mesh(panel)(out.size)
        lay.putalpha(c.mask_from(out.size, lambda d: d.rectangle([18, 0, 46, length], fill=255)))
        over(out, lay)
        for img in c.sides(limb):
            d = ImageDraw.Draw(img)
            d.rectangle([0, length - 6, img.width, length], fill=fx.rgba(panel))
    dt.text(g.left.faces["F"], brand, (30, 40), 7, p.get("print", panel), style="black", spacing=1)
    c.finish(g, 0.65, hem=length)
    drawstring_waist(g, fx.tone(base, 0.9), 94, 12, string=p.get("string", (245, 245, 245)))
    c.socks(g, (250, 250, 250), 86, 112, stripe=panel)
    c.sneakers(g, **p.get("shoes", {}))
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
    tex = c.tex_plaid(p["sett"])
    g = c.pants(tex, top=96)
    for limb in g.limbs:
        for img in c.sides(limb):
            d = ImageDraw.Draw(img)
            d.line([(0, 120), (img.width, 120)], fill=fx.rgba((0, 0, 0), 90))
    c.finish(g, 0.8, baggy=0.9)
    drawstring_waist(g, p.get("band", fx.tone(p["sett"][0][0], 0.8)), 96, 12, string=(245, 245, 240))
    return g
