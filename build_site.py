#!/usr/bin/env python3
"""
Static site generator for smokymountainespresso — adapted from the
local-business-website skill's generate_pages.py.

Defines the shared chrome (head, header, footer, CTA strip) ONCE and every
page as a spec, then writes <path>/index.html into the repo root, plus
sitemap.xml, robots.txt, llms.txt and 404.html.

Run:  python3 build_site.py
Facts live in site.config.json AND in the constants below — keep both in sync.
Enforces: unique titles/descriptions, breadcrumb JSON-LD from specs.
"""
import json
import pathlib

DOMAIN = "https://www.smokymountainespresso.com"  # TODO: confirm real domain before launch

NAME = "Smoky Mountain Espresso"
PHONE = "(865) 366-1685"
TEL = "+18653661685"
STREET = "1259 Middle Creek Rd"
CITY = "Sevierville"
STATE = "TN"
ZIP = "37862"
ADDR = f"{STREET}, {CITY}, {STATE} {ZIP}"
MAPS = "https://www.google.com/maps/search/?api=1&query=Smoky+Mountain+Espresso+1259+Middle+Creek+Rd+Sevierville+TN+37862"
FACEBOOK = "https://www.facebook.com/smespresso/"
INSTAGRAM = "https://www.instagram.com/smespresso/"
DOORDASH = "https://www.doordash.com/store/smoky-mountain-espresso-sevierville-30429526"

# ---------------------------------------------------------------- inline SVG
I_PHONE = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.08 4.18 2 2 0 0 1 4.06 2h3a2 2 0 0 1 2 1.72c.13.96.37 1.9.72 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.35 1.85.59 2.81.72A2 2 0 0 1 22 16.92z"/></svg>'
I_PIN = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
I_CLOCK = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
I_STAR = '<svg class="ic" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'
I_ARROW = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>'

LOGO_MARK = (
    '<svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true">'
    '<circle cx="24" cy="24" r="22" fill="var(--roast)"/>'
    '<path d="M8 33l9-13 6 8 4-5 13 10z" fill="var(--cream)" opacity=".92"/>'
    '<path d="M8 33l9-13 4 5.5L14 33z" fill="var(--smoke)" opacity=".85"/>'
    '<path d="M20 14c-1.6-2 .8-3 .4-4.8M25.5 14c-1.6-2 .8-3 .4-4.8" stroke="var(--cream)" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    "</svg>"
)

RIDGE = (
    '<div class="ridge{cls}" aria-hidden="true"><svg viewBox="0 0 1440 90" preserveAspectRatio="none">'
    '<path d="M0 70L160 30l140 34 180-48 170 42 160-30 190 44 150-36 160 28 130-20v46H0z" class="r1"/>'
    '<path d="M0 90L200 56l180 26 210-40 200 34 220-26 210 30 220-22v32H0z" class="r2"/>'
    "</svg></div>"
)

# ------------------------------------------------------------------- chrome
HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<!-- TODO: paste Google Search Console verification meta tag here -->
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta property="og:image" content="{domain}/images/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/style.css">
{jsonld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

NAV_ITEMS = [
    ("Home", "/", "home"),
    ("Menu", "/menu/", "menu"),
    ("Frozen yogurt", "/frozen-yogurt/", "froyo"),
    ("Our story", "/about/", "about"),
    ("Visit us", "/contact/", "contact"),
]


def header(nav_key):
    CUR = ' aria-current="page"'
    links = "".join(
        f'<li><a href="{url}"{CUR if key == nav_key else ""}>{label}</a></li>'
        for label, url, key in NAV_ITEMS
    )
    return f"""<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="/">{LOGO_MARK}<span class="brand-text"><span class="brand-top">Smoky Mountain</span><span class="brand-bottom">Espresso</span></span></a>
    <nav class="site-nav" aria-label="Main">
      <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu"><span class="nav-bars" aria-hidden="true"></span>Menu</button>
      <ul id="nav-menu">{links}</ul>
    </nav>
    <a class="btn btn-call header-call" href="tel:{TEL}">{I_PHONE}<span>{PHONE}</span></a>
  </div>
</header>
<main id="main">
"""


CTA_STRIP = f"""<section class="cta-strip">
  <div class="wrap cta-inner">
    <div>
      <h2>Come sit by the fire</h2>
      <p>Open seven days a week at {ADDR} — about ten minutes from both Dollywood and the Pigeon Forge Parkway.</p>
    </div>
    <div class="cta-buttons">
      <a class="btn btn-solid" href="tel:{TEL}">{I_PHONE}<span>Call {PHONE}</span></a>
      <a class="btn btn-ghost" href="{MAPS}" rel="noopener">{I_PIN}<span>Get directions</span></a>
    </div>
  </div>
</section>
"""

FOOTER = f"""</main>
{RIDGE.format(cls=" ridge-dark")}
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="footer-brand">Smoky Mountain Espresso</p>
      <address>
        {STREET}<br>{CITY}, {STATE} {ZIP}<br>
        <a href="tel:{TEL}">{PHONE}</a>
      </address>
      <p class="footer-social">
        <a href="{FACEBOOK}" rel="noopener">Facebook</a> ·
        <a href="{INSTAGRAM}" rel="noopener">Instagram</a> ·
        <a href="{DOORDASH}" rel="noopener">DoorDash</a>
      </p>
    </div>
    <div>
      <p class="footer-head">Hours</p>
      <ul class="footer-hours">
        <li><span>Mon – Thu</span><span>7:30 AM – 9:00 PM</span></li>
        <li><span>Fri – Sat</span><span>7:30 AM – 9:30 PM</span></li>
        <li><span>Sunday</span><span>1:00 PM – 9:00 PM</span></li>
      </ul>
    </div>
    <div>
      <p class="footer-head">Pages</p>
      <ul class="footer-links">
        <li><a href="/menu/">Menu</a></li>
        <li><a href="/frozen-yogurt/">sweetFrog frozen yogurt</a></li>
        <li><a href="/about/">Our story</a></li>
        <li><a href="/contact/">Hours &amp; directions</a></li>
        <li><a href="/coffee-near-pigeon-forge/">Coffee near Pigeon Forge</a></li>
        <li><a href="/coffee-near-dollywood/">Coffee near Dollywood</a></li>
      </ul>
    </div>
    <div>
      <p class="footer-head">Love the shop?</p>
      <p class="footer-note">Reviews from regulars are how new folks find us. <a href="{MAPS}" rel="noopener">Leave us a Google review</a> — it means more than you'd think.</p>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <p>&copy; 2026 Smoky Mountain Espresso · {ADDR}</p>
    <p class="footer-legal"><a href="/privacy-policy/">Privacy policy</a> · <a href="/terms-of-service/">Terms of service</a> · <a href="/accessibility/">Accessibility</a></p>
  </div>
</footer>
<div class="mobile-bar">
  <a href="tel:{TEL}">{I_PHONE}<span>Call</span></a>
  <a href="{MAPS}" rel="noopener">{I_PIN}<span>Directions</span></a>
  <a href="/menu/">{I_ARROW}<span>Menu</span></a>
</div>
<script src="/js/main.js" defer></script>
</body>
</html>
"""

# --------------------------------------------------------------- JSON-LD
BUSINESS_LD = {
    "@context": "https://schema.org",
    "@type": "CafeOrCoffeeShop",
    "@id": DOMAIN + "/#business",
    "name": "Smoky Mountain Espresso",
    "alternateName": "Smoky Mountain Espresso Coffee & Tea",
    "url": DOMAIN + "/",
    "telephone": TEL,
    "priceRange": "$",
    "image": DOMAIN + "/images/og-image.jpg",
    "servesCuisine": ["Coffee", "Tea", "Frozen yogurt", "Pastries"],
    "foundingDate": "2018",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": STREET,
        "addressLocality": CITY,
        "addressRegion": STATE,
        "postalCode": ZIP,
        "addressCountry": "US",
    },
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"], "opens": "07:30", "closes": "21:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Friday", "Saturday"], "opens": "07:30", "closes": "21:30"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "13:00", "closes": "21:00"},
    ],
    "areaServed": ["Sevierville TN", "Pigeon Forge TN", "Gatlinburg TN"],
    "sameAs": [FACEBOOK, INSTAGRAM],
}


def faq_ld(pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }


def faq_html(heading, pairs):
    items = "".join(
        f"<details class=\"faq\"><summary>{q}</summary><div class=\"faq-a\"><p>{a}</p></div></details>"
        for q, a in pairs
    )
    return f'<section class="section faq-section"><div class="wrap wrap-narrow"><h2>{heading}</h2>{items}</div></section>'


def crumb_ld(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u}
            for i, (n, u) in enumerate(items)
        ],
    }


# ================================================================== PAGES
# ------ home
HOME_FAQ = [
    ("What time does Smoky Mountain Espresso open?", "We open at 7:30 AM Monday through Saturday and at 1:00 PM on Sundays. We close at 9:00 PM most nights and 9:30 PM on Friday and Saturday. Hours can shift with the season, so call (865) 366-1685 if you're making a special trip."),
    ("Does Smoky Mountain Espresso serve food?", "Yes — the bakery case is stocked with muffins, bagels, and pastries baked by Crust &amp; Crumb Bakery in Gatlinburg, and there's a self-serve sweetFrog frozen yogurt bar inside the shop."),
    ("Is Smoky Mountain Espresso kid-friendly?", "Very. Kids can build their own frozen yogurt at the sweetFrog bar while you drink your coffee like a civilized person, and there's plenty of comfortable seating for families."),
    ("Can I get Smoky Mountain Espresso delivered?", "Yes — we're on DoorDash for delivery around Sevierville and Pigeon Forge. Most people still come in, though. The fireplace doesn't deliver."),
]

HOME_BODY = f"""<section class="hero hero-photo-hero">
  <div class="hero-bg" aria-hidden="true"><img src="/images/hero-patio.webp" width="1080" height="1437" fetchpriority="high" alt=""></div>
  <div class="hero-scrim" aria-hidden="true"></div>
  <div class="wrap hero-inner">
    <p class="kicker">Sevierville, Tennessee · pouring since 2018</p>
    <h1>A Sevierville coffee shop worth slowing down for</h1>
    <p class="lede">Espresso drinks people plan their vacations around, sweetFrog frozen yogurt under the same roof, and a fireplace that makes it hard to leave. Find us at {STREET}, about ten minutes from Dollywood.</p>
    <div class="hero-buttons">
      <a class="btn btn-solid" href="tel:{TEL}">{I_PHONE}<span>Call {PHONE}</span></a>
      <a class="btn btn-ghost" href="/menu/">{I_ARROW}<span>See the menu</span></a>
    </div>
    <ul class="proof-chips">
      <li>{I_STAR}4.6 stars on Google</li>
      <li>800+ five-star reviews</li>
      <li>98% recommend on Facebook</li>
    </ul>
  </div>
</section>
{RIDGE.format(cls="")}
<section class="section">
  <div class="wrap wrap-narrow">
    <h2>Coffee first, everything else second</h2>
    <p>Michael and Karen Williams opened this shop in 2018 with zero coffee-industry experience and a stubborn idea about how a coffee shop should feel. Eight years on, Smoky Mountain Espresso has racked up more than 800 five-star Google reviews and sits near the top of every coffee ranking in Sevier County.</p>
    <p>The espresso itself comes from <a href="/about/">Crimson Cup Coffee &amp; Tea</a>, an award-winning Ohio roaster, and it's pulled all day long — hot, iced, frozen, or on nitro tap. If you don't see what you want on the board, ask. The crew builds custom drinks constantly.</p>
  </div>
</section>
<section class="cup-band" id="cup-band" aria-label="Interactive 3D espresso cup">
  <script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@4.2.0/dist/model-viewer.min.js"></script>
  <model-viewer
    src="/models/smoky-espresso-cup-web.glb"
    ios-src="/models/smoky-espresso-cup-web.usdz"
    alt="A Smoky Mountain Espresso cup in 3D — it spins as you scroll; drag to rotate, or tap the AR button to see it on your own table"
    camera-orbit="0deg 75deg 105%"
    camera-controls
    disable-zoom
    touch-action="pan-y"
    ar
    ar-modes="webxr scene-viewer quick-look"
    shadow-intensity="1"
    loading="lazy"></model-viewer>
  <p class="cup-band-hint">Scroll to spin the cup — or drag it, and tap the cube to set it on your own table in AR.</p>
</section>
<script>
(function () {{
  var band = document.getElementById('cup-band');
  var mv = band.querySelector('model-viewer');
  var ticking = false;
  window.addEventListener('scroll', function () {{
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {{
      var r = band.getBoundingClientRect();
      var p = Math.min(1, Math.max(0, (window.innerHeight - r.top) / (window.innerHeight + r.height)));
      mv.cameraOrbit = (p * 360).toFixed(1) + 'deg 75deg 105%';
      ticking = false;
    }});
  }}, {{ passive: true }});
}})();
</script>
<section class="section section-tint">
  <div class="wrap">
    <h2>What people drive across Sevier County for</h2>
    <div class="card-grid">
      <article class="card"><h3>Smoky Mountain Mocha Freeze</h3><p>The house signature: white chocolate and caramel sauces blended with espresso and ice. Order it once and you'll understand the line.</p></article>
      <article class="card"><h3>Red velvet latte</h3><p>Just enough sweetness to balance the espresso without burying it. A regulars' favorite year-round.</p></article>
      <article class="card"><h3>Nitro cold brew</h3><p>Cold-brewed coffee on a nitrogen tap — smooth, creamy, no sugar needed. The summer answer to a hot mountain afternoon.</p></article>
      <article class="card"><h3>Coffee flights</h3><p>Can't pick one? Get a flight of small pours and try several drinks in one sitting. Popular with first-timers for a reason.</p></article>
    </div>
    <p class="section-cta"><a class="btn btn-solid" href="/menu/">{I_ARROW}<span>Browse the full menu</span></a></p>
  </div>
</section>
<section class="marquee-band" aria-label="Photos of drinks from Smoky Mountain Espresso">
  <div class="marquee-track">
    <figure class="marquee-item"><img src="/images/frappes-duo.webp" width="868" height="934" loading="lazy" alt="Two Smoky Mountain Mocha Freezes drizzled with chocolate"></figure>
    <figure class="marquee-item"><img src="/images/strawberry-freeze.webp" width="960" height="949" loading="lazy" alt="A strawberry freeze piled with whipped cream on the patio"></figure>
    <figure class="marquee-item"><img src="/images/pb-poster.webp" width="860" height="1082" loading="lazy" alt="Peanut Butter Banana Latte — served hot, iced, or frozen"></figure>
    <figure class="marquee-item"><img src="/images/choc-frappe.webp" width="640" height="800" loading="lazy" alt="A chocolate mocha freeze with whipped cream and chocolate drizzle"></figure>
    <figure class="marquee-item"><img src="/images/froyo-swirl.webp" width="800" height="800" loading="lazy" alt="A sweetFrog frozen yogurt swirl with peanut butter drizzle"></figure>
    <figure class="marquee-item"><img src="/images/froyo-duo.webp" width="900" height="1029" loading="lazy" alt="A sweetFrog frozen yogurt cup with fresh fruit next to a caramel shake"></figure>
    <figure class="marquee-item" aria-hidden="true"><img src="/images/frappes-duo.webp" width="868" height="934" loading="lazy" alt=""></figure>
    <figure class="marquee-item" aria-hidden="true"><img src="/images/strawberry-freeze.webp" width="960" height="949" loading="lazy" alt=""></figure>
    <figure class="marquee-item" aria-hidden="true"><img src="/images/pb-poster.webp" width="860" height="1082" loading="lazy" alt=""></figure>
    <figure class="marquee-item" aria-hidden="true"><img src="/images/choc-frappe.webp" width="640" height="800" loading="lazy" alt=""></figure>
    <figure class="marquee-item" aria-hidden="true"><img src="/images/froyo-swirl.webp" width="800" height="800" loading="lazy" alt=""></figure>
    <figure class="marquee-item" aria-hidden="true"><img src="/images/froyo-duo.webp" width="900" height="1029" loading="lazy" alt=""></figure>
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div>
      <h2>Built for staying a while</h2>
      <p>This isn't a grab-and-go window. The room is rustic and warm — couches, a fireplace, space for kids — and it fills up with the same mix every day: locals on laptops, church groups, and families thawing out after a day in the mountains.</p>
      <p>The Williams family runs the shop on faith, and it shows in quiet ways: scripture on the walls and a pay-it-forward board where customers leave notes of encouragement, and sometimes a paid-ahead drink for a stranger. Come as you are. Stay longer than you planned.</p>
    </div>
    <figure class="figure"><img src="/images/pay-it-forward.webp" width="1200" height="800" loading="lazy" alt="The pay-it-forward board inside Smoky Mountain Espresso, covered in handwritten notes of encouragement"></figure>
  </div>
</section>
<section class="section section-tint">
  <div class="wrap froyo-strip">
    <figure class="froyo-badge"><img src="/images/froyo-swirl.webp" width="800" height="800" loading="lazy" alt="A sweetFrog frozen yogurt swirl topped with peanut butter drizzle"></figure>
    <div>
      <h2>Frozen yogurt, same roof</h2>
      <p>There's a full self-serve <a href="/frozen-yogurt/">sweetFrog Premium Frozen Yogurt</a> bar inside the shop. Kids build their own cups while you drink your latte in peace — the rare stop that works for the whole crew.</p>
    </div>
    <p><a class="btn btn-ghost" href="/frozen-yogurt/">{I_ARROW}<span>More about sweetFrog</span></a></p>
  </div>
</section>
<section class="section reviews-band">
  <div class="wrap">
    <h2>What regulars say</h2>
    <div class="review-grid">
      <blockquote class="review"><p>"The most friendly staff and best coffee in town."</p><footer>Tripadvisor review</footer></blockquote>
      <blockquote class="review"><p>"We travel to the area four to six times a year, and this is always a must-stop — every day — for great coffee and lattes."</p><footer>Tripadvisor review</footer></blockquote>
      <blockquote class="review"><p>"The kind of coffee shop that makes you feel warm and welcomed."</p><footer>Yelp review</footer></blockquote>
    </div>
    <p class="review-links">Read more on <a href="{MAPS}" rel="noopener">Google</a>, <a href="{FACEBOOK}" rel="noopener">Facebook</a>, or Tripadvisor — then come see for yourself.</p>
  </div>
</section>
<section class="section section-tint">
  <div class="wrap">
    <h2>In town for the mountains?</h2>
    <div class="card-grid card-grid-2">
      <article class="card"><h3><a href="/coffee-near-pigeon-forge/">Staying in Pigeon Forge?</a></h3><p>We're a short hop up Middle Creek Road — real espresso without the Parkway traffic.</p></article>
      <article class="card"><h3><a href="/coffee-near-dollywood/">Headed to Dollywood?</a></h3><p>We open at 7:30, well before the park gates. Fuel up on the way in, wind down on the way out.</p></article>
    </div>
  </div>
</section>
""" + faq_html("Quick answers", HOME_FAQ)

# ------ menu
MENU_FAQ = [
    ("What is the Smoky Mountain Mocha Freeze?", "It's the house signature: white chocolate and caramel sauces blended with espresso and ice. Think frozen mocha, but richer — it's the drink people mention in reviews by name."),
    ("Can the baristas make a custom drink?", "Yes. Custom drinks are half the fun here — tell the crew what you like (sweet, strong, fruity, cold) and they'll build something for you. Plenty of board drinks started as customer experiments."),
    ("Where do the pastries come from?", "The muffins, bagels, and pastries in the case are baked by Crust &amp; Crumb Bakery over in Gatlinburg and delivered fresh."),
    ("Can I order from the menu for delivery?", "Yes — Smoky Mountain Espresso is on DoorDash, covering the Sevierville and Pigeon Forge area."),
]

MENU_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>The menu at Smoky Mountain Espresso</h1>
    <p class="lede">Most drinks come hot, iced, or frozen — your call. Prices are posted at the counter, and seasonal specials rotate on the board. If nothing below sounds right, ask for a custom drink. The crew loves those.</p>
    <figure class="figure figure-tall"><img src="/images/frappes-duo.webp" width="868" height="934" fetchpriority="high" alt="Two Smoky Mountain Mocha Freezes topped with whipped cream and chocolate drizzle"></figure>
  </div>
</section>
<section class="section menu-section">
  <div class="wrap wrap-narrow">
    <h2>House signatures</h2>
    <ul class="menu-list">
      <li><h3>Smoky Mountain Mocha Freeze</h3><p>White chocolate and caramel sauces blended with espresso and ice. The drink this shop is known for.</p></li>
      <li><h3>Tuxedo latte</h3><p>White and dark chocolate together — dressed up, like the name says.</p></li>
      <li><h3>Red velvet latte</h3><p>Sweet enough to counter the espresso, never enough to bury it.</p></li>
      <li><h3>Caramel pecan latte</h3><p>Buttery caramel and toasted pecan — tastes like the Smokies in October.</p></li>
      <li><h3>Peanut butter mocha</h3><p>Peanut butter and chocolate in drinkable form. Yes, it's as good as that sounds.</p></li>
      <li><h3>Hawaiian salted caramel coconut latte</h3><p>Salted caramel with coconut — a beach drink that somehow works in the mountains.</p></li>
    </ul>
    <aside class="menu-feature">
      <figure class="menu-feature-photo"><img src="/images/pb-poster.webp" width="860" height="1082" loading="lazy" alt="Peanut Butter Banana Latte poster — rich and buttery caramel, served hot, iced, or frozen"></figure>
      <div class="menu-feature-copy">
        <p class="kicker">On the board now</p>
        <h2>Peanut Butter Banana Latte</h2>
        <p>Rich, buttery caramel meets peanut butter and banana — the kind of drink you order once as a joke and then every visit after. Hot, iced, or frozen, your call.</p>
      </div>
    </aside>
    <h2>Espresso classics</h2>
    <ul class="menu-list">
      <li><h3>Espresso &amp; americano</h3><p>Crimson Cup espresso, pulled properly. The americano is the local remote-workers' default.</p></li>
      <li><h3>Latte</h3><p>Plain or with any syrup on the shelf. Hot, iced, or frozen.</p></li>
      <li><h3>Cappuccino</h3><p>Traditional ratio, actual foam.</p></li>
      <li><h3>Mocha</h3><p>Chocolate and espresso, hot, iced, or frozen.</p></li>
    </ul>
    <h2>Cold brew &amp; iced</h2>
    <ul class="menu-list">
      <li><h3>Nitro cold brew</h3><p>Slow-steeped, poured from a nitrogen tap. Smooth and naturally sweet — try it black before you doctor it.</p></li>
      <li><h3>Cold brew &amp; iced coffee</h3><p>Straight up or flavored, over ice.</p></li>
      <li><h3>Iced tea</h3><p>Brewed here, sweet or not — this is Tennessee, we won't judge either way.</p></li>
    </ul>
    <h2>Tea, chai &amp; matcha</h2>
    <ul class="menu-list">
      <li><h3>Chai latte</h3><p>Spiced chai with steamed milk. The apple pie chai shows up when the leaves turn.</p></li>
      <li><h3>Matcha latte</h3><p>Earthy green tea, hot or iced.</p></li>
      <li><h3>Hot tea</h3><p>A rotating shelf of black, green, and herbal options.</p></li>
    </ul>
    <h2>Not coffee (still worth the trip)</h2>
    <ul class="menu-list">
      <li><h3>Hot chocolate</h3><p>A kid favorite year-round; the peppermint version arrives with the holidays.</p></li>
      <li><h3>Fruit smoothies</h3><p>Real fruit, blended cold — the caffeine-free answer for the under-ten crowd.</p></li>
      <li><h3>Coffee flights</h3><p>Several small pours on one board, so you can try the signatures side by side.</p></li>
    </ul>
    <h2>The bakery case</h2>
    <ul class="menu-list">
      <li><h3>Muffins, bagels &amp; pastries</h3><p>Baked by Crust &amp; Crumb Bakery in Gatlinburg and delivered fresh. When the case is empty, it's empty — come early.</p></li>
    </ul>
    <div class="callout">
      <h2>sweetFrog frozen yogurt</h2>
      <p>A full self-serve frozen yogurt bar lives inside the shop — flavors, toppings, the works. <a href="/frozen-yogurt/">Here's how it works.</a></p>
    </div>
  </div>
</section>
""" + faq_html("Menu questions", MENU_FAQ)

# ------ about
ABOUT_FAQ = [
    ("Who owns Smoky Mountain Espresso?", "Michael and Karen Williams, who opened the shop in 2018 and still run it. It's an independent, family-owned business — not a chain or a franchise coffee brand."),
    ("What coffee does Smoky Mountain Espresso serve?", "Crimson Cup Coffee &amp; Tea, an award-winning independent roaster out of Columbus, Ohio that partners with independent coffee shops across the country."),
    ("What is the pay-it-forward board?", "A board in the shop where customers leave notes of encouragement — and sometimes pre-pay a drink for a stranger who needs one. It started small and never stopped."),
    ("Why do you open at 1 PM on Sundays?", "Sunday mornings are for church and family in this house. We open the doors at 1:00 and pour until 9:00."),
]

ABOUT_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>Our story: coffee, faith, and a room full of regulars</h1>
    <p class="lede">Smoky Mountain Espresso opened on Middle Creek Road in 2018. Nobody involved had ever worked in coffee. It went better than anyone expected.</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow">
    <h2>Two people, no coffee experience, one good idea</h2>
    <p>Michael and Karen Williams didn't come from the coffee world. What they had was a picture of the shop they wanted: real espresso, a room you'd actually want to sit in, and a business that treated people the way their faith told them to.</p>
    <figure class="figure figure-tall"><img src="/images/sign-bear.webp" width="960" height="1156" loading="lazy" alt="The carved black bear holding a coffee cup under the Smoky Mountain Espresso sign"></figure>
    <p>For the coffee itself, they partnered with <a href="https://www.crimsoncup.com/" rel="noopener">Crimson Cup Coffee &amp; Tea</a>, an award-winning roaster in Columbus, Ohio that has helped hundreds of independent shops open their doors. Crimson Cup trained the team and still supplies every bean pulled here. "Without Crimson Cup, we wouldn't have made it this far," Michael says. "They gave us everything we needed — expertise, quality, and unwavering support."</p>
    <h2>What eight years builds</h2>
    <p>Since 2018 the shop has become the kind of place reviews are written about: more than 800 five-star Google reviews, a 98% recommend rating on Facebook, and a spot at the top of Sevierville's coffee rankings on Yelp and Tripadvisor. Vacationers plan return trips around it. Locals just call it theirs.</p>
    <h2>The faith part, plainly</h2>
    <p>This is a Christian-owned shop and it doesn't hide that — there's scripture on the walls and a pay-it-forward board where strangers cover each other's drinks and leave notes of encouragement. Nobody's checking anyone at the door. Everyone's welcome, every day, exactly as they are.</p>
    <h2>Where the money goes when you buy a latte here</h2>
    <p>Into a family business on Middle Creek Road — not a corporate office three time zones away. Independent shops live and die on regulars and word of mouth, so if you've enjoyed a visit, <a href="{MAPS}" rel="noopener">a Google review</a> genuinely helps keep the lights on and the fireplace burning.</p>
  </div>
</section>
""" + faq_html("About the shop", ABOUT_FAQ)

# ------ frozen yogurt
FROYO_FAQ = [
    ("Is sweetFrog inside Smoky Mountain Espresso?", "Yes — the sweetFrog Premium Frozen Yogurt bar is inside the coffee shop at 1259 Middle Creek Rd in Sevierville. One stop, one register, coffee on one side and froyo on the other."),
    ("How does the self-serve frozen yogurt work?", "Grab a cup, pull the flavors you want from the machines, pile on toppings, and bring it to the counter. Mix as many flavors as you like — that's the point."),
    ("Can we come just for the frozen yogurt?", "Absolutely. Plenty of families do, especially on hot afternoons and after Dollywood. The coffee is here if the grown-ups get tempted, which they usually do."),
    ("What are the frozen yogurt hours?", "Same as the shop: 7:30 AM to 9:00 PM Monday through Thursday, until 9:30 Friday and Saturday, and 1:00 to 9:00 PM on Sundays."),
]

FROYO_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>sweetFrog frozen yogurt in Sevierville — inside the coffee shop</h1>
    <p class="lede">Smoky Mountain Espresso shares its roof with a full self-serve sweetFrog Premium Frozen Yogurt bar. Espresso for you, froyo for the kids, one table for everybody.</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow">
    <h2>Why a coffee shop has a froyo bar</h2>
    <p>Because families travel in packs. Half the group wants a caramel pecan latte, the other half is nine years old. The sweetFrog partnership means nobody loses: kids build their own cups — flavors, toppings, sprinkles, all of it — while the adults sit by the fireplace with something from the <a href="/menu/">espresso menu</a>.</p>
    <figure class="figure figure-tall"><img src="/images/froyo-duo.webp" width="900" height="1029" loading="lazy" alt="A sweetFrog frozen yogurt cup piled with fresh fruit next to a caramel shake"></figure>
    <h2>The best rainy-day move in Sevier County</h2>
    <p>Every Smokies vacation hits one rained-out afternoon. When the mountain trails are mud and the cabin walls are closing in, a warm room with a fireplace, hot chocolate, espresso, and a build-your-own frozen yogurt bar solves the whole day. We've watched it happen from behind the counter about a thousand times.</p>
    <h2>After the park, before the cabin</h2>
    <p>We're about ten minutes from <a href="/coffee-near-dollywood/">Dollywood</a>, right on the way back toward Sevierville. A froyo stop on the drive home beats a meltdown in the parking lot — and we're open until 9:00 most nights, 9:30 on Friday and Saturday.</p>
    <figure class="figure figure-tall"><img src="/images/froyo-swirl.webp" width="800" height="800" loading="lazy" alt="A sweetFrog frozen yogurt swirl with peanut butter drizzle and crushed peanuts"></figure>
  </div>
</section>
""" + faq_html("Frozen yogurt questions", FROYO_FAQ)

# ------ pigeon forge
PF_FAQ = [
    ("Is there a good non-chain coffee shop near Pigeon Forge?", "Yes — Smoky Mountain Espresso, an independent family-owned shop at 1259 Middle Creek Rd in Sevierville, holds a 4.6-star Google rating with over 800 five-star reviews. It's a short drive from the Parkway via Middle Creek Road."),
    ("How do I get there from the Pigeon Forge Parkway?", "Take Wears Valley Rd or Teaster Lane over to Middle Creek Road and follow it toward Sevierville — the shop is at 1259 Middle Creek Rd, on the right. You skip most of the Parkway traffic entirely."),
    ("Is Smoky Mountain Espresso open in the evening?", "Yes — until 9:00 PM Sunday through Thursday and 9:30 PM on Friday and Saturday, which makes it a rare quality-coffee option after dinner or a show."),
    ("Does it work for kids too?", "Better than most: there's a self-serve sweetFrog frozen yogurt bar inside the shop, plus hot chocolate and fruit smoothies on the menu."),
]

PF_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>A coffee shop near Pigeon Forge — without the Parkway crawl</h1>
    <p class="lede">Smoky Mountain Espresso sits on Middle Creek Road, the back way between Pigeon Forge and Sevierville. Real espresso, no bumper-to-bumper, no forty-person line.</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow">
    <h2>The locals' route to better coffee</h2>
    <p>Anyone who's driven the Pigeon Forge Parkway in July knows the math: two miles, forty-five minutes. Middle Creek Road is how locals get around it — and partway up that road, at number 1259, is the coffee shop those same locals actually use. From the middle of Pigeon Forge you're looking at roughly a ten-minute drive on a normal day.</p>
    <p>What's waiting is the opposite of a tourist-strip coffee stand: couches, a fireplace, scripture on the walls, and a <a href="/menu/">menu</a> that runs from a proper cappuccino to the Smoky Mountain Mocha Freeze — white chocolate, caramel, espresso, and ice, blended.</p>
    <figure class="figure figure-tall"><img src="/images/strawberry-freeze.webp" width="960" height="949" loading="lazy" alt="A strawberry freeze piled with whipped cream on the patio at Smoky Mountain Espresso"></figure>
    <h2>Evenings are the secret</h2>
    <p>Most independent coffee around here closes mid-afternoon. This one pours until 9:00 PM on weeknights and 9:30 on Friday and Saturday — after-dinner coffee, dessert froyo for the kids at the <a href="/frozen-yogurt/">sweetFrog bar</a>, and somewhere warm to land after a show without rejoining the Parkway parade.</p>
    <h2>Worth leaving the strip for?</h2>
    <p>The reviews answer that one: 4.6 stars on Google across years of vacationers and regulars, and travelers on Tripadvisor calling it a must-stop on every trip. One reviewer put it simply — "the most friendly staff and best coffee in town."</p>
  </div>
</section>
""" + faq_html("Pigeon Forge visitor questions", PF_FAQ)

# ------ dollywood
DW_FAQ = [
    ("Where can I get coffee before Dollywood opens?", "Smoky Mountain Espresso at 1259 Middle Creek Rd opens at 7:30 AM Monday through Saturday — well before the park gates — and it's about a ten-minute drive from Dollywood's entrance."),
    ("How far is Smoky Mountain Espresso from Dollywood?", "About ten minutes by car. The shop sits on Middle Creek Road on the Sevierville side, and Middle Creek connects straight through toward the Dollywood area."),
    ("What should I order on a park day?", "Going in: a nitro cold brew or an americano travels well. Coming out: the Smoky Mountain Mocha Freeze is basically dessert and air conditioning in a cup, and the kids can hit the sweetFrog frozen yogurt bar."),
    ("Is it open after the park closes?", "Usually, yes — the shop pours until 9:00 PM most nights and 9:30 on Friday and Saturday, while Dollywood's closing time varies by season."),
]

DW_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>Coffee near Dollywood: open before the gates, pouring after the fireworks</h1>
    <p class="lede">Smoky Mountain Espresso is about ten minutes from Dollywood on Middle Creek Road — open at 7:30 AM for the rope-drop crowd and until 9:00 or later for the survivors.</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow">
    <h2>Park days start early</h2>
    <p>If you're doing Dollywood right, you're up before the park is. We open at 7:30 AM Monday through Saturday, which leaves time for a real espresso and a Crust &amp; Crumb muffin from the bakery case before you're standing at the gates. A nitro cold brew rides shotgun just fine.</p>
    <figure class="figure figure-tall"><img src="/images/choc-frappe.webp" width="640" height="800" loading="lazy" alt="A chocolate mocha freeze with whipped cream and chocolate drizzle"></figure>
    <h2>The decompression stop</h2>
    <p>Eight hours of coasters and August heat earns you a soft landing. On the drive back toward Sevierville, the shop shows up right when everyone's fading: frozen drinks and the <a href="/frozen-yogurt/">self-serve sweetFrog bar</a> for the kids, a couch and a quiet latte for whoever did the sunscreen logistics. Most nights we're pouring until 9:00, and until 9:30 on Friday and Saturday.</p>
    <h2>Staying in a cabin nearby?</h2>
    <p>Middle Creek Road and the hills around it are full of rental cabins, and we're the closest real coffee shop for a lot of them. Skip the cabin-coffee-maker disappointment — the <a href="/menu/">full menu</a> is ten minutes away, and DoorDash covers the area if nobody wants to put on shoes.</p>
    <h2>Yes, it beats standing in a park coffee line</h2>
    <p>You're on vacation; drink something worth the trip. This is an independent, family-run shop with a 4.6-star Google rating, espresso from an award-winning roaster, and a Mocha Freeze that reviewers mention by name.</p>
  </div>
</section>
""" + faq_html("Dollywood trip questions", DW_FAQ)

# ------ contact
CONTACT_FAQ = [
    ("Where is Smoky Mountain Espresso located?", "1259 Middle Creek Rd, Sevierville, TN 37862 — on Middle Creek Road between downtown Sevierville and the Dollywood/Pigeon Forge area."),
    ("Is there parking at the shop?", "Yes, there's parking on site. Middle Creek Road traffic is far gentler than the Parkway, even in peak season."),
    ("Do you take large groups?", "Yes — the room handles church groups, youth groups, and family reunions regularly. For a big group, a quick call to (865) 366-1685 ahead of time helps the crew get ready for you."),
    ("What's the fastest way to reach you?", "Call (865) 366-1685 during open hours, or message the shop on Facebook. The form below works too — it's just not watched minute to minute."),
]

CONTACT_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>Visit us on Middle Creek Road</h1>
    <p class="lede">Seven days a week in Sevierville — between downtown and Dollywood, minutes off the Parkway, with parking out front.</p>
    <figure class="figure"><img src="/images/storefront.webp" width="1200" height="800" fetchpriority="high" alt="The stone fireplace patio at Smoky Mountain Espresso, 1259 Middle Creek Rd, at sunset"></figure>
  </div>
</section>
<section class="section">
  <div class="wrap contact-grid">
    <div class="contact-card">
      <h2>{I_PIN}Address</h2>
      <address>{STREET}<br>{CITY}, {STATE} {ZIP}</address>
      <p><a class="btn btn-solid" href="{MAPS}" rel="noopener">{I_PIN}<span>Get directions</span></a></p>
    </div>
    <div class="contact-card">
      <h2>{I_PHONE}Phone</h2>
      <p><a class="tel-big" href="tel:{TEL}">{PHONE}</a></p>
      <p>Call during open hours — or message us on <a href="{FACEBOOK}" rel="noopener">Facebook</a>, we're quick there.</p>
    </div>
    <div class="contact-card">
      <h2>{I_CLOCK}Hours</h2>
      <ul class="hours-table">
        <li><span>Monday – Thursday</span><span>7:30 AM – 9:00 PM</span></li>
        <li><span>Friday – Saturday</span><span>7:30 AM – 9:30 PM</span></li>
        <li><span>Sunday</span><span>1:00 PM – 9:00 PM</span></li>
      </ul>
      <p class="hours-note">Hours can shift with the season — call ahead if you're making a special trip.</p>
    </div>
  </div>
</section>
<section class="section section-tint">
  <div class="wrap wrap-narrow">
    <h2>Find us on the map</h2>
    <div class="map-shell" id="map-shell">
      <div class="map-preview">
        {I_PIN}
        <p><strong>{NAME}</strong><br>{ADDR}</p>
        <button class="btn btn-solid" id="map-load" data-map-src="https://www.google.com/maps?q=Smoky+Mountain+Espresso+1259+Middle+Creek+Rd+Sevierville+TN+37862&output=embed">Load interactive map</button>
        <p class="map-note">The map loads from Google when you tap the button — keeps the page fast.</p>
      </div>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow">
    <h2>Send us a note</h2>
    <p>Group visits, event questions, wholesale, or anything else that isn't urgent. For same-day questions, calling is faster.</p>
    <!-- TODO: replace data-endpoint with a real Formspree endpoint (formspree.io) or a Coraline embed before launch -->
    <form class="contact-form" id="contact-form" method="POST" data-endpoint="TODO-FORMSPREE-ENDPOINT">
      <div class="form-row">
        <label for="cf-name">Name<input id="cf-name" name="name" type="text" autocomplete="name" required></label>
        <label for="cf-phone">Phone<input id="cf-phone" name="phone" type="tel" autocomplete="tel" required></label>
      </div>
      <label for="cf-msg">Message<textarea id="cf-msg" name="message" rows="4" required></textarea></label>
      <button class="btn btn-solid" type="submit">Send message</button>
      <p class="form-status" id="form-status" role="status"></p>
    </form>
  </div>
</section>
""" + faq_html("Visiting questions", CONTACT_FAQ)

# ------ legal pages
# Facts these pages are written around (re-check on every site change — see PHOTOS.md
# pattern): contact form collects name/phone/message (endpoint not yet wired — when it
# goes live on Formspree or Coraline/LeadConnector, NAME the processor below and bump
# the effective date); jsDelivr CDN serves the 3D viewer script on the home page;
# Google Maps loads only when tapped on /contact/; hosting is Vercel; fonts self-hosted;
# NO analytics, ad pixels, ecommerce, accounts, or UGC. If any of that changes,
# update these pages and re-evaluate the cookie-banner answer (currently: not needed).
LEGAL_DATE = "July 19, 2026"

PRIVACY_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>Privacy policy</h1>
    <p class="lede">Effective {LEGAL_DATE}. The short version: we collect very little, we don't sell anything about you, and most of what we know about our customers we learned across the counter.</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow legal-body">
    <h2>Who we are</h2>
    <p>Smoky Mountain Espresso is a family-owned coffee shop at {ADDR}, phone {PHONE}. This policy covers our website; it doesn't change anything about ordering a latte in person.</p>
    <h2>Information you give us</h2>
    <p>If you use the contact form on our <a href="/contact/">Visit us</a> page, we receive the name, phone number, and message you type. If you call us or message us on Facebook, we see what you send there. That's it — the site has no accounts, no ordering, and no newsletter signup.</p>
    <p>Contact form submissions are delivered to us by a form-processing service acting on our behalf, which stores them so we can reply.</p>
    <h2>Information collected automatically</h2>
    <p>Like nearly every website, our hosting provider (Vercel) keeps standard server logs — IP address, pages requested, browser type, and timestamps — used for security and keeping the site running. The interactive 3D coffee cup on our home page loads from a content-delivery network (jsDelivr), which receives the same standard request data when your browser fetches it. The map on the Visit us page loads from Google <em>only if you tap the "Load interactive map" button</em>; until then, Google gets nothing from your visit.</p>
    <p>We do not run analytics trackers, advertising pixels, or retargeting on this site.</p>
    <h2>Text messaging (SMS)</h2>
    <p>If you give us your phone number, we may call or text you back about your question. Message frequency varies; message and data rates may apply. Reply STOP to opt out, HELP for help. No mobile information will be shared with third parties or affiliates for marketing or promotional purposes. Opt-in data and consent are not shared with any third party.</p>
    <h2>How we share information</h2>
    <p>We do not sell personal information, and we don't share it for marketing. The only parties that touch website data are the service providers named above — our hosting provider and our form-processing service — acting on our instructions, plus anyone the law genuinely requires us to answer to.</p>
    <h2>Cookies</h2>
    <p>This site does not set advertising or analytics cookies. If our contact form provider sets a small functional cookie to make the form work, that's the extent of it. There's nothing here that needs a cookie banner, so we don't show one.</p>
    <h2>Retention and security</h2>
    <p>We keep contact messages as long as we need them to help you, then delete them in the ordinary course. We use reasonable safeguards to protect information in our care, but no website can promise absolute security, and we won't pretend otherwise.</p>
    <h2>Children</h2>
    <p>Our shop is family-friendly; our website is a general-audience site and is not directed to children under 13. We don't knowingly collect personal information from children online. If you believe a child has sent us information, call us and we'll delete it.</p>
    <h2>Your choices and rights</h2>
    <p>Want to know what we have about you, or want it deleted? Call {PHONE} or send a note to {ADDR}. We honor these requests for everyone, regardless of which state you live in.</p>
    <h2>Links to other sites</h2>
    <p>We link out to Facebook, Instagram, DoorDash, and Google Maps. Those services have their own privacy practices, and what happens there is governed by their policies, not this one.</p>
    <h2>Changes and contact</h2>
    <p>If we change this policy, we'll update it here and change the effective date at the top. Questions? Call {PHONE}, or just ask at the counter.</p>
  </div>
</section>
"""

TERMS_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>Terms of service</h1>
    <p class="lede">Effective {LEGAL_DATE}. Using this website means you accept these terms. They're short, because this is a coffee shop's website, not a software license.</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow legal-body">
    <h2>What this site is</h2>
    <p>This website tells you about Smoky Mountain Espresso — our menu, hours, location, and story. It's informational. Menu items, prices, and hours can change without notice (especially seasonally); the board and register at {ADDR} are the final word on what's available and what it costs today.</p>
    <h2>Ordering and delivery</h2>
    <p>We don't sell anything through this website. Delivery orders go through DoorDash, a separate company with its own terms, prices, and policies — your DoorDash order is a contract between you and DoorDash under their terms.</p>
    <h2>Our content</h2>
    <p>The text, photos, and design of this site belong to Smoky Mountain Espresso. Please don't republish them as your own. Third-party names and logos that appear here — sweetFrog, Crimson Cup Coffee &amp; Tea, Crust &amp; Crumb Bakery, DoorDash, Google — belong to their respective owners and appear only to describe who we work with.</p>
    <h2>Acceptable use</h2>
    <p>Don't attempt to break, overload, scrape at abusive volume, or misuse this website, and don't use our contact form to send spam or anything unlawful. That's the whole list.</p>
    <h2>No warranties</h2>
    <p>The site is provided "as is." We work to keep the information accurate and the site available, but we don't warrant that it will always be current, error-free, or uninterrupted.</p>
    <h2>Limitation of liability</h2>
    <p>To the fullest extent permitted by law, Smoky Mountain Espresso's total liability arising out of your use of this website will not exceed one hundred dollars ($100). Nothing in these terms limits liability that can't legally be limited.</p>
    <h2>Indemnification</h2>
    <p>If you misuse the site in a way that gets us dragged into a claim, you agree to cover the costs of that claim.</p>
    <h2>Governing law — and a request</h2>
    <p>These terms are governed by Tennessee law, and any dispute belongs in the state or federal courts serving Sevier County, Tennessee. Before it comes to that: call us. {PHONE}. Nearly everything is fixable over a phone call, and we'd rather fix it than litigate it.</p>
    <h2>Changes, severability, contact</h2>
    <p>We may update these terms by posting a new version here with a new effective date. If part of these terms turns out to be unenforceable, the rest still stands. Questions go to {PHONE} or {ADDR}.</p>
  </div>
</section>
"""

A11Y_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>Accessibility statement</h1>
    <p class="lede">Everyone's welcome in the shop, and we want the website to work the same way. Last reviewed {LEGAL_DATE}.</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow legal-body">
    <h2>Our commitment</h2>
    <p>We aim for the Web Content Accessibility Guidelines (WCAG) 2.1, Level AA on this site, and we treat that as ongoing work rather than a one-time checkbox.</p>
    <h2>What's built in</h2>
    <ul>
      <li>Semantic headings and landmarks, plus a skip-to-content link on every page.</li>
      <li>Full keyboard operability with visible focus outlines.</li>
      <li>Descriptive alt text on photographs; decorative duplicates are hidden from screen readers.</li>
      <li>High color contrast between text and backgrounds throughout.</li>
      <li>Motion respect: if your device is set to reduce motion, the site's animations — the hero zoom, the scrolling photo strip, scroll-reveal effects — switch off or become static.</li>
      <li>Responsive layout that works from small phones (320px) up, with no horizontal scrolling.</li>
      <li>Self-hosted fonts, no autoplaying audio or video.</li>
    </ul>
    <h2>Known limitations</h2>
    <p>A few pieces come from third parties and aren't fully under our control: the Google map on the Visit us page (it loads only when you choose to open it, and written directions are always available by phone), the interactive 3D coffee cup on the home page (it's decorative — every piece of information it conveys is also in regular text), and the contact form's processing service. If any of these blocks you, the phone works for everything: {PHONE}.</p>
    <h2>Found a barrier?</h2>
    <p>If something on this site is hard to use with your assistive technology, please tell us — call {PHONE} or ask for the owner at the shop. We'll fix what we can promptly, and in the meantime we'll get you whatever information the page was supposed to provide.</p>
  </div>
</section>
"""

# ---------------------------------------------------------------- specs
PAGES = [
    {
        "path": "/",
        "nav": "home",
        "title": "Smoky Mountain Espresso | Coffee Shop in Sevierville, TN",
        "desc": "Family-owned Sevierville coffee shop near Dollywood — award-winning espresso, sweetFrog frozen yogurt, and a fireplace. Open 7 days. (865) 366-1685.",
        "jsonld": [BUSINESS_LD, faq_ld(HOME_FAQ)],
        "crumbs": None,
        "body": HOME_BODY,
    },
    {
        "path": "/menu/",
        "nav": "menu",
        "title": "Coffee & Drink Menu | Smoky Mountain Espresso",
        "desc": "The full menu: signature lattes, the Smoky Mountain Mocha Freeze, nitro cold brew, coffee flights, chai, smoothies, and fresh Crust & Crumb pastries.",
        "jsonld": [BUSINESS_LD, faq_ld(MENU_FAQ)],
        "crumbs": [["Home", "/"], ["Menu", "/menu/"]],
        "body": MENU_BODY,
    },
    {
        "path": "/about/",
        "nav": "about",
        "title": "Our Story | Smoky Mountain Espresso, Sevierville",
        "desc": "Michael and Karen Williams opened Smoky Mountain Espresso in 2018 — now it's Sevierville's top-rated coffee shop, with 800+ five-star Google reviews.",
        "jsonld": [BUSINESS_LD, faq_ld(ABOUT_FAQ)],
        "crumbs": [["Home", "/"], ["Our story", "/about/"]],
        "body": ABOUT_BODY,
    },
    {
        "path": "/frozen-yogurt/",
        "nav": "froyo",
        "title": "sweetFrog Frozen Yogurt in Sevierville, TN | Inside SME",
        "desc": "Self-serve sweetFrog frozen yogurt inside Smoky Mountain Espresso at 1259 Middle Creek Rd, Sevierville — froyo for the kids, espresso for you.",
        "jsonld": [BUSINESS_LD, faq_ld(FROYO_FAQ)],
        "crumbs": [["Home", "/"], ["Frozen yogurt", "/frozen-yogurt/"]],
        "body": FROYO_BODY,
    },
    {
        "path": "/coffee-near-pigeon-forge/",
        "nav": "",
        "title": "Coffee Shop Near Pigeon Forge, TN | Smoky Mountain Espresso",
        "desc": "Skip the Parkway traffic: an independent coffee shop minutes from Pigeon Forge via Middle Creek Rd, open until 9:00–9:30 PM. 4.6 stars on Google.",
        "jsonld": [
            {**BUSINESS_LD, "@id": DOMAIN + "/coffee-near-pigeon-forge/#business", "areaServed": {"@type": "City", "name": "Pigeon Forge", "containedInPlace": {"@type": "State", "name": "Tennessee"}}},
            faq_ld(PF_FAQ),
        ],
        "crumbs": [["Home", "/"], ["Coffee near Pigeon Forge", "/coffee-near-pigeon-forge/"]],
        "body": PF_BODY,
    },
    {
        "path": "/coffee-near-dollywood/",
        "nav": "",
        "title": "Coffee Near Dollywood | Smoky Mountain Espresso",
        "desc": "Ten minutes from Dollywood on Middle Creek Rd: espresso from 7:30 AM before the gates open, frozen drinks and sweetFrog froyo after the park closes.",
        "jsonld": [
            {**BUSINESS_LD, "@id": DOMAIN + "/coffee-near-dollywood/#business", "areaServed": {"@type": "Place", "name": "Dollywood area, Pigeon Forge, Tennessee"}},
            faq_ld(DW_FAQ),
        ],
        "crumbs": [["Home", "/"], ["Coffee near Dollywood", "/coffee-near-dollywood/"]],
        "body": DW_BODY,
    },
    {
        "path": "/contact/",
        "nav": "contact",
        "title": "Hours, Directions & Contact | Smoky Mountain Espresso",
        "desc": "Smoky Mountain Espresso: 1259 Middle Creek Rd, Sevierville, TN 37862. Open 7 days — call (865) 366-1685 or get directions here.",
        "jsonld": [BUSINESS_LD, faq_ld(CONTACT_FAQ)],
        "crumbs": [["Home", "/"], ["Visit us", "/contact/"]],
        "body": CONTACT_BODY,
    },
    {
        "path": "/privacy-policy/",
        "nav": "",
        "title": "Privacy Policy | Smoky Mountain Espresso",
        "desc": "How Smoky Mountain Espresso handles website information: what the contact form collects, what our host logs, and the short list of services involved.",
        "jsonld": [],
        "crumbs": [["Home", "/"], ["Privacy policy", "/privacy-policy/"]],
        "body": PRIVACY_BODY,
        "cta": False,
    },
    {
        "path": "/terms-of-service/",
        "nav": "",
        "title": "Terms of Service | Smoky Mountain Espresso",
        "desc": "The website terms for smokymountainespresso.com: what the site is for, ordering through DoorDash, our content, and Tennessee governing law.",
        "jsonld": [],
        "crumbs": [["Home", "/"], ["Terms of service", "/terms-of-service/"]],
        "body": TERMS_BODY,
        "cta": False,
    },
    {
        "path": "/accessibility/",
        "nav": "",
        "title": "Accessibility Statement | Smoky Mountain Espresso",
        "desc": "Our WCAG 2.1 AA commitment: keyboard support, alt text, reduced-motion behavior, known third-party limitations, and how to report a barrier.",
        "jsonld": [],
        "crumbs": [["Home", "/"], ["Accessibility", "/accessibility/"]],
        "body": A11Y_BODY,
        "cta": False,
    },
]

NOT_FOUND_BODY = f"""<section class="page-head">
  <div class="wrap wrap-narrow">
    <h1>That page wandered off the trail</h1>
    <p class="lede">No such page here — but the coffee is exactly where it always is: {ADDR}.</p>
    <div class="hero-buttons">
      <a class="btn btn-solid" href="/">{I_ARROW}<span>Back to the home page</span></a>
      <a class="btn btn-ghost" href="/menu/">{I_ARROW}<span>See the menu</span></a>
      <a class="btn btn-ghost" href="tel:{TEL}">{I_PHONE}<span>Call {PHONE}</span></a>
    </div>
  </div>
</section>
"""


def render(spec):
    path = spec["path"]
    url = DOMAIN + path
    lds = list(spec.get("jsonld", []))
    crumbs_html = ""
    if spec.get("crumbs"):
        lds.append(crumb_ld(spec["crumbs"]))
        crumbs_html = '<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap">' + " &rsaquo; ".join(
            f'<a href="{u}">{n}</a>' if u != path else f"<span>{n}</span>"
            for n, u in spec["crumbs"]
        ) + "</div></nav>"
    jsonld = "\n".join(
        '<script type="application/ld+json">' + json.dumps(ld) + "</script>" for ld in lds
    )
    html = HEAD.format(title=spec["title"], desc=spec["desc"], url=url, domain=DOMAIN, jsonld=jsonld)
    html += header(spec.get("nav", ""))
    html += crumbs_html
    html += spec["body"]
    if spec.get("cta", True):
        html += CTA_STRIP
    html += FOOTER
    return html


def main():
    root = pathlib.Path(__file__).parent
    seen_t, seen_d = set(), set()
    urls = []
    for spec in PAGES:
        if spec["title"] in seen_t:
            raise SystemExit(f"DUPLICATE TITLE: {spec['path']}")
        if spec["desc"] in seen_d:
            raise SystemExit(f"DUPLICATE DESC: {spec['path']}")
        seen_t.add(spec["title"])
        seen_d.add(spec["desc"])
        out = root / spec["path"].lstrip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(spec))
        urls.append(DOMAIN + spec["path"])
        print(f"wrote {out.relative_to(root)}")

    # 404 — no canonical/crumbs, noindex
    nf = HEAD.format(
        title="Page Not Found | Smoky Mountain Espresso",
        desc="That page doesn't exist — head back to Smoky Mountain Espresso's home page, menu, or hours.",
        url=DOMAIN + "/404.html", domain=DOMAIN, jsonld="",
    ).replace("<!-- TODO: paste Google Search Console verification meta tag here -->",
              '<meta name="robots" content="noindex">')
    nf += header("") + NOT_FOUND_BODY + CTA_STRIP + FOOTER
    (root / "404.html").write_text(nf)
    print("wrote 404.html")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
    sitemap += "</urlset>\n"
    (root / "sitemap.xml").write_text(sitemap)
    print("wrote sitemap.xml")

    (root / "robots.txt").write_text(f"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
""")
    print("wrote robots.txt")

    (root / "llms.txt").write_text(f"""# Smoky Mountain Espresso

> Independent, family-owned coffee shop at {ADDR}, open since 2018. Award-winning espresso drinks made with Crimson Cup coffee, a self-serve sweetFrog frozen yogurt bar inside the shop, and fresh pastries from Crust & Crumb Bakery (Gatlinburg). About ten minutes from Dollywood and the Pigeon Forge Parkway. Phone: {PHONE}. Open Mon–Thu 7:30 AM–9:00 PM, Fri–Sat 7:30 AM–9:30 PM, Sun 1:00–9:00 PM.

Known for: the Smoky Mountain Mocha Freeze (white chocolate + caramel + espresso, blended), red velvet lattes, nitro cold brew, coffee flights, and a cozy fireplace room. 4.6-star Google rating with 800+ five-star reviews; 98% recommend on Facebook.

## Pages

- [Home]({DOMAIN}/): Overview of the shop, signature drinks, and what to expect
- [Menu]({DOMAIN}/menu/): Full drink and bakery menu — signatures, espresso classics, cold brew, tea, smoothies
- [Our story]({DOMAIN}/about/): Michael and Karen Williams, the 2018 opening, Crimson Cup coffee, and the pay-it-forward board
- [sweetFrog frozen yogurt]({DOMAIN}/frozen-yogurt/): The self-serve froyo bar inside the coffee shop
- [Coffee near Pigeon Forge]({DOMAIN}/coffee-near-pigeon-forge/): Getting here from the Parkway, evening hours
- [Coffee near Dollywood]({DOMAIN}/coffee-near-dollywood/): Pre-park and post-park visits, cabin guests
- [Hours, directions & contact]({DOMAIN}/contact/): Address, phone, hours, map, contact form
- [Privacy policy]({DOMAIN}/privacy-policy/), [Terms of service]({DOMAIN}/terms-of-service/), [Accessibility statement]({DOMAIN}/accessibility/)
""")
    print("wrote llms.txt")


if __name__ == "__main__":
    main()
