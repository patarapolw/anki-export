import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/api/anki-export': 'http://localhost:9000'
    }
  }
})
