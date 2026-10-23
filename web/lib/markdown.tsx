import type { ReactNode } from "react";
import { decouper } from "./citations.ts";

/**
 * Rendu léger du Markdown qu'écrit Mistral : paragraphes, titres, listes (numérotées ou à puces, avec
 * une sous-liste indentée), gras, italique, et les citations [n], rendues par `citation`. Pas de
 * bibliothèque et jamais de HTML brut : React échappe tout le texte.
 */

type Citation = (numeros: number[], cle: string) => ReactNode;

const PUCE = /^(\s*)[-*•]\s+(.*)$/;
const NUMERO = /^\s*(\d+)[.)]\s+(.*)$/;
const TITRE = /^#{1,6}\s+(.*)$/;
const EMPHASE = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*)/;

function enLigne(texte: string, citation: Citation, cle: string): ReactNode[] {
  return texte.split(EMPHASE).map((partie, i) => {
    const citer = (t: string) =>
      decouper(t).map((m, j) => (typeof m === "string" ? m : citation(m.numeros, `${cle}-${i}-${j}`)));
    if (partie.length > 4 && partie.startsWith("**") && partie.endsWith("**"))
      return <strong key={i}>{citer(partie.slice(2, -2))}</strong>;
    if (partie.length > 2 && partie.startsWith("*") && partie.endsWith("*"))
      return <em key={i}>{citer(partie.slice(1, -1))}</em>;
    return <span key={i}>{citer(partie)}</span>;
  });
}

interface Liste {
  debut: number | null; // null : liste à puces
  items: { texte: string; sous: string[] }[];
}

export function rendreMarkdown(texte: string, citation: Citation): ReactNode[] {
  const blocs: ReactNode[] = [];
  let liste: Liste | null = null;

  const fermer = () => {
    if (!liste) return;
    const k = `b${blocs.length}`;
    const items = liste.items.map((item, i) => (
      <li key={i}>
        {enLigne(item.texte, citation, `${k}-${i}`)}
        {item.sous.length > 0 && (
          <ul>{item.sous.map((s, j) => <li key={j}>{enLigne(s, citation, `${k}-${i}-${j}`)}</li>)}</ul>
        )}
      </li>
    ));
    blocs.push(liste.debut === null ? <ul key={k}>{items}</ul> : <ol key={k} start={liste.debut}>{items}</ol>);
    liste = null;
  };

  for (const ligne of texte.split("\n")) {
    const numero = NUMERO.exec(ligne);
    const puce = PUCE.exec(ligne);
    if (puce && puce[1].length >= 2 && liste?.items.length) {
      liste.items[liste.items.length - 1].sous.push(puce[2]);
    } else if (numero || puce) {
      const debut = numero ? Number(numero[1]) : null;
      if (liste && (liste.debut === null) !== (debut === null)) fermer();
      liste ??= { debut, items: [] };
      liste.items.push({ texte: numero ? numero[2] : puce![2], sous: [] });
    } else if (ligne.trim()) {
      // une ligne vide ne ferme pas la liste : Mistral espace souvent ses « 1. », « 2. »
      fermer();
      const k = `b${blocs.length}`;
      const titre = TITRE.exec(ligne);
      blocs.push(titre ? <h3 key={k}>{enLigne(titre[1], citation, k)}</h3> : <p key={k}>{enLigne(ligne, citation, k)}</p>);
    }
  }
  fermer();
  return blocs;
}
