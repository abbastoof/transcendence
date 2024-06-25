// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  // Specify the entry point of your application
  // Adjust the path as needed

  root: './',
  base: '/',
  build: {
    outDir: './dist', // Output directory
  },
  optimizeDeps: {
    include: ['three'], // Include 'three' in optimized dependencies
  },
});