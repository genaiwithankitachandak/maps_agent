import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Ensures assets are loaded relative to the index.html path
  server: {
    proxy: {
      '/recommend': 'http://localhost:8080',
      '/profile': 'http://localhost:8080',
      '/weather': 'http://localhost:8080',
      '/funfact': 'http://localhost:8080'
    }
  }
})
