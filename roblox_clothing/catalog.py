"""Every sellable item: design function, colourway and Marketplace listing copy.

The line is aimed at girls' avatar trends (coquette, Y2K, cottagecore, preppy,
soft girl, alt), with names that use the words players search for.
"""

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


def outfit(title, *slugs):
    OUTFITS.append((title, list(slugs)))


WHITE = (252, 252, 252)
PINK = (246, 170, 196)
HOT_PINK = (236, 96, 150)
BLACK = (26, 26, 30)
WHITE_KICKS = {"upper": (246, 246, 246), "sole": (218, 218, 222), "accent": (226, 226, 230)}
BLACK_KICKS = {"upper": (34, 34, 38), "sole": (245, 245, 245), "accent": (60, 60, 66), "lace": (40, 40, 44)}
PINK_CHUNKY = {"upper": (252, 252, 252), "sole": (250, 236, 242), "accent": (248, 190, 210)}

# ------------------------------------------------------------------ coquette

for key, label, pal in (
        ("baby-pink", "Baby Pink", {"base": (246, 196, 210), "bow": WHITE}),
        ("cream", "Cream", {"base": (242, 232, 214), "bow": HOT_PINK}),
        ("lavender", "Lavender", {"base": (206, 190, 236), "bow": WHITE}),
        ("black", "Black", {"base": (30, 28, 32), "bow": PINK, "trim": PINK})):
    add(f"bow-cardigan-{key}", "shirt", f"Coquette Bow Cardigan - {label}",
        f"Cute cropped {label.lower()} knit cardigan with satin bows down the front, lace trim and puff "
        "sleeves. Soft girl coquette aesthetic. Pair it with the Ruffle Skirt or Flare Jeans.", 8,
        garment(S.bow_cardigan, pal), pair="ruffle-skirt-pink" if key != "black" else "pleated-skirt-black-tights",
        collection="Coquette", keywords=["coquette", "cardigan", "bow", "soft girl", "cute"])

for key, label, pal in (
        ("champagne", "Champagne", {"base": (238, 222, 196), "lace": (252, 246, 236)}),
        ("black", "Black", {"base": (24, 24, 28), "lace": (44, 44, 50)}),
        ("blush", "Blush Pink", {"base": (246, 200, 210), "lace": (255, 240, 244)}),
        ("white", "White", {"base": (248, 246, 242), "lace": WHITE})):
    add(f"lace-cami-{key}", "shirt", f"Lace Trim Satin Cami - {label}",
        f"Silky {label.lower()} satin cami top with lace trim, thin straps and a tiny bow. Coquette, "
        "clean girl and date-night ready.", 7, garment(S.lace_cami, pal), pair="flare-jeans-light-wash",
        collection="Coquette", keywords=["cami", "satin", "lace", "coquette", "y2k"])

for key, label, pal in (
        ("ivory", "Ivory", {"base": (248, 244, 236), "bow": (238, 230, 216)}),
        ("black", "Black", {"base": (28, 28, 32)}),
        ("blush", "Blush", {"base": (244, 206, 212)}),
        ("burgundy", "Burgundy", {"base": (112, 28, 46)})):
    add(f"bow-blouse-{key}", "shirt", f"Satin Bow Blouse - {label}",
        f"Elegant {label.lower()} satin blouse with a big neck bow, balloon sleeves, frilled cuffs and "
        "pearl buttons. Old money and coquette vibes.", 8, garment(S.bow_blouse, pal),
        pair="wide-trousers-cream" if key != "ivory" else "wide-trousers-black",
        collection="Coquette", keywords=["blouse", "bow", "satin", "old money", "elegant"])

for key, label, pal in (
        ("pink", "Pink", {"base": (246, 196, 210), "lace": WHITE, "legwear": "lace_socks", "shoes": "mary_janes",
                          "shoe_bow": PINK}),
        ("pink-gingham", "Pink Gingham", {"base": (240, 150, 175), "fabric": "gingham", "lace": WHITE,
                                          "bow": (236, 96, 150), "legwear": "lace_socks", "shoes": "mary_janes",
                                          "shoe_bow": PINK}),
        ("black", "Black", {"base": (30, 28, 32), "lace": PINK, "bow": PINK, "legwear": "lace_socks",
                            "shoes": "mary_janes", "shoe_bow": PINK})):
    add(f"ruffle-skirt-{key}", "pants", f"Ruffle Mini Skirt + Lace Socks - {label}",
        f"Tiered {label.lower()} ruffle mini skirt with lace trim, a waist bow, frilly socks and Mary Jane "
        "shoes with bows.", 8, garment(P.ruffle_skirt, pal),
        pair=f"bow-cardigan-{'black' if key == 'black' else 'cream'}",
        collection="Coquette", keywords=["skirt", "ruffle", "coquette", "mary janes", "cute"])

outfit("Coquette Set - Baby Pink", "bow-cardigan-baby-pink", "ruffle-skirt-pink")
outfit("Coquette Set - Cream & Gingham", "bow-cardigan-cream", "ruffle-skirt-pink-gingham")
outfit("Coquette Set - Black", "bow-cardigan-black", "ruffle-skirt-black")

# ------------------------------------------------------------------ y2k

BABY_TEES = [
    ("sweet-cherry", "Sweet Cherry", {"base": (250, 250, 250), "trim": (236, 110, 140), "graphic": "cherries",
                                      "text": "SWEET CHERRY", "ink": (220, 60, 100)}),
    ("sweetheart", "Sweetheart", {"base": (248, 200, 214), "trim": (220, 40, 70), "graphic": "angel_heart",
                                  "graphic_width": 46, "text": "SWEETHEART", "ink": (220, 40, 70)}),
    ("lucky-star", "Lucky Star", {"base": BLACK, "trim": PINK, "graphic": "chrome_star", "text": "LUCKY STAR",
                                  "ink": PINK}),
    ("butterfly", "Butterfly", {"base": (182, 214, 246), "trim": WHITE, "graphic": "butterfly",
                                "text": "BUTTERFLY", "ink": (80, 100, 200)}),
    ("berry-sweet", "Berry Sweet", {"base": (214, 200, 244), "trim": WHITE, "graphic": "strawberry",
                                    "text": "BERRY SWEET", "ink": (130, 80, 190)}),
]
for key, label, pal in BABY_TEES:
    add(f"baby-tee-{key}", "shirt", f"Y2K Baby Tee - {label}",
        f"Fitted cropped baby tee with contrast trims and a cute {label.lower()} graphic. Y2K aesthetic "
        "basic for every outfit.", 6, garment(S.baby_tee, pal), pair="flare-jeans-light-wash",
        collection="Y2K", keywords=["baby tee", "y2k", "crop top", "cute", "aesthetic"])

for key, label, pal in (
        ("black-butterfly", "Black Butterfly", {"base": BLACK, "fabric": "satin", "graphic": "butterfly",
                                                "trim": (60, 60, 66)}),
        ("pink-rhinestone", "Pink Rhinestone", {"base": (246, 170, 200), "rhinestones": WHITE,
                                                "trim": (226, 130, 170)}),
        ("white-butterfly", "White Butterfly", {"base": (248, 248, 246), "graphic": "butterfly",
                                                "trim": (220, 220, 226)}),
        ("lilac-rhinestone", "Lilac Rhinestone", {"base": (200, 180, 236), "rhinestones": (236, 240, 250),
                                                  "trim": (170, 150, 210)})):
    add(f"halter-top-{key}", "shirt", f"Y2K Halter Top - {label}",
        f"Y2K halter crop top in {label.lower()}: bare shoulders, open back tied with a bow.", 7,
        garment(S.halter_top, pal), pair="cargo-pants-baby-pink" if "black" in key else "flare-jeans-light-wash",
        collection="Y2K", keywords=["halter", "y2k", "crop top", "butterfly", "baddie"])

for key, label, pal in (
        ("light-wash", "Light Wash + Heart Belt", {"denim": (128, 164, 204), "wash": 0.3, "belt": "heart"}),
        ("mid-wash", "Mid Wash + Studded Belt", {"denim": (74, 110, 162), "wash": 0.26, "belt": "studded"}),
        ("black", "Black + Chain Belt", {"denim": (40, 42, 48), "wash": 0.14, "thread": (140, 140, 146),
                                         "belt": "chain"}),
        ("pink", "Pink Denim", {"denim": (240, 160, 190), "wash": 0.25, "thread": (255, 255, 255),
                                "heart_pockets": (255, 255, 255), "button": (230, 230, 236)})):
    add(f"flare-jeans-{key}", "pants", f"Low Rise Flare Jeans - {label}",
        f"Y2K low rise flared jeans ({label.lower()}) with faded wash, whiskers and stitched back pockets.", 8,
        garment(P.jeans, pal, baggy=0.2, top=104, flared=True), pair="baby-tee-sweet-cherry",
        collection="Y2K", keywords=["flare jeans", "low rise", "y2k", "denim", "belt"])

for key, label, tee, stripes, graphic in (
        ("white", "White & Black", (244, 244, 242), [(28, 28, 32), (244, 244, 242)], "chrome_star"),
        ("black", "Black & Pink", (30, 30, 34), [PINK, (30, 30, 34)], "pixel_heart")):
    add(f"skater-layered-tee-{key}", "shirt", f"Skater Layered Tee - {label}",
        f"Short sleeve graphic tee layered over striped long sleeves ({label.lower()}). Y2K skater girl.", 7,
        garment(S.layered_tee, {"tee": tee, "stripes": stripes, "graphic": graphic,
                                "ink": (30, 30, 34) if key == "white" else (240, 240, 240)}),
        pair="pleated-skirt-black-tights", collection="Y2K", keywords=["skater", "y2k", "striped", "layered"])

outfit("Y2K Set - Sweet Cherry", "baby-tee-sweet-cherry", "flare-jeans-light-wash")
outfit("Y2K Set - Lucky Star", "baby-tee-lucky-star", "flare-jeans-black")
outfit("Y2K Set - Butterfly", "halter-top-black-butterfly", "cargo-pants-baby-pink")

# ------------------------------------------------------------------ cottagecore

for key, label, pal in (
        ("white", "White", {"base": (250, 248, 244), "lace": HOT_PINK, "trim": WHITE}),
        ("pink-gingham", "Pink Gingham", {"base": (240, 140, 170), "fabric": "gingham", "lace": (220, 40, 90)}),
        ("blue-gingham", "Blue Gingham", {"base": (110, 150, 220), "fabric": "gingham", "lace": (40, 70, 160)}),
        ("strawberry", "Strawberry Print", {"base": (252, 248, 246), "fabric": "print", "motif": "strawberry",
                                            "spacing": (14, 14), "lace": (220, 40, 70)})):
    add(f"milkmaid-top-{key}", "shirt", f"Milkmaid Corset Top - {label}",
        f"Cottagecore milkmaid top in {label.lower()} with a sweetheart neckline, lace-up corset front, puff "
        "sleeves and frilled hem.", 8, garment(S.milkmaid_top, pal), pair="denim-skirt-light-wash",
        collection="Cottagecore", keywords=["milkmaid", "cottagecore", "corset", "gingham", "puff sleeves"])

SUNDRESS = [
    ("yellow-daisy", "Yellow Daisy", {"base": (255, 226, 120), "fabric": "print", "motif": "flower",
                                      "motif_args": [WHITE], "tie": WHITE}),
    ("pink-floral", "Pink Floral", {"base": (248, 184, 204), "fabric": "print", "motif": "flower",
                                    "motif_args": [WHITE, (255, 214, 90), 0.9], "tie": WHITE}),
    ("blue-gingham", "Blue Gingham", {"base": (110, 150, 220), "fabric": "gingham", "tie": WHITE, "sleeves": 40}),
    ("cherry", "Cherry Print", {"base": (252, 250, 246), "fabric": "print", "motif": "cherry",
                                "spacing": (15, 15), "tie": (214, 28, 48)}),
]
for key, label, pal in SUNDRESS:
    add(f"sundress-top-{key}", "shirt", f"Sundress Top - {label}",
        f"Top half of the {label} sundress: square neck, straps, smocked back and ribbon waist bow. Wear it "
        "with the matching Sundress Skirt for the full dress.", 7, garment(S.sundress_top, pal),
        pair=f"sundress-skirt-{key}", collection="Cottagecore",
        keywords=["sundress", "dress", "cottagecore", "summer", "floral"])
    skirt = dict(pal, shoes="ballet", shoe_color=WHITE if key != "cherry" else (214, 28, 48),
                 shoe_bow=pal.get("tie"))
    add(f"sundress-skirt-{key}", "pants", f"Sundress Skirt - {label}",
        f"Flowy {label.lower()} midi skirt with a frilled hem and ballet flats. Matches the {label} Sundress Top.",
        7, garment(P.sundress_skirt, skirt), pair=f"sundress-top-{key}", collection="Cottagecore",
        keywords=["sundress", "dress", "skirt", "cottagecore", "floral"])
    outfit(f"Sundress - {label}", f"sundress-top-{key}", f"sundress-skirt-{key}")

outfit("Cottagecore Fit", "milkmaid-top-strawberry", "denim-skirt-light-wash")

# ------------------------------------------------------------------ soft girl / cozy

for key, label, base, heart in (("cream-pink", "Cream & Pink", (240, 232, 218), (240, 120, 160)),
                                ("pink-red", "Pink & Red", (248, 196, 210), (214, 36, 64)),
                                ("black-pink", "Black & Pink", (32, 30, 34), (246, 160, 192)),
                                ("lavender", "Lavender & White", (206, 190, 236), WHITE)):
    add(f"heart-sweater-{key}", "shirt", f"Fuzzy Heart Sweater - {label}",
        f"Oversized fuzzy mohair sweater with a big knitted heart ({label.lower()}). Cozy soft girl essential.",
        8, garment(S.heart_sweater, {"base": base, "heart": heart, "back_heart": True}),
        pair="flare-leggings-black", collection="Cozy", keywords=["sweater", "heart", "fuzzy", "cozy", "soft girl"])

for key, label, base in (("cream", "Cream", (240, 232, 214)), ("baby-pink", "Baby Pink", (244, 196, 208)),
                         ("sage", "Sage", (170, 188, 160)), ("burgundy", "Burgundy", (110, 32, 46))):
    add(f"cable-knit-sweater-{key}", "shirt", f"Cable Knit Sweater - {label}",
        f"Chunky {label.lower()} cable knit sweater with rope cables and ribbed trims. Cozy fall aesthetic.", 8,
        garment(S.cable_sweater, {"base": base}), pair="pleated-skirt-red-tartan", collection="Cozy",
        keywords=["sweater", "knit", "cozy", "fall", "aesthetic"])

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
    ("lavender", "Lavender", {"base": (200, 184, 232), "print": (110, 80, 160), "back_print": (110, 80, 160),
                              "string": (255, 255, 255)}),
]
for key, label, pal in HOODIE_COLOURS:
    add(f"essential-hoodie-{key}", "shirt", f"Essential Hoodie - {label}",
        f"Comfy {label.lower()} oversized hoodie with hood, drawstrings, kangaroo pocket and a minimal logo. "
        "Pair it with the matching joggers for the full set.", 8,
        garment(S.hoodie, pal), pair=f"essential-joggers-{key}", collection="Cozy",
        keywords=["hoodie", "matching set", "cozy", "aesthetic"])
    jog = {"base": pal["base"], "grain": pal.get("grain", 0.022), "print": pal["print"]}
    add(f"essential-joggers-{key}", "pants", f"Essential Joggers - {label}",
        f"Relaxed {label.lower()} sweatpants with a drawstring waist, scrunched cuffs and clean white "
        "sneakers. Matches the Essential Hoodie.", 8,
        garment(P.joggers, jog, shoes=WHITE_KICKS), pair=f"essential-hoodie-{key}", collection="Cozy",
        keywords=["joggers", "sweatpants", "shoes", "matching set"])
    outfit(f"Sweatsuit Set - {label}", f"essential-hoodie-{key}", f"essential-joggers-{key}")

for key, label, base, ink in (("baby-pink", "Baby Pink", (246, 196, 208), (190, 80, 120)),
                              ("lilac", "Lilac", (204, 184, 236), (112, 84, 160)),
                              ("baby-blue", "Baby Blue", (172, 206, 240), (64, 104, 160)),
                              ("white", "White", (244, 244, 244), (40, 40, 44)),
                              ("black", "Black", (30, 30, 34), (246, 170, 196))):
    add(f"crop-hoodie-{key}", "shirt", f"Cropped Hoodie - {label}",
        f"Trendy cropped {label.lower()} hoodie with hood and drawstrings, finished with a ribbed hem above "
        "the waist.", 8, garment(S.hoodie, {"base": base, "print": ink}, crop=True),
        pair="flare-leggings-black" if key != "black" else "cargo-pants-baby-pink", collection="Cozy",
        keywords=["crop top", "cropped hoodie", "y2k", "aesthetic"])

for key, label, base in (("mocha", "Mocha", (124, 92, 74)), ("baby-blue", "Baby Blue", (172, 206, 240)),
                         ("black", "Black", (30, 30, 34))):
    add(f"zip-hoodie-{key}", "shirt", f"Zip Up Hoodie - {label}",
        f"Full-zip {label.lower()} hoodie with silver zipper, side pockets, hood and drawstrings.", 8,
        garment(S.hoodie, {"base": base, "print": (236, 236, 236), "string": (236, 236, 236)}, zip_up=True),
        pair="flare-leggings-mocha" if key == "mocha" else "baggy-jeans-light-wash", collection="Cozy",
        keywords=["zip up", "hoodie", "jacket"])

for key, label, base in (("baby-pink", "Baby Pink", (246, 190, 206)), ("cream", "Cream", (240, 232, 214)),
                         ("lilac", "Lilac", (196, 176, 232)), ("black", "Black", (26, 26, 30))):
    add(f"cropped-puffer-{key}", "shirt", f"Cropped Puffer Jacket - {label}",
        f"Glossy cropped {label.lower()} puffer jacket with stand collar, zip and elastic cuffs. Winter baddie.",
        10, garment(S.puffer, {"base": base, "trim": base if key != "black" else (40, 40, 44)}, crop=True),
        pair="flare-jeans-light-wash" if key != "black" else "flare-leggings-black", collection="Cozy",
        keywords=["puffer", "jacket", "winter", "cropped", "baddie"])

for key, label, pal in (("pink-plaid", "Pink Plaid", {"sett": [((246, 186, 206), 8), (WHITE, 2),
                                                               ((222, 120, 160), 4), (WHITE, 2)]}),
                        ("strawberry", "Strawberry", {"base": (250, 214, 224), "fabric": "print",
                                                      "motif": "strawberry", "spacing": (14, 14)})):
    add(f"pajama-pants-{key}", "pants", f"Cozy Pajama Pants - {label}",
        f"Soft {label.lower()} pajama pants with a drawstring waist. Sleepover approved.", 5,
        garment(P.pajama_pants, pal), pair="heart-sweater-cream-pink", collection="Cozy",
        keywords=["pajamas", "pjs", "cozy", "sleepover", "cute"])

outfit("Cozy Fit - Heart Sweater", "heart-sweater-cream-pink", "flare-leggings-black")
outfit("Sleepover Fit", "heart-sweater-pink-red", "pajama-pants-strawberry")
outfit("Winter Fit", "cropped-puffer-baby-pink", "flare-jeans-light-wash")

# ------------------------------------------------------------------ preppy / school

PLAID = {
    "red-tartan": [((170, 30, 40), 8), ((28, 34, 60), 4), ((170, 30, 40), 2), ((230, 200, 90), 1),
                   ((170, 30, 40), 2), ((28, 34, 60), 4)],
    "navy-green": [((30, 42, 78), 8), ((40, 92, 64), 6), ((30, 42, 78), 2), ((240, 240, 240), 1),
                   ((30, 42, 78), 2), ((40, 92, 64), 6)],
    "pink": [((246, 186, 206), 8), (WHITE, 3), ((214, 130, 170), 2), (WHITE, 3)],
    "black": [((34, 34, 38), 8), ((120, 122, 128), 4), ((34, 34, 38), 2), ((200, 30, 44), 1),
              ((34, 34, 38), 2), ((120, 122, 128), 4)],
    "lavender": [((200, 180, 236), 8), (WHITE, 3), ((150, 120, 200), 2), (WHITE, 3)],
}
SKIRTS = [
    ("red-tartan", "Red Tartan + Knee Socks", {"sett": PLAID["red-tartan"], "legwear": "knee_socks",
                                               "shoes": "mary_janes"}),
    ("navy-green", "Navy Plaid + Knee Socks", {"sett": PLAID["navy-green"], "legwear": "knee_socks",
                                               "shoes": "loafers", "shoe_color": (40, 26, 20)}),
    ("pink-thigh-highs", "Pink Plaid + Bow Thigh Highs", {"sett": PLAID["pink"], "legwear": "thigh_highs",
                                                         "sock_bow": HOT_PINK, "shoes": "mary_janes",
                                                         "shoe_bow": PINK}),
    ("black-tights", "Black Plaid + Tights & Boots", {"sett": PLAID["black"], "legwear": "tights",
                                                      "shoes": "platform_boots"}),
    ("lavender-warmers", "Lilac Plaid + Leg Warmers", {"sett": PLAID["lavender"], "legwear": "leg_warmers",
                                                       "warmers": (250, 250, 250), "shoes": "chunky",
                                                       "sneakers": PINK_CHUNKY}),
]
for key, label, pal in SKIRTS:
    add(f"pleated-skirt-{key}", "pants", f"Pleated Skirt - {label}",
        f"Plaid pleated mini skirt ({label.lower()}). School girl and preppy aesthetic, shoes included.", 8,
        garment(P.pleated_skirt, pal), pair="sweater-vest-navy" if key != "black-tights" else "corset-top-black-mesh",
        collection="Preppy", keywords=["skirt", "plaid", "school uniform", "aesthetic", "pleated"])

for key, label, base in (("white", "White", (250, 250, 250)), ("baby-pink", "Baby Pink", (248, 196, 210)),
                         ("black", "Black", (30, 30, 34)), ("navy", "Navy", (34, 46, 84))):
    add(f"tennis-skirt-{key}", "pants", f"Tennis Skirt + Sneakers - {label}",
        f"Sporty {label.lower()} pleated tennis skirt with crew socks and chunky white sneakers. Clean girl "
        "and preppy.", 8,
        garment(P.pleated_skirt, {"base": base, "pleat": 10, "length": 40, "legwear": "crew_socks",
                                  "shoes": "chunky", "button": False}),
        pair="cricket-sweater-cream", collection="Preppy", keywords=["tennis skirt", "preppy", "sporty", "skirt"])

for key, label, base, stripes in (("cream", "Cream", (242, 236, 222), [(30, 42, 82), (140, 30, 44)]),
                                  ("white-green", "White & Green", (250, 250, 248), [(30, 100, 60), (30, 42, 82)]),
                                  ("pink", "Pink", (248, 200, 214), [WHITE, (220, 90, 130)])):
    add(f"cricket-sweater-{key}", "shirt", f"Preppy Cable V-Neck Sweater - {label}",
        f"Old money {label.lower()} cable knit V-neck with sporty striped trims. Preppy tennis club look.", 8,
        garment(S.cricket_sweater, {"base": base, "stripes": stripes}),
        pair=f"tennis-skirt-{'white' if key != 'pink' else 'baby-pink'}",
        collection="Preppy", keywords=["sweater", "preppy", "old money", "tennis", "v neck"])

for key, label, argyle, tie in (("navy", "Navy Argyle", ((30, 42, 78), (60, 80, 130), (226, 226, 230)), (130, 24, 36)),
                                ("beige", "Beige Argyle", ((196, 172, 136), (150, 118, 84), (250, 246, 236)), None)):
    add(f"sweater-vest-{key}", "shirt", f"Preppy Sweater Vest - {label}",
        f"{label} sweater vest over a crisp white collared shirt{' and tie' if tie else ''}. Smart, preppy "
        "and school-ready.", 8, garment(S.sweater_vest, {"argyle": argyle, "tie": tie}),
        pair="pleated-skirt-navy-green" if key == "navy" else "pleated-skirt-red-tartan", collection="Preppy",
        keywords=["sweater vest", "argyle", "preppy", "school"])

ACADEMY = [
    ("navy", "Navy", {"jacket": (28, 36, 68), "piping": (226, 186, 90), "crest": (120, 24, 36),
                      "neckwear": (120, 24, 36), "tie_stripe": (226, 186, 90), "buttons": (214, 176, 84)},
     "red-tartan"),
    ("maroon", "Maroon", {"jacket": (100, 26, 40), "piping": (236, 226, 204), "crest": (28, 36, 68),
                          "neckwear": (28, 36, 68), "tie_stripe": (236, 226, 204), "buttons": (214, 176, 84)},
     "navy-green"),
    ("black", "Black", {"jacket": (28, 28, 32), "piping": (200, 30, 44), "crest": (200, 30, 44),
                        "neckwear": (200, 30, 44), "tie_stripe": (28, 28, 32), "buttons": (190, 192, 198)},
     "black-tights"),
]
for key, label, pal, skirt in ACADEMY:
    add(f"academy-blazer-{key}", "shirt", f"School Uniform Blazer - {label}",
        f"Private-school {label.lower()} blazer with contrast piping, embroidered crest, striped tie and "
        "white collared shirt. Made for school and roleplay games.", 10,
        garment(S.suit, pal, neckwear="tie", crest=True), pair=f"pleated-skirt-{skirt}",
        collection="Preppy", keywords=["school uniform", "blazer", "roleplay", "preppy"])
    outfit(f"School Uniform - {label}", f"academy-blazer-{key}", f"pleated-skirt-{skirt}")

SAILORS = [
    ("white", "Summer White", {"base": (250, 250, 250), "collar": (30, 42, 82), "stripe": WHITE,
                               "scarf": (200, 30, 44)}, "navy-green"),
    ("navy", "Winter Navy", {"base": (34, 46, 84), "collar": (24, 32, 62), "stripe": WHITE,
                             "scarf": (200, 30, 44), "sleeves": "long"}, "navy-green"),
    ("black", "Black", {"base": (28, 28, 32), "collar": (20, 20, 24), "stripe": WHITE, "scarf": (200, 30, 44),
                        "sleeves": "long"}, "black-tights"),
    ("pink", "Pink", {"base": (248, 206, 220), "collar": WHITE, "stripe": (236, 110, 150), "scarf": HOT_PINK},
     "pink-thigh-highs"),
]
for key, label, pal, skirt in SAILORS:
    add(f"sailor-top-{key}", "shirt", f"Sailor Uniform Top - {label}",
        f"Classic {label.lower()} sailor uniform top with striped sailor collar, big scarf bow and striped "
        "cuffs. Kawaii school look.", 8, garment(S.sailor_top, pal), pair=f"pleated-skirt-{skirt}",
        collection="Preppy", keywords=["sailor uniform", "school uniform", "kawaii", "anime", "cute"])
    outfit(f"Sailor Uniform - {label}", f"sailor-top-{key}", f"pleated-skirt-{skirt}")

for key, label, base in (("cream", "Cream", (236, 226, 206)), ("black", "Black", (28, 28, 32)),
                         ("taupe", "Taupe", (160, 146, 132))):
    add(f"wide-trousers-{key}", "pants", f"Wide Leg Trousers - {label}",
        f"High-waisted {label.lower()} wide leg trousers with front pleats, a pressed crease, thin belt and "
        "loafers. Old money aesthetic.", 8,
        garment(P.wide_trousers, {"base": base, "belt": (60, 38, 28) if key != "black" else (20, 20, 22)}),
        pair="bow-blouse-ivory" if key != "cream" else "bow-blouse-black", collection="Preppy",
        keywords=["trousers", "wide leg", "old money", "office", "elegant"])

outfit("Tennis Club Fit", "cricket-sweater-cream", "tennis-skirt-white")
outfit("Old Money Fit", "bow-blouse-ivory", "wide-trousers-black")

# ------------------------------------------------------------------ alt / baddie

for key, label, pal in (
        ("black-mesh", "Black Mesh", {"base": (22, 22, 26), "lacing": (220, 40, 70), "mesh": (16, 16, 18)}),
        ("burgundy", "Burgundy", {"base": (110, 26, 44), "lacing": (24, 22, 24)}),
        ("white-lace", "White Lace", {"base": (248, 246, 240), "lacing": (236, 150, 176), "lace_trim": WHITE}),
        ("pink-satin", "Pink Satin", {"base": (246, 180, 200), "lacing": WHITE, "lace_trim": WHITE})):
    add(f"corset-top-{key}", "shirt", f"Satin Corset Top - {label}",
        f"Satin corset top ({label.lower()}) with a sweetheart neckline, boning and lace-up front and back.", 8,
        garment(S.corset_top, pal),
        pair="denim-skirt-black" if key in ("black-mesh", "burgundy") else "flare-jeans-light-wash",
        collection="Alt", keywords=["corset", "baddie", "alt", "goth", "y2k"])

for key, label, base in (("black", "Black", (24, 24, 28)), ("white", "White", (246, 246, 244)),
                         ("red", "Cherry Red", (196, 28, 48)), ("baby-blue", "Baby Blue", (172, 206, 240))):
    add(f"off-shoulder-top-{key}", "shirt", f"Off Shoulder Ruffle Crop Top - {label}",
        f"Ribbed {label.lower()} off-the-shoulder crop top with a ruffled neckline, long sleeves and a gold "
        "heart necklace.", 7, garment(S.off_shoulder_top, {"base": base}), pair="flare-jeans-mid-wash",
        collection="Alt", keywords=["off shoulder", "crop top", "baddie", "y2k", "aesthetic"])

add("lace-up-mesh-top", "shirt", "Lace Up Mesh Top - Goth",
    "Black lace-up top with fishnet sleeves, square neckline and a silver crescent chain necklace.", 7,
    garment(S.mesh_top, {"base": (22, 22, 26)}), pair="ripped-skinny-jeans-black", collection="Alt",
    keywords=["goth", "emo", "fishnet", "grunge"])

add("biker-jacket-black", "shirt", "Leather Biker Jacket - Black",
    "Asymmetric-zip black leather moto jacket with wide lapels, belted hem and zipped cuffs over a white tee.",
    10, garment(S.biker_jacket, {"leather": (26, 24, 26)}), pair="denim-skirt-black", collection="Alt",
    keywords=["leather jacket", "biker", "baddie", "edgy"])

for key, label, pal in (
        ("light-wash", "Light Wash + Black Boots", {"denim": (118, 154, 194), "shoes": "knee_boots"}),
        ("black", "Black + Studded Belt & Boots", {"denim": (40, 42, 48), "thread": (140, 140, 146),
                                                   "belt": "studded", "shoes": "knee_boots"}),
        ("mid-wash", "Mid Wash + Brown Boots", {"denim": (74, 110, 162), "shoes": "knee_boots",
                                                "shoe_color": (92, 56, 36)})):
    add(f"denim-skirt-{key}", "pants", f"Denim Mini Skirt - {label}",
        f"Denim mini skirt ({label.lower()}) with a frayed hem and tall leather boots.", 8,
        garment(P.denim_skirt, pal), pair="corset-top-black-mesh" if key == "black" else "milkmaid-top-white",
        collection="Alt", keywords=["denim skirt", "mini skirt", "boots", "baddie", "y2k"])

for key, label, base, kicks in (("black", "Black", (26, 26, 30), WHITE_KICKS),
                                ("mocha", "Mocha", (110, 80, 64), WHITE_KICKS),
                                ("baby-pink", "Baby Pink", (240, 180, 200), PINK_CHUNKY)):
    add(f"flare-leggings-{key}", "pants", f"Flare Leggings + Sneakers - {label}",
        f"Stretchy {label.lower()} flare leggings with a crossover waistband and chunky sneakers. Clean girl "
        "pilates fit.", 7, garment(P.flare_leggings, {"base": base, "sneakers": kicks}),
        pair="crop-hoodie-baby-pink" if key != "baby-pink" else "crop-hoodie-white", collection="Alt",
        keywords=["leggings", "flare leggings", "clean girl", "yoga", "sneakers"])

for key, label, pal in (("light", "Light Wash", {"denim": (128, 164, 204), "wash": 0.3}),
                        ("black", "Black", {"denim": (40, 42, 48), "wash": 0.14, "thread": (130, 130, 136),
                                            "button": (150, 150, 155)})):
    add(f"ripped-skinny-jeans-{key}", "pants", f"Ripped Skinny Jeans - {label}",
        f"Slim {label.lower()} jeans with distressed knee rips, frayed threads and faded thighs.", 8,
        garment(P.jeans, pal, baggy=0.1, rips=True), pair="off-shoulder-top-black", collection="Alt",
        keywords=["ripped jeans", "skinny", "distressed", "grunge"])

outfit("Alt Fit - Corset", "corset-top-black-mesh", "denim-skirt-black")
outfit("Baddie Fit", "off-shoulder-top-black", "flare-jeans-black")
outfit("Clean Girl Fit", "crop-hoodie-baby-pink", "flare-leggings-black")

# ------------------------------------------------------------------ denim, layers & streetwear

for key, label, pal, shoes in (
        ("light-wash", "Light Wash", {"denim": (128, 164, 204), "wash": 0.3}, WHITE_KICKS),
        ("mid-wash", "Mid Wash", {"denim": (74, 110, 162), "wash": 0.26}, None),
        ("dark-wash", "Dark Wash", {"denim": (34, 48, 82), "wash": 0.14}, None),
        ("black", "Washed Black", {"denim": (44, 46, 52), "wash": 0.18, "thread": (140, 140, 146),
                                   "button": (150, 150, 155)}, BLACK_KICKS)):
    add(f"baggy-jeans-{key}", "pants", f"Baggy Jeans - {label}" + (" + Sneakers" if shoes else ""),
        f"Loose fit {label.lower()} jeans with realistic fading, whiskers, stitched pockets and stacked "
        f"hems{' and sneakers' if shoes else ''}.", 8, garment(P.jeans, pal, baggy=1.0, shoes=shoes),
        pair="baby-tee-lucky-star" if key == "black" else "basic-tee-white",
        collection="Denim", keywords=["jeans", "baggy", "denim", "streetwear"])

for key, label, pal, kw in (
        ("baby-pink", "Baby Pink + Chain", {"base": (246, 190, 206), "belt": "chain"}, {}),
        ("white", "White + Chain", {"base": (244, 242, 238), "belt": "chain"}, {}),
        ("black-techwear", "Black Techwear", {"base": (34, 34, 38), "belt": (18, 18, 20), "cuff": (28, 28, 32)},
         {"shoes": BLACK_KICKS, "straps": True}),
        ("khaki", "Khaki", {"base": (190, 168, 128)}, {})):
    add(f"cargo-pants-{key}", "pants", f"Cargo Pants - {label}",
        f"Baggy utility cargo pants in {label.lower()} with flap cargo pockets, knee seams and back pockets.", 8,
        garment(P.cargo, pal, **kw), pair="halter-top-black-butterfly" if key == "baby-pink" else "crop-hoodie-black",
        collection="Denim", keywords=["cargo", "streetwear", "y2k", "baddie"])

for key, label, pal in (
        ("classic", "Classic Blue", {"denim": (58, 92, 140)}),
        ("light", "Light Wash", {"denim": (118, 154, 194)}),
        ("black", "Washed Black", {"denim": (48, 50, 56), "thread": (150, 150, 155), "button": (150, 150, 155)}),
        ("sherpa", "Sherpa Collar", {"denim": (70, 104, 150), "collar": (238, 230, 214)})):
    add(f"denim-jacket-{key}", "shirt", f"Denim Jacket - {label}",
        f"Trucker-style denim jacket ({label.lower()}) with contrast top-stitching, flap chest pockets, metal "
        "buttons and a realistic faded wash.", 10, garment(S.denim_jacket, pal), pair="pleated-skirt-black-tights",
        collection="Denim", keywords=["denim", "jean jacket", "vintage"])

VARSITY = [
    ("pink", "Pink", {"body": (240, 160, 190), "sleeve": (250, 244, 236), "rib": (240, 160, 190),
                      "stripe": (250, 244, 236), "letter_edge": (200, 60, 110), "snap": (250, 244, 236)}),
    ("black-pink", "Black & Pink", {"body": (26, 26, 28), "sleeve": (248, 196, 212), "rib": (26, 26, 28),
                                    "stripe": (248, 196, 212), "letter_edge": (236, 96, 150), "snap": (248, 196, 212)}),
    ("cherry", "Cherry Red", {"body": (170, 26, 40), "sleeve": (240, 230, 210), "rib": (170, 26, 40),
                              "stripe": (240, 230, 210), "letter_edge": (30, 30, 34), "snap": (240, 230, 210),
                              "back_number": "08"}),
    ("navy", "Navy", {"body": (28, 38, 72), "sleeve": (238, 230, 210), "rib": (28, 38, 72), "stripe": (238, 230, 210),
                      "letter_edge": (214, 160, 52), "snap": (230, 222, 200)}),
]
for key, label, pal in VARSITY:
    add(f"varsity-jacket-{key}", "shirt", f"Varsity Jacket - {label}",
        f"{label} letterman jacket with cream leather sleeves, striped ribbed trims, snap buttons, a chenille "
        "letter patch and an arched back print.", 10, garment(S.varsity, pal),
        pair="tennis-skirt-white" if key != "navy" else "baggy-jeans-light-wash", collection="Layers",
        keywords=["varsity", "letterman", "jacket", "preppy"])

for key, label, sett, tee_print in (
        ("pink", "Pink Plaid", [((236, 140, 170), 8), (WHITE, 2), ((190, 70, 110), 4), (WHITE, 2)], "pixel_heart"),
        ("red-black", "Red Buffalo", [((178, 34, 34), 8), ((22, 22, 24), 8)], None),
        ("brown", "Brown Plaid", [((120, 84, 60), 8), ((230, 214, 190), 2), ((60, 40, 30), 6), ((230, 214, 190), 2)],
         "daisy")):
    add(f"open-flannel-{key}", "shirt", f"Open Flannel + Tee - {label}",
        f"Unbuttoned {label.lower()} flannel layered over a white tee, with chest pockets, collar and "
        "button cuffs.", 8, garment(S.flannel_open, {"sett": sett, "tee_print": tee_print}),
        pair="ripped-skinny-jeans-light", collection="Layers", keywords=["flannel", "plaid", "grunge", "layered"])

for key, label, tee, ink in (("white", "White", (244, 244, 242), (30, 30, 34)),
                             ("black", "Black", (30, 30, 34), (240, 240, 240))):
    add(f"basic-tee-{key}", "shirt", f"Basic Tee - {label}",
        f"Clean {label.lower()} short sleeve t-shirt with a ribbed crew neck and soft cotton shading. "
        "The everyday base layer that goes with everything.", 5,
        garment(S.graphic_tee, {"tee": tee, "ink": ink}), pair="flare-jeans-mid-wash", collection="Basics",
        keywords=["basic", "plain", "tee", "t-shirt", "aesthetic"])

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

# ------------------------------------------------------------------ roleplay

for key, label, base in (("ceil-blue", "Ceil Blue", (116, 160, 210)), ("pink", "Pink", (240, 160, 190)),
                         ("lavender", "Lavender", (176, 156, 220)), ("teal", "Teal", (20, 128, 130))):
    add(f"scrubs-top-{key}", "shirt", f"Medical Scrubs Top - {label}",
        f"{label} V-neck scrubs top with chest pocket, pen and ID badge. For hospital and nurse roleplay.", 6,
        garment(S.scrubs_top, {"base": base}), pair=f"scrubs-pants-{key}", collection="Roleplay",
        keywords=["scrubs", "nurse", "doctor", "hospital", "roleplay"])
    add(f"scrubs-pants-{key}", "pants", f"Medical Scrubs Pants - {label}",
        f"{label} scrubs pants with drawstring waist, cargo pocket and white sneakers.", 6,
        garment(P.scrubs_pants, {"base": base}), pair=f"scrubs-top-{key}", collection="Roleplay",
        keywords=["scrubs", "nurse", "doctor", "hospital", "roleplay"])
    outfit(f"Scrubs - {label}", f"scrubs-top-{key}", f"scrubs-pants-{key}")

# ------------------------------------------------------------------ drop 2: more styles

for key, label, base in (("ballet-pink", "Ballet Pink", (244, 200, 210)), ("black", "Black", (28, 26, 30)),
                         ("cream", "Cream", (240, 230, 212)), ("lavender", "Lavender", (206, 190, 236))):
    add(f"wrap-top-{key}", "shirt", f"Ballet Wrap Top - {label}",
        f"Balletcore {label.lower()} wrap top with a crossover V neck, fitted long sleeves and a side tie bow.",
        7, garment(S.wrap_top, {"base": base}), pair=f"tulle-skirt-{'black' if key == 'black' else 'pink'}",
        collection="Balletcore", keywords=["balletcore", "wrap top", "ballet", "coquette", "soft girl"])

for key, label, pal in (
        ("black", "Black", {"base": BLACK, "ring": (226, 196, 120)}),
        ("white", "White", {"base": (248, 248, 246), "ring": (226, 196, 120)}),
        ("hot-pink", "Hot Pink", {"base": HOT_PINK, "bow": (250, 210, 226)}),
        ("leopard", "Leopard", {"base": (214, 164, 98), "fabric": "leopard", "ring": (226, 196, 120)})):
    add(f"tube-top-{key}", "shirt", f"Ruched Tube Top - {label}",
        f"Strapless ruched {label.lower()} tube top, cropped, with a {'gold ring' if pal.get('ring') else 'bow'} "
        "at the centre. Baddie summer staple.", 6, garment(S.tube_top, pal),
        pair="mini-skirt-black-satin" if key == "leopard" else "cargo-skirt-black",
        collection="Baddie", keywords=["tube top", "baddie", "y2k", "crop top", "summer"])

for key, label, pal in (
        ("pink-white", "Pink & White", {"cami": (248, 246, 242), "shrug": (246, 196, 210)}),
        ("white-black", "White & Black", {"cami": (24, 24, 28), "shrug": (250, 250, 250), "lace": (44, 44, 50)}),
        ("lavender", "Lavender", {"cami": (206, 190, 236), "shrug": (226, 214, 248)})):
    add(f"shrug-cami-{key}", "shirt", f"Fuzzy Shrug + Cami - {label}",
        f"Cropped fuzzy bolero shrug over a lace-trim satin cami ({label.lower()}). Balletcore and coquette.", 8,
        garment(S.shrug_cami, pal), pair=f"tulle-skirt-{'black' if key == 'white-black' else 'white'}",
        collection="Balletcore", keywords=["shrug", "bolero", "balletcore", "coquette", "fuzzy"])

for key, label, base, ribbon, extra in (
        ("pink", "Ballet Pink", (246, 190, 206), (240, 150, 180),
         {"tights": (252, 252, 252), "tights_opacity": 0.7, "shoes": "ballet", "shoe_color": (246, 190, 206)}),
        ("white", "White", (252, 252, 252), (236, 224, 232), {"shoes": "ballet", "shoe_color": (252, 252, 252),
                                                              "shoe_bow": (246, 190, 206)}),
        ("black", "Black", (30, 28, 32), (30, 28, 32), {"tights": (22, 22, 26), "shoes": "mary_janes"}),
        ("lavender", "Lavender", (206, 190, 236), (186, 166, 226), {"shoes": "ballet", "shoe_color": (252, 252, 252),
                                                                    "shoe_bow": (186, 166, 226)})):
    add(f"tulle-skirt-{key}", "pants", f"Tulle Ballet Skirt - {label}",
        f"Layered sheer {label.lower()} tulle skirt with a satin ribbon bow"
        f"{' and tights' if extra.get('tights') else ''}, plus ballet shoes. Balletcore dream.", 8,
        garment(P.tulle_skirt, dict(extra, base=base, ribbon=ribbon)),
        pair=f"wrap-top-{'black' if key == 'black' else 'ballet-pink'}", collection="Balletcore",
        keywords=["tulle skirt", "tutu", "balletcore", "ballet", "coquette"])

outfit("Balletcore Set - Pink", "wrap-top-ballet-pink", "tulle-skirt-pink")
outfit("Balletcore Set - Black", "wrap-top-black", "tulle-skirt-black")
outfit("Balletcore Set - Shrug", "shrug-cami-pink-white", "tulle-skirt-white")

CHEER = [
    ("red", "Red & White", {"base": (200, 30, 44), "accent": WHITE, "accent2": (28, 28, 32), "number": "1"}),
    ("pink", "Pink & White", {"base": (240, 130, 170), "accent": WHITE, "accent2": (200, 60, 110), "number": "7"}),
    ("blue-gold", "Blue & Gold", {"base": (30, 70, 170), "accent": (246, 196, 60), "accent2": WHITE, "number": "3"}),
    ("black-pink", "Black & Pink", {"base": (26, 26, 30), "accent": PINK, "accent2": WHITE, "number": "9"}),
]
for key, label, pal in CHEER:
    add(f"cheer-top-{key}", "shirt", f"Cheerleader Top - {label}",
        f"{label} cheer uniform crop top with V neck, chevron stripes and the team name. For school and "
        "cheer roleplay.", 7, garment(S.cheer_top, pal), pair=f"cheer-skirt-{key}", collection="Cheer",
        keywords=["cheerleader", "cheer", "uniform", "school", "roleplay"])
    add(f"cheer-skirt-{key}", "pants", f"Cheer Skirt + Sneakers - {label}",
        f"{label} pleated cheer skirt with striped hem, crew socks and white sneakers.", 7,
        garment(P.pleated_skirt, {"base": pal["base"], "pleat": 10, "length": 40, "button": False,
                                  "hem_stripes": [pal["accent"], pal["accent2"]], "legwear": "crew_socks",
                                  "shoes": "chunky"}),
        pair=f"cheer-top-{key}", collection="Cheer", keywords=["cheerleader", "cheer skirt", "uniform", "roleplay"])
    outfit(f"Cheer Uniform - {label}", f"cheer-top-{key}", f"cheer-skirt-{key}")

GOWNS = [
    ("rose-pink", "Rose Pink", {"base": (240, 170, 190)}),
    ("midnight-sparkle", "Midnight Sparkle", {"base": (28, 34, 80), "sparkle": (220, 226, 255),
                                              "brooch": (230, 235, 250)}),
    ("red", "Red", {"base": (190, 20, 40), "straps": True}),
    ("bridal-white", "Bridal White", {"base": (250, 248, 244), "lace": WHITE, "sparkle": WHITE,
                                      "brooch": (240, 240, 250)}),
    ("lavender", "Lavender", {"base": (200, 180, 236), "sparkle": WHITE}),
    ("black-sparkle", "Black Sparkle", {"base": (24, 24, 28), "sparkle": (220, 220, 230), "straps": True}),
]
for key, label, pal in GOWNS:
    add(f"prom-dress-top-{key}", "shirt", f"Prom Dress Top - {label}",
        f"Top half of the {label} prom gown: satin sweetheart bodice and waist sash. Wear it with the matching "
        "Prom Dress Skirt for a floor-length gown. Prom, wedding and royal roleplay.", 8,
        garment(S.gown_top, pal), pair=f"prom-dress-skirt-{key}", collection="Formal",
        keywords=["prom dress", "gown", "formal", "wedding", "princess"])
    add(f"prom-dress-skirt-{key}", "pants", f"Prom Dress Skirt - {label}",
        f"Floor-length {label.lower()} satin gown skirt with flowing folds. Matches the {label} Prom Dress Top.", 8,
        garment(P.gown_skirt, pal), pair=f"prom-dress-top-{key}", collection="Formal",
        keywords=["prom dress", "gown", "formal", "wedding", "princess"])
    outfit(f"Prom Dress - {label}", f"prom-dress-top-{key}", f"prom-dress-skirt-{key}")

for key, label, base, piping in (("pink", "Pink", (246, 196, 210), WHITE),
                                 ("lavender", "Lavender", (206, 190, 236), WHITE),
                                 ("champagne", "Champagne", (238, 222, 196), (30, 30, 34)),
                                 ("baby-blue", "Baby Blue", (180, 210, 240), WHITE)):
    pal = {"base": base, "piping": piping, "slippers": WHITE if key != "champagne" else (246, 196, 210)}
    add(f"satin-pj-shirt-{key}", "shirt", f"Satin Pajama Shirt - {label}",
        f"Silky {label.lower()} button-up pajama shirt with contrast piping and a chest pocket. Matches the "
        "Satin Pajama Pants.", 7, garment(S.pj_shirt, pal), pair=f"satin-pj-pants-{key}", collection="Sleepover",
        keywords=["pajamas", "satin", "sleepover", "pjs", "matching set"])
    add(f"satin-pj-pants-{key}", "pants", f"Satin Pajama Pants + Slippers - {label}",
        f"Silky {label.lower()} pajama pants with piping, drawstring waist and fluffy slippers.", 7,
        garment(P.pj_pants, pal), pair=f"satin-pj-shirt-{key}", collection="Sleepover",
        keywords=["pajamas", "satin", "slippers", "sleepover", "matching set"])
    outfit(f"Satin PJ Set - {label}", f"satin-pj-shirt-{key}", f"satin-pj-pants-{key}")

for key, label, pal in (
        ("light", "Light Denim", {"denim": (128, 164, 204), "tee": (250, 250, 250)}),
        ("pink", "Pink Denim", {"denim": (240, 160, 190), "tee_stripes": [(250, 250, 250), (236, 110, 150)],
                                "thread": WHITE}),
        ("black", "Black Denim", {"denim": (44, 46, 52), "tee": (250, 250, 250), "thread": (150, 150, 156)})):
    add(f"overall-top-{key}", "shirt", f"Overalls + Tee - {label}",
        f"Cute {label.lower()} overall bib and straps with gold buttons over a tee. Wear with the matching "
        "Overall Shorts.", 7, garment(S.overall_top, pal), pair=f"overall-shorts-{key}", collection="Y2K",
        keywords=["overalls", "denim", "cute", "y2k", "matching set"])
    add(f"overall-shorts-{key}", "pants", f"Overall Shorts + Sneakers - {label}",
        f"{label} rolled-cuff shorts with crew socks and chunky sneakers. Bottom half of the overalls.", 7,
        garment(P.overall_shorts, dict(pal, legwear="crew_socks", shoes="chunky")), pair=f"overall-top-{key}",
        collection="Y2K", keywords=["overalls", "shorts", "denim", "sneakers"])
    outfit(f"Overalls - {label}", f"overall-top-{key}", f"overall-shorts-{key}")

for key, label, base, kicks in (("black", "Black", (26, 26, 30), WHITE_KICKS),
                                ("grey", "Heather Grey", (150, 152, 158), WHITE_KICKS),
                                ("baby-pink", "Baby Pink", (240, 180, 200), PINK_CHUNKY),
                                ("mocha", "Mocha", (110, 80, 64), WHITE_KICKS)):
    add(f"biker-shorts-{key}", "pants", f"Biker Shorts + Sneakers - {label}",
        f"High-waisted {label.lower()} biker shorts with crew socks and chunky sneakers. Sporty clean girl fit.",
        6, garment(P.biker_shorts, {"base": base, "legwear": "crew_socks", "shoes": "chunky", "sneakers": kicks}),
        pair="crop-hoodie-baby-pink" if key != "baby-pink" else "crop-hoodie-white", collection="Alt",
        keywords=["biker shorts", "sporty", "clean girl", "shorts", "sneakers"])

for key, label, pal in (
        ("khaki", "Khaki + Sneakers", {"base": (190, 168, 128), "shoes": "chunky", "legwear": "crew_socks"}),
        ("black", "Black + Platform Boots", {"base": (34, 34, 38), "belt": "studded", "shoes": "platform_boots"}),
        ("pink", "Pink + Chain", {"base": (246, 190, 206), "belt": "chain", "shoes": "chunky",
                                  "sneakers": PINK_CHUNKY})):
    add(f"cargo-skirt-{key}", "pants", f"Cargo Mini Skirt - {label}",
        f"Y2K cargo mini skirt ({label.lower()}) with flap pockets and shoes included.", 7,
        garment(P.cargo_skirt, pal), pair="tube-top-black" if key != "pink" else "tube-top-white",
        collection="Baddie", keywords=["cargo skirt", "mini skirt", "y2k", "baddie"])

for key, label, pal in (
        ("leopard", "Leopard + Knee Boots", {"base": (214, 164, 98), "fabric": "leopard", "shoes": "knee_boots"}),
        ("cow-print", "Cow Print + Sneakers", {"base": (250, 250, 248), "fabric": "cow", "shoes": "chunky",
                                               "legwear": "crew_socks"}),
        ("black-satin", "Black Satin + Knee Boots", {"base": (24, 24, 28), "fabric": "satin", "shoes": "knee_boots"}),
        ("red", "Red + Tights", {"base": (196, 28, 48), "fabric": "rib", "legwear": "tights",
                                 "shoes": "mary_janes"})):
    add(f"mini-skirt-{key}", "pants", f"Bodycon Mini Skirt - {label}",
        f"Fitted {label.split(' + ')[0].lower()} mini skirt with {label.split(' + ')[1].lower()}. Baddie night out.",
        7, garment(P.mini_skirt, pal), pair="tube-top-leopard" if key == "black-satin" else "tube-top-black",
        collection="Baddie", keywords=["mini skirt", "baddie", "bodycon", "y2k"])

outfit("Baddie Set - Leopard", "tube-top-leopard", "mini-skirt-black-satin")
outfit("Baddie Set - Cargo", "tube-top-black", "cargo-skirt-black")
outfit("Sporty Fit", "crop-hoodie-baby-pink", "biker-shorts-grey")

for key, label, pal in (
        ("sunshine", "Sunshine", {"base": (255, 236, 150), "trim": WHITE, "graphic": "sunflower",
                                  "text": "SUNSHINE", "ink": (214, 130, 20)}),
        ("dreamy", "Dreamy", {"base": (34, 40, 82), "trim": (214, 200, 244), "graphic": "moon_stars",
                              "text": "DREAMY", "ink": (240, 220, 140)}),
        ("cloud-nine", "Cloud Nine", {"base": (190, 222, 250), "trim": WHITE, "graphic": "kawaii_cloud",
                                      "text": "CLOUD NINE", "ink": (70, 110, 200)}),
        ("lucky", "Lucky Ladybug", {"base": (250, 250, 250), "trim": (220, 40, 50), "graphic": "ladybug",
                                    "text": "LUCKY", "ink": (220, 40, 50)})):
    add(f"baby-tee-{key}", "shirt", f"Y2K Baby Tee - {label}",
        f"Fitted cropped baby tee with contrast trims and a cute {label.lower()} graphic.", 6,
        garment(S.baby_tee, pal), pair="biker-shorts-baby-pink" if key == "cloud-nine" else "flare-jeans-mid-wash",
        collection="Y2K", keywords=["baby tee", "y2k", "crop top", "cute", "aesthetic"])

# extra colourways of earlier designs
for key, label, pal in (("cherry-red", "Cherry Red", {"base": (196, 28, 48), "bow": WHITE, "trim": WHITE}),
                        ("sage", "Sage", {"base": (170, 188, 160), "bow": (250, 244, 232)})):
    add(f"bow-cardigan-{key}", "shirt", f"Coquette Bow Cardigan - {label}",
        f"Cute cropped {label.lower()} knit cardigan with satin bows down the front, lace trim and puff sleeves.",
        8, garment(S.bow_cardigan, pal),
        pair="ruffle-skirt-pink-gingham" if key == "sage" else "ruffle-skirt-black",
        collection="Coquette", keywords=["coquette", "cardigan", "bow", "soft girl", "cute"])
add("heart-sweater-white-red", "shirt", "Fuzzy Heart Sweater - White & Red",
    "Oversized fuzzy mohair sweater with a big red knitted heart. Cozy soft girl essential.", 8,
    garment(S.heart_sweater, {"base": (250, 250, 248), "heart": (214, 36, 64), "back_heart": True}),
    pair="flare-jeans-mid-wash", collection="Cozy", keywords=["sweater", "heart", "fuzzy", "cozy", "soft girl"])
add("milkmaid-top-cherry", "shirt", "Milkmaid Corset Top - Cherry Print",
    "Cottagecore milkmaid top in cherry print with a sweetheart neckline, lace-up corset front, puff sleeves "
    "and frilled hem.", 8,
    garment(S.milkmaid_top, {"base": (252, 250, 246), "fabric": "print", "motif": "cherry", "spacing": (15, 15),
                             "lace": (214, 28, 48)}),
    pair="denim-skirt-light-wash", collection="Cottagecore", keywords=["milkmaid", "cottagecore", "cherry"])
STRAW = {"base": (252, 236, 240), "fabric": "print", "motif": "strawberry", "spacing": (14, 14),
         "tie": (232, 46, 64)}
add("sundress-top-strawberry", "shirt", "Sundress Top - Strawberry",
    "Top half of the Strawberry sundress: square neck, straps, smocked back and ribbon waist bow. Wear it with "
    "the matching Sundress Skirt.", 7, garment(S.sundress_top, STRAW), pair="sundress-skirt-strawberry",
    collection="Cottagecore", keywords=["sundress", "dress", "strawberry", "cottagecore"])
add("sundress-skirt-strawberry", "pants", "Sundress Skirt - Strawberry",
    "Flowy strawberry print midi skirt with a frilled hem and ballet flats. Matches the Strawberry Sundress Top.",
    7, garment(P.sundress_skirt, dict(STRAW, shoes="ballet", shoe_color=(232, 46, 64), shoe_bow=(232, 46, 64))),
    pair="sundress-top-strawberry", collection="Cottagecore", keywords=["sundress", "dress", "strawberry"])
outfit("Sundress - Strawberry", "sundress-top-strawberry", "sundress-skirt-strawberry")
for key, label, pal in (("red", "Red", {"base": (176, 20, 40), "lace": (196, 40, 60)}),
                        ("lavender", "Lavender", {"base": (210, 196, 238), "lace": (240, 234, 252)})):
    add(f"lace-cami-{key}", "shirt", f"Lace Trim Satin Cami - {label}",
        f"Silky {label.lower()} satin cami top with lace trim, thin straps and a tiny bow.", 7,
        garment(S.lace_cami, pal), pair="mini-skirt-black-satin" if key == "red" else "tulle-skirt-lavender",
        collection="Coquette", keywords=["cami", "satin", "lace", "coquette", "y2k"])
add("off-shoulder-top-pink", "shirt", "Off Shoulder Ruffle Crop Top - Pink",
    "Ribbed pink off-the-shoulder crop top with a ruffled neckline, long sleeves and a gold heart necklace.", 7,
    garment(S.off_shoulder_top, {"base": (240, 150, 180)}), pair="flare-jeans-light-wash", collection="Alt",
    keywords=["off shoulder", "crop top", "baddie", "y2k"])
add("crop-hoodie-sage", "shirt", "Cropped Hoodie - Sage",
    "Trendy cropped sage hoodie with hood and drawstrings, finished with a ribbed hem above the waist.", 8,
    garment(S.hoodie, {"base": (152, 172, 146), "print": (246, 246, 240)}, crop=True),
    pair="biker-shorts-grey", collection="Cozy", keywords=["crop top", "cropped hoodie", "aesthetic"])

# ------------------------------------------------------------------ classic T-shirts (decals)

TEE_COPY = {
    "satin_bow": ("Coquette Bow", "Glossy pink satin coquette bow."),
    "angel_heart": ("Angel Heart", "Pink heart with angel wings and a golden halo."),
    "strawberry": ("Strawberry", "Juicy cartoon strawberry."),
    "daisy": ("Daisy", "Happy white daisy flower."),
    "butterfly": ("Pastel Butterfly", "Dreamy pastel butterfly with sparkles."),
    "mushroom": ("Cute Mushroom", "Kawaii cottagecore mushroom with a smile."),
    "cherries": ("Cherry Cute", "Glossy cartoon cherries with a little leaf."),
    "pixel_heart": ("Pixel Heart", "8-bit pixel art heart."),
    "good_vibes": ("Good Vibes", "Bubbly gradient GOOD VIBES lettering with sparkles."),
    "boba": ("Kawaii Boba", "Kawaii bubble tea with a smiley face and pearls."),
    "ringed_planet": ("Cosmic Planet", "Pastel ringed planet with twinkling stars."),
    "chrome_star": ("Chrome Star", "Y2K chrome sparkle star."),
    "retro_sunset": ("Retro Sunset", "Synthwave sunset with neon grid."),
    "mountain_badge": ("Explore More Badge", "Sunset mountain badge."),
    "lightning_bolt": ("Lightning Bolt", "Glowing yellow lightning bolt."),
    "rainbow": ("Rainbow", "Pastel rainbow with fluffy clouds."),
    "moon_stars": ("Sleepy Moon", "Sleepy crescent moon with twinkling stars."),
    "sunflower": ("Sunflower", "Bright sunny sunflower."),
    "kawaii_cloud": ("Kawaii Cloud", "Smiling kawaii rain cloud."),
    "ladybug": ("Lucky Ladybug", "Cute cartoon ladybug."),
}
for key in TEE_COPY:
    title, blurb = TEE_COPY[key]
    add(f"tshirt-{key.replace('_', '-')}", "tshirt", f"{title} T-Shirt",
        f"{blurb} Transparent background, so it layers over any shirt or your avatar's body.", 5,
        (lambda f: (lambda brand: padded(f())))(GRAPHICS[key]), pair="basic-tee-white", collection="T-Shirts",
        keywords=["t-shirt", "graphic", "cute", "aesthetic"])


BY_SLUG = {i.slug: i for i in ITEMS}
assert len(BY_SLUG) == len(ITEMS), "duplicate slugs"
assert set(TEE_COPY) == set(GRAPHICS), "every graphic needs T-shirt copy"
for _i in ITEMS:
    assert _i.pair is None or _i.pair in BY_SLUG, f"{_i.slug}: unknown pair {_i.pair}"
for _t, _slugs in OUTFITS:
    assert all(s in BY_SLUG for s in _slugs), _t
