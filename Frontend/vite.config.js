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
          target: 'http://localhost:3000/user',  // Proxy requests to the auth service through Nginx
          changeOrigin: true,
          secure: false,
          //rewrite: (path) => path.replace(/^\/auth/, '/auth'),
        },
      },
    },
    optimizeDeps: {
      include: ['three'],  // Include 'three' in optimized dependencies
    },
  };
});
