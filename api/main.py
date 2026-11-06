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
    erreur      {"message": "...", "reessai": bool}  reessai = un nouvel essai suit, sinon le flux s'arrête
    fin         {}

Le même contrat est décrit côté navigateur dans web/lib/flux.ts.
"""

import asyncio
import json
import re
import sys
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from openai import RateLimitError
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # rag.py et extract.py vivent dans src/

import rag  # noqa: E402  charge l'index Faiss et le modèle une seule fois, au démarrage
from extract import SORTIE as BRUTS  # noqa: E402

ESSAIS = 4
ATTENTE = 3  # secondes entre deux essais : le pool Mistral d'OpenRouter sature par rafales
CITATION = re.compile(r"\[(\d+(?:\s*[,;]\s*\d+)*)\]")  # [2], et [1, 3] quand le modèle en groupe
CHAMPS = ["uid", "titre", "dates_texte", "date_debut", "date_fin", "lieu", "ville", "lien",
          "image", "latitude", "longitude", "age_min", "age_max"]

app = FastAPI(title="Puls-Events")


class Question(BaseModel):
    question: str
    filtres: rag.Filtres | None = None


def sse(nom, donnees):
    return f"event: {nom}\ndata: {json.dumps(donnees, ensure_ascii=False)}\n\n"


def fiche(metadata):
    # les champs absents d'un index construit avant la V2, ou vides dans OpenAgenda, partent à null
    return {c: metadata.get(c) if metadata.get(c) != "" else None for c in CHAMPS}


def citations(texte, nombre):
    numeros = {int(n) for groupe in CITATION.findall(texte) for n in re.split(r"[,;]", groupe)}
    return {"cites": sorted(n for n in numeros if 1 <= n <= nombre),
            "inconnus": sorted(n for n in numeros if not 1 <= n <= nombre)}


async def repondre(question, imposes):
    lecture = rag.Lecture(**imposes.model_dump()) if imposes else await rag.lecteur.ainvoke(question)
    yield sse("filtres", lecture.model_dump(mode="json", exclude={"precision", "pistes"}))
    if lecture.vague():
        yield sse("texte", {"texte": lecture.precision})
        yield sse("pistes", {"pistes": lecture.pistes})
        yield sse("fin", {})
        return

    documents = await rag.recherche.ainvoke({"question": question, "filtres": lecture})
    # un évènement découpé en plusieurs chunks n'est qu'une source, numérotée comme dans rag.en_contexte
    evenements = list({d.metadata["uid"]: d for d in documents}.values())
    yield sse("sources", {"sources": [{"numero": n} | fiche(d.metadata) for n, d in enumerate(evenements, 1)]})

    for essai in range(1, ESSAIS + 1):
        texte = ""
        try:
            async for morceau in rag.generation.astream({"question": question, "documents": documents}):
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
