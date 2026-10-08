// Carte d'une séance : l'essentiel en un coup d'œil, le détail complet dans la fenêtre de détail.
import { BadgeDomaine, BadgePeriode, BadgeStatut } from './Badges.jsx';
import { GROUPES, PERIODES, nomFormateur } from '../libelles.js';

export default function CarteSeance({ seance, onOuvrir }) {
  return (
    <article className="flex w-full flex-col gap-3 rounded-lg border border-slate-300 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap gap-2">
        <BadgePeriode periode={seance.period} libelle={PERIODES[seance.period]} />
        <BadgeStatut statut={seance.status} />
      </div>
      <h3 className="text-lg font-semibold text-slate-900">{seance.title}</h3>
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
        <dt className="text-slate-700">Domaine</dt>
        <dd><BadgeDomaine domaine={seance.domain} /></dd>
        <dt className="text-slate-700">Groupe</dt>
        <dd className="font-medium text-slate-900">{GROUPES[seance.group]}</dd>
        <dt className="text-slate-700">Formateur</dt>
        <dd className="font-medium text-slate-900">{nomFormateur(seance.teacherId)}</dd>
      </dl>
      <button
        type="button"
        // Le bouton est transmis pour pouvoir lui rendre le focus à la fermeture du détail.
        onClick={e => onOuvrir(seance, e.currentTarget)}
        className="mt-auto self-start rounded-md bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
      >
        Voir le détail<span className="sr-only"> de « {seance.title} »</span>
      </button>
    </article>
  );
}
