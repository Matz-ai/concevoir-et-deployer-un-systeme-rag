"""Vérifie l'installation : importe chaque bibliothèque du POC et affiche sa version."""

import importlib
from importlib.metadata import version

# module à importer -> paquet pip correspondant
BIBLIOTHEQUES = {
    "langchain": "langchain",
    "langchain_community": "langchain-community",
    "langchain_openai": "langchain-openai",
    "faiss": "faiss-cpu",
    "pandas": "pandas",
    "requests": "requests",
    "dotenv": "python-dotenv",
    "pytest": "pytest",
}

for module, paquet in BIBLIOTHEQUES.items():
    importlib.import_module(module)
    print(f"{paquet:<20} {version(paquet)}")
