/**
 * ============================================================
 *  Medical Report Analyzer — Service Worker
 *  Offline support: cache-first for static assets,
 *  network-first for API calls, offline fallback for pages.
 * ============================================================
 */

const APP_VERSION   = 'v1.0.0';
const CACHE_STATIC  = `static-${APP_VERSION}`;
const CACHE_PAGES   = `pages-${APP_VERSION}`;

/* ── Files to pre-cache on install ─────────────────────────── */
const STATIC_ASSETS = [
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  /* Add your CSS / JS bundle paths here, e.g.:
  '/static/css/main.css',
  '/static/js/main.js',
  */
];

const PAGES_TO_CACHE = [
  '/',          // Home / index
  '/offline',   // Offline fallback page  ← Flask route below
];

/* ── Install: pre-cache everything ─────────────────────────── */
self.addEventListener('install', event => {
  event.waitUntil(
    Promise.all([
      caches.open(CACHE_STATIC).then(cache => cache.addAll(STATIC_ASSETS)),
      caches.open(CACHE_PAGES).then(cache  => cache.addAll(PAGES_TO_CACHE)),
    ]).then(() => self.skipWaiting())
  );
});

/* ── Activate: delete old caches ────────────────────────────── */
self.addEventListener('activate', event => {
  const CURRENT = [CACHE_STATIC, CACHE_PAGES];
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => !CURRENT.includes(k)).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

/* ── Fetch: smart routing ────────────────────────────────────── */
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // 1) Skip non-GET & cross-origin requests
  if (request.method !== 'GET' || url.origin !== location.origin) return;

  // 2) API calls → Network-first, no cache fallback
  if (url.pathname.startsWith('/api/') ||
      url.pathname.startsWith('/auth/') ||
      url.pathname.startsWith('/login') ||
      url.pathname.startsWith('/logout')) {
    event.respondWith(
      fetch(request).catch(() =>
        new Response(
          JSON.stringify({ error: 'Offline – no network connection' }),
          { status: 503, headers: { 'Content-Type': 'application/json' } }
        )
      )
    );
    return;
  }

  // 3) Static assets → Cache-first
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then(cached => cached || fetchAndCache(request, CACHE_STATIC))
    );
    return;
  }

  // 4) HTML pages → Network-first, offline fallback
  event.respondWith(
    fetch(request)
      .then(response => {
        // Update page cache with fresh copy
        const clone = response.clone();
        caches.open(CACHE_PAGES).then(cache => cache.put(request, clone));
        return response;
      })
      .catch(() =>
        caches.match(request)
          .then(cached => cached || caches.match('/offline'))
      )
  );
});

/* ── Helper: fetch + save to cache ──────────────────────────── */
function fetchAndCache(request, cacheName) {
  return fetch(request).then(response => {
    if (response.ok) {
      const clone = response.clone();
      caches.open(cacheName).then(cache => cache.put(request, clone));
    }
    return response;
  });
}
