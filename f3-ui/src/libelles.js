// Traduction des codes du jeu de données en libellés lisibles.
import { FORMATEURS } from './donnees/seances.js';

export const PERIODES = { am: 'Matin', pm: 'Après-midi' };

export const GROUPES = { A: 'Groupe A', B: 'Groupe B', Promotion: 'Promotion' };

export const DOMAINES = { web: 'Web', data: 'Data', cyber: 'Cyber', projet: 'Projet' };

export const STATUTS = {
  confirmed: { libelle: 'Confirmée', explication: 'La séance est confirmée avec son formateur.' },
  proposed: { libelle: 'Proposée', explication: 'La séance est proposée et attend une confirmation.' },
};

export function nomFormateur(teacherId) {
  return teacherId ? FORMATEURS[teacherId] : 'Aucun formateur';
}

/**
 * « 2026-10-19 » → « Lundi 19 octobre 2026 ».
 * La date est construite et formatée en UTC : le jour affiché ne dépend pas du fuseau du navigateur.
 */
export function formaterDate(iso) {
  const [annee, mois, jour] = iso.split('-').map(Number);
  const texte = new Intl.DateTimeFormat('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(Date.UTC(annee, mois - 1, jour)));
  return texte.charAt(0).toUpperCase() + texte.slice(1);
}
