const CACHE_NAME = 'iiits-timetable-v1';

// The core files needed for the app to run offline
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/manifest.json',
    '/icon.png',
    '/students.json',
    '/timetable.json'
];

// 1. Install & Cache
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// 2. Cleanup old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// 3. Stale-While-Revalidate Strategy (Maximum Speed)
self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            const fetchPromise = fetch(event.request).then(networkResponse => {
                // Update the cache silently in the background
                if (networkResponse.ok) {
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, networkResponse.clone());
                    });
                }
                return networkResponse;
            }).catch(() => {
                // Ignore network errors (user is offline)
            });

            // Return the instant cached version if it exists, otherwise wait for the network
            return cachedResponse || fetchPromise;
        })
    );
});