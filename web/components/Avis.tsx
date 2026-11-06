"use client";

import { useRef, useState } from "react";
import type { Echange } from "@/lib/flux.ts";

/** 👍 / 👎 sous une réponse : le clic est enregistré tout de suite, le commentaire vient le compléter. */
export default function Avis({ echange }: { echange: Echange }) {
  const [avis, setAvis] = useState<"pour" | "contre" | null>(null);
  const [commentaire, setCommentaire] = useState("");
  const [envoye, setEnvoye] = useState(false);
  const id = useRef(`${Date.now()}-${Math.random()}`);

  function enregistrer(choix: "pour" | "contre", texte: string) {
    const { question, filtres, sources, reponse } = echange;
    return fetch("/api/avis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: id.current,
        avis: choix,
        commentaire: texte,
        question,
        filtres: filtres ?? null,
        sources: sources.map(({ numero, uid, titre }) => ({ numero, uid, titre })),
        reponse,
      }),
    });
  }

  const pouce = (choix: "pour" | "contre", signe: string, nom: string) => (
    <button
      type="button"
      aria-label={nom}
      aria-pressed={avis === choix}
      onClick={() => {
        setAvis(choix);
        enregistrer(choix, commentaire);
      }}
    >
      {signe}
    </button>
  );

  return (
    <div className="avis">
      {pouce("pour", "👍", "Réponse utile")}
      {pouce("contre", "👎", "Réponse à revoir")}
      {avis && !envoye && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            enregistrer(avis, commentaire).then(() => setEnvoye(true));
          }}
        >
          <input
            value={commentaire}
            onChange={(e) => setCommentaire(e.target.value)}
            placeholder="Un commentaire ? (facultatif)"
            aria-label="Commentaire sur la réponse (facultatif)"
          />
          <button type="submit" disabled={!commentaire.trim()}>Envoyer</button>
        </form>
      )}
      {avis && <span role="status">{envoye ? "Merci, commentaire reçu." : "Merci !"}</span>}
    </div>
  );
}
