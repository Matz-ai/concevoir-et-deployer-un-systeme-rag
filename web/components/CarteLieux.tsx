"use client";

import { useEffect, useRef, useState } from "react";
import type { LayerGroup, Map as CarteLeaflet, Marker } from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Lieu } from "@/lib/lieux.ts";

const CENTRE_93: [number, number] = [48.91, 2.47];

/** Carte OpenStreetMap des lieux cités. Leaflet touche à `window` : on ne le charge que dans le navigateur. */
export default function CarteLieux({ lieux, survol, survoler, ouvrir }: {
  lieux: Lieu[];
  survol: number[];
  survoler: (numeros: number[]) => void;
  ouvrir: (numero: number) => void;
}) {
  const conteneur = useRef<HTMLDivElement>(null);
  const [carte, setCarte] = useState<{ L: typeof import("leaflet"); map: CarteLeaflet; reperes: LayerGroup } | null>(null);
  const marqueurs = useRef<{ lieu: Lieu; marqueur: Marker }[]>([]);
  const cadrage = useRef<() => void>(() => {});

  useEffect(() => {
    let annule = false;
    let fin = () => {};
    import("leaflet").then((L) => {
      if (annule || !conteneur.current) return;
      const map = L.map(conteneur.current, { scrollWheelZoom: false }).setView(CENTRE_93, 11);
      map.attributionControl.setPrefix(false);
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }).addTo(map);
      // sur téléphone la carte naît masquée sous l'onglet Liste : il faut la recadrer quand elle apparaît
      const taille = new ResizeObserver(() => {
        map.invalidateSize();
        cadrage.current();
      });
      taille.observe(conteneur.current);
      fin = () => {
        taille.disconnect();
        map.remove();
      };
      setCarte({ L, map, reperes: L.layerGroup().addTo(map) });
    });
    return () => {
      annule = true;
      fin();
    };
  }, []);

  useEffect(() => {
    if (!carte) return;
    const { L, map, reperes } = carte;
    reperes.clearLayers();
    marqueurs.current = lieux.map((lieu) => {
      const marqueur = L.marker([lieu.latitude, lieu.longitude], {
        title: `${lieu.nom}, évènement ${lieu.numeros.join(" et ")}`,
        icon: L.divIcon({
          className: "repere",
          html: lieu.numeros.join(","),
          iconSize: [lieu.numeros.join(",").length * 8 + 18, 26],
        }),
      })
        .on("mouseover", () => survoler(lieu.numeros))
        .on("mouseout", () => survoler([]))
        .on("click", () => ouvrir(lieu.numeros[0]))
        .addTo(reperes);
      return { lieu, marqueur };
    });
    cadrage.current = () => {
      if (lieux.length && map.getSize().x > 0)
        map.fitBounds(L.latLngBounds(lieux.map((l) => [l.latitude, l.longitude])), { padding: [36, 36], maxZoom: 14 });
    };
    cadrage.current();
  }, [carte, lieux, survoler, ouvrir]);

  useEffect(() => {
    for (const { lieu, marqueur } of marqueurs.current) {
      const allume = lieu.numeros.some((n) => survol.includes(n));
      marqueur.getElement()?.classList.toggle("repere--allume", allume);
      marqueur.setZIndexOffset(allume ? 1000 : 0);
    }
  }, [survol, carte, lieux]);

  return <div ref={conteneur} className="carte-lieux" role="region" aria-label="Carte des lieux cités" />;
}
