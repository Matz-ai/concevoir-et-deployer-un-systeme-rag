"""Chaîne RAG : filtres lus dans la question, recherche hybride (BM25 + Faiss), puis réponse de Mistral."""

import os
import re
import sys
from datetime import date

from dotenv import load_dotenv
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from build_index import MODELE, OPENROUTER, SORTIE

MODELE_CHAT = "mistralai/mistral-large-2512"
K = 10  # chunks remontés par question : le modèle écarte ceux qui ne répondent pas
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

CONSIGNE = """Tu es l'assistant de Puls-Events. Tu recommandes des évènements culturels en
Seine-Saint-Denis. Nous sommes le {aujourdhui}.
Réponds uniquement à partir des évènements ci-dessous. Si aucun ne correspond à la question,
dis-le franchement au lieu d'en inventer un. Cite pour chaque évènement proposé son titre,
sa date et son lieu, suivis de son numéro entre crochets, par exemple [2].

Évènements :
{contexte}"""

LECTURE = """Tu prépares la recherche dans un agenda culturel de Seine-Saint-Denis. Nous sommes le
{jour} {aujourdhui}. Remplis seulement ce que la question dit explicitement, laisse vide le reste :
- ville : une commune de cette liste, écrite à l'identique : {communes} ;
- date_min et date_max : la période demandée, en dates réelles (« ce week-end » : le samedi et le
  dimanche qui viennent ; « en décembre » : du 1er au 31 décembre ; « le 21 juin » : ce seul jour) ;
- age : l'âge de l'enfant ou du public, s'il est donné ;
- theme : le genre ou le sujet cherché, en un à trois mots (« jazz », « marionnettes »).
Seulement si la question ne permet de remplir aucun de ces champs (« un truc sympa ? »), écris dans
precision une question courte pour la préciser, et dans pistes deux ou trois demandes que
l'utilisateur pourrait envoyer telles quelles, sans nommer de lieu ni d'évènement précis (« Un
concert ce week-end », « Une sortie avec un enfant de 6 ans »). Sinon, laisse precision et pistes vides."""


class Filtres(BaseModel):
    """Ce que la question impose à la recherche ; un champ vide ne filtre rien."""
    ville: str | None = Field(None, description="commune de Seine-Saint-Denis citée")
    date_min: date | None = Field(None, description="premier jour de la période demandée")
    date_max: date | None = Field(None, description="dernier jour de la période demandée")
    age: int | None = Field(None, description="âge de l'enfant ou du public, en années")
    theme: str | None = Field(None, description="genre ou sujet cherché, en un à trois mots")


class Lecture(Filtres):
    precision: str | None = Field(None, description="question de précision, si la demande est trop vague")
    pistes: list[str] = Field([], description="deux ou trois demandes plus précises à proposer")

    def vague(self):
        # le modèle demande trop volontiers une précision : on ne la pose que s'il n'a lu aucun filtre
        return bool(self.precision) and not any([self.ville, self.date_min, self.date_max, self.age, self.theme])


def numeros(documents):
    """Numérote les évènements dans l'ordre où la recherche les remonte. Les chunks d'un même évènement
    partagent son numéro : c'est lui que le modèle cite et que l'API rattache à la carte affichée."""
    return {uid: n for n, uid in enumerate(dict.fromkeys(d.metadata["uid"] for d in documents), 1)}


def en_contexte(documents):
    n = numeros(documents)
    # les dates affichées par OpenAgenda n'ont pas d'année : on préfixe la date de début complète
    return "\n\n".join(f"[{n[d.metadata['uid']]}] Début : {d.metadata['date_debut'][:10]}\n{d.page_content}"
                       for d in documents)


def mots(texte):
    # BM25 compare des mots exacts : « Jazz, » et « jazz » doivent être le même mot
    return re.findall(r"\w+", texte.lower())


def garde(filtres):
    """Le test appliqué aux métadonnées de chaque chunk : pas encore terminé, puis ce que la question impose."""
    debut = max(filtres.date_min or aujourdhui, aujourdhui).isoformat()
    fin = filtres.date_max.isoformat() if filtres.date_max else "9999"
    ville = (filtres.ville or "").lower()
    # 88 % des évènements n'indiquent pas d'âge : on ne les écarte pas, on écarte ceux qui excluent cet âge
    age = filtres.age
    return lambda m: (m["date_fin"][:10] >= debut and m["date_debut"][:10] <= fin
                      and m["ville"].lower().startswith(ville)  # « Saint-Ouen » couvre « Saint-Ouen-sur-Seine »
                      and (age is None or (m["age_min"] or 0) <= age <= (m["age_max"] or 120)))


def chercher(entree):
    """question + filtres -> les K meilleurs chunks de BM25 (mots exacts) et de Faiss (sens), réunis."""
    passe = garde(entree["filtres"])
    semantique = index.as_retriever(search_kwargs={"k": K, "fetch_k": index.index.ntotal, "filter": passe})
    # BM25 cherche les mots du thème lu (« jazz ») : ceux du reste de la question (« prévus »,
    # « Seine-Saint-Denis ») sont partout dans l'agenda et noient le mot qui compte
    mots_cles = entree["filtres"].theme or entree["question"]
    exacts = RunnableLambda(lambda _: [d for d in bm25.invoke(mots_cles) if passe(d.metadata)][:K])
    ensemble = EnsembleRetriever(retrievers=[exacts, semantique], weights=[0.5, 0.5])
    return ensemble.invoke(entree["question"])[:K]


load_dotenv()
cle = os.environ["OPENROUTER_API_KEY"]
# le jeu de test est écrit au 25/09/2026 : DATE_REFERENCE=2026-09-25 le rejoue tel qu'il a été annoté
aujourdhui = date.fromisoformat(os.environ.get("DATE_REFERENCE") or date.today().isoformat())
vectoriseur = OpenAIEmbeddings(model=MODELE, base_url=OPENROUTER, api_key=cle,
                               check_embedding_ctx_length=False)
index = FAISS.load_local(str(SORTIE), vectoriseur, allow_dangerous_deserialization=True)  # index produit par build_index.py
chunks = [index.docstore.search(i) for i in index.index_to_docstore_id.values()]
# BM25 classe tous les chunks, puis on garde les K meilleurs qui passent les filtres, comme pour Faiss
bm25 = BM25Retriever.from_documents(chunks, k=len(chunks), preprocess_func=mots)
communes = sorted({d.metadata["ville"] for d in chunks})

modele = ChatOpenAI(model=MODELE_CHAT, base_url=OPENROUTER, api_key=cle, temperature=0,
                    max_retries=5)  # le pool Mistral d'OpenRouter renvoie des 429 par moments
lecteur = (ChatPromptTemplate.from_messages([("system", LECTURE), ("human", "{question}")]).partial(
    jour=JOURS[aujourdhui.weekday()], aujourdhui=aujourdhui.strftime("%d/%m/%Y"), communes=", ".join(communes))
    | modele.with_structured_output(Lecture))
recherche = RunnableLambda(chercher)
prompt = ChatPromptTemplate.from_messages([("system", CONSIGNE), ("human", "{question}")])
generation = (RunnablePassthrough.assign(contexte=lambda x: en_contexte(x["documents"]))
              | prompt.partial(aujourdhui=aujourdhui.strftime("%d/%m/%Y")) | modele | StrOutputParser())


def repondre(question):
    """question -> filtres lus, documents, réponse : les sources restent disponibles pour l'affichage."""
    lecture = lecteur.invoke(question)
    if lecture.vague():  # trop vague pour chercher : on demande avant de proposer des évènements au hasard
        reponse = "\n".join([lecture.precision] + [f"- {p}" for p in lecture.pistes])
        return {"question": question, "filtres": lecture, "documents": [], "reponse": reponse}
    documents = recherche.invoke({"question": question, "filtres": lecture})
    return {"question": question, "filtres": lecture, "documents": documents,
            "reponse": generation.invoke({"question": question, "documents": documents})}


chaine = RunnableLambda(repondre)


if __name__ == "__main__":
    resultat = chaine.invoke(sys.argv[1])
    print(resultat["filtres"], "\n")
    print(resultat["reponse"], "\n")
    for d in resultat["documents"]:
        print("-", d.metadata["titre"], "|", d.metadata["dates_texte"], "|", d.metadata["lieu"])
