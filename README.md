# Smoky Mountain Espresso — website

Static website for Smoky Mountain Espresso, 1259 Middle Creek Rd, Sevierville, TN.
Plain HTML/CSS/JS — no frameworks, no build tools required to *serve* it.
Any static host works; it's set up for Vercel (Framework Preset: **Other**, zero config).

## How the site is put together

- **Pages are generated** by `build_site.py`. Each page's content, title, and
  structured data live in that one file; the shared header/footer/CTA are
  defined once so the phone number, address, and hours can never drift
  between pages. After editing it, run:

  ```
  python3 build_site.py
  ```

  This rewrites every `*/index.html`, plus `sitemap.xml`, `robots.txt`,
  `llms.txt`, and `404.html`. **Don't hand-edit the generated HTML** — your
  change will be lost on the next build. Edit `build_site.py` and rebuild.

- **Business facts** (phone, address, hours, links) live in `site.config.json`
  *and* as constants at the top of `build_site.py`. If a fact changes, update
  both, rebuild, then sanity-check: `grep -r "366-1685" --include="*.html" .`

- **Design** lives in `css/style.css`. The whole palette is CSS custom
  properties in the `:root` block at the top — rebranding is a one-block edit.

- **Photos**: see `PHOTOS.md`. Placeholders are in `images/`; drop real photos
  into `raw-photos/` and run `python3 tools/prepare_photos.py`.

## Editing workflow (edit → preview → publish)

1. **Local preview**: from the repo root run `npx serve .` (or
   `python3 -m http.server 8000`) and open the printed localhost URL.
2. **Staging**: never edit `main` directly. Make changes on a branch
   (e.g. `edits`), push it, and Vercel gives that branch its own preview URL
   to review and share with the client.
3. **Publish**: merge the branch into `main` — Vercel deploys production
   automatically.

## Before launch (one-time checklist)

- [ ] **Domain**: `build_site.py` and `site.config.json` currently use
      `https://www.smokymountainespresso.com` as the canonical domain —
      confirm the real domain, find/replace, rebuild.
      (Heads-up: `smokymountainespresso.shop` looks like an unaffiliated
      scraper site, not the client's.)
- [ ] **Contact form**: create a free form at [formspree.io](https://formspree.io),
      then in `build_site.py` replace `TODO-FORMSPREE-ENDPOINT` with the real
      endpoint URL and rebuild. Until then the form politely tells visitors to
      call instead of silently dropping messages. (If the client is on
      Coraline, use their Coraline form embed instead.)
- [ ] **Real photos**: follow `PHOTOS.md`.
- [ ] **Hours**: confirm current hours with the shop (listings note seasonal shifts).
- [ ] **Google review link**: replace the maps search link in the footer
      ("Leave us a Google review") with the direct review short-link from
      their Business Profile (`g.page/r/...`).
- [ ] **Search Console**: verify the site (paste the verification meta tag
      into the TODO slot in `build_site.py`'s HEAD template, rebuild), then
      submit `sitemap.xml`.

## Deploying to Vercel

1. Push this repo to GitHub.
2. [vercel.com/new](https://vercel.com/new) → import the repo → Framework
   Preset "Other" → Deploy. Clean URLs and `404.html` work automatically;
   `vercel.json` adds the security headers.
