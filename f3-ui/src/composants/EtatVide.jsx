// État vide : explique pourquoi rien ne s'affiche et propose une action pour en sortir.
export default function EtatVide({ onReinitialiser }) {
  return (
    <div className="rounded-lg border-2 border-dashed border-slate-400 bg-white p-6 text-center">
      <p className="text-lg font-semibold text-slate-900">Aucune séance ne correspond à ces filtres.</p>
      <p className="mt-1 text-slate-700">Essayez un autre groupe ou un autre domaine.</p>
      <button
        type="button"
        onClick={onReinitialiser}
        className="mt-4 rounded-md bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
      >
        Réinitialiser les filtres
      </button>
    </div>
  );
}
