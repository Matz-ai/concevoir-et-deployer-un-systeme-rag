import assert from "node:assert/strict";
import test from "node:test";
import { periode, puces, sans } from "../lib/filtres.ts";
import type { Filtres } from "../lib/flux.ts";

const vides: Filtres = { ville: null, date_min: null, date_max: null, age: null, theme: null };

test("une période se dit comme à l'oral", () => {
  assert.equal(periode("2026-12-05", "2026-12-06"), "5–6 déc.");
  assert.equal(periode("2027-06-21", "2027-06-21"), "21 juin");
  assert.equal(periode("2026-11-28", "2026-12-01"), "28 nov. – 1 déc.");
  assert.equal(periode("2026-12-05", null), "dès le 5 déc.");
});

test("une puce par filtre lu, aucune sans filtre", () => {
  assert.deepEqual(puces(vides), []);
  const f = { ...vides, ville: "Montreuil", date_min: "2026-12-05", date_max: "2026-12-06", age: 4 };
  assert.deepEqual(puces(f).map((p) => p.texte), ["📍 Montreuil", "📅 5–6 déc.", "🧒 4 ans"]);
});

test("retirer la puce des dates efface les deux bornes", () => {
  const f = { ...vides, ville: "Bondy", date_min: "2026-12-05", date_max: "2026-12-06" };
  assert.deepEqual(sans(f, "dates"), { ...vides, ville: "Bondy" });
});
