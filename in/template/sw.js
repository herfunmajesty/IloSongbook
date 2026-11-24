// Service Worker for Krakow Ukulele Songbook PWA
const CACHE_NAME = 'uke-songbook-{{ build_version }}';

// Core application shell files needed for basic offline functionality
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/songs.html',
  '/how.html',
  '/manifest.json',
  '/images/icon.png',
  '/images/icon.PNG',
  '/images/icon-192.png',
  '/images/icon-512.png',
  '/images/icon-maskable-512.png',
  '/images/qrcode.png',
  '/images/ukulele-krakow.PNG',
  '/images/ukulele-krakow-trans.png',
  '/images/ukulele-krakow-trans-dark.png',
  '/images/ukulele-krakow-trans-light.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
  'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
  'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap'
];

// Pre-cached song pages and chord diagrams (JSON encoded to prevent syntax errors with quotes or emojis)
const ALL_SONGS_AND_CHORDS = {{ all_urls_json }};

// Helper: cache files in sequential batches to prevent network congestion on mobile
async function cacheInBatches(cache, urls, batchSize = 10) {
  for (let i = 0; i < urls.length; i += batchSize) {
    const batch = urls.slice(i, i + batchSize);
    await Promise.allSettled(
      batch.map(async (rawUrl) => {
        try {
          const safeUrl = encodeURI(rawUrl);
          const res = await fetch(safeUrl, { cache: 'no-cache' });
          if (res && res.status === 200) {
            await cache.put(safeUrl, res.clone());
            if (safeUrl !== rawUrl) {
              await cache.put(rawUrl, res);
            }
          }
        } catch (e) {
          // Ignore individual fetch failure
        }
      })
    );
  }
}

// Install Event: cache core assets and all songs for offline use
self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);

      // 1. Cache essential core shell first
      await Promise.allSettled(
        CORE_ASSETS.map(async (url) => {
          try {
            const res = await fetch(url, { cache: 'no-cache' });
            if (res && res.status === 200) {
              await cache.put(url, res);
            }
          } catch (e) {
            console.warn('Could not precache core asset:', url);
          }
        })
      );

      // 2. Pre-cache all song pages and chord diagrams in batches
      await cacheInBatches(cache, ALL_SONGS_AND_CHORDS, 12);

      // Force this service worker to activate immediately once cached
      await self.skipWaiting();
    })()
  );
});

// Activate Event: remove previous version caches and claim clients immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
      await self.clients.claim();
    })()
  );
});

// Fetch Event: handle requests with offline cache fallback
self.addEventListener('fetch', (event) => {
  const request = event.request;

  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  if (!url.protocol.startsWith('http')) return;

  // External audio/video streaming (YouTube, Spotify) cannot be cached offline
  if (
    url.hostname.includes('youtube.com') ||
    url.hostname.includes('spotify.com') ||
    url.hostname.includes('googlevideo.com')
  ) {
    return;
  }

  // HTML / Navigation requests: Network-First with Cache Fallback
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      (async () => {
        try {
          // Attempt network request first
          const networkResponse = await fetch(request);
          if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
          }
          return networkResponse;
        } catch (err) {
          // Network failed (Offline): search cache thoroughly with encoding fallbacks
          const cache = await caches.open(CACHE_NAME);

          let cached = await cache.match(request, { ignoreSearch: true });
          if (!cached) {
            cached =
              (await cache.match(encodeURI(request.url), { ignoreSearch: true })) ||
              (await cache.match(decodeURI(request.url), { ignoreSearch: true }));
          }
          if (!cached) {
            const pathname = url.pathname;
            cached =
              (await cache.match(pathname, { ignoreSearch: true })) ||
              (await cache.match(decodeURI(pathname), { ignoreSearch: true })) ||
              (await cache.match(encodeURI(pathname), { ignoreSearch: true }));
          }

          if (cached) return cached;

          // If a specific song wasn't found, fallback to song list
          return (await cache.match('/songs.html')) || (await cache.match('/index.html'));
        }
      })()
    );
    return;
  }

  // Static Assets (Chords, Images, Fonts, CSS): Cache-First with Network Fallback
  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE_NAME);

      let cachedResponse = await cache.match(request, { ignoreSearch: true });
      if (!cachedResponse) {
        const pathname = url.pathname;
        cachedResponse =
          (await cache.match(pathname, { ignoreSearch: true })) ||
          (await cache.match(decodeURI(pathname), { ignoreSearch: true })) ||
          (await cache.match(encodeURI(pathname), { ignoreSearch: true }));
      }

      if (cachedResponse) {
        return cachedResponse;
      }

      try {
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
          cache.put(request, networkResponse.clone());
        }
        return networkResponse;
      } catch (err) {
        // Silently fail for optional external assets if offline
      }
    })()
  );
});
