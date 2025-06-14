import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
      '@views': fileURLToPath(new URL('./src/views', import.meta.url))
    }
  },
  server: {
    proxy: {
      // Flask側APIエンドポイントに合わせて追加
      '/upload-items': 'http://localhost:8080',
      '/check-weights': 'http://localhost:8080',
      '/calculate-fixed': 'http://localhost:8080',
      '/items': 'http://localhost:8080',
      '/edit-csv': 'http://localhost:8080'
    }
  }
})