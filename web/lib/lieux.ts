import type { Source } from "./flux.ts";

/** Un repère sur la carte : plusieurs évènements au même endroit n'en font qu'un. */
export interface Lieu {
  latitude: number;
  longitude: number;
  nom: string;
  numeros: number[];
}

export function lieux(sources: Source[]): Lieu[] {
  const parPosition = new Map<string, Lieu>();
  for (const s of sources) {
    if (s.latitude === null || s.longitude === null) continue;
    const cle = `${s.latitude},${s.longitude}`;
    const lieu = parPosition.get(cle);
    if (lieu) lieu.numeros.push(s.numero);
    else
      parPosition.set(cle, {
        latitude: s.latitude,
        longitude: s.longitude,
        nom: [s.lieu, s.ville].filter(Boolean).join(", "),
        numeros: [s.numero],
      });
  }
  return [...parPosition.values()];
}
