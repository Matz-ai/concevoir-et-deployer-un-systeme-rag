"""API web de Puls-Events : expose au navigateur la chaîne RAG de src/rag.py.

`POST /api/chat` reçoit `{"question": "...", "filtres": {...} | null}` : des filtres envoyés (corrigés dans
l'interface) remplacent ceux que Mistral lit dans la question. La réponse est un flux SSE
(`text/event-stream`), chaque évènement porte un nom et un JSON :

    filtres     {"ville", "date_min", "date_max", "age", "theme"}   null quand la question ne dit rien
    pistes      {"pistes": ["...", "..."]}   question trop vague : le texte demande une précision,
                ces relances l'accompagnent, et le flux s'arrête là (ni sources ni citations)
    sources     {"sources": [{numero, uid, titre, dates_texte, lieu, ville, lien, image, ...}]}
                envoyé dès que la recherche a répondu, avant la génération ; `numero` est le [n] du contexte
    texte       {"texte": "..."}             un morceau de réponse, au fil de l'eau
    citations   {"cites": [1, 3], "inconnus": [7]}   les [n] de la réponse, rattachés ou non à une source
    cout        {"jetons_entree", "jetons_sortie", "euros", "recherche_s", "generation_s"}   juste avant fin ;
                recherche_s compte la lecture des filtres et la recherche, les jetons les deux appels Mistral
    erreur      {"message": "...", "reessai": bool}  reessai = un nouvel essai suit, sinon le flux s'arrête
    fin         {}

Le même contrat est décrit côté navigateur dans web/lib/flux.ts.

`POST /api/avis` enregistre un avis dans data/avis.jsonl, chaque réponse va dans data/journal.jsonl, et
`GET /api/qualite` réunit ces deux journaux et les évaluations du jeu de test pour la page /qualite.
"""

import asyncio
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import UsageMetadataCallbackHandler
from openai import RateLimitError
from pydantic import BaseModel

DONNEES = Path(__file__).resolve().parents[1] / "data"
sys.path.insert(0, str(DONNEES.parent / "src"))  # rag.py et extract.py vivent dans src/

import rag  # noqa: E402  charge l'index Faiss et le modèle une seule fois, au démarrage
from extract import SORTIE as BRUTS  # noqa: E402

ESSAIS = 4
ATTENTE = 3  # secondes entre deux essais : le pool Mistral d'OpenRouter sature par rafales
CITATION = re.compile(r"\[(\d+(?:\s*[,;]\s*\d+)*)\]")  # [2], et [1, 3] quand le modèle en groupe
CHAMPS = ["uid", "titre", "dates_texte", "date_debut", "date_fin", "lieu", "ville", "lien",
          "image", "latitude", "longitude", "age_min", "age_max"]
AVIS, JOURNAL = DONNEES / "avis.jsonl", DONNEES / "journal.jsonl"
PRIX_ENTREE, PRIX_SORTIE = 0.50, 1.50  # $ par million de jetons, mistral-large-2512 sur OpenRouter (06/11/2026)
EUROS_PAR_DOLLAR = 0.89  # taux BCE du 05/11/2026 : un ordre de grandeur, pas une facture

app = FastAPI(title="Puls-Events")


class Question(BaseModel):
    question: str
    filtres: rag.Filtres | None = None


class Avis(BaseModel):
    id: str  # le même id renvoyé avec un commentaire remplace le premier clic, sans compter deux avis
    avis: Literal["pour", "contre"]
    commentaire: str = ""
    question: str
    filtres: rag.Filtres | None = None
    sources: list[dict] = []
    reponse: str


def sse(nom, donnees):
    return f"event: {nom}\ndata: {json.dumps(donnees, ensure_ascii=False)}\n\n"


def fiche(metadata):
    # les champs absents d'un index construit avant la V2, ou vides dans OpenAgenda, partent à null
    return {c: metadata.get(c) if metadata.get(c) != "" else None for c in CHAMPS}


def citations(texte, nombre):
    numeros = {int(n) for groupe in CITATION.findall(texte) for n in re.split(r"[,;]", groupe)}
    return {"cites": sorted(n for n in numeros if 1 <= n <= nombre),
            "inconnus": sorted(n for n in numeros if not 1 <= n <= nombre)}


def ajouter(fichier, ligne):
    with fichier.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"date": datetime.now().isoformat(timespec="seconds")} | ligne, ensure_ascii=False) + "\n")


def lire(fichier):
    return [json.loads(ligne) for ligne in fichier.read_text(encoding="utf-8").splitlines()] if fichier.exists() else []


def cout(usage, recherche_s, generation_s):
    """Additionne les appels Mistral d'une réponse (lecture des filtres, génération) et convertit en euros."""
    entree = sum(u["input_tokens"] for u in usage.values())
    sortie = sum(u["output_tokens"] for u in usage.values())
    dollars = (entree * PRIX_ENTREE + sortie * PRIX_SORTIE) / 1_000_000
    return {"jetons_entree": entree, "jetons_sortie": sortie, "euros": round(dollars * EUROS_PAR_DOLLAR, 6),
            "recherche_s": round(recherche_s, 2), "generation_s": round(generation_s, 2)}


def noter(question, lecture, usage, recherche_s, generation_s=0):
    bilan = cout(usage.usage_metadata, recherche_s, generation_s)
    ajouter(JOURNAL, {"question": question, "filtres": lecture.model_dump(mode="json")} | bilan)
    return sse("cout", bilan)


async def repondre(question, imposes):
    usage = UsageMetadataCallbackHandler()  # relève les jetons de chaque appel Mistral lancé avec ce suivi
    suivi = {"callbacks": [usage]}
    debut = time.perf_counter()
    lecture = rag.Lecture(**imposes.model_dump()) if imposes else await rag.lecteur.ainvoke(question, suivi)
    yield sse("filtres", lecture.model_dump(mode="json", exclude={"precision", "pistes"}))
    if lecture.vague():
        yield sse("texte", {"texte": lecture.precision})
        yield sse("pistes", {"pistes": lecture.pistes})
        yield noter(question, lecture, usage, time.perf_counter() - debut)
        yield sse("fin", {})
        return

    documents = await rag.recherche.ainvoke({"question": question, "filtres": lecture})
    recherche_s = time.perf_counter() - debut
    # un évènement découpé en plusieurs chunks n'est qu'une source, numérotée comme dans rag.en_contexte
    evenements = list({d.metadata["uid"]: d for d in documents}.values())
    yield sse("sources", {"sources": [{"numero": n} | fiche(d.metadata) for n, d in enumerate(evenements, 1)]})

    for essai in range(1, ESSAIS + 1):
        texte = ""
        try:
            async for morceau in rag.generation.astream({"question": question, "documents": documents}, suivi):
                texte += morceau
                yield sse("texte", {"texte": morceau})
            break
        except RateLimitError:
            # une 429 au milieu d'une réponse déjà affichée ne se rejoue pas : on garde ce qui est arrivé
            if texte or essai == ESSAIS:
                yield sse("erreur", {"message": "Le service Mistral est saturé, réessayez dans un instant.",
                                     "reessai": False})
                return
            yield sse("erreur", {"message": "Le service Mistral est saturé, nouvel essai…", "reessai": True})
            await asyncio.sleep(ATTENTE)

    yield sse("citations", citations(texte, len(evenements)))
    yield noter(question, lecture, usage, recherche_s, time.perf_counter() - debut - recherche_s)
    yield sse("fin", {})


async def sans_plantage(flux):
    try:
        async for evenement in flux:
            yield evenement
    except RateLimitError:  # la lecture des filtres a épuisé les nouveaux essais du client OpenAI
        yield sse("erreur", {"message": "Le service Mistral est saturé, réessayez dans un instant.", "reessai": False})
    except Exception as e:  # clé refusée, réseau coupé : le navigateur doit lire une erreur, pas un flux coupé net
        yield sse("erreur", {"message": f"La réponse a échoué ({type(e).__name__}).", "reessai": False})


@app.post("/api/chat")
def chat(q: Question):
    # pas d'historique : chaque question est traitée seule, comme le demande l'énoncé
    return StreamingResponse(sans_plantage(repondre(q.question, q.filtres)), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache"})


@app.get("/api/evenements/{uid}")
def evenement(uid: int):
    for id_ in rag.index.index_to_docstore_id.values():
        metadata = rag.index.docstore.search(id_).metadata
        if metadata["uid"] == uid:
            return fiche(metadata) | {"description": metadata["description"]}
    raise HTTPException(404, f"aucun évènement {uid} dans l'index")


@app.get("/api/sante")
def sante():
    uids = {rag.index.docstore.search(i).metadata["uid"] for i in rag.index.index_to_docstore_id.values()}
    return {"index": True, "vecteurs": rag.index.index.ntotal, "evenements": len(uids),
            "donnees": date.fromtimestamp(BRUTS.stat().st_mtime).isoformat() if BRUTS.exists() else None}


@app.post("/api/avis", status_code=204)
def donner_avis(avis: Avis):
    ajouter(AVIS, avis.model_dump(mode="json"))


def scores(lignes):
    """Réponses correctes et rappel de la recherche d'un groupe de questions évaluées."""
    rappels = [r.split("/") for r in lignes.recherche if r != "-"]
    return {"correctes": int(lignes.correct.sum()), "questions": len(lignes),
            "trouves": sum(int(t) for t, _ in rappels), "attendus": sum(int(a) for _, a in rappels)}


@app.get("/api/qualite")
def qualite():
    v1, v2 = pd.read_csv(DONNEES / "evaluation_v1.csv"), pd.read_csv(DONNEES / "evaluation_v2.csv")
    annotees = json.loads((DONNEES / "qa_test.json").read_text(encoding="utf-8"))
    avis = list({a["id"]: a for a in lire(AVIS)}.values())  # le dernier envoi d'un même avis fait foi
    journal = pd.DataFrame(lire(JOURNAL))
    return {
        "total": {"v1": scores(v1), "v2": scores(v2)},
        "types": [{"type": t, "v1": scores(v1[v1.type == t]), "v2": scores(v2[v2.type == t])} for t in v2.type.unique()],
        "questions": [{"question": q["question"], "type": q["type"], "attendu": q["reponse_attendue"],
                       "obtenu": ligne.reponse, "justification": ligne.justification, "recherche": ligne.recherche,
                       "correct_v1": bool(avant), "correct_v2": bool(ligne.correct)}
                      for q, ligne, avant in zip(annotees, v2.itertuples(), v1.correct)],
        "avis": {"pour": sum(a["avis"] == "pour" for a in avis), "contre": sum(a["avis"] == "contre" for a in avis),
                 "commentaires": [{"avis": a["avis"], "question": a["question"], "commentaire": a["commentaire"]}
                                  for a in avis[::-1] if a["commentaire"]][:10]},
        "production": {"reponses": len(journal)} | (
            journal[["euros", "jetons_entree", "jetons_sortie", "recherche_s", "generation_s"]].mean().round(6).to_dict()
            if len(journal) else {}),
        "donnees": date.fromtimestamp(BRUTS.stat().st_mtime).isoformat() if BRUTS.exists() else None,
    }
