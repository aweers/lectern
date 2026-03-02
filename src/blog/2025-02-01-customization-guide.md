---
publish: true
---

# Customizing Your Blog

This guide will help you customize various aspects of your blog to make it truly yours.

## Configuration Options

The main configuration file is `config.py`. Here you can customize:

```python
SITE = {
    "title": "Your Name Here",
    "description": "Your professional tagline",
    "url": "https://yourdomain.com",
    "author": "Your Name",
    "profile_image": "/assets/img/profile.webp",
}
```

## Directory Structure

```
├── src/
│   ├── blog/              # Your blog posts go here
│   ├── assets/
│   │   └── img/          # Images and media files
│   ├── index.md          # Homepage content
│   └── publications.md   # Publications page
├── templates/             # HTML templates
├── static/               # CSS and JavaScript
├── bibliography/         # BibTeX file for citations and publications
└── src/lectern/build.py # Build command module
```

## Creating New Posts

To create a new blog post:

1. Create a new `.md` file in `src/blog/`
2. Use the naming convention: `YYYY-MM-DD-post-title.md`
3. Add frontmatter to opt the post into publishing:

```yaml
---
publish: true
title: Your Post Title
description: Brief description for previews
---
```

## Styling Customization

Edit `static/css/style.css` to customize the appearance:

```css
/* Example: Change primary color */
:root {
    --primary-color: #your-color-here;
    --font-family: 'Your-Font', sans-serif;
}
```

## Adding Interactive Elements

You can add custom JavaScript in `static/js/main.js` for interactive features.

## Template Customization

Templates are located in the `templates/` directory:

- `base.html` - Main layout template
- `blog_post.html` - Individual post template
- `blog_list.html` - Blog listing page
- `home.html` - Homepage template
- `publications.html` - Publications page template

## Tips for Best Results

1. **Keep posts organized**: Use consistent filenames and dating
2. **Optimize images**: Compress images before adding them
3. **Test locally**: Run `uv run python -m lectern.build build` before deploying
4. **Use version control**: Commit regularly to track changes
5. **Add alt text**: Make your content accessible with image descriptions

## Building Your Site

Generate the static site with:

```bash
uv run python -m lectern.build build
```

The output will be in the `dist/` directory, ready to deploy to any static hosting service.

## Deployment Options

This static blog can be deployed to:

- GitHub Pages
- Netlify
- Vercel
- Any static hosting service

Just point your hosting provider to the `dist/` directory.
