import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// Story 7.3 - Epic 7: Performance Optimization
// Vite configuration optimized for production CDN delivery
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // Build Configuration for Production
  build: {
    // Output directory
    outDir: 'dist',

    // Asset handling with cache busting
    assetsDir: 'assets',

    // Asset fingerprinting - adds content hash to filenames
    // e.g., main.js -> main.abc123.js
    rollupOptions: {
      output: {
        // Chunk naming with hash for cache busting
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]',

        // Manual chunk splitting for optimal caching
        manualChunks: {
          // Vendor chunks - split large dependencies
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-select'],
          'chart-vendor': ['recharts'],
        },
      },
    },

    // Code splitting - split into smaller chunks
    chunkSizeWarningLimit: 1000,

    // Source maps for production debugging
    sourcemap: false,

    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // Remove console.logs in production
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info'],
      },
    },

    // CSS code splitting
    cssCodeSplit: true,

    // Target modern browsers for smaller bundles
    target: 'es2015',

    // Asset inline threshold (smaller assets inlined as base64)
    assetsInlineLimit: 4096,  // 4kb
  },

  // Preview/Production server configuration
  preview: {
    port: 3000,
    host: true,
    headers: {
      // Cache control headers
      'Cache-Control': 'public, max-age=300',  // 5 minutes for HTML
    },
  },

  // Development server configuration
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  // Test Configuration (Vitest)
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.stories.tsx',
        '**/*.test.tsx',
        'vite.config.ts',
      ],
    },
  },

  // Performance Optimizations
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
    ],
  },
});
