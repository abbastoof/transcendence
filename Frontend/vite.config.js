import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: './',
  base: '/', // Base path for the application
  build: {
    outDir: './dist', // Output directory for production build
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'), // Entry point for the build
      },
    },
  },
  optimizeDeps: {
    include: ['three'], // Include 'three' in optimized dependencies
  },
});
