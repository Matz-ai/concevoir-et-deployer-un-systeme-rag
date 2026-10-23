"""Chaîne RAG : recherche des évènements dans l'index Faiss, puis réponse générée par Mistral."""

import os
import sys
from datetime import date

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from build_index import MODELE, OPENROUTER, SORTIE

MODELE_CHAT = "mistralai/mistral-large-2512"
K = 10  # chunks remontés par question : le modèle écarte ceux qui ne répondent pas

CONSIGNE = """Tu es l'assistant de Puls-Events. Tu recommandes des évènements culturels en
Seine-Saint-Denis. Nous sommes le {aujourdhui}.
Réponds uniquement à partir des évènements ci-dessous. Si aucun ne correspond à la question,
dis-le franchement au lieu d'en inventer un. Cite pour chaque évènement proposé son titre,
sa date et son lieu, suivis de son numéro entre crochets, par exemple [2].

Évènements :
{contexte}"""


def numeros(documents):
    """Numérote les évènements dans l'ordre où la recherche les remonte. Les chunks d'un même évènement
    partagent son numéro : c'est lui que le modèle cite et que l'API rattache à la carte affichée."""
    return {uid: n for n, uid in enumerate(dict.fromkeys(d.metadata["uid"] for d in documents), 1)}


def en_contexte(documents):
    n = numeros(documents)
    # les dates affichées par OpenAgenda n'ont pas d'année : on préfixe la date de début complète
    return "\n\n".join(f"[{n[d.metadata['uid']]}] Début : {d.metadata['date_debut'][:10]}\n{d.page_content}"
                       for d in documents)


load_dotenv()
cle = os.environ["OPENROUTER_API_KEY"]
aujourdhui = date.today()
vectoriseur = OpenAIEmbeddings(model=MODELE, base_url=OPENROUTER, api_key=cle,
                               check_embedding_ctx_length=False)
index = FAISS.load_local(str(SORTIE), vectoriseur, allow_dangerous_deserialization=True)  # index produit par build_index.py

# l'index garde un an d'historique, mais on ne recommande que ce qui n'est pas encore terminé :
# Faiss classe tout l'index, puis on garde les K meilleurs chunks encore d'actualité
recherche = index.as_retriever(search_kwargs={
    "k": K, "fetch_k": index.index.ntotal,
    "filter": lambda m: m["date_fin"] >= aujourdhui.isoformat()})
prompt = ChatPromptTemplate.from_messages([("system", CONSIGNE), ("human", "{question}")])
modele = ChatOpenAI(model=MODELE_CHAT, base_url=OPENROUTER, api_key=cle, temperature=0,
                    max_retries=5)  # le pool Mistral d'OpenRouter renvoie des 429 par moments
generation = (RunnablePassthrough.assign(contexte=lambda x: en_contexte(x["documents"]))
              | prompt.partial(aujourdhui=aujourdhui.strftime("%d/%m/%Y")) | modele | StrOutputParser())

# question -> {question, documents} -> + reponse : les sources restent disponibles pour l'affichage
chaine = RunnableParallel(question=RunnablePassthrough(), documents=recherche).assign(reponse=generation)


if __name__ == "__main__":
    resultat = chaine.invoke(sys.argv[1])
    print(resultat["reponse"], "\n")
    for d in resultat["documents"]:
        print("-", d.metadata["titre"], "|", d.metadata["dates_texte"], "|", d.metadata["lieu"])
