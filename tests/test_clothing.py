"""Run with: python3 -m unittest discover tests"""

import unittest

from roblox_clothing.catalog import ITEMS
from roblox_clothing.template import LAYOUT, SIZE, WRAP
from roblox_clothing.validate import problems


class TemplateGeometry(unittest.TestCase):
    def test_faces_fit_canvas_without_overlap(self):
        rects = [r for faces in LAYOUT.values() for r in faces.values()]
        for x, y, w, h in rects:
            self.assertTrue(0 <= x and x + w <= SIZE[0] and 0 <= y and y + h <= SIZE[1])
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                overlap = a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]
                self.assertFalse(overlap, (a, b))

    def test_wrap_order_is_left_to_right(self):
        for part, faces in LAYOUT.items():
            row = sorted((r[0], f) for f, r in faces.items() if f in "FBLR")
            self.assertEqual("".join(f for _, f in row), WRAP[part])


class Catalog(unittest.TestCase):
    def test_names_fit_marketplace_limits(self):
        for item in ITEMS:
            self.assertLessEqual(len(item.name), 50, item.name)
            self.assertLessEqual(len(item.description), 1000, item.slug)

    def test_every_item_builds_a_valid_upload(self):
        for item in ITEMS:
            with self.subTest(item.slug):
                self.assertEqual(problems(item.build("TEST"), item.kind), [])


if __name__ == "__main__":
    unittest.main()
