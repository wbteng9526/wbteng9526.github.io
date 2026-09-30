#!/usr/bin/env python3
"""Check migrated content, local destinations, and the homepage asset budget."""

from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
PAGES = ("index.html", "news/index.html", "cv/index.html", "publications/index.html",
         "academic_services/index.html", "404.html")


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.images, self.resources, self.ids, self.scripts = [], [], [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "script":
            self.scripts.append(attrs)
        if "src" in attrs:
            self.resources.append(attrs["src"])
        if tag == "link" and attrs.get("rel") in ("stylesheet", "preload"):
            self.resources.append(attrs["href"])


def destination(source, url):
    parsed = urlsplit(url)
    if parsed.scheme in ("mailto", "tel", "data"):
        return None
    if parsed.netloc and parsed.netloc != "wbteng9526.github.io":
        return None
    path = unquote(parsed.path)
    target = SITE / path.lstrip("/") if path.startswith("/") else source.parent / path
    if not path:
        target = source
    if target.is_dir():
        target /= "index.html"
    return target, parsed.fragment


def check():
    errors = []
    for name in PAGES:
        source = SITE / name
        page = Page(source.read_text())
        if len(page.ids) != len(set(page.ids)):
            errors.append(f"{name}: duplicate element IDs")
        for url in page.links + page.resources:
            result = destination(source, url)
            if result is None:
                continue
            target, anchor = result
            if not target.is_file():
                errors.append(f"{name}: missing local target {url}")
            elif anchor and target.suffix == ".html" and anchor not in Page(target.read_text()).ids:
                errors.append(f"{name}: missing anchor {url}")
        for img in page.images:
            if not all(img.get(key) for key in ("alt", "width", "height")):
                errors.append(f"{name}: image lacks alt text or intrinsic dimensions")

    home = (SITE / "index.html").read_text()
    parsed_home = Page(home)
    titles = re.findall(r"\btitle\s*=\s*\{([^{}]+)\}", (ROOT / "_bibliography/papers.bib").read_text())
    for title in titles:
        if title not in unescape(home):
            errors.append(f"Missing publication: {title}")
    if len(parsed_home.images) != len(titles) + 1:
        errors.append("Homepage should contain one portrait and one thumbnail per paper")
    if parsed_home.scripts:
        errors.append("Homepage unexpectedly loads JavaScript")
    if any(urlsplit(url).netloc for url in parsed_home.resources):
        errors.append("Homepage unexpectedly depends on a third-party resource")
    if any(img.get("loading") != "lazy" for img in parsed_home.images[1:]):
        errors.append("Publication thumbnails must load lazily")
    for thumbnail in (SITE / "assets/img/optimized").glob("*.webp"):
        data = thumbnail.read_bytes()
        if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
            errors.append(f"Invalid WebP file: {thumbnail.name}")

    # Full homepage payload after scrolling, excluding on-demand originals/PDFs.
    assets = {SITE / url.lstrip("/") for url in parsed_home.resources}
    assets.update(SITE / "assets/fonts" / name for name in
                  ("lato-regular.woff2", "lato-bold.woff2", "lato-italic.woff2"))
    payload = (SITE / "index.html").stat().st_size + sum(p.stat().st_size for p in assets)
    if payload > 250_000:
        errors.append(f"Homepage payload exceeds 250 KB: {payload:,} bytes")
    for project in ("arss", "fvgen"):
        for original in (ROOT / project).rglob("*"):
            if original.is_file() and original.name != ".DS_Store":
                copied = SITE / original.relative_to(ROOT)
                if not copied.is_file() or copied.read_bytes() != original.read_bytes():
                    errors.append(f"Project asset was not preserved: {original.relative_to(ROOT)}")
    if (SITE / "assets/pdf/Teng_Wenbin_CV.pdf").read_bytes() != (ROOT / "assets/pdf/Teng_Wenbin_CV.pdf").read_bytes():
        errors.append("CV PDF was not preserved")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(titles)} publications, {len(PAGES)} pages, local links and anchors, "
          f"zero homepage scripts/third-party resources, {payload:,}-byte full homepage payload, "
          "and unchanged project assets/CV PDF.")


if __name__ == "__main__":
    check()
