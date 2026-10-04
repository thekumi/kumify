import { clientsClaim } from 'workbox-core'
import { precacheAndRoute, createHandlerBoundToURL } from 'workbox-precaching'
import { registerRoute, NavigationRoute } from 'workbox-routing'
import { NetworkFirst } from 'workbox-strategies'
import { ExpirationPlugin } from 'workbox-expiration'
import { CacheableResponsePlugin } from 'workbox-cacheable-response'

clientsClaim()
precacheAndRoute(self.__WB_MANIFEST)

const denylist = [/^\/api\//, /^\/admin\//, /^\/accounts\//, /^\/oidc\//, /^\/sw\.js/]
registerRoute(
  new NavigationRoute(createHandlerBoundToURL('/static/spa/index.html'), { denylist })
)

registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-cache',
    networkTimeoutSeconds: 10,
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] }),
      new ExpirationPlugin({ maxEntries: 300, maxAgeSeconds: 7 * 24 * 60 * 60 }),
    ],
  })
)

// Wake-up push — the SW decides what to show based on local state.
self.addEventListener('push', event => {
  event.waitUntil(
    (async () => {
      // Check the API cache for habits and recent mood logs to build a
      // relevant message without needing decryption.
      let body = 'Time to check in!'
      try {
        const [habitsResp, statusesResp] = await Promise.all([
          caches.match('/api/habits/'),
          caches.match('/api/statuses/?limit=1'),
        ])
        const habits = habitsResp ? await habitsResp.json() : null
        const statuses = statusesResp ? await statusesResp.json() : null
        const habitCount = habits?.results?.length ?? habits?.length ?? 0
        const lastEntry = statuses?.results?.[0] ?? statuses?.[0] ?? null
        const lastDate = lastEntry?.timestamp ? new Date(lastEntry.timestamp) : null
        const today = new Date()
        const loggedToday = lastDate && lastDate.toDateString() === today.toDateString()

        if (!loggedToday && habitCount > 0) {
          body = `Log your mood and check your ${habitCount} habit${habitCount !== 1 ? 's' : ''}!`
        } else if (!loggedToday) {
          body = 'How are you feeling today?'
        } else if (habitCount > 0) {
          body = `Don't forget your ${habitCount} habit${habitCount !== 1 ? 's' : ''} today.`
        }
      } catch {}

      return self.registration.showNotification('MoodyDuck', {
        body,
        icon: '/static/spa/icons/icon.svg',
        badge: '/static/spa/icons/icon.svg',
        tag: 'moodyduck-reminder',
        data: { url: '/' },
      })
    })()
  )
})

self.addEventListener('notificationclick', event => {
  event.notification.close()
  const url = event.notification.data?.url ?? '/'
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      const existing = windowClients.find(c => 'focus' in c)
      if (existing) {
        existing.navigate(url)
        return existing.focus()
      }
      return clients.openWindow(url)
    })
  )
})
