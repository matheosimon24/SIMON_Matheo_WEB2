// Suite de tests partagée : la même suite est lancée sur le composant initial et sur le composant corrigé.
// Ce fichier ne se termine pas par .test.jsx : il n'est pas lancé seul, il est appelé par les fichiers de test.
import { describe, test, expect, vi } from 'vitest';
import { render, screen, act, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SEANCES } from '../donnees/seances.js';
import { creerApiPlanning } from '../api/planningApi.js';

/** Promesse que le test résout ou rejette lui-même, au moment choisi. */
function creerDiffere() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

/**
 * Faux loadSessions piloté par le test : chaque appel crée une requête « en attente »
 * que le test termine quand il veut (pour contrôler l'ordre des réponses).
 */
function creerLoadSessionsPilote() {
  const requetes = [];
  const loadSessions = vi.fn(() => {
    const differe = creerDiffere();
    requetes.push(differe);
    return differe.promise;
  });
  return { loadSessions, requetes };
}

const titres = seances => seances.map(s => s.title);
const titresAffiches = () => screen.queryAllByRole('listitem').map(li => li.textContent);

export function decrirePlanningList(nomVersion, PlanningList) {
  describe(`PlanningList (${nomVersion})`, () => {
    test('1. chargement : affiche « Chargement… » pendant la requête et demande tous les groupes', () => {
      const { loadSessions } = creerLoadSessionsPilote();
      render(<PlanningList loadSessions={loadSessions} />);

      expect(screen.getByRole('status')).toHaveTextContent('Chargement');
      expect(loadSessions).toHaveBeenCalledWith({ group: 'all' });
    });

    test('2. succès : affiche les séances reçues et retire le chargement', async () => {
      const { loadSessions, requetes } = creerLoadSessionsPilote();
      render(<PlanningList loadSessions={loadSessions} />);

      await act(async () => requetes[0].resolve(SEANCES));

      expect(titresAffiches()).toEqual(titres(SEANCES));
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });

    test('3. groupe A : affiche les séances de A et celles de la Promotion, pas celles de B', async () => {
      const user = userEvent.setup();
      // Adaptateur réel (règle métier A + Promotion), sans délai.
      const loadSessions = creerApiPlanning({ delais: { all: 0, A: 0 } });
      render(<PlanningList loadSessions={loadSessions} />);
      await screen.findByText('React composants');

      await user.selectOptions(screen.getByRole('combobox', { name: 'Groupe' }), 'A');

      await screen.findByText('Authentification');
      expect(titresAffiches()).toEqual(['React composants', 'Données et SQL', 'Authentification', 'Travail autonome']);
      expect(screen.queryByText('React événements')).not.toBeInTheDocument();
      expect(screen.queryByText('Revue de projet')).not.toBeInTheDocument();
    });

    test('4. résultat vide : affiche un message explicite au lieu d\'une liste vide', async () => {
      const { loadSessions, requetes } = creerLoadSessionsPilote();
      render(<PlanningList loadSessions={loadSessions} />);

      await act(async () => requetes[0].resolve([]));

      expect(screen.getByText(/aucune séance/i)).toBeInTheDocument();
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });

    test('5. erreur puis nouvelle tentative : affiche l\'erreur, puis recharge au clic sur « Réessayer »', async () => {
      const user = userEvent.setup();
      const { loadSessions, requetes } = creerLoadSessionsPilote();
      render(<PlanningList loadSessions={loadSessions} />);

      await act(async () => requetes[0].reject(new Error('Erreur réseau')));

      // L'erreur doit être annoncée et le chargement doit s'arrêter.
      expect(screen.getByRole('alert')).toHaveTextContent(/impossible de charger/i);
      expect(screen.queryByRole('status')).not.toBeInTheDocument();

      // Nouvelle tentative : une 2e requête part, et son succès affiche les séances.
      await user.click(screen.getByRole('button', { name: 'Réessayer' }));
      expect(loadSessions).toHaveBeenCalledTimes(2);
      await act(async () => requetes[1].resolve(SEANCES));

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(titresAffiches()).toEqual(titres(SEANCES));
    });

    test('6. réponses dans le désordre : seule la réponse du dernier filtre choisi est affichée', async () => {
      const user = userEvent.setup();
      const { loadSessions, requetes } = creerLoadSessionsPilote();
      render(<PlanningList loadSessions={loadSessions} />);
      await act(async () => requetes[0].resolve(SEANCES));

      const filtre = screen.getByRole('combobox', { name: 'Groupe' });
      await user.selectOptions(filtre, 'A');   // requête n°1 (lente)
      await user.selectOptions(filtre, 'B');   // requête n°2 (rapide)

      const seancesB = SEANCES.filter(s => s.group === 'B' || s.group === 'Promotion');
      const seancesA = SEANCES.filter(s => s.group === 'A' || s.group === 'Promotion');

      // La réponse B arrive d'abord, puis la réponse A, devenue obsolète.
      await act(async () => requetes[2].resolve(seancesB));
      await act(async () => requetes[1].resolve(seancesA));

      expect(filtre).toHaveValue('B');
      expect(titresAffiches()).toEqual(titres(seancesB));
    });

    test('7. accessibilité : le filtre a le nom accessible « Groupe » et propose les 4 choix', () => {
      const { loadSessions } = creerLoadSessionsPilote();
      render(<PlanningList loadSessions={loadSessions} />);

      const filtre = screen.getByRole('combobox', { name: 'Groupe' });
      const options = within(filtre).getAllByRole('option').map(o => o.textContent);
      expect(options).toEqual(['Tous', 'Groupe A', 'Groupe B', 'Promotion']);
    });

    test('8. clavier : le filtre est atteignable avec Tab et son changement relance le chargement', async () => {
      const user = userEvent.setup();
      const { loadSessions, requetes } = creerLoadSessionsPilote();
      render(<PlanningList loadSessions={loadSessions} />);
      await act(async () => requetes[0].resolve(SEANCES));

      await user.tab();
      const filtre = screen.getByRole('combobox', { name: 'Groupe' });
      expect(filtre).toHaveFocus();

      // jsdom ne simule pas l'ouverture native d'un <select> aux flèches : on choisit l'option
      // sur l'élément qui a le focus, ce qui déclenche le même événement « change ».
      await user.selectOptions(filtre, 'Promotion');

      expect(loadSessions).toHaveBeenLastCalledWith({ group: 'Promotion' });
      expect(screen.getByRole('status')).toHaveTextContent('Chargement');
      expect(filtre).toHaveFocus();
    });
  });
}
