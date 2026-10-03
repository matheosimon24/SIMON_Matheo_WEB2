// Lance la suite de tests sur le composant INITIAL du sujet (preuve « avant »).
// Des tests rouges sont attendus ici : ils révèlent les défauts du composant.
// Commande : npm run test:initial   (non incluse dans npm test, qui doit rester vert)
import PlanningListInitial from '../PlanningList.initial.jsx';
import { decrirePlanningList } from './suitePlanningList.jsx';

decrirePlanningList('version initiale', PlanningListInitial);
