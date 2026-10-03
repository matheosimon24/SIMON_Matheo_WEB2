// Interface minimale pour constater le comportement du composant dans le navigateur.
import { useState } from 'react';
import PlanningListInitial from './PlanningList.initial.jsx';
import PlanningListCorrige from './PlanningList.jsx';
import { creerApiPlanning } from './api/planningApi.js';

// « Tous » répond lentement et les groupes rapidement : choisir « Groupe A », puis vite « Tous »
// et encore « Groupe A » permet d'observer le problème des réponses dans le désordre.
const DELAIS = { all: 1500, A: 300, B: 300, Promotion: 300 };

export default function App() {
  const [version, setVersion] = useState('corrigee');
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

  const PlanningList = version === 'initiale' ? PlanningListInitial : PlanningListCorrige;

  return (
    <main>
      <fieldset>
        <legend>Version du composant</legend>
        <label>
          <input type="radio" name="version" value="initiale"
                 checked={version === 'initiale'} onChange={e => setVersion(e.target.value)} />
          Initiale (sujet)
        </label>
        <label>
          <input type="radio" name="version" value="corrigee"
                 checked={version === 'corrigee'} onChange={e => setVersion(e.target.value)} />
          Corrigée
        </label>
      </fieldset>
      <label>
        <input type="checkbox" checked={panne} onChange={basculerPanne} />
        Simuler une panne réseau
      </label>
      {/* key : changer de version remonte un composant neuf (état remis à zéro). */}
      <PlanningList key={version} loadSessions={api.loadSessions} />
    </main>
  );
}
