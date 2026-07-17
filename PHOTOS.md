# Photos — what goes where

Every page has photo slots already built in. Right now they hold branded
placeholder images; the site works, but it will really come alive once the
real photos are in. This build session's network policy blocked downloading
images directly from Facebook and Google, so installing them is a
two-minute manual job:

## How to install the real photos

1. Open the shop's [Facebook photos](https://www.facebook.com/smespresso/photos)
   (or their Google Business Profile photo section) and download the shots
   listed below. Photos the owners posted themselves are safest to use.
2. Save each one into a `raw-photos/` folder at the root of this repo, named
   for its slot (e.g. `raw-photos/storefront.jpg`).
3. Run `python3 tools/prepare_photos.py` — it crops, resizes, and converts
   each photo and replaces the placeholder automatically.
4. Commit and push.

## The shot list

| Slot filename | What to look for | Used on |
|---|---|---|
| `storefront.jpg` | Exterior of the shop / signage on Middle Creek Rd | Home hero, Contact |
| `fireplace-lounge.jpg` | The couches + fireplace seating area | Home |
| `mocha-freeze.jpg` | A Smoky Mountain Mocha Freeze (or any pretty signature drink) | Menu |
| `pastry-case.jpg` | The Crust & Crumb bakery case | Menu |
| `counter-crew.jpg` | Michael, Karen, and/or the baristas behind the counter | About |
| `froyo-bar.jpg` | The sweetFrog self-serve yogurt machines/toppings bar | Frozen yogurt |
| `coffee-flight.jpg` | A coffee flight board with the small pours | Coffee near Pigeon Forge |
| `nitro-pour.jpg` | Nitro cold brew being poured / a latte-art pour | Coffee near Dollywood |

Landscape orientation works best (everything is cropped to 3:2, 1200x800).

## Rights note (important)

- Photos **the shop posted on its own Facebook/Instagram/GBP** are theirs — use freely.
- Photos **guests attached to Google/Yelp/Tripadvisor reviews** belong to the
  guest. Get a quick OK (a comment or DM works: "Love this shot — mind if we
  use it on our website?") before publishing one, and credit them if they'd like.

## Alt text

Each slot's `alt` text already describes the intended real photo, so no HTML
edits are needed when you swap the files. If you use a noticeably different
shot, update the `alt` in `build_site.py` and re-run `python3 build_site.py`.
