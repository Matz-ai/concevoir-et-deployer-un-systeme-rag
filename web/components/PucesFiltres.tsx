"use client";

import { useState } from "react";
import { CHAMPS, puces, sans, type Puce } from "@/lib/filtres.ts";
import type { Filtres } from "@/lib/flux.ts";

const ETIQUETTES: Record<keyof Filtres, string> = {
  ville: "Commune",
  date_min: "Du",
  date_max: "Au",
  age: "Âge",
  theme: "Thème",
};

/** Les filtres lus dans la question : retirer ou corriger une puce relance la question avec ces filtres. */
export default function PucesFiltres({ filtres, relancer, occupe }: {
  filtres: Filtres;
  relancer: (f: Filtres) => void;
  occupe: boolean;
}) {
  const [edition, setEdition] = useState<Puce | null>(null);
  const liste = puces(filtres);
  if (liste.length === 0) return null;

  function valider(puce: Puce, formulaire: FormData) {
    const valeurs = Object.fromEntries(
      CHAMPS[puce].map((c) => {
        const v = String(formulaire.get(c) ?? "").trim();
        return [c, v === "" ? null : c === "age" ? Number(v) : v];
      }),
    );
    setEdition(null);
    relancer({ ...filtres, ...valeurs });
  }

  return (
    <div className="puces" aria-label="Filtres appliqués à la recherche">
      {liste.map(({ puce, texte }) =>
        edition === puce ? (
          <form
            key={puce}
            className="puce puce--edition"
            onSubmit={(e) => {
              e.preventDefault();
              valider(puce, new FormData(e.currentTarget));
            }}
            onKeyDown={(e) => e.key === "Escape" && setEdition(null)}
          >
            {CHAMPS[puce].map((c) => (
              <label key={c}>
                {ETIQUETTES[c]}
                <input
                  name={c}
                  type={c.startsWith("date") ? "date" : c === "age" ? "number" : "text"}
                  min={c === "age" ? 0 : undefined}
                  defaultValue={filtres[c] ?? ""}
                  autoFocus={c === CHAMPS[puce][0]}
                />
              </label>
            ))}
            <button type="submit" disabled={occupe}>
              Relancer
            </button>
          </form>
        ) : (
          <span key={puce} className="puce">
            <button type="button" onClick={() => setEdition(puce)} title="Corriger ce filtre" disabled={occupe}>
              {texte}
            </button>
            <button
              type="button"
              onClick={() => relancer(sans(filtres, puce))}
              aria-label={`Retirer ${texte}`}
              disabled={occupe}
            >
              ×
            </button>
          </span>
        ),
      )}
    </div>
  );
}
