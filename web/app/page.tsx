"use client";

import { useRef, useState } from "react";
import Echange from "@/components/Echange.tsx";
import Logo from "@/components/Logo.tsx";
import { AMORCES } from "@/lib/amorces.ts";
import { appliquer, lireFlux, type Echange as EchangeType } from "@/lib/flux.ts";

export default function Accueil() {
  const [echanges, setEchanges] = useState<EchangeType[]>([]);
  const [saisie, setSaisie] = useState("");
  const [enCours, setEnCours] = useState(false);
  const arret = useRef<AbortController | null>(null);
  const champ = useRef<HTMLTextAreaElement>(null);

  const modifierDernier = (f: (e: EchangeType) => EchangeType) =>
    setEchanges((liste) => [...liste.slice(0, -1), f(liste[liste.length - 1])]);

  async function envoyer() {
    const question = saisie.trim();
    if (!question || enCours) return;
    setSaisie("");
    setEnCours(true);
    setEchanges((liste) => [...liste, { question, reponse: "", sources: [], etat: "en_cours" }]);
    arret.current = new AbortController();
    try {
      // une question, une réponse : les échanges précédents restent à l'écran mais ne partent pas au modèle
      const reponse = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
        signal: arret.current.signal,
      });
      if (!reponse.ok || !reponse.body) throw new Error(String(reponse.status));
      const lecteur = reponse.body.pipeThrough(new TextDecoderStream()).getReader();
      let tampon = "";
      for (;;) {
        const { value, done } = await lecteur.read();
        if (done) break;
        const { evenements, reste } = lireFlux(tampon + value);
        tampon = reste;
        for (const evenement of evenements) modifierDernier((e) => appliquer(e, evenement));
      }
      modifierDernier((e) => (e.etat === "en_cours" ? { ...e, etat: "fini" } : e));
    } catch {
      // Arrêter garde le texte déjà reçu ; toute autre coupure vient de l'API injoignable
      modifierDernier((e) =>
        arret.current?.signal.aborted
          ? { ...e, etat: "arrete" }
          : { ...e, etat: "fini", erreur: { message: "L'API Puls-Events ne répond pas. Est-elle lancée ?", reessai: false } },
      );
    }
    setEnCours(false);
  }

  function amorcer(texte: string) {
    setSaisie(texte);
    // le curseur se place au bout de l'amorce, prêt pour la suite
    requestAnimationFrame(() => {
      champ.current?.focus();
      champ.current?.setSelectionRange(texte.length, texte.length);
    });
  }

  return (
    <main className="page">
      {echanges.length === 0 ? (
        <div className="bienvenue">
          <Logo grand />
          <h1>Envie de sortir en Seine-Saint-Denis ?</h1>
          <p>Concerts, spectacles, expos, sorties en famille : dites à Puls ce qui vous tente, il cherche dans l'agenda.</p>
          <div className="amorces">
            {AMORCES.map((a) => (
              <button key={a} type="button" onClick={() => amorcer(a)}>
                {a.trim()}…
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="fil">
          {echanges.map((e, i) => <Echange key={i} echange={e} rang={i} />)}
        </div>
      )}

      <form
        className="saisie"
        onSubmit={(e) => {
          e.preventDefault();
          envoyer();
        }}
      >
        <textarea
          ref={champ}
          value={saisie}
          rows={1}
          placeholder="Votre envie de sortie…"
          aria-label="Votre question"
          onChange={(e) => setSaisie(e.target.value)}
          onKeyDown={(e) => {
            // Entrée envoie, Maj+Entrée saute une ligne
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              envoyer();
            }
          }}
        />
        {enCours ? (
          <button type="button" className="bouton bouton--arret" onClick={() => arret.current?.abort()}>
            Arrêter
          </button>
        ) : (
          <button type="submit" className="bouton" disabled={!saisie.trim()}>
            Envoyer
          </button>
        )}
      </form>
    </main>
  );
}
