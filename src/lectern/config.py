"""Site configuration for the markdown blog."""

SITE = {
    "title": "Your Name Here",
    "description": "Your professional tagline or short bio goes here",
    "url": "https://yourdomain.com",
    "author": "Your Name",
    "profile_image": "/assets/img/profile.webp",
    # Optional emoji favicon (e.g. "📝"). Set to None or "" to disable.
    "favicon_emoji": None,
}

NAV = [
    {"title": "Home", "url": "/"},
    {"title": "Blog", "url": "/blog/"},
    {"title": "Publications", "url": "/publications/"},
]

FOOTER_LINKS = [
    {"title": "Privacy", "url": "/privacy/"},
    {"title": "Impressum", "url": "/impressum/"},
]

# Number of latest posts to show on homepage
LATEST_POSTS_COUNT = 3

# MathJax configuration.
# Set self_host to True to copy a local MathJax distribution into dist/.
# Install MathJax with `npm install mathjax` or point local_source at another
# directory containing the MathJax es5 files.
MATHJAX = {
    "enabled": True,
    "self_host": False,
    "cdn_url": "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
    "local_source": "node_modules/mathjax/es5",
    "local_output": "static/vendor/mathjax",
    "entrypoint": "tex-mml-chtml.js",
}

# Markdown <strong> styling by theme.
# These values are injected into CSS variables at build time.
MARKDOWN_BOLD_COLORS = {
    "light": "#1a1a1a",
    "dark": "#93c5fd",
}
