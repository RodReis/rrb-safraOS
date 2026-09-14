/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: Number(process.env.SAFRAOS_WEB_PORT ?? 8183),
    strictPort: true,
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    globals: true,
    // Inclui os testes de packages/frontend (ex.: DataTable) no glob padrão
    // rodado por `npm run test`, além dos testes locais de apps/web.
    include: [
      '**/*.{test,spec}.?(c|m)[jt]s?(x)',
      '../../packages/frontend/src/**/*.{test,spec}.?(c|m)[jt]s?(x)',
    ],
  },
})
