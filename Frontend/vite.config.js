import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: resolve(__dirname, 'src'),
  build: {
    outDir: '../dist', // Output directory for production build
  },
  server: {
    port:8080,
  },
  optimizeDeps: {
    include: ['three'], // Include 'three' in optimized dependencies
  },
});
