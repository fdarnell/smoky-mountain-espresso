#!/usr/bin/env python3
"""
Enhance + install the real shop photos from raw-photos/ into images/.

Unlike prepare_photos.py (generic center-crop), this script carries a
per-photo spec: crop box tuned to each shot's subject, a light "pro edit"
grade (contrast / saturation / brightness + unsharp mask), and the output
size the site actually uses. Re-running is idempotent.

Run:  python3 tools/enhance_photos.py
"""
import pathlib
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw-photos"
OUT = ROOT / "images"

# crop: (left, top, right, bottom) in source pixels, or None for full frame.
# grade: (brightness, contrast, color/saturation)
# sharpen: unsharp-mask percent
# out: (width, height) final resize, or None to keep crop size
SPECS = {
    # sunset patio exterior — homepage hero background (portrait, full frame)
    "hero-patio": dict(src="hero-patio.png", crop=None, grade=(1.00, 1.05, 1.10),
                       sharpen=70, out=(1080, 1437), q=70, name="hero-patio.webp"),
    # same shot, landscape 3:2 crop centered on the building — contact page
    "storefront": dict(src="hero-patio.png", crop=(0, 415, 1078, 1134),
                       grade=(1.00, 1.05, 1.10), sharpen=70, out=(1200, 800), q=75,
                       name="storefront.webp"),
    # pay-it-forward board — crop off the Google Maps overlay strip at the top
    "pay-it-forward": dict(src="pay-it-forward.png", crop=(0, 100, 1934, 1438),
                           grade=(1.03, 1.08, 1.06), sharpen=75, out=(1200, 800),
                           q=75, name="pay-it-forward.webp", fit=True),
    # carved bear under the sign — about page (4:5 portrait); bottom burn
    # de-emphasizes the patio-cover clutter at the base of the frame
    "sign-bear": dict(src="sign-bear.png", crop=(0, 43, 1086, 1350),
                      grade=(1.00, 1.06, 1.10), sharpen=70, out=(960, 1156), q=75,
                      name="sign-bear.webp", burn=True),
    # chocolate mocha freeze — Dollywood page
    "choc-frappe": dict(src="choc-frappe.png", crop=(0, 102, 558, 799),
                        grade=(1.06, 1.10, 1.08), sharpen=110, out=(640, 800), q=82,
                        name="choc-frappe.webp"),
    # sweetFrog cup + shake against the pink wall — frozen yogurt page
    "froyo-duo": dict(src="froyo-duo.png", crop=None, grade=(1.02, 1.12, 1.18),
                      sharpen=110, out=(900, 1029), q=82, name="froyo-duo.webp"),
    # Peanut Butter Banana Latte poster — menu feature
    "pb-poster": dict(src="pb-poster.png", crop=None, grade=(1.00, 1.05, 1.08),
                      sharpen=70, out=(860, 1082), q=82, name="pb-poster.webp"),
    # froyo swirl cup on gingham — round badge on home + froyo page
    "froyo-swirl": dict(src="froyo-swirl.png", crop=(13, 0, 979, 966),
                        grade=(1.00, 1.03, 1.05), sharpen=60, out=(800, 800), q=82,
                        name="froyo-swirl.webp"),
    # strawberry freeze on the patio table — Pigeon Forge page
    "strawberry-freeze": dict(src="strawberry-freeze.png", crop=None,
                              grade=(1.02, 1.12, 1.15), sharpen=110, out=(960, 949),
                              q=78, name="strawberry-freeze.webp"),
    # two mocha freezes — menu page head
    "frappes-duo": dict(src="frappes-duo.png", crop=None, grade=(1.02, 1.08, 1.08),
                        sharpen=100, out=(868, 934), q=82, name="frappes-duo.webp"),
    # roasted beans macro — dark parallax band behind the reviews section
    "beans": dict(src="beans.png", crop=None, grade=(0.98, 1.05, 1.05),
                  sharpen=60, out=(1600, 894), q=70, name="beans-band.webp"),
    # og image — wide crop of the sunset patio for link previews
    "og": dict(src="hero-patio.png", crop=(0, 417, 1078, 983),
               grade=(1.00, 1.05, 1.10), sharpen=70, out=(1200, 630), q=85,
               name="og-image.jpg"),
    # --- 2026-08 batch: AI-enhanced versions of the shop's own photos
    # (already color-graded upstream, so grade stays neutral)
    # daytime patio, shade sail + green picnic tables — Dollywood page
    "patio-day": dict(src="patio-day.png", crop=None, grade=(1.00, 1.00, 1.00),
                      sharpen=45, out=(1200, 900), q=70, name="patio-day.webp"),
    # patio tables beside the stone fireplace — about page
    "patio-fireside": dict(src="patio-fireside.png", crop=None, grade=(1.00, 1.00, 1.00),
                           sharpen=45, out=(1200, 900), q=70, name="patio-fireside.webp"),
    # string lights over the patio — Pigeon Forge page
    "patio-lights": dict(src="patio-lights.png", crop=None, grade=(1.00, 1.00, 1.00),
                         sharpen=45, out=(1200, 900), q=70, name="patio-lights.webp"),
    # sweetFrog dining room — frozen yogurt page
    "froyo-room": dict(src="froyo-room.png", crop=None, grade=(1.00, 1.00, 1.00),
                       sharpen=45, out=(1200, 900), q=78, name="froyo-room.webp"),
    # self-serve toppings bar — frozen yogurt page
    "froyo-toppings": dict(src="froyo-toppings.png", crop=None, grade=(1.00, 1.00, 1.00),
                           sharpen=45, out=(1200, 900), q=78, name="froyo-toppings.webp"),
    # storefront with both signs — contact page head
    "storefront-facade": dict(src="storefront-facade.png", crop=None, grade=(1.00, 1.00, 1.00),
                              sharpen=45, out=(1200, 900), q=78, name="storefront-facade.webp"),
    # drive-thru lane beside the building — contact page
    "drive-thru": dict(src="drive-thru.png", crop=None, grade=(1.00, 1.00, 1.00),
                       sharpen=45, out=(1200, 900), q=75, name="drive-thru.webp"),
}


def process(spec):
    img = Image.open(RAW / spec["src"])
    img = ImageOps.exif_transpose(img).convert("RGB")
    if spec.get("crop"):
        img = img.crop(spec["crop"])
    if spec.get("fit"):
        img = ImageOps.fit(img, spec["out"], Image.LANCZOS)
    elif spec.get("out"):
        img = img.resize(spec["out"], Image.LANCZOS)
    b, c, s = spec["grade"]
    img = ImageEnhance.Brightness(img).enhance(b)
    img = ImageEnhance.Contrast(img).enhance(c)
    img = ImageEnhance.Color(img).enhance(s)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=spec["sharpen"], threshold=2))
    if spec.get("burn"):
        # darken the bottom ~third with a smooth gradient (photographic burn)
        grad = Image.linear_gradient("L").resize(img.size)
        alpha = grad.point(lambda v: int(max(0, v - 170) / 85 * 110))
        shadow = Image.new("RGB", img.size, (14, 8, 4))
        img = Image.composite(shadow, img, alpha)
    dest = OUT / spec["name"]
    if spec["name"].endswith(".jpg"):
        img.save(dest, "JPEG", quality=spec["q"], optimize=True, progressive=True)
    else:
        img.save(dest, "WEBP", quality=spec["q"], method=6)
    kb = dest.stat().st_size // 1024
    print(f"  wrote images/{spec['name']}  {img.size[0]}x{img.size[1]}  {kb} KB")


if __name__ == "__main__":
    for key, spec in SPECS.items():
        process(spec)
    print("done.")
