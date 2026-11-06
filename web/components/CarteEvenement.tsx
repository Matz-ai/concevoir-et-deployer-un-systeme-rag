import type { Source } from "@/lib/flux.ts";

function ages(s: Source): string | null {
  if (s.age_min && s.age_max && s.age_max < 99) return `${s.age_min}–${s.age_max} ans`;
  if (s.age_min) return `dès ${s.age_min} an${s.age_min > 1 ? "s" : ""}`;
  return null;
}

export default function CarteEvenement({ source, id, cite, allume, survoler }: {
  source: Source;
  id: string;
  cite: boolean;
  allume?: boolean;
  survoler?: (numeros: number[]) => void;
}) {
  const tranche = ages(source);
  return (
    <article
      className={`carte${cite ? " carte--citee" : ""}${allume ? " carte--allumee" : ""}`}
      id={id}
      onMouseEnter={() => survoler?.([source.numero])}
      onMouseLeave={() => survoler?.([])}
      onFocus={() => survoler?.([source.numero])}
      onBlur={() => survoler?.([])}
    >
      {source.image ? (
        <img className="carte-image" src={source.image} alt="" loading="lazy" />
      ) : (
        <div className="carte-image carte-image--vide" aria-hidden="true" />
      )}
      <div className="carte-corps">
        <div className="carte-badges">
          <span className="numero">{source.numero}</span>
          {cite && <span className="badge">cité</span>}
          {tranche && <span className="badge badge--discret">{tranche}</span>}
        </div>
        <h2>{source.titre}</h2>
        {source.dates_texte && <p className="carte-date">{source.dates_texte}</p>}
        <p className="carte-lieu">{[source.lieu, source.ville].filter(Boolean).join(" · ")}</p>
        {source.lien && (
          <a href={source.lien} target="_blank" rel="noopener noreferrer">
            Fiche OpenAgenda<span aria-hidden="true"> ↗</span>
          </a>
        )}
      </div>
    </article>
  );
}
