"use client";

import { useCallback, useMemo, useState } from "react";
import { cites } from "@/lib/citations.ts";
import type { Echange as EchangeType, Filtres } from "@/lib/flux.ts";
import { lieux } from "@/lib/lieux.ts";
import { rendreMarkdown } from "@/lib/markdown.tsx";
import Avis from "./Avis.tsx";
import CarteEvenement from "./CarteEvenement.tsx";
import CarteLieux from "./CarteLieux.tsx";
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
  const { question, filtres, pistes, reponse, sources, erreur, etat, cout } = echange;
  const [survol, setSurvol] = useState<number[]>([]);
  const [vue, setVue] = useState<"liste" | "carte">("liste");
  const numerosCites = echange.citations?.cites ?? cites(reponse, sources.length);
  const citees = sources.filter((s) => numerosCites.includes(s.numero));
  const autres = sources.filter((s) => !numerosCites.includes(s.numero));
  const ancre = (n: number) => `ev-${rang}-${n}`;
  const lieuxCites = useMemo(() => lieux(citees), [citees.map((s) => s.numero).join()]);
  // retour à la liste sur téléphone, puis la carte de l'évènement s'allume comme après une pastille
  const ouvrir = useCallback((n: number) => {
    setVue("liste");
    requestAnimationFrame(() => {
      location.hash = `ev-${rang}-${n}`;
    });
  }, [rang]);

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

      {etat === "en_cours" && !sources.length && !reponse && !erreur && (
        <div className="cartes squelettes" aria-hidden="true">
          {[0, 1, 2].map((i) => (
            <div key={i} className="carte carte--squelette">
              <div className="carte-image" />
              <div className="carte-corps">
                <span /><span /><span />
              </div>
            </div>
          ))}
        </div>
      )}

      {etat === "fini" && reponse && !erreur && (
        <div className="bilan">
          <Avis echange={echange} />
          {cout && (
            <p className="cout">
              {cout.jetons_entree.toLocaleString("fr-FR")} + {cout.jetons_sortie.toLocaleString("fr-FR")} jetons ·{" "}
              {cout.euros.toLocaleString("fr-FR", { maximumFractionDigits: 4 })} € · recherche{" "}
              {cout.recherche_s.toLocaleString("fr-FR", { maximumFractionDigits: 1 })} s
              {cout.generation_s > 0 && ` · génération ${cout.generation_s.toLocaleString("fr-FR", { maximumFractionDigits: 1 })} s`}
            </p>
          )}
        </div>
      )}

      {sources.length > 0 && (
        <div className="evenements">
          {lieuxCites.length > 0 && (
            <div className="onglets" role="group" aria-label="Affichage des évènements">
              <button type="button" aria-pressed={vue === "liste"} onClick={() => setVue("liste")}>Liste</button>
              <button type="button" aria-pressed={vue === "carte"} onClick={() => setVue("carte")}>Carte</button>
            </div>
          )}
          {citees.length > 0 && (
            <div className={`evenements-grille${lieuxCites.length ? " evenements-grille--carte" : ""} vue-${vue}`}>
              <div className="cartes">
                {citees.map((s) => (
                  <CarteEvenement
                    key={s.uid}
                    source={s}
                    id={ancre(s.numero)}
                    cite
                    allume={survol.includes(s.numero)}
                    survoler={lieuxCites.length ? setSurvol : undefined}
                  />
                ))}
              </div>
              {lieuxCites.length > 0 && <CarteLieux lieux={lieuxCites} survol={survol} survoler={setSurvol} ouvrir={ouvrir} />}
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
