import type { Filtres } from "./flux.ts";

/** Une puce regroupe les champs qu'on corrige ensemble : les deux bornes d'une période vont de pair. */
export type Puce = "ville" | "dates" | "age" | "theme";

export const CHAMPS: Record<Puce, (keyof Filtres)[]> = {
  ville: ["ville"],
  dates: ["date_min", "date_max"],
  age: ["age"],
  theme: ["theme"],
};

const MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];

function jour(iso: string): string {
  const [, m, j] = iso.split("-").map(Number);
  return `${j} ${MOIS[m - 1]}`;
}

/** « 5–6 déc. », « 21 juin », « dès le 5 déc. » : la période telle qu'on la dit. */
export function periode(min: string | null, max: string | null): string {
  if (min && max) {
    if (min === max) return jour(min);
    // même mois : on ne l'écrit qu'une fois
    return min.slice(0, 7) === max.slice(0, 7) ? `${Number(min.slice(8))}–${jour(max)}` : `${jour(min)} – ${jour(max)}`;
  }
  return min ? `dès le ${jour(min)}` : `jusqu'au ${jour(max ?? "")}`;
}

/** Les puces à afficher, dans un ordre stable ; un filtre vide n'en a pas. */
export function puces(f: Filtres): { puce: Puce; texte: string }[] {
  const liste: { puce: Puce; texte: string }[] = [];
  if (f.ville) liste.push({ puce: "ville", texte: `📍 ${f.ville}` });
  if (f.date_min || f.date_max) liste.push({ puce: "dates", texte: `📅 ${periode(f.date_min, f.date_max)}` });
  if (f.age !== null) liste.push({ puce: "age", texte: `🧒 ${f.age} ans` });
  if (f.theme) liste.push({ puce: "theme", texte: `🎭 ${f.theme}` });
  return liste;
}

/** Les filtres sans une puce : ce qu'on renvoie quand on la retire. */
export function sans(f: Filtres, puce: Puce): Filtres {
  return { ...f, ...Object.fromEntries(CHAMPS[puce].map((c) => [c, null])) };
}
