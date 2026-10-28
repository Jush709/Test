"""Shirt designs. Each function takes a colourway dict and the brand name and
returns a finished Garment."""

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .. import details as dt
from .. import fx
from ..garment import over
from . import common as c
from .graphics import GRAPHICS


def hoodie(p, brand, crop=False, zip_up=False):
    base = p["base"]
    rib = p.get("rib", fx.tone(base, 0.93))
    tex = c.tex_fabric(base, p.get("grain", 0.022))
    g = c.shirt(tex, "long", length=86 if crop else 128)
    F, B = g.torso.faces["F"], g.torso.faces["B"]
    c.hem_band(g, rib, 8 if crop else 10)
    c.cuffs(g, rib, 9)

    if zip_up:
        for side in (0, 1):
            pts = [(20, 82), (30, 108)]
            pts = c.mirror_pts(pts) if side else pts
            d = ImageDraw.Draw(F)
            d.line(pts, fill=fx.rgba(fx.tone(base, 0.55)), width=2)
            dt.stitch(d, [(x + (2 if not side else -2), y) for x, y in pts], fx.rgba(fx.tone(base, 0.8)))
    elif not crop:
        pk = [(34, 72), (94, 72), (104, 96), (104, 118), (24, 118), (24, 96)]
        lay = dt.textured_polygon(F.size, pk, tex(F.size, 9))
        d = ImageDraw.Draw(lay)
        d.line([pk[0], pk[1]], fill=fx.rgba(fx.tone(base, 0.75)), width=1)
        dt.stitch(d, [(35, 75), (93, 75)], fx.rgba(fx.tone(base, 0.78)))
        for a, b in ((pk[1], pk[2]), (pk[0], pk[5])):
            d.line([a, b], fill=fx.rgba(fx.tone(base, 0.4)), width=2)
            d.line([(a[0] + (1 if a[0] < 64 else -1), a[1] + 1), (b[0] + (1 if b[0] < 64 else -1), b[1])],
                   fill=fx.rgba(fx.tone(base, 1.25), 150), width=1)
        dt.place(F, lay, (0, 1, 1.2, 0.35))

    if p.get("print") and zip_up:
        dt.text(F, brand, (101, 48), 7, p["print"], style="black", spacing=1)
    elif p.get("print"):
        dt.text(F, brand, (64, 62 if not crop else 60), 12, p["print"], style="black", spacing=1)
    if p.get("back_print"):
        dt.text(B, brand, (64, 66), 18, p["back_print"], style="black", spacing=2)
        dt.text(B, p.get("back_sub", "WORLDWIDE"), (64, 80), 7, p["back_print"], style="bold", spacing=2)

    c.hood(g, tex, base)
    c.finish(g, p.get("shade", 0.85))
    if zip_up:
        dt.zipper(F, 64, 14, g.length, base, pull_y=18)
    dt.drawstrings(F, (52, 76), 19, 24 if crop else 28, p.get("string", fx.tone(base, 1.3)),
                   tip=p.get("tip", (210, 210, 214)))
    return g


def varsity(p, brand):
    body, sleeve, rib, stripe = p["body"], p["sleeve"], p["rib"], p["stripe"]
    wool = c.tex_fabric(body, 0.02)
    leather = c.tex_smooth(sleeve, 0.01, 0.06)
    g = c.shirt(wool, "long", sleeve_tex=leather)
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]

    def striped_rib(img, y0, y1):
        dt.rib_band(img, y0, y1, rib)
        d = ImageDraw.Draw(img)
        h = y1 - y0
        for yy in (y0 + h * 0.3, y0 + h * 0.62):
            d.rectangle([0, int(yy), img.width, int(yy) + 1], fill=fx.rgba(stripe))

    for img in c.sides(T):
        striped_rib(img, 116, 128)
    for limb in g.limbs:
        for img in c.sides(limb):
            striped_rib(img, 96, 108)

    # ribbed V collar
    collar = [(42, 0), (86, 0), (64, 30)]
    lay = dt.polygon_layer(F.size, [(34, 0), (94, 0), (64, 38)], rib)
    d = ImageDraw.Draw(lay)
    d.line([(38, 0), (64, 34), (90, 0)], fill=fx.rgba(stripe), width=2)
    dt.place(F, lay, (0, 1, 1.2, 0.5))
    fx.cut(F, c.mask_from(F.size, lambda dd: dd.polygon(collar, fill=255)))
    blay = Image.new("RGBA", B.size)
    ImageDraw.Draw(blay).rectangle([30, 0, 98, 7], fill=fx.rgba(rib))
    ImageDraw.Draw(blay).line([(30, 4), (98, 4)], fill=fx.rgba(stripe), width=1)
    dt.place(B, blay)

    # leather welt pockets
    for pts in ([(14, 76), (22, 74), (28, 100), (20, 102)],):
        for poly in (pts, c.mirror_pts(pts)):
            dt.place(F, dt.polygon_layer(F.size, poly, sleeve, fx.tone(sleeve, 0.7)), (0, 1, 1, 0.4))

    d = ImageDraw.Draw(F)
    d.line([(64, 36), (64, 116)], fill=fx.rgba(fx.tone(body, 0.6)), width=1)
    # chenille letter patch on the wearer's left chest
    dt.text(F, brand[0], (94, 54), 30, stripe, style="black", stroke=3, stroke_color=p.get("letter_edge", sleeve),
            shadow=(0, 2, 1.2, 0.55))
    dt.arc_text(B, brand, 64, 104, 54, 16, stripe, stroke=2, stroke_color=p.get("letter_edge", sleeve), spread=12)
    dt.text(B, p.get("back_number", "26"), (64, 80), 26, stripe, style="black", stroke=2,
            stroke_color=p.get("letter_edge", sleeve), shadow=(0, 2, 1.2, 0.55))
    c.finish(g, 0.8)
    for limb in g.limbs:
        for f in ("F", c.OUTER[limb.name]):
            c.sheen(limb.faces[f], 18, 28, 0.22)
    for y in range(44, 112, 14):
        dt.button(F, 64, y, 2.2, p.get("snap", stripe), holes=False)
    return g


def flannel_open(p, brand):
    tex = c.tex_plaid(p["sett"])
    tee = p.get("tee", (242, 242, 240))
    g = c.shirt(tex, "long")
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]
    # open front showing a tee
    panel = c.tex_fabric(tee, 0.015)(F.size)
    panel.putalpha(c.mask_from(F.size, lambda d: d.polygon([(44, 0), (84, 0), (88, 128), (40, 128)], fill=255)))
    over(F, panel)
    neck = c.mask_from(F.size, lambda d: d.ellipse([48, -9, 80, 9], fill=255))
    trim = Image.new("RGBA", F.size, fx.rgba(fx.tone(tee, 0.9)))
    trim.putalpha(c.mask_from(F.size, lambda d: d.ellipse([45, -12, 83, 12], fill=255)))
    over(F, trim)
    fx.cut(F, neck)
    if p.get("tee_print"):
        dt.paste_graphic(F, GRAPHICS[p["tee_print"]](), (64, 60), 34)
    # flannel front edges + placket, casting a shadow on the tee
    for side in (0, 1):
        edge = [(0, 0), (44, 0), (40, 128), (0, 128)] if not side else [(84, 0), (128, 0), (128, 128), (88, 128)]
        lay = dt.textured_polygon(F.size, edge, tex(F.size, 0))
        d = ImageDraw.Draw(lay)
        x_top, x_bot = (44, 40) if not side else (84, 88)
        d.line([(x_top, 0), (x_bot, 128)], fill=fx.rgba((30, 30, 30), 150), width=1)
        dt.stitch(d, [(x_top + (-5 if not side else 5), 6), (x_bot + (-5 if not side else 5), 128)],
                  fx.rgba((240, 240, 240), 120))
        dt.place(F, lay, ((2 if not side else -2), 0, 2.0, 0.5))
    # collar points lying open
    for side in (0, 1):
        pts = [(26, 0), (46, 0), (44, 20), (36, 12)]
        pts = c.mirror_pts(pts) if side else pts
        lay = dt.textured_polygon(F.size, pts, tex(F.size, 0))
        ImageDraw.Draw(lay).line(pts + [pts[0]], fill=fx.rgba((20, 20, 20), 120))
        dt.place(F, lay, (0, 2, 1.2, 0.5))
    for box in ((12, 30, 34, 52), (94, 30, 116, 52)):
        dt.pocket(F, box, p["sett"][0][0], texture=tex(F.size, 3), flap=7,
                  button_color=p.get("button", (235, 232, 225)))
    # back yoke and collar
    d = ImageDraw.Draw(B)
    d.line([(0, 22), (128, 22)], fill=fx.rgba((20, 20, 20), 120))
    dt.stitch(d, [(0, 24), (128, 24)], fx.rgba((240, 240, 240), 100))
    lay = dt.textured_polygon(B.size, [(30, 0), (98, 0), (96, 7), (32, 7)], tex(B.size, 4))
    dt.place(B, lay, (0, 1, 1.0, 0.5))
    # cuffs with a button on the outer side
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            d = ImageDraw.Draw(img)
            d.line([(0, 98), (64, 98)], fill=fx.rgba((20, 20, 20), 140))
            dt.stitch(d, [(0, 100), (64, 100)], fx.rgba((240, 240, 240), 100))
    c.finish(g, 0.75)
    for limb in g.limbs:
        dt.button(limb.faces[c.OUTER[limb.name]], 32, 103, 1.8, p.get("button", (235, 232, 225)), holes=False)
    for y in range(14, 124, 18):
        dt.button(F, 36, y, 1.8, p.get("button", (235, 232, 225)), holes=False)
    return g


def suit(p, brand, neckwear="bow", crest=False):
    jacket, shirt_c = p["jacket"], p.get("shirt", (246, 246, 244))
    lapel_c = p.get("lapel", fx.tone(jacket, 1.1 if sum(fx.rgb(jacket)) < 400 else 0.94))
    tex = c.tex_smooth(jacket, 0.012, 0.04)
    g = c.shirt(tex, 100)
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]
    shirt_tex = c.tex_fabric(shirt_c, 0.01)
    # shirt V and neckwear
    vee = [(40, 0), (88, 0), (64, 72)]
    lay = dt.textured_polygon(F.size, vee, shirt_tex(F.size))
    d = ImageDraw.Draw(lay)
    if neckwear == "bow":
        for y in (24, 34, 44, 54):
            dt.button(lay, 64, y, 1.4, (40, 40, 44), holes=False)
        d.line([(60, 14), (58, 66)], fill=fx.rgba(fx.tone(shirt_c, 0.85)))
        d.line([(68, 14), (70, 66)], fill=fx.rgba(fx.tone(shirt_c, 0.85)))
    for side in (0, 1):
        pts = [(50, 0), (64, 6), (58, 14)]
        d.polygon(c.mirror_pts(pts) if side else pts, fill=fx.rgba(fx.tone(shirt_c, 0.92)),
                  outline=fx.rgba(fx.tone(shirt_c, 0.75)))
    over(F, lay)
    nw = p.get("neckwear", (20, 20, 22))
    if neckwear == "bow":
        bow = Image.new("RGBA", F.size)
        bd = ImageDraw.Draw(bow)
        bd.polygon([(50, 6), (64, 11), (50, 17)], fill=fx.rgba(nw))
        bd.polygon([(78, 6), (64, 11), (78, 17)], fill=fx.rgba(nw))
        bd.rounded_rectangle([61, 7, 67, 15], radius=2, fill=fx.rgba(fx.tone(nw, 1.15)))
        dt.place(F, bow, (0, 1, 0.8, 0.5))
    else:
        tie = Image.new("RGBA", F.size)
        td = ImageDraw.Draw(tie)
        td.polygon([(60, 8), (68, 8), (66, 15), (62, 15)], fill=fx.rgba(nw))
        td.polygon([(62, 15), (66, 15), (71, 62), (64, 70), (57, 62)], fill=fx.rgba(nw))
        if p.get("tie_stripe"):
            for y in range(20, 66, 7):
                td.line([(56, y + 4), (72, y - 4)], fill=fx.rgba(p["tie_stripe"]), width=2)
            tie.putalpha(Image.fromarray(np.minimum(np.asarray(tie.getchannel("A")), np.asarray(
                c.mask_from(F.size, lambda dd: dd.polygon([(60, 8), (68, 8), (66, 15), (71, 62), (64, 70), (57, 62),
                                                          (62, 15)], fill=255))))))
        dt.place(F, tie, (1, 1, 0.8, 0.5))
    # lapels
    for side in (0, 1):
        pts = [(40, 0), (30, 0), (24, 30), (31, 30), (28, 36), (63, 74)]
        pts = c.mirror_pts(pts) if side else pts
        lay = dt.textured_polygon(F.size, pts, c.tex_smooth(lapel_c, 0.006, 0.02)(F.size))
        ImageDraw.Draw(lay).line(pts + [pts[0]], fill=fx.rgba(fx.tone(lapel_c, 0.55)), width=1)
        if p.get("piping"):
            ImageDraw.Draw(lay).line(pts[1:], fill=fx.rgba(p["piping"]), width=1)
        dt.place(F, lay, ((-1 if side else 1), 1, 1.2, 0.6))
    d = ImageDraw.Draw(F)
    d.line([(64, 74), (60, 128)], fill=fx.rgba(fx.tone(jacket, 0.5)), width=1)
    for box in ((12, 98, 42, 104), (86, 98, 116, 104)):
        lay = Image.new("RGBA", F.size)
        ImageDraw.Draw(lay).rectangle(box, fill=fx.rgba(fx.tone(jacket, 1.04)), outline=fx.rgba(fx.tone(jacket, 0.55)))
        dt.place(F, lay, (0, 1, 0.8, 0.5))
    d.line([(88, 44), (108, 42)], fill=fx.rgba(fx.tone(jacket, 0.5)), width=1)
    if crest:
        sh = [(92, 30), (110, 30), (110, 44), (101, 52), (92, 44)]
        lay = dt.polygon_layer(F.size, sh, p["crest"], fx.tone(p["crest"], 0.6))
        ImageDraw.Draw(lay).text((101, 40), brand[0], font=dt.font(10, "serif"),
                                 fill=fx.rgba(p.get("piping", (240, 210, 120))), anchor="mm")
        dt.place(F, lay, (0, 1, 0.8, 0.5))
    else:
        sq = Image.new("RGBA", F.size)
        ImageDraw.Draw(sq).polygon([(92, 43), (95, 37), (98, 41), (101, 36), (104, 41), (106, 43)],
                                   fill=fx.rgba(p.get("pocket_square", shirt_c)))
        dt.place(F, sq, (0, 1, 0.6, 0.4))
    # back: centre seam and vent
    d = ImageDraw.Draw(B)
    d.line([(64, 8), (64, 128)], fill=fx.rgba(fx.tone(jacket, 0.6)), width=1)
    d.line([(65, 104), (65, 128)], fill=fx.rgba(fx.tone(jacket, 0.45)), width=1)
    lay = dt.textured_polygon(B.size, [(30, 0), (98, 0), (96, 8), (32, 8)], c.tex_smooth(lapel_c)(B.size))
    dt.place(B, lay, (0, 1, 1.0, 0.5))
    # shirt cuffs below the jacket sleeves
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            cuff = shirt_tex((64, 8))
            over(img, cuff, (0, 100))
            ImageDraw.Draw(img).line([(0, 100), (64, 100)], fill=fx.rgba(fx.tone(shirt_c, 0.6)))
    c.finish(g, 0.7, folds=0.8)
    for limb in g.limbs:
        out = limb.faces[c.OUTER[limb.name]]
        for i in range(3):
            dt.button(out, 26 + i * 6, 95, 1.4, p.get("buttons", fx.tone(jacket, 0.6)), holes=False)
    buttons = (80,) if neckwear == "bow" else (80, 96)
    for y in buttons:
        dt.button(F, 64, y, 2.4, p.get("buttons", fx.tone(jacket, 0.6)))
    return g


def denim_jacket(p, brand):
    tex = c.tex_denim(p["denim"])
    thread = p.get("thread", (214, 150, 70))
    g = c.shirt(tex, "long")
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]
    for img in c.sides(T) + [s for limb in g.limbs for s in c.sides(limb)]:
        c.fade(img, [(8, 20, img.width - 8, 90)], 0.18, 12)
    ink = fx.rgba(fx.tone(p["denim"], 0.55), 220)
    st = fx.rgba(thread, 230)

    def dbl(d, pts, off=(0, 2)):
        d.line(pts, fill=ink)
        dt.stitch(d, [(x + off[0], y + off[1]) for x, y in pts], st, 2, 2)
        dt.stitch(d, [(x - off[0], y - off[1] + 4 * (off[1] != 0)) for x, y in pts], st, 2, 2)

    d = ImageDraw.Draw(F)
    dbl(d, [(0, 28), (128, 28)])
    for x in (30, 98):
        dbl(d, [(x, 56), (x, 114)], (2, 0))
    d.line([(64, 0), (64, 114)], fill=ink)
    dt.stitch(d, [(68, 4), (68, 114)], st, 2, 2)
    for box in ((32, 32, 54, 52), (74, 32, 96, 52)):
        dt.pocket(F, box, p["denim"], stitch_color=thread, texture=tex(F.size, 1), flap=8,
                  button_color=p.get("button", (176, 116, 60)))
    collar_c = p.get("collar")
    ctex = c.tex_fabric(collar_c, 0.06, 0.2) if collar_c else tex
    for side in (0, 1):
        pts = [(30, 0), (60, 0), (58, 14), (40, 22)]
        pts = c.mirror_pts(pts) if side else pts
        lay = dt.textured_polygon(F.size, pts, ctex(F.size, 2))
        ImageDraw.Draw(lay).line(pts + [pts[0]], fill=ink if not collar_c else fx.rgba(fx.tone(collar_c, 0.75)))
        dt.place(F, lay, (0, 2, 1.4, 0.5))
    for img in c.sides(T):
        band = tex((img.width, 14), 3)
        over(img, band, (0, 114))
        dd = ImageDraw.Draw(img)
        dd.line([(0, 114), (img.width, 114)], fill=ink)
        dt.stitch(dd, [(0, 117), (img.width, 117)], st, 2, 2)
        dt.stitch(dd, [(0, 125), (img.width, 125)], st, 2, 2)
    d = ImageDraw.Draw(B)
    dbl(d, [(0, 26), (64, 42), (128, 26)])
    for x in (34, 94):
        dbl(d, [(x, 38 if x < 64 else 38), (x, 114)], (2, 0))
    if collar_c:
        lay = dt.textured_polygon(B.size, [(26, 0), (102, 0), (98, 10), (30, 10)], ctex(B.size, 5))
        dt.place(B, lay, (0, 1, 1.0, 0.5))
    for limb in g.limbs:
        for f in limb.sides:
            img = limb.faces[f]
            dd = ImageDraw.Draw(img)
            dd.line([(0, 96), (64, 96)], fill=ink)
            dt.stitch(dd, [(0, 99), (64, 99)], st, 2, 2)
        dd = ImageDraw.Draw(limb.faces[c.OUTER[limb.name]])
        dbl(dd, [(32, 0), (32, 96)], (2, 0))
    c.finish(g, 0.8)
    for y in (10, 40, 62, 84, 104, 120):
        dt.button(F, 64, y, 2.2, p.get("button", (176, 116, 60)))
    for limb in g.limbs:
        dt.button(limb.faces[c.OUTER[limb.name]], 32, 102, 2.0, p.get("button", (176, 116, 60)))
    return g


def layered_tee(p, brand):
    tee, sleeve_cols = p["tee"], p["stripes"]
    tex = c.tex_fabric(tee, 0.015)
    stripes = c.tex_stripes(sleeve_cols, [5, 5])
    g = c.shirt(tex, "long", sleeve_tex=stripes)
    for limb in g.limbs:
        fill_short = tex((limb.strip_width, 128))
        limb.over_strip(fx.keep_rows(fill_short, 0, 46))
    g.sleeve_end = 108
    c.cuffs(g, sleeve_cols[0], 6, period=2)
    c.crew_neck(g, fx.tone(tee, 0.92), width=40, depth=9)
    c.hem_band(g, fx.tone(tee, 0.95), 4)
    F, B = g.torso.faces["F"], g.torso.faces["B"]
    if p.get("graphic"):
        dt.paste_graphic(F, GRAPHICS[p["graphic"]](), (64, 56), 62)
    dt.text(B, brand, (64, 16), 8, p.get("ink", (30, 30, 34)), style="black", spacing=1)
    c.finish(g, 0.65)
    for limb in g.limbs:
        for img in c.sides(limb):
            lay = Image.new("RGBA", img.size)
            d = ImageDraw.Draw(lay)
            d.rectangle([0, 41, 64, 46], fill=fx.rgba(fx.tone(tee, 0.88)))
            d.line([(0, 46), (64, 46)], fill=fx.rgba(fx.tone(tee, 0.55)))
            dt.place(img, lay, (0, 2, 1.2, 0.5))
    return g


def graphic_tee(p, brand):
    tee = p["tee"]
    tex = c.tiedye_tex(p["tiedye"]) if p.get("tiedye") else c.tex_fabric(tee, 0.015)
    g = c.shirt(tex, "short")
    F, B = g.torso.faces["F"], g.torso.faces["B"]
    if p.get("tiedye"):
        B.paste(fx.tiedye(B.size, p["tiedye"], center=(70, 56), seed=11), (0, 0))
    c.crew_neck(g, fx.tone(tee, 0.9), width=40, depth=9)
    if p.get("graphic"):
        dt.paste_graphic(F, GRAPHICS[p["graphic"]](), (64, 60), p.get("graphic_width", 74))
    if p.get("chest_text"):
        dt.text(F, p["chest_text"], (64, 102), 9, p.get("ink", (255, 255, 255)), style="black", spacing=2)
    if not p.get("tiedye"):
        dt.text(B, brand, (64, 18), 9, p.get("ink", (255, 255, 255)), style="black", spacing=1)
    c.finish(g, 0.6)
    c.sleeve_hem(g, tee)
    return g


def puffer(p, brand, crop=False):
    base = p["base"]
    tex = c.tex_smooth(base, 0.008, 0.05)
    g = c.shirt(tex, 106, length=94 if crop else 128)
    T = g.torso
    for f in T.sides:
        T.faces[f].paste(c.quilt(T.faces[f], 14, 22, 0.5), (0, 0))
    for limb in g.limbs:
        for f in limb.sides:
            limb.faces[f].paste(c.quilt(limb.faces[f], 2, 19, 0.5), (0, 0))
    F, B = T.faces["F"], T.faces["B"]
    # stand collar
    for face, x0, x1 in ((F, 26, 102), (B, 22, 106)):
        lay = c.tex_smooth(fx.tone(base, 1.06))(face.size)
        lay.putalpha(c.mask_from(face.size, lambda d: d.rounded_rectangle([x0, -6, x1, 13], radius=4, fill=255)))
        ImageDraw.Draw(lay).line([(x0 + 2, 6), (x1 - 2, 6)], fill=fx.rgba(fx.tone(base, 0.7)))
        dt.place(face, lay, (0, 2, 1.6, 0.6))
    fx.cut(F, c.mask_from(F.size, lambda d: d.ellipse([44, -14, 84, 6], fill=255)))
    c.hem_band(g, p.get("trim", fx.tone(base, 0.4)), 7)
    c.cuffs(g, p.get("trim", fx.tone(base, 0.4)), 7)
    lay = Image.new("RGBA", F.size)
    ImageDraw.Draw(lay).rounded_rectangle([88, 36, 108, 44], radius=2, fill=fx.rgba(p.get("patch", (245, 245, 245))))
    ImageDraw.Draw(lay).text((98, 40), brand, font=dt.font(5, "black"), fill=fx.rgba(base), anchor="mm")
    dt.place(F, lay, (0, 1, 0.6, 0.4))
    c.finish(g, 0.6, folds=0.6)
    for face in (F, B):
        c.sheen(face, 30, 44, 0.12, 6)
    for limb in g.limbs:
        for f in ("F", c.OUTER[limb.name]):
            c.sheen(limb.faces[f], 20, 30, 0.14, 4)
    dt.zipper(F, 64, 0, g.length - 7, base, pull_y=10)
    return g


def biker_jacket(p, brand):
    base, tee = p["leather"], p.get("tee", (240, 240, 238))
    tex = c.tex_smooth(base, 0.01, 0.12)
    g = c.shirt(tex, "long")
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]
    metal = p.get("metal", (200, 202, 208))
    # tee showing in the open neck
    tee_lay = c.tex_fabric(tee, 0.01)(F.size)
    tee_lay.putalpha(c.mask_from(F.size, lambda d: d.polygon([(40, 0), (88, 0), (60, 40), (46, 40)], fill=255)))
    over(F, tee_lay)
    fx.cut(F, c.mask_from(F.size, lambda d: d.ellipse([50, -8, 78, 8], fill=255)))
    # wide lapels
    for pts in ([(40, 0), (24, 0), (20, 26), (28, 28), (26, 34), (48, 52), (50, 40)],
                [(88, 0), (106, 0), (110, 22), (102, 26), (104, 32), (78, 44), (62, 40)]):
        lay = dt.textured_polygon(F.size, pts, c.tex_smooth(fx.tone(base, 1.22), 0.008, 0.1)(F.size))
        ImageDraw.Draw(lay).line(pts + [pts[0]], fill=fx.rgba(fx.tone(base, 0.35)), width=1)
        ImageDraw.Draw(lay).line(pts[1:4], fill=fx.rgba(fx.tone(base, 1.6), 160), width=1)
        dt.place(F, lay, (0, 2, 1.6, 0.6))
    # belt at the hem
    for img in c.sides(T):
        lay = c.tex_smooth(fx.tone(base, 0.95), 0.01, 0.12)((img.width, 12))
        d = ImageDraw.Draw(lay)
        d.line([(0, 0), (img.width, 0)], fill=fx.rgba(fx.tone(base, 0.4)))
        dt.stitch(d, [(0, 2), (img.width, 2)], fx.rgba(fx.tone(base, 1.6), 140), 2, 2)
        dt.stitch(d, [(0, 9), (img.width, 9)], fx.rgba(fx.tone(base, 1.6), 140), 2, 2)
        over(img, lay, (0, 114))
    d = ImageDraw.Draw(B)
    d.line([(0, 30), (128, 30)], fill=fx.rgba(fx.tone(base, 0.45)))
    d.line([(36, 30), (40, 114)], fill=fx.rgba(fx.tone(base, 0.45)))
    d.line([(92, 30), (88, 114)], fill=fx.rgba(fx.tone(base, 0.45)))
    c.finish(g, 0.75)
    for face in (F, B):
        c.sheen(face, 16, 26, 0.16, 5)
        c.sheen(face, 96, 104, 0.1, 4)
    for limb in g.limbs:
        for f in ("F", c.OUTER[limb.name]):
            c.sheen(limb.faces[f], 18, 26, 0.22, 3)
        dt.zipper(limb.faces[c.OUTER[limb.name]], 32, 86, 108, base, teeth=metal, pull_y=90)
    # asymmetric front zip: diagonal from the shoulder, then straight down
    d = ImageDraw.Draw(F)
    d.line([(80, 43), (50, 54)], fill=fx.rgba(fx.tone(base, 0.6)), width=4)
    for i in range(15):
        t = i / 14
        d.point([(80 - 30 * t, 43 + 11 * t + (i % 2) - 0.5)], fill=fx.rgba(metal))
    dt.zipper(F, 50, 54, 114, base, teeth=metal, pull_y=60)
    dt.zipper(F, 96, 54, 74, base, teeth=metal, pull_y=56)
    lay = Image.new("RGBA", F.size)
    ld = ImageDraw.Draw(lay)
    ld.rectangle([12, 113, 24, 127], outline=fx.rgba(metal), width=2)
    ld.line([(18, 114), (18, 126)], fill=fx.rgba(metal), width=1)
    dt.place(F, lay, (0, 1, 0.6, 0.5))
    for x, y in ((24, 28), (104, 26), (20, 120), (108, 120)):
        dt.button(F, x, y, 1.6, metal, holes=False)
    return g


def scrubs_top(p, brand):
    base = p["base"]
    tex = c.tex_fabric(base, 0.012)
    g = c.shirt(tex, "short")
    c.v_neck(g, fx.tone(base, 0.82), width=30, depth=28, band=3)
    F = g.torso.faces["F"]
    dt.pocket(F, (84, 40, 106, 62), base, stitch_color=fx.tone(base, 0.7), texture=tex(F.size, 2))
    for box in ((14, 80, 40, 106), (88, 80, 114, 106)):
        dt.pocket(F, box, base, stitch_color=fx.tone(base, 0.7), texture=tex(F.size, 4))
    c.finish(g, 0.6)
    c.sleeve_hem(g, base)
    lay = Image.new("RGBA", F.size)
    d = ImageDraw.Draw(lay)
    d.line([(100, 38), (100, 50)], fill=fx.rgba((40, 40, 46)), width=1)
    d.rounded_rectangle([90, 46, 108, 60], radius=1, fill=fx.rgba((250, 250, 250)), outline=fx.rgba((160, 160, 168)))
    d.rectangle([92, 48, 97, 54], fill=fx.rgba(p.get("badge", (90, 140, 220))))
    d.line([(99, 49), (106, 49)], fill=fx.rgba((120, 120, 130)))
    d.line([(99, 52), (105, 52)], fill=fx.rgba((160, 160, 168)))
    d.rectangle([90, 56, 108, 60], fill=fx.rgba(p.get("badge", (90, 140, 220))))
    dt.place(F, lay, (0, 1, 0.6, 0.45))
    pen = Image.new("RGBA", F.size)
    ImageDraw.Draw(pen).rectangle([86, 34, 87, 44], fill=fx.rgba((30, 30, 36)))
    dt.place(F, pen, (0, 1, 0.5, 0.4))
    return g


def cable_sweater(p, brand):
    base = p["base"]
    tex = c.tex_knit(base)
    g = c.shirt(tex, "long")
    c.crew_neck(g, fx.tone(base, 0.95), width=42, depth=10, band=4)
    c.hem_band(g, fx.tone(base, 0.95), 10, period=2)
    c.cuffs(g, fx.tone(base, 0.95), 10, period=2)
    c.finish(g, 0.7)
    return g


def sweater_vest(p, brand):
    shirt_c = p.get("shirt", (246, 246, 244))
    shirt_tex = c.tex_fabric(shirt_c, 0.01)
    g = c.shirt(shirt_tex, "long")
    T = g.torso
    a = p["argyle"]
    vest = lambda size, ox=0: fx.argyle(size, a[0], a[1], a[2], offset=(ox, 0))  # noqa: E731
    strip = vest((T.strip_width, 128))
    strip = fx.keep_rows(strip, 0, 118)
    T.over_strip(strip)
    F, B = T.faces["F"], T.faces["B"]
    # V neck on the vest showing the shirt and tie
    vee = [(36, 0), (92, 0), (64, 50)]
    lay = dt.textured_polygon(F.size, vee, shirt_tex(F.size))
    over(F, lay)
    trim = p.get("trim", fx.tone(a[0], 0.8))
    d = ImageDraw.Draw(F)
    d.line([(36, 0), (64, 50), (92, 0)], fill=fx.rgba(trim), width=4, joint="curve")
    if p.get("tie"):
        tie = Image.new("RGBA", F.size)
        td = ImageDraw.Draw(tie)
        td.polygon([(60, 8), (68, 8), (66, 14), (62, 14)], fill=fx.rgba(p["tie"]))
        td.polygon([(62, 14), (66, 14), (69, 44), (64, 49), (59, 44)], fill=fx.rgba(p["tie"]))
        dt.place(F, tie, (1, 1, 0.8, 0.5))
    for side in (0, 1):
        pts = [(46, 0), (62, 0), (58, 12), (48, 16)]
        pts = c.mirror_pts(pts) if side else pts
        lay = dt.polygon_layer(F.size, pts, shirt_c, fx.tone(shirt_c, 0.72))
        dt.place(F, lay, (0, 1, 1.0, 0.45))
    for img in c.sides(T):
        dt.rib_band(img, 108, 118, trim, period=2)
        ImageDraw.Draw(img).line([(0, 118), (img.width, 118)], fill=fx.rgba((0, 0, 0), 60))
    lay = Image.new("RGBA", B.size)
    ImageDraw.Draw(lay).rectangle([30, 0, 98, 5], fill=fx.rgba(shirt_c))
    dt.place(B, lay)
    for limb in g.limbs:
        for f in limb.sides:
            ImageDraw.Draw(limb.faces[f]).line([(0, 98), (64, 98)], fill=fx.rgba(fx.tone(shirt_c, 0.7)))
    c.finish(g, 0.7)
    for limb in g.limbs:
        dt.button(limb.faces[c.OUTER[limb.name]], 32, 103, 1.5, (230, 230, 230), holes=False)
    return g


def mesh_top(p, brand):
    base = p["base"]
    tex = c.tex_smooth(base, 0.01, 0.06)
    net = lambda size, ox=0: fx.fishnet(size, p.get("net", (18, 18, 20)), 7, (ox, 0))  # noqa: E731
    g = c.shirt(tex, "long", sleeve_tex=net)
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]
    for face, depth in ((F, 16), (B, 6)):
        fx.cut(face, c.mask_from(face.size, lambda d: d.rectangle([34, 0, 94, depth], fill=255)))
        d = ImageDraw.Draw(face)
        d.line([(34, depth + 1), (94, depth + 1)], fill=fx.rgba(fx.tone(base, 1.6)), width=1)
    # lace-up front
    d = ImageDraw.Draw(F)
    for i, y in enumerate(range(30, 108, 10)):
        d.line([(58, y), (70, y + 8)], fill=fx.rgba(p.get("lace", (180, 30, 50))), width=1)
        d.line([(70, y), (58, y + 8)], fill=fx.rgba(p.get("lace", (180, 30, 50))), width=1)
    for y in range(30, 116, 10):
        dt.button(F, 57, y, 1.2, (200, 200, 205), holes=False)
        dt.button(F, 71, y, 1.2, (200, 200, 205), holes=False)
    for img in c.sides(T):
        ImageDraw.Draw(img).line([(0, 124), (img.width, 124)], fill=fx.rgba(fx.tone(base, 1.5)))
    dt.text(B, brand, (64, 40), 9, p.get("ink", (200, 30, 50)), style="black", spacing=2)
    c.finish(g, 0.55)
    for face in (F, B):
        c.sheen(face, 20, 30, 0.08, 5)
    # chain necklace with a crescent pendant
    lay = Image.new("RGBA", F.size)
    ld = ImageDraw.Draw(lay)
    pts = dt.arc_points(64, 0, 24, 30, 15, 165)
    for i in range(0, len(pts) - 1, 2):
        ld.line([pts[i], pts[i + 1]], fill=fx.rgba((215, 218, 224)), width=1)
    ld.ellipse([59, 28, 69, 38], fill=fx.rgba((215, 218, 224)))
    ld.ellipse([62, 27, 71, 36], fill=(0, 0, 0, 0))
    dt.place(F, lay, (0, 1, 0.6, 0.6))
    return g


# ================================================================= women's line

FITTED = {"fit": "fitted"}


def bow_cardigan(p, brand):
    """Cropped coquette cardigan: puff sleeves, scalloped trim and satin bows instead of buttons."""
    base, bow_c, trim = p["base"], p["bow"], p.get("trim", (252, 250, 246))
    tex = c.tex_knit(base, cable=0)
    g = c.shirt(tex, "long", length=104)
    T = g.torso
    F = T.faces["F"]
    c.puff(g, 0, 42)
    c.cuffs(g, fx.tone(base, 0.95), 8, period=2)
    c.hem_band(g, fx.tone(base, 0.95), 9, period=2)
    neck = c.mask_from(F.size, lambda d: d.ellipse([40, -18, 88, 18], fill=255))
    c.edge_trim(F, neck, fx.tone(base, 0.93), 3)
    fx.cut(F, neck)
    band = fx.ribbed((10, 104 - 17), fx.tone(base, 0.95), period=2)
    over(F, band, (59, 17))
    d = ImageDraw.Draw(F)
    d.line([(59, 17), (59, 104)], fill=fx.rgba(fx.tone(base, 0.7), 180))
    d.line([(69, 17), (69, 104)], fill=fx.rgba(fx.tone(base, 0.7), 180))
    c.finish(g, 0.9, **FITTED)
    c.scallop_edge(F, neck, trim, r=1.8, step=4)
    for img in c.sides(T):
        dt.lace_band(img, 101, 108, trim, scallop=6)
    for limb in g.limbs:
        for img in c.sides(limb):
            dt.lace_band(img, 105, 111, trim, scallop=6)
    for y in (30, 56, 82):
        dt.bow(F, 64, y, 17, bow_c, tails=0.7)
    return g


def milkmaid_top(p, brand):
    """Cottagecore milkmaid top: sweetheart neckline, lace-up bodice, puff sleeves and a frilled hem."""
    base = p["base"]
    tex = c.fabric_tex(p)
    g = c.shirt(tex, 42, length=100)
    T = g.torso
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    c.puff(g, 0, 40)
    trim = p.get("trim", (252, 252, 250))
    neck = c.sweetheart_mask(F.size, depth=30, x0=22, x1=106)
    c.edge_trim(F, neck, trim, 2)
    fx.cut(F, neck)
    bneck = c.mask_from(B.size, lambda d: d.rectangle([26, -4, 102, 8], fill=255))
    c.edge_trim(B, bneck, trim, 2)
    fx.cut(B, bneck)
    c.clear(U, (26, 0, 102, 64))
    dt.smocking(B, 14, 98, base)
    d = ImageDraw.Draw(F)
    for side in (0, 1):
        pts = [(38, 24), (44, 60), (40, 100)]
        d.line(c.mirror_pts(pts) if side else pts, fill=fx.rgba(fx.tone(base, 0.7), 170), width=1)
    c.finish(g, 0.85, **FITTED)
    c.gathered_cuff(g, 42, trim if p.get("trim_cuffs", True) else base, band=3, frill=3)
    for img in c.sides(T):
        dt.ruffle(img, 97, 103, tex(img.size, 5), base, wave=5, amp=1.2)
    c.scallop_edge(F, neck, trim, r=1.5, step=3.5)
    dt.lacing(F, 64, 28, 92, 8, p.get("lace", trim), step=8)
    return g


def off_shoulder_top(p, brand):
    """Ribbed off-the-shoulder crop top with long fitted sleeves and a heart necklace."""
    base = p["base"]
    tex = c.tex_rib(base, 3, 0.12)
    g = c.shirt(tex, "long", length=88)
    top = 14
    for part in g.parts:
        for f in part.sides:
            c.clear(part.faces[f], (0, 0, part.faces[f].width, top))
        part.faces["U"].paste(Image.new("RGBA", part.size("U")), (0, 0))
    frill = c.tex_rib(base, 3, 0.12)
    for img in c.sides(g.torso):
        d = ImageDraw.Draw(img)
        d.line([(0, 84), (img.width, 84)], fill=fx.rgba(fx.tone(base, 0.65), 200))
        dt.stitch(d, [(0, 86), (img.width, 86)], fx.rgba(fx.tone(base, 0.75)), 2, 2)
    c.cuffs(g, fx.tone(base, 0.95), 6, period=2)
    c.finish(g, 0.9, **FITTED)
    for part in g.parts:
        for img in c.sides(part):
            dt.ruffle(img, top, top + 10, frill(img.size, 4), base, wave=7, amp=1.4)
    dt.necklace(g.torso.faces["F"], 64, 9, 44, p.get("chain", (232, 196, 110)), "heart")
    return g


def lace_cami(p, brand):
    """Satin slip cami with lace trim, thin straps and a tiny bow."""
    base, lace = p["base"], p.get("lace", p["base"])
    tex = c.tex_satin(base)
    g = c.shirt(tex, "none", length=104)
    T = g.torso
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    straps = ((31, 35), (93, 97))

    def neckline(img, y):
        m = c.mask_from(img.size, lambda d: d.rectangle([0, 0, img.width, y], fill=255))
        d = ImageDraw.Draw(m)
        for x0, x1 in straps:
            d.rectangle([x0, 0, x1, y], fill=0)
        fx.cut(img, m)

    neckline(F, 22)
    neckline(B, 30)
    for f in "RL":
        c.clear(T.faces[f], (0, 0, 64, 32))
    U.paste(Image.new("RGBA", U.size), (0, 0))
    for x0, x1 in straps:
        over(U, tex((x1 - x0 + 1, 64)), (x0, 0))
    c.finish(g, 0.8, **FITTED)
    for face in (F, B):
        c.sheen(face, 36, 48, 0.12, 5)
        c.sheen(face, 84, 90, 0.08, 3)
    dt.lace_band(F, 14, 28, lace, scallop=8, edge="top", x0=0, x1=128)
    dt.lace_band(B, 22, 34, lace, scallop=8, edge="top")
    for img in c.sides(T):
        dt.lace_band(img, 98, 110, lace, scallop=7)
    dt.bow(F, 64, 25, 9, p.get("bow", lace), tails=0.8)
    return g


def baby_tee(p, brand):
    """Fitted Y2K baby tee: cropped, ringer trims and a cute centre graphic."""
    base, trim = p["base"], p.get("trim", p["base"])
    g = c.shirt(c.tex_rib(base, 2, 0.07), 34, length=96)
    c.crew_neck(g, trim, width=38, depth=8, band=3)
    for limb in g.limbs:
        for img in c.sides(limb):
            ImageDraw.Draw(img).rectangle([0, 30, img.width, 33], fill=fx.rgba(trim))
    F, B = g.torso.faces["F"], g.torso.faces["B"]
    for img in c.sides(g.torso):
        d = ImageDraw.Draw(img)
        d.line([(0, 92), (img.width, 92)], fill=fx.rgba(fx.tone(base, 0.7), 170))
    if p.get("graphic"):
        dt.paste_graphic(F, GRAPHICS[p["graphic"]](), (64, 42 if p.get("text") else 50), p.get("graphic_width", 40))
    if p.get("text"):
        dt.text(F, p["text"], (64, 68), p.get("text_size", 9), p.get("ink", trim), style="black", spacing=1,
                stroke=p.get("stroke", 0), stroke_color=p.get("stroke_color"))
    dt.text(B, brand, (64, 16), 7, p.get("ink", trim), style="black", spacing=1)
    c.finish(g, 0.8, **FITTED)
    return g


def heart_sweater(p, brand):
    """Oversized fuzzy mohair sweater with a big knitted heart."""
    base, heart = p["base"], p["heart"]
    tex = c.tex_mohair(base)
    g = c.shirt(tex, "long", length=128)
    F = g.torso.faces["F"]
    pts = dt.heart_points(64, 60, 30)
    lay = c.tex_mohair(heart)(F.size)
    lay.putalpha(c.mask_from(F.size, lambda d: d.polygon(pts, fill=255)))
    over(F, lay)
    if p.get("back_heart"):
        B = g.torso.faces["B"]
        lay = c.tex_mohair(heart)(B.size)
        lay.putalpha(c.mask_from(B.size, lambda d: d.polygon(dt.heart_points(64, 22, 8), fill=255)))
        over(B, lay)
    c.crew_neck(g, fx.tone(base, 0.95), width=42, depth=10, band=4)
    c.hem_band(g, fx.tone(base, 0.95), 12, period=2)
    c.cuffs(g, fx.tone(base, 0.95), 12, period=2)
    c.finish(g, 0.9)
    return g


def halter_top(p, brand):
    """Y2K halter crop top: bare shoulders, open back tied with a bow, butterfly on the front."""
    base = p["base"]
    tex = c.fabric_tex(p)
    g = c.shirt(tex, "none", length=92)
    T = g.torso
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    front = [(44, 0), (84, 0), (112, 34), (118, 92), (10, 92), (16, 34)]
    c.keep_only(F, lambda d: d.polygon(front, fill=255))
    c.keep_only(B, lambda d: (d.rectangle([0, 70, 128, 92], fill=255), d.rectangle([44, 0, 84, 6], fill=255)))
    for f in "RL":
        c.keep_only(T.faces[f], lambda d: d.rectangle([0, 36, 64, 92], fill=255))
    c.keep_only(U, lambda d: d.rectangle([44, 0, 84, 64], fill=255))
    trim = p.get("trim", fx.tone(base, 0.8))
    d = ImageDraw.Draw(F)
    d.line(front[1:5], fill=fx.rgba(trim), width=2)
    d.line([front[5], front[0]], fill=fx.rgba(trim), width=2)
    if p.get("graphic"):
        dt.paste_graphic(F, GRAPHICS[p["graphic"]](), (64, 52), p.get("graphic_width", 44))
    c.finish(g, 0.8, **FITTED)
    if p.get("fabric") == "satin":
        c.sheen(F, 36, 46, 0.12, 5)
    dt.bow(B, 64, 4, 14, base, tails=1.2)
    if p.get("rhinestones"):
        dt.rhinestones(F, dt.heart_points(64, 54, 17, 26), 1.0, p["rhinestones"])
        dt.rhinestones(F, dt.heart_points(64, 54, 10, 16), 0.8, p["rhinestones"])
    return g


def bow_blouse(p, brand):
    """Satin blouse with balloon sleeves, frilled cuffs, pearl buttons and a big pussy-bow."""
    base = p["base"]
    tex = c.tex_satin(base, 0.3)
    g = c.shirt(tex, 102, length=128)
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]
    c.puff(g, 0, 46)
    d = ImageDraw.Draw(F)
    d.rectangle([40, 0, 88, 5], fill=fx.rgba(fx.tone(base, 0.92)))
    d.line([(64, 14), (64, 128)], fill=fx.rgba(fx.tone(base, 0.62), 200))
    d.line([(67, 14), (67, 128)], fill=fx.rgba(fx.tone(base, 0.8), 140))
    ImageDraw.Draw(B).line([(0, 20), (128, 20)], fill=fx.rgba(fx.tone(base, 0.65), 170))
    c.finish(g, 0.85, **FITTED)
    for face in (F, B):
        c.sheen(face, 26, 38, 0.10, 5)
        c.sheen(face, 92, 98, 0.07, 3)
    c.gathered_cuff(g, 102, base, band=5, frill=4, tex=tex)
    for y in range(46, 124, 14):
        dt.pearls(F, [(64, y)], 1.4, p.get("buttons", (250, 246, 236)))
    dt.bow(F, 64, 12, 38, p.get("bow", fx.tone(base, 0.9)), tails=1.2)
    return g


def sailor_top(p, brand):
    """Sailor-uniform top: striped sailor collar, big scarf bow, striped cuffs."""
    base, collar, stripe, scarf = p["base"], p["collar"], p["stripe"], p["scarf"]
    long_sleeves = p.get("sleeves") == "long"
    g = c.shirt(c.tex_fabric(base, 0.01), "long" if long_sleeves else "short", length=116)
    T = g.torso
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    fx.cut(F, c.mask_from(F.size, lambda d: d.polygon([(46, 0), (82, 0), (64, 30)], fill=255)))
    ctex = c.tex_fabric(collar, 0.01)
    for side in (0, 1):
        flap = [(16, 0), (46, 0), (64, 30), (62, 44)]
        flap = c.mirror_pts(flap) if side else flap
        lay = dt.textured_polygon(F.size, flap, ctex(F.size))
        ld = ImageDraw.Draw(lay)
        for k in (0.16, 0.3):
            o = [(16 + 46 * t, 44 * t) for t in (0, 1)]
            i = [(46 + 18 * t, 30 * t) for t in (0, 1)]
            line = [(o[j][0] + k * (i[j][0] - o[j][0]), o[j][1] + k * (i[j][1] - o[j][1])) for j in (0, 1)]
            ld.line(c.mirror_pts(line) if side else line, fill=fx.rgba(stripe), width=1)
        dt.place(F, lay, (0, 2, 1.4, 0.5))
    lay = ctex(B.size)
    lay.putalpha(c.mask_from(B.size, lambda d: d.rectangle([14, 0, 114, 46], fill=255)))
    ld = ImageDraw.Draw(lay)
    for k in (4, 7):
        ld.line([(14 + k, 0), (14 + k, 46 - k), (114 - k, 46 - k), (114 - k, 0)], fill=fx.rgba(stripe), width=1)
    dt.place(B, lay, (0, 2, 1.6, 0.5))
    U.paste(ctex(U.size), (0, 0))
    e = g.sleeve_end
    for limb in g.limbs:
        for img in c.sides(limb):
            band = ctex((img.width, 9))
            over(img, band, (0, e - 9))
            dd = ImageDraw.Draw(img)
            dd.line([(0, e - 6), (img.width, e - 6)], fill=fx.rgba(stripe))
            dd.line([(0, e - 3), (img.width, e - 3)], fill=fx.rgba(stripe))
    for img in c.sides(T):
        ImageDraw.Draw(img).line([(0, 112), (img.width, 112)], fill=fx.rgba(fx.tone(base, 0.7), 170))
    if p.get("badge"):
        dt.text(g.left.faces[c.OUTER["left"]], "✦", (32, 22), 10, stripe)
    c.finish(g, 0.8, **FITTED)
    dt.bow(F, 64, 40, 24, scarf, tails=1.1)
    return g


def corset_top(p, brand):
    """Satin corset with a sweetheart neckline, boning, lace-up front and a pointed waist."""
    base, lace_c = p["base"], p.get("lacing", (240, 240, 244))
    tex = c.tex_satin(base, 0.3)
    mesh = p.get("mesh")
    def sheer(size, ox=0):
        """Sheer mesh: a light tint with a fine net over it."""
        tint = fx.to_image(np.broadcast_to(np.array(fx.rgb(mesh), np.float32) / 255, (size[1], size[0], 3)).copy(),
                           np.full((size[1], size[0]), 0.28, np.float32))
        tint.alpha_composite(fx.fishnet(size, mesh, 4, (ox, 0)))
        return tint
    g = c.shirt(tex, "long" if mesh else "none", sleeve_tex=sheer if mesh else None, length=112)
    T = g.torso
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    neck = c.sweetheart_mask(F.size, depth=30, x0=18, x1=110)
    fx.cut(F, neck)
    c.keep_only(F, lambda d: d.polygon([(0, 0), (128, 0), (128, 104), (64, 114), (0, 104)], fill=255))
    c.clear(B, (0, 0, 128, 10))
    for f in "RL":
        c.clear(T.faces[f], (0, 0, 64, 22))
    c.clear(U, (0, 0, 128, 64))
    if mesh:
        for img, m in ((F, neck),):
            lay = sheer(img.size)
            lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m))))
            over(img, lay)
        for f in "RLB":
            img = T.faces[f]
            y1 = 10 if f == "B" else 22
            over(img, sheer((img.width, y1)), (0, 0))
        U.paste(sheer(U.size), (0, 0))
    else:
        for x0 in (30, 94):
            for face in (F, B):
                over(face, tex((4, 30)), (x0, 0))
            over(U, tex((4, 64)), (x0, 0))
    d = ImageDraw.Draw(F)
    for x in (24, 44):
        for side in (0, 1):
            pts = [(x, 26), (x + 6, 64), (x, 104)]
            pts = c.mirror_pts(pts) if side else pts
            d.line(pts, fill=fx.rgba(fx.tone(base, 0.55), 220), width=1)
            d.line([(px + 1, py) for px, py in pts], fill=fx.rgba(fx.tone(base, 1.5), 90), width=1)
    db = ImageDraw.Draw(B)
    for x in (28, 50, 78, 100):
        db.line([(x, 14), (x, 108)], fill=fx.rgba(fx.tone(base, 0.55), 200), width=1)
    c.finish(g, 0.85, **FITTED)
    for face in (F, B):
        c.sheen(face, 32, 40, 0.14, 4)
        c.sheen(face, 88, 94, 0.10, 3)
    if p.get("lace_trim"):
        c.scallop_edge(F, neck, p["lace_trim"], r=1.8, step=4)
    dt.lacing(F, 64, 34, 100, 10, lace_c, step=9)
    dt.lacing(B, 64, 18, 102, 12, lace_c, step=10, bow_top=False)
    dt.bow(B, 64, 104, 10, lace_c, tails=1.0)
    return g


def sundress_top(p, brand):
    """Bodice of a sundress: square neck, straps, smocked back and a ribbon waist tie.

    The skirt continues on the matching pants (pants.sundress_skirt)."""
    base = p["base"]
    tex = c.fabric_tex(p)
    g = c.shirt(tex, p.get("sleeves", "none"), length=128)
    T = g.torso
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    straps = ((22, 32), (96, 106))

    def cut_between(img, y):
        m = c.mask_from(img.size, lambda d: d.rectangle([0, 0, img.width, y], fill=255))
        d = ImageDraw.Draw(m)
        for x0, x1 in straps:
            d.rectangle([x0, 0, x1, y], fill=0)
        fx.cut(img, m)

    neck = c.mask_from(F.size, lambda d: d.rectangle([32, -4, 96, 18], fill=255))
    c.edge_trim(F, neck, p.get("trim", fx.tone(base, 0.85)), 2)
    cut_between(F, 18)
    cut_between(B, 12)
    for f in "RL":
        c.clear(T.faces[f], (0, 0, 64, 26))
    if g.sleeve_end:
        c.puff(g, 0, g.sleeve_end - 2)
    U.paste(Image.new("RGBA", U.size), (0, 0))
    for x0, x1 in straps:
        over(U, tex((x1 - x0 + 1, 64)), (x0, 0))
    dt.smocking(B, 14, 58, base)
    for img in c.sides(T):
        c.drape(img, 62, 128, 14, 0.4, seed=img.width)
    c.finish(g, 0.75, **FITTED)
    if g.sleeve_end:
        c.gathered_cuff(g, g.sleeve_end, base, band=3, frill=3, tex=tex)
    tie = p.get("tie", fx.tone(base, 0.8))
    for img in c.sides(T):
        lay = Image.new("RGBA", img.size)
        ImageDraw.Draw(lay).rectangle([0, 58, img.width, 63], fill=fx.rgba(tie))
        dt.place(img, lay, (0, 1, 0.8, 0.45))
    dt.bow(F, 64, 60, 16, tie, tails=1.4)
    return g


def cricket_sweater(p, brand):
    """Preppy cable V-neck with sporty stripes at the neck, cuffs and hem."""
    base, (s1, s2) = p["base"], p["stripes"]
    tex = c.tex_knit(base, period=26, cable=10)
    g = c.shirt(tex, "long", length=128)
    c.v_neck(g, fx.tone(base, 0.96), width=34, depth=40, band=6)
    F = g.torso.faces["F"]
    d = ImageDraw.Draw(F)
    for k, col in ((2, s1), (4, s2)):
        d.line([(64 - 17 - k, 0), (64, 40 + k * 1.6), (64 + 17 + k, 0)], fill=fx.rgba(col), width=1)
    for img in c.sides(g.torso):
        dt.rib_band(img, 116, 128, fx.tone(base, 0.96), period=2)
        dd = ImageDraw.Draw(img)
        dd.rectangle([0, 119, img.width, 120], fill=fx.rgba(s1))
        dd.rectangle([0, 122, img.width, 123], fill=fx.rgba(s2))
    for limb in g.limbs:
        for img in c.sides(limb):
            dt.rib_band(img, 98, 108, fx.tone(base, 0.96), period=2)
            dd = ImageDraw.Draw(img)
            dd.rectangle([0, 101, img.width, 102], fill=fx.rgba(s1))
            dd.rectangle([0, 104, img.width, 105], fill=fx.rgba(s2))
    c.finish(g, 0.8)
    return g


# ================================================================= more women's tops

def wrap_top(p, brand):
    """Balletcore wrap top: crossover V front, fitted long sleeves and a side tie."""
    base = p["base"]
    tex = c.tex_rib(base, 2, 0.07)
    g = c.shirt(tex, "long", length=100)
    F = g.torso.faces["F"]
    vee = c.mask_from(F.size, lambda d: d.polygon([(38, -2), (90, -2), (64, 44)], fill=255))
    c.edge_trim(F, vee, fx.tone(base, 0.92), 3)
    fx.cut(F, vee)
    panel = [(0, 0), (38, 0), (64, 44), (112, 96), (112, 100), (0, 100)]
    lay = dt.textured_polygon(F.size, panel, tex(F.size, 3))
    ld = ImageDraw.Draw(lay)
    ld.line(panel[1:4], fill=fx.rgba(fx.tone(base, 1.3), 170), width=1)
    fx.cut(lay, vee)
    dt.place(F, lay, (1, 1, 1.4, 0.55))
    for img in c.sides(g.torso):
        dt.rib_band(img, 94, 100, fx.tone(base, 0.95), period=2)
    c.cuffs(g, fx.tone(base, 0.95), 5, period=2)
    c.finish(g, 0.85, **FITTED)
    dt.bow(F, 112, 96, 13, fx.tone(base, 0.96), tails=1.6)
    return g


def tube_top(p, brand):
    """Strapless ruched tube top, cropped, with a ring or bow at the centre."""
    base = p["base"]
    tex = c.fabric_tex(p)
    g = c.shirt(tex, "none", length=88)
    T = g.torso
    top = 22
    for f in T.sides:
        c.clear(T.faces[f], (0, 0, T.faces[f].width, top))
    T.faces["U"].paste(Image.new("RGBA", T.size("U")), (0, 0))
    for f in T.sides:
        img = T.faces[f]
        w = img.width
        rnd = random.Random(f"ruche/{f}")
        m = Image.new("L", img.size, 128)
        d = ImageDraw.Draw(m)
        for i in range(9 if f in "FB" else 4):
            y = top + 6 + i * (60 / (9 if f in "FB" else 4)) + rnd.uniform(-2, 2)
            for side in ((0, 1) if f in "FB" else (0,)):
                x0, x1 = rnd.uniform(0, 18), (w / 2 - rnd.uniform(2, 10)) if f in "FB" else rnd.uniform(40, 64)
                pts = [(x0, y), ((x0 + x1) / 2, y + rnd.uniform(0, 3)), (x1, y + rnd.uniform(2, 5))]
                if side:
                    pts = [(w - x, yy) for x, yy in pts]
                d.line(pts, fill=70, width=2)
                d.line([(x, yy - 2) for x, yy in pts], fill=170, width=1)
        m = m.filter(ImageFilter.GaussianBlur(0.9))
        img.paste(fx.apply_shade(img, m, 0.8), (0, 0))
        ImageDraw.Draw(img).line([(0, top), (w, top)], fill=fx.rgba(fx.tone(base, 1.35), 160))
    c.finish(g, 0.85, **FITTED)
    F = T.faces["F"]
    if p.get("ring"):
        lay = Image.new("RGBA", F.size)
        ImageDraw.Draw(lay).ellipse([58, 44, 70, 56], outline=fx.rgba(p["ring"]), width=2)
        dt.place(F, lay, (0, 1, 0.6, 0.5))
    else:
        dt.bow(F, 64, top + 5, 12, p.get("bow", fx.tone(base, 0.9)), tails=0.8)
    return g


def shrug_cami(p, brand):
    """Fuzzy cropped bolero shrug over a satin cami."""
    cami, shrug = p["cami"], p["shrug"]
    stex, ctex = c.tex_mohair(shrug), c.tex_satin(cami, 0.25)
    g = c.shirt(stex, "long", length=128)
    T = g.torso
    for f in T.sides:
        T.faces[f].paste(Image.new("RGBA", T.size(f)), (0, 0))
    T.faces["D"].paste(Image.new("RGBA", T.size("D")), (0, 0))
    c.fill(T, ctex, 20, 104, caps="")
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    U.paste(stex(U.size), (0, 0))
    edge = fx.tone(shrug, 0.92)
    for side in (0, 1):
        pts = [(0, 0), (36, 0), (32, 16), (20, 32), (0, 42)]
        pts = c.mirror_pts(pts) if side else pts
        lay = dt.textured_polygon(F.size, pts, stex(F.size, side))
        ImageDraw.Draw(lay).line(pts[1:], fill=fx.rgba(edge), width=2)
        dt.place(F, lay, ((2 if not side else -2), 1, 1.4, 0.5))
    back = stex(B.size, 4)
    back.putalpha(c.mask_from(B.size, lambda d: d.chord([-30, -60, 158, 48], 0, 180, fill=255)))
    dt.place(B, back, (0, 2, 1.6, 0.5))
    for f in "RL":
        img = T.faces[f]
        lay = stex(img.size, 6)
        lay.putalpha(c.mask_from(img.size, lambda d: d.rectangle([0, 0, 64, 40], fill=255)))
        dt.place(img, lay, (0, 2, 1.4, 0.45))
    c.cuffs(g, edge, 7, period=2)
    c.finish(g, 0.85, **FITTED)
    c.sheen(F, 40, 50, 0.1, 5)
    dt.lace_band(F, 14, 26, p.get("lace", fx.tone(cami, 1.05)), scallop=8, edge="top", x0=30, x1=98)
    for img in c.sides(T):
        dt.lace_band(img, 98, 110, p.get("lace", fx.tone(cami, 1.05)), scallop=7)
    return g


def cheer_top(p, brand):
    """Cheerleader shell top: V neck, chevron stripes and the team name across the chest."""
    base, accent, accent2 = p["base"], p["accent"], p.get("accent2", (252, 252, 252))
    g = c.shirt(c.tex_fabric(base, 0.01), "none", length=96)
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]
    for f in "RL":
        c.clear(T.faces[f], (0, 0, 64, 30))
    c.v_neck(g, accent, width=30, depth=30, band=3)
    d = ImageDraw.Draw(F)
    for off, col, wdt in ((0, accent, 5), (7, accent2, 2), (11, accent, 2)):
        d.line([(0, 34 + off), (64, 64 + off), (128, 34 + off)], fill=fx.rgba(col), width=wdt)
    for img in c.sides(T):
        dd = ImageDraw.Draw(img)
        dd.rectangle([0, 86, img.width, 91], fill=fx.rgba(accent))
        dd.rectangle([0, 93, img.width, 94], fill=fx.rgba(accent2))
    dt.text(F, p.get("team", brand), (64, 86), 13, accent2, style="black", stroke=2, stroke_color=accent, spacing=1)
    dt.text(B, p.get("team", brand), (64, 28), 11, accent, style="black", spacing=2)
    dt.text(B, p.get("number", "1"), (64, 58), 30, accent, style="black", stroke=2, stroke_color=accent2)
    c.finish(g, 0.8, **FITTED)
    return g


def gown_top(p, brand):
    """Bodice of a prom / party gown: strapless sweetheart, waist sash, flowing skirt start.

    The floor-length skirt is pants.gown_skirt."""
    base = p["base"]
    tex = c.tex_satin(base, 0.3)
    g = c.shirt(tex, "none", length=128)
    T = g.torso
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    neck = c.sweetheart_mask(F.size, depth=28, x0=18, x1=110)
    fx.cut(F, neck)
    c.clear(B, (0, 0, 128, 18))
    for f in "RL":
        c.clear(T.faces[f], (0, 0, 64, 24))
    U.paste(Image.new("RGBA", U.size), (0, 0))
    if p.get("straps"):
        for x0 in (28, 96):
            for face in (F, B):
                over(face, tex((4, 30)), (x0, 0))
            over(U, tex((4, 64)), (x0, 0))
    d = ImageDraw.Draw(F)
    for side in (0, 1):
        pts = [(36, 30), (44, 60), (42, 88)]
        d.line(c.mirror_pts(pts) if side else pts, fill=fx.rgba(fx.tone(base, 0.62), 180), width=1)
    for img in c.sides(T):
        c.drape(img, 92, 128, 16, 0.35, seed=img.width + 1)
    c.finish(g, 0.8, **FITTED)
    for face in (F, B):
        c.sheen(face, 34, 44, 0.12, 5)
    sash = p.get("sash", fx.tone(base, 0.88))
    for img in c.sides(T):
        lay = c.tex_satin(sash, 0.3)(img.size)
        lay.putalpha(c.mask_from(img.size, lambda dd: dd.rectangle([0, 86, img.width, 92], fill=255)))
        dt.place(img, lay, (0, 1, 1.0, 0.5))
    if p.get("lace"):
        c.scallop_edge(F, neck, p["lace"], r=1.8, step=4)
    if p.get("sparkle"):
        for img in c.sides(T):
            c.glitter(img, 0.05, p["sparkle"], seed=img.width)
    if p.get("brooch"):
        dt.rhinestones(F, [(64 + 4 * math.cos(a), 89 + 3 * math.sin(a)) for a in
                           [i * math.pi / 4 for i in range(8)]] + [(64, 89)], 1.0, p["brooch"])
    else:
        dt.bow(F, 64, 89, 16, sash, tails=1.2)
    return g


def pj_shirt(p, brand):
    """Satin button-up pajama shirt with contrast piping."""
    base, piping = p["base"], p["piping"]
    tex = c.tex_satin(base, 0.25)
    g = c.shirt(tex, "long", length=124)
    T = g.torso
    F, B = T.faces["F"], T.faces["B"]
    vee = c.mask_from(F.size, lambda d: d.polygon([(46, -2), (82, -2), (64, 30)], fill=255))
    fx.cut(F, vee)
    d = ImageDraw.Draw(F)
    d.line([(64, 30), (64, 124)], fill=fx.rgba(fx.tone(base, 0.6), 200))
    d.line([(67, 30), (67, 124)], fill=fx.rgba(piping), width=1)
    pk = (84, 40, 102, 58)
    dt.pocket(F, pk, base, stitch_color=fx.tone(base, 0.75), texture=tex(F.size, 2))
    ImageDraw.Draw(F).line([(pk[0], pk[1]), (pk[2], pk[1])], fill=fx.rgba(piping), width=1)
    for img in c.sides(T):
        ImageDraw.Draw(img).line([(0, 121), (img.width, 121)], fill=fx.rgba(piping), width=1)
    for limb in g.limbs:
        for img in c.sides(limb):
            over(img, c.tex_satin(fx.tone(base, 0.95), 0.2)((img.width, 8)), (0, 100))
            ImageDraw.Draw(img).line([(0, 100), (img.width, 100)], fill=fx.rgba(piping), width=1)
    lay = dt.textured_polygon(B.size, [(30, 0), (98, 0), (96, 7), (32, 7)], tex(B.size, 4))
    ImageDraw.Draw(lay).line([(32, 7), (96, 7)], fill=fx.rgba(piping))
    dt.place(B, lay, (0, 1, 1.0, 0.5))
    c.finish(g, 0.8)
    for face in (F, B):
        c.sheen(face, 28, 38, 0.1, 5)
    for side in (0, 1):
        flap = [(30, 0), (46, 0), (64, 30), (58, 34), (38, 18)]
        flap = c.mirror_pts(flap) if side else flap
        lay = dt.textured_polygon(F.size, flap, tex(F.size, 5))
        ImageDraw.Draw(lay).line(flap[1:] + [flap[0]], fill=fx.rgba(piping), width=1)
        dt.place(F, lay, (0, 1, 1.2, 0.5))
    for y in range(42, 122, 18):
        dt.button(F, 66, y, 1.8, piping, holes=False)
    return g


def overall_top(p, brand):
    """Denim overall bib and straps over a tee (pants.overall_shorts are the bottom half)."""
    denim_c, thread = p["denim"], p.get("thread", (214, 150, 70))
    if p.get("tee_stripes"):
        tee_tex = c.tex_stripes(p["tee_stripes"], [3, 3])
    else:
        tee_tex = c.tex_fabric(p["tee"], 0.012)
    g = c.shirt(tee_tex, "short", length=128)
    tee_c = p.get("tee", p.get("tee_stripes", [(250, 250, 250)])[0])
    c.crew_neck(g, fx.tone(tee_c, 0.92), width=40, depth=9)
    dtex = c.tex_denim(denim_c)
    T = g.torso
    F, B, U = T.faces["F"], T.faces["B"], T.faces["U"]
    ink = fx.rgba(fx.tone(denim_c, 0.5))

    def denim_poly(face, pts, seed=0):
        lay = dt.textured_polygon(face.size, pts, dtex(face.size, seed))
        ld = ImageDraw.Draw(lay)
        ld.line(pts + [pts[0]], fill=ink)
        dt.place(face, lay, (0, 1, 1.2, 0.5))
        return lay

    bib = [(30, 40), (98, 40), (98, 128), (30, 128)]
    denim_poly(F, bib, 1)
    d = ImageDraw.Draw(F)
    dt.stitch(d, [(32, 42), (96, 42), (96, 128)], fx.rgba(thread), 2, 2)
    dt.stitch(d, [(32, 42), (32, 128)], fx.rgba(thread), 2, 2)
    dt.pocket(F, (46, 52, 82, 76), denim_c, stitch_color=thread, texture=dtex(F.size, 2))
    for f in "RL":
        lay = dtex(T.size(f), 3)
        lay.putalpha(c.mask_from(T.size(f), lambda dd: dd.rectangle([0, 84, 64, 128], fill=255)))
        dt.place(T.faces[f], lay, (0, 1, 1.0, 0.45))
    for x0 in (32, 86):
        denim_poly(F, [(x0, 0), (x0 + 10, 0), (x0 + 10, 42), (x0, 42)], 4)
        over(U, dtex((10, 64), 5), (x0, 0))
    for a, b in (((34, 0), (78, 62)), ((94, 0), (50, 62))):
        lay = Image.new("RGBA", B.size)
        ImageDraw.Draw(lay).line([a, b], fill=(255, 255, 255, 255), width=10)
        strap = dtex(B.size, 6)
        strap.putalpha(lay.getchannel("A"))
        dt.place(B, strap, (0, 1, 1.0, 0.5))
    denim_poly(B, [(40, 60), (88, 60), (88, 128), (40, 128)], 7)
    c.finish(g, 0.75)
    c.sleeve_hem(g, tee_c)
    for x in (37, 91):
        dt.button(F, x, 42, 2.6, p.get("button", (214, 176, 84)))
    for f in "RL":
        dt.button(T.faces[f], 32, 90, 2.2, p.get("button", (214, 176, 84)))
    return g
