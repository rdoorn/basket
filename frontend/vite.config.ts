/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// VITE_API_BASE is read at runtime in the app via import.meta.env.
// The dev server binds host/port to match the Dockerfile/compose config.
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 8173,
  },
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
  },
})
