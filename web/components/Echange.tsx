import { cites } from "@/lib/citations.ts";
import type { Echange as EchangeType, Filtres } from "@/lib/flux.ts";
import { rendreMarkdown } from "@/lib/markdown.tsx";
import CarteEvenement from "./CarteEvenement.tsx";
import PucesFiltres from "./PucesFiltres.tsx";

/** Une question, sa réponse au fil de l'eau, et les évènements qui la fondent : cités d'abord. */
export default function Echange({ echange, rang, poser, occupe }: {
  echange: EchangeType;
  rang: number;
  /** Une réponse est en cours : on ne relance rien avant qu'elle finisse. */
  occupe: boolean;
  /** Envoie une question, avec des filtres imposés quand on a corrigé les puces. */
  poser: (question: string, filtres?: Filtres) => void;
}) {
  const { question, filtres, pistes, reponse, sources, erreur, etat } = echange;
  const numerosCites = echange.citations?.cites ?? cites(reponse, sources.length);
  const citees = sources.filter((s) => numerosCites.includes(s.numero));
  const autres = sources.filter((s) => !numerosCites.includes(s.numero));
  const ancre = (n: number) => `ev-${rang}-${n}`;

  // une pastille mène à la carte de l'évènement ; un numéro sans source le dit au lieu de mener nulle part
  const citation = (numeros: number[], cle: string) => (
    <span key={cle} className="pastilles">
      {numeros.map((n) =>
        n >= 1 && n <= sources.length ? (
          <a key={n} className="pastille" href={`#${ancre(n)}`} title={sources[n - 1].titre}>
            {n}
          </a>
        ) : (
          <span key={n} className="pastille pastille--inconnue" title="Aucun évènement ne porte ce numéro">
            {n}
          </span>
        ),
      )}
    </span>
  );

  return (
    <section className="echange">
      <p className="question">{question}</p>
      {filtres && <PucesFiltres filtres={filtres} relancer={(f) => poser(question, f)} occupe={occupe} />}
      <div className="reponse" aria-live="polite" aria-busy={etat === "en_cours"}>
        {reponse ? rendreMarkdown(reponse, citation) : etat === "en_cours" && !erreur && (
          <p className="attente">{sources.length ? "Puls rédige sa réponse…" : "Puls cherche dans l'agenda…"}</p>
        )}
        {pistes && pistes.length > 0 && (
          <div className="pistes">
            {pistes.map((p) => (
              <button key={p} type="button" onClick={() => poser(p)} disabled={occupe}>
                {p}
              </button>
            ))}
          </div>
        )}
        {etat === "arrete" && <p className="note">Réponse arrêtée.</p>}
        {erreur && <p className={erreur.reessai ? "note" : "note note--erreur"}>{erreur.message}</p>}
      </div>

      {sources.length > 0 && (
        <div className="evenements">
          {citees.length > 0 && (
            <div className="cartes">
              {citees.map((s) => <CarteEvenement key={s.uid} source={s} id={ancre(s.numero)} cite />)}
            </div>
          )}
          {autres.length > 0 && (
            <details>
              <summary>
                {citees.length ? "Autres évènements consultés" : "Évènements consultés"} ({autres.length})
              </summary>
              <div className="cartes">
                {autres.map((s) => <CarteEvenement key={s.uid} source={s} id={ancre(s.numero)} cite={false} />)}
              </div>
            </details>
          )}
        </div>
      )}
    </section>
  );
}
