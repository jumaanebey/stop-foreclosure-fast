// UI ENHANCEMENTS JAVASCRIPT

// 1. ANIMATED URGENCY INDICATOR - Countdown for consultation slots
function updateConsultationSlots() {
    const slotsElement = document.getElementById('consultation-slots');
    if (slotsElement) {
        // Simulate dynamic slots based on time of day
        const hour = new Date().getHours();
        let slots = 3;

        if (hour >= 9 && hour <= 12) slots = 2;
        else if (hour >= 12 && hour <= 15) slots = 1;
        else if (hour >= 15 && hour <= 17) slots = 3;

        slotsElement.textContent = slots;

        // Add urgency class if low slots
        if (slots <= 1) {
            slotsElement.parentElement.parentElement.classList.add('urgent');
        }
    }
}

// 2. TRUST SIGNALS CAROUSEL
function initTrustCarousel() {
    const items = document.querySelectorAll('.trust-item');
    if (items.length === 0) return;

    let currentIndex = 0;

    function rotateItems() {
        // Remove active class from all
        items.forEach(item => item.classList.remove('active'));

        // Add active class to current
        items[currentIndex].classList.add('active');

        // Update index
        currentIndex = (currentIndex + 1) % items.length;
    }

    // Rotate every 3 seconds
    setInterval(rotateItems, 3000);
}

// 4. STICKY NAVIGATION with scroll effect
function initStickyNav() {
    const header = document.getElementById('main-header');
    if (!header) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        // Add scrolled class when scrolling down
        if (currentScroll > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });

    // Smooth scroll for nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const offset = 100; // Account for fixed header
                    const targetPosition = target.offsetTop - offset;
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
}

// 5. PERFORMANCE OPTIMIZATIONS

// Lazy load images
function initLazyLoading() {
    const images = document.querySelectorAll('img[loading="lazy"]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => img.classList.add('loaded'));
    }
}

// Add loading states to forms
function initFormLoading() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('btn-loading');
                submitBtn.textContent = 'Processing...';
            }
        });
    });
}

// Add fade-in animation to sections
function initScrollAnimations() {
    const sections = document.querySelectorAll('section');

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, {
        threshold: 0.1
    });

    sections.forEach(section => sectionObserver.observe(section));
}

// Add floating phone button for mobile
function addFloatingPhone() {
    if (window.innerWidth <= 768) {
        const phoneBtn = document.createElement('a');
        phoneBtn.href = 'tel:+1-949-328-4811';
        phoneBtn.className = 'floating-phone';
        phoneBtn.setAttribute('aria-label', 'Call us');
        document.body.appendChild(phoneBtn);
    }
}

// Performance monitoring
function initPerformanceMonitoring() {
    // Log page load time
    window.addEventListener('load', () => {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);

        // Send to analytics if needed
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_load_time', {
                'event_category': 'performance',
                'value': loadTime
            });
        }
    });
}

// Initialize all enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    updateConsultationSlots();
    initTrustCarousel();
    initStickyNav();
    initLazyLoading();
    initFormLoading();
    initScrollAnimations();
    addFloatingPhone();
    initPerformanceMonitoring();

    // Update consultation slots every minute
    setInterval(updateConsultationSlots, 60000);
});

// Handle page visibility for performance
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause animations when page is hidden
        document.querySelectorAll('.trust-carousel').forEach(el => {
            el.style.animationPlayState = 'paused';
        });
    } else {
        // Resume animations when page is visible
        document.querySelectorAll('.trust-carousel').forEach(el => {
            el.style.animationPlayState = 'running';
        });
    }
});