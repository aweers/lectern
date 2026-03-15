#!/usr/bin/env python3
"""Static site generator for markdown blog."""

import html
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import click
import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader
from markdown.extensions.toc import TocExtension
from pybtex.database import parse_file as parse_bib
from pygments.formatters import HtmlFormatter

from lectern.config import LATEST_POSTS_COUNT, MARKDOWN_BOLD_COLORS, NAV, SITE

ROOT = Path(__file__).parent.parent.parent
SRC = ROOT / "src"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
BIBLIOGRAPHY = ROOT / "bibliography"
DIST = ROOT / "dist"

_bibliography_cache = None


def is_truthy_flag(value) -> bool:
    """Normalize boolean-like frontmatter and BibTeX flags."""
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


def find_code_regions(content: str) -> list[tuple[int, int]]:
    """Find ranges for fenced and inline markdown code regions."""
    ranges = []
    length = len(content)
    i = 0

    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_start = 0

    inline_ticks = 0
    inline_start = 0

    def line_end(pos: int) -> int:
        end = content.find("\n", pos)
        return length if end == -1 else end

    while i < length:
        is_line_start = i == 0 or content[i - 1] == "\n"

        if in_fence:
            if is_line_start:
                end = line_end(i)
                line = content[i:end]
                marker_match = re.match(r" {0,3}((`{3,}|~{3,}))(.*)$", line)
                if marker_match:
                    marker = marker_match.group(1)
                    marker_char = marker[0]
                    rest = marker_match.group(3)
                    if (
                        marker_char == fence_char
                        and len(marker) >= fence_len
                        and rest.strip() == ""
                    ):
                        close_end = end + 1 if end < length else end
                        ranges.append((fence_start, close_end))
                        in_fence = False
                        i = close_end
                        continue

            i += 1
            continue

        if is_line_start and inline_ticks == 0:
            end = line_end(i)
            line = content[i:end]
            marker_match = re.match(r" {0,3}((`{3,}|~{3,}))(.*)$", line)
            if marker_match:
                marker = marker_match.group(1)
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
                fence_start = i
                i = end + 1 if end < length else end
                continue

        if content[i] == "`" and not in_fence:
            tick_count = 1
            while i + tick_count < length and content[i + tick_count] == "`":
                tick_count += 1

            if inline_ticks == 0:
                inline_ticks = tick_count
                inline_start = i
                i += tick_count
                continue

            if tick_count == inline_ticks:
                ranges.append((inline_start, i + tick_count))
                inline_ticks = 0
                i += tick_count
                continue

            i += tick_count
            continue

        i += 1

    if in_fence:
        ranges.append((fence_start, length))

    ranges.sort()
    return ranges


def build_emoji_favicon_href(value) -> Optional[str]:
    """Build a SVG data: URL favicon from an emoji string.

    Returns None when the value is missing/empty.
    """
    if value is None:
        return None

    emoji = str(value).strip()
    if not emoji:
        return None

    emoji = html.escape(emoji)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" '
        'viewBox="0 0 100 100">'
        '<text x="50" y="50" font-size="80" text-anchor="middle" dominant-baseline="middle" '
        'font-family="system-ui, Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji">'
        f"{emoji}"
        "</text>"
        "</svg>"
    )
    return "data:image/svg+xml;charset=utf-8," + quote(svg)


def process_footnotes(content: str) -> tuple[str, list]:
    """Replace \\footnote[...] syntax with placeholders."""
    footnotes = []
    output = []
    i = 0
    length = len(content)
    command = "\\footnote"
    code_regions = find_code_regions(content)
    code_region_idx = 0

    while i < length:
        while (
            code_region_idx < len(code_regions)
            and i >= code_regions[code_region_idx][1]
        ):
            code_region_idx += 1

        if (
            code_region_idx < len(code_regions)
            and code_regions[code_region_idx][0] <= i < code_regions[code_region_idx][1]
        ):
            start, end = code_regions[code_region_idx]
            output.append(content[start:end])
            i = end
            continue

        is_command = content.startswith(command, i)
        is_escaped = i > 0 and content[i - 1] == "\\"
        if not is_command or is_escaped:
            output.append(content[i])
            i += 1
            continue

        j = i + len(command)
        while j < length and content[j].isspace():
            j += 1

        if j >= length or content[j] != "[":
            output.append(content[i])
            i += 1
            continue

        k = j + 1
        depth = 1
        note_chars = []

        while k < length:
            ch = content[k]

            if ch == "\\" and k + 1 < length and content[k + 1] == "]":
                note_chars.append("]")
                k += 2
                continue

            if ch == "[":
                depth += 1
                note_chars.append(ch)
                k += 1
                continue

            if ch == "]":
                depth -= 1
                if depth == 0:
                    break
                note_chars.append(ch)
                k += 1
                continue

            note_chars.append(ch)
            k += 1

        if depth != 0:
            output.append(content[i:])
            break

        footnotes.append("".join(note_chars).strip())
        output.append(f"<!--FOOTNOTE_PLACEHOLDER_{len(footnotes) - 1}_END-->")
        i = k + 1

    return "".join(output), footnotes


def render_inline_markdown(content: str) -> str:
    """Render inline markdown without wrapping paragraph tags."""
    html = markdown.markdown(content, extensions=["tables"])
    html = html.replace("</p>\n<p>", "<br><br>")
    html = html.replace("</p><p>", "<br><br>")
    html = re.sub(r"^<p>", "", html)
    html = re.sub(r"</p>$", "", html)
    return html


def restore_footnotes(html: str, footnotes: list) -> str:
    """Replace footnote placeholders with superscript markers and sidenotes."""
    for i, note in enumerate(footnotes):
        number = i + 1
        ref_id = f"fnref-{number}"
        note_id = f"fn-{number}"
        note_html = render_inline_markdown(note) if note else ""
        placeholder = f"<!--FOOTNOTE_PLACEHOLDER_{i}_END-->"
        replacement = (
            f'<sup class="footnote-ref" id="{ref_id}">'
            f'<a href="#{note_id}" aria-describedby="{note_id}">[{number}]</a>'
            "</sup>"
            f'<span class="footnote-sidenote" id="{note_id}">'
            f'<span class="footnote-sidenote-number">[{number}]</span> '
            f'<span class="footnote-sidenote-content">{note_html}</span> '
            f'<a href="#{ref_id}" class="footnote-backlink" '
            'aria-label="Back to reference">↩</a>'
            "</span>"
        )
        html = html.replace(placeholder, replacement)
    return html


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
    content, footnotes = process_footnotes(content)

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
    html = restore_footnotes(html, footnotes)

    result = {"html": html, "toc": toc}
    if process_cites:
        result["citations"] = citations
        result["references_html"] = references_html

    return result


def estimate_reading_time_minutes(content_html: str, words_per_minute: int = 200) -> int:
    """Estimate reading time from HTML content while excluding code blocks."""
    # Drop code sections before counting readable words.
    prose_only = re.sub(r"<pre\b[^>]*>.*?</pre>", " ", content_html, flags=re.DOTALL)
    prose_only = re.sub(r"<code\b[^>]*>.*?</code>", " ", prose_only, flags=re.DOTALL)
    prose_only = re.sub(r"<[^>]+>", " ", prose_only)
    prose_only = html.unescape(prose_only)

    words = re.findall(r"\b[\w'-]+\b", prose_only)
    word_count = len(words)
    return max(1, (word_count + words_per_minute - 1) // words_per_minute)


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
        if not is_truthy_flag(post.get("publish")):
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
        meta["reading_time_minutes"] = estimate_reading_time_minutes(meta["content"])
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
        if not is_truthy_flag(fields.get("publication", "")):
            continue

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
                "selected": is_truthy_flag(fields.get("selected", "")),
                "image": fields.get("image", ""),
            }
        )

    return sorted(pubs, key=lambda p: (p["year"], p["title"]), reverse=True)


def group_publications_by_year(publications: list) -> list:
    """Group publications into reverse-chronological year sections."""
    sections = []

    for pub in publications:
        year = pub["year"] or "Other"
        if sections and sections[-1]["year"] == year:
            sections[-1]["publications"].append(pub)
            continue

        sections.append({"year": year, "publications": [pub]})

    return sections


def generate_pygments_css() -> str:
    """Generate Pygments CSS for github-dark theme."""
    formatter = HtmlFormatter(style="github-dark")
    return formatter.get_style_defs(".highlight")


def generate_theme_overrides_css() -> str:
    """Generate CSS overrides based on site configuration."""
    light_color = str(MARKDOWN_BOLD_COLORS.get("light", "var(--text)")).strip()
    dark_color = str(MARKDOWN_BOLD_COLORS.get("dark", "var(--accent)")).strip()
    return (
        "\n\n/* Lectern config overrides */\n"
        ":root {\n"
        f"    --markdown-strong-color: {light_color};\n"
        "}\n\n"
        '[data-theme="dark"] {\n'
        f"    --markdown-strong-color: {dark_color};\n"
        "}\n"
    )


def build_site():
    """Build the static site."""
    click.echo("Building site...")

    env = Environment(loader=FileSystemLoader(TEMPLATES))
    env.globals["site"] = SITE
    env.globals["nav"] = NAV
    env.globals["current_year"] = datetime.now().year
    env.globals["favicon_href"] = build_emoji_favicon_href(SITE.get("favicon_emoji"))

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
        publication_sections=group_publications_by_year(publications),
    )
    (DIST / "publications" / "index.html").write_text(html)
    click.echo("  Built: publications/index.html")

    shutil.copytree(STATIC, DIST / "static")

    theme_overrides_css = generate_theme_overrides_css()
    pygments_css = generate_pygments_css()
    css_file = DIST / "static" / "css" / "style.css"
    with open(css_file, "a") as f:
        f.write(theme_overrides_css)
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
