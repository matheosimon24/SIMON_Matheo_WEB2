// Exécuté avant chaque fichier de test (voir vite.config.js).
import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Démonte les composants rendus après chaque test, pour que les tests restent indépendants.
// (Testing Library ne le fait automatiquement que si les globals de Vitest sont activés.)
afterEach(() => {
  cleanup();
});
