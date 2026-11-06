import assert from "node:assert/strict";
import { test } from "node:test";
import type { Source } from "../lib/flux.ts";
import { lieux } from "../lib/lieux.ts";

const source = (numero: number, latitude: number | null, lieu: string) =>
  ({ numero, latitude, longitude: latitude && 2.4, lieu, ville: "Pantin" }) as Source;

test("deux évènements au même endroit font un seul repère", () => {
  const trouves = lieux([source(1, 48.9, "La Dynamo"), source(2, 48.8, "Le Théâtre"), source(3, 48.9, "La Dynamo")]);
  assert.deepEqual(trouves.map((l) => l.numeros), [[1, 3], [2]]);
  assert.equal(trouves[0].nom, "La Dynamo, Pantin");
});

test("un évènement sans coordonnées n'a pas de repère", () => {
  assert.deepEqual(lieux([source(1, null, "Inconnu")]), []);
});
