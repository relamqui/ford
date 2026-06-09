const CACHE_NAME = 'wp-crm-entregador-v1';
const ASSETS = [
  '/entregador',
  '/css/entregador.css',
  '/js/entregador.js',
  '/img/icon-192.png',
  '/img/icon-512.png',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (e) => {
  // Only cache static assets, let API calls go to network
  if (e.request.url.includes('/api/')) return;
  
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});
