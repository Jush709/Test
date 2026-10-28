"""Every sellable item: design function, colourway and Marketplace listing copy."""

from dataclasses import dataclass, field
from typing import Callable, Optional

from PIL import Image

from .designs import pants as P
from .designs import shirts as S
from .designs.graphics import GRAPHICS


@dataclass
class Item:
    slug: str
    kind: str  # "shirt", "pants" or "tshirt"
    name: str
    description: str
    price: int
    build: Callable  # build(brand) -> PIL image
    pair: Optional[str] = None  # slug shown with this item in its preview
    collection: str = ""
    keywords: list = field(default_factory=list)


ITEMS = []
OUTFITS = []  # (title, [slugs])


def add(slug, kind, name, desc, price, build, pair=None, collection="", keywords=()):
    ITEMS.append(Item(slug, kind, name, desc, price, build, pair, collection, list(keywords)))


def padded(img, scale=0.84):
    """Shrink a T-shirt graphic onto a transparent canvas so it keeps a margin on the torso."""
    out = Image.new("RGBA", img.size)
    w, h = int(img.width * scale), int(img.height * scale)
    out.alpha_composite(img.resize((w, h), Image.LANCZOS), ((img.width - w) // 2, (img.height - h) // 2))
    return out


def garment(fn, palette, **kw):
    return lambda brand: fn(palette, brand, **kw).image()


WHITE_KICKS = {"upper": (246, 246, 246), "sole": (218, 218, 222), "accent": (226, 226, 230)}
BLACK_KICKS = {"upper": (34, 34, 38), "sole": (245, 245, 245), "accent": (60, 60, 66), "lace": (40, 40, 44)}

# ------------------------------------------------------------------ basics

for key, label, tee, ink in (("white", "White", (244, 244, 242), (30, 30, 34)),
                             ("black", "Black", (30, 30, 34), (240, 240, 240))):
    add(f"basic-tee-{key}", "shirt", f"Basic Tee - {label}",
        f"Clean {label.lower()} short sleeve t-shirt with a ribbed crew neck and soft cotton shading. "
        "The everyday base layer that goes with everything.", 5,
        garment(S.graphic_tee, {"tee": tee, "ink": ink}), pair="baggy-jeans-mid-wash", collection="Basics",
        keywords=["basic", "plain", "tee", "t-shirt", "aesthetic"])

# ------------------------------------------------------------------ hoodies + joggers sets

HOODIE_COLOURS = [
    ("jet-black", "Jet Black", {"base": (30, 30, 34), "print": (236, 236, 236), "back_print": (236, 236, 236),
                                "string": (228, 228, 228)}),
    ("heather-grey", "Heather Grey", {"base": (176, 178, 182), "grain": 0.03, "print": (44, 44, 48),
                                      "back_print": (44, 44, 48), "string": (248, 248, 248)}),
    ("cream", "Cream", {"base": (236, 227, 210), "print": (128, 104, 82), "back_print": (128, 104, 82),
                        "string": (214, 202, 184)}),
    ("sage", "Sage Green", {"base": (152, 172, 146), "print": (246, 246, 240), "back_print": (246, 246, 240),
                            "string": (244, 244, 238)}),
    ("baby-pink", "Baby Pink", {"base": (246, 196, 208), "print": (176, 84, 116), "back_print": (176, 84, 116),
                                "string": (255, 255, 255)}),
    ("navy", "Navy", {"base": (34, 44, 76), "print": (238, 238, 238), "back_print": (238, 238, 238),
                      "string": (236, 236, 236)}),
]

for key, label, pal in HOODIE_COLOURS:
    add(f"essential-hoodie-{key}", "shirt", f"Essential Hoodie - {label}",
        f"Heavyweight {label.lower()} pullover hoodie with hood, drawstrings, kangaroo pocket, ribbed cuffs and "
        "a minimal logo. Pair it with the matching joggers for the full set.", 8,
        garment(S.hoodie, pal), pair=f"essential-joggers-{key}", collection="Essentials Set",
        keywords=["hoodie", "streetwear", "cozy", "matching set"])
    jog = {"base": pal["base"], "grain": pal.get("grain", 0.022), "print": pal["print"]}
    add(f"essential-joggers-{key}", "pants", f"Essential Joggers - {label}",
        f"Relaxed {label.lower()} fleece joggers with a drawstring waist, stacked ribbed cuffs and clean white "
        "sneakers. Matches the Essential Hoodie.", 8,
        garment(P.joggers, jog, shoes=WHITE_KICKS), pair=f"essential-hoodie-{key}", collection="Essentials Set",
        keywords=["joggers", "sweatpants", "shoes", "matching set"])
    OUTFITS.append((f"Essentials Set - {label}", [f"essential-hoodie-{key}", f"essential-joggers-{key}"]))

for key, label, base in (("charcoal", "Charcoal", (62, 64, 70)), ("forest", "Forest Green", (40, 74, 54)),
                         ("maroon", "Maroon", (108, 30, 44))):
    add(f"zip-hoodie-{key}", "shirt", f"Zip Up Hoodie - {label}",
        f"Full-zip {label.lower()} hoodie with silver zipper, side pockets, hood and drawstrings.", 8,
        garment(S.hoodie, {"base": base, "print": (236, 236, 236), "string": (236, 236, 236)}, zip_up=True),
        pair="baggy-jeans-dark-wash", collection="Essentials", keywords=["zip up", "hoodie", "jacket"])

for key, label, base, ink in (("lilac", "Lilac", (204, 184, 236), (112, 84, 160)),
                              ("baby-blue", "Baby Blue", (172, 206, 240), (64, 104, 160)),
                              ("white", "White", (244, 244, 244), (40, 40, 44))):
    add(f"crop-hoodie-{key}", "shirt", f"Cropped Hoodie - {label}",
        f"Trendy cropped {label.lower()} hoodie with hood and drawstrings, finished with a ribbed hem above "
        "the waist.", 8, garment(S.hoodie, {"base": base, "print": ink}, crop=True),
        pair="cargo-pants-khaki", collection="Essentials", keywords=["crop top", "cropped hoodie", "y2k", "aesthetic"])

# ------------------------------------------------------------------ jackets

VARSITY = [
    ("navy", "Navy", {"body": (28, 38, 72), "sleeve": (238, 230, 210), "rib": (28, 38, 72), "stripe": (238, 230, 210),
                      "letter_edge": (214, 160, 52), "snap": (230, 222, 200)}),
    ("black", "Black", {"body": (26, 26, 28), "sleeve": (240, 240, 236), "rib": (26, 26, 28),
                        "stripe": (240, 240, 236), "letter_edge": (196, 30, 44), "snap": (236, 236, 232)}),
    ("red", "Red", {"body": (150, 26, 36), "sleeve": (236, 226, 204), "rib": (150, 26, 36), "stripe": (236, 226, 204),
                    "letter_edge": (30, 30, 34), "snap": (236, 226, 204), "back_number": "08"}),
    ("green", "Forest Green", {"body": (24, 70, 48), "sleeve": (236, 226, 204), "rib": (24, 70, 48),
                               "stripe": (236, 226, 204), "letter_edge": (214, 160, 52), "snap": (236, 226, 204),
                               "back_number": "99"}),
]
for key, label, pal in VARSITY:
    add(f"varsity-jacket-{key}", "shirt", f"Varsity Jacket - {label}",
        f"Classic {label.lower()} letterman jacket with cream leather sleeves, striped ribbed trims, snap "
        "buttons, a chenille letter patch and an arched back print.", 12,
        garment(S.varsity, pal), pair="baggy-jeans-light-wash", collection="Campus",
        keywords=["varsity", "letterman", "jacket", "preppy"])

for key, label, pal in (
        ("classic", "Classic Blue", {"denim": (58, 92, 140)}),
        ("light", "Light Wash", {"denim": (118, 154, 194)}),
        ("black", "Washed Black", {"denim": (48, 50, 56), "thread": (150, 150, 155), "button": (150, 150, 155)}),
        ("sherpa", "Sherpa Collar", {"denim": (70, 104, 150), "collar": (238, 230, 214)})):
    add(f"denim-jacket-{key}", "shirt", f"Denim Jacket - {label}",
        f"Trucker-style denim jacket ({label.lower()}) with contrast top-stitching, flap chest pockets, metal "
        "buttons and a realistic faded wash.", 10,
        garment(S.denim_jacket, pal), pair="cargo-pants-black-techwear", collection="Denim",
        keywords=["denim", "jean jacket", "vintage"])

for key, label, base in (("black", "Black", (24, 24, 28)), ("glacier", "Glacier Blue", (150, 196, 232)),
                         ("orange", "Safety Orange", (236, 112, 36)), ("lilac", "Lilac", (186, 160, 226))):
    add(f"puffer-jacket-{key}", "shirt", f"Puffer Jacket - {label}",
        f"Glossy quilted {label.lower()} puffer with stand collar, front zip and elastic cuffs. Winter ready.", 12,
        garment(S.puffer, {"base": base, "trim": (30, 30, 34)}), pair="cargo-pants-black-techwear",
        collection="Winter", keywords=["puffer", "winter", "jacket", "coat"])

for key, label, base in (("black", "Black", (26, 24, 26)), ("brown", "Brown", (92, 54, 36))):
    add(f"biker-jacket-{key}", "shirt", f"Leather Biker Jacket - {label}",
        f"Asymmetric-zip {label.lower()} leather moto jacket with wide lapels, belted hem, zipped cuffs and "
        "shiny highlights, worn over a white tee.", 12,
        garment(S.biker_jacket, {"leather": base}), pair="ripped-skinny-jeans-black", collection="Rebel",
        keywords=["leather jacket", "biker", "punk", "edgy"])

CAMO = {
    "woodland": ("Woodland Camo", [(86, 98, 64), (54, 64, 42), (112, 94, 66), (32, 34, 28)]),
    "urban": ("Urban Camo", [(150, 152, 156), (102, 104, 110), (62, 64, 68), (204, 204, 206)]),
    "desert": ("Desert Camo", [(196, 176, 138), (160, 132, 96), (122, 100, 72), (222, 208, 178)]),
}
for key, (label, cols) in CAMO.items():
    add(f"field-jacket-{key}", "shirt", f"Field Jacket - {label}",
        f"Military-style field jacket in {label.lower()} with four flap pockets, collar, button front and a "
        "sleeve patch.", 10, garment(S.field_jacket, {"camo": cols}),
        pair="cargo-pants-olive", collection="Tactical", keywords=["camo", "army", "military", "jacket"])

# ------------------------------------------------------------------ formal

TUX = [
    ("black", "Black Tie", {"jacket": (26, 26, 30), "lapel": (46, 46, 52), "neckwear": (16, 16, 18)}, "black"),
    ("midnight", "Midnight Navy", {"jacket": (24, 32, 58), "lapel": (16, 20, 36), "neckwear": (16, 20, 36)}, "navy"),
    ("white", "White Dinner", {"jacket": (238, 234, 226), "lapel": (232, 228, 220), "neckwear": (16, 16, 18),
                               "buttons": (30, 30, 30), "pocket_square": (20, 20, 22)}, "black"),
]
for key, label, pal, trousers in TUX:
    add(f"tuxedo-{key}", "shirt", f"Tuxedo - {label}",
        f"{label} tuxedo jacket with satin peak lapels, pleated dress shirt, bow tie and pocket square. "
        "Perfect for prom, weddings and roleplay.", 12, garment(S.suit, pal, neckwear="bow"),
        pair=f"suit-trousers-{trousers}", collection="Formal", keywords=["tuxedo", "suit", "formal", "prom"])
    OUTFITS.append((f"Tuxedo - {label}", [f"tuxedo-{key}", f"suit-trousers-{trousers}"]))

SUITS = [
    ("charcoal", "Charcoal", {"jacket": (58, 60, 66), "neckwear": (130, 24, 36), "tie_stripe": (210, 170, 70)}),
    ("navy", "Navy", {"jacket": (30, 42, 78), "neckwear": (146, 120, 60), "tie_stripe": (30, 42, 78)}),
    ("grey", "Light Grey", {"jacket": (154, 158, 166), "neckwear": (28, 28, 32), "tie_stripe": None}),
]
for key, label, pal in SUITS:
    add(f"business-suit-{key}", "shirt", f"Business Suit - {label}",
        f"Sharp {label.lower()} two-button suit jacket with notch lapels, white dress shirt, striped tie and "
        "pocket square.", 10, garment(S.suit, pal, neckwear="tie"), pair=f"suit-trousers-{key}",
        collection="Formal", keywords=["suit", "business", "office", "formal"])
    OUTFITS.append((f"Business Suit - {label}", [f"business-suit-{key}", f"suit-trousers-{key}"]))

for key, label, base in (("black", "Black", (26, 26, 30)), ("navy", "Navy", (30, 42, 78)),
                         ("charcoal", "Charcoal", (58, 60, 66)), ("grey", "Light Grey", (154, 158, 166))):
    add(f"suit-trousers-{key}", "pants", f"Suit Trousers - {label}",
        f"Pressed {label.lower()} dress trousers with a sharp crease, leather belt and polished dress shoes.", 8,
        garment(P.suit_trousers, {"base": base}), pair=f"business-suit-{key}" if key != "black" else "tuxedo-black",
        collection="Formal", keywords=["dress pants", "suit", "formal", "shoes"])

ACADEMY = [
    ("navy", "Navy", {"jacket": (28, 36, 68), "piping": (226, 186, 90), "crest": (120, 24, 36),
                      "neckwear": (120, 24, 36), "tie_stripe": (226, 186, 90), "buttons": (214, 176, 84)}),
    ("maroon", "Maroon", {"jacket": (100, 26, 40), "piping": (236, 226, 204), "crest": (28, 36, 68),
                          "neckwear": (28, 36, 68), "tie_stripe": (236, 226, 204), "buttons": (214, 176, 84)}),
    ("black", "Black", {"jacket": (28, 28, 32), "piping": (200, 30, 44), "crest": (200, 30, 44),
                        "neckwear": (200, 30, 44), "tie_stripe": (28, 28, 32), "buttons": (190, 192, 198)}),
]
SKIRT_FOR = {"navy": "red-tartan", "maroon": "navy-green", "black": "black-grey"}
for key, label, pal in ACADEMY:
    add(f"academy-blazer-{key}", "shirt", f"School Uniform Blazer - {label}",
        f"Private-school {label.lower()} blazer with contrast piping, embroidered crest, striped tie and "
        "white collared shirt. Made for school and roleplay games.", 10,
        garment(S.suit, pal, neckwear="tie", crest=True), pair=f"pleated-skirt-{SKIRT_FOR[key]}",
        collection="Academy", keywords=["school uniform", "blazer", "roleplay", "preppy"])
    OUTFITS.append((f"School Uniform - {label}", [f"academy-blazer-{key}", f"pleated-skirt-{SKIRT_FOR[key]}"]))

# ------------------------------------------------------------------ knits & layers

for key, label, sett, tee_print in (
        ("red-black", "Red Buffalo", [((178, 34, 34), 8), ((22, 22, 24), 8)], None),
        ("blue-green", "Blue & Green", [((32, 58, 96), 8), ((46, 108, 80), 6), ((32, 58, 96), 2), ((226, 196, 90), 1),
                                        ((32, 58, 96), 2), ((46, 108, 80), 6)], None),
        ("grey", "Charcoal Grey", [((92, 94, 100), 8), ((42, 44, 48), 6), ((190, 194, 200), 2), ((42, 44, 48), 6)],
         "lightning_bolt")):
    add(f"open-flannel-{key}", "shirt", f"Open Flannel + Tee - {label}",
        f"Unbuttoned {label.lower()} plaid flannel layered over a white tee, with chest pockets, collar and "
        "button cuffs.", 8, garment(S.flannel_open, {"sett": sett, "tee_print": tee_print}),
        pair="baggy-jeans-dark-wash", collection="Layers", keywords=["flannel", "plaid", "grunge", "layered"])

for key, label, base in (("oatmeal", "Oatmeal", (214, 196, 168)), ("forest", "Forest Green", (46, 84, 60)),
                         ("burgundy", "Burgundy", (110, 32, 46)), ("cream", "Cream", (240, 232, 214))):
    add(f"cable-knit-sweater-{key}", "shirt", f"Cable Knit Sweater - {label}",
        f"Chunky {label.lower()} cable knit sweater with rope cables, ribbed crew neck, cuffs and hem.", 8,
        garment(S.cable_sweater, {"base": base}), pair="baggy-jeans-light-wash", collection="Cozy",
        keywords=["sweater", "knit", "cozy", "fall"])

for key, label, argyle, tie in (("navy", "Navy Argyle", ((30, 42, 78), (60, 80, 130), (226, 226, 230)), (130, 24, 36)),
                                ("beige", "Beige Argyle", ((196, 172, 136), (150, 118, 84), (250, 246, 236)), None)):
    add(f"sweater-vest-{key}", "shirt", f"Preppy Sweater Vest - {label}",
        f"{label} sweater vest over a crisp white collared shirt{' and tie' if tie else ''}. Smart, preppy "
        "and school-ready.", 8, garment(S.sweater_vest, {"argyle": argyle, "tie": tie}),
        pair="pleated-skirt-navy-green" if key == "navy" else "suit-trousers-charcoal", collection="Academy",
        keywords=["sweater vest", "argyle", "preppy", "school"])

for key, label, tee, stripes, graphic in (
        ("white", "White & Black", (244, 244, 242), [(28, 28, 32), (244, 244, 242)], "chrome_star"),
        ("black", "Black & Red", (30, 30, 34), [(196, 30, 44), (30, 30, 34)], "pixel_heart")):
    add(f"skater-layered-tee-{key}", "shirt", f"Skater Layered Tee - {label}",
        f"Short sleeve graphic tee layered over striped long sleeves ({label.lower()}). Y2K skater energy.", 8,
        garment(S.layered_tee, {"tee": tee, "stripes": stripes, "graphic": graphic,
                                "ink": (30, 30, 34) if key == "white" else (240, 240, 240)}),
        pair="baggy-jeans-light-wash", collection="Y2K", keywords=["skater", "y2k", "striped", "layered"])

add("lace-up-mesh-top", "shirt", "Lace Up Mesh Top - Goth",
    "Black lace-up top with fishnet sleeves, square neckline and a silver crescent chain necklace.", 8,
    garment(S.mesh_top, {"base": (22, 22, 26)}), pair="ripped-skinny-jeans-black", collection="Rebel",
    keywords=["goth", "emo", "fishnet", "grunge"])

# ------------------------------------------------------------------ graphic tees

for key, label, pal in (
        ("retro-sunset", "Retro Sunset Tee", {"tee": (28, 28, 34), "graphic": "retro_sunset"}),
        ("ringed-planet", "Cosmic Planet Tee", {"tee": (28, 36, 70), "graphic": "ringed_planet"}),
        ("rainbow-tie-dye", "Rainbow Tie Dye Tee",
         {"tee": (240, 240, 240), "tiedye": [(255, 92, 120), (255, 170, 60), (255, 232, 90), (80, 200, 140),
                                             (70, 150, 240), (160, 100, 230)], "chest_text": "GOOD VIBES",
          "ink": (30, 24, 48)}),
        ("pastel-tie-dye", "Pastel Tie Dye Tee",
         {"tee": (240, 240, 240), "tiedye": [(255, 190, 210), (200, 186, 255), (176, 226, 255), (190, 245, 214)],
          "graphic": "boba", "graphic_width": 54, "ink": (110, 90, 150)})):
    add(f"tee-{key}", "shirt", label,
        f"Oversized short sleeve tee with an original {label.replace(' Tee', '').lower()} design.", 6,
        garment(S.graphic_tee, pal), pair="baggy-jeans-mid-wash", collection="Graphic Tees",
        keywords=["graphic tee", "aesthetic", "t-shirt"])

# ------------------------------------------------------------------ sports & work

for key, label, pal in (("royal", "Royal Blue", {"base": (30, 80, 200), "accent": (250, 250, 250),
                                                 "text": (250, 250, 250), "number": "10"}),
                        ("red", "Red Stripe", {"base": (200, 30, 40), "accent": (20, 20, 24), "text": (250, 250, 250),
                                               "pinstripe": (150, 20, 30), "number": "7"}),
                        ("green", "Green & Gold", {"base": (20, 120, 70), "accent": (240, 196, 60),
                                                   "text": (250, 250, 250), "number": "9"})):
    add(f"soccer-jersey-{key}", "shirt", f"Soccer Jersey - {label}",
        f"{label} football kit with V-neck collar, side panels, sleeve stripes and a big number on the back.", 8,
        garment(S.soccer_jersey, pal), pair="track-pants-black", collection="Sport",
        keywords=["soccer", "football", "jersey", "sports"])

BALL = [("purple-gold", "Purple & Gold", {"base": (86, 40, 140), "trim": (246, 190, 40), "number": "24"},
         {"base": (86, 40, 140), "panel": (246, 190, 40)}),
        ("red", "Red", {"base": (196, 26, 40), "trim": (250, 250, 250), "number": "23"},
         {"base": (196, 26, 40), "panel": (250, 250, 250)}),
        ("black", "Black & White", {"base": (26, 26, 30), "trim": (250, 250, 250), "number": "0"},
         {"base": (26, 26, 30), "panel": (250, 250, 250)})]
for key, label, top, bottom in BALL:
    add(f"basketball-jersey-{key}", "shirt", f"Basketball Jersey - {label}",
        f"{label} mesh basketball tank with an arched team name and big front and back numbers.", 8,
        garment(S.basketball_jersey, top), pair=f"basketball-shorts-{key}", collection="Sport",
        keywords=["basketball", "jersey", "tank top", "sports"])
    add(f"basketball-shorts-{key}", "pants", f"Basketball Shorts - {label}",
        f"{label} mesh basketball shorts with side panels, drawstring waist, crew socks and sneakers.", 8,
        garment(P.basketball_shorts, bottom), pair=f"basketball-jersey-{key}", collection="Sport",
        keywords=["basketball", "shorts", "sports", "shoes"])
    OUTFITS.append((f"Basketball Set - {label}", [f"basketball-jersey-{key}", f"basketball-shorts-{key}"]))

for key, label, base in (("ceil-blue", "Ceil Blue", (116, 160, 210)), ("navy", "Navy", (34, 48, 86)),
                         ("wine", "Wine", (112, 28, 52)), ("teal", "Teal", (20, 128, 130))):
    add(f"scrubs-top-{key}", "shirt", f"Medical Scrubs Top - {label}",
        f"{label} V-neck scrubs top with chest pocket, pen and ID badge. For hospital and doctor roleplay.", 6,
        garment(S.scrubs_top, {"base": base}), pair=f"scrubs-pants-{key}", collection="Roleplay",
        keywords=["scrubs", "doctor", "nurse", "hospital", "roleplay"])
    add(f"scrubs-pants-{key}", "pants", f"Medical Scrubs Pants - {label}",
        f"{label} scrubs pants with drawstring waist, cargo pocket and white sneakers.", 6,
        garment(P.scrubs_pants, {"base": base}), pair=f"scrubs-top-{key}", collection="Roleplay",
        keywords=["scrubs", "doctor", "nurse", "hospital", "roleplay"])
    OUTFITS.append((f"Scrubs - {label}", [f"scrubs-top-{key}", f"scrubs-pants-{key}"]))

# ------------------------------------------------------------------ pants

for key, label, pal, shoes in (
        ("light-wash", "Light Wash", {"denim": (128, 164, 204), "wash": 0.3}, WHITE_KICKS),
        ("mid-wash", "Mid Wash", {"denim": (74, 110, 162), "wash": 0.26}, None),
        ("dark-wash", "Dark Wash", {"denim": (34, 48, 82), "wash": 0.14}, None),
        ("black", "Washed Black", {"denim": (44, 46, 52), "wash": 0.18, "thread": (140, 140, 146),
                                   "button": (150, 150, 155)}, BLACK_KICKS)):
    extra = " and sneakers" if shoes else ""
    add(f"baggy-jeans-{key}", "pants", f"Baggy Jeans - {label}" + (" + Sneakers" if shoes else ""),
        f"Loose fit {label.lower()} jeans with realistic fading, whiskers, stitched pockets, belt loops and "
        f"stacked hems{extra}.", 8, garment(P.jeans, pal, baggy=1.0, shoes=shoes), pair="basic-tee-white",
        collection="Denim", keywords=["jeans", "baggy", "denim", "streetwear"])

for key, label, pal in (("light", "Light Wash", {"denim": (128, 164, 204), "wash": 0.3}),
                        ("black", "Black", {"denim": (40, 42, 48), "wash": 0.14, "thread": (130, 130, 136),
                                            "button": (150, 150, 155)})):
    add(f"ripped-skinny-jeans-{key}", "pants", f"Ripped Skinny Jeans - {label}",
        f"Slim {label.lower()} jeans with distressed knee rips, frayed threads and faded thighs.", 8,
        garment(P.jeans, pal, baggy=0.1, rips=True), pair="biker-jacket-black" if key == "black" else "basic-tee-black",
        collection="Denim", keywords=["ripped jeans", "skinny", "distressed", "grunge"])

for key, label, pal, kw in (
        ("black-techwear", "Black Techwear", {"base": (34, 34, 38), "belt": (18, 18, 20), "cuff": (28, 28, 32)},
         {"shoes": BLACK_KICKS, "straps": True}),
        ("khaki", "Khaki", {"base": (190, 168, 128)}, {}),
        ("olive", "Olive", {"base": (92, 100, 62), "cuff": (80, 88, 54)}, {"shoes": BLACK_KICKS}),
        ("camo", "Woodland Camo", {"base": (86, 98, 64), "camo": CAMO["woodland"][1]}, {})):
    add(f"cargo-pants-{key}", "pants", f"Cargo Pants - {label}",
        f"Utility cargo pants in {label.lower()} with flap cargo pockets, knee seams and back pockets.", 8,
        garment(P.cargo, pal, **kw), pair="crop-hoodie-white" if key == "khaki" else "basic-tee-black",
        collection="Tactical", keywords=["cargo", "streetwear", "techwear", "utility"])

for key, label, base, stripe in (("black", "Black", (28, 28, 32), (246, 246, 246)),
                                 ("navy", "Navy", (30, 42, 82), (246, 246, 246)),
                                 ("red", "Red", (190, 30, 40), (246, 246, 246))):
    add(f"track-pants-{key}", "pants", f"Track Pants - {label}",
        f"Retro {label.lower()} track pants with double side stripes, ankle zips and a drawstring waist.", 6,
        garment(P.track_pants, {"base": base, "stripe": stripe}), pair="soccer-jersey-royal", collection="Sport",
        keywords=["track pants", "tracksuit", "retro", "sports"])

for key, label, sett, socks in (
        ("red-tartan", "Red Tartan", [((170, 30, 40), 8), ((28, 34, 60), 4), ((170, 30, 40), 2), ((230, 200, 90), 1),
                                      ((170, 30, 40), 2), ((28, 34, 60), 4)], None),
        ("navy-green", "Navy & Green", [((30, 42, 78), 8), ((40, 92, 64), 6), ((30, 42, 78), 2), ((240, 240, 240), 1),
                                        ((30, 42, 78), 2), ((40, 92, 64), 6)], None),
        ("pink", "Pastel Pink", [((246, 186, 206), 8), ((255, 255, 255), 3), ((214, 130, 170), 2),
                                 ((255, 255, 255), 3)], (214, 130, 170)),
        ("black-grey", "Black & Grey", [((34, 34, 38), 8), ((120, 122, 128), 4), ((34, 34, 38), 2),
                                        ((200, 30, 44), 1), ((34, 34, 38), 2), ((120, 122, 128), 4)], None)):
    add(f"pleated-skirt-{key}", "pants", f"Pleated Skirt - {label}",
        f"{label} plaid pleated mini skirt with knee-high socks and Mary Jane shoes.", 8,
        garment(P.pleated_skirt, {"sett": sett, "sock_stripe": socks}), pair="sweater-vest-navy",
        collection="Academy", keywords=["skirt", "plaid", "school uniform", "aesthetic"])

for key, label, sett in (("red-buffalo", "Red Buffalo", [((178, 34, 34), 8), ((22, 22, 24), 8)]),
                         ("blue-plaid", "Blue Plaid", [((60, 90, 150), 8), ((230, 230, 236), 2), ((30, 44, 80), 6),
                                                       ((230, 230, 236), 2)])):
    add(f"pajama-pants-{key}", "pants", f"Cozy Pajama Pants - {label}",
        f"Soft {label.lower()} flannel pajama pants with a drawstring waist. Sleepover approved.", 5,
        garment(P.pajama_pants, {"sett": sett}), pair="cable-knit-sweater-cream", collection="Cozy",
        keywords=["pajamas", "pjs", "cozy", "plaid"])

OUTFITS += [
    ("Campus Fit", ["varsity-jacket-navy", "baggy-jeans-light-wash"]),
    ("Techwear Fit", ["puffer-jacket-black", "cargo-pants-black-techwear"]),
    ("Rebel Fit", ["biker-jacket-black", "ripped-skinny-jeans-black"]),
]

# ------------------------------------------------------------------ classic T-shirts (decals)

TEE_COPY = {
    "retro_sunset": ("Retro Sunset", "Synthwave sunset with neon grid. 80s vibes."),
    "pixel_heart": ("Pixel Heart", "8-bit pixel art heart. Wear it on any outfit."),
    "good_vibes": ("Good Vibes", "Bubbly gradient GOOD VIBES lettering with sparkles."),
    "cherries": ("Cherry Cute", "Glossy cartoon cherries with a little leaf."),
    "mountain_badge": ("Explore More Badge", "Outdoorsy sunset mountain badge."),
    "lightning_bolt": ("Lightning Bolt", "Glowing yellow lightning bolt."),
    "boba": ("Kawaii Boba", "Kawaii bubble tea with a smiley face and pearls."),
    "ringed_planet": ("Cosmic Planet", "Pastel ringed planet with twinkling stars."),
    "chrome_star": ("Chrome Star", "Y2K chrome sparkle star."),
}
for key, fn in GRAPHICS.items():
    title, blurb = TEE_COPY[key]
    add(f"tshirt-{key.replace('_', '-')}", "tshirt", f"{title} T-Shirt",
        f"{blurb} Transparent background, so it layers over any shirt or your avatar's body.", 5,
        (lambda f: (lambda brand: padded(f())))(fn), pair="basic-tee-white", collection="T-Shirts",
        keywords=["t-shirt", "graphic", "cute", "aesthetic"])


BY_SLUG = {i.slug: i for i in ITEMS}
assert len(BY_SLUG) == len(ITEMS), "duplicate slugs"
for _i in ITEMS:
    assert _i.pair is None or _i.pair in BY_SLUG, f"{_i.slug}: unknown pair {_i.pair}"
for _t, _slugs in OUTFITS:
    assert all(s in BY_SLUG for s in _slugs), _t
