const CACHE = 'msnow-v1';
const PRECACHE = [
  '/',
  '/static/images/favicon.png',
  '/static/images/logo.png',
];

// Install: pre-cache shell assets
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

// Activate: delete old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch strategy:
//   - API calls → Network first, no cache (always fresh data)
//   - Everything else → Network first, fall back to cache
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Always go to network for API and auth routes
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/auth/')) {
    return; // default browser behaviour
  }

  e.respondWith(
    fetch(e.request)
      .then(res => {
        // Cache successful GET responses
        if (e.request.method === 'GET' && res.status === 200) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
