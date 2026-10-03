// Version INITIALE du composant, recopiée telle quelle depuis le sujet (F2 – « Point de départ »).
// Elle est conservée sans modification pour pouvoir montrer les tests rouges (preuve « avant »).
import { useEffect, useState } from 'react';

export default function PlanningList({ loadSessions }) {
  const [group, setGroup] = useState('all');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    loadSessions({ group }).then(result => {
      setItems(result);
      setLoading(false);
    });
  }, [group, loadSessions]);

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
        : <ul>{items.map(s => <li key={s.id}>{s.title}</li>)}</ul>}
    </section>
  );
}
