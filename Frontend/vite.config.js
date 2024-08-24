import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig(({ mode }) => ({
  root: resolve(__dirname, 'src'),
  build: {
    outDir: '../dist',  // Output directory for production build
    sourcemap: mode === 'development',  // Enable source maps in development mode
    // minify: 'esbuild',  // Minify using esbuild in production mode
  },
  server: {
    port: 3000,  // Port for Vite development server
    strictPort: true,  // Ensure the server will only listen on the specified port
    host: '0.0.0.0',  // Listen on all network interfaces for container access
    proxy: {
      '/auth': {
        target: 'http://token-service:8000',
        changeOrigin: true,
      },
      '/user': {
        target: 'http://user-service:8001',  // Proxy to user service
        changeOrigin: true,
      },
      '/game-history': {
        target: 'http://game-history:8002',  // Proxy to game history service
        changeOrigin: true,
      },
      '/game-stat': {
        target: 'http://game-history:8002',  // Proxy to game history service
        changeOrigin: true,
      },
      '/ws': {
        target: 'http://user-service:8001',
        changeOrigin: true,
        ws: true,
      },
      '/game-server/socket.io': {
        target: 'http://game-server:8010/socket.io',  // Proxy to game server
        changeOrigin: true,
        ws: true,  // Enable WebSocket support
      },
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        // Include paths for SCSS imports
        includePaths: [resolve(__dirname, 'src/scss')],
      },
    },
  },
}));
