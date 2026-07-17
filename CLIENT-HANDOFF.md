# Smoky Mountain Espresso — website handoff

Plain-English guide to what was built, why, and what's left to do before launch.

## What you got

A fast, seven-page website built from the shop's public Facebook page and
Google Business Profile information:

| Page | Who it's for / the search it targets |
|---|---|
| Home (`/`) | "coffee shop sevierville tn" — the front door |
| Menu (`/menu/`) | "smoky mountain espresso menu", drink-name searches |
| Our story (`/about/`) | People checking who's behind the shop; press; AI answers |
| Frozen yogurt (`/frozen-yogurt/`) | "frozen yogurt sevierville", "sweetfrog sevierville" |
| Coffee near Pigeon Forge | "coffee shop near pigeon forge" — tourist traffic |
| Coffee near Dollywood | "coffee near dollywood" — park-day tourists |
| Visit us (`/contact/`) | Hours/directions lookers — the highest-intent visitors |

Every page also answers common questions in a FAQ section with structured
data (FAQPage + CafeOrCoffeeShop schema), which is what gets a business
quoted by Google's rich results and AI assistants like ChatGPT and Claude.
`robots.txt` explicitly welcomes AI crawlers and `llms.txt` gives them a
clean summary of the business.

**Conversion design**: the phone number is a tap-to-call button in the header
of every page, a sticky call/directions/menu bar sits at the thumb on phones,
and every page ends with hours + directions. The Google map only loads when
tapped, which keeps pages loading in well under a second.

## Where the facts came from

Public listings as of July 2026: the shop's Facebook page, Google Business
Profile info surfaced in search, Tripadvisor/Yelp, and Crimson Cup's shop
profile. The review quotes on the home page are lightly trimmed lines from
real public Tripadvisor/Yelp reviews — swap in the owner's favorite Google
reviews any time.

## Before launch — the punch list

1. **Confirm the domain** and find/replace `www.smokymountainespresso.com`
   (details in README). Note: `smokymountainespresso.shop` appears to be an
   unaffiliated scraper site, not the client's property.
2. **Real photos** — the #1 improvement. Photo slots are built into every
   page with placeholders; `PHOTOS.md` has the exact shot list and a script
   that installs them. This build session couldn't download from Facebook
   directly (network policy), so this is a quick manual step. Review-photo
   rights note is in `PHOTOS.md`.
3. **Wire the contact form** to a free Formspree endpoint (README checklist).
   Until then it politely redirects people to the phone.
4. **Confirm hours with the shop** — listings hint they shift seasonally.
5. **Google Business Profile**: make sure the client owns/claims it, then put
   the website URL on it, and replace the footer review link with their direct
   `g.page/r/...` review link.
6. **Search Console**: add the verification tag (TODO slot is in
   `build_site.py`), submit the sitemap.
7. Facts worth double-checking with the owners: founding year (2018),
   owner names (Michael & Karen Williams), the exact aggregate numbers
   (4.6 stars / 800+ five-star reviews / 98% recommend), DoorDash link.

## Not fabricated, on purpose

No invented prices, no invented reviews, no fake license/credential claims,
no stock photos pretending to be the shop. Anything unconfirmed is marked
TODO in the repo rather than guessed at on the live site.

## Making changes later

- Small edits: see README ("Editing workflow"). Never edit `main` directly —
  branches get free preview URLs on Vercel before anything goes live.
- **Edit your site with Claude**: after the repo is on GitHub, send the client
  this link (works once they have a Claude account + GitHub access to the repo):

  ```
  https://claude.ai/code?repositories=fdarnell/smokymountainespresso&prompt=I%20want%20to%20make%20a%20change%20to%20my%20business%20website%20in%20this%20repo.%20Ask%20me%20what%20I%27d%20like%20to%20change%2C%20then%20make%20the%20edit.%20Keep%20the%20site%27s%20existing%20design%2C%20follow%20the%20conventions%20in%20README.md%2C%20and%20never%20edit%20main%20directly%20%E2%80%94%20put%20changes%20on%20a%20branch%20so%20I%20get%20a%20preview%20link%20to%20approve.
  ```

  They describe a change ("update Saturday hours to 9–2"), Claude makes it on
  a branch, and the branch's Vercel preview URL shows the change privately
  before anyone approves it. Keep merge rights with the agency so every edit
  passes through you.

## If you want ongoing SEO growth

The site launches with the two highest-value visitor pages (Pigeon Forge,
Dollywood). Natural next installments, roughly one to two pages a month:
Gatlinburg and Wears Valley visitor pages, a "best things to do in
Sevierville on a rainy day" guide, seasonal-drink pages timed to fall/
Christmas, and a Crust & Crumb bakery spotlight. Each new page is another
search the shop can win. Happy to plan a full content calendar if the client
wants the recurring program.
