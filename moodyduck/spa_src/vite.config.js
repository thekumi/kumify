import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      injectRegister: null,
      strategies: 'generateSW',
      filename: 'sw.js',
      manifest: {
        name: 'MoodyDuck',
        short_name: 'MoodyDuck',
        description: 'Your personal mood and wellness journal',
        theme_color: '#fdf6f0',
        background_color: '#fdf6f0',
        display: 'standalone',
        start_url: '/',
        scope: '/',
        icons: [
          { src: '/static/spa/icons/icon.svg', sizes: '512x512', type: 'image/svg+xml', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,woff,woff2,ttf,svg}'],
        maximumFileSizeToCacheInBytes: 4 * 1024 * 1024,
        navigateFallback: '/static/spa/index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/admin\//, /^\/accounts\//, /^\/oidc\//, /^\/sw\.js/],
        runtimeCaching: [
          {
            urlPattern: /^\/api\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              cacheableResponse: { statuses: [0, 200] },
              expiration: { maxEntries: 300, maxAgeSeconds: 7 * 24 * 60 * 60 },
            },
          },
        ],
      },
    }),
  ],
  base: '/static/spa/',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    outDir: '../spa',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/accounts': 'http://localhost:8000',
    },
  },
})
