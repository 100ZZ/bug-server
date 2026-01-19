import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 11234,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        // 在 Docker 容器中使用服务名 backend，本地开发时使用 localhost
        // 通过环境变量 DOCKER_ENV 判断是否在 Docker 环境中
        target: process.env.DOCKER_ENV ? 'http://backend:43211' : 'http://localhost:43211',
        changeOrigin: true
      }
    }
  }
})

