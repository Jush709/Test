"""A shirt or pants texture held as one image per template face."""

from PIL import Image, ImageDraw

from .template import LAYOUT, SIZE, WRAP


def over(base, layer, xy=(0, 0)):
    """Alpha-composite `layer` onto `base` in place; `layer` may hang off the edges."""
    if layer.size != base.size or tuple(xy) != (0, 0):
        canvas = Image.new("RGBA", base.size)
        canvas.paste(layer, (int(xy[0]), int(xy[1])))
        layer = canvas
    base.alpha_composite(layer)


class Part:
    """One box of the template (torso, right limb or left limb)."""

    def __init__(self, name):
        self.name = name
        self.rects = LAYOUT[name]
        self.faces = {f: Image.new("RGBA", (w, h)) for f, (_, _, w, h) in self.rects.items()}

    @property
    def sides(self):
        return WRAP[self.name]

    @property
    def strip_width(self):
        return sum(self.faces[f].width for f in self.sides)

    def offset(self, face):
        """x offset of a side face inside the wrap strip."""
        x = 0
        for f in self.sides:
            if f == face:
                return x
            x += self.faces[f].width
        raise KeyError(face)

    def size(self, face):
        return self.faces[face].size

    def draw(self, face):
        return ImageDraw.Draw(self.faces[face])

    def over(self, face, layer, xy=(0, 0)):
        over(self.faces[face], layer, xy)

    def over_strip(self, strip):
        """Composite a wrap-strip image (strip_width wide) across the four side faces."""
        for f in self.sides:
            x = self.offset(f)
            w, h = self.faces[f].size
            over(self.faces[f], strip.crop((x, 0, x + w, h)))

    def map(self, fn, faces=None):
        """Overwrite each face in place with fn(face_name, image), so references stay valid."""
        for f in faces or self.faces:
            img = self.faces[f]
            img.paste(fn(f, img), (0, 0))


class Garment:
    """Shirt (torso + arms) or pants (torso + legs)."""

    def __init__(self, kind):
        assert kind in ("shirt", "pants")
        self.kind = kind
        self.torso = Part("torso")
        self.right = Part("right")
        self.left = Part("left")

    @property
    def parts(self):
        return (self.torso, self.right, self.left)

    @property
    def limbs(self):
        return (self.right, self.left)

    def image(self):
        out = Image.new("RGBA", SIZE)
        for part in self.parts:
            for f, (x, y, _, _) in part.rects.items():
                out.paste(part.faces[f], (x, y))
        return out
