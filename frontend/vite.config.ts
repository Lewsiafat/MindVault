import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/mind-vault/',
  build: {
    outDir: '../src/static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://localhost:10016',
    },
  },
})
