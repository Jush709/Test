"""Render front/back previews of a blocky (R6-style) avatar wearing templates.

Previews are built from the final 585x559 PNGs, so they show exactly what
was exported, including any transparent areas where skin shows through.
"""

from PIL import Image, ImageDraw, ImageFilter

from .details import font
from .fx import rgb, rgba, tone
from .template import LAYOUT

SKIN = (236, 192, 158)
BG_TOP = (246, 247, 250)
BG_BOTTOM = (226, 229, 236)
HEAD = (80, 70)


def _crop(img, part, face):
    x, y, w, h = LAYOUT[part][face]
    return img.crop((x, y, x + w, y + h))


def _layered(size, skin, layers):
    out = Image.new("RGBA", size, rgb(skin) + (255,))
    for lay in layers:
        if lay is not None:
            out.alpha_composite(lay.convert("RGBA").resize(size, Image.LANCZOS) if lay.size != size else lay)
    return out


def _head(face_front, skin):
    w, h = HEAD
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=22, fill=rgba(skin), outline=rgba(tone(skin, 0.85)))
    if face_front:
        eye = rgba((30, 30, 34))
        d.ellipse([24, 26, 31, 35], fill=eye)
        d.ellipse([w - 31, 26, w - 24, 35], fill=eye)
        d.arc([26, 34, w - 26, 54], 20, 160, fill=eye, width=3)
    return img


def view(shirt=None, pants=None, tshirt=None, side="front", skin=SKIN):
    """One unscaled view (256 x ~330 px) of the avatar."""
    front = side == "front"
    f = "F" if front else "B"
    # viewer's left-to-right order of arms/legs
    order = ("right", "left") if front else ("left", "right")
    tee = tshirt.resize((128, 128), Image.LANCZOS) if (tshirt is not None and front) else None

    torso = _layered((128, 128), skin, [
        _crop(pants, "torso", f) if pants else None,
        _crop(shirt, "torso", f) if shirt else None,
        tee,
    ])
    arms = [_layered((64, 128), skin, [_crop(shirt, p, f) if shirt else None]) for p in order]
    legs = [_layered((64, 128), skin, [_crop(pants, p, f) if pants else None]) for p in order]

    W, top = 256, HEAD[1] + 6
    img = Image.new("RGBA", (W, top + 256))
    img.alpha_composite(_head(front, skin), ((W - HEAD[0]) // 2, 2))
    img.alpha_composite(torso, (64, top))
    img.alpha_composite(arms[0], (0, top))
    img.alpha_composite(arms[1], (192, top))
    img.alpha_composite(legs[0], (64, top + 128))
    img.alpha_composite(legs[1], (128, top + 128))
    d = ImageDraw.Draw(img)
    gap = (0, 0, 0, 70)
    d.line([(64, top), (64, top + 127)], fill=gap)
    d.line([(191, top), (191, top + 127)], fill=gap)
    d.line([(128, top + 128), (128, top + 255)], fill=gap)
    return img


def _background(size):
    w, h = size
    bg = Image.new("RGBA", size)
    d = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)) + (255,))
    return bg


def render(shirt=None, pants=None, tshirt=None, title=None, subtitle=None, scale=2, skin=SKIN):
    """Front and back views side by side on a soft backdrop, optionally captioned."""
    views = [view(shirt, pants, tshirt, s, skin) for s in ("front", "back")]
    vw, vh = views[0].size
    margin, gutter = 28, 40
    cap = 54 if title else 0
    W = margin * 2 + vw * 2 + gutter
    H = margin * 2 + vh + 14 + cap
    canvas = _background((W, H))
    for i, v in enumerate(views):
        x = margin + i * (vw + gutter)
        y = margin
        sh = Image.new("RGBA", (W, H))
        ImageDraw.Draw(sh).ellipse([x + 40, y + vh - 8, x + vw - 40, y + vh + 12], fill=(0, 0, 0, 60))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
        canvas.alpha_composite(v, (x, y))
    d = ImageDraw.Draw(canvas)
    lbl = font(11, "bold")
    for i, s in enumerate(("FRONT", "BACK")):
        d.text((margin + i * (vw + gutter) + vw / 2, margin + vh + 12), s, font=lbl, fill=(130, 134, 145), anchor="mm")
    out = canvas.resize((W * scale, H * scale), Image.LANCZOS)
    if title:
        d = ImageDraw.Draw(out)
        y = (H - cap) * scale + 8
        d.text((W * scale / 2, y + 18), title, font=font(15 * scale, "bold"), fill=(28, 30, 38), anchor="mm")
        if subtitle:
            d.text((W * scale / 2, y + 18 + 17 * scale), subtitle, font=font(10 * scale, "regular"),
                   fill=(110, 114, 125), anchor="mm")
    return out


def contact_sheet(tiles, cols=5, tile_width=360, title=None):
    """Grid of preview images, each scaled to `tile_width`."""
    if not tiles:
        raise ValueError("no tiles")
    scaled = [t.resize((tile_width, int(t.height * tile_width / t.width)), Image.LANCZOS) for t in tiles]
    th = max(t.height for t in scaled)
    rows = (len(scaled) + cols - 1) // cols
    pad = 12
    head = 70 if title else 0
    sheet = Image.new("RGBA", (cols * (tile_width + pad) + pad, head + rows * (th + pad) + pad), (255, 255, 255, 255))
    if title:
        ImageDraw.Draw(sheet).text((sheet.width / 2, 38), title, font=font(30, "black"), fill=(24, 26, 32),
                                   anchor="mm")
    for i, t in enumerate(scaled):
        r, c = divmod(i, cols)
        sheet.alpha_composite(t, (pad + c * (tile_width + pad), head + pad + r * (th + pad)))
    return sheet
