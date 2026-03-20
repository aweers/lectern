# Lectern

A lightweight static site generator for academic blogs and portfolios. Built with Python, Lectern generates clean, fast websites from Markdown files with support for academic citations, math equations, and code highlighting.

## Features

- **Markdown-based content** - Write blog posts in Markdown with frontmatter support
- **Academic citations** - Built-in BibTeX citation processing with `[@key]` syntax
- **Sidenotes** - Inline `\footnote[...]` syntax with auto-numbered right-side notes
- **Math equations** - Full LaTeX math support with `$...$` (inline) and `$$...$$` (display)
- **Syntax highlighting** - Code blocks with Pygments (GitHub dark theme)
- **Table of contents** - Automatic TOC generation for blog posts
- **Publications page** - Display academic publications from BibTeX files
- **Responsive design** - Clean, minimal CSS that works on all devices
- **Fast builds** - No JavaScript frameworks, just static HTML

## Installation

Install [uv](https://github.com/astral-sh/uv):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and install dependencies:

```bash
git clone <your-repo-url>
cd lectern
uv sync
```

## Usage

Build the site:

```bash
uv run python -m lectern.build build
```

Build + serve + rebuild on changes (dev mode):

```bash
uv run python -m lectern.build dev
```

Clean build artifacts:

```bash
uv run python -m lectern.build clean
```

Serve locally:

```bash
uv run python -m http.server --directory dist 8000
```

Visit `http://localhost:8000` in your browser.

## Project Structure

```
lectern/
├── src/
│   ├── blog/              # Blog posts (YYYY-MM-DD-slug.md)
│   ├── lectern/           # Core package
│   │   ├── build.py      # Build functions
│   │   └── config.py     # Site configuration
│   ├── assets/            # Images and other assets
│   ├── index.md           # Homepage content
│   └── publications.md    # Publications page content
├── templates/             # Jinja2 HTML templates
├── static/                # Static assets (CSS, JS)
├── bibliography/          # BibTeX file for citations and publications
│   └── references.bib
└── dist/                 # Generated site (gitignored)
```

## Writing Blog Posts

Create a new Markdown file in `src/blog/` with the naming convention: `YYYY-MM-DD-slug.md`

Example:

```markdown
---
publish: true
title: My Blog Post Title
description: Short summary shown on blog index pages
---

# My Blog Post Title

This is the introduction paragraph.

## Section Heading

Your content here...

### Math Support

Inline math: $E = mc^2$

Display math:
$$
\frac{\partial L}{\partial w} = 2(y - \hat{y})x
$$

### Citations

Reference a paper with [@key] where `key` matches an entry in `bibliography/references.bib`.

### Footnotes

Use `\footnote[...]` to create an auto-numbered sidenote in blog content.

Example:

```markdown
Transformer models improved sequence modeling\footnote[See *Attention Is All You Need* for details].
```

### Code Blocks

\```python
def hello_world():
    print("Hello, world!")
\```
```

Notes:

- Posts are discovered from files named `YYYY-MM-DD-slug.md`
- The date is taken from the filename, not frontmatter
- `publish` defaults to `false` if omitted
- Only `publish`, `title`, and `description` are supported frontmatter fields

## Configuration

Edit `src/lectern/config.py` to customize your site:

```python
SITE = {
    "title": "Your Name",
    "description": "Your description",
    "url": "https://yoursite.com",
    "author": "Your Name",
    "favicon_emoji": "📝",
}

MARKDOWN_BOLD_COLORS = {
    "light": "#1a1a1a",
    "dark": "#93c5fd",
}
```

## Managing Publications

Add your citations and publications to `bibliography/references.bib`:

```bibtex
@article{yourkey2025,
  title={Your Paper Title},
  author={Your Name and Coauthor},
  journal={Conference/Journal Name},
  year={2025},
  url={https://link-to-paper.com},
  publication={true},
  selected={true},
  image={publications/yourkey2025.png}
}
```

Use these BibTeX flags:

- `publication={true}` to show an entry on `/publications/`
- `selected={true}` to feature a publication on the homepage
- entries without `publication={true}` can still be cited in blog posts but will not appear on the publications page

## Acknowledgments

Design inspired by [al-folio](https://github.com/alshedivat/al-folio)
