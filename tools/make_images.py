#!/usr/bin/env python3
"""
Generates the site's image assets:

1. Branded PLACEHOLDER photos in /images/*.webp — each marks a slot where a
   real photo from the shop's Facebook page / customer reviews belongs.
   Swap them by dropping real photos with the same filenames into raw-photos/
   and running tools/prepare_photos.py (see PHOTOS.md).
2. og-image.png (1200x630) — branded social share card (a real deliverable).
3. apple-touch-icon.png (180x180) and favicon.ico — from the logo mark.

Run: python3 tools/make_images.py   (from the repo root; needs Pillow)
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
IMAGES.mkdir(exist_ok=True)

CREAM = (250, 244, 233)
CREAM2 = (241, 229, 209)
ROAST = (62, 42, 28)
ROAST_DEEP = (43, 29, 18)
CARAMEL = (160, 90, 23)
CARAMEL_BRIGHT = (200, 134, 59)
SMOKE = (100, 118, 108)
PINE = (47, 64, 56)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size)
    for y in range(h):
        t = y / max(h - 1, 1)
        img.paste(tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)), (0, y, w, y + 1))
    return img


def ridge(draw, w, y0, amp, color):
    pts = [(0, y0)]
    xs = [0, 0.11, 0.21, 0.33, 0.45, 0.56, 0.69, 0.79, 0.9, 1.0]
    ys = [0.6, 0.1, 0.5, -0.4, 0.3, -0.1, 0.55, 0.0, 0.4, 0.15]
    for x, yy in zip(xs, ys):
        pts.append((int(x * w), int(y0 + yy * amp)))
    pts += [(w, y0 + 3 * amp), (0, y0 + 3 * amp)]
    draw.polygon(pts, fill=color)


def steam_cup(draw, cx, cy, s, color):
    # mug
    draw.rounded_rectangle([cx - s, cy - s * 0.7, cx + s * 0.7, cy + s * 0.7], radius=int(s * 0.25), outline=color, width=max(3, s // 12))
    draw.arc([cx + s * 0.5, cy - s * 0.35, cx + s * 1.25, cy + s * 0.45], 270, 90, fill=color, width=max(3, s // 12))
    # steam
    for dx in (-s * 0.55, -s * 0.1, s * 0.35):
        draw.arc([cx + dx, cy - s * 1.7, cx + dx + s * 0.35, cy - s * 1.0], 90, 270, fill=color, width=max(2, s // 16))


def placeholder(name, label):
    w, h = 1200, 800
    img = vgrad((w, h), CREAM, CREAM2)
    d = ImageDraw.Draw(img)
    ridge(d, w, 560, 90, SMOKE + (0,) if False else (SMOKE))
    ridge(d, w, 640, 70, PINE)
    steam_cup(d, 560, 300, 90, ROAST)
    f_big = ImageFont.truetype(SERIF_B, 44)
    f_sm = ImageFont.truetype(SANS, 26)
    f_tag = ImageFont.truetype(SANS_B, 22)
    d.text((600, 470), "Photo slot: " + label, font=f_big, fill=ROAST, anchor="mm")
    d.text((600, 525), "Replace with a real photo from the shop's Facebook page or guest reviews", font=f_sm, fill=(90, 70, 50), anchor="mm")
    tag = "see PHOTOS.md"
    d.rounded_rectangle([w / 2 - 110, 700, w / 2 + 110, 748], radius=24, fill=CARAMEL)
    d.text((w / 2, 724), tag, font=f_tag, fill=(255, 255, 255), anchor="mm")
    img.save(IMAGES / f"{name}.webp", "WEBP", quality=70)
    print("placeholder:", name)


SLOTS = [
    ("storefront", "the storefront"),
    ("fireplace-lounge", "fireplace seating area"),
    ("mocha-freeze", "Smoky Mountain Mocha Freeze"),
    ("pastry-case", "the bakery case"),
    ("counter-crew", "the crew / owners"),
    ("froyo-bar", "sweetFrog froyo bar"),
    ("coffee-flight", "a coffee flight"),
    ("nitro-pour", "nitro cold brew pour"),
]


def og_image():
    w, h = 1200, 630
    img = vgrad((w, h), (250, 244, 233), (231, 216, 189))
    d = ImageDraw.Draw(img)
    ridge(d, w, 430, 80, SMOKE)
    ridge(d, w, 500, 65, PINE)
    steam_cup(d, 150, 200, 70, ROAST)
    f_top = ImageFont.truetype(SANS_B, 34)
    f_main = ImageFont.truetype(SERIF_B, 84)
    f_sub = ImageFont.truetype(SANS, 30)
    d.text((270, 130), "S M O K Y   M O U N T A I N", font=f_top, fill=CARAMEL)
    d.text((266, 180), "Espresso", font=f_main, fill=ROAST)
    d.text((270, 300), "Coffee shop in Sevierville, TN  ·  since 2018", font=f_sub, fill=(74, 56, 42))
    d.text((270, 345), "1259 Middle Creek Rd  ·  (865) 366-1685", font=f_sub, fill=(74, 56, 42))
    img.save(ROOT / "og-image.png", "PNG", optimize=True)
    print("og-image.png")


def icons():
    s = 512
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([8, 8, s - 8, s - 8], fill=ROAST)
    # mountains
    d.polygon([(70, 360), (190, 190), (260, 290), (310, 230), (450, 360)], fill=CREAM)
    d.polygon([(70, 360), (190, 190), (240, 262), (140, 360)], fill=SMOKE)
    # steam
    for cx in (215, 275):
        d.arc([cx, 90, cx + 34, 160], 90, 270, fill=CREAM, width=14)
    img.resize((180, 180), Image.LANCZOS).save(ROOT / "apple-touch-icon.png", "PNG")
    img.resize((32, 32), Image.LANCZOS).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32)])
    print("apple-touch-icon.png, favicon.ico")


if __name__ == "__main__":
    for name, label in SLOTS:
        placeholder(name, label)
    og_image()
    icons()
