#!/usr/bin/env python3
"""Assemble the static GitHub Pages site using only Python's standard library."""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_site"
FILES = ("index.html", "stylesheet.css", "404.html", "robots.txt", "sitemap.xml",
         "google66be3b72d36e6749.html")
DIRECTORIES = ("assets", "data", "news", "cv", "publications", "academic_services",
               "arss", "fvgen")


def build():
    # _site is disposable build output, never source or an arbitrary destination.
    if OUTPUT.is_symlink():
        raise RuntimeError("Refusing to replace a symlink at _site")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for name in FILES:
        shutil.copy2(ROOT / name, OUTPUT / name)
    for name in DIRECTORIES:
        shutil.copytree(ROOT / name, OUTPUT / name,
                        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
    (OUTPUT / ".nojekyll").touch()
    print(f"Built static site at {OUTPUT}")


if __name__ == "__main__":
    build()
