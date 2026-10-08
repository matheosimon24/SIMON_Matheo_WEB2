// Détail d'une séance dans une fenêtre modale.
// L'élément natif <dialog> ouvert avec showModal() gère déjà : le piège du focus dans la fenêtre,
// la touche Échap pour fermer, et le reste de la page rendu inerte (inaccessible au clavier et aux lecteurs d'écran).
import { useEffect, useRef } from 'react';
import { BadgeDomaine, BadgePeriode, BadgeStatut } from './Badges.jsx';
import { GROUPES, PERIODES, STATUTS, formaterDate, nomFormateur } from '../libelles.js';

export default function DetailSeance({ seance, onFermer }) {
  const dialogue = useRef(null);
  const boutonFermer = useRef(null);

  useEffect(() => {
    // Garde « open » : en développement, StrictMode exécute l'effet deux fois.
    if (!dialogue.current.open) dialogue.current.showModal();
    // À l'ouverture, le focus va sur le bouton « Fermer » : première action possible, Entrée ou Échap pour ressortir.
    boutonFermer.current.focus();
  }, []);

  return (
    <dialog
      ref={dialogue}
      aria-labelledby="detail-titre"
      aria-describedby="detail-statut"
      // L'événement « close » arrive pour Échap comme pour le bouton : un seul point de sortie.
      onClose={onFermer}
      // Un clic sur le fond assombri (en dehors du contenu) ferme aussi la fenêtre.
      onClick={e => { if (e.target === dialogue.current) dialogue.current.close(); }}
      className="m-auto w-[calc(100%-2rem)] max-w-lg rounded-xl p-0 shadow-xl backdrop:bg-slate-900/60"
    >
      <div className="flex flex-col gap-4 p-5">
        <div className="flex items-start justify-between gap-4">
          <h2 id="detail-titre" className="text-xl font-bold text-slate-900">{seance.title}</h2>
          <button
            ref={boutonFermer}
            type="button"
            onClick={() => dialogue.current.close()}
            className="shrink-0 rounded-md border border-slate-400 px-3 py-1.5 text-sm font-semibold text-slate-900 hover:bg-slate-100 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
          >
            Fermer
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          <BadgeStatut statut={seance.status} />
          <BadgeDomaine domaine={seance.domain} />
          <BadgePeriode periode={seance.period} libelle={PERIODES[seance.period]} />
        </div>
        <p id="detail-statut" className="text-sm text-slate-700">{STATUTS[seance.status].explication}</p>

        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
          <dt className="text-slate-700">Date</dt>
          <dd className="font-medium text-slate-900">{formaterDate(seance.date)}</dd>
          <dt className="text-slate-700">Demi-journée</dt>
          <dd className="font-medium text-slate-900">{PERIODES[seance.period]}</dd>
          <dt className="text-slate-700">Groupe</dt>
          <dd className="font-medium text-slate-900">{GROUPES[seance.group]}</dd>
          <dt className="text-slate-700">Mode</dt>
          <dd className="font-medium text-slate-900">{seance.mode}</dd>
          <dt className="text-slate-700">Formateur</dt>
          <dd className="font-medium text-slate-900">{nomFormateur(seance.teacherId)}</dd>
          <dt className="text-slate-700">Identifiant</dt>
          <dd className="font-mono text-slate-900">{seance.id}</dd>
        </dl>
      </div>
    </dialog>
  );
}
