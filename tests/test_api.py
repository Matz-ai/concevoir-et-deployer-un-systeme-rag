"""Contrôles de l'API web, sans réseau : l'index et le modèle Mistral sont remplacés par des faux.

La CI n'a ni clé OpenRouter ni index Faiss. On importe donc la vraie chaîne de rag.py (prompt,
numérotation du contexte, filtres) en neutralisant le chargement de l'index et le client Mistral, puis
chaque test branche la lecture des filtres, la recherche et la génération dont il a besoin.
"""

import json
import os
from datetime import date
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.runnables import RunnableLambda
from openai import RateLimitError

faux_modele = GenericFakeChatModel(messages=iter([]))
with (patch.dict(os.environ, {"OPENROUTER_API_KEY": "test"}),
      patch("langchain_community.vectorstores.FAISS.load_local"),
      patch("langchain_openai.ChatOpenAI", lambda **_: faux_modele),
      patch("langchain_community.retrievers.BM25Retriever.from_documents"),
      patch.object(GenericFakeChatModel, "with_structured_output", lambda modele, _: modele)):
    import main
    import rag


def chunk(uid, titre, texte):
    return Document(page_content=texte, metadata={
        "uid": uid, "titre": titre, "description": texte, "date_debut": "2026-11-20T19:00:00+00:00",
        "date_fin": "2026-11-20T21:00:00+00:00", "dates_texte": "Vendredi 20 novembre, 20h00",
        "lieu": "Espace Albatros", "ville": "Montreuil", "lien": f"https://openagenda.com/e/{uid}",
        "age_min": "", "age_max": ""})


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
    monkeypatch.setattr(rag, "lecteur", RunnableLambda(lambda question: rag.Lecture(ville="Montreuil")))
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
    assert noms[:2] == ["filtres", "sources"] and noms[-2:] == ["citations", "fin"] and "texte" in noms
    assert flux[0][1]["ville"] == "Montreuil" and flux[0][1]["date_min"] is None
    assert [(s["numero"], s["titre"]) for s in flux[1][1]["sources"]] == [(1, "Macbeth"), (2, "Le Conte d'hiver")]
    assert "".join(d["texte"] for nom, d in flux if nom == "texte").endswith("fantôme [7].")
    assert flux[-2][1] == {"cites": [1, 2], "inconnus": [7]}


def test_une_429_est_reessayee(client, monkeypatch):
    monkeypatch.setattr(rag, "generation", Saturee(echecs=1))
    flux = evenements(client.post("/api/chat", json={"question": "Du Shakespeare ?"}))
    assert [nom for nom, _ in flux] == ["filtres", "sources", "erreur", "texte", "citations", "fin"]
    assert flux[2][1]["reessai"] is True


def test_une_saturation_durable_finit_par_une_erreur(client, monkeypatch):
    monkeypatch.setattr(rag, "generation", Saturee(echecs=10))
    flux = evenements(client.post("/api/chat", json={"question": "Du Shakespeare ?"}))
    assert flux[-1][0] == "erreur" and flux[-1][1]["reessai"] is False
    assert len(flux) == 2 + main.ESSAIS


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
    assert flux[1:] == [("erreur", {"message": "La réponse a échoué (ConnectionError).", "reessai": False})]


def test_une_question_vague_appelle_une_precision(client, monkeypatch):
    monkeypatch.setattr(rag, "lecteur", RunnableLambda(lambda question: rag.Lecture(
        precision="Plutôt concert ou spectacle ?", pistes=["Un concert ce week-end", "Un spectacle pour enfants"])))
    flux = evenements(client.post("/api/chat", json={"question": "Un truc sympa ?"}))
    assert [nom for nom, _ in flux] == ["filtres", "texte", "pistes", "fin"]
    assert flux[2][1]["pistes"] == ["Un concert ce week-end", "Un spectacle pour enfants"]


def test_des_filtres_imposes_remplacent_la_lecture(client, monkeypatch):
    recus = []
    monkeypatch.setattr(rag, "lecteur", RunnableLambda(lambda question: pytest.fail("la question a été relue")))
    monkeypatch.setattr(rag, "recherche", RunnableLambda(lambda entree: recus.append(entree["filtres"]) or DOCUMENTS))
    faux_modele.messages = iter(["Macbeth [1]."])
    flux = evenements(client.post("/api/chat", json={"question": "Du Shakespeare ?",
                                                      "filtres": {"date_min": "2026-11-20"}}))
    assert flux[0] == ("filtres", {"ville": None, "date_min": "2026-11-20", "date_max": None, "age": None, "theme": None})
    assert recus[0].date_min.isoformat() == "2026-11-20"


def test_les_filtres_s_appliquent_aux_metadonnees(monkeypatch):
    monkeypatch.setattr(rag, "aujourdhui", date(2026, 9, 25))
    macbeth = DOCUMENTS[0].metadata | {"age_min": 8, "age_max": 99}
    assert rag.garde(rag.Filtres())(macbeth)
    assert rag.garde(rag.Filtres(ville="montreuil", date_min=date(2026, 11, 20), date_max=date(2026, 11, 22)))(macbeth)
    assert not rag.garde(rag.Filtres(ville="Bobigny"))(macbeth)
    assert not rag.garde(rag.Filtres(date_max=date(2026, 11, 19)))(macbeth)
    assert not rag.garde(rag.Filtres(age=4))(macbeth)
    assert rag.garde(rag.Filtres(age=4))(DOCUMENTS[0].metadata)  # sans âge indiqué, l'évènement reste
    monkeypatch.setattr(rag, "aujourdhui", date(2026, 12, 1))
    assert not rag.garde(rag.Filtres())(macbeth)  # déjà terminé


def test_la_recherche_hybride_trouve_un_mot_exact_et_respecte_les_filtres(monkeypatch):
    monkeypatch.setattr(rag, "aujourdhui", date(2026, 9, 25))
    monkeypatch.setattr(rag, "index", FAISS.from_documents(DOCUMENTS, DeterministicFakeEmbedding(size=8)))
    monkeypatch.setattr(rag, "bm25", BM25Retriever.from_documents(DOCUMENTS, k=3, preprocess_func=rag.mots))
    trouves = rag.chercher({"question": "shakespeare", "filtres": rag.Filtres()})
    assert trouves[0].metadata["titre"] == "Le Conte d'hiver"  # le faux vectoriseur classe au hasard, BM25 non
    assert rag.chercher({"question": "shakespeare", "filtres": rag.Filtres(ville="Bobigny")}) == []


def test_une_saturation_a_la_lecture_des_filtres_est_lisible(client, monkeypatch):
    async def saturee(question):
        raise RateLimitError("429", response=httpx.Response(429, request=httpx.Request("POST", "https://x")), body=None)
    monkeypatch.setattr(rag, "lecteur", RunnableLambda(saturee))
    flux = evenements(client.post("/api/chat", json={"question": "Du jazz ?"}))
    assert flux == [("erreur", {"message": "Le service Mistral est saturé, réessayez dans un instant.", "reessai": False})]
