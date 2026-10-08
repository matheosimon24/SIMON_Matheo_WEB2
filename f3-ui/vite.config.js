import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  // Le plugin Tailwind génère uniquement les classes réellement utilisées dans le code.
  plugins: [react(), tailwindcss()],
});
