# Verushka Patel — research portfolio

A minimalist, monochrome, static HTML/CSS site for sharing research with
professors and researchers. No JavaScript framework, no build step, no
backend, no tracking.

## Structure

```
.
├── index.html                              Main page
├── styles.css                              All styling (monochrome, serif)
├── favicon.svg                             VP monogram favicon
├── robots.txt
├── papers/
│   ├── beyond-the-black-swan.pdf           CJSJ paper (original PDF)
│   ├── disclosure-originality.html
│   ├── disclosure-homogenization.html
│   └── convergence-ai-esg.html
└── .build/                                 Tooling used to generate paper pages
    ├── paper-template.html                 Pandoc template
    └── cleanpaper.py                       Post-processor for .docx -> HTML
```

The original `.docx` and `.pdf` source files are kept at the repo root and
are the authoritative source. `papers/*.html` are generated from them.

## Editing the site

### Change the contact email or LinkedIn

Edit `index.html`. Search for `verushkapatel4@gmail.com` and for `LinkedIn`
— each appears in two places (header contact strip + contact section) and
once in the schema.org JSON-LD block. Replace the `#` in the LinkedIn
`href` with your actual profile URL, e.g. `https://www.linkedin.com/in/verushka-patel/`.

### Add or edit a paper entry

Open `index.html`, find the section `<section id="publications">`, and
duplicate an existing `<article class="entry">` block. Each entry needs:

- `<h3>` with the title (optionally linked)
- `.byline` line with status/venue
- `.summary` paragraph with 2–4 plain-language sentences
- `.links` with PDF/HTML links

### Add a new paper PDF or HTML page

Drop PDFs into `papers/` with a clean lowercase, hyphenated filename.
For HTML paper pages, re-run the pandoc build (see below).

### Re-generate paper pages from `.docx`

If you edit a `.docx` and want to rebuild its HTML page:

```bash
# Example: rebuild disclosure-originality.html
pandoc -f docx -t html --template=.build/paper-template.html \
  -M title="Disclosure Originality and Stock Volatility in the Age of AI" \
  -M description="Short description for search engines." \
  -V paperstatus="Working paper &middot; 2026" \
  patel_verushka_disclosure_originality.docx \
  -o papers/disclosure-originality.html

python3 .build/cleanpaper.py \
  papers/disclosure-originality.html \
  "Disclosure Originality and Stock Volatility in the Age of AI"
```

Requires only [pandoc](https://pandoc.org/). No LaTeX or LibreOffice needed.

## Viewing locally

Just open `index.html` in a browser. Or serve the directory:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploying

Two zero-config options, both free and trusted by academics.

### GitHub Pages

1. Create a public GitHub repo and push these files.
2. In the repo, go to **Settings → Pages**.
3. Under **Source**, choose `Deploy from a branch` and select `main` /
   `(root)`. Save.
4. The site will be live at `https://<username>.github.io/<repo>` within
   a minute.

For a custom domain (e.g. `verushkapatel.com`):

1. Add a file named `CNAME` at the repo root containing just your domain.
2. Configure your DNS provider with a `CNAME` record pointing to
   `<username>.github.io`.
3. Re-enable **Enforce HTTPS** in the Pages settings once DNS resolves.

### Netlify

Drag the project folder onto <https://app.netlify.com/drop>. Done.
Netlify will give you a `*.netlify.app` URL and lets you attach a custom
domain from the dashboard.

## Design principles

- Monochrome only. No color accents.
- System serif typography for credibility (reads like a preprint).
- Single column, narrow measure, generous whitespace.
- No gradients, no animation, no icon libraries, no emojis.
- Page weight for `index.html + styles.css` is under 20 KB.
- Full keyboard navigation, honours `prefers-reduced-motion` and
  `prefers-color-scheme`.
- Prints cleanly.
