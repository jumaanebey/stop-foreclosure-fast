/* =========================================================================
   TRACKING CONFIG — the only file you need to edit to turn analytics on.
   Paste your IDs between the quotes. Leave a value empty to keep it off.
   ========================================================================= */

var GA4_ID        = '';   // Google Analytics 4, looks like 'G-AB12CD34EF'
var META_PIXEL_ID = '';   // Meta (Facebook) Pixel, looks like '1234567890123456'

/* ===== Nothing below here needs editing ================================== */

(function () {
  'use strict';

  // ---- Google Analytics 4 ------------------------------------------------
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  if (GA4_ID) {
    var ga = document.createElement('script');
    ga.async = true;
    ga.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA4_ID);
    document.head.appendChild(ga);
    gtag('js', new Date());
    gtag('config', GA4_ID);
  }

  // ---- Meta Pixel --------------------------------------------------------
  if (META_PIXEL_ID) {
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () {
        n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
      };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
      t = b.createElement(e); t.async = !0; t.src = v;
      s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', META_PIXEL_ID);
    fbq('track', 'PageView');
  }

  // Safe no-op so page code can call fbq() whether or not the pixel is on.
  window.fbq = window.fbq || function () {};

  // ---- Conversion events -------------------------------------------------
  // Phone and text taps. Delegated once, site-wide, so every page is covered.
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="tel:"], a[href^="sms:"]');
    if (!a) return;
    var isCall = a.getAttribute('href').indexOf('tel:') === 0;
    var method = isCall ? 'call' : 'text';
    gtag('event', 'generate_lead', { method: method, page: location.pathname });
    fbq('track', 'Contact', { method: method });
  });

  // Called by page-level form handlers after a successful submit.
  window.trackLead = function (source) {
    gtag('event', 'generate_lead', { method: 'form', source: source || location.pathname });
    fbq('track', 'Lead', { source: source || location.pathname });
  };

  // ---- Lead delivery -----------------------------------------------------
  // Primary path mails the lead from the owner's own Gmail to himself, which
  // Gmail treats as Primary — the third-party form service was being filed as
  // "Updates" and auto-archived unread. The old service stays wired as a
  // fallback so a submission is never dropped if the endpoint is down.
  var LEAD_ENDPOINT = 'https://mfs-leads-chi.vercel.app/api/lead';
  var LEAD_FALLBACK = 'https://formsubmit.co/ajax/8b8dfa68d9af5c17be1256a407c00383';

  window.submitLead = function (form, source) {
    var fd = new FormData(form);
    return fetch(LEAD_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Accept': 'application/json'
      },
      body: new URLSearchParams(fd).toString()
    }).then(function (r) {
      if (!r.ok) throw new Error('lead endpoint ' + r.status);
    }).catch(function () {
      return fetch(LEAD_FALLBACK, {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: fd
      }).catch(function () {});
    }).then(function () {
      trackLead(source);
    });
  };
})();
