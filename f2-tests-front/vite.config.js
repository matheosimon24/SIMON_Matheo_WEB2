import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    // jsdom simule un navigateur (DOM) dans Node pour pouvoir rendre les composants.
    environment: 'jsdom',
    // Ajoute les vérifications DOM de jest-dom (toBeInTheDocument, etc.) avant chaque fichier de test.
    setupFiles: ['./src/setupTests.js'],
  },
});
