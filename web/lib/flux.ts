/**
 * Le flux SSE de `POST /api/chat`, côté navigateur. Même contrat que la docstring de api/main.py :
 *
 *   filtres    Filtres                      lus dans la question (ou imposés), en premier
 *   pistes     { pistes: string[] }         question trop vague : relances proposées, puis fin
 *   sources    { sources: Source[] }        dès que la recherche a répondu, avant le texte
 *   texte      { texte: string }            un morceau de réponse
 *   citations  { cites: number[], inconnus: number[] }   les [n] relevés par le serveur
 *   erreur     { message: string, reessai: boolean }
 *   fin        {}
 */

export interface Source {
  numero: number;
  uid: number;
  titre: string;
  dates_texte: string | null;
  date_debut: string | null;
  date_fin: string | null;
  lieu: string | null;
  ville: string | null;
  lien: string | null;
  image: string | null;
  latitude: number | null;
  longitude: number | null;
  age_min: number | null;
  age_max: number | null;
}

/** Ce que la recherche impose ; null = pas de filtre. Les dates sont au format AAAA-MM-JJ. */
export interface Filtres {
  ville: string | null;
  date_min: string | null;
  date_max: string | null;
  age: number | null;
  theme: string | null;
}

export interface Echange {
  question: string;
  filtres?: Filtres;
  /** Relances proposées quand la question était trop vague pour chercher. */
  pistes?: string[];
  reponse: string;
  sources: Source[];
  /** Donnés par le serveur à la fin ; d'ici là, l'interface relève les [n] elle-même. */
  citations?: { cites: number[]; inconnus: number[] };
  erreur?: { message: string; reessai: boolean };
  etat: "en_cours" | "fini" | "arrete";
}

export interface Evenement {
  nom: string;
  donnees: Record<string, unknown>;
}

/** Découpe le texte reçu en évènements SSE ; le dernier bloc, peut-être incomplet, revient dans `reste`. */
export function lireFlux(tampon: string): { evenements: Evenement[]; reste: string } {
  const blocs = tampon.replace(/\r\n/g, "\n").split("\n\n");
  const reste = blocs.pop() ?? "";
  const evenements = blocs.flatMap((bloc) => {
    const nom = /^event: (.*)$/m.exec(bloc)?.[1];
    const donnees = /^data: (.*)$/m.exec(bloc)?.[1];
    return nom && donnees ? [{ nom, donnees: JSON.parse(donnees) }] : [];
  });
  return { evenements, reste };
}

/** Applique un évènement à l'échange en cours ; un évènement inconnu le laisse tel quel. */
export function appliquer(e: Echange, { nom, donnees }: Evenement): Echange {
  switch (nom) {
    case "filtres":
      return { ...e, filtres: donnees as unknown as Filtres };
    case "pistes":
      return { ...e, pistes: donnees.pistes as string[] };
    case "sources":
      return { ...e, sources: donnees.sources as Source[] };
    case "texte":
      // le texte qui arrive efface l'avis « nouvel essai… » d'une 429
      return { ...e, reponse: e.reponse + String(donnees.texte), erreur: undefined };
    case "citations":
      return { ...e, citations: donnees as Echange["citations"] };
    case "erreur": {
      const erreur = donnees as Echange["erreur"] & {};
      return { ...e, erreur, etat: erreur.reessai ? e.etat : "fini" };
    }
    case "fin":
      return { ...e, etat: "fini" };
    default:
      return e;
  }
}
