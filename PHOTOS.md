# Photos — installed

Real shop photos are now live on every page. The originals live in
`raw-photos/` and the processed versions (cropped, color-graded, sharpened,
WebP) in `images/`. To re-process after swapping a raw photo, run:

    python3 tools/enhance_photos.py

then `python3 build_site.py` and commit. Per-photo crop/grade settings live
at the top of `tools/enhance_photos.py`.

## What's where

| Image | Shot | Used on |
|---|---|---|
| `hero-patio.webp` | Sunset patio + stone fireplace exterior | Home hero (full-bleed background, slow Ken Burns zoom) |
| `storefront.webp` | Same shot, landscape crop | Contact page head |
| `og-image.jpg` | Same shot, 1200x630 | Social link previews (og:image) |
| `pay-it-forward.webp` | The pay-it-forward board (Google overlay cropped out) | Home "Built for staying a while" |
| `sign-bear.webp` | Carved bear under the wall sign | About page |
| `frappes-duo.webp` | Two mocha freezes | Menu head + home marquee |
| `pb-poster.webp` | Peanut Butter Banana Latte poster | Menu "On the board now" feature + marquee |
| `choc-frappe.webp` | Chocolate mocha freeze | Dollywood page + marquee |
| `strawberry-freeze.webp` | Strawberry freeze on the patio | Pigeon Forge page + marquee |
| `froyo-duo.webp` | sweetFrog cup + shake, pink wall | Frozen yogurt page + marquee |
| `froyo-swirl.webp` | sweetFrog swirl with PB drizzle | Home froyo badge (round, bobbing) + froyo page + marquee |
| `beans-band.webp` | Roasted beans macro | Dark parallax band behind home reviews |
| `espresso-bar.jpg` | Espresso bar interior | Background of the 3D cup band |

## Two photos deliberately not used

Two shots in the source folder were Dreamstime stock previews with visible
watermarks (the milk-splash cup and the coffee-bean heart). Publishing
watermarked stock on a commercial site is a copyright problem — if you want
those exact looks, license them (or shoot similar in-store) and drop them
into `raw-photos/`.

## Rights note (still important)

- Photos **the shop posted on its own Facebook/Instagram/GBP** are theirs — use freely.
- Photos **guests attached to reviews** belong to the guest — get a quick OK
  before publishing, and credit them if they'd like.
