---
publish: true
---

# Welcome to Your Blog!

This is an example blog post demonstrating the basic features of this markdown-based blog system.

## What This Blog System Supports

This static blog generator supports a variety of features:

- **Markdown formatting** for easy content creation
- **Syntax highlighting** for code blocks
- **Mathematical equations** using LaTeX
- **Images and media** embedding
- **Tags and categories** for organization
- **Bibliography and citations** support

## Basic Formatting

You can write in **bold**, *italics*, or ***both***. You can also create lists:

This line demonstrates the new styling: **accented bold text** should stand out in both light and dark mode\footnote[You can tune this color in `MARKDOWN_BOLD_COLORS` inside `src/lectern/config.py`.].

1. First item
2. Second item
3. Third item

And unordered lists:

- Point one
- Point two
- Point three

## Code Examples

Here's a simple Python code block:

```python
def hello_world():
    """A simple greeting function."""
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
```

## Mathematical Equations

You can include inline math like $E = mc^2$ or display equations:

$$
\frac{\partial f}{\partial x} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
$$

## Next Steps

To customize this blog:

1. Edit `config.py` to add your personal information
2. Create new blog posts in the `src/blog/` directory
3. Add your profile image to `src/assets/img/`
4. Customize the templates in the `templates/` directory
5. Run `python build.py` to generate your static site

Happy blogging!
