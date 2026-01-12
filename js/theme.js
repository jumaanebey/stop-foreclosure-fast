/**
 * Theme Detector - Applies the correct variant class based on A/B test
 * Reads from localStorage and applies variant-a or variant-b class to body
 */
(function() {
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
})();
