// Interface minimale pour constater le comportement du composant dans le navigateur.
import { useState } from 'react';
import PlanningList from './PlanningList.initial.jsx';
import { creerApiPlanning } from './api/planningApi.js';

// « Tous » répond lentement et les groupes rapidement : choisir « Tous » puis vite « Groupe A »
// permet d'observer le problème des réponses dans le désordre.
const DELAIS = { all: 1500, A: 300, B: 300, Promotion: 300 };

export default function App() {
  const [panne, setPanne] = useState(false);
  // Variable lue à chaque requête : on peut activer/désactiver la panne sans recréer l'API.
  const [api] = useState(() => {
    const etat = { panne: false };
    return { etat, loadSessions: creerApiPlanning({ delais: DELAIS, doitEchouer: () => etat.panne }) };
  });

  function basculerPanne(e) {
    api.etat.panne = e.target.checked;
    setPanne(e.target.checked);
  }

  return (
    <main>
      <label>
        <input type="checkbox" checked={panne} onChange={basculerPanne} />
        Simuler une panne réseau
      </label>
      <PlanningList loadSessions={api.loadSessions} />
    </main>
  );
}
