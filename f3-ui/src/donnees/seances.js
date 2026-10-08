// Jeu de données fourni par le sujet (F3 – « Jeu de données fourni »).
export const SEANCES = [
  { id: 's01', date: '2026-10-19', period: 'am', group: 'A', mode: 'DG', title: 'React composants', domain: 'web', teacherId: 't1', status: 'confirmed' },
  { id: 's02', date: '2026-10-19', period: 'am', group: 'B', mode: 'DG', title: 'React événements', domain: 'web', teacherId: 't2', status: 'confirmed' },
  { id: 's03', date: '2026-10-19', period: 'pm', group: 'Promotion', mode: 'CE', title: 'Données et SQL', domain: 'data', teacherId: 't1', status: 'confirmed' },
  { id: 's04', date: '2026-10-20', period: 'am', group: 'A', mode: 'DG', title: 'Authentification', domain: 'cyber', teacherId: 't2', status: 'proposed' },
  { id: 's05', date: '2026-10-20', period: 'am', group: 'B', mode: 'DG', title: 'Revue de projet', domain: 'projet', teacherId: 't3', status: 'proposed' },
  { id: 's06', date: '2026-10-20', period: 'pm', group: 'Promotion', mode: 'AUTO', title: 'Travail autonome', domain: 'projet', teacherId: null, status: 'proposed' },
];

// Formateurs fictifs fournis par le sujet.
export const FORMATEURS = {
  t1: 'Camille Exemple',
  t2: 'Alex Démonstration',
  t3: 'Sam Fictif',
};

/** Règle du filtre : A affiche A + Promotion ; B affiche B + Promotion ; Promotion seule ; « all » tout. */
export function filtrerParGroupe(seances, groupe) {
  if (groupe === 'all') return seances;
  if (groupe === 'Promotion') return seances.filter(s => s.group === 'Promotion');
  return seances.filter(s => s.group === groupe || s.group === 'Promotion');
}
