"""Vectorisation des évènements nettoyés et construction de l'index Faiss."""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

ENTREE = Path("data/processed/evenements_93.csv")
SORTIE = Path("data/faiss_index")
MODELE = "mistralai/mistral-embed-2312"
OPENROUTER = "https://openrouter.ai/api/v1"
TAILLE_CHUNK = 1000  # caractères : 74 % des évènements tiennent en un seul chunk
RECOUVREMENT = 100
LOT = 50  # textes envoyés par appel à l'API

METADONNEES = ["uid", "titre", "description", "date_debut", "date_fin", "dates_texte", "lieu", "ville", "lien"]


def en_documents(evenements):
    """Compose le texte à vectoriser pour chaque évènement, puis le découpe en chunks.

    Le texte reprend titre, mots-clés, lieu et dates avant la description : sans eux, le
    même spectacle joué à Montreuil et à Bobigny aurait le même vecteur, et une question
    du type « quoi faire à Montreuil ce week-end » ne pourrait pas les départager. Les
    champs restent par ailleurs disponibles en métadonnées, et le `uid` relie chaque
    chunk à son évènement d'origine.
    """
    textes = (evenements.titre + "\n" + evenements.mots_cles + "\n" + evenements.lieu + ", "
              + evenements.ville + "\n" + evenements.dates_texte + "\n" + evenements.description)
    decoupeur = RecursiveCharacterTextSplitter(chunk_size=TAILLE_CHUNK, chunk_overlap=RECOUVREMENT)
    return decoupeur.create_documents(textes.tolist(), evenements[METADONNEES].to_dict("records"))


if __name__ == "__main__":
    load_dotenv()
    evenements = pd.read_csv(ENTREE).fillna("")
    documents = en_documents(evenements)
    vectoriseur = OpenAIEmbeddings(
        model=MODELE,
        base_url=OPENROUTER,
        api_key=os.environ["OPENROUTER_API_KEY"],
        chunk_size=LOT,
        check_embedding_ctx_length=False,  # sinon LangChain envoie des tokens OpenAI, que Mistral refuse
    )
    index = FAISS.from_documents(documents, vectoriseur)
    index.save_local(str(SORTIE))

    print(f"{len(evenements)} évènements découpés en {len(documents)} chunks")
    print(f"index de {index.index.ntotal} vecteurs à {index.index.d} dimensions écrit dans {SORTIE}")
