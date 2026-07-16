// Silverwoods Main JS - Animations & Interactions

// Preloader
window.addEventListener('load', () => {
    const preloader = document.getElementById('preloader');
    if (preloader) {
        preloader.style.opacity = '0';
        setTimeout(() => {
            preloader.style.display = 'none';
            animateHero();
        }, 500);
    }
});

// Smooth Scroll
function smoothScroll(e, id) {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
window.smoothScroll = smoothScroll;

// Hero Animations
function animateHero() {
    const elements = document.querySelectorAll('.hero-badge, .hero-title, .hero-subtitle, .hero-desc, .hero-buttons');
    elements.forEach(el => el.classList.add('animated'));

    // Animate stat counters after a delay
    setTimeout(animateStats, 1200);
}

// Stat Counter Animation
function animateStats() {
    const items = document.querySelectorAll('.stat-item');
    items.forEach((item, i) => {
        setTimeout(() => {
            item.classList.add('animated');
            const counter = item.querySelector('[data-count]');
            if (counter) {
                const target = parseInt(counter.getAttribute('data-count'));
                if (!isNaN(target)) animateCounter(counter, target);
            }
        }, i * 150);
    });
}

function animateCounter(el, target, formatter) {
    let current = 0;
    const duration = 2000;
    const step = target / (duration / 16);
    const fmt = formatter || function(n){ return n; };
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            el.textContent = fmt(target);
            clearInterval(timer);
        } else {
            el.textContent = Math.floor(current);
        }
    }, 16);
}

// Scroll Reveal
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            if (entry.target.classList.contains('amenity-card') || entry.target.classList.contains('pricing-card')) {
                const cards = entry.target.parentElement.children;
                const index = Array.from(cards).indexOf(entry.target);
                setTimeout(() => entry.target.classList.add('revealed'), index * 100);
            } else {
                entry.target.classList.add('revealed');
            }
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.section-reveal, .amenity-card, .pricing-card').forEach(el => {
        revealObserver.observe(el);
    });

    // Popup Ads
    if (!window.location.pathname.startsWith('/admin-panel')) loadPopups();
});

var POPUP_INTERVAL = 8 * 60 * 1000;
var _popupTimer = null;

function _canShowPopup() {
    if (window.location.pathname.startsWith('/admin-panel')) return false;
    if (document.fullscreenElement) return false;
    return true;
}

function _schedulePopup(popups, index) {
    index = index || 0;
    var last = parseInt(sessionStorage.getItem('lastPopupTime') || '0');
    var elapsed = last ? Date.now() - last : POPUP_INTERVAL;
    var delay = elapsed >= POPUP_INTERVAL ? 2000 : POPUP_INTERVAL - elapsed;
    if (_popupTimer) clearTimeout(_popupTimer);
    _popupTimer = setTimeout(function() {
        if (!_canShowPopup()) { _schedulePopup(popups, index); return; }
        showPopup(popups[index]);
        var nextIndex = (index + 1) % popups.length;
        window._pendingPopupNext = function() { _schedulePopup(popups, nextIndex); };
    }, delay);
}

function loadPopups() {
    fetch('/api/popups/')
        .then(r => r.json())
        .then(data => {
            if (!data.popups || !data.popups.length) return;
            // Always restart from index 0 with fresh data
            if (_popupTimer) clearTimeout(_popupTimer);
            window._pendingPopupNext = null;
            _schedulePopup(data.popups, 0);
        })
        .catch(() => {});
}

function showPopup(popup) {
    const overlay = document.getElementById('popup-overlay');
    const content = document.getElementById('popup-content');
    if (!overlay || !content) return;

    document.getElementById('popup-title').textContent = popup.title;
    document.getElementById('popup-desc').textContent = popup.description;

    const flatType = document.getElementById('popup-flat-type');
    if (popup.flat_type) {
        flatType.textContent = popup.flat_type;
        flatType.style.display = 'inline-block';
    } else {
        flatType.style.display = 'none';
    }

    const imgDiv = document.getElementById('popup-image');
    const videoEl = document.getElementById('popup-video');
    if (popup.image && popup.is_video) {
        imgDiv.style.backgroundImage = '';
        videoEl.src = popup.image;
        videoEl.classList.remove('hidden');
        videoEl.play();
    } else if (popup.image) {
        videoEl.classList.add('hidden');
        videoEl.src = '';
        imgDiv.style.backgroundImage = `url(${popup.image})`;
        imgDiv.style.backgroundSize = 'cover';
        imgDiv.style.backgroundPosition = 'center';
    } else {
        videoEl.classList.add('hidden');
        videoEl.src = '';
        imgDiv.style.backgroundImage = '';
    }

    const logoWrap = document.getElementById('popup-logo-wrap');
    const logo = document.getElementById('popup-logo');
    if (popup.project_logo) {
        logo.src = popup.project_logo;
        logoWrap.classList.remove('hidden');
    } else {
        logoWrap.classList.add('hidden');
    }

    // Visit button — only show when external link
    const visitBtn = document.getElementById('popup-visit-btn');
    if (visitBtn) {
        if (popup.is_external && popup.link) {
            visitBtn.href = popup.link;
            visitBtn.classList.remove('hidden');
        } else {
            visitBtn.classList.add('hidden');
        }
    }

    // Pre-fill flat preference in interest form
    const flatPref = document.getElementById('interest-flat-pref');
    if (flatPref) flatPref.value = popup.flat_type || '';
    const popupAdId = document.getElementById('interest-popup-ad-id');
    if (popupAdId) popupAdId.value = popup.id || '';

    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
    overlay.dataset.popupId = popup.id;

    const chatWrap = document.getElementById('sw-chat-wrap');
    if (chatWrap) { chatWrap.style.pointerEvents = 'none'; chatWrap.style.zIndex = '50'; }

    requestAnimationFrame(() => {
        content.style.transform = 'scale(1)';
        content.style.opacity = '1';
    });
}

function closePopup() {
    const overlay = document.getElementById('popup-overlay');
    const content = document.getElementById('popup-content');
    content.style.transform = 'scale(0.95)';
    content.style.opacity = '0';
    setTimeout(() => {
        overlay.classList.add('hidden');
        overlay.classList.remove('flex');
        const chatWrap = document.getElementById('sw-chat-wrap');
        if (chatWrap) { chatWrap.style.pointerEvents = ''; chatWrap.style.zIndex = ''; chatWrap.style.opacity = ''; }
    }, 300);
    sessionStorage.setItem('lastPopupTime', Date.now());
    if (window._pendingPopupNext) {
        window._pendingPopupNext();
        window._pendingPopupNext = null;
    }
}
window.closePopup = closePopup;

function openInterestModal() {
    const modal = document.getElementById('interest-overlay');
    if (!modal) return;
    closePopup();
    const msgEl = document.getElementById('interest-msg');
    if (msgEl) { msgEl.classList.add('hidden'); msgEl.textContent = ''; }
    document.getElementById('interest-form').reset();
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeInterestModal() {
    const modal = document.getElementById('interest-overlay');
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}
window.openInterestModal = openInterestModal;
window.closeInterestModal = closeInterestModal;

// Show Interest form submit
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('interest-form');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msgEl = document.getElementById('interest-msg');
        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Submitting...';
        try {
            const res = await fetch('/submit-lead/', {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await res.json();
            if (data.success) {
                msgEl.textContent = 'Thank you! We will contact you soon.';
                msgEl.className = 'text-center text-sm py-2 px-3 rounded-lg bg-green-50 text-green-700';
                msgEl.classList.remove('hidden');
                form.reset();
                setTimeout(closeInterestModal, 2000);
            } else {
                msgEl.textContent = 'Please fill all required fields.';
                msgEl.className = 'text-center text-sm py-2 px-3 rounded-lg bg-red-50 text-red-600';
                msgEl.classList.remove('hidden');
            }
        } catch {
            msgEl.textContent = 'Something went wrong. Please try again.';
            msgEl.className = 'text-center text-sm py-2 px-3 rounded-lg bg-red-50 text-red-600';
            msgEl.classList.remove('hidden');
        }
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>SUBMIT';
    });
});

// Close popups on overlay click
document.addEventListener('click', (e) => {
    if (e.target.id === 'popup-overlay') closePopup();
    if (e.target.id === 'interest-overlay') closeInterestModal();
});


// ── Liquid Water Drop Lamp Toggle ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const knobGroup  = document.getElementById('cord-knob-group');
    const rope       = document.getElementById('cord-rope');
    const knobBody   = document.getElementById('knob-body');
    const knobIcon   = document.getElementById('knob-icon');
    const knobGlow   = document.getElementById('knob-glow');
    const dropBody   = document.getElementById('drop-body');
    const dropGlow   = document.getElementById('drop-outer-glow');
    const dropClick  = document.getElementById('drop-click-area');
    const dropMenu   = document.getElementById('liquid-drop-menu');
    if (!knobGroup || !rope) return;

    const KNOB_BASE_Y  = 235;
    const PULL_TRIGGER = 50;
    const MAX_DRAG     = 100;
    const ROPE_PATH_BASE = 'M38,115 Q30,135 38,155 Q46,175 38,195 Q30,215 38,235 Q46,255 38,272 Q30,287 38,';
    const ICON_MOON    = '';
    const ICON_SUN     = '';

    let dragging = false, startY = 0, triggered = false, activePointer = null;
    let menuOpen = false;

    function setVisuals(isDark) {
        // Lamp shade, base, rims, stem handled by CSS .dark rules
        // Knob icon (rope/knob colors handled by CSS)
        knobIcon.textContent = isDark ? ICON_MOON : ICON_SUN;
        knobIcon.style.fill  = isDark ? '#ffe8a0' : '#e8d0a0';
        const ring = document.getElementById('drop-border-ring');
        if (ring) {
            ring.setAttribute('stroke', isDark ? '#c9a84c' : 'none');
            ring.setAttribute('stroke-width', isDark ? '3' : '0');
            ring.style.opacity = isDark ? '1' : '0';
        }
        if (dropBody) dropBody.setAttribute('fill', isDark ? 'url(#dropGradDark)' : 'url(#dropGradLight)');
        if (dropGlow) {
            dropGlow.style.transition = 'opacity 0.6s ease';
            dropGlow.style.opacity    = isDark ? '0.35' : '0';
        }
        // Cloud menu colors handled by CSS .dark rules — no inline override needed
    }

    // ── Shade hover → "Menu" tooltip ─────────────────────────────────────────
    var menuTooltip = document.getElementById('menu-tooltip');
    var shadeArea = document.getElementById('drop-click-area');
    if (shadeArea && menuTooltip) {
        shadeArea.addEventListener('mouseenter', function() {
            if (dropMenu && dropMenu.style.display === 'block') return;
            var rect = shadeArea.closest('svg').getBoundingClientRect();
            menuTooltip.style.top   = (rect.top + 47 * rect.height / 300) + 'px';
            menuTooltip.style.right = (window.innerWidth - rect.left + 8) + 'px';
            menuTooltip.style.left  = 'auto';
            menuTooltip.style.display = 'block';
        });
        shadeArea.addEventListener('mouseleave', function() {
            menuTooltip.style.display = 'none';
        });
        shadeArea.addEventListener('click', function() {
            menuTooltip.style.display = 'none';
        });
    }

    // ── Knob hover → "Pull Down" tooltip ─────────────────────────────────────
    var pullTooltip = document.getElementById('pull-tooltip');
    if (knobGroup && pullTooltip) {
        knobGroup.addEventListener('mouseenter', function() {
            var rect = knobGroup.getBoundingClientRect();
            pullTooltip.style.top   = (rect.top + rect.height / 2) + 'px';
            pullTooltip.style.right = (window.innerWidth - rect.left + 8) + 'px';
            pullTooltip.style.left  = 'auto';
            pullTooltip.style.display = 'block';
        });
        knobGroup.addEventListener('mouseleave', function() {
            pullTooltip.style.display = 'none';
        });
        knobGroup.addEventListener('pointerdown', function() {
            pullTooltip.style.display = 'none';
        });
    }

    // Close menu on clicks outside the lamp wrap (ignore knob drags)
    document.addEventListener('click', (e) => {
        var lampWrap = document.getElementById('liquid-lamp-wrap');
        if (lampWrap && lampWrap.contains(e.target)) return;
        if (dropMenu) dropMenu.style.display = 'none';
        ['cloud-dot1','cloud-dot2','cloud-dot3','cloud-dot4'].forEach(function(id){
            var d = document.getElementById(id); if(d) d.style.display='none';
        });
        var o = document.getElementById('ldi-overlay');
        if(o) o.style.display = 'none';
    });

    function toggleTheme() {
        const body = document.body;
        if (body._x_dataStack) {
            body._x_dataStack[0].darkMode = !body._x_dataStack[0].darkMode;
        } else {
            const d = document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', d ? 'dark' : 'light');
        }
    }

    function applyDrag(dy) {
        const travel = Math.min(Math.max(dy, 0), MAX_DRAG);
        const eased  = Math.sqrt(travel / MAX_DRAG) * MAX_DRAG;
        knobGroup.style.transform  = 'translateY(' + eased + 'px)';
        rope.setAttribute('d', ROPE_PATH_BASE + (300 + eased));
        const pct = Math.min(travel / PULL_TRIGGER, 1);
        knobGlow.style.stroke      = '#c9a84c';
        knobGlow.style.opacity     = (pct * 0.7).toFixed(2);
        knobGlow.style.strokeWidth = (pct * 8).toFixed(1);
        if (dropGlow) {
            dropGlow.style.transition = 'none';
            dropGlow.style.opacity    = (pct * 0.8).toFixed(2);
        }
    }

    function releaseDrag() {
        if (!dragging) return;
        dragging = false; activePointer = null;
        knobGroup.style.cursor     = 'grab';
        knobGroup.style.transition = 'transform 0.5s cubic-bezier(0.34,1.56,0.64,1)';
        knobGroup.style.transform  = 'translateY(0)';
        knobGlow.style.opacity     = '0';
        knobGlow.style.strokeWidth = '0';

        // Animate rope path endpoint back in sync with the knob spring animation
        const currentD = rope.getAttribute('d');
        const startEnd = parseFloat(currentD.split(ROPE_PATH_BASE)[1]) || 300;
        const start    = performance.now();
        const dur      = 500;
        (function animateRope(now) {
            const t     = Math.min((now - start) / dur, 1);
            const ease  = 1 - Math.pow(1 - t, 3);
            const endY  = startEnd + (300 - startEnd) * ease;
            rope.setAttribute('d', ROPE_PATH_BASE + endY);
            if (t < 1) requestAnimationFrame(animateRope);
            else rope.setAttribute('d', ROPE_PATH_BASE + '300');
        })(start);
        const isDark = document.documentElement.classList.contains('dark');
        if (dropGlow) {
            dropGlow.style.transition = 'opacity 0.6s ease';
            dropGlow.style.opacity    = isDark ? '0.35' : '0';
        }
        setTimeout(() => { knobGroup.style.transition = ''; triggered = false; }, 550);
    }

    knobGroup.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        knobGroup.setPointerCapture(e.pointerId);
        activePointer = e.pointerId;
        dragging = true; triggered = false;
        startY   = e.clientY;
        knobGroup.style.transition = '';
        knobGroup.style.cursor     = 'grabbing';
    });

    knobGroup.addEventListener('pointermove', (e) => {
        if (!dragging || e.pointerId !== activePointer) return;
        e.preventDefault();
        const dy = e.clientY - startY;
        applyDrag(dy);
        if (!triggered && dy >= PULL_TRIGGER) {
            triggered = true;
            toggleTheme();
            const isDarkNow = document.documentElement.classList.contains('dark');
            setVisuals(isDarkNow);
            knobGlow.style.opacity     = '1';
            knobGlow.style.strokeWidth = '12';
        }
    });

    knobGroup.addEventListener('pointerup',     releaseDrag);
    knobGroup.addEventListener('pointercancel', releaseDrag);
    window.addEventListener('pointerup',        releaseDrag);
    window.addEventListener('pointercancel',    releaseDrag);

    // Alpine defer runs before DOMContentLoaded, so classList is already correct here
    setVisuals(document.documentElement.classList.contains('dark'));

    // Update on every theme toggle dispatched by Alpine
    window.addEventListener('theme-changed', function(e) {
        if (!dragging) setVisuals(e.detail.dark);
    });
});

// Scroll Spy — highlight active nav link
(function() {
    var sections = ['home','about','amenities','gallery','pricing','contact'];
    var links = {};
    document.addEventListener('DOMContentLoaded', function() {
        sections.forEach(function(id) {
            var el = document.querySelector('.nav-link[href="#' + id + '"]');
            if (el) links[id] = el;
        });
    });
    window.addEventListener('scroll', function() {
        var scrollY = window.scrollY + 120;
        var active = sections[0];
        sections.forEach(function(id) {
            var sec = document.getElementById(id);
            if (sec && sec.offsetTop <= scrollY) active = id;
        });
        Object.keys(links).forEach(function(id) {
            links[id].classList.toggle('active', id === active);
        });
    }, { passive: true });
})();

// Parallax on hero (subtle)
window.addEventListener('scroll', () => {
    const hero = document.getElementById('home');
    if (hero) {
        const scroll = window.scrollY;
        const bgs = hero.querySelectorAll('.absolute.inset-0 > div');
        if (scroll < window.innerHeight) {
            hero.style.setProperty('--parallax', `${scroll * 0.3}px`);
        }
    }
});