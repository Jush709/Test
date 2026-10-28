"""Checks that an exported image is a valid Roblox classic clothing upload."""

import numpy as np

from .template import LAYOUT, SIZE, TSHIRT_SIZE


def problems(img, kind):
    """Return a list of human-readable problems (empty when the image is fine)."""
    out = []
    want = TSHIRT_SIZE if kind == "tshirt" else SIZE
    if img.size != want:
        out.append(f"size {img.size}, expected {want}")
    if img.mode != "RGBA":
        out.append(f"mode {img.mode}, expected RGBA")
    if out:
        return out
    alpha = np.asarray(img.getchannel("A"))
    if kind == "tshirt":
        if alpha.max() == 0:
            out.append("image is fully transparent")
        return out
    inside = np.zeros(alpha.shape, bool)
    for part, faces in LAYOUT.items():
        for face, (x, y, w, h) in faces.items():
            inside[y:y + h, x:x + w] = True
    if alpha[~inside].any():
        out.append("paint outside the template regions")
    x, y, w, h = LAYOUT["torso"]["F"]
    if alpha[y:y + h, x:x + w].mean() < 8:
        out.append("torso front is (almost) empty")
    return out
