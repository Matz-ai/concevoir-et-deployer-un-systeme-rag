import assert from "node:assert/strict";
import test from "node:test";
import { cites, decouper } from "../lib/citations.ts";

test("le texte est coupé autour des citations, groupes compris", () => {
  assert.deepEqual(decouper("Macbeth [1], Le Conte d'hiver [2, 3]."), [
    "Macbeth ", { numeros: [1] }, ", Le Conte d'hiver ", { numeros: [2, 3] }, ".",
  ]);
});

test("seuls les numéros qui ont une source comptent, sans doublon", () => {
  assert.deepEqual(cites("[3] puis [1] puis [3] et [7]", 4), [1, 3]);
});

test("un crochet qui n'est pas un numéro reste du texte", () => {
  assert.deepEqual(decouper("[à confirmer]"), ["[à confirmer]"]);
});
