#!/usr/bin/env python3
"""Static site generator for markdown blog."""

import re
import shutil
from datetime import datetime
from pathlib import Path

import click
import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader
from markdown.extensions.toc import TocExtension
from pybtex.database import parse_file as parse_bib
from pygments.formatters import HtmlFormatter

from lectern.config import LATEST_POSTS_COUNT, NAV, SITE

ROOT = Path(__file__).parent.parent.parent
SRC = ROOT / "src"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
BIBLIOGRAPHY = ROOT / "bibliography"
DIST = ROOT / "dist"

_bibliography_cache = None


def is_published(value) -> bool:
    """Normalize the publish frontmatter flag."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "on"}
    if isinstance(value, int):
        return value != 0
    return False


def load_bibliography() -> dict:
    """Load and cache the bibliography from references.bib."""
    global _bibliography_cache
    if _bibliography_cache is not None:
        return _bibliography_cache

    bib_file = BIBLIOGRAPHY / "references.bib"
    if not bib_file.exists():
        _bibliography_cache = {}
        return _bibliography_cache

    bib = parse_bib(str(bib_file))
    _bibliography_cache = {}

    for key, entry in bib.entries.items():
        fields = entry.fields

        authors_list = []
        for person in entry.persons.get("author", []):
            first = " ".join(person.first_names) if person.first_names else ""
            last = " ".join(person.last_names) if person.last_names else ""
            first = clean_latex(first)
            last = clean_latex(last)
            if first and last:
                authors_list.append(f"{first} {last}")
            elif last:
                authors_list.append(last)

        _bibliography_cache[key] = {
            "key": key,
            "title": clean_latex(fields.get("title", "")),
            "authors": ", ".join(authors_list),
            "year": fields.get("year", ""),
            "venue": clean_latex(fields.get("journal", fields.get("booktitle", ""))),
            "url": fields.get("url", fields.get("html", "")),
        }

    return _bibliography_cache


def process_citations(content: str) -> tuple[str, list]:
    """Process [@key] citations in markdown content."""
    bibliography = load_bibliography()
    citations_used = []
    citation_numbers = {}

    def replace_citation(match):
        key = match.group(1)
        if key not in bibliography:
            return match.group(0)

        if key not in citation_numbers:
            citation_numbers[key] = len(citations_used) + 1
            citations_used.append(bibliography[key])

        num = citation_numbers[key]
        return f'<sup class="citation"><a href="#ref-{key}" id="cite-{key}">[{num}]</a></sup>'

    processed = re.sub(r"\[@([a-zA-Z0-9_:-]+)\]", replace_citation, content)
    return processed, citations_used


def generate_references_html(citations: list) -> str:
    """Generate HTML for the references section."""
    if not citations:
        return ""

    html = ['<section class="references">', "<h2>References</h2>", "<ol>"]

    for cite in citations:
        authors = cite["authors"]
        if authors.count(",") > 2:
            first_author = authors.split(",")[0]
            authors = f"{first_author} et al."

        title = cite["title"]
        year = cite["year"]
        venue = cite["venue"]
        url = cite["url"]
        key = cite["key"]

        html.append(f'  <li id="ref-{key}">')
        if url:
            html.append(f'    <a href="{url}" target="_blank" rel="noopener">{title}</a>')
        else:
            html.append(f"    {title}")
        html.append(f'    <br><span class="ref-authors">{authors}</span>')
        if venue:
            html.append(f'    <span class="ref-venue">{venue}, {year}</span>')
        elif year:
            html.append(f'    <span class="ref-venue">{year}</span>')
        html.append(
            f'    <a href="#cite-{key}" class="ref-backlink" title="Back to citation">↩</a>'
        )
        html.append("  </li>")

    html.append("</ol>")
    html.append("</section>")

    return "\n".join(html)


def protect_math(content: str) -> tuple[str, list]:
    """Protect math blocks from markdown processing."""
    placeholders = []

    def replace_math(match):
        placeholder = f"MATH_PLACEHOLDER_{len(placeholders)}_END"
        placeholders.append(match.group(0))
        return placeholder

    content = re.sub(r"\$\$[\s\S]+?\$\$", replace_math, content)
    content = re.sub(r"\$(?!\s)([^\$\n]+?)(?<!\s)\$", replace_math, content)

    return content, placeholders


def restore_math(html: str, placeholders: list) -> str:
    """Restore math blocks after markdown processing."""
    for i, math in enumerate(placeholders):
        placeholder = f"MATH_PLACEHOLDER_{i}_END"
        html = html.replace(placeholder, math)
    return html


def parse_markdown(content: str, process_cites: bool = False) -> dict:
    """Convert markdown to HTML with extensions."""
    citations = []
    references_html = ""
    if process_cites:
        content, citations = process_citations(content)
        references_html = generate_references_html(citations)

    content, math_placeholders = protect_math(content)

    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "codehilite",
            TocExtension(permalink=True, toc_depth=3),
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": False,
            }
        },
    )
    html = md.convert(content)
    toc = md.toc

    html = restore_math(html, math_placeholders)
    toc = restore_math(toc, math_placeholders)

    result = {"html": html, "toc": toc}
    if process_cites:
        result["citations"] = citations
        result["references_html"] = references_html

    return result


def extract_metadata(filepath: Path, content: str) -> dict:
    """Extract title, date, slug from file."""
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else filepath.stem

    filename = filepath.stem
    date_match = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)", filename)
    if date_match:
        year, month, day, slug = date_match.groups()
        date = datetime(int(year), int(month), int(day))
    else:
        date = None
        slug = filename

    desc_match = re.search(
        r"^#\s+.+\n+(?:\*\*.+\*\*:?\s*)?(.+?)(?:\n\n|\n#|\n---|\n\*\*|$)",
        content,
        re.MULTILINE,
    )
    description = ""
    if desc_match:
        desc = desc_match.group(1).strip()
        desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc)
        desc = re.sub(r"\*\*([^*]+)\*\*", r"\1", desc)
        desc = re.sub(r"\*([^*]+)\*", r"\1", desc)
        desc = re.sub(r"`([^`]+)`", r"\1", desc)
        description = desc[:200]

    return {
        "title": title,
        "date": date,
        "slug": slug,
        "description": description,
    }


def load_posts() -> list:
    """Load all blog posts, sorted by date descending."""
    posts = []
    blog_dir = SRC / "blog"
    if not blog_dir.exists():
        return posts

    for filepath in blog_dir.glob("*.md"):
        post = frontmatter.load(filepath)
        if not is_published(post.get("publish")):
            click.echo(f"  Skipping {filepath.name} (publish is false)")
            continue

        content = post.content
        meta = extract_metadata(filepath, content)

        if meta["date"] is None:
            click.echo(f"  Skipping {filepath.name} (no date in filename)")
            continue

        meta["title"] = post.get("title", meta["title"])
        meta["description"] = post.get("description", meta["description"])

        parsed = parse_markdown(content, process_cites=True)
        meta["content"] = parsed["html"]
        meta["toc"] = parsed["toc"]
        meta["citations"] = parsed.get("citations", [])
        meta["references_html"] = parsed.get("references_html", "")
        meta["url"] = f"/blog/{meta['date'].year}/{meta['slug']}/"
        meta["filepath"] = filepath
        posts.append(meta)

    return sorted(posts, key=lambda p: p["date"], reverse=True)


def clean_latex(text: str) -> str:
    """Clean LaTeX formatting from text."""
    text = text.replace("{", "").replace("}", "")
    replacements = {
        '\\"u': "ü",
        '\\"o': "ö",
        '\\"a': "ä",
        '\\"U': "Ü",
        '\\"O': "Ö",
        '\\"A': "Ä",
        "\\'e": "é",
        "\\'a": "á",
        "\\ss": "ß",
    }
    for latex, char in replacements.items():
        text = text.replace(latex, char)
    return text


def load_publications() -> list:
    """Load publications from BibTeX file."""
    bib_file = BIBLIOGRAPHY / "references.bib"
    if not bib_file.exists():
        return []

    bib = parse_bib(str(bib_file))
    pubs = []

    for key, entry in bib.entries.items():
        fields = entry.fields

        authors_list = []
        for person in entry.persons.get("author", []):
            first = " ".join(person.first_names) if person.first_names else ""
            last = " ".join(person.last_names) if person.last_names else ""
            first = clean_latex(first)
            last = clean_latex(last)
            if first and last:
                author_name = f"{first} {last}"
                if author_name == SITE.get("author", ""):
                    author_name = f"<u>{author_name}</u>"
                authors_list.append(author_name)
            elif last:
                authors_list.append(last)
        authors = ", ".join(authors_list)

        pubs.append(
            {
                "key": key,
                "title": clean_latex(fields.get("title", "")),
                "authors": authors,
                "year": fields.get("year", ""),
                "venue": clean_latex(
                    fields.get("journal", fields.get("booktitle", ""))
                ),
                "abstract": fields.get("abstract", ""),
                "url": fields.get("html", fields.get("url", "")),
                "selected": fields.get("selected", "").lower() == "true",
                "image": fields.get("image", ""),
            }
        )

    return sorted(pubs, key=lambda p: p["year"], reverse=True)


def generate_pygments_css() -> str:
    """Generate Pygments CSS for github-dark theme."""
    formatter = HtmlFormatter(style="github-dark")
    return formatter.get_style_defs(".highlight")


def build_site():
    """Build the static site."""
    click.echo("Building site...")

    env = Environment(loader=FileSystemLoader(TEMPLATES))
    env.globals["site"] = SITE
    env.globals["nav"] = NAV

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    posts = load_posts()
    publications = load_publications()

    click.echo(f"  Found {len(posts)} posts")
    click.echo(f"  Found {len(publications)} publications")

    index_content = ""
    index_file = SRC / "index.md"
    if index_file.exists():
        index_content = parse_markdown(index_file.read_text())["html"]

    template = env.get_template("home.html")
    html = template.render(
        title="Home",
        content=index_content,
        latest_posts=posts[:LATEST_POSTS_COUNT],
        selected_publications=[p for p in publications if p["selected"]],
    )
    (DIST / "index.html").write_text(html)
    click.echo("  Built: index.html")

    (DIST / "blog").mkdir(parents=True)
    template = env.get_template("blog_list.html")
    html = template.render(title="Blog", posts=posts)
    (DIST / "blog" / "index.html").write_text(html)
    click.echo("  Built: blog/index.html")

    template = env.get_template("blog_post.html")
    for post in posts:
        post_dir = DIST / "blog" / str(post["date"].year) / post["slug"]
        post_dir.mkdir(parents=True, exist_ok=True)
        html = template.render(title=post["title"], post=post)
        (post_dir / "index.html").write_text(html)
    click.echo(f"  Built: {len(posts)} blog posts")

    (DIST / "publications").mkdir()
    pub_content = ""
    pub_file = SRC / "publications.md"
    if pub_file.exists():
        pub_content = parse_markdown(pub_file.read_text())["html"]

    template = env.get_template("publications.html")
    html = template.render(
        title="Publications",
        content=pub_content,
        publications=publications,
    )
    (DIST / "publications" / "index.html").write_text(html)
    click.echo("  Built: publications/index.html")

    shutil.copytree(STATIC, DIST / "static")

    pygments_css = generate_pygments_css()
    css_file = DIST / "static" / "css" / "style.css"
    with open(css_file, "a") as f:
        f.write("\n\n/* Pygments github-dark syntax highlighting */\n")
        f.write(pygments_css)
    click.echo("  Built: static assets + syntax highlighting CSS")

    src_assets = SRC / "assets"
    if src_assets.exists():
        shutil.copytree(src_assets, DIST / "assets")
        click.echo("  Built: assets")

    click.echo("")
    click.echo(f"Done! Built {len(posts)} posts, {len(publications)} publications")
    click.echo(f"Output: {DIST}")


@click.group()
def cli():
    """Markdown blog static site generator."""
    pass


@cli.command()
def build():
    """Build the site to dist/."""
    build_site()


@cli.command()
def clean():
    """Remove the dist/ directory."""
    if DIST.exists():
        shutil.rmtree(DIST)
        click.echo("Cleaned dist/")
    else:
        click.echo("Nothing to clean")


if __name__ == "__main__":
    cli()
