// Lance la suite de tests sur le composant CORRIGÉ (preuve « après »).
// C'est ce fichier que lance « npm test » : tous les tests doivent être verts.
import PlanningList from '../PlanningList.jsx';
import { decrirePlanningList } from './suitePlanningList.jsx';

decrirePlanningList('version corrigée', PlanningList);
