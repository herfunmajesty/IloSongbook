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

// Pre-cached dynamic song pages and chord diagrams
const ALL_SONGS_AND_CHORDS = [
  {% for url in song_urls %}
  '{{ url }}',
  {% endfor %}
  {% for chord in chord_urls %}
  '{{ chord }}',
  {% endfor %}
];

// Install Event: cache core assets immediately, cache songs in background
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      // 1. Cache essential shell
      try {
        await cache.addAll(CORE_ASSETS);
      } catch (err) {
        console.warn('Some core assets failed to precache:', err);
      }

      // 2. Cache all songs and chords in background
      // Using Promise.allSettled so an individual missing asset doesn't fail installation
      await Promise.allSettled(
        ALL_SONGS_AND_CHORDS.map((url) =>
          fetch(url, { cache: 'no-cache' })
            .then((res) => {
              if (res.ok) {
                return cache.put(url, res);
              }
            })
            .catch(() => {})
        )
      );
    })
  );
});

// Activate Event: remove previous version caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      caches.keys().then((keys) => {
        return Promise.all(
          keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
        );
      }),
      self.clients.claim()
    ])
  );
});

// Fetch Event: handle offline requests
self.addEventListener('fetch', (event) => {
  const request = event.request;

  // Only handle GET requests
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Skip unsupported schemes (e.g. chrome-extension:)
  if (!url.protocol.startsWith('http')) return;

  // Video / Audio external streaming (YouTube, Spotify) is skipped
  if (url.hostname.includes('youtube.com') || url.hostname.includes('spotify.com') || url.hostname.includes('googlevideo.com')) {
    return;
  }

  // HTML / Navigation requests: Network-First with Cache Fallback
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return networkResponse;
        })
        .catch(async () => {
          const cachedResponse = await caches.match(request);
          if (cachedResponse) return cachedResponse;

          // If offline and specific song is not in cache, fallback to songs list
          const fallback = await caches.match('/songs.html');
          return fallback || caches.match('/index.html');
        })
    );
    return;
  }

  // Static Assets (Chords, Images, Fonts, CSS): Cache-First with Network Fallback
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
        }
        return networkResponse;
      }).catch(() => {
        // Silently fail for optional external resources if offline
      });
    })
  );
});
