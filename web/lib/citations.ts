/**
 * Les citations [n] d'une réponse. Le modèle cite les évènements du contexte par leur numéro ; rien ne
 * l'empêche d'écrire un numéro qui n'existe pas. Pendant le flux, l'interface les relève elle-même ;
 * à la fin, la liste du serveur fait foi. Même expression que CITATION dans api/main.py.
 */

const CITATION = /\[(\d+(?:\s*[,;]\s*\d+)*)\]/g;

export type Morceau = string | { numeros: number[] };

/** Le texte coupé en morceaux de texte et en groupes de citations ([1, 3] donne un seul groupe). */
export function decouper(texte: string): Morceau[] {
  const morceaux: Morceau[] = [];
  let dernier = 0;
  for (const m of texte.matchAll(CITATION)) {
    if (m.index > dernier) morceaux.push(texte.slice(dernier, m.index));
    morceaux.push({ numeros: m[1].split(/[,;]/).map(Number) });
    dernier = m.index + m[0].length;
  }
  if (dernier < texte.length) morceaux.push(texte.slice(dernier));
  return morceaux;
}

/** Les numéros cités qui correspondent à une source, dans l'ordre croissant. */
export function cites(texte: string, nombreSources: number): number[] {
  const numeros = decouper(texte).flatMap((m) => (typeof m === "string" ? [] : m.numeros));
  return [...new Set(numeros)].filter((n) => n >= 1 && n <= nombreSources).sort((a, b) => a - b);
}
