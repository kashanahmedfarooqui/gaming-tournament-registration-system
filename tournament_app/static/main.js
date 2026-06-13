
document.addEventListener('DOMContentLoaded', () => {

    const toggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    if (toggle && navLinks) {
        toggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
            const spans = toggle.querySelectorAll('span');
            if (navLinks.classList.contains('open')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
            } else {
                spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
            }
        });

        document.addEventListener('click', (e) => {
            if (!toggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('open');
                toggle.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
            }
        });
    }

    document.querySelectorAll('.flash-msg').forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s, transform 0.5s';
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100%)';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    document.querySelectorAll('.card-countdown[data-date]').forEach(el => {
        const target = new Date(el.dataset.date).getTime();
        function updateTimer() {
            const diff = target - Date.now();
            if (diff <= 0) {
                el.textContent = '⚡ LIVE NOW';
                el.style.color = 'var(--neon-pink)';
                return;
            }
            const days = Math.floor(diff / 86400000);
            const hours = Math.floor((diff % 86400000) / 3600000);
            const mins = Math.floor((diff % 3600000) / 60000);
            if (days > 0) {
                el.textContent = `⏳ ${days}d ${hours}h ${mins}m`;
            } else {
                const secs = Math.floor((diff % 60000) / 1000);
                el.textContent = `⏳ ${hours}h ${mins}m ${secs}s`;
            }
        }
        updateTimer();
        setInterval(updateTimer, 1000);
    });

    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(5, 8, 16, 0.98)';
                navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.5)';
            } else {
                navbar.style.background = 'rgba(5, 8, 16, 0.92)';
                navbar.style.boxShadow = 'none';
            }
        });
    }

    const cards = document.querySelectorAll('.tournament-card, .step-card, .admin-stat-card');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        cards.forEach(card => {
            card.style.animationPlayState = 'paused';
            observer.observe(card);
        });
    }

    const hero = document.querySelector('.hero');
    if (hero) {
        let trail = null;
        hero.addEventListener('mousemove', (e) => {
            if (!trail) {
                trail = document.createElement('div');
                trail.style.cssText = `
                    position: fixed; pointer-events: none; z-index: 9999;
                    width: 300px; height: 300px; border-radius: 50%;
                    background: radial-gradient(circle, rgba(0,255,136,0.06), transparent 70%);
                    transform: translate(-50%, -50%); transition: left 0.1s, top 0.1s;
                `;
                document.body.appendChild(trail);
            }
            trail.style.left = e.clientX + 'px';
            trail.style.top = e.clientY + 'px';
        });
        hero.addEventListener('mouseleave', () => {
            if (trail) { trail.remove(); trail = null; }
        });
    }

    document.querySelectorAll('.admin-table tbody tr').forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.borderLeft = '2px solid var(--neon-purple)';
        });
        row.addEventListener('mouseleave', () => {
            row.style.borderLeft = '';
        });
    });

    document.querySelectorAll('.form-input').forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.style.position = 'relative';
        });
    });

    console.log('%c[NEXUS ARENA] Ready to compete.', 'color: #00ff88; font-family: monospace; font-size: 14px; font-weight: bold;');
});
