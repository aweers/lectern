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

# Number of latest posts to show on homepage
LATEST_POSTS_COUNT = 3

# Markdown <strong> styling by theme.
# These values are injected into CSS variables at build time.
MARKDOWN_BOLD_COLORS = {
    "light": "#1a1a1a",
    "dark": "#93c5fd",
}
