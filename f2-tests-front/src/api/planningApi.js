// Adaptateur qui simule l'API du planning (aucun backend n'est demandé pour F2).
import { SEANCES } from '../donnees/seances.js';

/**
 * Règle métier du filtre : A affiche A + Promotion ; B affiche B + Promotion ;
 * Promotion n'affiche que Promotion ; « all » affiche tout.
 */
export function filtrerParGroupe(seances, group) {
  if (group === 'all') return seances;
  if (group === 'Promotion') return seances.filter(s => s.group === 'Promotion');
  return seances.filter(s => s.group === group || s.group === 'Promotion');
}

/**
 * Crée une fonction loadSessions({ group }) qui répond après un délai.
 * - delais : délai de réponse en ms, par groupe (pour pouvoir provoquer des réponses dans le désordre).
 * - doitEchouer : fonction appelée à chaque requête ; si elle renvoie true, la requête échoue.
 */
export function creerApiPlanning({ delais = {}, doitEchouer = () => false } = {}) {
  return function loadSessions({ group }) {
    const delai = delais[group] ?? 300;
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (doitEchouer()) reject(new Error('Erreur réseau simulée'));
        else resolve(filtrerParGroupe(SEANCES, group));
      }, delai);
    });
  };
}
