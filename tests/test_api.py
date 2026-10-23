"""Contrôles de l'API web, sans réseau : l'index et le modèle Mistral sont remplacés par des faux.

La CI n'a ni clé OpenRouter ni index Faiss. On importe donc la vraie chaîne de rag.py (prompt,
numérotation du contexte) en neutralisant le chargement de l'index et le client Mistral, puis chaque
test branche la recherche et la génération dont il a besoin.
"""

import json
import os
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.runnables import RunnableLambda
from openai import RateLimitError

faux_modele = GenericFakeChatModel(messages=iter([]))
with (patch.dict(os.environ, {"OPENROUTER_API_KEY": "test"}),
      patch("langchain_community.vectorstores.FAISS.load_local"),
      patch("langchain_openai.ChatOpenAI", lambda **_: faux_modele)):
    import main
    import rag


def chunk(uid, titre, texte):
    return Document(page_content=texte, metadata={
        "uid": uid, "titre": titre, "description": texte, "date_debut": "2026-11-20T19:00:00+00:00",
        "date_fin": "2026-11-20T21:00:00+00:00", "dates_texte": "Vendredi 20 novembre, 20h00",
        "lieu": "Espace Albatros", "ville": "Montreuil", "lien": f"https://openagenda.com/e/{uid}"})


# trois chunks, deux évènements : Macbeth est assez long pour avoir été découpé en deux
DOCUMENTS = [chunk(11, "Macbeth", "Macbeth, première partie."), chunk(22, "Le Conte d'hiver", "Shakespeare."),
             chunk(11, "Macbeth", "Macbeth, seconde partie.")]


class Saturee:
    """Une génération qui renvoie des 429 d'OpenRouter avant de répondre."""

    def __init__(self, echecs):
        self.echecs = echecs

    async def astream(self, entree):
        if self.echecs:
            self.echecs -= 1
            raise RateLimitError("429", response=httpx.Response(429, request=httpx.Request("POST", "https://x")),
                                 body=None)
        yield "Macbeth [1]."


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(rag, "recherche", RunnableLambda(lambda question: DOCUMENTS))
    monkeypatch.setattr(rag, "index", FAISS.from_documents(DOCUMENTS, DeterministicFakeEmbedding(size=8)))
    monkeypatch.setattr(main, "ATTENTE", 0)
    return TestClient(main.app)


def evenements(reponse):
    """Le flux SSE relu en liste de (nom, données)."""
    blocs = [b.split("\n") for b in reponse.text.strip().split("\n\n")]
    return [(b[0].removeprefix("event: "), json.loads(b[1].removeprefix("data: "))) for b in blocs]


def test_contexte_numerote_par_evenement():
    contexte = rag.en_contexte(DOCUMENTS)
    assert contexte.count("[1] Début") == 2 and contexte.count("[2] Début") == 1


def test_sources_puis_texte_puis_citations_verifiees(client):
    faux_modele.messages = iter(["Macbeth [1], Le Conte d'hiver [2] et un fantôme [7]."])
    flux = evenements(client.post("/api/chat", json={"question": "Du Shakespeare ?"}))

    noms = [nom for nom, _ in flux]
    assert noms[0] == "sources" and noms[-2:] == ["citations", "fin"] and "texte" in noms
    assert [(s["numero"], s["titre"]) for s in flux[0][1]["sources"]] == [(1, "Macbeth"), (2, "Le Conte d'hiver")]
    assert "".join(d["texte"] for nom, d in flux if nom == "texte").endswith("fantôme [7].")
    assert flux[-2][1] == {"cites": [1, 2], "inconnus": [7]}


def test_une_429_est_reessayee(client, monkeypatch):
    monkeypatch.setattr(rag, "generation", Saturee(echecs=1))
    flux = evenements(client.post("/api/chat", json={"question": "Du Shakespeare ?"}))
    assert [nom for nom, _ in flux] == ["sources", "erreur", "texte", "citations", "fin"]
    assert flux[1][1]["reessai"] is True


def test_une_saturation_durable_finit_par_une_erreur(client, monkeypatch):
    monkeypatch.setattr(rag, "generation", Saturee(echecs=10))
    flux = evenements(client.post("/api/chat", json={"question": "Du Shakespeare ?"}))
    assert flux[-1][0] == "erreur" and flux[-1][1]["reessai"] is False
    assert len(flux) == 1 + main.ESSAIS


def test_fiche_d_un_evenement(client):
    assert client.get("/api/evenements/22").json()["titre"] == "Le Conte d'hiver"
    assert client.get("/api/evenements/99").status_code == 404


def test_sante(client):
    assert client.get("/api/sante").json() | {"donnees": None} == {
        "index": True, "vecteurs": 3, "evenements": 2, "donnees": None}


def test_une_panne_de_recherche_devient_une_erreur_lisible(client, monkeypatch):
    def panne(question):
        raise ConnectionError("réseau coupé")
    monkeypatch.setattr(rag, "recherche", RunnableLambda(panne))
    flux = evenements(client.post("/api/chat", json={"question": "Du jazz ?"}))
    assert flux == [("erreur", {"message": "La réponse a échoué (ConnectionError).", "reessai": False})]
