// Badges de domaine et de statut.
// Le statut ne dépend jamais uniquement de la couleur : il combine un texte, une icône et un style de bordure.
import { DOMAINES, STATUTS } from '../libelles.js';

// Couleurs foncées sur fond clair : contraste du texte supérieur à 7:1 (niveau AAA).
const COULEURS_DOMAINE = {
  web: 'bg-sky-100 text-sky-900',
  data: 'bg-violet-100 text-violet-900',
  cyber: 'bg-rose-100 text-rose-900',
  projet: 'bg-slate-200 text-slate-900',
};

const BASE = 'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-sm font-medium';

export function BadgeDomaine({ domaine }) {
  return (
    <span className={`${BASE} ${COULEURS_DOMAINE[domaine]}`}>
      <span className="sr-only">Domaine : </span>
      {DOMAINES[domaine]}
    </span>
  );
}

export function BadgeStatut({ statut }) {
  const confirme = statut === 'confirmed';
  return (
    <span
      className={`${BASE} border-2 ${confirme
        ? 'border-solid border-emerald-700 bg-emerald-50 text-emerald-900'
        : 'border-dashed border-amber-700 bg-amber-50 text-amber-900'}`}
    >
      {/* Icône décorative : le texte suffit, elle est donc masquée aux lecteurs d'écran. */}
      <span aria-hidden="true">{confirme ? '✓' : '◷'}</span>
      <span className="sr-only">Statut : </span>
      {STATUTS[statut].libelle}
    </span>
  );
}

export function BadgePeriode({ periode, libelle }) {
  return (
    <span className={`${BASE} bg-white text-slate-800 ring-1 ring-slate-300`}>
      <span aria-hidden="true">{periode === 'am' ? '☀' : '◑'}</span>
      {libelle}
    </span>
  );
}
