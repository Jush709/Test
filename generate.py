#!/usr/bin/env python3
"""Build every clothing item, its preview, outfit previews and listing sheets.

    python3 generate.py                     # everything into ./output
    python3 generate.py --brand NOVA        # put your own brand name on the clothes
    python3 generate.py --only hoodie tux   # just items whose slug contains these words
"""

import argparse
import csv
import sys
import time
from pathlib import Path

from roblox_clothing import preview
from roblox_clothing.catalog import BY_SLUG, ITEMS, OUTFITS
from roblox_clothing.validate import problems

FOLDER = {"shirt": "shirts", "pants": "pants", "tshirt": "tshirts"}
KIND_LABEL = {"shirt": "Shirt", "pants": "Pants", "tshirt": "T-Shirt"}
DEFAULT_PANTS = "baggy-jeans-mid-wash"
DEFAULT_SHIRT = "basic-tee-white"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand", default="ZYNTH", help="brand name printed on the clothes (default ZYNTH)")
    ap.add_argument("--out", default="output", help="output folder (default ./output)")
    ap.add_argument("--only", nargs="*", default=None, help="build only slugs containing any of these words")
    ap.add_argument("--no-previews", action="store_true", help="skip preview renders")
    args = ap.parse_args()

    out = Path(args.out)
    brand = args.brand.upper()
    cache = {}

    def get(slug):
        if slug not in cache:
            cache[slug] = BY_SLUG[slug].build(brand)
        return cache[slug]

    items = [i for i in ITEMS if not args.only or any(w in i.slug for w in args.only)]
    if not items:
        sys.exit("no items match --only")
    t0 = time.time()
    failed = []
    for item in items:
        img = get(item.slug)
        bad = problems(img, item.kind)
        if bad:
            failed.append((item.slug, bad))
        path = out / FOLDER[item.kind] / f"{item.slug}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, optimize=True)
    print(f"built {len(items)} items in {time.time() - t0:.1f}s")

    if not args.no_previews:
        tiles = {"shirt": [], "pants": [], "tshirt": []}
        for item in items:
            tiles[item.kind].append(render_item(item, get))
            path = out / "previews" / f"{item.slug}.jpg"
            path.parent.mkdir(parents=True, exist_ok=True)
            tiles[item.kind][-1].convert("RGB").save(path, quality=86)
        outfit_tiles = []
        for title, slugs in OUTFITS:
            if args.only and not any(any(w in s for w in args.only) for s in slugs):
                continue
            kinds = {BY_SLUG[s].kind: get(s) for s in slugs}
            tile = preview.render(shirt=kinds.get("shirt"), pants=kinds.get("pants"), tshirt=kinds.get("tshirt"),
                                  title=title, subtitle=" + ".join(BY_SLUG[s].name for s in slugs))
            outfit_tiles.append(tile)
            path = out / "outfits" / f"{slugify(title)}.jpg"
            path.parent.mkdir(parents=True, exist_ok=True)
            tile.convert("RGB").save(path, quality=86)
        for kind, ts in tiles.items():
            if ts:
                preview.contact_sheet(ts, title=f"{brand} - {FOLDER[kind].upper()}").convert("RGB").save(
                    out / f"catalog-{FOLDER[kind]}.jpg", quality=88)
        if outfit_tiles:
            preview.contact_sheet(outfit_tiles, cols=4, title=f"{brand} - OUTFITS").convert("RGB").save(
                out / "catalog-outfits.jpg", quality=88)
        print(f"previews done in {time.time() - t0:.1f}s")

    write_listings(out, items)
    if failed:
        for slug, bad in failed:
            print(f"INVALID {slug}: {'; '.join(bad)}")
        sys.exit(1)
    print(f"all {len(items)} templates passed validation -> {out}/")


def render_item(item, get):
    pair = item.pair
    if item.kind == "shirt":
        pants = get(pair) if pair and BY_SLUG[pair].kind == "pants" else get(DEFAULT_PANTS)
        return preview.render(shirt=get(item.slug), pants=pants, title=item.name,
                              subtitle=f"Shirt  ·  {item.price} Robux")
    if item.kind == "pants":
        shirt = get(pair) if pair and BY_SLUG[pair].kind == "shirt" else get(DEFAULT_SHIRT)
        return preview.render(shirt=shirt, pants=get(item.slug), title=item.name,
                              subtitle=f"Pants  ·  {item.price} Robux")
    return preview.render(shirt=get(pair or DEFAULT_SHIRT), pants=get(DEFAULT_PANTS), tshirt=get(item.slug),
                          title=item.name, subtitle=f"T-Shirt  ·  {item.price} Robux")


def slugify(s):
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in s).replace("--", "-").strip("-")


def write_listings(out, items):
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "listings.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "type", "name", "description", "suggested_price_robux", "collection", "keywords"])
        for i in items:
            w.writerow([f"{FOLDER[i.kind]}/{i.slug}.png", KIND_LABEL[i.kind], i.name, i.description, i.price,
                        i.collection, ", ".join(i.keywords)])
    lines = ["# Listings", "",
             "Copy the name and description when you upload each file. Prices are suggestions.", ""]
    by_col = {}
    for i in items:
        by_col.setdefault(i.collection, []).append(i)
    for col, group in by_col.items():
        lines += [f"## {col}", "", "| Preview | Name | Type | Price | Description |", "|---|---|---|---|---|"]
        for i in group:
            lines.append(f"| [file]({FOLDER[i.kind]}/{i.slug}.png) · [preview](previews/{i.slug}.jpg) | {i.name} | "
                         f"{KIND_LABEL[i.kind]} | {i.price} | {i.description} |")
        lines.append("")
    (out / "LISTINGS.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
