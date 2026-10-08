// Page planning : en-tête, filtres, séances regroupées par date, détail en fenêtre modale.
import { useRef, useState } from 'react';
import { SEANCES, filtrerParGroupe } from './donnees/seances.js';
import { formaterDate } from './libelles.js';
import BarreFiltres from './composants/BarreFiltres.jsx';
import CarteSeance from './composants/CarteSeance.jsx';
import DetailSeance from './composants/DetailSeance.jsx';
import EtatVide from './composants/EtatVide.jsx';

/** Regroupe les séances par date, en conservant l'ordre du planning. */
function grouperParDate(seances) {
  const jours = new Map();
  for (const s of seances) {
    if (!jours.has(s.date)) jours.set(s.date, []);
    jours.get(s.date).push(s);
  }
  return [...jours.entries()];
}

export default function App() {
  const [groupe, setGroupe] = useState('all');
  const [domaine, setDomaine] = useState('all');
  const [selection, setSelection] = useState(null);
  // Bouton qui a ouvert le détail : il reçoit à nouveau le focus à la fermeture.
  const declencheur = useRef(null);

  const visibles = filtrerParGroupe(SEANCES, groupe)
    .filter(s => domaine === 'all' || s.domain === domaine);

  function ouvrirDetail(seance, bouton) {
    declencheur.current = bouton;
    setSelection(seance);
  }

  function fermerDetail() {
    setSelection(null);
    declencheur.current?.focus();
  }

  function reinitialiser() {
    setGroupe('all');
    setDomaine('all');
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-300 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-5">
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-800">MATRiCE</p>
          <h1 className="text-2xl font-bold sm:text-3xl">Planning pédagogique</h1>
          <p className="mt-1 text-slate-700">Séances par date, demi-journée, groupe et formateur.</p>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-6">
        <BarreFiltres
          groupe={groupe}
          domaine={domaine}
          onGroupe={setGroupe}
          onDomaine={setDomaine}
          nombre={visibles.length}
        />

        {visibles.length === 0 ? (
          <EtatVide onReinitialiser={reinitialiser} />
        ) : (
          grouperParDate(visibles).map(([date, seances]) => (
            <section key={date} aria-labelledby={`jour-${date}`}>
              <h2 id={`jour-${date}`} className="mb-3 text-xl font-bold">{formaterDate(date)}</h2>
              <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {seances.map(s => (
                  <li key={s.id} className="flex">
                    <CarteSeance seance={s} onOuvrir={ouvrirDetail} />
                  </li>
                ))}
              </ul>
            </section>
          ))
        )}
      </main>

      {selection && <DetailSeance seance={selection} onFermer={fermerDetail} />}
    </div>
  );
}
