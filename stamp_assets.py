#!/usr/bin/env python3
"""Content-hash every local asset reference so /images, /img, /css and /js can
be cached immutably for a year without ever stranding an edit.

Run this AFTER the site generator. It is idempotent, so running it twice (or
running the generator again and re-running it) is safe.

Order matters and is handled here so callers do not have to think about it:

  1. stamp image references inside css/style.css   (changes the CSS bytes)
  2. recompute the CSS/JS hashes and fix every HTML reference to them
  3. stamp image references inside the HTML

Doing step 1 before step 2 is the whole point: if the stylesheet's own version
query were computed before its contents changed, returning visitors would keep
a cached stylesheet pointing at old image URLs.

Deliberately NOT stamped:
  * absolute/external URLs (another origin's cache is not ours to bust)
  * <meta> content (og:image, twitter:image) — social scrapers re-fetch on
    their own schedule and some normalise query strings away
  * anything already carrying a ?v= — the old stamp is replaced, not appended
"""
import hashlib
import pathlib
import re
import sys

ASSET_DIRS = ("images", "img", "fonts", "models")
VERSIONED_CODE = ("css", "js")
IMG_EXT = r"(?:webp|avif|jpe?g|png|gif|svg|ico|glb|usdz|mp4|webm|woff2?)"


def _hash(path: pathlib.Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:10]


def _resolve(root: pathlib.Path, url: str):
    """Map a root-relative URL to a file on disk, or None if it is not ours."""
    if url.startswith(("http://", "https://", "//", "data:", "mailto:", "tel:", "#")):
        return None
    clean = url.split("?")[0].split("#")[0]
    if not clean.startswith("/"):
        return None
    p = root / clean.lstrip("/")
    return p if p.is_file() else None


def _stamp_url(root: pathlib.Path, url: str) -> str:
    f = _resolve(root, url)
    if f is None:
        return url
    base = url.split("?")[0]
    return f"{base}?v={_hash(f)}"


def stamp_css(root: pathlib.Path) -> int:
    """Rewrite url(...) references to local assets inside every stylesheet."""
    changed = 0
    for css in (root / "css").glob("*.css") if (root / "css").is_dir() else []:
        text = original = css.read_text(encoding="utf-8")

        def repl(m):
            quote, url = m.group("q") or "", m.group("url")
            return f"url({quote}{_stamp_url(root, url)}{quote})"

        text = re.sub(
            r"url\(\s*(?P<q>['\"]?)(?P<url>/(?:%s)/[^)'\"]+?)(?P=q)\s*\)" % "|".join(ASSET_DIRS),
            repl, text)
        if text != original:
            css.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def stamp_html(root: pathlib.Path) -> int:
    """Fix code-asset versions, then stamp image references, in every page."""
    code_ver = {}
    for d in VERSIONED_CODE:
        for f in (root / d).glob("*.*") if (root / d).is_dir() else []:
            if f.suffix in (".css", ".js"):
                code_ver[f"/{d}/{f.name}"] = _hash(f)

    pages = [p for p in root.rglob("*.html") if ".git" not in p.parts]
    touched = 0
    for page in pages:
        text = original = page.read_text(encoding="utf-8")

        # 1. css/js version queries, recomputed from current bytes
        for path, h in code_ver.items():
            text = re.sub(re.escape(path) + r"(\?v=[A-Za-z0-9]+)?",
                          f"{path}?v={h}", text)

        # 2. image-ish references in src / href / srcset / imagesrcset,
        #    skipping <meta ...> so og:image is left alone
        def attr_repl(m):
            if m.group(0).lower().startswith("<meta"):
                return m.group(0)
            return m.group(0)

        def one(m):
            return f'{m.group("a")}="{_stamp_url(root, m.group("url"))}"'

        text = re.sub(
            r'(?P<a>\bsrc|\bhref|\bposter|\bios-src)="(?P<url>/(?:%s)/[^"]+?\.%s)"'
            % ("|".join(ASSET_DIRS), IMG_EXT),
            one, text, flags=re.I)

        def sset(m):
            parts = []
            for chunk in m.group("v").split(","):
                chunk = chunk.strip()
                if not chunk:
                    continue
                bits = chunk.split(None, 1)
                parts.append(" ".join([_stamp_url(root, bits[0])] + bits[1:]))
            return f'{m.group("a")}="{", ".join(parts)}"'

        text = re.sub(r'(?P<a>\bsrcset|\bimagesrcset)="(?P<v>[^"]+)"', sset, text, flags=re.I)

        # never stamp inside <meta ...> tags
        text = re.sub(r"(<meta[^>]*?)\?v=[A-Za-z0-9]+", r"\1", text, flags=re.I)

        if text != original:
            page.write_text(text, encoding="utf-8")
            touched += 1
    return touched


def main(root="."):
    root = pathlib.Path(root).resolve()
    css = stamp_css(root)
    html = stamp_html(root)
    print(f"stamp_assets: {css} stylesheet(s), {html} page(s) updated")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
