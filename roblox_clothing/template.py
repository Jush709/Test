"""Geometry of the Roblox classic clothing template.

Shirts and pants share one 585x559 layout: a torso block at the top, the
right limb (arm on shirts, leg on pants) at the bottom left and the left limb
at the bottom right. Each block is an unfolded box: four side faces that wrap
around the part, plus an up (U) and a down (D) cap.

Faces are drawn as seen from outside the body, so the back (B) faces read
correctly when you look at the avatar from behind.
"""

SIZE = (585, 559)
TSHIRT_SIZE = (512, 512)

# face -> (x, y, width, height) on the 585x559 canvas
LAYOUT = {
    "torso": {
        "U": (231, 8, 128, 64),
        "R": (165, 74, 64, 128),
        "F": (231, 74, 128, 128),
        "L": (361, 74, 64, 128),
        "B": (427, 74, 128, 128),
        "D": (231, 204, 128, 64),
    },
    "right": {
        "U": (217, 289, 64, 64),
        "L": (19, 355, 64, 128),
        "B": (85, 355, 64, 128),
        "R": (151, 355, 64, 128),
        "F": (217, 355, 64, 128),
        "D": (217, 485, 64, 64),
    },
    "left": {
        "U": (308, 289, 64, 64),
        "F": (308, 355, 64, 128),
        "L": (374, 355, 64, 128),
        "B": (440, 355, 64, 128),
        "R": (506, 355, 64, 128),
        "D": (308, 485, 64, 64),
    },
}

# Side faces in the order they wrap around the part. This is also their
# left-to-right order on the template, so neighbouring seams line up.
WRAP = {"torso": "RFLB", "right": "LBRF", "left": "FLBR"}

# Limb side face that touches the body's centre line, and the one facing out.
INNER = {"right": "L", "left": "R"}
OUTER = {"right": "R", "left": "L"}


def inner_edge_x(part, face, width):
    """x coordinate of the edge of a limb's front/back face nearest the body's centre."""
    if face == "F":
        return width if part == "right" else 0
    if face == "B":
        return 0 if part == "right" else width
    raise ValueError("only front and back faces have an inner edge")
