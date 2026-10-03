// Configuration utilisée uniquement par « npm run test:initial » :
// reprend la configuration normale, mais ne lance que la suite sur le composant initial.
import { defineConfig, mergeConfig } from 'vitest/config';
import configBase from './vite.config.js';

export default mergeConfig(configBase, defineConfig({
  test: {
    include: ['src/tests/initial.verif.jsx'],
  },
}));
