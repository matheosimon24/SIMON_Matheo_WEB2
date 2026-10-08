// Barre de filtres : groupe et domaine. Les <select> natifs sont utilisables au clavier sans code en plus.
import { DOMAINES, GROUPES } from '../libelles.js';

const CHAMP = 'mt-1 block w-full rounded-md border border-slate-400 bg-white px-3 py-2 text-base text-slate-900 '
  + 'focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-blue-700';

export default function BarreFiltres({ groupe, domaine, onGroupe, onDomaine, nombre }) {
  return (
    <form
      role="search"
      aria-label="Filtres du planning"
      onSubmit={e => e.preventDefault()}
      className="flex flex-col gap-3 rounded-lg border border-slate-300 bg-white p-4 sm:flex-row sm:items-end"
    >
      <div className="sm:w-48">
        <label htmlFor="filtre-groupe" className="text-sm font-semibold text-slate-800">Groupe</label>
        <select id="filtre-groupe" value={groupe} onChange={e => onGroupe(e.target.value)} className={CHAMP}>
          <option value="all">Tous les groupes</option>
          {Object.entries(GROUPES).map(([valeur, libelle]) => (
            <option key={valeur} value={valeur}>{libelle}</option>
          ))}
        </select>
      </div>
      <div className="sm:w-48">
        <label htmlFor="filtre-domaine" className="text-sm font-semibold text-slate-800">Domaine</label>
        <select id="filtre-domaine" value={domaine} onChange={e => onDomaine(e.target.value)} className={CHAMP}>
          <option value="all">Tous les domaines</option>
          {Object.entries(DOMAINES).map(([valeur, libelle]) => (
            <option key={valeur} value={valeur}>{libelle}</option>
          ))}
        </select>
      </div>
      {/* Zone « live » : le nombre de résultats est annoncé par les lecteurs d'écran à chaque changement. */}
      <p aria-live="polite" className="text-sm text-slate-700 sm:ml-auto">
        {nombre} séance{nombre > 1 ? 's' : ''} affichée{nombre > 1 ? 's' : ''}
      </p>
    </form>
  );
}
