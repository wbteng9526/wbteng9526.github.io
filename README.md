# Wenbin Teng's personal website

Published at **https://wbteng9526.github.io/**. The homepage uses the typography,
colors, 800 px layout, portrait treatment, and publication rows from
[Jon Barron's source code](https://github.com/jonbarron/jonbarron.github.io).
It is plain HTML and CSS, with no homepage JavaScript or third-party asset requests.

## Preview and validate

Python 3.9 or newer is sufficient; no packages, Ruby, Node, or Docker are needed.

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open http://127.0.0.1:8000/. Re-run the build and reload after editing files.
`_site/` is disposable output and is replaced by each build.

## Editing

- `index.html`: biography, contact links, all news from 2025 onward (newest first), all publications,
  and academic services. This is now the primary source, like Jon Barron's template.
- `news/index.html`: full news archive, including announcements before 2025.
- `cv/index.html`: existing CV content; the original PDF remains at
  `assets/pdf/Teng_Wenbin_CV.pdf`.
- `stylesheet.css`: template styling and the small-screen layout.
- `assets/img/optimized/`: checked-in, resized WebP images. Click a publication
  image to see its original. Preserve the alpha channel when resizing transparent
  PNGs so they render correctly on the white page background. The Light Sampling
  preview uses the white-background pipeline figure from its
  [project page](https://jingyangcarl.github.io/LightSamplingField/).
- `assets/fonts/`: the template's original Latin Lato regular, bold, and italic
  WOFF2 files, served locally. The font license is `Lato-OFL.txt`.
- `data/`: downloadable BibTeX.

For a new publication, copy a publication row in `index.html`, add a small thumbnail,
and keep `_bibliography/papers.bib` in sync. The content check ensures bibliography
titles are present on the homepage. Update both news lists when adding an announcement.

The old al-folio/Jekyll files (`_pages`, `_layouts`, `_includes`, `_posts`, `_config.yml`,
and related files) remain in the repository as migration reference. They are no longer
compiled or published. Editing them alone will not update the new site.

## Deployment and existing URLs

The `Deploy site` GitHub Actions workflow builds and validates pull requests. Pushes
to `main` publish `_site/` to the existing `gh-pages` branch using the existing deploy
action. GitHub Pages should continue using **gh-pages / (root)**. The repository name,
GitHub Pages hostname, and project paths do not change. No custom domain is introduced.

- `/`: new homepage.
- `/publications/`: redirects to `/#publications`.
- `/academic_services/`: redirects to `/#academic-services`.
- `/news/` and `/cv/`: preserved, with the same typography as the homepage.
- `/arss/` and `/fvgen/`: copied without changes, including every project asset.
- Existing `/assets/...` URLs, CV PDF, and Google verification file remain available.

Unused al-folio example blogs/projects are not included in the new build. Their source
is retained. The two research project pages keep their original dependencies and styling;
the homepage performance improvements do not change those pages.

## Performance findings

The old live homepage HTML referenced nine `*-480.webp` publication thumbnails, all
of which returned HTTP 404 when checked on September 30, 2026. Its image error handler
removed every responsive source on the page, falling back to the original images.
All nine publication images were marked `loading="eager"`, despite the lazy-loading
setting in the Jekyll configuration. Their original files total about 22.5 MB.

The old homepage also referenced 18 script files and seven stylesheet files, including
Bootstrap/MDB, jQuery, MathJax, masonry, icon fonts, and publication badge scripts.
`defer` on a stylesheet link does not make it non-blocking. The legacy Lighthouse
workflow was checking the al-folio demo URL, not this website.

The new homepage uses actual checked-in WebP thumbnails, explicit image dimensions,
lazy loading for publications, a high-priority portrait, one stylesheet, and locally
served Lato fonts. Its complete HTML/CSS/fonts/images payload is under 250 KB before
HTTP compression, even after scrolling through all publications. Original images and
the PDF download only when clicked. This is an asset-size comparison, not a measured
production load-time or Lighthouse score.

The biography, publication venues, news, and reviewing history include the owner's
updates supplied during the migration. Older announcements retain their dated wording.
