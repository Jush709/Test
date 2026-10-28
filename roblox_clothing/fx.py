"""Procedural fabric textures and pixel helpers built on numpy + Pillow.

Every texture function takes a (width, height) size and returns an RGBA image.
"""

import math
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# ---------------------------------------------------------------- colours

def rgb(color):
    if isinstance(color, str):
        c = color.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in color[:3])


def rgba(color, alpha=255):
    return rgb(color) + (int(alpha),)


def tone(color, k):
    """k < 1 darkens towards black, k > 1 lightens towards white (2 = white)."""
    r = rgb(color)
    if k <= 1:
        return tuple(int(c * k) for c in r)
    t = min(k - 1, 1)
    return tuple(int(c + (255 - c) * t) for c in r)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- arrays

def _solid(size, color):
    w, h = size
    return np.broadcast_to(np.array(rgb(color), np.float32) / 255, (h, w, 3)).copy()


def to_image(arr, alpha=None):
    out = np.clip(arr * 255 + 0.5, 0, 255).astype(np.uint8)
    img = Image.fromarray(out, "RGB").convert("RGBA")
    if alpha is not None:
        img.putalpha(Image.fromarray(np.clip(alpha * 255 + 0.5, 0, 255).astype(np.uint8), "L"))
    return img


def to_array(img):
    return np.asarray(img.convert("RGBA"), np.float32) / 255


def _rng(seed):
    if not isinstance(seed, int):
        seed = zlib.crc32(str(seed).encode())
    return np.random.default_rng(seed)


def smooth_noise(size, cell, seed=0):
    """Value noise in [0, 1]: a random grid every `cell` px, bicubic upsampled.

    `cell` may be an (x, y) pair for stretched noise, e.g. vertical drapes.
    """
    w, h = size
    cx, cy = (cell, cell) if not isinstance(cell, tuple) else cell
    cx, cy = max(1, int(cx)), max(1, int(cy))
    gw, gh = math.ceil(w / cx) + 3, math.ceil(h / cy) + 3
    grid = Image.fromarray(_rng(seed).random((gh, gw)).astype(np.float32), "F")
    big = np.asarray(grid.resize((gw * cx, gh * cy), Image.BICUBIC), np.float32)
    return big[cy:cy + h, cx:cx + w]


def fbm(size, cell, seed=0, octaves=3):
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        c = tuple(max(1, v // 2 ** o) for v in cell) if isinstance(cell, tuple) else max(1, cell // 2 ** o)
        total = total + amp * smooth_noise(size, c, seed * 31 + o)
        norm += amp
        amp *= 0.5
    return total / norm


def grain(size, amount, seed=0, streak=0.5, streak_len=3):
    """Zero-mean luminance noise with short vertical flecks, like knit yarn."""
    w, h = size
    r = _rng(seed)
    n = r.normal(0, 1, (h, w))
    s = np.repeat(r.normal(0, 1, (h // streak_len + 1, w)), streak_len, axis=0)[:h]
    return ((n * (1 - streak) + s * streak) * amount).astype(np.float32)


def lum(img, factor):
    """Multiply an image's RGB by a per-pixel factor array (alpha kept)."""
    a = to_array(img)
    a[..., :3] = np.clip(a[..., :3] * factor[..., None], 0, 1)
    return to_image(a[..., :3], a[..., 3])


# ---------------------------------------------------------------- textures

def fabric(size, color, amount=0.035, seed=0, streak=0.5):
    """Plain jersey/fleece: flat colour with fine heathered grain."""
    return to_image(_solid(size, color) + grain(size, amount, seed, streak)[..., None])


def smooth(size, color, amount=0.012, seed=0, cell=10, mottle=0.04):
    """Low-grain fabric (satin, nylon, leather) with soft mottling."""
    m = (fbm(size, cell, seed) - 0.5) * mottle
    return to_image(_solid(size, color) * (1 + m[..., None]) + grain(size, amount, seed, 0.2)[..., None])


def ribbed(size, color, period=3, depth=0.16, seed=0):
    """Vertical rib knit for cuffs, hems and collars."""
    w, h = size
    x = np.arange(w, dtype=np.float32)
    prof = 0.5 + 0.5 * np.cos(2 * np.pi * x / period)
    k = (1 - depth * (1 - prof))[None, :] * np.ones((h, 1), np.float32)
    return to_image(_solid(size, color) * k[..., None] + grain(size, 0.02, seed)[..., None])


def denim(size, color, seed=0, offset=(0, 0)):
    """Twill-weave denim: diagonal wale, vertical slubs and speckle."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    xx = xx + offset[0]
    yy = yy + offset[1]
    twill = (((xx + yy) % 4) < 2).astype(np.float32) - 0.5
    r = _rng(seed)
    cols = r.normal(0, 1, w + offset[0] + 1)[offset[0]:offset[0] + w]
    slub = cols[None, :] * (0.6 + 0.4 * smooth_noise(size, 12, seed + 1))
    speck = r.normal(0, 1, (h, w))
    k = 1 + 0.11 * twill + 0.035 * slub + 0.03 * speck
    return to_image(_solid(size, color) * k[..., None])


def plaid(size, sett, offset=(0, 0), twill=0.32, seed=0):
    """Tartan woven from `sett`, a list of (colour, thread count) used for warp and weft."""
    seq = []
    for color, n in sett:
        seq += [rgb(color)] * int(n)
    seq = np.array(seq, np.float32) / 255
    period = len(seq)
    w, h = size
    xs = (np.arange(w) + offset[0]) % period
    ys = (np.arange(h) + offset[1]) % period
    warp = seq[xs][None, :, :]
    weft = seq[ys][:, None, :]
    yy, xx = np.mgrid[0:h, 0:w]
    t = np.where(((xx + yy + offset[0] + offset[1]) % 4) < 2, 0.5 + twill, 0.5 - twill)[..., None]
    arr = warp * t + weft * (1 - t)
    return to_image(arr * (1 + grain(size, 0.03, seed, 0.3)[..., None]))


def camo(size, colors, seed=0, cell=18, coverage=(0.56, 0.6, 0.64)):
    """Blotchy camouflage: each extra colour is a thresholded noise layer."""
    arr = _solid(size, colors[0])
    for i, c in enumerate(colors[1:]):
        n = fbm(size, cell, seed * 7 + i, 4)
        arr[n > coverage[min(i, len(coverage) - 1)]] = np.array(rgb(c), np.float32) / 255
    img = to_image(arr).filter(ImageFilter.GaussianBlur(0.5))
    return to_image(to_array(img)[..., :3] + grain(size, 0.03, seed)[..., None])


def tiedye(size, colors, center=None, arms=3, twist=0.05, seed=0):
    """Spiral tie-dye with crinkled white dye-resist lines."""
    w, h = size
    cx, cy = center if center else (w / 2, h / 2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = np.arctan2(yy - cy, xx - cx) / (2 * np.pi)
    rad = np.hypot(yy - cy, xx - cx)
    n = fbm(size, 20, seed, 3)
    t = (ang * arms + rad * twist + n * 0.7) % 1.0
    pal = np.array([rgb(c) for c in colors], np.float32) / 255
    k = len(pal)
    f = t * k
    i0 = np.floor(f).astype(int) % k
    i1 = (i0 + 1) % k
    fr = np.clip((f - np.floor(f) - 0.25) / 0.5, 0, 1)
    fr = fr * fr * (3 - 2 * fr)
    arr = pal[i0] * (1 - fr)[..., None] + pal[i1] * fr[..., None]
    crinkle = np.abs(((t * k) % 1.0) - 0.5) < 0.04 + 0.04 * fbm(size, 6, seed + 3)
    arr[crinkle] = arr[crinkle] * 0.4 + 0.6
    img = to_image(arr).filter(ImageFilter.GaussianBlur(0.8))
    return to_image(to_array(img)[..., :3] + grain(size, 0.025, seed)[..., None])


def argyle(size, c1, c2, line, cell=(32, 40), offset=(0, 0)):
    """Argyle diamonds in two colours with a thin dashed over-check."""
    w, h = size
    cw, ch = cell
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = xx + offset[0] + cw / 2
    y = yy + offset[1]
    a = x / cw + y / ch
    b = x / cw - y / ch
    cellv = (np.floor(a) + np.floor(b)) % 2
    arr = np.where(cellv[..., None] > 0, _solid(size, c1), _solid(size, c2))
    fa = np.abs((a + 0.5) % 1 - 0.5)
    fb = np.abs((b + 0.5) % 1 - 0.5)
    lw = 0.75 / cw
    dash = ((xx + yy) // 2 % 2) == 0
    on = ((fa < lw) | (fb < lw)) & dash
    arr[on] = np.array(rgb(line), np.float32) / 255
    return to_image(arr + grain(size, 0.025, 1)[..., None])


def cable_knit(size, color, period=32, cable=12, offset=0, seed=0):
    """Chunky sweater knit: stockinette columns with twisted rope cables (cable=0 for plain knit)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = xx + offset
    sx = x % 4
    sy = yy % 4
    k = 1 - 0.09 * (np.abs(sx - 1.5) / 1.5) ** 2 - 0.035 * (sy == 3)
    cx = (x % period) - period / 2
    in_cable = np.abs(cx) < cable / 2 if cable else np.zeros_like(cx, bool)
    rope = ((yy + np.abs(cx) * 1.3 * np.sign(cx + 0.01)) % 9) / 9
    rope_k = 0.9 + 0.15 * np.sin(np.pi * rope) - 0.1 * (np.abs(cx) / (max(cable, 1) / 2)) ** 2
    groove = (np.abs(np.abs(cx) - cable / 2) < 1.2) if cable else np.zeros_like(cx, bool)
    k = np.where(in_cable, rope_k, k)
    k = np.where(groove, 0.84, k)
    k = k + grain(size, 0.02, seed)
    return to_image(_solid(size, color) * k[..., None])


def mesh(size, color, period=3, depth=0.14, seed=0):
    """Athletic mesh: a grid of tiny dark holes."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    holes = ((xx % period) == 1) & ((yy % period) == 1)
    k = 1 - depth * holes + grain(size, 0.015, seed)
    return to_image(_solid(size, color) * k[..., None])


def fishnet(size, color, period=8, offset=(0, 0)):
    """Transparent diamond net (lets skin show through)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = xx + offset[0]
    y = yy + offset[1]
    da = np.abs(((x + y) % period) - period / 2)
    db = np.abs(((x - y) % period) - period / 2)
    line = np.clip(1.4 - np.minimum(period / 2 - da, period / 2 - db), 0, 1)
    return to_image(_solid(size, color), line * 0.95)


def stripes(size, colors, widths, vertical=False, offset=0):
    """Repeating flat stripes; `colors` and `widths` are matched lists."""
    w, h = size
    seq = []
    for c, n in zip(colors, widths):
        seq += [rgb(c)] * int(n)
    seq = np.array(seq, np.float32) / 255
    if vertical:
        idx = (np.arange(w) + offset) % len(seq)
        arr = np.broadcast_to(seq[idx][None, :, :], (h, w, 3)).copy()
    else:
        idx = (np.arange(h) + offset) % len(seq)
        arr = np.broadcast_to(seq[idx][:, None, :], (h, w, 3)).copy()
    return to_image(arr + grain(size, 0.025, 2)[..., None])


def satin(size, color, seed=0, sheen=0.35, drape=(22, 90)):
    """Liquid satin: soft vertical drapes with bright, narrow highlights."""
    n = fbm(size, drape, seed, 2)
    k = 0.95 + (n - 0.5) * 0.22
    hl = np.clip((n - 0.6) / 0.12, 0, 1) ** 2 * sheen * 0.7
    arr = _solid(size, color) * k[..., None]
    arr = arr + (1 - arr) * hl[..., None]
    return to_image(arr + grain(size, 0.004, seed, 0)[..., None])


def mohair(size, color, seed=0, fuzz=0.10):
    """Fuzzy brushed knit: soft blotches plus stray light and dark fibres."""
    w, h = size
    base = _solid(size, color) * (1 + (fbm(size, 5, seed, 2) - 0.5) * 0.12)[..., None]
    img = to_image(base + grain(size, 0.02, seed, 0.3)[..., None])
    fib = Image.new("RGBA", size)
    d = ImageDraw.Draw(fib)
    r = _rng(seed + 7)
    light, dark = tone(color, 1.0 + fuzz * 3), tone(color, 1 - fuzz * 2.5)
    for _ in range(int(w * h / 9)):
        x, y = r.uniform(0, w), r.uniform(0, h)
        a = r.uniform(0, math.pi)
        ln = r.uniform(1.5, 3.5)
        c = light if r.random() < 0.6 else dark
        d.line([(x, y), (x + ln * math.cos(a), y + ln * math.sin(a))], fill=c + (int(r.uniform(50, 110)),))
    img.alpha_composite(fib.filter(ImageFilter.GaussianBlur(0.35)))
    return img


def gingham(size, color, ground=(255, 255, 255), check=6, offset=(0, 0)):
    """Two-colour gingham: solid where both threads are coloured, half-tone where one is."""
    return plaid(size, [(color, check), (ground, check)], offset=offset, twill=0.12)


def leopard(size, base=(214, 164, 98), spot=(150, 98, 46), ring=(34, 24, 18), seed=0, density=0.007):
    """Leopard rosettes: broken dark rings around darker centres."""
    w, h = size
    s = 3
    img = Image.new("RGBA", (w * s, h * s), rgba(base))
    d = ImageDraw.Draw(img)
    r = _rng(seed)
    for _ in range(int(w * h * density)):
        x, y = r.uniform(-4, w + 4) * s, r.uniform(-4, h + 4) * s
        rx, ry = r.uniform(3.2, 5.0) * s, r.uniform(2.6, 4.0) * s
        d.ellipse([x - rx * 0.6, y - ry * 0.6, x + rx * 0.6, y + ry * 0.6], fill=rgba(spot))
        a0 = r.uniform(0, 360)
        for k in range(int(r.integers(2, 4))):
            start = a0 + k * 120 + r.uniform(-20, 20)
            d.arc([x - rx, y - ry, x + rx, y + ry], start, start + r.uniform(70, 105), fill=rgba(ring),
                  width=int(1.8 * s))
    out = img.resize(size, Image.LANCZOS)
    return to_image(to_array(out)[..., :3] + grain(size, 0.02, seed)[..., None])


def cow(size, base=(250, 250, 248), spot=(26, 26, 28), seed=0, cell=30):
    """Cow print: big soft-edged blobs."""
    n = fbm(size, cell, seed, 3)
    m = np.clip((n - 0.58) / 0.03, 0, 1)[..., None]
    arr = _solid(size, base) * (1 - m) + _solid(size, spot) * m
    return to_image(arr + grain(size, 0.015, seed)[..., None])


def print_pattern(size, base, motif, spacing=(16, 16), seed=0, ground=None, jitter=1.5):
    """Ditsy all-over print: `motif(draw, x, y, s, rnd)` stamped on a half-drop grid.

    Motifs draw in final-pixel units multiplied by `s` (the supersampling factor).
    """
    w, h = size
    s = 4
    img = ground(size) if ground else fabric(size, base, 0.012, seed)
    big = Image.new("RGBA", (w * s, h * s))
    d = ImageDraw.Draw(big)
    r = _rng(seed)
    sx, sy = spacing
    for j in range(-1, h // sy + 2):
        for i in range(-1, w // sx + 2):
            x = i * sx + (sx / 2 if j % 2 else 0) + r.uniform(-jitter, jitter)
            y = j * sy + r.uniform(-jitter, jitter)
            motif(d, x * s, y * s, s, r)
    img.alpha_composite(big.resize(size, Image.LANCZOS))
    return img


# small motifs for print_pattern ------------------------------------------------

def _heart_pts(x, y, r, n=28):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        hx = 16 * math.sin(t) ** 3
        hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x + hx * r / 16, y + hy * r / 16))
    return pts


def motif_heart(color):
    def draw(d, x, y, s, r):
        d.polygon(_heart_pts(x, y, 2.6 * s), fill=rgba(color))
    return draw


def motif_flower(petal, center=(255, 214, 90), size=1.0):
    def draw(d, x, y, s, r):
        k = s * size
        for a in range(5):
            ang = math.radians(a * 72 - 90 + r.uniform(0, 30))
            px, py = x + 1.9 * k * math.cos(ang), y + 1.9 * k * math.sin(ang)
            d.ellipse([px - 1.5 * k, py - 1.5 * k, px + 1.5 * k, py + 1.5 * k], fill=rgba(petal))
        d.ellipse([x - 1.1 * k, y - 1.1 * k, x + 1.1 * k, y + 1.1 * k], fill=rgba(center))
    return draw


def motif_cherry(red=(214, 28, 48), stem=(60, 120, 50)):
    def draw(d, x, y, s, r):
        d.line([(x - 1.4 * s, y + 1.2 * s), (x + 0.4 * s, y - 2.6 * s), (x + 1.8 * s, y + 1.6 * s)],
               fill=rgba(stem), width=max(1, int(0.6 * s)))
        d.ellipse([x + 0.4 * s, y - 3.2 * s, x + 2.2 * s, y - 2.2 * s], fill=rgba(stem))
        for cx, cy in ((x - 1.6 * s, y + 1.8 * s), (x + 1.8 * s, y + 2.2 * s)):
            d.ellipse([cx - 1.6 * s, cy - 1.6 * s, cx + 1.6 * s, cy + 1.6 * s], fill=rgba(red))
            d.ellipse([cx - 0.9 * s, cy - 1.0 * s, cx - 0.2 * s, cy - 0.3 * s], fill=(255, 255, 255, 170))
    return draw


def motif_strawberry(red=(232, 46, 64), leaf=(66, 150, 70)):
    def draw(d, x, y, s, r):
        d.polygon([(x - 2.4 * s, y - 1.0 * s), (x + 2.4 * s, y - 1.0 * s), (x + 1.2 * s, y + 2.4 * s),
                   (x, y + 3.2 * s), (x - 1.2 * s, y + 2.4 * s)], fill=rgba(red))
        d.ellipse([x - 2.5 * s, y - 2.0 * s, x + 2.5 * s, y + 0.6 * s], fill=rgba(red))
        for dx, dy in ((-1, 0.2), (1, 0.3), (0, 1.4), (-0.7, 2.2), (0.8, 2.0), (0, -0.6)):
            d.point([(x + dx * s, y + dy * s)], fill=(255, 236, 150, 255))
        d.polygon([(x - 2.0 * s, y - 1.6 * s), (x, y - 2.8 * s), (x + 2.0 * s, y - 1.6 * s), (x, y - 0.8 * s)],
                  fill=rgba(leaf))
    return draw


def motif_bow(color):
    def draw(d, x, y, s, r):
        d.polygon([(x, y), (x - 2.6 * s, y - 1.6 * s), (x - 2.6 * s, y + 1.6 * s)], fill=rgba(color))
        d.polygon([(x, y), (x + 2.6 * s, y - 1.6 * s), (x + 2.6 * s, y + 1.6 * s)], fill=rgba(color))
        d.line([(x, y), (x - 1.4 * s, y + 2.8 * s)], fill=rgba(color), width=int(0.8 * s))
        d.line([(x, y), (x + 1.4 * s, y + 2.8 * s)], fill=rgba(color), width=int(0.8 * s))
        d.ellipse([x - 0.8 * s, y - 0.8 * s, x + 0.8 * s, y + 0.8 * s], fill=rgba(tone(color, 0.8)))
    return draw


def motif_star(color):
    def draw(d, x, y, s, r):
        pts = []
        for i in range(10):
            rr = (2.8 if i % 2 == 0 else 1.2) * s
            a = math.radians(-90 + i * 36)
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        d.polygon(pts, fill=rgba(color))
    return draw


# ---------------------------------------------------------------- masks & compositing

def keep_rows(img, y0, y1):
    """Return a copy with everything outside rows [y0, y1) made transparent."""
    out = img.copy()
    a = np.asarray(out.getchannel("A")).copy()
    a[:max(0, int(y0))] = 0
    a[int(y1):] = 0
    out.putalpha(Image.fromarray(a))
    return out


def cut(img, mask):
    """Make `img` transparent wherever the L-mode `mask` is white (in place)."""
    a = np.asarray(img.getchannel("A"), np.float32)
    m = np.asarray(mask, np.float32) / 255
    img.putalpha(Image.fromarray((a * (1 - m)).astype(np.uint8)))


def clip_to(layer, base):
    """Limit `layer`'s alpha to the coverage of `base` (same size)."""
    la = np.asarray(layer.getchannel("A"), np.float32)
    ba = np.asarray(base.getchannel("A"), np.float32) / 255
    out = layer.copy()
    out.putalpha(Image.fromarray((la * ba).astype(np.uint8)))
    return out


def shadow_of(layer, offset=(0, 2), blur=1.5, opacity=0.45, color=(0, 0, 0)):
    """Soft drop shadow image shaped like `layer`'s alpha."""
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new("RGBA", layer.size, rgb(color) + (0,))
    sh.putalpha(a.point(lambda v: int(v * opacity)))
    out = Image.new("RGBA", layer.size)
    out.paste(sh, offset)
    return out


def apply_shade(img, shade, strength=1.0):
    """Light/darken `img` from an L-mode `shade` map where 128 is neutral."""
    a = to_array(img)
    s = (np.asarray(shade, np.float32) / 255 - 0.5) * 2 * strength
    s = np.clip(s, -1, 1)[..., None]
    c = a[..., :3]
    c = c + c * np.minimum(s, 0) + (1 - c) * np.maximum(s, 0) * 0.55
    return to_image(c, a[..., 3])
