self.addEventListener('install', () => {
  console.log('[SW] Installed')
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  console.log('[SW] Activated')
  event.waitUntil(self.clients.claim())
})

self.addEventListener('push', (event) => {
  console.log('[SW] Push event received')

  event.waitUntil(
    (async () => {
      let title = 'SAFAIR Alert'
      let body = 'Dust risk has increased near you.'
      let url = '/construction-dust'

      try {
        if (event.data) {
          const rawText = event.data.text()
          console.log('[SW] Raw push payload:', rawText)

          try {
            const parsed = JSON.parse(rawText)
            title = parsed.title || title
            body = parsed.body || body
            url = parsed.url || url
          } catch {
            body = rawText || body
          }
        }

        await self.registration.showNotification(title, {
          body,
          icon: '/favicon.png',
          badge: '/favicon.png',
          tag: 'safair-alert',
          renotify: true,
          requireInteraction: true,
          data: { url },
        })

        console.log('[SW] showNotification success')
      } catch (err) {
        console.error('[SW] showNotification failed', err)
      }
    })()
  )
})

self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked')
  event.notification.close()

  const targetUrl = event.notification?.data?.url || '/'

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if ('focus' in client) {
          client.navigate(targetUrl)
          return client.focus()
        }
      }

      if (clients.openWindow) {
        return clients.openWindow(targetUrl)
      }
    })
  )
})

self.addEventListener('notificationclose', () => {
  console.log('[SW] Notification closed')
})