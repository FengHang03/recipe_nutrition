import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true, // 接受所有主机连接
    allowedHosts: ['172.18.11.73', 'd130-113-87-81-162.ngrok-free.app', 'a92e-113-87-81-162.ngrok-free.app'],
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://172.18.11.73:8000',  // 更新为当前的IP地址
        changeOrigin: true,
        secure: false,
      },
    },
  }, 
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['framer-motion', 'lucide-react'],
          charts: ['recharts'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'framer-motion', 'recharts'],
  },
})