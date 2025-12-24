# Lectern

A lightweight static site generator for academic blogs and portfolios. Built with Python, Lectern generates clean, fast websites from Markdown files with support for academic citations, math equations, and code highlighting.

## Features

- **Markdown-based content** - Write blog posts in Markdown with frontmatter support
- **Academic citations** - Built-in BibTeX citation processing with `[@key]` syntax
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
uv run build.py build
```

Clean build artifacts:

```bash
uv run build.py clean
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
├── bibliography/          # BibTeX files
│   └── references.bib    # Citation references
├── build.py              # Build script entrypoint
└── dist/                 # Generated site (gitignored)
```

## Writing Blog Posts

Create a new Markdown file in `src/blog/` with the naming convention: `YYYY-MM-DD-slug.md`

Example:

```markdown
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

### Code Blocks

\```python
def hello_world():
    print("Hello, world!")
\```
```

## Configuration

Edit `src/lectern/config.py` to customize your site:

```python
SITE = {
    "title": "Your Name",
    "description": "Your description",
    "url": "https://yoursite.com",
    "author": "Your Name",
}
```

## Managing Publications

Add your publications to `bibliography/references.bib`:

```bibtex
@article{yourkey2025,
  title={Your Paper Title},
  author={Your Name and Coauthor},
  journal={Conference/Journal Name},
  year={2025},
  url={https://link-to-paper.com},
  selected={true},
  image={publications/yourkey2025.png}
}
```

## Acknowledgments

Design inspired by [al-folio](https://github.com/alshedivat/al-folio)
