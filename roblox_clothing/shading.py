"""Procedural cloth shading: folds, wrinkles and ambient occlusion per face.

Each map is an L-mode image where 128 is neutral, darker values are shadow
and lighter values are highlight. Maps are applied with fx.apply_shade, so
they only affect pixels that already have fabric on them.
"""

import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .fx import apply_shade
from .template import INNER, inner_edge_x

N = 128
PAD = 16


def _bezier(pts, n=24):
    """Points along a quadratic (3 pts) or cubic (4 pts) Bezier curve."""
    out = []
    for i in range(n + 1):
        t = i / n
        if len(pts) == 3:
            (x0, y0), (x1, y1), (x2, y2) = pts
            x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t ** 2 * x2
            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t ** 2 * y2
        else:
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts
            u = 1 - t
            x = u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3
            y = u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3
        out.append((x, y))
    return out


class _Map:
    def __init__(self, size):
        self.w, self.h = size
        big = (self.w + 2 * PAD, self.h + 2 * PAD)
        self.broad = Image.new("L", big, N)
        self.fine = Image.new("L", big, N)
        self.bd = ImageDraw.Draw(self.broad)
        self.fd = ImageDraw.Draw(self.fine)

    def _p(self, pts):
        return [(x + PAD, y + PAD) for x, y in pts]

    def ellipse(self, box, value):
        x0, y0, x1, y1 = box
        self.bd.ellipse([x0 + PAD, y0 + PAD, x1 + PAD, y1 + PAD], fill=value)

    def rect(self, box, value):
        x0, y0, x1, y1 = box
        self.bd.rectangle([x0 + PAD, y0 + PAD, x1 + PAD, y1 + PAD], fill=value)

    def edges(self, left=92, right=92, top=None, bottom=None, t=3):
        w, h = self.w, self.h
        if left is not None:
            self.rect((-PAD, -PAD, t, h + PAD), left)
        if right is not None:
            self.rect((w - t, -PAD, w + PAD, h + PAD), right)
        if top is not None:
            self.rect((-PAD, -PAD, w + PAD, t), top)
        if bottom is not None:
            self.rect((-PAD, h - t, w + PAD, h + PAD), bottom)

    def fold(self, pts, depth=55, width=2, hl=(0, -2)):
        """A crease: a dark line with a thin highlight just beside it."""
        line = _bezier(pts)
        if hl:
            self.fd.line(self._p([(x + hl[0], y + hl[1]) for x, y in line]), fill=N + depth // 2, width=1)
        self.fd.line(self._p(line), fill=N - depth, width=width)

    def result(self, broad_blur=7, fine_blur=1.3):
        b = np.asarray(self.broad.filter(ImageFilter.GaussianBlur(broad_blur)), np.float32)
        f = np.asarray(self.fine.filter(ImageFilter.GaussianBlur(fine_blur)), np.float32)
        out = np.clip(b + f - N, 0, 255).astype(np.uint8)
        return Image.fromarray(out, "L").crop((PAD, PAD, PAD + self.w, PAD + self.h))


def face_map(kind, part, face, size, seed=0, sleeve_end=110, hem=128, baggy=0.0, folds=1.0):
    """Shading map for one face.

    kind: "shirt" or "pants"; part: "torso" / "right" / "left".
    sleeve_end: lowest fabric row on arm faces (bunching collects above it).
    hem: lowest fabric row on leg faces. baggy: 0..1, more stacking at ankles.
    folds: scales the depth of fine creases.
    """
    rnd = random.Random(f"{kind}/{part}/{face}/{seed}")
    m = _Map(size)
    w, h = size
    d = lambda v: int(v * folds)  # noqa: E731

    def jit(v, a):
        return v + rnd.uniform(-a, a)

    if face in "UD":
        m.edges(left=100, right=100, top=100, bottom=100, t=2)
        return m.result(broad_blur=5)

    if part == "torso":
        if face in "FB":
            m.edges(left=84, right=84, bottom=104 if kind == "shirt" else None)
            if kind == "shirt":
                m.ellipse((20, 4 if face == "F" else 0, 108, 70), 142)
                for side in (0, 1):
                    for i in range(3):
                        y0 = jit(20 + i * 9, 2)
                        pts = [(-3, y0), (jit(12 + i * 4, 2), y0 + 8 + i * 2), (jit(26 + i * 7, 3), y0 + 22 + i * 6)]
                        if side:
                            pts = [(w - x, y) for x, y in pts]
                        m.fold(pts, depth=d(52 - i * 8))
                for x in (jit(26, 6), jit(64, 6), jit(102, 6)):
                    m.fold([(x, h + 2), (jit(x, 3), h - 10), (jit(x, 5), h - jit(22, 4))], depth=d(34), hl=(2, 0))
            else:
                m.ellipse((8, 70, 120, 150), 146)
                for side in (0, 1):
                    for i in range(2):
                        pts = [(44 + i * 7, h + 2), (54 + i * 3, h - 7), (62, h - 12 - i * 5)]
                        if side:
                            pts = [(w - x, y) for x, y in pts]
                        m.fold(pts, depth=d(40), hl=(2, 0))
        else:
            m.rect((-PAD, -PAD, w + PAD, h + PAD), 116)
            m.ellipse((-20, -40, w + 20, 34), 84)
            m.edges(left=100, right=100)
        return m.result()

    # limbs
    inner = face == INNER[part]
    if inner:
        m.rect((-PAD, -PAD, w + PAD, h + PAD), 112)
    m.edges(left=94, right=94)

    if kind == "shirt":
        if not inner:
            m.ellipse((-6, -20, 70, 20), 146)
        end = sleeve_end
        if end > 70:
            ey = jit(60, 4)
            for i in range(2):
                y = ey + i * 7
                m.fold([(jit(6, 4), jit(y, 3)), (32, jit(y + 7, 2)), (jit(58, 4), jit(y - 2, 3))], depth=d(52))
        for i in range(3 if end > 70 else 2):
            y = jit(end - 5 - i * 7, 2)
            x0, x1 = rnd.uniform(-4, 18), rnd.uniform(46, 68)
            m.fold([(x0, y), ((x0 + x1) / 2, jit(y, 4)), (x1, jit(y, 3))], depth=d(44))
        if inner:
            for i in range(3):
                m.fold([(jit(2, 2), 4 + i * 8), (jit(22, 3), 14 + i * 9), (jit(44, 4), 26 + i * 10)], depth=d(46))
        return m.result()

    # legs
    if not inner:
        m.ellipse((10, -8, 54, 58), 146)
    if face in "FB":
        ix = inner_edge_x(part, face, w)
        sgn = -1 if ix else 1
        if face == "F":
            for i in range(3):
                m.fold([(ix, 1 + i * 7), (ix + sgn * jit(14, 3), 8 + i * 9), (ix + sgn * jit(30, 4), 14 + i * 12)],
                       depth=d(48 - i * 6))
        else:
            m.ellipse((-6, 54, w + 6, 82), 102)
            for i in range(2):
                y = 16 + i * 9
                m.fold([(ix, y), (ix + sgn * 20, jit(y + 6, 2)), (ix + sgn * jit(46, 4), jit(y + 2, 3))], depth=d(46))
    ky = jit(66, 4)
    for i in range(2):
        y = ky + i * 8
        m.fold([(jit(4, 4), jit(y, 3)), (32, jit(y + 6, 2)), (jit(60, 4), jit(y - 1, 3))], depth=d(44))
    for i in range(2 + int(round(baggy * 4))):
        y = jit(hem - 4 - i * (7 - 2 * baggy), 1.5)
        if y < 70:
            break
        x0, x1 = rnd.uniform(-4, 14), rnd.uniform(50, 68)
        m.fold([(x0, y), ((x0 + x1) / 2 + rnd.uniform(-10, 10), jit(y - 3, 3)), (x1, jit(y, 3))],
               depth=d(44 + 14 * baggy))
    return m.result()


def shade_garment(g, strength=0.8, seed=0, **kw):
    """Apply cloth shading to every face of a Garment in place."""
    for part in g.parts:
        part.map(lambda f, img: apply_shade(
            img, face_map(g.kind, part.name, f, img.size, seed=seed, **kw), strength))


def shade_face(img, shade, strength=1.0):
    return apply_shade(img, shade, strength)
