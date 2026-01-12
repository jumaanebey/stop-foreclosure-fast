/**
 * Theme JS - My Foreclosure Solution
 * Handles: A/B variant, mobile menu, exit intent, sticky phone, FAQ accordion
 */
(function() {
    // Apply A/B variant class
    const variant = localStorage.getItem('mfs_ab_variant');
    if (variant === 'B') {
        document.body.classList.add('variant-b');
    } else {
        document.body.classList.add('variant-a');
    }

    // Track page view with variant
    if (typeof gtag !== 'undefined') {
        gtag('event', 'page_view', {
            'ab_variant': variant || 'unknown',
            'page_type': 'secondary'
        });
    }

    // Wait for DOM
    document.addEventListener('DOMContentLoaded', function() {

        // ========== Mobile Menu ==========
        const menuToggle = document.querySelector('.menu-toggle');
        const mobileNav = document.querySelector('.mobile-nav');

        if (menuToggle && mobileNav) {
            menuToggle.addEventListener('click', function() {
                menuToggle.classList.toggle('active');
                mobileNav.classList.toggle('active');
                document.body.classList.toggle('mobile-nav-open');
            });

            // Close menu when clicking a link
            mobileNav.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    menuToggle.classList.remove('active');
                    mobileNav.classList.remove('active');
                    document.body.classList.remove('mobile-nav-open');
                });
            });
        }

        // ========== Sticky Phone (Desktop) ==========
        const stickyPhone = document.querySelector('.sticky-phone');
        if (stickyPhone) {
            let lastScroll = 0;
            window.addEventListener('scroll', function() {
                const currentScroll = window.pageYOffset;

                // Show after scrolling 400px
                if (currentScroll > 400) {
                    stickyPhone.classList.add('visible');
                } else {
                    stickyPhone.classList.remove('visible');
                }

                lastScroll = currentScroll;
            });
        }

        // ========== Exit Intent Popup ==========
        const exitPopup = document.querySelector('.exit-popup-overlay');
        if (exitPopup) {
            let hasShown = sessionStorage.getItem('exitPopupShown');

            // Only show once per session
            if (!hasShown) {
                document.addEventListener('mouseout', function(e) {
                    // If mouse leaves the top of the viewport
                    if (e.clientY < 10 && !hasShown) {
                        exitPopup.classList.add('active');
                        sessionStorage.setItem('exitPopupShown', 'true');
                        hasShown = true;

                        if (typeof gtag !== 'undefined') {
                            gtag('event', 'exit_intent_shown');
                        }
                    }
                });
            }

            // Close popup handlers
            const closeBtn = exitPopup.querySelector('.exit-popup-close');
            const skipLink = exitPopup.querySelector('.skip-link');

            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    exitPopup.classList.remove('active');
                });
            }

            if (skipLink) {
                skipLink.addEventListener('click', () => {
                    exitPopup.classList.remove('active');
                });
            }

            // Close on overlay click
            exitPopup.addEventListener('click', function(e) {
                if (e.target === exitPopup) {
                    exitPopup.classList.remove('active');
                }
            });

            // Close on escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    exitPopup.classList.remove('active');
                }
            });
        }

        // ========== FAQ Accordion ==========
        document.querySelectorAll('.faq-question').forEach(question => {
            question.addEventListener('click', function() {
                const item = this.parentElement;
                const wasActive = item.classList.contains('active');

                // Close all other items
                document.querySelectorAll('.faq-item').forEach(faq => {
                    faq.classList.remove('active');
                });

                // Toggle current item
                if (!wasActive) {
                    item.classList.add('active');
                }
            });
        });

        // ========== Form Redirect to Thank You ==========
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const formId = form.id || 'unknown';

                // Track form submission
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'form_submit', {
                        'form_id': formId
                    });
                }
            });
        });

    });
})();
