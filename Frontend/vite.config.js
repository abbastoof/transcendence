import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig(({ mode }) => {
  return {
    root: resolve(__dirname, 'src'),
    build: {
      outDir: '../dist',  // Output directory for production build
      sourcemap: mode === 'development',  // Enable source maps in development mode
    },
    server: {
      port: 3001,  // Port for Vite development server
      strictPort: true,  // Ensure the server will only listen on the specified port
      host: '0.0.0.0',  // Listen on all network interfaces for container access
      proxy: {
        '/user': {
          target: 'http://user-service:8001/',  // Proxy requests to the user service
          changeOrigin: true,
          ///secure: false,
          //rewrite: (path) => path.replace(/^\/auth/, '/auth'),
        },
        '/game-history': {
          target: 'http://game-history:8002', // game history service
          changeOrigin: true,
        },
    },
    optimizeDeps: {
      include: ['three'],  // Include 'three' in optimized dependencies
    },
  },
  };
});
