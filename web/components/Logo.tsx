/** Mot-symbole Puls-Events : le nom précédé d'une ligne de pouls, qui prend la couleur d'accent. */
export default function Logo({ grand = false }: { grand?: boolean }) {
  return (
    <span className={grand ? "logo logo--grand" : "logo"}>
      <svg viewBox="0 0 40 20" aria-hidden="true">
        <polyline points="0,11 10,11 14,4 19,17 24,1 28,11 40,11" />
      </svg>
      Puls-Events
    </span>
  );
}
