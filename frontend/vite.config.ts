import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// In development, requests to /api are forwarded to the Flask server,
// so the front end never needs to know the backend's address.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
});
