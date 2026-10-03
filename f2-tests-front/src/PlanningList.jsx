// Version CORRIGÉE du composant. Correction minimale de la version initiale (PlanningList.initial.jsx) ;
// chaque ajout est signalé par un commentaire « Correction ».
import { useEffect, useState } from 'react';

export default function PlanningList({ loadSessions }) {
  const [group, setGroup] = useState('all');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  // Correction 1 : mémoriser l'échec du chargement pour l'afficher.
  const [error, setError] = useState(null);
  // Correction 1 : compteur de tentatives ; l'incrémenter relance le chargement.
  const [tentative, setTentative] = useState(0);

  useEffect(() => {
    // Correction 2 : « ignore » passe à true quand le filtre change ou que le composant
    // est démonté. Une réponse arrivée trop tard (obsolète) est alors ignorée.
    let ignore = false;
    setLoading(true);
    setError(null);
    loadSessions({ group })
      .then(result => {
        if (!ignore) setItems(result);
      })
      // Correction 1 : sans catch, un échec laissait « Chargement… » affiché pour toujours.
      .catch(err => {
        if (!ignore) setError(err);
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [group, loadSessions, tentative]);

  return (
    <section>
      <h1>Planning</h1>
      <select aria-label="Groupe" value={group}
              onChange={e => setGroup(e.target.value)}>
        <option value="all">Tous</option>
        <option value="A">Groupe A</option>
        <option value="B">Groupe B</option>
        <option value="Promotion">Promotion</option>
      </select>
      {loading ? <p role="status">Chargement…</p>
        // Correction 1 : erreur annoncée (role="alert") et bouton pour réessayer.
        : error ? (
          <>
            <p role="alert">Impossible de charger le planning.</p>
            <button type="button" onClick={() => setTentative(t => t + 1)}>Réessayer</button>
          </>
        )
        // Correction 3 : message explicite quand il n'y a aucune séance.
        : items.length === 0 ? <p>Aucune séance pour ce groupe.</p>
        : <ul>{items.map(s => <li key={s.id}>{s.title}</li>)}</ul>}
    </section>
  );
}
