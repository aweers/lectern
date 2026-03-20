const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;
const SCROLL_OFFSET = 80;
const CITATION_BACKLINK_SCROLL_OFFSET = 110;

function scrollToAnchor(targetId, offset = SCROLL_OFFSET) {
    const targetElement = document.getElementById(targetId);
    if (!targetElement) return;

    const elementPosition = targetElement.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = html.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        html.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });
}

const tocLinks = document.querySelectorAll('.toc a');
const headings = document.querySelectorAll('.prose h1[id], .prose h2[id], .prose h3[id]');

if (tocLinks.length && headings.length) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    tocLinks.forEach((link) => link.classList.remove('active'));
                    
                    const id = entry.target.getAttribute('id');
                    const activeLink = document.querySelector(`.toc a[href="#${id}"]`);
                    if (activeLink) {
                        activeLink.classList.add('active');
                    }
                }
            });
        },
        {
            rootMargin: '-80px 0px -80% 0px',
            threshold: 0
        }
    );
    
    headings.forEach((heading) => observer.observe(heading));
    
    tocLinks.forEach((link) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').slice(1);
            scrollToAnchor(targetId);
            history.replaceState(null, '', `#${targetId}`);
        });
    });
}

const footnoteLinks = document.querySelectorAll(
    '.footnote-ref a[href^="#fn-"], .footnote-backlink[href^="#fnref-"]'
);

if (footnoteLinks.length) {
    footnoteLinks.forEach((link) => {
        link.addEventListener('click', (e) => {
            const target = link.getAttribute('href');
            if (!target || !target.startsWith('#')) return;

            const targetId = target.slice(1);
            if (!targetId) return;

            e.preventDefault();
            scrollToAnchor(targetId);
            history.replaceState(null, '', target);
        });
    });
}

const citationLinks = document.querySelectorAll(
    '.citation a[href^="#ref-"], .ref-backlink[href^="#cite-"]'
);

if (citationLinks.length) {
    citationLinks.forEach((link) => {
        link.addEventListener('click', (e) => {
            const target = link.getAttribute('href');
            if (!target || !target.startsWith('#')) return;

            const targetId = target.slice(1);
            if (!targetId) return;

            e.preventDefault();
            const offset = link.classList.contains('ref-backlink')
                ? CITATION_BACKLINK_SCROLL_OFFSET
                : SCROLL_OFFSET;
            scrollToAnchor(targetId, offset);
            history.replaceState(null, '', target);
        });
    });
}

const pubImages = document.querySelectorAll('.pub-image img');

if (pubImages.length > 0) {
    const overlay = document.createElement('div');
    overlay.className = 'image-zoom-overlay';
    const overlayImg = document.createElement('img');
    overlay.appendChild(overlayImg);
    document.body.appendChild(overlay);
    
    pubImages.forEach((img) => {
        img.addEventListener('click', (e) => {
            e.stopPropagation();
            overlayImg.src = img.src;
            overlayImg.alt = img.alt;
            overlay.classList.add('active');
        });
    });
    
    overlay.addEventListener('click', () => {
        overlay.classList.remove('active');
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('active')) {
            overlay.classList.remove('active');
        }
    });
}

async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
    }

    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    textarea.style.top = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    document.execCommand('copy');
    textarea.remove();
}

const copyBibtexButtons = document.querySelectorAll('button.copy-bibtex[data-copy-target]');

if (copyBibtexButtons.length) {
    copyBibtexButtons.forEach((button) => {
        button.addEventListener('click', async () => {
            const targetId = button.getAttribute('data-copy-target');
            if (!targetId) return;

            const target = document.getElementById(targetId);
            if (!target) return;

            const text = target.textContent || '';
            if (!text.trim()) return;

            try {
                await copyToClipboard(text);
                const originalText = button.textContent;
                button.textContent = 'Copied';
                button.classList.add('copied');
                window.setTimeout(() => {
                    button.textContent = originalText;
                    button.classList.remove('copied');
                }, 1500);
            } catch {
                // Ignore clipboard failures silently.
            }
        });
    });
}
