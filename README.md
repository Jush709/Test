# Roblox Classic Clothing Pack

111 original, ready-to-upload Roblox clothing items: **66 shirts, 36 pants and 9 T-shirts**.
All of them come from one Python generator, so you can rebrand or restyle the whole line in a
few seconds.

| | |
|---|---|
| ![Shirts](output/catalog-shirts.jpg) | ![Pants](output/catalog-pants.jpg) |
| ![Outfits](output/catalog-outfits.jpg) | ![T-Shirts](output/catalog-tshirts.jpg) |

## What's in `output/`

| Folder / file | What it is |
|---|---|
| `shirts/*.png` | 585×559 classic **Shirt** templates. Upload these files. |
| `pants/*.png` | 585×559 classic **Pants** templates. Upload these files. |
| `tshirts/*.png` | 512×512 classic **T-Shirt** graphics with transparent backgrounds. |
| `previews/*.jpg` | Front and back render of each item on a blocky avatar (not for upload). |
| `outfits/*.jpg` | 25 matching sets (hoodie + joggers, suits, scrubs, school uniforms, …). |
| `LISTINGS.md` / `listings.csv` | A name, description and suggested price for every file, ready to copy. |
| `catalog-*.jpg` | Contact sheets of everything. |

### Collections

- **Essentials Set**: pullover hoodies and matching joggers with sneakers in 6 colours,
  plus zip-up and cropped hoodies.
- **Formal**: tuxedos (3), business suits (3) and matching suit trousers with dress shoes.
- **Academy**: school-uniform blazers with crests, argyle sweater vests and pleated plaid skirts
  with knee socks.
- **Campus / Denim**: varsity jackets, denim jackets (one with a sherpa collar), baggy jeans,
  ripped skinny jeans.
- **Winter / Tactical / Rebel**: puffer jackets, camo field jackets, cargo pants, leather biker
  jackets and a goth lace-up mesh top.
- **Layers / Cozy / Y2K**: open flannel over a tee, cable-knit sweaters, skater layered tees,
  tie-dye and graphic tees, pajama pants.
- **Sport / Roleplay**: soccer kits, basketball jersey + shorts sets, track pants and medical
  scrubs (top + pants) in 4 colours.
- **T-Shirts**: retro sunset, pixel heart, good vibes, cherries, mountain badge, lightning bolt,
  kawaii boba, ringed planet and chrome star.

All artwork is original. There are no real brands, logos or characters, which Roblox moderation
rejects. The placeholder brand on the clothes is **ZYNTH**. Swap in your own name (see below).

## Uploading to Roblox

1. Open the Roblox **Creator Hub** and go to the classic clothing upload (Avatar items → Shirts /
   Pants / T-Shirts; Roblox moves this around, so search "upload classic clothing" if you can't
   find it). Upload as yourself or as a **group** if you want earnings to go to a group.
2. Pick the matching type (Shirt for `shirts/`, Pants for `pants/`, T-Shirt for `tshirts/`)
   and choose the PNG.
3. Paste the name and description from `output/LISTINGS.md`.
4. Pay the upload fee and submit, then wait for moderation to approve it.
5. Once it's approved, turn on **sale** and set a price.

**Check before you spend Robux.** Sources disagree on the current rules, and I couldn't reach
Roblox's own docs from where this was built:

- **Upload fee:** most 2026 guides say 10 Robux per classic shirt or pants. One snippet of Roblox's
  docs page showed a higher number. The upload dialog shows the real fee before it charges you.
- **Premium:** third-party guides say you need an active Roblox Premium subscription to put 2D
  clothing on sale.
- **Your share:** Roblox keeps a marketplace cut, so you get roughly 70% of each sale price.

See [create.roblox.com/docs/avatar/classic-clothing](https://create.roblox.com/docs/avatar/classic-clothing)
for the current official rules.

## Tips for actually making Robux

- **Don't upload all 111 at once.** Start with 10–15 likely sellers: the Essentials sets, the
  basic tees, baggy jeans, school uniform and scrubs (roleplay games drive a lot of sales), and
  the tuxedo. Add more colours of whatever sells.
- **Price low to start** (5–10 Robux, as suggested in the listings). Cheap items get bought, and
  sales push items up in search.
- **Sell matching sets.** Upload both halves of an outfit and mention the other half in each
  description (the listings already do this).
- **Use a group and a homestore.** Many sellers upload under a group and put the clothes in a
  small "homestore" experience, so players can try them on.
- Be patient. Classic clothing is a crowded market and earnings aren't guaranteed. Consistent
  uploads and good thumbnails matter more than any one item.

### About "UGC"

On Roblox, "UGC" usually means **3D accessories and layered clothing**. Those need 3D models
built in Blender (meshes, cages, textures) and have their own requirements and much higher
publishing costs. This pack is **classic 2D clothing**, the template-based shirts, pants and
T-shirts that most new creators start with. It needs only a PNG upload.

## Avatar compatibility

- **R6 and R15.** The templates use the standard layout, so they wrap both body types.
- Long sleeves stop just above the bottom of the arm, so R15 hands stay skin-coloured.
- Some pants include shoes (sneakers, dress shoes, Mary Janes) on the feet. The names say
  "+ Sneakers" or mention shoes where they apply.
- Crop tops, short sleeves, the tank top, the knee rips and the fishnet sleeves use transparency,
  so the avatar's skin tone shows through.

## Regenerating / customising

Requires Python 3.9+ with Pillow and numpy (`pip install -r requirements.txt`).

```bash
python3 generate.py                         # rebuild everything into ./output
python3 generate.py --brand NOVA            # print your own brand name on the clothes
python3 generate.py --only hoodie joggers   # only items whose file name contains these words
python3 -m unittest discover tests          # check every template is a valid upload
```

Every build checks each file: correct size, RGBA, and no paint outside the template regions.

To add a colourway, add an entry next to the existing ones in `roblox_clothing/catalog.py`. To
add a new design, write a function in `roblox_clothing/designs/shirts.py` or `pants.py`; the
helpers in `designs/common.py` handle fabric, trims, hoods, shoes and shading.

| Module | Purpose |
|---|---|
| `template.py` | Exact face coordinates of the 585×559 Roblox template |
| `garment.py` | Paints per face and assembles the final template image |
| `fx.py` | Procedural fabrics: heather, denim, plaid, camo, tie-dye, argyle, cable knit, mesh, fishnet |
| `shading.py` | Cloth folds, wrinkles and ambient occlusion per face |
| `details.py` | Zips, buttons, pockets, drawstrings, stitching, text |
| `designs/` | The shirt, pants and graphic designs |
| `preview.py` | Avatar previews and contact sheets |
