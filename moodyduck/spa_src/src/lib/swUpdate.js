import { ref } from 'vue'

export const updateAvailable = ref(false)
let _reg = null

export function watchForUpdate(registration) {
  _reg = registration

  const track = (sw) => {
    sw.addEventListener('statechange', () => {
      if (sw.state === 'installed' && navigator.serviceWorker.controller) {
        updateAvailable.value = true
      }
    })
  }

  if (registration.installing) track(registration.installing)
  registration.addEventListener('updatefound', () => {
    if (registration.installing) track(registration.installing)
  })
}

export function applyUpdate() {
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    window.location.reload()
  })
  if (_reg?.waiting) {
    _reg.waiting.postMessage({ type: 'SKIP_WAITING' })
  }
}
