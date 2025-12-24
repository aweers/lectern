const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;

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
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                const offset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - offset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
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
