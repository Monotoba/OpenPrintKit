# Publishing Documentation

This repo includes a docs/ tree suitable for static site generators like MkDocs. You can publish locally or via GitHub Pages.

## MkDocs (recommended)

1) Install mkdocs (and optionally `mkdocs-material`):
   ```bash
   pip install mkdocs mkdocs-material
   ```
2) Build and serve locally:
   ```bash
   mkdocs serve
   ```
3) Build static site:
   ```bash
   mkdocs build
   ```

A minimal `mkdocs.yml` is included at repo root; adjust nav/theme as desired.

## GitHub Pages

- Configure the repo to serve the `site/` directory (built by MkDocs) via Pages.
- Alternatively, use GitHub Actions to build and deploy. Suggested action: `actions/setup-python` + `mkdocs build` then `peaceiris/actions-gh-pages` to publish.

## Print / PDF

If you have `pandoc`, you can produce a print‑friendly PDF for the user manual:

```bash
# Optional – requires pandoc + LaTeX engine
pandoc docs/user-manual.md -o docs/user-manual.pdf
```

Tip: Browsers can also print `docs/user-manual.md` rendered on the docs site to PDF for a quick export.
