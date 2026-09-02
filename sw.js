"use strict";
/* Shirorekha service worker.
 *
 * Precaches the whole app on first visit so it works with no connection
 * afterwards. The app is one 6 MB document, so the install is deliberately
 * all-or-nothing: a half-cached app that loads its shell and then fails to
 * find its data is worse than one that admits it is offline.
 */

const CACHE_NAME = "shirorekha-v1";
const SHELL = [
  "./",
  "index.html",
  "hind.html",
  "manifest.webmanifest",
  "icons/icon.svg"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(function (c) { return c.addAll(SHELL); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys.map(function (k) {
          return k === CACHE_NAME ? null : caches.delete(k);
        }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  // Cache first: nothing here changes without a redeploy, and the whole point
  // is that a dead network is indistinguishable from a live one.
  e.respondWith(
    caches.match(e.request).then(function (hit) {
      return hit || fetch(e.request).then(function (res) {
        if (res && res.ok && res.type === "basic") {
          const copy = res.clone();
          caches.open(CACHE_NAME).then(function (c) { c.put(e.request, copy); });
        }
        return res;
      });
    })
  );
});
