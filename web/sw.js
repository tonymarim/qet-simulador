/* qet-simulador: guarda o simulador no PC para funcionar sem internet.
   Rede primeiro (pega a versão nova quando há internet); sem rede, usa a cópia guardada. */
const CACHE = "qet-simulador-v1";
const BASE = ["./", "index.html", "motor.js", "manifest.webmanifest",
              "icones/icone-192.png", "icones/icone-512.png", "icones/icone-maskable-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(
    fetch(e.request).then(r => {
      if (r.ok) { const copia = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copia)); }
      return r;
    }).catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
