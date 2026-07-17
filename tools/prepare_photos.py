#!/usr/bin/env python3
"""
Converts real photos into the site's image slots.

1. Save/export the real photos (from the shop's Facebook page, camera roll,
   or customer reviews — see PHOTOS.md for which shot goes where and the
   permission notes) into raw-photos/, named after their slot:
       raw-photos/storefront.jpg   (jpg/jpeg/png/webp all fine)
2. Run:  python3 tools/prepare_photos.py
3. Each photo is center-cropped to 3:2, resized to 1200x800, converted to
   WebP, and written over the placeholder in images/.

Needs Pillow (pip install pillow).
"""
import pathlib
import sys
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw-photos"
OUT = ROOT / "images"
SLOTS = ["storefront", "fireplace-lounge", "mocha-freeze", "pastry-case",
         "counter-crew", "froyo-bar", "coffee-flight", "nitro-pour"]
W, H = 1200, 800

if not RAW.is_dir():
    sys.exit("Create raw-photos/ and drop real photos in it first (see PHOTOS.md).")

done = 0
for slot in SLOTS:
    src = next((p for ext in ("jpg", "jpeg", "png", "webp")
                for p in [RAW / f"{slot}.{ext}"] if p.exists()), None)
    if not src:
        print(f"  (no raw photo for '{slot}' yet — placeholder stays)")
        continue
    img = Image.open(src)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img = ImageOps.fit(img, (W, H), Image.LANCZOS)
    img.save(OUT / f"{slot}.webp", "WEBP", quality=82)
    print(f"  wrote images/{slot}.webp from {src.name}")
    done += 1

print(f"{done} photo(s) installed. Commit and push to publish.")
