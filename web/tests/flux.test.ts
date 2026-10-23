import assert from "node:assert/strict";
import test from "node:test";
import { appliquer, lireFlux, type Echange } from "../lib/flux.ts";

const vide: Echange = { question: "Du jazz ?", reponse: "", sources: [], etat: "en_cours" };

test("un bloc SSE coupé en deux attend la suite", () => {
  const { evenements, reste } = lireFlux('event: texte\ndata: {"texte": "Bon"}\n\nevent: texte\ndata: {"tex');
  assert.deepEqual(evenements, [{ nom: "texte", donnees: { texte: "Bon" } }]);
  assert.equal(lireFlux(reste + 'te": "jour"}\n\n').evenements[0].donnees.texte, "jour");
});

test("le texte s'ajoute et efface l'avis de nouvel essai", () => {
  let e = appliquer(vide, { nom: "erreur", donnees: { message: "saturé, nouvel essai…", reessai: true } });
  assert.equal(e.etat, "en_cours");
  e = appliquer(e, { nom: "texte", donnees: { texte: "Macbeth [1]" } });
  assert.equal(e.reponse, "Macbeth [1]");
  assert.equal(e.erreur, undefined);
});

test("une erreur définitive termine l'échange, fin aussi", () => {
  assert.equal(appliquer(vide, { nom: "erreur", donnees: { message: "échec", reessai: false } }).etat, "fini");
  assert.equal(appliquer(vide, { nom: "fin", donnees: {} }).etat, "fini");
});
